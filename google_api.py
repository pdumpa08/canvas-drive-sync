# google_api.py
import requests
import json
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

def refresh_google_token(refresh_token):
    """Uses the refresh_token to get a brand new access_token from Google."""
    url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    
    resp = requests.post(url, data=data)
    if resp.status_code == 200:
        return resp.json().get("access_token")
    else:
        print(f"Failed to refresh Google token: {resp.text}")
        return None

def create_folder(name, parent_id, access_token):
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder"
    }
    if parent_id:
        metadata["parents"] = [parent_id]

    resp = requests.post(
        "https://www.googleapis.com/drive/v3/files",
        headers={"Authorization": f"Bearer {access_token}"},
        json=metadata,
    )
    return resp.json().get("id")

def upload_file_stream(name, file_obj, parent_id, access_token):
    metadata = {"name": name, "parents": [parent_id]}
    
    files = {
        "metadata": ("metadata.json", json.dumps(metadata), "application/json"),
        "file": (name, file_obj.raw), # .raw uses the stream
    }

    resp = requests.post(
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
        headers={"Authorization": f"Bearer {access_token}"},
        files=files,
    )
    if resp.status_code == 200:
        return resp.json().get("id")
    else:
        print("Upload failed:", resp.text)
        return None