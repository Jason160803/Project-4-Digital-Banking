from pydantic import BaseModel, Field

# Definisikan Regex di sini (di luar class) agar bisa diakses secara global di dalam file ini
name_regex = r"^[a-zA-Z .]+$"
pin_regex = r"^\d{6}$"

class AccountCreate(BaseModel):
    name: str = Field(
        ..., 
        min_length=3, 
        description="Customer's full name (letters, spaces, and dots only)",
        pattern=name_regex # Sekarang variabel ini sudah dikenali
    )
    bank_name: str = Field(..., description="Bank where the account is registered")
    pin: str = Field(..., description="6-digit personal identification number", pattern=pin_regex)

class AccountUpdate(BaseModel):
    name: str = Field(
        ..., 
        min_length=3, 
        description="Customer's new full name (letters, spaces, and dots only)",
        pattern=name_regex
    )

class AuthorizedTransactionRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Transaction amount, must be positive")
    pin: str = Field(..., description="Your 6-digit PIN for authorization")

class AuthorizedTransferRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Transfer amount")
    target_account_number: str = Field(..., description="The account number to transfer to")
    pin: str = Field(..., description="Your 6-digit PIN for authorization")

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

class Transaction(BaseModel):
    type: str
    amount: float
    timestamp: str
    description: str