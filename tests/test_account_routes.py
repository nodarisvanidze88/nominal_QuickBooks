import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
from main import app
from database.session import get_db

client = TestClient(app)


@pytest.fixture
def mock_token():
    token = MagicMock()
    token.access_token = "valid"
    token.realm_id = "12345"
    return token


@pytest.fixture
def mock_account_data():
    return {
        "QueryResponse": {
            "Account": [
                {
                    "Id": "1",
                    "Name": "Bank",
                    "Classification": "Asset",
                    "CurrencyRef": {"value": "USD"},
                    "AccountType": "Bank",
                    "Active": True,
                    "CurrentBalance": 1500.0,
                    "SubAccount": False
                }
            ]
        }
    }

def test_sync_accounts_success(mock_token, mock_account_data):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_account_data

    db = MagicMock()
    db.query.return_value.all.return_value = [
        SimpleNamespace(
            id=1,
            name="Bank",
            classification="Asset",
            currency="USD",
            account_type="Bank",
            active=True,
            current_balance=1500.0,
            parent_id=None
        )
    ]

    def override_get_db():
        yield db

    with patch("routes.account_routes.get_latest_token", return_value=mock_token), \
         patch("routes.account_routes.fetch_accounts_from_qbo", return_value=mock_response), \
         patch("routes.account_routes.refresh_token") as mock_refresh:

        app.dependency_overrides[get_db] = override_get_db

        response = client.get("/accounts")

        assert response.status_code == 200
        assert response.json()[0]["name"] == "Bank"
        db.merge.assert_called_once()
        db.commit.assert_called_once()
        mock_refresh.assert_not_called()

        app.dependency_overrides = {}

def test_sync_accounts_expired_token(mock_token, mock_account_data):
    expired_token = MagicMock()
    expired_token.access_token = "expired"
    expired_token.realm_id = "12345"

    unauthorized_response = MagicMock()
    unauthorized_response.status_code = 401

    refreshed_response = MagicMock()
    refreshed_response.status_code = 200
    refreshed_response.json.return_value = mock_account_data

    db = MagicMock()
    db.query.return_value.all.return_value = [
        SimpleNamespace(
            id=1,
            name="Bank",
            classification="Asset",
            currency="USD",
            account_type="Bank",
            active=True,
            current_balance=1500.0,
            parent_id=None
        )
    ]

    def override_get_db():
        yield db

    with patch("routes.account_routes.get_latest_token", return_value=expired_token), \
         patch("routes.account_routes.fetch_accounts_from_qbo", side_effect=[unauthorized_response, refreshed_response]), \
         patch("routes.account_routes.refresh_token", return_value=mock_token):

        app.dependency_overrides[get_db] = override_get_db

        response = client.get("/accounts")

        assert response.status_code == 200
        assert response.json()[0]["name"] == "Bank"
        db.merge.assert_called_once()
        db.commit.assert_called_once()

        app.dependency_overrides = {}

def test_sync_accounts_no_token():
    db = MagicMock()

    def override_get_db():
        yield db

    with patch("routes.account_routes.get_latest_token", return_value=None), \
         patch("routes.account_routes.raise_token_not_found") as mock_raise:

        app.dependency_overrides[get_db] = override_get_db

        client.get("/accounts")

        mock_raise.assert_called_once()

        app.dependency_overrides = {}

def test_sync_accounts_fetch_fails(mock_token):
    failed_response = MagicMock()
    failed_response.status_code = 500
    failed_response.json.return_value = {"error": "Internal Server Error"}

    db = MagicMock()

    def override_get_db():
        yield db

    with patch("routes.account_routes.get_latest_token", return_value=mock_token), \
         patch("routes.account_routes.fetch_accounts_from_qbo", return_value=failed_response):

        app.dependency_overrides[get_db] = override_get_db

        response = client.get("/accounts")

        assert response.status_code == 200
        assert "error" in response.json()

        app.dependency_overrides = {}
