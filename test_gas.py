import requests
import json

GAS_URL = "https://script.google.com/macros/s/AKfycbwBe1pCD1yudWMojDUI-PqXxn5XueZrq8xBNjWKmE7YAdjkP5t83aWkLrbvnFpnArOJYA/exec"

payload = {
    "action": "get_history",
    "part_no": "G92D1-VU010" # Based on user screenshot
}

try:
    print(f"Testing URL: {GAS_URL}")
    response = requests.post(GAS_URL, json=payload, timeout=15)
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text[:500]}") # Print first 500 chars
except Exception as e:
    print(f"Error: {e}")
