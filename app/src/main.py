from fastapi import FastAPI, File, UploadFile, HTTPException, Header, Depends, Request
from fastapi.responses import JSONResponse, FileResponse
import os
import shutil
from uuid import uuid4
from datetime import datetime, timedelta
import asyncio
import sqlite3
import hashlib

app = FastAPI()

UPLOAD_DIRECTORY = "./uploads"
TOKEN_DB = "tokens.db"
TOKEN_PASSWORD = os.getenv("TOKEN_PASSWORD", "defaultpassword")

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

# Initialize SQLite database
def init_db():
    with sqlite3.connect(TOKEN_DB) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        conn.commit()

init_db()

# Helper to hash tokens
def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

# Middleware to check token
async def validate_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization.split(" ")[1]
    hashed_token = hash_token(token)

    with sqlite3.connect(TOKEN_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT token FROM tokens WHERE token = ?", (hashed_token,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=401, detail="Invalid token")

@app.api_route("/", methods=["POST", "PUT"])
async def upload_file(request: Request, token: str = Depends(validate_token)):
    if "content-length" not in request.headers or int(request.headers["content-length"]) == 0:
        raise HTTPException(status_code=400, detail="No file provided")

    file_id = str(uuid4())
    filename = request.headers.get('filename', 'uploaded_file')
    file_location = f"{UPLOAD_DIRECTORY}/{file_id}_{filename}"

    with open(file_location, "wb") as buffer:
        async for chunk in request.stream():
            buffer.write(chunk)

    download_url = f"http://localhost:8000/download/{file_id}/{filename}"
    return JSONResponse(content={"download_url": download_url})

@app.get("/download/{file_id}/{filename}")
async def download_file(file_id: str, filename: str, token: str = Depends(validate_token)):
    file_path = f"{UPLOAD_DIRECTORY}/{file_id}_{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return JSONResponse(content={"error": "File not found"}, status_code=404)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cleanup_files())

async def cleanup_files():
    while True:
        now = datetime.now()
        for filename in os.listdir(UPLOAD_DIRECTORY):
            file_path = os.path.join(UPLOAD_DIRECTORY, filename)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if now - file_time > timedelta(minutes=60):
                os.remove(file_path)
        await asyncio.sleep(3600)  # Run cleanup every hour