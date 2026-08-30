"""
Legal reference configuration
=============================
Everything the Thanoy integration needs from the environment, in one place.

Only `THANOY_API_URL` is required for the feature to do anything. With it
unset the client reports itself unconfigured and `/query` returns the other two
fields exactly as before — the deployment is valid, the field is simply empty.
That is the intended state until the endpoint is supplied, and it is why
nothing here raises on import.

The auth and request-shape settings are variables rather than constants because
the contract has not been confirmed. If Thanoy wants `X-API-Key: <key>` instead
of `Authorization: Bearer <key>`, or `question` instead of `query`, that is an
environment change and not a code change.
"""

from __future__ import annotations

import os

# ── required ─────────────────────────────────────────────────────────────
# Full URL of the endpoint that takes an incident description and returns
# relevant provisions, e.g. "https://api.example.co.th/v1/search".
THANOY_API_URL = os.getenv("THANOY_API_URL", "").strip()

# ── credentials ──────────────────────────────────────────────────────────
THANOY_API_KEY = os.getenv("THANOY_API_KEY", "")
# Header the key is sent in, and the scheme prefix. Set THANOY_AUTH_SCHEME to
# an empty string for services that want the bare key.
THANOY_AUTH_HEADER = os.getenv("THANOY_AUTH_HEADER", "Authorization")
THANOY_AUTH_SCHEME = os.getenv("THANOY_AUTH_SCHEME", "Bearer")

# ── request shape ────────────────────────────────────────────────────────
# JSON key the incident text is sent under.
THANOY_QUERY_FIELD = os.getenv("THANOY_QUERY_FIELD", "query")
THANOY_MAX_RESULTS = int(os.getenv("THANOY_MAX_RESULTS", "8"))

# ── budget ───────────────────────────────────────────────────────────────
# The router applies its own ceiling as well; this one bounds the socket.
THANOY_TIMEOUT_SECONDS = float(os.getenv("THANOY_TIMEOUT_SECONDS", "15"))

# Shown to the reader as the source of the provisions.
THANOY_PROVIDER_NAME = os.getenv("THANOY_PROVIDER_NAME", "thanoy")
