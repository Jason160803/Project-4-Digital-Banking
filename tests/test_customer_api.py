# digital_banking/tests/test_customer_api.py

from fastapi.testclient import TestClient
from ..main import app
from ..database import accounts_db, transactions_db
from .. import services

client = TestClient(app)

def setup_function():
    """Clear and set up a predictable state before each test."""
    accounts_db.clear()
    transactions_db.clear()
    
    # Create two accounts for testing
    acc1 = services.create_new_account({"name": "User Satu", "bank_name": "Bank Digital API"})
    acc2 = services.create_new_account({"name": "User Dua", "bank_name": "Bank Lain"})
    
    # Manually set account numbers to be predictable
    accounts_db["1111111111"] = accounts_db.pop(list(accounts_db.keys())[0])
    transactions_db["1111111111"] = []
    accounts_db["2222222222"] = accounts_db.pop(list(accounts_db.keys())[0])
    transactions_db["2222222222"] = []
    
    # Give user 1 some initial balance
    accounts_db["1111111111"]["balance"] = 100000.0


def test_deposit():
    response = client.post("/accounts/1111111111/deposit/", json={"amount": 50000})
    assert response.status_code == 200
    assert response.json()["balance"] == 150000.0
    assert len(transactions_db["1111111111"]) == 1
    assert transactions_db["1111111111"][0]["type"] == "DEPOSIT"

def test_withdraw_success():
    response = client.post("/accounts/1111111111/withdraw/", json={"amount": 20000})
    assert response.status_code == 200
    assert response.json()["balance"] == 80000.0

def test_withdraw_insufficient_balance():
    response = client.post("/accounts/1111111111/withdraw/", json={"amount": 95000})
    assert response.status_code == 400 # Bad Request
    assert "insufficient balance" in response.json()["detail"].lower()

def test_transfer_inter_bank_success():
    response = client.post(
        "/accounts/1111111111/transfer/", 
        json={"target_account_number": "2222222222", "amount": 10000}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Transfer successful"
    assert response.json()["fee"] == services.INTER_BANK_TRANSFER_FEE
    # Check balances
    assert accounts_db["1111111111"]["balance"] == 100000.0 - 10000 - services.INTER_BANK_TRANSFER_FEE
    assert accounts_db["2222222222"]["balance"] == 10000.0

def test_transfer_fail_exceeds_limit():
    response = client.post(
        "/accounts/1111111111/transfer/", 
        json={"target_account_number": "2222222222", "amount": services.MAX_TRANSFER_AMOUNT + 1}
    )
    assert response.status_code == 400
    assert "exceeds the maximum limit" in response.json()["detail"]

def test_get_transaction_history():
    client.post("/accounts/1111111111/deposit/", json={"amount": 5000})
    client.post("/accounts/1111111111/withdraw/", json={"amount": 1000})
    
    response = client.get("/accounts/1111111111/transactions/")
    assert response.status_code == 200
    assert len(response.json()) == 2