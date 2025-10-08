from pydantic import BaseModel, Field
from typing import Optional

class AccountCreate(BaseModel):
    name: str = Field(..., min_length=3, description="Customer's full name")
    bank_name: str = Field(..., description="Bank where the account is registered")

class AccountUpdate(BaseModel):
    name: str = Field(..., min_length=3, description="Customer's new full name")

class TransactionRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Transaction amount, must be positive")

class TransferRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Transfer amount")
    target_account_number: str = Field(..., description="The account number to transfer to")

# Response Models
class AccountInfoBase(BaseModel):
    account_number: str
    name: str
    bank_name: str
    is_active: bool

class AccountInfoAdmin(AccountInfoBase):
    pass # Admin sees basic info

class AccountInfoCustomer(AccountInfoBase):
    balance: float

class Transaction(BaseModel):
    type: str
    amount: float
    timestamp: str
    description: str