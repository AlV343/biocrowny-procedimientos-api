from flask import Flask, request, jsonify
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

app = Flask(__name__)

def get_drive_service():
    creds = Credentials(
        None,
        refresh_token=os.environ["REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["CLIENT_ID"],
        client_secret=os.environ["CLIENT_SECRET"],
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    return build("drive", "v3", credentials=creds)

@app.route("/documentos", methods=["GET"])
def buscar_documentos():
    q = request.args.get("q")
    if not q:
        return jsonify({"error": "Falta el parámetro 'q'"}), 400

    service = get_drive_service()
    results = service.files().list(
        q=f"name contains '{q}' and '{os.environ['FOLDER_ID']}' in parents",
        fields="files(id, name, webViewLink)",
        pageSize=10
    ).execute()

    documentos = [
        {
            "id": f["id"],
            "nombre": f["name"],
            "url": f["webViewLink"]
        }
        for f in results.get("files", [])
    ]

    return jsonify({"documentos": documentos})

@app.route("/documentos/<id>", methods=["GET"])
def obtener_documento(id):
    service = get_drive_service()
    file = service.files().get(fileId=id, fields="name, mimeType").execute()
    if file["mimeType"] != "application/vnd.google-apps.document":
        return jsonify({"error": "Tipo de archivo no soportado"}), 400

    content = service.files().export(fileId=id, mimeType="text/plain").execute()
    return jsonify({"contenido": content.decode("utf-8")})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
