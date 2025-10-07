# digital_banking/tests/test_admin_api.py

from fastapi.testclient import TestClient
from digital_banking.main import app
from digital_banking.database import accounts_db, transactions_db
from digital_banking.models import AccountCreate
from digital_banking import services


client = TestClient(app)

def setup_function():
    """Clear databases before each test."""
    accounts_db.clear()
    transactions_db.clear()

def test_create_account():
    response = client.post("/admin/accounts/", json={"name": "Budi Santoso", "bank_name": "Bank Digital API"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Budi Santoso"
    assert data["balance"] == 0.0
    assert data["is_active"] is True
    assert len(accounts_db) == 1

def test_get_all_accounts():
    # Create two accounts first
    client.post("/admin/accounts/", json={"name": "Andi", "bank_name": "Bank A"})
    client.post("/admin/accounts/", json={"name": "Citra", "bank_name": "Bank B"})
    
    response = client.get("/admin/accounts/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Admin view should not contain balance
    assert "balance" not in data[0]

def test_update_account_info():
    res_create = client.post("/admin/accounts/", json={"name": "Joko", "bank_name": "Bank C"})
    acc_num = res_create.json()["account_number"]
    
    response = client.put(f"/admin/accounts/{acc_num}/", json={"name": "Joko Susilo"})
    assert response.status_code == 200
    assert response.json()["name"] == "Joko Susilo"
    assert accounts_db[acc_num]["name"] == "Joko Susilo"

def test_deactivate_account():
    res_create = client.post("/admin/accounts/", json={"name": "Eka", "bank_name": "Bank D"})
    acc_num = res_create.json()["account_number"]
    
    assert accounts_db[acc_num]["is_active"] is True
    response = client.delete(f"/admin/accounts/{acc_num}/")
    assert response.status_code == 200
    assert accounts_db[acc_num]["is_active"] is False

def test_admin_get_all_accounts_hides_balance():
    """
    Memverifikasi bahwa endpoint GET /admin/accounts/ TIDAK menampilkan field 'balance'.
    """
    # 1. SETUP: Buat akun baru terlebih dahulu
    response_create = client.post(
        "/admin/accounts/", 
        json={"name": "Nasabah Rahasia", "bank_name": "Bank Aman"}
    )
    assert response_create.status_code == 201
    created_account = response_create.json()
    account_number = created_account["account_number"]

    # Secara manual, kita set saldonya agar tidak nol untuk pembuktian
    accounts_db[account_number]["balance"] = 500000.0

    # 2. ACTION: Panggil endpoint admin untuk mendapatkan daftar akun
    response_get = client.get("/admin/accounts/")
    
    # 3. ASSERTION: Periksa hasilnya
    assert response_get.status_code == 200
    accounts_list = response_get.json()

    # Pastikan data yang kembali adalah list dan tidak kosong
    assert isinstance(accounts_list, list)
    assert len(accounts_list) > 0

    # Ambil data akun pertama dari daftar
    first_account_from_admin_view = accounts_list[0]

    # Pastikan 'balance' TIDAK ADA dalam respons
    assert "balance" not in first_account_from_admin_view

    # Pastikan field yang seharusnya ada, memang ada
    assert "account_number" in first_account_from_admin_view
    assert "name" in first_account_from_admin_view
    assert "bank_name" in first_account_from_admin_view