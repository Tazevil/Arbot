import os
import sys
import urllib.parse

import pytest


def test_oauth_manager_builds_auth_url(monkeypatch):
    monkeypatch.setenv("OPENAI_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("OPENAI_CLIENT_SECRET", "test_client_secret")
    monkeypatch.setenv("OPENAI_REDIRECT_URI", "http://localhost:8000/callback")

    # Ensure repository root on path
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from oauth_token_manager import OAuthTokenManager

    mgr = OAuthTokenManager()
    url = mgr.get_authorization_url()
    parsed = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(parsed.query)

    assert parsed.scheme in {"http", "https"}
    assert qs.get("client_id", [None])[0] == "test_client_id"
    assert qs.get("redirect_uri", [None])[0] == "http://localhost:8000/callback"
    assert qs.get("response_type", [None])[0] == "code"
