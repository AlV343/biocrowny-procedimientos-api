import json
import os
from google_auth_oauthlib.flow import InstalledAppFlow

# Configura tus datos aquí
CLIENT_ID = "TU_CLIENT_ID"
CLIENT_SECRET = "TU_CLIENT_SECRET"
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
REDIRECT_URI = "http://localhost:8080/"

client_config = {
    "installed": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [REDIRECT_URI]
    }
}

def main():
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=8080, prompt='consent')

    print("\n✅ AUTENTICACIÓN EXITOSA")
    print("Access Token:", creds.token)
    print("Refresh Token:", creds.refresh_token)
    print("\nGuarda este refresh token en tu backend o entorno seguro (por ejemplo, en Render).")

if __name__ == "__main__":
    main()
