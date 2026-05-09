# docx-to-md Converter — Spec v1.0

## Purpose
A FastAPI web service that accepts a .docx file upload, converts it to Markdown,
and returns a downloadable .md file with the same base filename.

## Endpoints
- GET /
  - Returns the HTML upload UI
- POST /convert
  - Input: multipart form-data, field name `file`, accepts .docx only
  - Output: .md file download, filename mirrors input (e.g. report.docx → report.md)
  - Errors: 400 if wrong file type, 500 on conversion failure
- GET /health
  - Returns JSON: { "status": "ok" }

## Conversion Rules
- Use mammoth library for docx → markdown
- Preserve headings, bold, italic, lists, and hyperlinks
- Strip comments and tracked changes
- Output UTF-8

## UI
- Single HTML page at GET /
- Drag-and-drop or browse to upload a .docx
- Download link appears after conversion
- No JavaScript frameworks — plain HTML + Fetch API

## Security
- Secrets managed via environment variables only
- .env file never committed — use .env.example as template
- AWS credentials sourced from instance IAM role in production, never hardcoded
- .gitignore excludes: .env, .aws/, *.pem, *.key, .elasticbeanstalk/

## Docker

### Local Development
- Dockerfile base image: python:3.11-slim
- Working directory: /app
- Expose port 8000
- Run with uvicorn, hot reload enabled via docker-compose volume mount

### docker-compose
- Service name: web
- Mount project root as volume for live reload during development
- Command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

### .dockerignore
- Exclude: __pycache__/, *.pyc, .env, .git, .ebignore, Procfile

### Production (AWS EC2)
- Same Dockerfile used for both local and production
- No compose in production — plain docker run
- Port mapping: 8000:8000

## Deployment Target
- Primary: AWS Elastic Beanstalk, Python 3.11 platform (free tier, t3.micro)
- Alternative: AWS EC2 with Docker (docker run -p 8000:8000 docx-converter)
- Secondary: Render.com or Fly.io via Dockerfile (free tier)

## File Limits (v1.1 — future)
- Max upload size: 10MB
- Return 413 if exceeded

# Phase 2 — User Accounts, Auth & Analytics

## 2.1 Authentication

### Supported Login Methods
- Email + password (local accounts)
- Google OAuth 2.0 (Gmail)
- Microsoft OAuth 2.0 (Outlook/Office 365)
- GitHub OAuth (optional — useful for developer audience)

### Auth Library
- Use Authlib for OAuth 2.0 flows
- Use passlib[bcrypt] for local password hashing — never store plaintext
- Use python-jose for JWT access + refresh token generation

### Token Strategy
- Access token: short-lived (15 minutes), stored in memory (JS variable)
- Refresh token: long-lived (7 days), stored in HttpOnly cookie only
- Reason: HttpOnly cookies are inaccessible to JavaScript,
  blocking XSS-based token theft

---

## 2.2 Security Hardening

### Password Policy (local accounts)
- Minimum 12 characters
- Must contain uppercase, lowercase, number, special character
- Breach check via HaveIBeenPwned API (k-anonymity model —
  only first 5 chars of SHA-1 hash sent, never the full password)
- Enforce on registration and password change

### Rate Limiting
- Login endpoint: max 5 attempts per IP per 15 minutes
- Registration: max 3 accounts per IP per hour
- Convert endpoint: max 20 conversions per user per hour
- Use slowapi (Starlette-compatible rate limiter)

### Brute Force Protection
- Lock account for 15 minutes after 5 failed login attempts
- Notify user by email on lockout
- Admin alert on 10+ failed attempts from same IP

### Multi-Factor Authentication (MFA)
- TOTP (Time-based One-Time Password) via pyotp
  compatible with Google Authenticator, Authy, 1Password
- MFA optional at registration, can be enforced per account
- Backup codes: 8 single-use codes generated at MFA setup,
  stored hashed (bcrypt), shown once to user

### Session Security
- Rotate session ID on login (session fixation prevention)
- Invalidate all sessions on password change
- Concurrent session limit: 5 active sessions per user
- Session table tracks: user_id, ip_address, user_agent,
  created_at, last_seen, is_active

### Transport Security
- HTTPS enforced in production (TLS via AWS Certificate Manager)
- HSTS header: Strict-Transport-Security: max-age=31536000
- Redirect all HTTP → HTTPS at load balancer level

### Input Validation & Injection Prevention
- All user inputs validated via Pydantic models (FastAPI native)
- Email addresses normalized and validated (email-validator library)
- File uploads: validate MIME type server-side, not just extension
- SQL queries: ORM only (SQLAlchemy) — no raw string queries

### Security Headers (all responses)
- Content-Security-Policy: restrict script/style sources
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- Referrer-Policy: strict-origin-when-cross-origin
- Permissions-Policy: restrict camera, microphone, geolocation

