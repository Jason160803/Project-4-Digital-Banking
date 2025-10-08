# app/models.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Model Dasar Akun
class AccountBase(BaseModel):
    name: str = Field(..., min_length=3, description="Nama lengkap nasabah")
    bank_name: str = Field(..., description="Nama bank tempat akun terdaftar")

# Model untuk membuat akun baru (oleh admin)
class AccountCreate(AccountBase):
    initial_deposit: float = Field(..., gt=0, description="Setoran awal saat pembukaan akun")

# Model untuk response saat akun berhasil dibuat
class AccountCreateResponse(AccountBase):
    account_number: str
    balance: float
    is_active: bool

# Model untuk informasi dasar akun yang bisa dilihat admin
class AccountInfo(AccountBase):
    account_number: str
    is_active: bool

# Model untuk update informasi akun (oleh admin)
class AccountUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3)
    bank_name: Optional[str] = None

# Model untuk transaksi
class Transaction(BaseModel):
    amount: float = Field(..., gt=0, description="Jumlah nominal transaksi")

class Transfer(Transaction):
    target_account_number: str = Field(..., description="Nomor rekening tujuan")

# Model untuk riwayat transaksi
class TransactionHistory(BaseModel):
    type: str
    amount: float
    timestamp: datetime
    description: str

# Model Response Umum
class MessageResponse(BaseModel):
    message: str