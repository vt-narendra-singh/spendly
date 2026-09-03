from flask import Flask, redirect, render_template, request, session, url_for

from database.db import create_user, get_db, get_user_by_email, init_db, seed_db, verify_user
from database.queries import (
    get_category_breakdown,
    get_recent_transactions,
    get_summary_stats,
    get_user_by_id,
)

app = Flask(__name__)
app.secret_key = "spendly-dev-secret-key-change-in-production"  # dev-only; replace before deploying

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("landing"))

    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not name or not email:
        return render_template(
            "register.html", error="Name and email are required.", name=name, email=email
        )

    if len(password) < 8:
        return render_template(
            "register.html", error="Password must be at least 8 characters.", name=name, email=email
        )

    if get_user_by_email(email):
        return render_template(
            "register.html", error="An account with this email already exists.", name=name, email=email
        )

    create_user(name, email, password)
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("landing"))

    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    user = verify_user(email, password)
    if user is None:
        return render_template("login.html", error="Invalid email or password")

    session["user_id"] = user["id"]
    return redirect(url_for("profile"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user_id = session["user_id"]
    user_row = get_user_by_id(user_id)

    initials = "".join(part[0] for part in user_row["name"].split()[:2]).upper()
    user = {
        "name": user_row["name"],
        "email": user_row["email"],
        "initials": initials,
        "member_since": user_row["member_since"],
    }

    # === SUBAGENT-1: transaction history ===
    transactions = [
        {
            "date": tx["date"],
            "description": tx["description"],
            "category": tx["category"],
            "amount": f"₹{tx['amount']:,.2f}",
        }
        for tx in get_recent_transactions(user_id)
    ]

    # === SUBAGENT-2: summary stats ===
    summary = get_summary_stats(user_id)
    stats = [
        {"label": "Total Spent", "value": f"₹{summary['total_spent']:,.2f}"},
        {"label": "Transactions", "value": str(summary["transaction_count"])},
        {"label": "Top Category", "value": summary["top_category"]},
    ]

    # === SUBAGENT-3: category breakdown ===
    categories = [
        {
            "name": cat["name"],
            "amount": f"₹{cat['amount']:,.2f}",
            "percent": cat["pct"],
            "bar_class": f"mock-bar-{cat['name'].lower()}",
        }
        for cat in get_category_breakdown(user_id)
    ]

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
