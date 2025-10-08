# app/services.py

from fastapi import HTTPException, status
from datetime import datetime, date
import random
import string
from . import data
from .models import TransactionHistory

def generate_account_number():
    """Menghasilkan nomor rekening unik 10 digit."""
    while True:
        # Menghasilkan string acak dari angka
        acc_num = ''.join(random.choices(string.digits, k=10))
        if acc_num not in data.accounts:
            return acc_num

def check_daily_transaction_limit(account_number: str):
    """Memeriksa dan memperbarui batas transaksi harian."""
    today = date.today()
    
    if account_number not in data.daily_transaction_limits:
        data.daily_transaction_limits[account_number] = {"date": today, "count": 1}
        return

    tx_info = data.daily_transaction_limits[account_number]
    if tx_info["date"] == today:
        if tx_info["count"] >= data.MAX_DAILY_TRANSACTIONS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Batas transaksi harian ({data.MAX_DAILY_TRANSACTIONS} kali) telah tercapai."
            )
        tx_info["count"] += 1
    else:
        # Reset jika hari sudah berganti
        tx_info["date"] = today
        tx_info["count"] = 1

def add_transaction_history(account_number: str, tx_type: str, amount: float, description: str):
    """Menambahkan catatan ke riwayat transaksi."""
    if account_number not in data.transactions:
        data.transactions[account_number] = []
    
    history = TransactionHistory(
        type=tx_type,
        amount=amount,
        timestamp=datetime.now(),
        description=description
    )
    data.transactions[account_number].append(history.dict())

def get_account_or_404(account_number: str):
    """Mengambil data akun, atau raise 404 jika tidak ditemukan."""
    if account_number not in data.accounts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Akun tidak ditemukan")
    
    account = data.accounts[account_number]
    if not account["is_active"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akun tidak aktif")
        
    return account