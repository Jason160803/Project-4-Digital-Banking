# app/routers/admin.py

from fastapi import APIRouter, HTTPException, status, Body
from typing import List
from .. import data, models, services

router = APIRouter(
    prefix="/admin",
    tags=["Admin Management"]
)

@router.post("/accounts", response_model=models.AccountCreateResponse, status_code=status.HTTP_201_CREATED)
def create_account(account_data: models.AccountCreate):
    """
    Membuat akun nasabah baru.
    - Menghasilkan nomor rekening unik.
    - Validasi setoran awal harus lebih besar dari saldo minimum.
    """
    if account_data.initial_deposit < data.MINIMUM_BALANCE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Setoran awal minimal harus Rp{data.MINIMUM_BALANCE}"
        )

    account_number = services.generate_account_number()
    
    new_account = {
        "account_number": account_number,
        "name": account_data.name,
        "bank_name": account_data.bank_name,
        "balance": account_data.initial_deposit,
        "is_active": True
    }
    
    data.accounts[account_number] = new_account
    
    # Menambahkan catatan transaksi setoran awal
    services.add_transaction_history(
        account_number, "deposit", account_data.initial_deposit, "Setoran awal pembukaan akun"
    )
    
    return new_account

@router.get("/accounts", response_model=List[models.AccountInfo])
def get_all_accounts():
    """
    Mendapatkan daftar semua akun nasabah (hanya informasi dasar).
    Admin tidak dapat melihat saldo.
    """
    account_list = []
    for acc_num, details in data.accounts.items():
        account_list.append(models.AccountInfo(**details))
    return account_list

@router.get("/accounts/{account_number}", response_model=models.AccountInfo)
def get_account_by_number(account_number: str):
    """
    Mendapatkan informasi dasar satu akun berdasarkan nomor rekening.
    """
    account = services.get_account_or_404(account_number)
    return models.AccountInfo(**account)

@router.put("/accounts/{account_number}", response_model=models.AccountInfo)
def update_account_info(account_number: str, update_data: models.AccountUpdate):
    """
    Memperbarui informasi nama atau nama bank nasabah.
    """
    account = services.get_account_or_404(account_number)
    
    if update_data.name:
        account["name"] = update_data.name
    if update_data.bank_name:
        account["bank_name"] = update_data.bank_name
        
    data.accounts[account_number] = account
    return models.AccountInfo(**account)

@router.delete("/accounts/{account_number}", response_model=models.MessageResponse)
def deactivate_account(account_number: str):
    """
    Menonaktifkan akun nasabah. Akun tidak dihapus, hanya statusnya diubah.
    """
    account = services.get_account_or_404(account_number)
    
    if not account["is_active"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Akun sudah tidak aktif")

    account["is_active"] = False
    data.accounts[account_number] = account
    
    return {"message": f"Akun {account_number} berhasil dinonaktifkan."}