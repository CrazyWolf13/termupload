# Termupload

This application allows you to upload files via a FastAPI interface. After uploading a file, you will receive a URL via which the file can be downloaded.

## Installation

1. clone the repository:

   ```
   git clone <repository-url>
   cd fastapi-file-upload
   ```

2. install the dependencies:

   ```
   pip install -r requirements.txt
   ```

## Utilisation

1. start the FastAPI application:

   ```
   uvicorn src.main:app --reload
   ```

2. use cURL to upload a file:

   ```
   curl -X POST "http://127.0.0.1:8000/upload" -F "file=@./file.txt"
   ```

   Replace `./file.txt` with the path to your file.

3. after uploading, you will receive a URL where you can download the file.

## Endpoints

- `POST /upload`: Uploads a file and returns a URL to download the file.

## Licence

This project is licensed under the AGPL-3.0 license.
