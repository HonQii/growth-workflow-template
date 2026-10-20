"""Lazy optional authentication; credentials are never printed or persisted."""
import os
from pathlib import Path
import time
from .core import fail


def google_token(scope):
    credentials = None

    def token():
        nonlocal credentials
        value = os.environ.get("GROWTH_GOOGLE_ACCESS_TOKEN")
        if value:
            return value
        try:
            import google.auth
            from google.auth.transport.requests import Request
        except ImportError:
            fail("missing_dependency", "Install requirements.txt for Google ADC or supply GROWTH_GOOGLE_ACCESS_TOKEN.", "unavailable")
        try:
            if credentials is None:
                credentials, _ = google.auth.default(scopes=[scope])
            if not credentials.valid:
                request = Request()

                def bounded_request(*args, **kwargs):
                    kwargs["timeout"] = 30
                    return request(*args, **kwargs)

                credentials.refresh(bounded_request)
            return credentials.token
        except Exception:
            fail("credentials_unavailable", "Google ADC could not refresh credentials. Configure access for this source.", "unavailable")
    return token


def apple_token(settings):
    def token():
        value = os.environ.get("GROWTH_APPLE_ACCESS_TOKEN")
        if value:
            return value
        path = os.environ.get("GROWTH_APPLE_PRIVATE_KEY_PATH")
        key_id = os.environ.get("GROWTH_APPLE_KEY_ID") or settings.get("key_id")
        issuer_id = os.environ.get("GROWTH_APPLE_ISSUER_ID") or settings.get("issuer_id")
        if not path or not key_id or not issuer_id:
            fail("credentials_unavailable", "Provide an Apple access token or Apple key ID, issuer ID and private-key path.", "unavailable")
        try:
            import jwt
        except ImportError:
            fail("missing_dependency", "Install requirements.txt for Apple JWT signing or supply GROWTH_APPLE_ACCESS_TOKEN.", "unavailable")
        try:
            key = Path(path).expanduser().read_text()
            now = int(time.time())
            return jwt.encode({"iss":issuer_id,"iat":now,"exp":now+600,"aud":"appstoreconnect-v1"},key,algorithm="ES256",headers={"kid":key_id,"typ":"JWT"})
        except Exception:
            fail("credentials_unavailable", "Unable to read or sign with the configured Apple team key.", "unavailable")
    return token
