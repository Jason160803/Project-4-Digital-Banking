from fastapi.testclient import TestClient
from digital_banking.main import app
from digital_banking.database import accounts_db, transactions_db
from digital_banking import services
from digital_banking.models import AccountCreate # <-- IMPORT AccountCreate

client = TestClient(app)

def setup_function():
    """Clear and set up a predictable state before each test."""
    accounts_db.clear()
    transactions_db.clear()
    
    # UBAH CARA MEMBUAT AKUN: Gunakan objek AccountCreate dan sertakan PIN
    services.create_new_account(AccountCreate(name="User Satu", bank_name="Bank Digital API", pin="111111"))
    services.create_new_account(AccountCreate(name="User Dua", bank_name="Bank Lain", pin="222222"))
    
    keys = list(accounts_db.keys())
    accounts_db["1111111111"] = accounts_db.pop(keys[0])
    transactions_db["1111111111"] = []
    accounts_db["2222222222"] = accounts_db.pop(keys[1])
    transactions_db["2222222222"] = []
    
    accounts_db["1111111111"]["balance"] = 100000.0

def test_deposit():
    # TAMBAHKAN "pin"
    response = client.post("/accounts/1111111111/deposit/", json={"amount": 50000, "pin": "111111"})
    assert response.status_code == 200
    assert response.json()["balance"] == 150000.0

def test_withdraw_success():
    # TAMBAHKAN "pin"
    response = client.post("/accounts/1111111111/withdraw/", json={"amount": 20000, "pin": "111111"})
    assert response.status_code == 200
    assert response.json()["balance"] == 80000.0

def test_withdraw_insufficient_balance_for_minimum():
    # TAMBAHKAN "pin"
    response = client.post("/accounts/1111111111/withdraw/", json={"amount": 95000, "pin": "111111"})
    assert response.status_code == 400

def test_transfer_inter_bank_success():
    # TAMBAHKAN "pin"
    response = client.post(
        "/accounts/1111111111/transfer/", 
        json={"target_account_number": "2222222222", "amount": 10000, "pin": "111111"}
    )
    assert response.status_code == 200
    assert accounts_db["1111111111"]["balance"] == 100000.0 - 10000 - services.INTER_BANK_TRANSFER_FEE
    assert accounts_db["2222222222"]["balance"] == 10000.0

def test_transfer_fail_exceeds_max_limit():
    # TAMBAHKAN "pin"
    response = client.post(
        "/accounts/1111111111/transfer/", 
        json={"target_account_number": "2222222222", "amount": services.MAX_TRANSFER_AMOUNT + 1, "pin": "111111"}
    )
    assert response.status_code == 400

def test_get_transaction_history():
    # TAMBAHKAN "pin" pada transaksi yang dilakukan sebelum tes
    client.post("/accounts/1111111111/deposit/", json={"amount": 5000, "pin": "111111"})
    
    response = client.get("/accounts/1111111111/transactions/")
    assert response.status_code == 200
    assert len(response.json()) == 1