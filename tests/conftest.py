"""Shared pytest fixtures for the Spendly test suite.

IMPORTANT: SPENDLY_DB_PATH must be pointed at a temp file BEFORE `app` is
imported anywhere, because `app.py` runs init_db()/seed_db() at module
import time. Any stale copy of the temp DB from a previous run is removed
first so each test session starts from a clean, freshly-seeded database.
"""

import os
import tempfile
import uuid

_TEST_DB_PATH = os.path.join(tempfile.gettempdir(), "spendly_test.db")
if os.path.exists(_TEST_DB_PATH):
    os.remove(_TEST_DB_PATH)
os.environ["SPENDLY_DB_PATH"] = _TEST_DB_PATH

import pytest  # noqa: E402

from app import app as flask_app  # noqa: E402  (import must follow env var set above)
from database.db import create_user, get_user_by_email  # noqa: E402


@pytest.fixture
def app():
    flask_app.config.update({"TESTING": True})
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def seed_user_id():
    """id of the demo user created by seed_db() (demo@spendly.com)."""
    user = get_user_by_email("demo@spendly.com")
    assert user is not None, "seed_db() did not create the demo user as expected"
    return user["id"]


@pytest.fixture
def empty_user_id():
    """id of a freshly-created user with zero expenses."""
    email = f"empty-{uuid.uuid4()}@example.com"
    create_user("Empty User", email, "password123")
    user = get_user_by_email(email)
    return user["id"]