### Secrets Management
- All secrets (JWT secret, OAuth client secrets, DB credentials)
  sourced from environment variables
- In production: AWS Secrets Manager — never .env files on server
- Secret rotation: OAuth tokens rotated every 90 days

### Audit Logging
- Every auth event logged: login, logout, failed attempt,
  password change, MFA enable/disable, account deletion
- Log fields: timestamp, user_id, ip_address, user_agent, event_type, outcome
- Logs shipped to AWS CloudWatch — retained 90 days minimum
- Logs are append-only — no log deletion via app layer

### CSRF Protection
- Double-submit cookie pattern for all state-changing endpoints
- FastAPI middleware applies CSRF token validation

### Dependency Security
- pip-audit in CI pipeline — blocks deployment on known CVEs
- Dependabot alerts enabled on GitHub repo
- All dependencies pinned to exact versions in requirements.txt

---

## 2.3 User Account Features

### Registration Flow
1. User submits email + password (or OAuth)
2. Server validates password strength + breach check
3. Verification email sent (token expires in 24 hours)
4. Account inactive until email verified
5. On verification: account activated, welcome email sent

### Login Flow (local)
1. Rate limit check (IP + account)
2. Email lookup — constant-time comparison (prevents timing attacks)
3. bcrypt password verify
4. Failed: increment attempt counter, check lockout threshold
5. Success: issue access token + refresh token, log event

### Login Flow (OAuth)
1. Redirect to provider (Google / Microsoft / GitHub)
2. Receive authorization code
3. Exchange for access token server-side (never in browser)
4. Fetch user profile from provider
5. Create or link local account by email
6. Issue app-level JWT (do not use provider token as app token)

### Account Dashboard (authenticated users)
- Conversion history: filename, file size, timestamp, status
- Download previously converted files (if stored — Phase 2.5)
- MFA setup / disable
- Active sessions list with revoke option
- Delete account (GDPR right to erasure — purges all data)

---

## 2.4 Database (Phase 2 adds)

### New Tables
- users: id, email, password_hash, is_verified, is_active,
  mfa_enabled, mfa_secret, created_at, updated_at
- oauth_accounts: id, user_id, provider, provider_user_id,
  access_token_enc, created_at
- sessions: id, user_id, token_hash, ip_address, user_agent,
  created_at, last_seen, is_active
- mfa_backup_codes: id, user_id, code_hash, used_at
- audit_log: id, user_id, event_type, ip_address, user_agent,
  outcome, created_at
- conversions: id, user_id, original_filename, file_size_bytes,
  status, created_at

### Database
- PostgreSQL (via SQLAlchemy ORM + Alembic migrations)
- Passwords and MFA secrets encrypted at rest
- Database credentials from AWS Secrets Manager in production

---

## 2.5 Analytics (Per-User + Aggregate)

### Per-User Metrics (visible on dashboard)
- Total conversions (all time, this month)
- Success rate
- Average file size uploaded
- Most active day/time
- Conversion history log (last 50)

### Aggregate Metrics (Prometheus + Grafana — admin only)
- conversions_total labelled by status (success | failure)
- conversion_duration_seconds histogram
- upload_file_size_bytes summary
- conversion_errors_total labelled by reason
- active_users_total (DAU / MAU)
- auth_events_total labelled by event_type and outcome
- All endpoints auto-instrumented via prometheus-fastapi-instrumentator

### Frontend Analytics (Umami — self-hosted)
- Page views, sessions, referrers, browser, OS, device
- GDPR-compliant, no third-party data sharing
- Runs as Docker sidecar

---

## 2.6 Phase 2 Tech Stack Additions

| Concern | Library / Service |
|---|---|
| OAuth 2.0 flows | Authlib |
| Password hashing | passlib[bcrypt] |
| JWT tokens | python-jose |
| MFA (TOTP) | pyotp |
| Rate limiting | slowapi |
| Email sending | FastAPI-Mail |
| ORM | SQLAlchemy + Alembic |
| Database | PostgreSQL |
| Security headers | starlette middleware |
| HIBP breach check | httpx (custom call) |
| Secrets (prod) | AWS Secrets Manager |
| Audit logs | AWS CloudWatch |
| Dependency audit | pip-audit |
| Metrics | prometheus-fastapi-instrumentator |
| Visualization | Grafana |
| Frontend analytics | Umami (self-hosted) |

---

## 2.7 Phase 2 Deployment Additions

- PostgreSQL via AWS RDS (free tier: db.t3.micro, 20GB)
- Secrets via AWS Secrets Manager
- Logs via AWS CloudWatch
- HTTPS via AWS Certificate Manager (ACM) + ALB
- Prometheus + Grafana as Docker sidecars
- Umami + PostgreSQL as Docker sidecars