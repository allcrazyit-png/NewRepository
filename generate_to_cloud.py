import json
import os

def generate_toml():
    """Reads credentials.json and prints the TOML format for Streamlit Cloud."""
    
    # 1. Read the credentials.json file
    try:
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
    except FileNotFoundError:
        print("❌ 找不到 credentials.json 檔案！請確保它在同一個資料夾內。")
        return

    # 2. Print the explanation
    print("\n" + "="*50)
    print("📋 請複製以下內容貼到 Streamlit Cloud 的 Secrets 欄位")
    print("--------------------------------------------------")
    print(f"⚠️ 重要：請務必將您的 Google Sheet 共用給此 Email：\n{creds.get('client_email')}")
    print("="*50 + "\n")

    # 3. Format as TOML
    print("[gcp_service_account]")
    for key, value in creds.items():
        # Handle newlines in private key specifically
        if key == "private_key":
            # Use TOML multi-line string """ ... """ to avoid escaping hell
            print(f'{key} = """')
            print(value)
            print('"""')
        else:
            print(f'{key} = "{value}"')
    
    print(f'\nspreadsheet_id = "YOUR_SPREADSHEET_ID"  # <-- 記得填入您的 Google Sheet ID')
    print(f'drive_folder_id = "root"                 # <-- 照片上傳位置 (預設為 Root，可填入特定資料夾 ID)')
    
    print("\n" + "="*50)
    print("✅ 複製上面的內容，然後去 Streamlit Cloud -> Settings -> Secrets 貼上即可！")
    print("="*50 + "\n")

if __name__ == "__main__":
    generate_toml()
