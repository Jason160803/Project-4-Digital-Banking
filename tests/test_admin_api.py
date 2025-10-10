from fastapi.testclient import TestClient
from digital_banking.main import app
from digital_banking.database import accounts_db

client = TestClient(app)

def setup_function():
    accounts_db.clear()

def test_create_account():
    response = client.post("/admin/accounts/", json={"name": "Budi Santoso", "bank_name": "Bank Digital API", "pin": "123456", "initial_balance": 50000})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Budi Santoso"
    assert data["balance"] == 50000

def test_get_all_accounts():
    client.post("/admin/accounts/", json={"name": "Andi", "bank_name": "Bank A", "pin": "111111", "initial_balance": 20000})
    client.post("/admin/accounts/", json={"name": "Citra", "bank_name": "Bank B", "pin": "222222", "initial_balance": 30000})
    response = client.get("/admin/accounts/")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_update_account_info():
    res_create = client.post("/admin/accounts/", json={"name": "Joko", "bank_name": "Bank C", "pin": "333333", "initial_balance": 25000})
    acc_num = res_create.json()["account_number"]
    response = client.put(f"/admin/accounts/{acc_num}/", json={"name": "Joko Susilo"})
    assert response.status_code == 200
    assert response.json()["name"] == "Joko Susilo"

def test_delete_account(): # Nama fungsi & logika tes diubah
    res_create = client.post("/admin/accounts/", json={"name": "Eka", "bank_name": "Bank D", "pin": "444444", "initial_balance": 20000})
    acc_num = res_create.json()["account_number"]
    assert acc_num in accounts_db
    response = client.delete(f"/admin/accounts/{acc_num}/")
    assert response.status_code == 200
    assert acc_num not in accounts_db # Pastikan akun benar-benar hilang

def test_admin_get_all_accounts_hides_balance():
    response_create = client.post("/admin/accounts/", json={"name": "Nasabah Rahasia", "bank_name": "Bank Aman", "pin": "555555", "initial_balance": 100000})
    assert response_create.status_code == 201
    response_get = client.get("/admin/accounts/")
    assert response_get.status_code == 200
    first_account = response_get.json()[0]
    assert "balance" not in first_account