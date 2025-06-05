from flask import Flask, jsonify
import os                               
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# ─────────── variables de entorno ───────────
CLIENT_ID     = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["REFRESH_TOKEN"]
FOLDER_ID     = os.environ["FOLDER_ID"]
SCOPES        = ["https://www.googleapis.com/auth/drive.readonly"]

app = Flask(__name__)

@app.route("/", methods=["GET", "HEAD"])
def root():
    return "Biocrowny API OK", 200

# ─────────── helper para Drive ───────────
def drive():
    creds = Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return build("drive", "v3", credentials=creds)

# ─────────── listar documentos ───────────
@app.route("/docs", methods=["GET"])
def list_docs():
    q = f"'{FOLDER_ID}' in parents and trashed = false"
    files = (
        drive().files()
        .list(q=q, fields="files(id,name,mimeType,size)", pageSize=1000)
        .execute()
        .get("files", [])
    )
    return jsonify(files)

# ─────────── descargar documento ───────────
@app.route("/doc/<file_id>", methods=["GET"])
def get_doc(file_id):
    file_id = request.args.get("id")
    service = drive()
    meta = service.files().get(fileId=file_id, fields="name").execute()
    data = service.files().get_media(fileId=file_id).execute()
    tmp = pathlib.Path("/tmp") / meta["name"]
    tmp.write_bytes(data)
    return send_file(tmp, as_attachment=True, download_name=meta["name"])

if __name__ == "__main__":          # para ejecución local
    app.run(host="0.0.0.0", port=8000)
