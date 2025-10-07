from fastapi import APIRouter, status, Body
from typing import List

from .. import services, models
from ..database import accounts_db

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.post("/accounts/", status_code=status.HTTP_201_CREATED, response_model=models.AccountInfoCustomer)
def create_account(account_create: models.AccountCreate):
    """
    Admin: Create a new customer account.
    """
    new_account = services.create_new_account(account_create.dict())
    return {**new_account, "account_number": list(accounts_db.keys())[-1]}

@router.get("/accounts/", response_model=List[models.AccountInfoAdmin])
def get_all_accounts():
    """
    Admin: Get a list of all customer accounts (basic information only).
    """
    admin_view_list = []
    for acc_num, details in accounts_db.items():
        admin_view_list.append(models.AccountInfoAdmin(
            account_number=acc_num,
            name=details['name'],
            bank_name=details['bank_name'],
            is_active=details['is_active']
        ))
    return admin_view_list

@router.put("/accounts/{account_number}/", response_model=models.AccountInfoAdmin)
def update_account_info(account_number: str, account_update: models.AccountUpdate):
    """
    Admin: Update a customer's name.
    """
    account = services.get_account_or_404(account_number)
    account['name'] = account_update.name
    return models.AccountInfoAdmin(account_number=account_number, **account)

@router.delete("/accounts/{account_number}/", status_code=status.HTTP_200_OK)
def deactivate_account(account_number: str):
    """
    Admin: Deactivate an account. The account data is kept but marked as inactive.
    """
    account = services.get_account_or_404(account_number)
    if not account['is_active']:
        return {"message": "Account already inactive"}
        
    account['is_active'] = False
    return {"message": "Account deactivated successfully"}