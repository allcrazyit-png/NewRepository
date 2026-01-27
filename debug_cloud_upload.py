import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import datetime

st.title("☁️ Cloud Upload Debugger")

# 1. Print Environment Info
st.write("Checking Secrets...")
if "gcp_service_account" in st.secrets:
    st.success("✅ Secrets Loaded")
else:
    st.error("❌ Secrets NOT Found")
    st.stop()

# 2. Get Config
folder_id = st.secrets.get("drive_folder_id", "root")
st.write(f"Target Folder ID: `{folder_id}`")

# 3. Build Service
try:
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], 
        scopes=['https://www.googleapis.com/auth/drive.file']
    )
    service = build('drive', 'v3', credentials=creds)
    
    # Check "Who am I"
    about = service.about().get(fields="user").execute()
    email = about['user']['emailAddress']
    st.info(f"🤖 Bot Email: `{email}`")
    
except Exception as e:
    st.error(f"❌ Auth Failed: {e}")
    st.stop()

# 4. Check Permission on Folder
try:
    st.write("Checking Folder Access...")
    # Add supportsAllDrives=True
    f_meta = service.files().get(
        fileId=folder_id, 
        fields="name, capabilities", 
        supportsAllDrives=True
    ).execute()
    st.success(f"✅ Can see folder: `{f_meta.get('name')}`")
    
    can_edit = f_meta.get('capabilities', {}).get('canAddChildren', False)
    if can_edit:
        st.success("✅ Permission: Can Add Children (Write Access)")
    else:
        st.error("❌ Permission: READ ONLY. Cannot upload files.")
        st.warning(f"請確認 `{email}` 是該資料夾的「編輯者」！")
        
except Exception as e:
    st.error(f"❌ Folder Access Failed: {e}")
    st.write("Raw Error:", str(e))

# 5. Force Upload Test
if st.button("🚀 Force Upload Test File"):
    try:
        file_metadata = {
            'name': f'DEBUG_TEST_{datetime.datetime.now()}.txt',
            'parents': [folder_id]
        }
        media = MediaIoBaseUpload(
            io.BytesIO(b"This is a test upload from Streamlit Cloud debug script."), 
            mimetype='text/plain',
            resumable=True
        )
        
        file = service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id, webViewLink',
            supportsAllDrives=True
        ).execute()
        
        st.success(f"🎉 Upload Successful! ID: {file.get('id')}")
        st.write(f"Link: {file.get('webViewLink')}")
        
    except Exception as e:
        st.error(f"❌ Upload Failed: {e}")
