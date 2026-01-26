import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import streamlit as st
from PIL import Image

SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/spreadsheets']
# If you have a service account file, name it credentials.json in the project root
CREDENTIALS_FILE = 'credentials.json'

# Helper to get secret from root or inside gcp_service_account
def get_secret(key, default):
    # 1. Try Root
    if key in st.secrets:
        return st.secrets[key]
    # 2. Try inside gcp_service_account (because generated script puts them there)
    if "gcp_service_account" in st.secrets and key in st.secrets["gcp_service_account"]:
        return st.secrets["gcp_service_account"][key]
    return default

# Get Folder ID
DRIVE_FOLDER_ID = get_secret("drive_folder_id", "root")

# Get Spreadsheet ID
# We set the default to the user's provided ID to ensure it works even if secrets fallback is weird
SPREADSHEET_ID = get_secret("spreadsheet_id", "1SXhH4aY7w0O4Usp35OaG7mJZqFZek3G8-lDaWX3Uk2o")

def get_services():
    creds = None
    
    # 1. Try Streamlit Secrets (Best for Cloud)
    if "gcp_service_account" in st.secrets:
        try:
            # Create a dict from the secrets object required by google.oauth2
            service_account_info = st.secrets["gcp_service_account"]
            creds = service_account.Credentials.from_service_account_info(
                service_account_info, scopes=SCOPES)
        except Exception as e:
            st.error(f"Error loading secrets: {e}")
            return None, None

    # 2. Try Local Service Account File
    elif os.path.exists(CREDENTIALS_FILE):
        try:
            creds = service_account.Credentials.from_service_account_file(
                CREDENTIALS_FILE, scopes=SCOPES)
        except Exception as e:
            st.error(f"Error loading credentials file: {e}")
            return None, None
    
    if not creds:
        # Mocking if no credentials found
        return None, None

    try:
        drive_service = build('drive', 'v3', credentials=creds)
        sheets_service = build('sheets', 'v4', credentials=creds)
        return drive_service, sheets_service
    except Exception as e:
        return None, None

def compress_image(image_file):
    """
    Compresses the uploaded image file (BytesIO) to JPEG with optimization.
    Returns: BytesIO object of compressed image.
    """
    img = Image.open(image_file)
    # Convert to RGB if RGBA
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    output_io = io.BytesIO()
    # Save with quality=70 (compressed)
    img.save(output_io, format='JPEG', quality=70, optimize=True)
    output_io.seek(0)
    return output_io

def upload_to_drive(image_file, filename):
    """
    Uploads file to Google Drive.
    Returns the shareable link (webViewLink).
    """
    drive_service, _ = get_services()
    
    # Mock return if no service
    if not drive_service:
        return "https://drive.google.com/mock_link_no_creds"

    try:
        compressed_io = compress_image(image_file)
        
        file_metadata = {
            'name': filename,
            'parents': [DRIVE_FOLDER_ID]
        }
        media = MediaIoBaseUpload(compressed_io, mimetype='image/jpeg', resumable=True)
        
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        
        # Make it readable to anyone with link (Optional, usually good for sharing)
        # drive_service.permissions().create(fileId=file.get('id'), body={'role': 'reader', 'type': 'anyone'}).execute()

        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Drive Upload Error: {e}")
        return "Error_Upload"

def append_to_sheet(row_data):
    """
    Appends a list of values to the Google Sheet.
    row_data: list of values [Date, Model, Part, ...]
    """
    _, sheets_service = get_services()
    
    if not sheets_service:
        print(f"MOCK APPEND: {row_data}")
        return True

    try:
        body = {
            'values': [row_data]
        }
        sheets_service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='Sheet1!A1', # Adjust range as needed
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        return True
    except Exception as e:
        st.error(f"Sheets Append Error: {e}")
        return False
