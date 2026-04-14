import sqlite3
import pyotp

users = [
    ("admin", "admin123"),
    ("john", "password123"),
    ("jane", "letmein"),
]

conn = sqlite3.connect("sql.db")
cursor = conn.cursor()

for username, password in users:
    totp_secret = pyotp.random_base32()
    try:
        cursor.execute(
            "INSERT INTO user (username, password, totp_secret) VALUES (?, ?, ?)",
            (username, password, totp_secret),
        )
        print(f"[+] Created: {username} / {password}")
    except sqlite3.IntegrityError:
        print(f"[!] Already exists: {username}")

conn.commit()
conn.close()

print("\nDone.")
