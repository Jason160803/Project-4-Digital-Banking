from pydantic import BaseModel, Field
from . import config

# Definisikan Regex di sini (di luar class) agar bisa diakses secara global di dalam file ini
name_regex = r"^[a-zA-Z .]+$"
pin_regex = r"^\d{6}$"

class AccountCreate(BaseModel):
    name: str = Field(..., min_length=3, pattern=name_regex)
    bank_name: str = Field(...)
    pin: str = Field(..., pattern=pin_regex)
    # --- PERUBAHAN DI SINI ---
    # Hapus nilai default `0.0` untuk membuatnya wajib
    # Tambahkan `ge` (greater than or equal to) dengan nilai dari config
    initial_balance: float = Field(
        ..., 
        ge=config.MINIMUM_BALANCE, 
        description=f"Initial balance must be at least Rp {config.MINIMUM_BALANCE}"
    )


class AccountUpdate(BaseModel):
    name: str = Field(
        ..., 
        min_length=3, 
        description="Customer's new full name (letters, spaces, and dots only)",
        pattern=name_regex
    )

class AuthorizedTransactionRequest(BaseModel):
    amount: float = Field(..., gt=0)
    pin: str
    timestamp: str

class AuthorizedTransferRequest(BaseModel):
    amount: float = Field(..., gt=0)
    target_account_number: str
    pin: str
    timestamp: str

# Response Models (tidak perlu diubah, tapi disertakan untuk kelengkapan)
class AccountInfoBase(BaseModel):
    account_number: str
    name: str
    bank_name: str
    is_active: bool

class AccountInfoAdmin(AccountInfoBase):
    pass

class AccountInfoCustomer(AccountInfoBase):
    balance: float
    daily_transaction_count: int

class Transaction(BaseModel):
    type: str
    amount: float
    timestamp: str
    description: str