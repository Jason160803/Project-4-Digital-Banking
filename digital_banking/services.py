import random
from datetime import datetime, date
from fastapi import HTTPException, status

from . import database as db
from .models import AccountCreate

MINIMUM_BALANCE = 20000.0
INTER_BANK_TRANSFER_FEE = 5000.0
MAX_TRANSFER_AMOUNT = 25000000.0
DAILY_TRANSACTION_LIMIT = 15
LOCAL_BANK_NAME = "Bank Digital API"

def _generate_account_number():
    while True:
        acc_num = str(random.randint(1000000000, 9999999999))
        if acc_num not in db.accounts_db:
            return acc_num

def _log_transaction(account_number: str, type: str, amount: float, description: str):
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
    if account_number not in db.accounts_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return db.accounts_db[account_number]

def validate_active_account(account: dict):
    if not account['is_active']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account is inactive")

def validate_daily_transaction_limit(account_number: str):
    db.reset_daily_limits_if_new_day(account_number)
    account = db.accounts_db[account_number]
    if account['daily_transaction_count'] >= DAILY_TRANSACTION_LIMIT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Daily transaction limit reached")

def validate_pin(account: dict, provided_pin: str):
    """Fungsi baru untuk memeriksa PIN."""
    if account.get('pin') != provided_pin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid PIN")

def create_new_account(account_data: AccountCreate):
    acc_num = _generate_account_number()
    new_account = {
        "name": account_data.name,
        "bank_name": account_data.bank_name,
        "pin": account_data.pin,  # Simpan PIN
        "balance": 0.0,
        "is_active": True,
        "daily_transaction_count": 0,
        "last_transaction_date": date.today(),
    }
    db.accounts_db[acc_num] = new_account
    db.transactions_db[acc_num] = []
    # Jangan tampilkan PIN di respons
    response_account = new_account.copy()
    response_account.pop('pin', None)
    return {"account_number": acc_num, **response_account}

def process_deposit(account_number: str, amount: float, pin: str):
    account = get_account_or_404(account_number)
    validate_pin(account, pin)
    validate_active_account(account)
    
    account['balance'] += amount
    _log_transaction(account_number, "DEPOSIT", amount, f"Deposited ${amount:,.2f} into account.")
    return account

def process_withdrawal(account_number: str, amount: float, pin: str):
    account = get_account_or_404(account_number)
    validate_pin(account, pin)
    validate_active_account(account)
    validate_daily_transaction_limit(account_number)

    if account['balance'] - amount < MINIMUM_BALANCE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance to maintain minimum")
    
    account['balance'] -= amount
    _log_transaction(account_number, "WITHDRAWAL", amount, f"Withdrew ${amount:,.2f} from account.")
    return account

def process_transfer(sender_acc_num: str, target_acc_num: str, amount: float, pin: str):
    if sender_acc_num == target_acc_num:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sender and target accounts cannot be the same")

    if amount > MAX_TRANSFER_AMOUNT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Transfer amount exceeds limit")

    sender_account = get_account_or_404(sender_acc_num)
    validate_pin(sender_account, pin)
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

    sender_account['balance'] -= total_deduction
    target_account['balance'] += amount

    _log_transaction(sender_acc_num, "TRANSFER_OUT", amount, f"Transferred ${amount:,.2f} to {target_acc_num}. Fee: ${fee:,.2f}")
    _log_transaction(target_acc_num, "TRANSFER_IN", amount, f"Received ${amount:,.2f} from {sender_acc_num}.")

    return {"message": "Transfer successful", "fee": fee}