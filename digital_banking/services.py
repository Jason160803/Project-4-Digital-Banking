# digital_banking/services.py

import random
from datetime import datetime
from fastapi import HTTPException, status

from . import database as db

# --- Business Logic Constants (Assumptions) ---
MINIMUM_BALANCE = 10000.0
INTER_BANK_TRANSFER_FEE = 6500.0
MAX_TRANSFER_AMOUNT = 25000000.0
DAILY_TRANSACTION_LIMIT = 10
LOCAL_BANK_NAME = "Bank Digital API"

def _generate_account_number():
    """Generates a new unique 10-digit account number."""
    while True:
        acc_num = str(random.randint(1000000000, 9999999999))
        if acc_num not in db.accounts_db:
            return acc_num

def _log_transaction(account_number: str, type: str, amount: float, description: str):
    """Logs a transaction for a given account."""
    if account_number not in db.transactions_db:
        db.transactions_db[account_number] = []
    
    transaction = {
        "type": type,
        "amount": amount,
        "timestamp": datetime.now().isoformat(),
        "description": description,
    }
    db.transactions_db[account_number].append(transaction)
    db.accounts_db[account_number]['daily_transaction_count'] += 1


def get_account_or_404(account_number: str):
    """Fetches an account or raises a 404 Not Found error."""
    if account_number not in db.accounts_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return db.accounts_db[account_number]

def validate_active_account(account: dict):
    """Checks if an account is active, raises 400 if not."""
    if not account['is_active']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account is inactive")

def validate_daily_transaction_limit(account_number: str):
    """Checks if the daily transaction limit has been reached."""
    db.reset_daily_limits_if_new_day(account_number)
    account = db.accounts_db[account_number]
    if account['daily_transaction_count'] >= DAILY_TRANSACTION_LIMIT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Daily transaction limit reached")

# --- Service Functions ---

def create_new_account(account_data: dict):
    acc_num = _generate_account_number()
    new_account = {
        "name": account_data['name'],
        "bank_name": account_data['bank_name'],
        "balance": 0.0,
        "is_active": True,
        "daily_transaction_count": 0,
        "last_transaction_date": datetime.now().date(),
    }
    db.accounts_db[acc_num] = new_account
    db.transactions_db[acc_num] = []
    return {"account_number": acc_num, **new_account}

def process_deposit(account_number: str, amount: float):
    account = get_account_or_404(account_number)
    validate_active_account(account)
    
    account['balance'] += amount
    _log_transaction(account_number, "DEPOSIT", amount, f"Deposited ${amount} into account.")
    return account

def process_withdrawal(account_number: str, amount: float):
    account = get_account_or_404(account_number)
    validate_active_account(account)
    validate_daily_transaction_limit(account_number)

    if account['balance'] - amount < MINIMUM_BALANCE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance to maintain minimum")
    
    account['balance'] -= amount
    _log_transaction(account_number, "WITHDRAWAL", amount, f"Withdrew ${amount} from account.")
    return account

def process_transfer(sender_acc_num: str, target_acc_num: str, amount: float):
    if sender_acc_num == target_acc_num:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sender and target accounts cannot be the same")

    if amount > MAX_TRANSFER_AMOUNT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transfer amount exceeds the maximum limit of ${MAX_TRANSFER_AMOUNT}"
        )

    sender_account = get_account_or_404(sender_acc_num)
    target_account = get_account_or_404(target_acc_num)
    
    validate_active_account(sender_account)
    validate_active_account(target_account)
    validate_daily_transaction_limit(sender_acc_num)

    fee = 0
    if sender_account['bank_name'] != target_account['bank_name']:
        fee = INTER_BANK_TRANSFER_FEE
    
    total_deduction = amount + fee
    if sender_account['balance'] - total_deduction < MINIMUM_BALANCE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance for transfer and fee")

    # Perform transaction
    sender_account['balance'] -= total_deduction
    target_account['balance'] += amount

    # Log transactions
    _log_transaction(
        sender_acc_num, 
        "TRANSFER_OUT", 
        amount, 
        f"Transferred ${amount} to {target_acc_num}. Fee: ${fee}"
    )
    _log_transaction(
        target_acc_num,
        "TRANSFER_IN",
        amount,
        f"Received ${amount} from {sender_acc_num}."
    )

    return {"message": "Transfer successful", "fee": fee}