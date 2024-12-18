import sys
from uuid import uuid4
import sqlite3
import hashlib
import os

TOKEN_DB = "tokens.db"
TOKEN_PASSWORD = os.getenv("TOKEN_PASSWORD", "defaultpassword")

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

# token management
def generate_token(password: str):
    if password != TOKEN_PASSWORD:
        raise ValueError("Invalid password")

    new_token = str(uuid4())
    hashed_token = hash_token(new_token)

    with sqlite3.connect(TOKEN_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tokens (token) VALUES (?)", (hashed_token,))
        conn.commit()

    print(f"Token generated: {new_token}")

def revoke_token(token: str, password: str):
    if password != TOKEN_PASSWORD:
        raise ValueError("Invalid password")

    hashed_token = hash_token(token)
    with sqlite3.connect(TOKEN_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tokens WHERE token = ?", (hashed_token,))
        conn.commit()

    print("Token revoked")

if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != "create":
        print("Usage: keymgmt.py create <Password>")
        sys.exit(1)

    password = sys.argv[2]
    try:
        generate_token(password)
    except ValueError as e:
        print(e)
        sys.exit(1)