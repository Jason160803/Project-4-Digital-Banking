from fastapi.testclient import TestClient
from digital_banking.main import app
from digital_banking.database import accounts_db, transactions_db

client = TestClient(app)

def setup_function():
    """Clear databases before each test."""
    accounts_db.clear()
    transactions_db.clear()

def test_create_account():
    # TAMBAHKAN "pin" di sini
    response = client.post("/admin/accounts/", json={"name": "Budi Santoso", "bank_name": "Bank Digital API", "pin": "123456"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Budi Santoso"
    assert "pin" not in data # Pastikan PIN tidak dikembalikan di respons

def test_get_all_accounts():
    # TAMBAHKAN "pin" di kedua post
    client.post("/admin/accounts/", json={"name": "Andi", "bank_name": "Bank A", "pin": "111111"})
    client.post("/admin/accounts/", json={"name": "Citra", "bank_name": "Bank B", "pin": "222222"})
    
    response = client.get("/admin/accounts/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_update_account_info():
    # TAMBAHKAN "pin" di sini
    res_create = client.post("/admin/accounts/", json={"name": "Joko", "bank_name": "Bank C", "pin": "333333"})
    acc_num = res_create.json()["account_number"]
    
    response = client.put(f"/admin/accounts/{acc_num}/", json={"name": "Joko Susilo"})
    assert response.status_code == 200
    assert response.json()["name"] == "Joko Susilo"

def test_deactivate_account():
    # TAMBAHKAN "pin" di sini
    res_create = client.post("/admin/accounts/", json={"name": "Eka", "bank_name": "Bank D", "pin": "444444"})
    acc_num = res_create.json()["account_number"]
    
    assert accounts_db[acc_num]["is_active"] is True
    response = client.delete(f"/admin/accounts/{acc_num}/")
    assert response.status_code == 200
    assert accounts_db[acc_num]["is_active"] is False

def test_admin_get_all_accounts_hides_balance():
    # TAMBAHKAN "pin" di sini
    response_create = client.post(
        "/admin/accounts/", 
        json={"name": "Nasabah Rahasia", "bank_name": "Bank Aman", "pin": "555555"}
    )
    assert response_create.status_code == 201
    account_number = response_create.json()["account_number"]
    accounts_db[account_number]["balance"] = 500000.0

    response_get = client.get("/admin/accounts/")
    assert response_get.status_code == 200
    accounts_list = response_get.json()
    assert len(accounts_list) > 0
    first_account = accounts_list[0]
    assert "balance" not in first_account