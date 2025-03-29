from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from models.account import Account
from main import app
from schemas.account import AccountOut
from database.session import get_db

client = TestClient(app)

def override_get_db():
    db = MagicMock()
    yield db


def test_sync_accounts_route_success():
    dummy_accounts = [
        AccountOut(
            id=1,
            name="Bank Account",
            account_type="Bank",
            classification="Asset",
            currency="USD",
            active=True,
            current_balance=1000.0
        ),
        AccountOut(
            id=2,
            name="Sales Account",
            account_type="Income",
            classification="Revenue",
            currency="USD",
            active=True,
            current_balance=3000.5
        )
    ]

    app.dependency_overrides[get_db] = override_get_db

    with patch("routes.account_routes.sync_qbo_accounts", return_value=dummy_accounts):
        response = client.get("/accounts")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert response.json()[0]["name"] == "Bank Account"

    app.dependency_overrides = {}  # Clean up


def test_search_accounts():
    mock_account = Account(
        id=1,
        name="Test Account",
        classification="Asset",
        currency="USD",
        account_type="Bank",
        active=True,
        current_balance=100.0
    )

    mock_db = MagicMock()

    # Emulate .filter().filter().all() by chaining return values
    mock_query = mock_db.query.return_value
    mock_filter_1 = mock_query.filter.return_value
    mock_filter_2 = mock_filter_1.filter.return_value
    mock_filter_2.all.return_value = [mock_account]

    def override_get_db_for_search():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db_for_search

    response = client.get("/accounts/search", params={"active": True, "classification": "Asset"})

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert data[0]["id"] == 1
    assert data[0]["name"] == "Test Account"
    assert data[0]["classification"] == "Asset"
    assert data[0]["currency"] == "USD"
    assert data[0]["active"] is True
    assert data[0]["current_balance"] == 100.0

    app.dependency_overrides = {}  # Clean up
