import pytest
from unittest.mock import patch, MagicMock
from services.quickbooks_service import fetch_accounts_from_qbo, sync_qbo_accounts, build_account_tree
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

def test_build_account_tree_single_root():
    account1 = MagicMock(id=1, name="Root Account", parent_id=None)
    account2 = MagicMock(id=2, name="Child Account", parent_id=1)
    account3 = MagicMock(id=3, name="Another Child", parent_id=1)

    accounts = [account1, account2, account3]

    tree = build_account_tree(accounts)

    assert len(tree) == 1
    assert tree[0]["id"] == 1
    assert len(tree[0]["children"]) == 2
    child_ids = {child["id"] for child in tree[0]["children"]}
    assert child_ids == {2, 3}


def test_build_account_tree_multiple_roots():
    account1 = MagicMock(id=1, name="Root A", parent_id=None)
    account2 = MagicMock(id=2, name="Root B", parent_id=None)
    account3 = MagicMock(id=3, name="Child of A", parent_id=1)
    account4 = MagicMock(id=4, name="Child of B", parent_id=2)

    accounts = [account1, account2, account3, account4]

    tree = build_account_tree(accounts)

    assert len(tree) == 2
    root_ids = {node["id"] for node in tree}
    assert root_ids == {1, 2}

    for node in tree:
        if node["id"] == 1:
            assert node["children"][0]["id"] == 3
        if node["id"] == 2:
            assert node["children"][0]["id"] == 4


def test_build_account_tree_orphan_node():
    account1 = MagicMock(id=1, name="Root", parent_id=None)
    account2 = MagicMock(id=2, name="Orphan", parent_id=99)  # 99 does not exist

    accounts = [account1, account2]
    tree = build_account_tree(accounts)

    assert len(tree) == 1
    assert tree[0]["id"] == 1
    assert len(tree[0]["children"]) == 0  # Orphan should be ignored