# tests/test_customer.py

from fastapi.testclient import TestClient
from app.main import app
from app import data

client = TestClient(app)

def setup_function():
    data.accounts.clear()
    data.transactions.clear()
    data.daily_transaction_limits.clear()
    
    # Buat dua akun untuk testing
    data.accounts["1111111111"] = {
        "account_number": "1111111111", "name": "Pengirim", "bank_name": "Bank A",
        "balance": 500000, "is_active": True
    }
    data.accounts["2222222222"] = {
        "account_number": "2222222222", "name": "Penerima", "bank_name": "Bank B",
        "balance": 200000, "is_active": True
    }

def test_deposit():
    response = client.post("/accounts/1111111111/deposit", json={"amount": 50000})
    assert response.status_code == 200
    assert data.accounts["1111111111"]["balance"] == 550000
    assert len(data.transactions["1111111111"]) == 1

def test_withdraw_insufficient_funds():
    response = client.post("/accounts/1111111111/withdraw", json={"amount": 460000})
    # Sisa saldo akan menjadi 40000, di bawah minimum balance 50000
    assert response.status_code == 400
    assert "Saldo tidak mencukupi" in response.json()["detail"]

def test_withdraw_success():
    response = client.post("/accounts/1111111111/withdraw", json={"amount": 100000})
    assert response.status_code == 200
    assert data.accounts["1111111111"]["balance"] == 400000

def test_transfer_inter_bank_success():
    response = client.post("/accounts/1111111111/transfer", json={
        "amount": 100000,
        "target_account_number": "2222222222"
    })
    assert response.status_code == 200
    # Saldo pengirim berkurang 100000 + 6500 (biaya admin)
    assert data.accounts["1111111111"]["balance"] == 500000 - 100000 - 6500
    # Saldo penerima bertambah 100000
    assert data.accounts["2222222222"]["balance"] == 200000 + 100000
    # Cek riwayat transaksi
    assert len(data.transactions["1111111111"]) == 2 # transfer_out & fee
    assert len(data.transactions["2222222222"]) == 1 # transfer_in

def test_transfer_exceeds_max_limit():
    response = client.post("/accounts/1111111111/transfer", json={
        "amount": 30000000, # Melebihi batas MAX_TRANSFER_AMOUNT
        "target_account_number": "2222222222"
    })
    assert response.status_code == 400
    assert "melebihi batas maksimum" in response.json()["detail"]

def test_daily_transaction_limit():
    acc_num = "1111111111"
    # Lakukan transaksi sampai batas maksimum
    for _ in range(data.MAX_DAILY_TRANSACTIONS):
        client.post(f"/accounts/{acc_num}/deposit", json={"amount": 1000})
    
    # Transaksi ke-11 seharusnya gagal
    response = client.post(f"/accounts/{acc_num}/deposit", json={"amount": 1000})
    assert response.status_code == 429 # Too Many Requests
    assert "Batas transaksi harian" in response.json()["detail"]

def test_get_history():
    client.post("/accounts/1111111111/deposit", json={"amount": 50000})
    client.post("/accounts/1111111111/withdraw", json={"amount": 20000})
    
    response = client.get("/accounts/1111111111/history")
    assert response.status_code == 200
    assert len(response.json()) == 2