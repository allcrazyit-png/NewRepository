import requests
import json
import time

GAS_URL = "https://script.google.com/macros/s/AKfycbyUXAjO4vOCmhOBWMT6svzpTXJzcVWO-jD4NQeEygB1-dyhCXb1m-gRC8_mkazIesTt/exec"

def test_update_flow():
    print("1. Fetching All Data to get a valid Timestamp...")
    try:
        resp = requests.post(GAS_URL, json={"action": "get_all_data"}, timeout=15)
        data = resp.json().get("data", [])
        
        if not data:
            print("❌ No data found in Sheet.")
            return

        # Pick the most recent row
        target_row = data[-1]
        target_ts = target_row.get("timestamp")
        target_part = target_row.get("part_no")
        print(f"🎯 Target Row Timestamp: '{target_ts}'")
        print(f"🎯 Target Row PartNo: '{target_part}'")
        
        # 2. Attempt Update
        print(f"\n2. Attempting Update on '{target_ts}'...")
        payload = {
            "action": "update_status",
            "timestamp": target_ts, # Use the EXACT string returned by GAS
            "status": "審核中",
            "manager_comment": "API Test Update " + str(time.time()),
            "part_no": target_part,
            "apply_all": True
        }
        
        upd_resp = requests.post(GAS_URL, json=payload, timeout=15)
        print(f"📤 Update Response: {upd_resp.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_update_flow()
