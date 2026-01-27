import streamlit as st
import pandas as pd
import data_manager
import datetime
import altair as alt
import json
import drive_integration

# --- Page Config ---
st.set_page_config(
    page_title="瑞全智慧巡檢",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Mobile Optimization / Aesthetics
st.markdown("""
<style>
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
</style>
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

# 5. Image Input (Camera or Upload)
input_method = st.radio("影像輸入", ["📸 拍照 (Camera)", "📂 上傳照片 (Upload)"], index=1, horizontal=True, label_visibility="collapsed")

img_file = None
if input_method == "📸 拍照 (Camera)":
    img_file = st.camera_input("拍照記錄")
else:
    img_file = st.file_uploader("上傳照片", type=["jpg", "jpeg", "png"])

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
            # Use UTC+8 for Taiwan/Beijing Time
            tz = datetime.timezone(datetime.timedelta(hours=8))
            timestamp = datetime.datetime.now(tz)
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
        st.write(f"歷史重量趨勢: {selected_part_no}")
        
        # 1. Fetch Data from GAS
        with st.spinner("載入歷史數據中..."):
            history_data = drive_integration.fetch_history(selected_part_no)
        
        # 2. Render Chart
        if history_data:
            chart_df = pd.DataFrame(history_data)
            
            # Robust Data Cleaning
            # 1. Replace empty strings with NaN
            chart_df.replace("", pd.NA, inplace=True)
            
            # 2. Convert timestamp (ISO 8601 from GAS is UTC)
            chart_df['timestamp'] = pd.to_datetime(chart_df['timestamp'], errors='coerce')
            
            # Convert to Taiwan Time (UTC+8)
            # If naive, assume UTC first (since GAS returns Z)
            if chart_df['timestamp'].dt.tz is None:
                 chart_df['timestamp'] = chart_df['timestamp'].dt.tz_localize('UTC')
            
            chart_df['timestamp'] = chart_df['timestamp'].dt.tz_convert('Asia/Taipei')
            
            
            # 3. Convert weight
            chart_df['weight'] = pd.to_numeric(chart_df['weight'], errors='coerce')
            
            # 4. Filter: Must have valid timestamp AND numeric weight
            chart_df = chart_df.dropna(subset=['timestamp', 'weight'])
            
            if not chart_df.empty:
                # Localize timezone to user's local if needed, but plotting UTC is safer for now or +8
                # chart_df['timestamp'] = chart_df['timestamp'].dt.tz_convert('Asia/Taipei') 
                # (Assuming browser handles standard ISO Z time, or we just show as is)
                
                # 5. Add Limits if available
                # current_part_data['clean_重量上限'] / ['clean_重量下限']
                w_max = pd.to_numeric(current_part_data.get('clean_重量上限'), errors='coerce')
                w_min = pd.to_numeric(current_part_data.get('clean_重量下限'), errors='coerce')
                
                # Create a list of columns to plot
                y_cols = ['weight']
                
                if pd.notna(w_max):
                    chart_df['Upper Limit'] = float(w_max)
                    y_cols.append('Upper Limit')
                
                if pd.notna(w_min):
                    chart_df['Lower Limit'] = float(w_min)
                    y_cols.append('Lower Limit')
                
                # Plot (Altair for better control over Y-axis scale)
                # Reshape to long format for Altair
                # CRITICAL FIX: explicit value_vars to avoid melting non-numeric cols like 'result'
                chart_long = chart_df.melt('timestamp', value_vars=y_cols, var_name='Type', value_name='Value')
                
                # Define dynamic Y-axis domain (min - 5%, max + 5%)
                y_min = chart_long['Value'].min()
                y_max = chart_long['Value'].max()
                padding = (y_max - y_min) * 0.1 if y_max != y_min else 5
                
                base = alt.Chart(chart_long).encode(
                    x=alt.X('timestamp', title='時間'),
                    y=alt.Y('Value', title='重量 (g)', 
                            scale=alt.Scale(domain=[y_min - padding, y_max + padding])),
                    color=alt.Color('Type', title='類別', 
                                    scale=alt.Scale(domain=['weight', 'Upper Limit', 'Lower Limit'],
                                                  range=['#FF6C6C', '#457B9D', '#457B9D'])), # Red for weight, Blue for limits
                    tooltip=['timestamp', 'Type', 'Value']
                )

                line_chart = base.mark_line().interactive()
                
                st.altair_chart(line_chart, use_container_width=True)
                
                # Show simple stats
                avg_w = chart_df['weight'].mean()
                st.caption(f"平均重量: {avg_w:.2f} g (樣本數: {len(chart_df)})")
            else:
                st.warning("有找到數據，但無法解析 (可能格式不符)。請確認 Sheet 欄位內容。")
        else:
            st.info("尚無歷史數據，或尚未更新 GAS 腳本。")
