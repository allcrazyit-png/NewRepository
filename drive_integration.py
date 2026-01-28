from PIL import Image
import io
import requests
import base64
import streamlit as st
import json

# Google Apps Script Web App URL
GAS_URL = "https://script.google.com/macros/s/AKfycbyUXAjO4vOCmhOBWMT6svzpTXJzcVWO-jD4NQeEygB1-dyhCXb1m-gRC8_mkazIesTt/exec"

def compress_image(image_file, max_size_mb=1.0, quality=85):
    """
    Compress image to be under max_size_mb.
    """
    try:
        if isinstance(image_file, bytes):
             img = Image.open(io.BytesIO(image_file))
        else:
             # Streamlit UploadedFile or BytesIO
             image_file.seek(0)
             img = Image.open(image_file)
        
        # Convert to RGB if needed (e.g., RGBA -> JPEG)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        output_buffer = io.BytesIO()
        
        # Initial Save
        img.save(output_buffer, format="JPEG", quality=quality)
        size_mb = output_buffer.tell() / (1024 * 1024)
        
        # Aggressive Resize Loop if still too big
        while size_mb > max_size_mb and quality > 30:
            output_buffer = io.BytesIO() # Reset buffer
            quality -= 10
            # Also scale down dimensions if huge
            if size_mb > 2.0: # If > 2MB, resize dimensions
                width, height = img.size
                img = img.resize((int(width * 0.7), int(height * 0.7)), Image.Resampling.LANCZOS)
                
            img.save(output_buffer, format="JPEG", quality=quality)
            size_mb = output_buffer.tell() / (1024 * 1024)
            
        return output_buffer.getvalue()
    except Exception as e:
        print(f"Compression failed: {e}")
        # Buildin fallback: if compression fails, return original bytes if possible
        if isinstance(image_file, bytes): return image_file
        image_file.seek(0)
        return image_file.read()

def upload_and_append(image_file, filename, row_data):
    """
    Sends data + image to Google Apps Script.
    GAS will handle Drive upload and Sheet append.
    
    row_data: dict containing all inspection fields
    """
    try:
        # 1. Compress & Encode Image to Base64
        # Note: image_file from Streamlit is a file-like object
        compressed_bytes = compress_image(image_file, max_size_mb=1.0)
        
        # DEBUG: Show Compression Result
        orig_size = 0
        if isinstance(image_file, bytes): orig_size = len(image_file)
        else: 
            image_file.seek(0, 2) # Seek end
            orig_size = image_file.tell()
            image_file.seek(0)
            
        comp_size = len(compressed_bytes)
        # Change to st.warning/success for better visibility than toast
        if comp_size < orig_size:
            st.success(f"📉 照片已壓縮: {orig_size/1024/1024:.2f}MB ➝ {comp_size/1024/1024:.2f}MB")
        else:
            st.info(f"ℹ️ 照片未壓縮 (已夠小): {comp_size/1024/1024:.2f}MB")
        
        image_base64 = base64.b64encode(compressed_bytes).decode('utf-8')
        
        # 2. Prepare Payload (Clean Version)
        payload = {
            "image_base64": image_base64, # Now compressed
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
            "result": row_data.get("result"),
            "key_control_status": row_data.get("key_control_status") 
        }
        
        # 3. Post to GAS (Use json=payload)
        response = requests.post(GAS_URL, json=payload)
        
        if response.status_code == 200 and "Success" in response.text:
            return True, "成功"
        else:
            return False, f"GAS Error: {response.text}"
            
    except Exception as e:
        return False, str(e)

def fetch_history(part_no):
    """
    Fetches history data for a specific part from GAS.
    Returns: DataFrame-ready list of dicts [{'timestamp':..., 'weight':...}]
    """
    try:
        payload = {
            "action": "get_history",
            "part_no": part_no
        }
        response = requests.post(GAS_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            resp_json = response.json()
            if resp_json.get("status") == "Success":
                return resp_json.get("data", [])
            else:
                return []
        else:
            return []
    except Exception:
        return []

def fetch_all_data():
    """
    Fetches ALL data from GAS (Columns A-K) for the Dashboard.
    Returns: List of dicts.
    """
    try:
        payload = {
            "action": "get_all_data" # New V4 action
        }
        response = requests.post(GAS_URL, json=payload, timeout=15) # Longer timeout for full data
        
        if response.status_code == 200:
            resp_json = response.json()
            if resp_json.get("status") == "Success":
                return resp_json.get("data", [])
            else:
                return []
        else:
            return []
    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
        return []

# --- Deprecated / Unused Legacy Functions (Kept empty/mocked if imports exist somewhere) ---
# We keep these signatures just in case app.py calls them individually during transition,
# effectively we should update app.py to call `upload_and_append` instead.

def get_services():
    return None, None

def upload_to_drive(image_file, filename):
    return "Handled by upload_and_append"

def append_to_sheet(row_data):
    return True
