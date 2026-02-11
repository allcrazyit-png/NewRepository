
import requests
import json
import pprint

GAS_URL = "https://script.google.com/macros/s/AKfycbyUXAjO4vOCmhOBWMT6svzpTXJzcVWO-jD4NQeEygB1-dyhCXb1m-gRC8_mkazIesTt/exec"

def test_get_all_data():
    payload = {
        "action": "get_all_data"
    }
    try:
        print(f"Fetching data from: {GAS_URL}")
        response = requests.post(GAS_URL, json=payload, timeout=15)
        
        if response.status_code == 200:
            resp_json = response.json()
            if resp_json.get("status") == "Success":
                data = resp_json.get("data", [])
                print(f"✅ Success! Fetched {len(data)} rows.")
                
                results = set()
                suspicious_count = 0
                
                print("\n--- Sample Data (First 3 Rows) ---")
                for i, row in enumerate(data[:3]):
                    print(f"Row {i}: Result='{row.get('result')}' | PartName='{row.get('part_name')}' | Image='{row.get('image')}'")

                print("\n--- Analysis ---")
                for row in data:
                    res = row.get('result', 'N/A')
                    results.add(res)
                    if res not in ['PASS', 'NG', 'CP', 'OK'] and len(str(res)) > 10:
                         print(f"⚠️ Suspicious Result Value: {res} | Row Part: {row.get('part_no')}")
                         suspicious_count += 1
                
                print(f"\nUnique Result Values found: {results}")
                if suspicious_count == 0:
                    print("🎉 Data looks clean! No URL-like strings in 'result' column.")
                else:
                    print(f"❌ Found {suspicious_count} rows with suspicious 'result' values. Fix needed.")
                    
            else:
                print(f"❌ API Error: {resp_json.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_get_all_data()
