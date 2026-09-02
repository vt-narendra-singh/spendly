from flask import Flask, redirect, render_template, request, session, url_for

from database.db import create_user, get_db, get_user_by_email, init_db, seed_db, verify_user

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

    user = {
        "name": "Demo User",
        "email": "demo@spendly.com",
        "initials": "DU",
        "member_since": "January 2025",
    }

    stats = [
        {"label": "Total Spent", "value": "₹18,420"},
        {"label": "Transactions", "value": "8"},
        {"label": "Top Category", "value": "Food"},
    ]

    transactions = [
        {"date": "2026-08-28", "description": "Grocery run - BigBasket", "category": "Food", "amount": "₹2,150"},
        {"date": "2026-08-25", "description": "Uber to airport", "category": "Transport", "amount": "₹890"},
        {"date": "2026-08-20", "description": "Electricity bill", "category": "Bills", "amount": "₹3,200"},
        {"date": "2026-08-15", "description": "Pharmacy - Apollo", "category": "Health", "amount": "₹640"},
        {"date": "2026-08-10", "description": "Movie night - PVR", "category": "Entertainment", "amount": "₹900"},
        {"date": "2026-08-05", "description": "Amazon order - shoes", "category": "Shopping", "amount": "₹3,499"},
        {"date": "2026-08-02", "description": "Dinner with friends", "category": "Food", "amount": "₹1,850"},
        {"date": "2026-07-29", "description": "Misc. stationery", "category": "Other", "amount": "₹290"},
    ]

    categories = [
        {"name": "Food", "amount": "₹4,000", "percent": 25, "bar_class": "mock-bar-food"},
        {"name": "Bills", "amount": "₹3,200", "percent": 20, "bar_class": "mock-bar-bills"},
        {"name": "Shopping", "amount": "₹3,499", "percent": 20, "bar_class": "mock-bar-shopping"},
        {"name": "Transport", "amount": "₹890", "percent": 10, "bar_class": "mock-bar-transport"},
        {"name": "Entertainment", "amount": "₹900", "percent": 10, "bar_class": "mock-bar-entertainment"},
        {"name": "Health", "amount": "₹640", "percent": 10, "bar_class": "mock-bar-health"},
        {"name": "Other", "amount": "₹290", "percent": 5, "bar_class": "mock-bar-other"},
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
