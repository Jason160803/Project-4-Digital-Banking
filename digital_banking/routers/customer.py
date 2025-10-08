from fastapi import APIRouter, Path
from typing import List

from .. import services, models
from ..database import transactions_db

router = APIRouter(
    prefix="/accounts/{account_number}",
    tags=["Customer"]
)

@router.get("/details/", response_model=models.AccountInfoCustomer)
def get_account_details(account_number: str = Path(..., description="The customer's account number")):
    account = services.get_account_or_404(account_number)
    # Jangan tampilkan PIN di respons
    response_account = account.copy()
    response_account.pop('pin', None)
    return models.AccountInfoCustomer(account_number=account_number, **response_account)

@router.post("/deposit/", response_model=models.AccountInfoCustomer)
def deposit(req: models.AuthorizedTransactionRequest, account_number: str = Path(..., description="The account number to deposit into")):
    updated_account = services.process_deposit(account_number, req.amount, req.pin)
    response_account = updated_account.copy()
    response_account.pop('pin', None)
    return models.AccountInfoCustomer(account_number=account_number, **response_account)

@router.post("/withdraw/", response_model=models.AccountInfoCustomer)
def withdraw(req: models.AuthorizedTransactionRequest, account_number: str = Path(..., description="The account number to withdraw from")):
    updated_account = services.process_withdrawal(account_number, req.amount, req.pin)
    response_account = updated_account.copy()
    response_account.pop('pin', None)
    return models.AccountInfoCustomer(account_number=account_number, **response_account)

@router.post("/transfer/")
def transfer(req: models.AuthorizedTransferRequest, account_number: str = Path(..., description="The sender's account number")):
    result = services.process_transfer(account_number, req.target_account_number, req.amount, req.pin)
    return result

@router.get("/transactions/", response_model=List[models.Transaction])
def get_transaction_history(account_number: str = Path(..., description="The account number to get history for")):
    services.get_account_or_404(account_number)
    return transactions_db.get(account_number, [])