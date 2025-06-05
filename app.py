# ── app.py  ──────────────────────────────────────────────────────────────
"""API mínima: lista y descarga documentos de Drive (read-only)."""

from __future__ import annotations

import os
import pathlib
from typing import Final

from flask import Flask, jsonify, request, send_file
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# ─────────────────────────────────────────────────────────────────────────
# Credenciales desde variables de entorno (Render)
# ─────────────────────────────────────────────────────────────────────────
CLIENT_ID: Final = os.environ["CLIENT_ID"]
CLIENT_SECRET: Final = os.environ["CLIENT_SECRET"]
REFRESH_TOKEN: Final = os.environ["REFRESH_TOKEN"]
FOLDER_ID: Final = os.environ["FOLDER_ID"]           # carpeta PROCEDIMIENTOS
SCOPES: Final = ["https://www.googleapis.com/auth/drive.readonly"]

app = Flask(__name__)

# ─────────────────────────────────────────────────────────────────────────
# Helper: inicializa servicio Drive usando refresh-token
# ─────────────────────────────────────────────────────────────────────────
def drive():
    creds = Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=SCOPES,
    )
    # refrescar si es necesario
    if not creds.valid:
        creds.refresh(Request())

    return build("drive", "v3", credentials=creds)

# ─────────────────── 1) Listar documentos ────────────────────────────────
@app.route("/docs", methods=["GET"])
def list_docs():
    service = drive()
    # Solo PDF/DOCX en la carpeta indicada
    query = (
        f"'{FOLDER_ID}' in parents and trashed = false "
        "and (mimeType = 'application/pdf' or mimeType = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')"
    )
    results = (
        service.files()
        .list(q=query, fields="files(id,name,mimeType,size)", pageSize=1000)
        .execute()
    )
    return jsonify(results["files"])

# ─────────────────── 2) Descargar un documento ───────────────────────────
@app.route("/doc/<file_id>", methods=["GET"])
def get_doc(file_id: str):
    service = drive()

    # Metadatos para nombre de archivo
    meta = service.files().get(fileId=file_id, fields="name").execute()

    # Descargar contenido binario
    data = service.files().get_media(fileId=file_id).execute()

    tmp = pathlib.Path("/tmp") / meta["name"]
    tmp.write_bytes(data)

    return send_file(tmp, as_attachment=True, download_name=meta["name"])

# ─────────────────── Ejecución local ─────────────────────────────────────
if __name__ == "__main__":
    # Solo para pruebas en tu máquina:  http://localhost:8000/docs
    app.run(host="0.0.0.0", port=8000)
