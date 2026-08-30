import os
import sqlite3
from datetime import date

from werkzeug.security import check_password_hash, generate_password_hash

DB_PATH = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "expense_tracker.db")
)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()


def get_user_by_email(email):
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,),
    ).fetchone()
    conn.close()
    return user


def verify_user(email, password):
    user = get_user_by_email(email)
    if user is None:
        return None
    if not check_password_hash(user["password_hash"], password):
        return None
    return user


def create_user(name, email, password):
    conn = get_db()
    password_hash = generate_password_hash(password)
    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, password_hash),
    )
    conn.commit()
    conn.close()


def seed_db():
    conn = get_db()
    cursor = conn.cursor()

    existing = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if existing > 0:
        conn.close()
        return

    password_hash = generate_password_hash("demo123")
    cursor.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", password_hash),
    )
    user_id = cursor.lastrowid

    today = date.today()

    def d(day):
        return date(today.year, today.month, day).strftime("%Y-%m-%d")

    sample_expenses = [
        (user_id, 45.50, "Food",          d(2),  "Groceries"),
        (user_id, 12.00, "Transport",     d(4),  "Bus pass top-up"),
        (user_id, 89.99, "Bills",         d(5),  "Electricity bill"),
        (user_id, 25.00, "Health",        d(9),  "Pharmacy"),
        (user_id, 18.75, "Entertainment", d(12), "Movie tickets"),
        (user_id, 60.00, "Shopping",      d(15), "New shoes"),
        (user_id, 15.20, "Food",          d(19), "Restaurant lunch"),
        (user_id, 30.00, "Other",         d(23), "Misc supplies"),
    ]

    cursor.executemany(
        """
        INSERT INTO expenses (user_id, amount, category, date, description)
        VALUES (?, ?, ?, ?, ?)
        """,
        sample_expenses,
    )

    conn.commit()
    conn.close()
