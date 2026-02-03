import requests
import json

GAS_URL = "https://script.google.com/macros/s/AKfycbyUXAjO4vOCmhOBWMT6svzpTXJzcVWO-jD4NQeEygB1-dyhCXb1m-gRC8_mkazIesTt/exec"

def fetch_history_debug(part_no):
    payload = {
        "action": "get_history",
        "part_no": part_no
    }
    print(f"Fetching history for: {part_no}...")
    try:
        response = requests.post(GAS_URL, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print("Status:", data.get("status"))
            items = data.get("data", [])
            print(f"Count: {len(items)}")
            if items:
                print("First item keys:", items[0].keys())
                print("First item sample:", items[0])
            else:
                print("No data returned.")
        else:
            print("HTTP Error:", response.status_code)
            print(response.text)
    except Exception as e:
        print("Exception:", e)

if __name__ == "__main__":
    # Pick a part number that likely has history. 
    # From parts_data.csv: G92D1-VU010, 62511-VU010
    fetch_history_debug("62511-VU010")
