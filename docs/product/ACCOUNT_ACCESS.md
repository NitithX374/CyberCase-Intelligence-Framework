# Account access

Updated 2026-09-10.

## Registration and login

Password registration validates the email format and normalizes it to lowercase. Duplicate email addresses are rejected. Passwords must contain 12–128 characters and are stored as salted scrypt hashes. Successful registration immediately creates an HTTP-only session cookie and opens the workspace.

Email format validation does not establish mailbox existence or ownership. Password accounts are not marked email-verified. Email confirmation, resend links and SMTP configuration were removed at the user's request on 2026-09-10. Existing password accounts can sign in without a verification timestamp.

Login requires matching saved credentials. Google and GitHub sign-in remain available when their provider credentials are configured. OAuth retains browser-bound state validation and requires a provider-verified email; an email registered through a different method is rejected rather than silently linked.

## Access and persistence

All workspace pages require a session. The backend separately requires authentication for chat, messages, runs, reports, PDFs and document ingestion. Chat routes enforce ownership. Historical anonymous chats remain unassigned and are not automatically claimed by new accounts.

PostgreSQL stores users, submitted messages, runs and reports. Account-scoped localStorage retains intake titles/narratives/source selections, chat drafts/action choices, extracted document previews and the last workspace route. Logout clears query caches and notifies other tabs. Passwords and session tokens are never stored in localStorage.

Clearing browser storage removes local drafts but not submitted database records. Original File objects are not reconstructed after a reload: files need reselecting if extraction has not finished. Completed extraction text and metadata are retained.

## Configuration

No SMTP host, sender address or mail-service credentials are required.

| Variable | Purpose |
| --- | --- |
| `JWT_SECRET_KEY` | Random signing secret of at least 32 characters |
| `JWT_COOKIE_SECURE` | Set true for HTTPS deployment; false is for local HTTP |
| `NEXT_PUBLIC_API_URL` | Backend public URL supplied when building the frontend |
| `FRONTEND_BASE_URL` | Frontend origin used for OAuth redirects |
| `CORS_ORIGINS` | Exact frontend origins allowed to call the API |
| `OAUTH_GOOGLE_CLIENT_ID`, `OAUTH_GOOGLE_CLIENT_SECRET`, `OAUTH_GOOGLE_REDIRECT_URI` | Optional Google OAuth application |
| `OAUTH_GITHUB_CLIENT_ID`, `OAUTH_GITHUB_CLIENT_SECRET`, `OAUTH_GITHUB_REDIRECT_URI` | Optional GitHub OAuth application |
| `AUTH_DEV_LOGIN_ENABLED` | Defaults to false; keep disabled on shared deployments |

Provider callback URLs must exactly match `/api/v1/auth/callback/google` or `/api/v1/auth/callback/github`. Cookies use SameSite=Lax, so frontend and backend should share a site; localhost with different ports works.

Install backend requirements, apply `python -m alembic upgrade head` against the intended PostgreSQL component settings, and rebuild the application services. The existing migration through 0004 is unchanged. Its nullable email-verification token fields remain unused; format-only registration neither populates them nor fabricates a verification timestamp. Existing account data is preserved.

## Validation

Tests cover invalid email/password rejection, duplicate registration rollback, immediate registration/session access, login with an unverified email, owner isolation and removed verification endpoints. Database persistence coverage now registers users without mail transport and checks real message submission followed by logout/login and another account's denied access.

The 2026-09-09 PostgreSQL-enabled suite passed 435 tests plus 2 subtests for the earlier email-verification implementation. That historical receipt does not establish a live database test of this simplified flow. The application database has not been migrated or services rebuilt by this change. No live Google/GitHub callback has been verified.

Final format-only validation: 425 backend tests plus 2 subtests passed; 11 database-dependent tests skipped. All 162 frontend tests, frontend lint, production build, scoped Ruff and git diff checks passed.
