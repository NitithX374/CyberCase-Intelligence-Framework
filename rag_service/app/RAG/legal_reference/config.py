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
# iApp's Thai Legal Data search endpoint: a Thai fact pattern in, the sections
# it matches out. Chosen over the `/ask` endpoint on the same service, which
# returns a grounded legal answer — that is advice, and this field is meant to
# be a reference. Defaulted rather than left blank because the URL is public
# documentation, not a secret; only the key has to be supplied.
THANOY_API_URL = os.getenv(
    "THANOY_API_URL", "https://api.iapp.co.th/v3/store/data/thai-legal/search"
).strip()

# ── credentials ──────────────────────────────────────────────────────────
THANOY_API_KEY = os.getenv("THANOY_API_KEY", "")
# Header the key is sent in, and the scheme prefix. Set THANOY_AUTH_SCHEME to
# an empty string for services that want the bare key.
# iApp wants the bare key under `apikey`, not `Authorization: Bearer <key>`.
THANOY_AUTH_HEADER = os.getenv("THANOY_AUTH_HEADER", "apikey")
THANOY_AUTH_SCHEME = os.getenv("THANOY_AUTH_SCHEME", "")

# ── request shape ────────────────────────────────────────────────────────
# JSON key the incident text is sent under.
THANOY_QUERY_FIELD = os.getenv("THANOY_QUERY_FIELD", "query")
# The endpoint caps top_k at 20 and defaults to 8.
THANOY_MAX_RESULTS = min(int(os.getenv("THANOY_MAX_RESULTS", "8")), 20)

# ── budget ───────────────────────────────────────────────────────────────
# The router applies its own ceiling as well; this one bounds the socket.
THANOY_TIMEOUT_SECONDS = float(os.getenv("THANOY_TIMEOUT_SECONDS", "15"))

# Shown to the reader as the source of the provisions.
THANOY_PROVIDER_NAME = os.getenv("THANOY_PROVIDER_NAME", "iapp-thai-legal")
