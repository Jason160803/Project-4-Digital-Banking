import random
from datetime import datetime, date

from fastapi import HTTPException, status

from . import database as db
from . import models
from . import config


def _generate_account_number():
    while True:
        acc_num = str(random.randint(1000000000, 9999999999))
        if acc_num not in db.accounts_db:
            return acc_num

def _log_transaction(account_number: str, type: str, amount: float, description: str, timestamp: str):
    final_timestamp = timestamp if timestamp else datetime.now().isoformat()
    
    transaction = {
        "type": type,
        "amount": amount,
        "timestamp": final_timestamp,
        "description": description,
    }
    if account_number not in db.transactions_db:
        db.transactions_db[account_number] = []
    db.transactions_db[account_number].append(transaction)
    
    # --- PERUBAHAN DI SINI: Baris di bawah ini dihapus ---
    # db.accounts_db[account_number]['daily_transaction_count'] += 1

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
    if account.get('pin') != provided_pin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid PIN")

def create_new_account(account_data: models.AccountCreate):
    # Validasi manual dihapus dari sini karena sudah ditangani Pydantic di models.py
    acc_num = _generate_account_number()
    new_account = {
        "name": account_data.name,
        "bank_name": account_data.bank_name,
        "pin": account_data.pin,
        "balance": account_data.initial_balance,
        "is_active": True,
        "daily_transaction_count": 0,
        "last_transaction_date": date.today(),
    }
    db.accounts_db[acc_num] = new_account
    db.transactions_db[acc_num] = []
    response_account = new_account.copy()
    response_account.pop('pin', None)
    return {"account_number": acc_num, **response_account}

def process_deposit(account_number: str, amount: float, pin: str, timestamp: str):
    account = get_account_or_404(account_number)
    validate_pin(account, pin)
    validate_active_account(account)
    
    account['balance'] += amount
    _log_transaction(account_number, "DEPOSIT", amount, f"Deposited ${amount:,.2f}", timestamp=timestamp)
    return account

def process_withdrawal(account_number: str, amount: float, pin: str, timestamp: str):
    account = get_account_or_404(account_number)
    validate_pin(account, pin)
    validate_active_account(account)
    
    # --- PERUBAHAN DI SINI: Pengecekan limit harian dihapus dari sini ---
    # validate_daily_transaction_limit(account_number)

    if account['balance'] - amount < MINIMUM_BALANCE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance to maintain minimum")
    
    account['balance'] -= amount
    _log_transaction(account_number, "WITHDRAWAL", amount, f"Withdrew ${amount:,.2f}", timestamp=timestamp)
    return account

def process_transfer(sender_acc_num: str, target_acc_num: str, amount: float, pin: str, timestamp: str):
    if sender_acc_num == target_acc_num:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sender and target accounts cannot be the same")

    if amount > MAX_TRANSFER_AMOUNT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Transfer amount exceeds limit")

    sender_account = get_account_or_404(sender_acc_num)
    validate_pin(sender_account, pin)
    target_account = get_account_or_404(target_acc_num)
    
    validate_active_account(sender_account)
    validate_active_account(target_account)
    validate_daily_transaction_limit(sender_acc_num) # <-- Pengecekan limit tetap di sini untuk transfer

    fee = 0
    if sender_account['bank_name'] != target_account['bank_name']:
        fee = INTER_BANK_TRANSFER_FEE
    
    total_deduction = amount + fee
    if sender_account['balance'] - total_deduction < MINIMUM_BALANCE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance for transfer and fee")

    sender_account['balance'] -= total_deduction
    target_account['balance'] += amount

    _log_transaction(sender_acc_num, "TRANSFER_OUT", amount, f"Transferred ${amount:,.2f} to {target_acc_num}. Fee: ${fee:,.2f}", timestamp=timestamp)
    _log_transaction(target_acc_num, "TRANSFER_IN", amount, f"Received ${amount:,.2f} from {sender_acc_num}.", timestamp=timestamp)
    
    # --- PERUBAHAN DI SINI: Counter ditambah secara manual hanya untuk transfer ---
    sender_account['daily_transaction_count'] += 1

    return {"message": "Transfer successful", "fee": fee}

def delete_account_permanently(account_number: str):
    get_account_or_404(account_number)
    del db.accounts_db[account_number]
    if account_number in db.transactions_db:
        del db.transactions_db[account_number]
    return {"message": "Account and all associated transactions have been permanently deleted."}