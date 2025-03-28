from unittest.mock import patch, MagicMock
from intuitlib.exceptions import AuthClientError
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_callback_successful_token_exchange():
    with patch("routes.auth_routes.auth_client") as mock_auth_client, \
         patch("services.token_service.save_tokens_to_db") as mock_save:

        mock_auth_client.get_bearer_token = MagicMock()
        mock_auth_client.access_token = "access"
        mock_auth_client.refresh_token = "refresh"
        mock_auth_client.expires_in = 3600
        mock_auth_client.realm_id = "12345"

        response = client.get("/callback?code=abc123&realmId=12345")

        mock_auth_client.get_bearer_token.assert_called_once_with("abc123", realm_id="12345")
        assert response.status_code == 200
        assert response.json()["message"] == "Authorization successful"


def test_callback_auth_client_error():
    with patch("core.config.auth_client") as mock_auth_client:
        mock_auth_client.get_bearer_token.side_effect = AuthClientError(response=MagicMock(status_code=400))

        response = client.get("/callback?code=badcode&realmId=12345")

        assert response.status_code == 200
        assert "error" in response.json()


def test_callback_missing_query_params():
    response = client.get("/callback")

    assert response.status_code == 200
    assert "error" in response.json() or "message" not in response.json()