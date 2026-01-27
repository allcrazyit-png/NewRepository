import requests
import base64
import streamlit as st
import json

# Google Apps Script Web App URL
GAS_URL = "https://script.google.com/macros/s/AKfycbwSsRYqPXDRLkm1msFu53WTelmUGEkilpSH5edtww_StxOjyXRQhXMciGmQLyJS3jV0Yg/exec"

def upload_and_append(image_file, filename, row_data):
    """
    Sends data + image to Google Apps Script.
    GAS will handle Drive upload and Sheet append.
    
    row_data: dict containing all inspection fields
    """
    try:
        # 1. Encode Image to Base64
        image_content = image_file.getvalue()
        image_base64 = base64.b64encode(image_content).decode('utf-8')
        
        # 2. Prepare Payload
        payload = {
            "image_base64": image_base64,
            "filename": filename,
            # Flatten row_data into individual fields expected by GAS
            "timestamp": row_data.get("timestamp"),
            "model": row_data.get("model"),
            "part_no": row_data.get("part_no"),
            "inspection_type": row_data.get("inspection_type"),
            "weight": row_data.get("weight"),
            "length": row_data.get("length"),
            "material_ok": row_data.get("material_ok"),
            "change_point": row_data.get("change_point"),
            "result": row_data.get("result")
        }
        
        # 3. Post to GAS (Use json=payload)
        response = requests.post(GAS_URL, json=payload)
        
        if response.status_code == 200 and "Success" in response.text:
            return True, "成功"
        else:
            return False, f"GAS Error: {response.text}"
            
    except Exception as e:
        return False, str(e)

# --- Deprecated / Unused Legacy Functions (Kept empty/mocked if imports exist somewhere) ---
# We keep these signatures just in case app.py calls them individually during transition,
# effectively we should update app.py to call `upload_and_append` instead.

def get_services():
    return None, None

def upload_to_drive(image_file, filename):
    return "Handled by upload_and_append"

def append_to_sheet(row_data):
    return True
