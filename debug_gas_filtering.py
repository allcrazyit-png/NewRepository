import requests
import json

GAS_URL = "https://script.google.com/macros/s/AKfycbwBe1pCD1yudWMojDUI-PqXxn5XueZrq8xBNjWKmE7YAdjkP5t83aWkLrbvnFpnArOJYA/exec"

def test_query(part_no, description):
    print(f"--- Testing: {description} (Part: '{part_no}') ---")
    payload = {
        "action": "get_history",
        "part_no": part_no
    }
    try:
        response = requests.post(GAS_URL, json=payload, timeout=10)
        data = response.json().get("data", [])
        print(f"Returned {len(data)} rows.")
        if len(data) > 0:
            print(f"Sample: {data[0]}")
    except Exception as e:
        print(f"Error: {e}")

# 1. Query for the REAL part
test_query("G92D1-VU010", "Existing Part")

# 2. Query for a FAKE part
test_query("NON_EXISTENT_PART_XYZ", "Fake Part")
