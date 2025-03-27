from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pytest
from types import SimpleNamespace
from main import app

client = TestClient(app)


@pytest.fixture
def mock_token():
    token = MagicMock()
    token.access_token = "valid"
    token.realm_id = "12345"
    return token


@pytest.fixture
def mock_account_response():
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {
        "QueryResponse": {
            "Account": [
                {
                    "Name": "Bank",
                    "Classification": "Asset",
                    "CurrencyRef": {"value": "USD"},
                    "AccountType": "Bank",
                    "Active": True,
                    "CurrentBalance": 1500.0
                }
            ]
        }
    }
    return response


@pytest.fixture
def fake_account_object():
    return SimpleNamespace(
        name="Bank",
        classification="Asset",
        currency="USD",
        account_type="Bank",
        active=True,
        current_balance=1500.0
    )


@pytest.fixture
def mock_db(fake_account_object):
    db = MagicMock()
    db.query.return_value.all.return_value = [fake_account_object]
    db.merge.return_value = None
    db.commit.return_value = None
    return db


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_accounts_route_with_valid_token(mock_token, mock_account_response, mock_db):
    with patch("services.quickbooks_service.get_latest_token", return_value=mock_token), \
         patch("services.quickbooks_service.fetch_accounts_from_qbo", return_value=mock_account_response), \
         patch("database.session.get_db", side_effect=lambda: iter([mock_db])):
        response = client.get("/accounts")
        assert response.status_code == 200
        assert response.json()[0]["name"] == "Bank"


def test_accounts_route_with_expired_token(mock_token, mock_account_response, mock_db):
    expired_token = MagicMock()
    expired_token.access_token = "expired"
    expired_token.realm_id = "12345"

    unauthorized_response = MagicMock()
    unauthorized_response.status_code = 401

    with patch("services.quickbooks_service.get_latest_token", return_value=expired_token), \
         patch("services.quickbooks_service.fetch_accounts_from_qbo", side_effect=[unauthorized_response, mock_account_response]), \
         patch("services.quickbooks_service.refresh_token", return_value=mock_token), \
         patch("database.session.get_db", side_effect=lambda: iter([mock_db])):
        response = client.get("/accounts")
        assert response.status_code == 200
        assert response.json()[0]["name"] == "Bank"


def test_accounts_route_failure(mock_token):
    failed_response = MagicMock()
    failed_response.status_code = 500
    failed_response.json.return_value = {"error": "Internal Server Error"}

    db = MagicMock()

    with patch("services.quickbooks_service.get_latest_token", return_value=mock_token), \
         patch("services.quickbooks_service.fetch_accounts_from_qbo", return_value=failed_response), \
         patch("database.session.get_db", side_effect=lambda: iter([db])):
        response = client.get("/accounts")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
        assert "error" in response.json()
        assert response.json()["error"] == "Failed to fetch accounts"


def test_account_merge_called_for_each_account(mock_token, mock_account_response):
    db = MagicMock()
    db.query.return_value.all.return_value = []
    db.merge.return_value = None
    db.commit.return_value = None

    with patch("services.quickbooks_service.get_latest_token", return_value=mock_token), \
         patch("services.quickbooks_service.fetch_accounts_from_qbo", return_value=mock_account_response), \
         patch("database.session.get_db", side_effect=lambda: iter([db])):
        client.get("/accounts")
        assert db.merge.call_count == 1
        assert db.commit.called


def test_search_accounts(fake_account_object):
    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = [fake_account_object]

    with patch("database.session.get_db", side_effect=lambda: iter([db])):
        response = client.get("/accounts/search?active=true&classification=Asset")
        assert response.status_code == 200
        assert response.json()[0]["classification"] == "Asset"
