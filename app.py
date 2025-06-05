# app.py – API Flask para listar y descargar documentos de una carpeta Drive
from __future__ import annotations

import os
import pathlib
from typing import Final

from flask import Flask, jsonify, request, send_file
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ---------------------------------------------------------------------------
# Credenciales y constantes
# ---------------------------------------------------------------------------
CLIENT_ID: Final = os.environ["CLIENT_ID"]
CLIENT_SECRET: Final = os.environ["CLIENT_SECRET"]
REFRESH_TOKEN: Final = os.environ["REFRESH_TOKEN"]
FOLDER_ID: Final = os.environ["FOLDER_ID"]          # carpeta “PROCEDIMIENTOS”
SCOPES: Final = ["https://www.googleapis.com/auth/drive.readonly"]

TMP_DIR = pathlib.Path("/tmp")
TMP_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def build_creds() -> Credentials:
    """Crea credenciales con Refresh-Token y las refresca si es necesario."""
    creds = Credentials(
        token=None,  # se rellenará con refresh()
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=SCOPES,
    )
    # fuerza refresco para garantizar access-token válido
    creds.refresh(Request())
    return creds


def drive():
    """Devuelve un servicio Drive v3 listo para usar."""
    return build("drive", "v3", credentials=build_creds(), cache_discovery=False)


# ---------------------------------------------------------------------------
# Flask
# ---------------------------------------------------------------------------
app = Flask(__name__)


@app.route("/docs", methods=["GET"])
def list_docs():
    """Lista los documentos (id y nombre) dentro de la carpeta."""
    try:
        svc = drive()
        res = (
            svc.files()
            .list(
                q=f"'{FOLDER_ID}' in parents and trashed = false",
                fields="files(id, name)",
            )
            .execute()
        )
        return jsonify(res["files"])
    except HttpError as err:
        return jsonify(error=str(err)), err.resp.status


@app.route("/doc/<file_id>", methods=["GET"])
def get_doc(file_id: str):
    """Descarga un archivo por su `file_id`.

    También soporta `?id=` como query-param por comodidad:
    https://tu-app.onrender.com/doc?id=<file_id>
    """
    # compatibilidad con ?id=xxxx
    file_id = request.args.get("id", file_id)

    try:
        svc = drive()

        meta = svc.files().get(fileId=file_id, fields="name").execute()
        data = svc.files().get_media(fileId=file_id).execute()

        tmp = TMP_DIR / meta["name"]
        tmp.write_bytes(data)

        return send_file(tmp, as_attachment=True, download_name=meta["name"])
    except HttpError as err:
        return jsonify(error=str(err)), err.resp.status


# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Ejecución local: FLASK_APP=app.py flask run --port 8000
    app.run(host="0.0.0.0", port=8000)
