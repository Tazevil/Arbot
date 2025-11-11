#!/usr/bin/env python3
"""
OAuth Token Manager for OpenAI API
Handles authorization, refresh, secure storage, and revocation.
"""

import os
import json
import webbrowser
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlencode
from datetime import datetime, timedelta

# 'requests' is imported lazily inside methods to avoid import-time failures

# Storage
OAUTH_DIR = Path(".oauth")
TOKEN_FILE = OAUTH_DIR / "openai_token.json"


def _load_env_local():
    """Load simple KEY=VALUE lines from .env.local into os.environ if present."""
    env_path = Path(".env.local")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth redirect and capture the authorization code."""
    auth_code = None

    def do_GET(self):
        qs = ""
        if "?" in self.path:
            qs = self.path.split("?", 1)[1]
        query = parse_qs(qs)

        if "code" in query:
            OAuthCallbackHandler.auth_code = query["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"""<html><body style="font-family: Arial; text-align:center; padding:48px">
                    <h1>Authorization Successful</h1>
                    <p>You can close this window and return to the terminal.</p>
                </body></html>"""
            )
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Authorization Failed</h1></body></html>")

    def log_message(self, fmt, *args):
        # Silence server logs
        return


class OAuthTokenManager:
    """Manage OAuth tokens for OpenAI API."""

    AUTH_URL = "https://api.openai.com/oauth/authorize"
    TOKEN_URL = "https://api.openai.com/oauth/token"
    REVOKE_URL = "https://api.openai.com/oauth/revoke"

    def __init__(self):
        _load_env_local()
        self.client_id = os.getenv("OPENAI_CLIENT_ID")
        self.client_secret = os.getenv("OPENAI_CLIENT_SECRET")
        self.redirect_uri = os.getenv("OPENAI_REDIRECT_URI", "http://localhost:8000/callback")
        if not self.client_id or not self.client_secret:
            raise ValueError("OPENAI_CLIENT_ID and OPENAI_CLIENT_SECRET must be set")

        OAUTH_DIR.mkdir(exist_ok=True)

    def get_authorization_url(self) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "read:models write:files read:files",
        }
        return f"{self.AUTH_URL}?{urlencode(params)}"

    def request_authorization(self) -> str:
        print("\n== OpenAI OAuth Authorization ==")
        url = self.get_authorization_url()
        print("Opening browser for authorization...")
        print(f"If it doesn't open, visit:\n{url}\n")

        server = HTTPServer(("localhost", 8000), OAuthCallbackHandler)
        webbrowser.open(url)
        print("Waiting for callback at http://localhost:8000/callback ...")

        while OAuthCallbackHandler.auth_code is None:
            server.handle_request()

        auth_code = OAuthCallbackHandler.auth_code
        server.server_close()
        print("Authorization received.")
        return auth_code

    def exchange_code_for_token(self, auth_code: str) -> dict:
        print("Exchanging authorization code for access token...")
        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
        }
        import requests  # lazy import
        resp = requests.post(self.TOKEN_URL, data=data, headers={"Accept": "application/json"})
        resp.raise_for_status()
        token = resp.json()
        token["obtained_at"] = datetime.utcnow().isoformat()
        print("Access token obtained.")
        return token

    def save_token(self, token: dict):
        TOKEN_FILE.write_text(json.dumps(token), encoding="utf-8")
        try:
            if os.name == "posix":
                os.chmod(TOKEN_FILE, 0o600)
        except Exception:
            pass
        print(f"Token saved to {TOKEN_FILE}")

    def load_token(self) -> dict | None:
        if not TOKEN_FILE.exists():
            return None
        return json.loads(TOKEN_FILE.read_text(encoding="utf-8"))

    def is_token_expired(self, token: dict) -> bool:
        if not token or "obtained_at" not in token:
            return True
        obtained = datetime.fromisoformat(token["obtained_at"])
        expires_in = int(token.get("expires_in", 3600))
        return datetime.utcnow() > (obtained + timedelta(seconds=expires_in))

    def refresh_token(self, token: dict) -> dict | None:
        if "refresh_token" not in token:
            print("No refresh token; re-authorization required.")
            return None
        print("Refreshing token...")
        data = {
            "grant_type": "refresh_token",
            "refresh_token": token["refresh_token"],
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        import requests  # lazy import
        resp = requests.post(self.TOKEN_URL, data=data, headers={"Accept": "application/json"})
        if not resp.ok:
            print(f"Token refresh failed: {resp.status_code} {resp.text}")
            return None
        new_token = resp.json()
        new_token["obtained_at"] = datetime.utcnow().isoformat()
        print("Token refreshed.")
        return new_token

    def get_valid_token(self) -> str:
        token = self.load_token()
        if token and not self.is_token_expired(token):
            print("Using cached token.")
            return token["access_token"]
        if token and self.is_token_expired(token):
            refreshed = self.refresh_token(token)
            if refreshed:
                self.save_token(refreshed)
                return refreshed["access_token"]
        code = self.request_authorization()
        token = self.exchange_code_for_token(code)
        self.save_token(token)
        return token["access_token"]

    def revoke_token(self):
        if not TOKEN_FILE.exists():
            return
        token = self.load_token() or {}
        try:
            import requests  # lazy import
            requests.post(self.REVOKE_URL, data={
                "token": token.get("access_token", ""),
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            })
            print("Token revoked on server (if supported).")
        except Exception:
            print("Could not revoke token on server.")
        try:
            TOKEN_FILE.unlink()
            print("Local token file removed.")
        except FileNotFoundError:
            pass


def main() -> int:
    try:
        manager = OAuthTokenManager()
        print("Getting valid token...")
        token = manager.get_valid_token()
        print(f"Obtained token: {token[:20]}...{token[-10:]}")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
