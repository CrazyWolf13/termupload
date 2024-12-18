# Inhalt der Datei: /fastapi-file-upload/fastapi-file-upload/README.md

# FastAPI Datei-Upload Anwendung

Diese Anwendung ermöglicht das Hochladen von Dateien über eine FastAPI-Schnittstelle. Nach dem Hochladen einer Datei erhalten Sie eine URL, über die die Datei heruntergeladen werden kann.

## Installation

1. Klonen Sie das Repository:

   ```
   git clone <repository-url>
   cd fastapi-file-upload
   ```

2. Installieren Sie die Abhängigkeiten:

   ```
   pip install -r requirements.txt
   ```

## Nutzung

1. Starten Sie die FastAPI-Anwendung:

   ```
   uvicorn src.main:app --reload
   ```

2. Verwenden Sie cURL, um eine Datei hochzuladen:

   ```
   curl -X POST "http://127.0.0.1:8000/upload" -F "file=@./file.txt"
   ```

   Ersetzen Sie `./file.txt` durch den Pfad zu Ihrer Datei.

3. Nach dem Hochladen erhalten Sie eine URL, unter der Sie die Datei herunterladen können.

## Endpunkte

- `POST /upload`: Lädt eine Datei hoch und gibt eine URL zurück, um die Datei herunterzuladen.

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.