# Spec: Registration

## Overview
This step implements the account creation flow for Spendly. The `GET /register` route already renders `register.html`, but submitting the form does nothing — there is no handler for the POST request. This spec wires up registration end to end: validating the submitted form, hashing the password, checking for duplicate emails, inserting the new user into the `users` table and shows success message and then redirecting to the sign-in page. This builds directly on the database layer from Step 1 and is a prerequisite for login (a future step) and everything that depends on an authenticated user (profile, expenses).

## Depends on
- Step 1 — Database setup (`database/db.py` with `get_db()`, `init_db()`, `users` table)

## Routes
- `GET /register` — renders the registration form — public (already implemented, unchanged)
- `POST /register` — validates input, creates the user, redirects to sign-in on success or re-renders the form with an error on failure — public

## Database changes
No database changes. The existing `users` table (`id`, `name`, `email`, `password_hash`, `created_at`) already supports registration. Two new functions are added to `database/db.py` (logic only, no schema change):
- `get_user_by_email(email)` — returns a user row or `None`, used to detect duplicate emails
- `create_user(name, email, password)` — hashes the password with `werkzeug.security.generate_password_hash` and inserts a new row

## Templates
- **Create:** none
- **Modify:** `templates/register.html` — repopulate `name` and `email` field values on validation failure so the user doesn't have to retype them (`value="{{ name or '' }}"`, `value="{{ email or '' }}"`); no structural changes, the existing `{% if error %}` block is reused

## Files to change
- `app.py` — change `register()` to accept `methods=["GET", "POST"]`, handle form validation and the create/redirect flow
- `database/db.py` — add `get_user_by_email()` and `create_user()`
- `templates/register.html` — repopulate submitted values on error

## Files to create
None

## New dependencies
No new dependencies

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (`generate_password_hash`)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- DB logic stays in `database/db.py` — never inline SQL in `app.py`
- Validate on the server even though HTML5 `required`/`type="email"` exist client-side: name and email non-empty, password at least 8 characters, email not already registered
- On success, redirect with `redirect(url_for('login'))` — do not create a session or log the user in (session handling belongs to the login step)
- On failure, re-render `register.html` with `error` set and the submitted `name`/`email` preserved — never redirect on failure

## Definition of done
- [x] Submitting the register form with a new name/email/password (≥8 chars) creates a row in `users` with a hashed password and redirects to `/login`
- [x] Submitting with an email that already exists re-renders `/register` with an inline error and does not insert a duplicate row
- [x] Submitting with a password under 8 characters re-renders `/register` with an inline error and does not insert a row
- [x] Submitting with an empty name or email re-renders `/register` with an inline error and does not insert a row
- [x] After a failed submission, the previously typed name and email are still shown in the form fields
- [x] Directly visiting `GET /register` still renders the empty form as before
- [x] No new pip packages were added to `requirements.txt`
