# digital_banking/tests/test_admin_api.py

from fastapi.testclient import TestClient
from ..main import app
from ..database import accounts_db, transactions_db

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