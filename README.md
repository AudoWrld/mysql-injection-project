# 🛡️ SQLite Injection Demo Project

This is a Flask-based web app built to **demonstrate SQL injection vulnerabilities, brute force attacks, and MFA bypass techniques**. Built for educational use only — **do not deploy this to production.**

---

## ⚙️ 1. Prerequisites

- Python 3.x
- Flask
- `pip` (Python package manager)

> No MySQL or MariaDB required — this project uses **SQLite** (`sql.db`) which is built into Python.

---

## 📦 2. Install Dependencies

```bash
git clone https://github.com/KenyanAudo03/mysql-injection-project.git
cd mysql-injection-project
pip install -r requirements.txt
```

Required packages:
```
flask
pyotp
qrcode[pil]
requests
```

---

## 🗃️ 3. Setting Up the Database

The database (`sql.db`) is **automatically created** when you run the app for the first time. No manual setup needed.

The user table schema created automatically:

```sql
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    totp_secret TEXT NOT NULL,
    failed_attempts INTEGER DEFAULT 0,
    is_locked INTEGER DEFAULT 0
);
```

---

## 👤 4. Creating Default Users

Run the provided script to seed the database with default users:

```bash
python create_users.py
```

This creates the following accounts:

| Username | Password    |
|----------|-------------|
| admin    | admin123    |
| john     | password123 |
| jane     | letmein     |

> Each user is assigned a unique TOTP secret for MFA automatically.

---

## 🚀 5. Running the App

```bash
python app.py
```

Then open your browser and go to:
```
http://127.0.0.1:5000
```

---

## 🔐 6. SQL Injection Demo

To simulate an SQL injection on the login form:

- In the **username** field, enter:
  ```
  admin'--
  ```
- Enter **any random value** as the password.

The injected `'--` comments out the password check in the SQL query, bypassing authentication entirely.

---

## 💣 7. Brute Force Attack Demo

A brute force script is included to demonstrate password cracking against the login endpoint.

Run it with:

```bash
python crack_passwords.py
```

The script:
- Tries passwords from a wordlist against a target username
- Automatically resets account lockouts via direct DB access
- Reports timestamps, elapsed time, and crack summary

Example output:
```
=============================================
          BRUTE FORCE ATTACK
=============================================
  Started  : 2026-04-14 20:36:28
  Target   : admin
  Wordlist : 6 passwords
=============================================
  [20:36:28] [-] Failed: 123456              (elapsed: 0.120s)
  [20:36:28] [-] Failed: admin               (elapsed: 0.133s)
  [20:36:28] [-] Failed: password            (elapsed: 0.179s)
  [20:36:29] [+] FOUND: admin123
=============================================
              SUMMARY
=============================================
  Target        : admin
  Started       : 2026-04-14 20:36:28
  Finished      : 2026-04-14 20:36:29
  Total Time    : 0.1930 seconds
  Avg Per Try   : 0.0482 seconds
  Total Attempts: 4
---------------------------------------------
  Status        : CRACKED
  Password      : admin123
  Found On      : Attempt #4
=============================================
```

To change the target username or wordlist, edit these lines in `crack_passwords.py`:

```python
username = "admin"

wordlist = [
    "123456", "admin", "password", "admin123", "letmein", "AudoWrld@59"
]
```

---

## 💡 8. Why This Matters

This project demonstrates how poor input handling and weak passwords can be exploited. Use it as a teaching tool to:

- Understand real-world SQL injection vulnerabilities
- See how brute force attacks work in practice
- Learn how account lockouts can be bypassed with DB access
- Understand how to secure apps using prepared statements and password hashing

---

## ⚠️ Disclaimer

This is for **educational use only**. Do not use this code in any live project or attempt unauthorized access on real systems. Stay ethical.

---

## ✨ Credits

Made with 💻 by [Victor Owino]  
Inspired by common security flaws in beginner backend apps.