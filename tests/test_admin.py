# tests/test_admin.py

from fastapi.testclient import TestClient
from app.main import app
from app import data

client = TestClient(app)

# Membersihkan data sebelum setiap tes
def setup_function():
    data.accounts.clear()
    data.transactions.clear()
    data.daily_transaction_limits.clear()

def test_create_account_success():
    response = client.post("/admin/accounts", json={
        "name": "Andi Wijaya",
        "bank_name": "Bank Digital",
        "initial_deposit": 100000
    })
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["name"] == "Andi Wijaya"
    assert res_data["balance"] == 100000
    assert len(data.accounts) == 1

def test_create_account_insufficient_deposit():
    response = client.post("/admin/accounts", json={
        "name": "Candra",
        "bank_name": "Bank Digital",
        "initial_deposit": 40000 # Kurang dari minimum balance
    })
    assert response.status_code == 400
    assert "Setoran awal minimal" in response.json()["detail"]

def test_get_all_accounts():
    # Buat 2 akun dulu
    client.post("/admin/accounts", json={"name": "Akun 1", "bank_name": "A", "initial_deposit": 100000})
    client.post("/admin/accounts", json={"name": "Akun 2", "bank_name": "B", "initial_deposit": 200000})
    
    response = client.get("/admin/accounts")
    assert response.status_code == 200
    res_data = response.json()
    assert len(res_data) == 2
    assert "balance" not in res_data[0] # Admin tidak boleh lihat saldo

def test_update_account_info():
    create_res = client.post("/admin/accounts", json={
        "name": "Nama Lama",
        "bank_name": "Bank Lama",
        "initial_deposit": 150000
    })
    acc_num = create_res.json()["account_number"]
    
    response = client.put(f"/admin/accounts/{acc_num}", json={
        "name": "Nama Baru"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Nama Baru"
    assert response.json()["bank_name"] == "Bank Lama" # Tidak berubah

def test_deactivate_account():
    create_res = client.post("/admin/accounts", json={
        "name": "User Aktif",
        "bank_name": "Bank Digital",
        "initial_deposit": 200000
    })
    acc_num = create_res.json()["account_number"]

    # Deaktivasi
    response = client.delete(f"/admin/accounts/{acc_num}")
    assert response.status_code == 200
    assert "berhasil dinonaktifkan" in response.json()["message"]
    
    # Coba akses akun yang sudah tidak aktif
    get_res = client.get(f"/accounts/{acc_num}/balance")
    assert get_res.status_code == 403 # Forbidden
    assert get_res.json()["detail"] == "Akun tidak aktif"