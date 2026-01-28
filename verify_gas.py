import requests
import json

# The URL provided by the user
GAS_URL = "https://script.google.com/macros/s/AKfycbyUXAjO4vOCmhOBWMT6svzpTXJzcVWO-jD4NQeEygB1-dyhCXb1m-gRC8_mkazIesTt/exec"

def verify_v4():
    print(f"🔍 Connecting to GAS: {GAS_URL}...")
    
    payload = {"action": "get_all_data"}
    
    try:
        response = requests.post(GAS_URL, json=payload, timeout=15)
        
        if response.status_code == 200:
            try:
                data = response.json()
                status = data.get("status")
                rows = data.get("data", [])
                
                print(f"📡 Status: {status}")
                print(f"📦 Records: {len(rows)}")
                
                if rows:
                    first_row = rows[0]
                    # Check for V4 specific columns
                    keys = list(first_row.keys())
                    print(f"🔑 Columns detected: {keys}")
                    
                    if "key_control_status" in keys and "image_url" in keys:
                        print("\n✅ [SUCCESS] GAS V4 is ACTIVE!")
                        print("   - 'key_control_status' found")
                        print("   - 'image_url' found")
                    else:
                        print("\n❌ [FAIL] Still running OLD VERSION (V3 or older).")
                        print("   - Missing 'key_control_status' or 'image_url'")
                        print("   Action: Please 'Manage Deployments' -> 'New Version'")
                else:
                    print("⚠️ Sheet is empty, cannot verify columns. But connection is OK.")
                    
            except json.JSONDecodeError:
                print(f"❌ JSON Decode Error. Response text:\n{response.text}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    verify_v4()
