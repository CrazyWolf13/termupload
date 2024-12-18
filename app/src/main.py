from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
import shutil
import os
from uuid import uuid4
from datetime import datetime, timedelta
import asyncio
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

app = FastAPI()

UPLOAD_DIRECTORY = "./uploads"
PRIVATE_KEY_PATH = "./private_key.pem"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

def load_private_key():
    with open(PRIVATE_KEY_PATH, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )
    return private_key

def verify_key(public_key_pem: str):
    private_key = load_private_key()
    public_key = serialization.load_pem_public_key(public_key_pem.encode('utf-8'))
    message = b"verify"
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid access key")

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), key: str = Depends(verify_key)):
    file_id = str(uuid4())
    file_location = f"{UPLOAD_DIRECTORY}/{file_id}_{file.filename}"
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    download_url = f"http://localhost:8000/download/{file_id}?key={key}"
    return JSONResponse(content={"download_url": download_url})

@app.get("/download/{file_id}")
async def download_file(file_id: str, key: str = Depends(verify_key)):
    files = os.listdir(UPLOAD_DIRECTORY)
    for file in files:
        if file.startswith(file_id):
            return FileResponse(f"{UPLOAD_DIRECTORY}/{file}")
    return JSONResponse(content={"error": "File not found"}, status_code=404)

async def cleanup_files():
    while True:
        now = datetime.now()
        for filename in os.listdir(UPLOAD_DIRECTORY):
            file_path = os.path.join(UPLOAD_DIRECTORY, filename)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if now - file_time > timedelta(minutes=60):
                os.remove(file_path)
        await asyncio.sleep(3600)  # Run cleanup every hour

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cleanup_files())