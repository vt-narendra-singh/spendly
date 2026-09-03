"""Pure query helpers for Spendly. No Flask imports — sqlite3 via get_db() only."""

from datetime import datetime

from database.db import get_db


def get_user_by_id(user_id):
    """Return {'name', 'email', 'member_since'} for user_id, or None if not found."""
    conn = get_db()
    row = conn.execute(
        "SELECT name, email, created_at FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    conn.close()

    if row is None:
        return None

    created_at = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S")
    return {
        "name": row["name"],
        "email": row["email"],
        "member_since": created_at.strftime("%B %Y"),
    }


def get_recent_transactions(user_id, limit=10):
    """List of dicts with date, description, category, amount (float),
    newest-first, limited to `limit` rows."""
    conn = get_db()
    rows = conn.execute(
        """
        SELECT date, description, category, amount
        FROM expenses
        WHERE user_id = ?
        ORDER BY date DESC, id DESC
        LIMIT ?
        """,
        (user_id, limit),
    ).fetchall()
    conn.close()

    return [
        {
            "date": row["date"],
            "description": row["description"],
            "category": row["category"],
            "amount": float(row["amount"]),
        }
        for row in rows
    ]


def get_summary_stats(user_id):
    """{'total_spent': float, 'transaction_count': int, 'top_category': str}.
    Zeros / '—' placeholder when the user has no expenses."""
    conn = get_db()

    totals_row = conn.execute(
        """
        SELECT COALESCE(SUM(amount), 0) AS total_spent,
               COUNT(*) AS transaction_count
        FROM expenses
        WHERE user_id = ?
        """,
        (user_id,),
    ).fetchone()

    top_category_row = conn.execute(
        """
        SELECT category, SUM(amount) AS category_total
        FROM expenses
        WHERE user_id = ?
        GROUP BY category
        ORDER BY category_total DESC, category ASC
        LIMIT 1
        """,
        (user_id,),
    ).fetchone()

    conn.close()

    top_category = top_category_row["category"] if top_category_row else "—"

    return {
        "total_spent": float(totals_row["total_spent"]),
        "transaction_count": int(totals_row["transaction_count"]),
        "top_category": top_category,
    }


def get_category_breakdown(user_id):
    """List of dicts with name, amount (float), pct (int), ordered by amount desc;
    pct values sum to exactly 100, remainder absorbed by the largest category."""
    conn = get_db()
    rows = conn.execute(
        """
        SELECT category, SUM(amount) AS total
        FROM expenses
        WHERE user_id = ?
        GROUP BY category
        ORDER BY total DESC, category ASC
        """,
        (user_id,),
    ).fetchall()
    conn.close()

    if not rows:
        return []

    grand_total = sum(row["total"] for row in rows)

    breakdown = [
        {"name": row["category"], "amount": float(row["total"]), "pct": 0}
        for row in rows
    ]

    for entry in breakdown:
        entry["pct"] = round(entry["amount"] / grand_total * 100)

    remainder = 100 - sum(entry["pct"] for entry in breakdown)
    if remainder != 0:
        largest = max(breakdown, key=lambda entry: entry["amount"])
        largest["pct"] += remainder

    return breakdown
