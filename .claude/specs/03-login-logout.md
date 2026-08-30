# Spec: Login and Logout

## Overview
This step implements authentication for Spendly: verifying credentials on `POST /login`, starting a server-side session for the signed-in user, and clearing that session on `GET /logout`. The `GET /login` route already renders `login.html`, but the form currently posts nowhere — there is no handler and no session mechanism exists anywhere in the app yet. This builds directly on Step 1 (database) and Step 2 (registration, which creates the `users` rows this step authenticates against) and is a prerequisite for every route that needs to know who is signed in (profile, expenses).

## Depends on
- Step 1 — Database setup (`database/db.py` with `get_db()`, `init_db()`, `users` table)
- Step 2 — Registration (`get_user_by_email()` in `database/db.py`, hashed passwords in `users.password_hash`)

## Routes
- `GET /login` — if already signed in, redirects to `/`; otherwise renders the sign-in form — public/logged-out only
- `POST /login` — validates the submitted email/password against `users`, starts a session on success and redirects to `/`, or re-renders the form with an error on failure — public/logged-out only
- `GET|POST /register` — if already signed in, redirects to `/` before running any registration logic; behavior for logged-out visitors is unchanged from Step 2 — public/logged-out only
- `GET /logout` — clears the session and redirects to `/` — logged-in (replaces the current stub that returns a raw string)

## Database changes
No database changes. The existing `users` table (`id`, `name`, `email`, `password_hash`, `created_at`) already supports login. One new function is added to `database/db.py`:
- `verify_user(email, password)` — looks up the user by email, checks the password with `werkzeug.security.check_password_hash`, and returns the user row on success or `None` on failure (invalid email or wrong password are indistinguishable to the caller)

## Templates
- **Create:** none
- **Modify:**
  - `templates/login.html` — change the hardcoded `action="/login"` to `action="{{ url_for('login') }}"`; no other structural changes, the existing `{% if error %}` block is reused
  - `templates/base.html` — nav links become session-aware: when a user is signed in, show a "Sign out" link (`{{ url_for('logout') }}`) instead of "Sign in" / "Get started"

## Files to change
- `app.py` — set `app.secret_key` for session support; change `login()` to accept `methods=["GET", "POST"]`, guard against already-authenticated visitors, and handle credential validation, session creation, and redirect to `/`; add the same already-authenticated guard to `register()`; replace the `logout()` stub to clear the session and redirect to `/`
- `database/db.py` — add `verify_user()`
- `templates/login.html` — fix hardcoded form action to use `url_for()`
- `templates/base.html` — conditionally render nav links based on session state

## Files to create
None

## New dependencies
No new dependencies (session support is built into Flask; no `Flask-Login` or similar)

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (`check_password_hash` against the stored hash — never compare plaintext)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- DB logic stays in `database/db.py` — never inline SQL or password-hash comparisons in `app.py`
- Store only `user_id` in the session (`session['user_id']`) — never store the password or password hash
- `GET|POST /login` and `GET|POST /register` must redirect an already-authenticated visitor (`session.get('user_id')` truthy) to `/` before doing anything else — a signed-in user must never see or resubmit either form
- On success, redirect with `redirect(url_for('landing'))` (i.e. `/`) — do not render a template directly
- On failure, re-render `login.html` with a single generic `error` (e.g. "Invalid email or password") — never reveal whether the email exists
- `GET /logout` must clear the entire session (`session.clear()`), not just the `user_id` key, and must work even if no one is logged in (no error on a logged-out visitor hitting `/logout`)
- Do not implement `/profile` beyond its existing stub — it stays "Profile page — coming in Step 4"; it is no longer a redirect target in this step
- Do not add *login-required* guards to any other route in this step (`/profile`, `/expenses/*`) — access control for protected pages is a later step. The only guards added here are the inverse: keeping already-authenticated users off `/login` and `/register`

## Definition of done
- [x] Submitting `/login` with a registered email and correct password redirects to `/` and sets a session
- [x] Submitting `/login` with a registered email and wrong password re-renders `/login` with a generic invalid-credentials error and no session is created
- [x] Submitting `/login` with an email that isn't registered re-renders `/login` with the same generic invalid-credentials error (no hint the email is unknown)
- [x] After a successful login, the navbar shows "Sign out" instead of "Sign in" / "Get started"
- [x] Visiting `/logout` while signed in clears the session and redirects to `/`, and the navbar reverts to "Sign in" / "Get started"
- [x] Visiting `/logout` while signed out does not error and redirects to `/`
- [x] Directly visiting `GET /login` still renders the empty form as before (when signed out)
- [x] Visiting `/login` while already signed in redirects to `/` without showing the form
- [x] Visiting `/register` while already signed in redirects to `/` without showing the form (and without running any registration logic)
- [x] No new pip packages were added to `requirements.txt`
