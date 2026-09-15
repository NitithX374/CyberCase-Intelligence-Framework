"""OAuth client adapter for Google provider."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode

import httpx
from app.config import settings


@dataclass(frozen=True)
class OAuthUserProfile:
    provider: str
    subject_id: str
    email: str
    name: str
    avatar_url: str | None = None


class OAuthProviderClient:
    """Base class for OAuth identity providers."""

    def get_authorization_url(self, state: str) -> str:
        raise NotImplementedError

    async def exchange_code_for_profile(self, code: str) -> OAuthUserProfile:
        raise NotImplementedError


class GoogleOAuthClient(OAuthProviderClient):
    AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
    USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v3/userinfo"

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        redirect_uri: str | None = None,
    ):
        self.client_id = client_id or settings.oauth_google_client_id
        self.client_secret = client_secret or settings.oauth_google_client_secret
        self.redirect_uri = redirect_uri or settings.oauth_google_redirect_uri
        if not self.client_id or not self.client_secret:
            raise ValueError("Google OAuth is not configured on this server")

    def get_authorization_url(self, state: str) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "select_account",
        }
        return f"{self.AUTH_ENDPOINT}?{urlencode(params)}"

    async def exchange_code_for_profile(self, code: str) -> OAuthUserProfile:
        async with httpx.AsyncClient(timeout=15.0) as client:
            token_resp = await client.post(
                self.TOKEN_ENDPOINT,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                },
                headers={"Accept": "application/json"},
            )
            token_resp.raise_for_status()
            token_data = token_resp.json()
            access_token = token_data.get("access_token")
            if not access_token:
                raise ValueError("Missing access_token in Google OAuth response")

            userinfo_resp = await client.get(
                self.USERINFO_ENDPOINT,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            userinfo_resp.raise_for_status()
            info = userinfo_resp.json()

            if not info.get("email") or info.get("email_verified") is not True:
                raise ValueError("Google must supply a verified email")
            return OAuthUserProfile(
                provider="google",
                subject_id=str(info["sub"]),
                email=info.get("email", ""),
                name=info.get("name") or info.get("email", "").split("@")[0] or "Google User",
                avatar_url=info.get("picture"),
            )


def get_oauth_client(provider: str) -> OAuthProviderClient:
    provider_lower = provider.lower()
    if provider_lower == "google":
        return GoogleOAuthClient()
    raise ValueError(f"Unsupported OAuth provider: {provider}")
