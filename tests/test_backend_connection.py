"""Tests for Step 5 (Backend Connection): database/queries.py and the
GET /profile route that consumes it.

Expected values are derived from the seed data in database/db.py's
seed_db() rather than hardcoded to the (stale) numbers in the spec doc.
"""

import re

import pytest

from database.queries import (
    get_category_breakdown,
    get_recent_transactions,
    get_summary_stats,
    get_user_by_id,
)

# Mirrors database/db.py:seed_db()'s sample_expenses for the demo user.
SEED_EXPENSES = [
    (45.50, "Food"),
    (12.00, "Transport"),
    (89.99, "Bills"),
    (25.00, "Health"),
    (18.75, "Entertainment"),
    (60.00, "Shopping"),
    (15.20, "Food"),
    (30.00, "Other"),
]
SEED_COUNT = len(SEED_EXPENSES)
SEED_TOTAL = round(sum(amount for amount, _ in SEED_EXPENSES), 2)
SEED_CATEGORY_COUNT = len({category for _, category in SEED_EXPENSES})  # 7 distinct
SEED_TOP_CATEGORY = "Bills"  # single highest line item, 89.99


def _login(client, email, password):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=False,
    )


# --------------------------------------------------------------------- #
# database/queries.py unit tests
# --------------------------------------------------------------------- #


class TestGetUserById:
    def test_valid_id_returns_expected_shape(self, seed_user_id):
        user = get_user_by_id(seed_user_id)
        assert user is not None
        assert user["name"] == "Demo User"
        assert user["email"] == "demo@spendly.com"
        assert isinstance(user["member_since"], str)
        assert user["member_since"]  # non-empty "%B %Y" string

    def test_nonexistent_id_returns_none(self):
        assert get_user_by_id(999_999) is None


class TestGetRecentTransactions:
    def test_user_with_expenses(self, seed_user_id):
        txs = get_recent_transactions(seed_user_id)
        assert len(txs) == SEED_COUNT
        for tx in txs:
            assert set(tx.keys()) == {"date", "description", "category", "amount"}
            assert isinstance(tx["amount"], float)
        # newest-first ordering
        dates = [tx["date"] for tx in txs]
        assert dates == sorted(dates, reverse=True)

    def test_user_without_expenses(self, empty_user_id):
        assert get_recent_transactions(empty_user_id) == []

    def test_limit_is_respected(self, seed_user_id):
        txs = get_recent_transactions(seed_user_id, limit=3)
        assert len(txs) == 3


class TestGetSummaryStats:
    def test_user_with_expenses(self, seed_user_id):
        stats = get_summary_stats(seed_user_id)
        assert stats["total_spent"] == pytest.approx(SEED_TOTAL)
        assert stats["transaction_count"] == SEED_COUNT
        assert stats["top_category"] == SEED_TOP_CATEGORY

    def test_user_without_expenses(self, empty_user_id):
        stats = get_summary_stats(empty_user_id)
        assert stats["total_spent"] == 0
        assert stats["transaction_count"] == 0
        assert stats["top_category"] == "—"  # "—" placeholder


class TestGetCategoryBreakdown:
    def test_user_with_expenses(self, seed_user_id):
        breakdown = get_category_breakdown(seed_user_id)
        assert len(breakdown) == SEED_CATEGORY_COUNT
        assert breakdown[0]["name"] == SEED_TOP_CATEGORY
        # descending by amount
        amounts = [entry["amount"] for entry in breakdown]
        assert amounts == sorted(amounts, reverse=True)
        # percentages sum to exactly 100 (remainder-absorption rule)
        assert sum(entry["pct"] for entry in breakdown) == 100

    def test_user_without_expenses(self, empty_user_id):
        assert get_category_breakdown(empty_user_id) == []


# --------------------------------------------------------------------- #
# GET /profile route tests
# --------------------------------------------------------------------- #


class TestProfileRoute:
    def test_unauthenticated_redirects_to_login(self, client):
        resp = client.get("/profile")
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/login")

    def test_seed_user_shows_real_data(self, client, seed_user_id):
        login_resp = _login(client, "demo@spendly.com", "demo123")
        assert login_resp.status_code == 302  # successful login redirects to /profile

        resp = client.get("/profile")
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)

        assert "Demo User" in html
        assert "demo@spendly.com" in html
        assert "₹" in html  # ₹ symbol present

        expected_total = f"{SEED_TOTAL:,.2f}"
        assert expected_total in html, f"expected total {expected_total!r} not found in response"

        # transaction count of 8 rendered as a standalone token
        assert re.search(r"\b" + str(SEED_COUNT) + r"\b", html)

        assert SEED_TOP_CATEGORY in html

    def test_new_user_with_no_expenses_shows_zero_state(self, client, empty_user_id):
        with client.session_transaction() as sess:
            sess["user_id"] = empty_user_id

        resp = client.get("/profile")
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)

        assert "0.00" in html
        assert "18,420" not in html  # old hardcoded mock value must be gone
        assert "January 2025" not in html  # old hardcoded mock value must be gone
