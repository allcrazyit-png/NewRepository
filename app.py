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
    
    /* ENLARGE INPUTS for Mobile */
    div[data-testid="stNumberInput"] input {
        font-size: 24px !important;
        height: 60px !important;
        padding: 10px !important;
        inputmode: decimal !important; /* Force decimal keypad on mobile */
    }
    div[data-testid="stNumberInput"] label {
        font-size: 1.2rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Load Data ---
df = data_manager.load_data()

if df.empty:
    st.error("No data found. Please check parts_data.csv.")
    st.stop()

# --- Mode Selection ---
mode = st.sidebar.radio("模式選擇", ["📝 巡檢輸入", "📊 數據戰情室"], index=0)

if mode == "📝 巡檢輸入":
    # --- Top Navigation / Filter ---
    st.header("瑞全智慧巡檢系統 (v3.1 壓縮版)")

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

    # --- History Trend Chart (Top) ---
    with st.expander(f"📊 歷史重量趨勢: {selected_part_no}", expanded=True):
        history_data = drive_integration.fetch_history(selected_part_no)
        
        if history_data:
            chart_df = pd.DataFrame(history_data)
            chart_df.replace("", pd.NA, inplace=True)
            chart_df['timestamp'] = pd.to_datetime(chart_df['timestamp'], errors='coerce')
            
            if chart_df['timestamp'].dt.tz is None:
                 chart_df['timestamp'] = chart_df['timestamp'].dt.tz_localize('UTC')
            chart_df['timestamp'] = chart_df['timestamp'].dt.tz_convert('Asia/Taipei')
            
            chart_df['weight'] = pd.to_numeric(chart_df['weight'], errors='coerce')
            chart_df = chart_df.dropna(subset=['timestamp', 'weight'])
            
            if not chart_df.empty:
                w_max_limit = pd.to_numeric(current_part_data.get('clean_重量上限'), errors='coerce')
                w_min_limit = pd.to_numeric(current_part_data.get('clean_重量下限'), errors='coerce')

                y_cols = ['weight']
                if pd.notna(w_max_limit):
                    chart_df['Upper Limit'] = float(w_max_limit)
                    y_cols.append('Upper Limit')
                if pd.notna(w_min_limit):
                    chart_df['Lower Limit'] = float(w_min_limit)
                    y_cols.append('Lower Limit')
                
                chart_long = chart_df.melt('timestamp', value_vars=y_cols, var_name='Type', value_name='Value')
                
                y_min_val = chart_long['Value'].min()
                y_max_val = chart_long['Value'].max()
                padding = (y_max_val - y_min_val) * 0.1 if y_max_val != y_min_val else 5
                
                base = alt.Chart(chart_long).encode(
                    x=alt.X('timestamp', title='時間', axis=alt.Axis(format='%m/%d %H:%M')),
                    y=alt.Y('Value', title='重量 (g)', 
                            scale=alt.Scale(domain=[y_min_val - padding, y_max_val + padding])),
                    color=alt.Color('Type', title='類別', 
                                    scale=alt.Scale(domain=['weight', 'Upper Limit', 'Lower Limit'],
                                                  range=['#FF6C6C', '#457B9D', '#457B9D'])),
                    tooltip=[alt.Tooltip('timestamp', format='%Y-%m-%d %H:%M'), alt.Tooltip('Type'), alt.Tooltip('Value', format='.1f')]
                )
                st.altair_chart(base.mark_line().interactive(), use_container_width=True)
            else:
                st.caption("無有效歷史數據")
        else:
            st.caption("載入中或無數據...")

    # --- Display Standard Info ---
    st.divider()
    info_col1, info_col2, info_col3 = st.columns(3)
    # Calculate Tolerance
    w_std = current_part_data['clean_重量']
    w_max = pd.to_numeric(current_part_data.get('clean_重量上限'), errors='coerce')
    w_min = pd.to_numeric(current_part_data.get('clean_重量下限'), errors='coerce')
    
    tol_str = ""
    if pd.notna(w_std) and pd.notna(w_max) and pd.notna(w_min):
        upper_diff = w_max - w_std
        lower_diff = w_std - w_min
        if abs(upper_diff - lower_diff) < 0.001:
            tol_str = f"±{upper_diff:g}"
        else:
            tol_str = f"+{upper_diff:g} / -{lower_diff:g}"

    info_col1.metric("標準重量", f"{current_part_data['重量']}", tol_str)
    info_col2.metric("原料編號", f"{current_part_data['原料編號']}")
    
    has_length = False
    if pd.notna(current_part_data['clean_標準長度']) and current_part_data['clean_標準長度'] > 0:
        has_length = True
        info_col3.metric("標準長度", f"{current_part_data['標準長度']}")

    # --- Inspection Form ---
    st.subheader("巡檢輸入")
    inspection_type = st.radio("巡檢階段", ["首件", "中件", "末件"], horizontal=True)

    col_input1, col_input2 = st.columns(2)
    with col_input1:
        measured_weight = st.number_input("實測重量 (g)", min_value=0.0, step=0.1, format="%.1f")
    with col_input2:
        measured_length = None
        if has_length:
            measured_length = st.number_input("實測長度 (mm)", min_value=0.0, step=0.1, format="%.1f")

    # --- Validation ---
    weight_status = "OK"
    if measured_weight > 0:
        if pd.notna(w_min) and pd.notna(w_max):
            if not (w_min <= measured_weight <= w_max):
                st.markdown(f'<div class="alert-box">⚠️ 重量異常! (標準: {w_min} ~ {w_max})</div>', unsafe_allow_html=True)
                weight_status = "NG"

    st.write(f"**確認原料**: `{current_part_data['原料編號']}`")
    material_check = st.radio("現場投料正確?", ["OK", "NG"], horizontal=True)
    material_ok = (material_check == "OK")

    # --- Key Control Points ---
    st.markdown("### ⚠️ 重點管制項目確認")
    control_points_status = {}
    has_ng_control_point = False
    control_points_log = [] 

    for i in range(1, 4):
        col_name = f"重點管制{i}"
        if col_name in current_part_data and pd.notna(current_part_data[col_name]):
            val = str(current_part_data[col_name]).strip()
            if val:
                status = st.radio(f"**{i}. {val}**", ["OK", "NG"], key=f"cp_{i}", horizontal=True)
                control_points_status[val] = status
                control_points_log.append(f"{i}.{status}")
                if status == "NG":
                    has_ng_control_point = True

    if has_ng_control_point:
        st.error("❌ 發現重點管制異常！請修正或記錄。")

    change_point = st.text_area("變化點說明 (選填)", placeholder="如有異常或變更請說明...")

    input_method = st.radio("影像輸入", ["📸 網頁相機 (Webcam)", "📂 上傳 / 後鏡頭 (Upload/Rear)"], index=1, horizontal=True, label_visibility="collapsed")
    img_file = None
    if input_method == "📸 網頁相機 (Webcam)":
        img_file = st.camera_input("拍照記錄")
    else:
        img_file = st.file_uploader("上傳照片", type=["jpg", "jpeg", "png"])

    # --- Submit ---
    if st.button("提交巡檢數據"):
        if measured_weight == 0:
            st.warning("請輸入重量")
        elif not material_ok:
            st.warning("原料確認為 NG，請確認正確料號")
        elif img_file is None:
            st.warning("請拍攝照片")
        else:
            with st.spinner("資料上傳中..."):
                tz = datetime.timezone(datetime.timedelta(hours=8))
                timestamp = datetime.datetime.now(tz)
                ts_str = timestamp.strftime("%Y%m%d_%H%M%S")
                filename = f"{selected_model}_{selected_part_no}_{inspection_type}_{ts_str}.jpg"
                
                key_control_str = ", ".join(control_points_log) if control_points_log else "N/A"
                
                row_data = {
                    "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "model": selected_model,
                    "part_no": selected_part_no,
                    "inspection_type": inspection_type,
                    "weight": measured_weight,
                    "length": measured_length if has_length else "",
                    "material_ok": "OK" if material_ok else "NG",
                    "change_point": change_point,
                    "result": weight_status,
                    "key_control_status": key_control_str
                }
                
                success, message = drive_integration.upload_and_append(img_file, filename, row_data)
            
            if success:
                st.success("數據提交成功!")
                st.balloons()
            else:
                st.error(f"提交失敗: {message}")

    # --- Bottom: Abnormal Images ---
    st.divider()
    st.subheader("異常圖示")
    import os
    img_dir = "quality_images"
    found_imgs = []
    if os.path.exists(img_dir):
        all_files = os.listdir(img_dir)
        for f in all_files:
            if selected_part_no in f:
                found_imgs.append(os.path.join(img_dir, f))
        if found_imgs:
            st.image(found_imgs, width=300, caption=[os.path.basename(p) for p in found_imgs])
        else:
            st.info("尚無異常照片歸檔")

elif mode == "📊 數據戰情室":
    st.header("📊 生產品質戰情室")
    st.caption("即時同步 Google Sheet 雲端數據")

    with st.spinner("正在連線至總部資料庫，請稍候..."):
        raw_data = drive_integration.fetch_all_data()

    if not raw_data:
        st.warning("目前無數據或無法連線至 Google Sheet (請確認 GAS V4 是否部署成功)。")
    else:
        df_dash = pd.DataFrame(raw_data)
        
        # --- Timezone Fix: Convert UTC to Taiwan Time ---
        if 'timestamp' in df_dash.columns:
            df_dash['timestamp'] = pd.to_datetime(df_dash['timestamp'], errors='coerce')
            # If naive (no timezone), assume UTC because GAS sends ISO/UTC
            if df_dash['timestamp'].dt.tz is None:
                 df_dash['timestamp'] = df_dash['timestamp'].dt.tz_localize('UTC')
            # Convert to Taiwan
            df_dash['timestamp'] = df_dash['timestamp'].dt.tz_convert('Asia/Taipei')
        
        # --- Filters ---
        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            models_dash = ["全部"] + list(df_dash['model'].unique())
            filter_model = st.selectbox("篩選車型", models_dash)
        
        with col_d2:
            # Dynamic Part No Filter based on Model
            if filter_model != "全部":
                parts_dash = ["全部"] + list(df_dash[df_dash['model'] == filter_model]['part_no'].unique())
            else:
                parts_dash = ["全部"] + list(df_dash['part_no'].unique())
            filter_part = st.selectbox("篩選品番", parts_dash)
            
        with col_d3:
            filter_result = st.radio("篩選結果", ["全部", "NG Only"], horizontal=True)

        # Apply Filters
        if filter_model != "全部":
            df_dash = df_dash[df_dash['model'] == filter_model]
        if filter_part != "全部":
            df_dash = df_dash[df_dash['part_no'] == filter_part]
        if filter_result == "NG Only":
            df_dash = df_dash[df_dash['result'] == 'NG']

        # --- KPI Cards ---
        kpi1, kpi2, kpi3 = st.columns(3)
        total_count = len(df_dash)
        ng_count = len(df_dash[df_dash['result'] == 'NG'])
        yield_rate = ((total_count - ng_count) / total_count * 100) if total_count > 0 else 0

        kpi1.metric("總檢驗數", total_count)
        kpi2.metric("NG 件數", ng_count, delta=-ng_count, delta_color="inverse")
        kpi3.metric("良率 (Yield)", f"{yield_rate:.1f}%")

        # --- Data Enrichment (Translate Control Points) ---
        # 1.OK, 2.NG -> 表面:OK, 尺寸:NG
        def enrich_control_status(row):
            raw_status = row.get('key_control_status', '')
            part_no = row.get('part_no')
            
            if not raw_status or raw_status == "N/A":
                return raw_status
            
            # Find Part Data
            part_info = df[df['品番'] == part_no]
            if part_info.empty:
                return raw_status
                
            part_info = part_info.iloc[0]
            
            # Parse "1.OK, 2.NG"
            segments = raw_status.split(',')
            enriched_segments = []
            
            for seg in segments:
                seg = seg.strip()
                if '.' in seg:
                    idx_str, state = seg.split('.', 1) # Split "1", "OK"
                    try:
                        idx = int(idx_str)
                        col_name = f"重點管制{idx}"
                        if col_name in part_info and pd.notna(part_info[col_name]):
                            desc = part_info[col_name]
                            enriched_segments.append(f"{desc}: {state}")
                        else:
                            enriched_segments.append(seg)
                    except:
                        enriched_segments.append(seg)
                else:
                    enriched_segments.append(seg)
            
            return " | ".join(enriched_segments)

        df_dash['詳細管制狀態'] = df_dash.apply(enrich_control_status, axis=1)

        # --- Data Grid ---
        st.subheader("📋 詳細履歷表")
        
        # Select columns to display
        display_cols = ['timestamp', 'model', 'part_no', 'weight', 'result', '詳細管制狀態', 'change_point']
        
        # Add Image Link Column
        if 'image_url' in df_dash.columns:
            df_dash['image_link'] = df_dash['image_url'].apply(lambda x: f"[查看照片]({x})" if x and str(x).startswith('http') else '無')
            display_cols.append('image_link')

        st.dataframe(
            df_dash[display_cols].sort_values(by='timestamp', ascending=False),
            use_container_width=True,
            column_config={
                "timestamp": st.column_config.DatetimeColumn("時間", format="YYYY/MM/DD HH:mm"),
                "image_link": st.column_config.LinkColumn("照片佐證"),
                "result": st.column_config.TextColumn("判定", help="OK or NG"),
                "change_point": st.column_config.TextColumn("變化點", width="medium"),
                "詳細管制狀態": st.column_config.TextColumn("重點管制細節", width="large"),
            }
        )

        # --- Charts ---
        st.subheader("趨勢分析")
        chart_bar = alt.Chart(df_dash).mark_bar().encode(
            x='model',
            y='count()',
            color='result'
        )
        st.altair_chart(chart_bar, use_container_width=True)
