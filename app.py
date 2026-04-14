from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import pyotp
import qrcode
import io
import base64
import re
import os

app = Flask(__name__)
app.secret_key = "secret_key"

DB_PATH = "sql.db"
MAX_ATTEMPTS = 3


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    if not os.path.exists(DB_PATH):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                totp_secret TEXT NOT NULL,
                failed_attempts INTEGER DEFAULT 0,
                is_locked INTEGER DEFAULT 0
            )
        """
        )
        conn.commit()
        conn.close()


def is_strong_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r"[A-Z]", password):
        return False, "Must contain an uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Must contain a lowercase letter"
    if not re.search(r"[0-9]", password):
        return False, "Must contain a number"
    if not re.search(r"[^a-zA-Z0-9]", password):
        return False, "Must contain a special character"
    return True, "Strong"


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM user WHERE username = ? AND password = ?",
            (username, password),
        )
        user = cursor.fetchone()

        if user:
            if user["is_locked"]:
                flash("Account is locked due to too many failed attempts.")
                conn.close()
                return redirect("/")

            cursor.execute(
                "UPDATE user SET failed_attempts = 0 WHERE username = ?", (username,)
            )
            conn.commit()
            conn.close()

            session["mfa_user"] = username
            return redirect("/mfa")
        else:
            cursor.execute("SELECT * FROM user WHERE username = ?", (username,))
            existing = cursor.fetchone()

            if existing:
                new_attempts = existing["failed_attempts"] + 1
                if new_attempts >= MAX_ATTEMPTS:
                    cursor.execute(
                        "UPDATE user SET failed_attempts = ?, is_locked = 1 WHERE username = ?",
                        (new_attempts, username),
                    )
                    conn.commit()
                    flash(f"Account locked after {MAX_ATTEMPTS} failed attempts.")
                else:
                    cursor.execute(
                        "UPDATE user SET failed_attempts = ? WHERE username = ?",
                        (new_attempts, username),
                    )
                    conn.commit()
                    flash(
                        f"Invalid credentials. {MAX_ATTEMPTS - new_attempts} attempt(s) remaining."
                    )
            else:
                flash("Invalid credentials.")

            conn.close()

        return redirect("/")

    return render_template("login.html")


@app.route("/mfa", methods=["GET", "POST"])
def mfa():
    if "mfa_user" not in session:
        return redirect("/")

    username = session["mfa_user"]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if request.method == "POST":
        token = request.form["token"]
        totp = pyotp.TOTP(user["totp_secret"])

        if totp.verify(token):
            session.pop("mfa_user", None)
            session["username"] = username
            return redirect("/welcome")
        else:
            flash("Invalid MFA code. Try again.")
            return redirect("/mfa")

    return render_template("mfa.html", username=username)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        valid, message = is_strong_password(password)
        if not valid:
            flash(f"Weak password: {message}")
            return redirect("/register")

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM user WHERE username = ?", (username,))
        if cursor.fetchone():
            flash("Username already exists.")
            conn.close()
            return redirect("/register")

        totp_secret = pyotp.random_base32()
        cursor.execute(
            "INSERT INTO user (username, password, totp_secret) VALUES (?, ?, ?)",
            (username, password, totp_secret),
        )
        conn.commit()
        conn.close()

        totp = pyotp.TOTP(totp_secret)
        uri = totp.provisioning_uri(name=username, issuer_name="SQLite Injection Lab")
        img = qrcode.make(uri)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        qr_b64 = base64.b64encode(buf.getvalue()).decode()

        return render_template(
            "setup_mfa.html", qr_b64=qr_b64, secret=totp_secret, username=username
        )

    return render_template("register.html")


@app.route("/welcome")
def welcome():
    if "username" in session:
        return render_template("welcome.html", username=session["username"])
    flash("You are not logged in")
    return redirect("/")


@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("You have been logged out")
    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
