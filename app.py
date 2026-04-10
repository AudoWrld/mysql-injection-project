from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
import pyotp
import qrcode
import io
import base64
import re

app = Flask(__name__)
app.secret_key = "secret_key"

db = mysql.connector.connect(
    host="localhost",
    user="injectionuser",
    password="injectionpass",
    database="mysql_injection",
)
cursor = db.cursor(dictionary=True)

MAX_ATTEMPTS = 3


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

        query = "SELECT * FROM user WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if user:
            if user["is_locked"]:
                flash("Account is locked due to too many failed attempts.")
                return redirect("/")

            cursor.execute(
                "UPDATE user SET failed_attempts = 0 WHERE username = %s", (username,)
            )
            db.commit()

            session["mfa_user"] = username
            return redirect("/mfa")
        else:
            cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
            existing = cursor.fetchone()

            if existing:
                new_attempts = existing["failed_attempts"] + 1
                if new_attempts >= MAX_ATTEMPTS:
                    cursor.execute(
                        "UPDATE user SET failed_attempts = %s, is_locked = 1 WHERE username = %s",
                        (new_attempts, username),
                    )
                    db.commit()
                    flash(f"Account locked after {MAX_ATTEMPTS} failed attempts.")
                else:
                    cursor.execute(
                        "UPDATE user SET failed_attempts = %s WHERE username = %s",
                        (new_attempts, username),
                    )
                    db.commit()
                    flash(
                        f"Invalid credentials. {MAX_ATTEMPTS - new_attempts} attempt(s) remaining."
                    )
            else:
                flash("Invalid credentials.")

        return redirect("/")

    return render_template("login.html")


@app.route("/mfa", methods=["GET", "POST"])
def mfa():
    if "mfa_user" not in session:
        return redirect("/")

    username = session["mfa_user"]
    cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
    user = cursor.fetchone()

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

        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
        if cursor.fetchone():
            flash("Username already exists.")
            return redirect("/register")

        totp_secret = pyotp.random_base32()
        cursor.execute(
            "INSERT INTO user (username, password, totp_secret) VALUES (%s, %s, %s)",
            (username, password, totp_secret),
        )
        db.commit()

        totp = pyotp.TOTP(totp_secret)
        uri = totp.provisioning_uri(name=username, issuer_name="MySQL Injection Lab")
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
    app.run(debug=True)
