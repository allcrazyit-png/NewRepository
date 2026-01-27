import streamlit as st
import pandas as pd
import data_manager
import datetime

# --- Page Config ---
st.set_page_config(
    page_title="瑞全智慧巡檢",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Mobile Optimization / Aesthetics
st.markdown("""
    /* --- 1. Global Reset & Dark Mode Base --- */
    .stApp {
        background-color: #0e1117; /* Dark background */
        color: #e6e6e6;
    }
    
    /* --- 2. Typography & Headers --- */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
    }
    .stMarkdown p {
        font-size: 1.2rem !important;
        color: #d0d0d0;
    }

    /* --- 3. Glassmorphism Cards for Metrics --- */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: transform 0.2s;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: #00d4ff; /* Tech Blue Glow */
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
        color: #a0a0a0 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        color: #00d4ff !important; /* Tech Blue */
        font-weight: bold;
    }

    /* --- 4. Modern Input Fields (Mobile Friendly) --- */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        height: 3.5rem !important; /* Larger for touch */
        font-size: 1.3rem !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #00d4ff !important;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.3) !important;
    }
    .stTextArea textarea {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border-radius: 12px !important;
        font-size: 1.2rem !important;
    }

    /* --- 5. Radio Buttons (Pills Style) --- */
    .stRadio > label { font-size: 1.3rem !important; color: white !important; margin-bottom: 10px; }
    .stRadio div[role='radiogroup'] {
        gap: 10px;
        display: flex;
        flex-wrap: wrap;
    }
    .stRadio div[role='radiogroup'] > label { 
        background-color: rgba(255, 255, 255, 0.05) !important;
        padding: 15px 30px !important; 
        border-radius: 50px !important; /* Rounded Pills */
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: #e0e0e0 !important;
        transition: all 0.3s ease;
        flex: 1;
        justify-content: center;
        text-align: center;
    }
    .stRadio div[role='radiogroup'] > label:hover {
        background-color: rgba(255, 255, 255, 0.15) !important;
        border-color: #00d4ff !important;
    }
    .stRadio div[role='radiogroup'] > label[data-checked='true'] {
        background: linear-gradient(135deg, #00d4ff 0%, #005bea 100%) !important; /* Neon Gradient */
        color: white !important;
        border: none !important;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.5);
        font-weight: bold;
    }

    /* --- 6. Submit Button (Big & Glowing) --- */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #ff416c 0%, #ff4b2b 100%) !important; /* Warning Red Gradient */
        color: white !important;
        font-size: 1.5rem !important;
        height: 4rem !important;
        border-radius: 50px !important;
        border: none !important;
        box-shadow: 0 5px 15px rgba(255, 75, 43, 0.4);
        transition: transform 0.2s, box-shadow 0.2s;
        width: 100%;
        margin-top: 20px;
    }
    div.stButton > button:first-child:active {
        transform: scale(0.98);
        box-shadow: 0 2px 10px rgba(255, 75, 43, 0.4);
    }

    /* --- 7. Alert Box --- */
    .alert-box {
        background: rgba(255, 0, 0, 0.1);
        backdrop-filter: blur(5px);
        color: #ff4b4b;
        border: 1px solid #ff4b4b;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        box-shadow: 0 0 20px rgba(255, 75, 75, 0.2);
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(255, 75, 75, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); }
    }
""", unsafe_allow_html=True)

# --- Load Data ---
df = data_manager.load_data()

if df.empty:
    st.error("No data found. Please check parts_data.csv.")
    st.stop()

# --- Top Navigation / Filter ---
st.header("瑞全智慧巡檢系統")

col_filter1, col_filter2 = st.columns(2)

with col_filter1:
    car_models = df['車型'].unique()
    selected_model = st.selectbox("車型", car_models)

# Filter Parts based on Model
filtered_df = data_manager.get_filtered_data(df, car_model=selected_model)
part_numbers = filtered_df['品番'].unique()

with col_filter2:
    selected_part_no = st.selectbox("品番", part_numbers)

# Get selected row data
current_part_data = filtered_df[filtered_df['品番'] == selected_part_no].iloc[0]

# --- Display Standard Info ---
st.divider()
info_col1, info_col2, info_col3 = st.columns(3)
info_col1.metric("標準重量", f"{current_part_data['重量']}")
info_col2.metric("原料編號", f"{current_part_data['原料編號']}")

has_length = False
if pd.notna(current_part_data['clean_標準長度']) and current_part_data['clean_標準長度'] > 0:
    has_length = True
    info_col3.metric("標準長度", f"{current_part_data['標準長度']}")

# --- Inspection Form ---
st.subheader("巡檢輸入")

# 1. Inspection Type
inspection_type = st.radio("巡檢階段", ["首件", "中件", "末件"], horizontal=True)

# 2. Measurements
col_input1, col_input2 = st.columns(2)

with col_input1:
    measured_weight = st.number_input("實測重量 (g)", min_value=0.0, step=0.1, format="%.1f")

with col_input2:
    measured_length = None
    if has_length:
        measured_length = st.number_input("實測長度 (mm)", min_value=0.0, step=0.1, format="%.1f")

# --- Validation Logic (Immediate Feedback) ---
weight_status = "OK"
if measured_weight > 0:
    w_min = current_part_data['clean_重量下限']
    w_max = current_part_data['clean_重量上限']
    
    # If explicit limits exist, use them. Otherwise parse from "2430g±50g" logic? 
    # Current CSV logic has separate columns for limits, but let's be safe.
    # If limits are NaN, maybe try to derive from standard if it has ±?
    # For now, rely on clean_重量上限/下限 existing in CSV.
    
    if pd.notna(w_min) and pd.notna(w_max):
        if not (w_min <= measured_weight <= w_max):
            st.markdown(f'<div class="alert-box">⚠️ 重量異常! (標準: {w_min} ~ {w_max})</div>', unsafe_allow_html=True)
            weight_status = "NG"

# 3. Material Check
st.write(f"**確認原料**: `{current_part_data['原料編號']}`")
material_ok = st.toggle("現場投料正確?", value=False)

# 4. Change Point
change_point = st.text_area("變化點說明 (選填)", placeholder="如有異常或變更請說明...")

# 5. Camera
img_file = st.camera_input("拍照記錄")

import drive_integration

# --- Sidebar: System Diagnostics ---
with st.sidebar:
    st.header("🔧 系統診斷")
    if st.button("測試雲端連線"):
        st.info("正在檢查設定...")
        
        # 1. Check Credentials
        # Get services using existing logic
        try:
            drive_service, sheets_service = drive_integration.get_services()
        except Exception as e:
            drive_service = None
            st.error(f"❌ 初始化發生錯誤: {e}")
        
        if not drive_service:
            st.error("❌ 無法載入 Google 憑證 (Secrets/JSON)")
        else:
            # Get Service Account Email
            try:
                about = drive_service.about().get(fields="user").execute()
                email = about['user']['emailAddress']
                st.success(f"✅ 憑證讀取成功\n\n機器人 Email: `{email}`")
                st.write("⚠️ 請確認此 Email 已加入 Google Drive 資料夾與 Sheet 的「編輯者」。")
            except Exception as e:
                st.error(f"❌ 查無機器人資訊 (API 未開通?): {e}")

            # 2. Check Drive Folder Access
            try:
                folder_id = drive_integration.DRIVE_FOLDER_ID
                # Try to get folder metadata (Support Shared Drives)
                f_meta = drive_service.files().get(
                    fileId=folder_id, 
                    fields="name", 
                    supportsAllDrives=True
                ).execute()
                st.success(f"✅ 能夠存取照片資料夾: `{f_meta.get('name')}` (ID: {folder_id})")
            except Exception as e:
                st.error(f"❌ 無法存取照片資料夾 (ID: {drive_integration.DRIVE_FOLDER_ID})")
                st.error(f"詳細錯誤: {e}")
                st.warning("請確認 secrets 的 `drive_folder_id` 正確，且已共用給機器人。")
                
            # 3. Check Spreadsheet Access
            try:
                sheet_id = drive_integration.SPREADSHEET_ID
                s_meta = sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
                st.success(f"✅ 能夠存取 Google Sheet: `{s_meta.get('properties', {}).get('title')}`")
            except Exception as e:
                st.error(f"❌ 無法存取 Google Sheet (ID: {drive_integration.SPREADSHEET_ID})")
                st.error(f"詳細錯誤: {e}")


# --- Submit ---
# --- Submit ---
if st.button("提交巡檢數據"):
    if measured_weight == 0:
        st.warning("請輸入重量")
    elif not material_ok:
        st.warning("請確任原料正確")
    elif img_file is None:
        st.warning("請拍攝照片")
    else:
        with st.spinner("資料上傳中..."):
            # 1. Prepare Filename
            timestamp = datetime.datetime.now()
            ts_str = timestamp.strftime("%Y%m%d_%H%M%S")
            filename = f"{selected_model}_{selected_part_no}_{inspection_type}_{ts_str}.jpg"
            
            # 2. Prepare Data Row (Dict)
            row_data = {
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "model": selected_model,
                "part_no": selected_part_no,
                "inspection_type": inspection_type,
                "weight": measured_weight,
                "length": measured_length if has_length else "",
                "material_ok": "OK" if material_ok else "NG",
                "change_point": change_point,
                "result": weight_status
            }
            
            # 3. Call Unified GAS Function
            success, message = drive_integration.upload_and_append(img_file, filename, row_data)
        
        if success:
            st.success("數據提交成功!")
            st.balloons()
        else:
            st.error(f"提交失敗: {message}")

# --- Bottom Section: History / Alerts / Quality Images ---
st.divider()
st.subheader("品質履歷 & 異常圖示")

tab1, tab2 = st.tabs(["異常圖示", "歷史趨勢"])

with tab1:
    # Look for images in quality_images/ matching the part number
    # For now, placeholder
    st.info(f"顯示 {selected_part_no} 的歷史異常照片 (需放置於 quality_images/ 資料夾)")
    
    # Example: Check if specific control points have images?
    # prompt said: "從 quality_images/ 資料夾顯示對應品番的歷史異常照片"
    # I will look for files with part_no in filename
    import os
    img_dir = "quality_images"
    found_imgs = []
    if os.path.exists(img_dir):
        for f in os.listdir(img_dir):
            if selected_part_no in f:
                found_imgs.append(os.path.join(img_dir, f))
    
    if found_imgs:
        st.image(found_imgs, width=300, caption=[os.path.basename(p) for p in found_imgs])
    else:
        st.write("無相關照片")

with tab2:
    # Placeholder Trend Chart
    st.write("歷史重量趨勢")
    # Generate dummy data for visualization
    chart_data = pd.DataFrame({
        'Date': pd.date_range(start='1/1/2026', periods=5),
        'Weight': [current_part_data['clean_重量'] if pd.notna(current_part_data['clean_重量']) else 100] * 5
    })
    st.line_chart(chart_data, x='Date', y='Weight')

