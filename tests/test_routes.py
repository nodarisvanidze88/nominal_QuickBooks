from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
import pytest

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

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_accounts_route_with_valid_token(mock_token, mock_account_response):
    with patch("services.token_service.get_valid_token", return_value=mock_token), \
         patch("services.quickbooks_service.fetch_accounts_from_qbo", return_value=mock_account_response):

        response = client.get("/accounts")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert response.json()[0]["name"] == "Bank"
        assert response.json()[0]["currency"] == "USD"

def test_accounts_route_with_expired_token(mock_token, mock_account_response):
    expired_token = MagicMock()
    expired_token.access_token = "expired"
    expired_token.realm_id = "12345"

    unauthorized_response = MagicMock()
    unauthorized_response.status_code = 401
    mock_auth_client = MagicMock()
    mock_auth_client.refresh_access_token.return_value = {
        "access_token": "new_valid_token",
        "refresh_token": "new_refresh_token",
        "expires_in": 3600
    }

    with patch("services.token_service.get_valid_token", return_value=expired_token), \
         patch("services.quickbooks_service.fetch_accounts_from_qbo", side_effect=[unauthorized_response, mock_account_response]), \
         patch("services.quickbooks_service.refresh_token", return_value=mock_token):

        response = client.get("/accounts")
        assert response.status_code == 200
        assert response.json()[0]["name"] == "Bank"

def test_accounts_route_failure(mock_token):
    failed_response = MagicMock()
    failed_response.status_code = 500
    failed_response.json.return_value = {"error": "Internal Server Error"}

    with patch("services.token_service.get_valid_token", return_value=mock_token), \
         patch("services.quickbooks_service.fetch_accounts_from_qbo", return_value=failed_response):

        response = client.get("/accounts")
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"] == "Failed to fetch accounts"

def test_expired_token_refreshes_and_saves(mock_token, mock_account_response):
    with patch("services.token_service.get_valid_token", return_value=mock_token), \
         patch("services.quickbooks_service.fetch_accounts_from_qbo", side_effect=[MagicMock(status_code=401), mock_account_response]), \
         patch("services.quickbooks_service.refresh_token", return_value=mock_token) as refresh_mock:

        response = client.get("/accounts")
        assert response.status_code == 200
        assert refresh_mock.called



def test_account_merge_called_for_each_account(mock_token, mock_account_response):
    with patch("services.token_service.get_valid_token", return_value=mock_token), \
         patch("services.quickbooks_service.fetch_accounts_from_qbo", return_value=mock_account_response), \
         patch("database.session.SessionLocal.merge") as merge_mock, \
         patch("database.session.SessionLocal.commit") as commit_mock:

        response = client.get("/accounts")
        assert response.status_code == 200
        assert merge_mock.call_count == 1
        assert commit_mock.called
