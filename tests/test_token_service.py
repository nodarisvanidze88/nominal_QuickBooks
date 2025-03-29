from unittest.mock import patch, MagicMock
import pytest
from requests.models import Response
from models.token import Token
from services.token_service import get_valid_token, get_latest_token, save_tokens_to_db, refresh_token
from intuitlib.exceptions import AuthClientError
from fastapi import HTTPException


def test_get_valid_token_with_valid_token():
    """
    Test the get_valid_token function when a valid token is found in the database.
    """
    token = MagicMock(spec=Token)
    token.is_token_expired.return_value = False

    db = MagicMock()
    db.query.return_value.order_by.return_value.first.return_value = token

    result = get_valid_token(db)
    assert result == token
    token.is_token_expired.assert_called_once()

def test_get_valid_token_with_expired_token():
    """
    Test the get_valid_token function when the token is expired and needs to be refreshed.
    """
    expired_token = MagicMock(spec=Token)
    expired_token.is_token_expired.return_value = True

    refreshed_token = MagicMock(spec=Token)

    db = MagicMock()
    db.query.return_value.order_by.return_value.first.return_value = expired_token

    with patch("services.token_service.refresh_token", return_value=refreshed_token):
        result = get_valid_token(db)
        expired_token.is_token_expired.assert_called_once()
        assert result == refreshed_token

def test_get_valid_token_with_no_token():
    """
    Test the get_valid_token function when no token is found in the database.
    """
    db = MagicMock()
    db.query.return_value.order_by.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        get_valid_token(db)

    assert exc_info.value.status_code == 400
    assert "QuickBooks Error" in exc_info.value.detail

def test_get_latest_token_returns_token():
    """
    Test the get_latest_token function when a token is found in the database.
    """
    latest_token = MagicMock(spec=Token)

    db = MagicMock()
    db.query.return_value.order_by.return_value.first.return_value = latest_token

    result = get_latest_token(db)

    db.query.assert_called_once_with(Token)
    assert result == latest_token

def test_get_latest_token_returns_none_when_no_token():
    """
    Test the get_latest_token function when no token is found in the database.
    """
    db = MagicMock()
    db.query.return_value.order_by.return_value.first.return_value = None

    result = get_latest_token(db)

    db.query.assert_called_once_with(Token)
    assert result is None

def test_save_tokens_to_db():
    """
    Test the save_tokens_to_db function with valid token data.
    """
    token_data = {
        "access_token": "abc123",
        "refresh_token": "refresh456",
        "expires_in": 3600,
        "realm_id": "78910",
        "token_type": "Bearer"
    }

    db = MagicMock()

    with patch("services.token_service.Token") as MockToken:
        mock_token_instance = MockToken.return_value

        save_tokens_to_db(db, token_data)

        MockToken.assert_called_once_with(
            access_token="abc123",
            refresh_token="refresh456",
            expires_in=3600,
            realm_id="78910",
            token_type="Bearer"
        )

        db.merge.assert_called_once_with(mock_token_instance)
        assert db.commit.call_count == 2

def test_refresh_token_success():
    """
    Test the refresh_token function when the auth client returns a new token successfully.
    """
    db = MagicMock()
    token = MagicMock(spec=Token)
    token.realm_id = "12345"
    token.refresh_token = "old-refresh"

    with patch("services.token_service.auth_client") as mock_auth_client, \
         patch("services.token_service.save_tokens_to_db") as mock_save_tokens, \
         patch("services.token_service.get_latest_token") as mock_get_latest:

        mock_auth_client.access_token = "new-access"
        mock_auth_client.refresh_token = "new-refresh"
        mock_auth_client.expires_in = 3600

        mock_get_latest.return_value = "latest-token"

        result = refresh_token(db, token)

        mock_auth_client.refresh.assert_called_once_with(refresh_token="old-refresh")
        mock_save_tokens.assert_called_once_with(db, {
            "access_token": "new-access",
            "refresh_token": "new-refresh",
            "expires_in": 3600,
            "realm_id": "12345",
            "token_type": "Bearer"
        })
        mock_get_latest.assert_called_once()
        assert result == "latest-token"


def test_refresh_token_failure():
    """
    Test the refresh_token function when the auth client raises an error.
    """
    db = MagicMock()
    token = MagicMock(spec=Token)
    token.realm_id = "12345"
    token.refresh_token = "old-refresh"
    fake_response = Response()
    fake_response.status_code = 400
    fake_response._content = b'{"error":"invalid_grant","error_description":"Incorrect or invalid refresh token"}'

    with patch("core.config.auth_client") as mock_auth_client:
        mock_auth_client.refresh.side_effect = AuthClientError(fake_response)

        with pytest.raises(HTTPException) as exc_info:
            refresh_token(db, token)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail["error"] == "Failed to refresh access token"
        assert "invalid refresh token" in exc_info.value.detail["details"]

