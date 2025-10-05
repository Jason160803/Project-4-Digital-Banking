# digital_banking/routers/customer.py

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
    """
    Customer: Get detailed information about their own account, including balance.
    """
    account = services.get_account_or_404(account_number)
    return models.AccountInfoCustomer(account_number=account_number, **account)

@router.post("/deposit/", response_model=models.AccountInfoCustomer)
def deposit(transaction_req: models.TransactionRequest, account_number: str = Path(..., description="The account number to deposit into")):
    """
    Customer: Deposit an amount into the account.
    """
    updated_account = services.process_deposit(account_number, transaction_req.amount)
    return models.AccountInfoCustomer(account_number=account_number, **updated_account)

@router.post("/withdraw/", response_model=models.AccountInfoCustomer)
def withdraw(transaction_req: models.TransactionRequest, account_number: str = Path(..., description="The account number to withdraw from")):
    """
    Customer: Withdraw an amount from the account.
    Validates against minimum balance.
    """
    updated_account = services.process_withdrawal(account_number, transaction_req.amount)
    return models.AccountInfoCustomer(account_number=account_number, **updated_account)

@router.post("/transfer/")
def transfer(transfer_req: models.TransferRequest, account_number: str = Path(..., description="The sender's account number")):
    """
    Customer: Transfer an amount to another account.
    Applies fees for inter-bank transfers and validates limits.
    """
    result = services.process_transfer(account_number, transfer_req.target_account_number, transfer_req.amount)
    return result

@router.get("/transactions/", response_model=List[models.Transaction])
def get_transaction_history(account_number: str = Path(..., description="The account number to get history for")):
    """
    Customer: Get the transaction history for the account.
    """
    services.get_account_or_404(account_number) # Validate account exists
    return transactions_db.get(account_number, [])