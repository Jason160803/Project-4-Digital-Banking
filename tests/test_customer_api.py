from fastapi.testclient import TestClient
from digital_banking.main import app
from digital_banking.database import accounts_db, transactions_db
from digital_banking import services, config
from digital_banking.models import AccountCreate

client = TestClient(app)

# Dapatkan timestamp saat ini untuk digunakan di semua tes
current_timestamp = "2025-10-10T12:00:00"

def setup_function():
    accounts_db.clear()
    transactions_db.clear()
    services.create_new_account(AccountCreate(name="User Satu", bank_name="Bank Digital API", pin="111111", initial_balance=100000))
    services.create_new_account(AccountCreate(name="User Dua", bank_name="Bank Lain", pin="222222", initial_balance=50000))
    keys = list(accounts_db.keys())
    accounts_db["1111111111"] = accounts_db.pop(keys[0])
    transactions_db["1111111111"] = []
    accounts_db["2222222222"] = accounts_db.pop(keys[1])
    transactions_db["2222222222"] = []

def test_deposit():
    response = client.post("/accounts/1111111111/deposit/", json={"amount": 50000, "pin": "111111", "timestamp": current_timestamp})
    assert response.status_code == 200
    assert response.json()["balance"] == 150000.0

def test_withdraw_success():
    response = client.post("/accounts/1111111111/withdraw/", json={"amount": 20000, "pin": "111111", "timestamp": current_timestamp})
    assert response.status_code == 200
    assert response.json()["balance"] == 80000.0

def test_withdraw_insufficient_balance_for_minimum():
    response = client.post("/accounts/1111111111/withdraw/", json={"amount": 80001, "pin": "111111", "timestamp": current_timestamp})
    assert response.status_code == 400

def test_transfer_inter_bank_success():
    response = client.post("/accounts/1111111111/transfer/", json={"target_account_number": "2222222222", "amount": 10000, "pin": "111111", "timestamp": current_timestamp})
    assert response.status_code == 200
    assert accounts_db["1111111111"]["balance"] == 100000.0 - 10000 - config.INTER_BANK_TRANSFER_FEE
    assert accounts_db["2222222222"]["balance"] == 50000.0 + 10000

def test_transfer_fail_exceeds_max_limit():
    response = client.post("/accounts/1111111111/transfer/", json={"target_account_number": "2222222222", "amount": config.MAX_TRANSFER_AMOUNT + 1, "pin": "111111", "timestamp": current_timestamp})
    assert response.status_code == 400

def test_get_transaction_history():
    client.post("/accounts/1111111111/deposit/", json={"amount": 5000, "pin": "111111", "timestamp": current_timestamp})
    response = client.get("/accounts/1111111111/transactions/")
    assert response.status_code == 200
    assert len(response.json()) == 1