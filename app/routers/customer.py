# app/routers/customer.py

from fastapi import APIRouter, HTTPException, status, Path
from typing import List
from .. import data, models, services

router = APIRouter(
    prefix="/accounts",
    tags=["Customer Transactions"]
)

@router.get("/{account_number}/balance")
def get_balance(account_number: str = Path(..., description="Nomor rekening nasabah")):
    """
    Melihat saldo terkini.
    """
    account = services.get_account_or_404(account_number)
    return {"account_number": account_number, "balance": account["balance"]}

@router.post("/{account_number}/deposit", response_model=models.MessageResponse)
def deposit(account_number: str, transaction: models.Transaction):
    """
    Melakukan setor tunai ke akun sendiri.
    """
    account = services.get_account_or_404(account_number)
    services.check_daily_transaction_limit(account_number)
    
    account["balance"] += transaction.amount
    data.accounts[account_number] = account
    
    services.add_transaction_history(
        account_number, "deposit", transaction.amount, f"Setor tunai ke rekening {account_number}"
    )
    
    return {"message": f"Setor tunai sebesar Rp{transaction.amount} berhasil. Saldo baru: Rp{account['balance']}"}

@router.post("/{account_number}/withdraw", response_model=models.MessageResponse)
def withdraw(account_number: str, transaction: models.Transaction):
    """
    Melakukan tarik tunai dari akun sendiri.
    Validasi: Saldo setelah penarikan tidak boleh kurang dari saldo minimum.
    """
    account = services.get_account_or_404(account_number)
    services.check_daily_transaction_limit(account_number)
    
    if (account["balance"] - transaction.amount) < data.MINIMUM_BALANCE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Saldo tidak mencukupi. Saldo setelah penarikan minimal harus Rp{data.MINIMUM_BALANCE}"
        )
        
    account["balance"] -= transaction.amount
    data.accounts[account_number] = account
    
    services.add_transaction_history(
        account_number, "withdraw", transaction.amount, f"Tarik tunai dari rekening {account_number}"
    )
    
    return {"message": f"Tarik tunai sebesar Rp{transaction.amount} berhasil. Saldo sisa: Rp{account['balance']}"}

@router.post("/{account_number}/transfer", response_model=models.MessageResponse)
def transfer(account_number: str, transfer_data: models.Transfer):
    """
    Melakukan transfer ke akun lain.
    Validasi:
    - Batas maksimum nominal transfer.
    - Saldo mencukupi (termasuk biaya admin jika beda bank).
    - Akun tujuan harus ada dan aktif.
    """
    # Validasi batas maksimum transfer
    if transfer_data.amount > data.MAX_TRANSFER_AMOUNT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Nominal transfer melebihi batas maksimum (Rp{data.MAX_TRANSFER_AMOUNT})"
        )

    # Validasi akun pengirim dan tujuan
    sender_account = services.get_account_or_404(account_number)
    services.check_daily_transaction_limit(account_number)
    
    target_account = services.get_account_or_404(transfer_data.target_account_number)
    
    if account_number == transfer_data.target_account_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tidak dapat mentransfer ke rekening sendiri."
        )

    # Cek biaya transfer antarbank
    transfer_fee = 0
    is_inter_bank = sender_account["bank_name"] != target_account["bank_name"]
    if is_inter_bank:
        transfer_fee = data.INTER_BANK_TRANSFER_FEE
        
    total_debit = transfer_data.amount + transfer_fee
    
    # Validasi saldo pengirim
    if (sender_account["balance"] - total_debit) < data.MINIMUM_BALANCE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Saldo tidak mencukupi untuk melakukan transfer dan membayar biaya admin."
        )

    # Proses transaksi
    sender_account["balance"] -= total_debit
    target_account["balance"] += transfer_data.amount
    
    data.accounts[account_number] = sender_account
    data.accounts[transfer_data.target_account_number] = target_account

    # Catat riwayat transaksi
    services.add_transaction_history(
        account_number, "transfer_out", transfer_data.amount, f"Transfer ke {target_account['name']} ({transfer_data.target_account_number})"
    )
    if is_inter_bank:
        services.add_transaction_history(
            account_number, "fee", transfer_fee, "Biaya admin transfer antarbank"
        )
    services.add_transaction_history(
        transfer_data.target_account_number, "transfer_in", transfer_data.amount, f"Transfer dari {sender_account['name']} ({account_number})"
    )

    return {"message": "Transfer berhasil"}


@router.get("/{account_number}/history", response_model=List[models.TransactionHistory])
def get_transaction_history(account_number: str):
    """
    Melihat riwayat transaksi.
    """
    services.get_account_or_404(account_number) # Validasi akun ada dan aktif
    
    return data.transactions.get(account_number, [])