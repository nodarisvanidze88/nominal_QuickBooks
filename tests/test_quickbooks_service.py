import pytest
from unittest.mock import patch, MagicMock
from services.quickbooks_service import fetch_accounts_from_qbo, sync_qbo_accounts
from models.token import Token
from requests.exceptions import RequestException
from requests.models import Response
from core.config import ACCOUNT_API_URL

@pytest.fixture
def mock_token():
    token = MagicMock(spec=Token)
    token.access_token = "abc123"
    token.realm_id = "12345"
    return token


def test_fetch_accounts_success(mock_token):
    """
    Test the fetch_accounts_from_qbo function with a valid token and successful account fetch.
    """
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 200

    with patch("services.quickbooks_service.requests.get", return_value=mock_response) as mock_get:
        response = fetch_accounts_from_qbo(mock_token)

        expected_url = ACCOUNT_API_URL.format(realm_id="12345") + "?query=select * from Account&minorversion=65"
        expected_headers = {
            "Authorization": "Bearer abc123",
            "Accept": "application/json",
            "Content-Type": "application/text"
        }

        mock_get.assert_called_once_with(expected_url, headers=expected_headers)
        assert response.status_code == 200


def test_fetch_accounts_retries_on_failure(mock_token):
    """
    Test that the function retries on failure using backoff.
    """
    with patch("services.quickbooks_service.requests.get", side_effect=RequestException("Network error")) as mock_get:
        with pytest.raises(RequestException):
            fetch_accounts_from_qbo(mock_token)

        assert mock_get.call_count == 3  # Because of backoff max_tries=3

def test_sync_qbo_accounts_success():
    db = MagicMock()
    mock_token = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "QueryResponse": {
            "Account": [
                {"Id": "1", "Name": "Cash", "AccountType": "Bank"},
                {"Id": "2", "Name": "Revenue", "AccountType": "Income"},
            ]
        }
    }

    with patch("services.quickbooks_service.get_latest_token", return_value=mock_token), \
         patch("services.quickbooks_service.fetch_accounts_from_qbo", return_value=mock_response), \
         patch("services.quickbooks_service.save_accounts_to_db") as mock_save:

        result = sync_qbo_accounts(db)

        mock_save.assert_called_once()
        db.query.assert_called_once()