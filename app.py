import streamlit as st
import pandas as pd
import data_manager
import datetime
import altair as alt
import json
import drive_integration
import streamlit.components.v1 as components

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
        height: 60px !important;
        padding: 10px !important;
    }
    div[data-testid="stNumberInput"] label {
        font-size: 1.2rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Inject JS for Mobile Keypad ---
# CSS 'inputmode' is not supported, so we use JS to set the HTML attribute
components.html("""
<script>
    function updateInputMode() {
        const inputs = window.parent.document.querySelectorAll('input[type="number"]');
        inputs.forEach(input => {
            input.setAttribute('inputmode', 'decimal');
        });
    }
    // Run periodically to catch re-renders
    setInterval(updateInputMode, 1000);
</script>
""", height=0)

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

    # --- Product Image (Standard) ---
    product_img_filename = current_part_data.get('產品圖片')
    if pd.notna(product_img_filename) and str(product_img_filename).strip():
        # Construct full path
        import os
        img_path = os.path.join("quality_images", str(product_img_filename).strip())
        
        # Display in an expander
        with st.expander("🖼️ 產品標準圖 (Standard Image)", expanded=True):
            if os.path.exists(img_path):
                st.image(img_path, caption=f"標準圖: {product_img_filename}", use_container_width=True)
            else:
                st.warning(f"找不到圖片檔案: {product_img_filename} (請確認 quality_images 資料夾)")

    # --- Pre-process Dual Mode Logic ---
    raw_weight_clean = current_part_data['clean_重量']
    is_dual = isinstance(raw_weight_clean, list)

    # Helper to get specific limit (Left/Right) or shared limit
    def get_spec_val(col_name, idx):
        val = current_part_data.get(col_name)
        if isinstance(val, list):
            return val[idx] if idx < len(val) else None
        return val

    # Prepare Specifications for 1 or 2 items
    specs = [] # List of dicts: {suffix, label, std, max, min, len_std, len_max, len_min ...}
    if is_dual:
        specs.append({
            "suffix": "_1", "label": " (右/R)", 
            "std": raw_weight_clean[0],
            "max": get_spec_val('clean_重量上限', 0),
            "min": get_spec_val('clean_重量下限', 0),
            "len_std": get_spec_val('clean_標準長度', 0),
            "len_max": get_spec_val('clean_長度上限', 0),
            "len_min": get_spec_val('clean_長度下限', 0)
        })
        specs.append({
            "suffix": "_2", "label": " (左/L)", 
            "std": raw_weight_clean[1], 
            "max": get_spec_val('clean_重量上限', 1),
            "min": get_spec_val('clean_重量下限', 1),
            "len_std": get_spec_val('clean_標準長度', 1),
            "len_max": get_spec_val('clean_長度上限', 1),
            "len_min": get_spec_val('clean_長度下限', 1)
        })
    else:
        specs.append({
            "suffix": "", "label": "",
            "std": raw_weight_clean,
            "max": current_part_data.get('clean_重量上限'),
            "min": current_part_data.get('clean_重量下限'),
            "len_std": current_part_data.get('clean_標準長度'),
            "len_max": current_part_data.get('clean_長度上限'),
            "len_min": current_part_data.get('clean_長度下限')
        })

    # --- History Trend Charts ---
    # Display side-by-side if dual
    cols_chart = st.columns(len(specs))
    
    for idx, sp in enumerate(specs):
        with cols_chart[idx]:
            # 1. Weight Chart
            chart_title = f"{selected_part_no}{sp['label']}"
            with st.expander(f"📊 重量歷史: {chart_title}", expanded=True):
                history_target_no = f"{selected_part_no}{sp['suffix']}"
                history_data = drive_integration.fetch_history(history_target_no)
                
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
                        w_max_limit = sp['max']
                        w_min_limit = sp['min']

                        y_cols = ['weight']
                        if w_max_limit is not None:
                            chart_df['Upper Limit'] = float(w_max_limit)
                            y_cols.append('Upper Limit')
                        if w_min_limit is not None:
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
                        st.caption("無有效重量歷史數據")
                else:
                    st.caption("尚無數據")

            # 2. Length Chart (if applicable)
            if sp['len_std'] is not None and sp['len_std'] > 0:
                with st.expander(f"📏 長度歷史: {chart_title}", expanded=False):
                     # Re-use history_data if available
                    if history_data:
                        chart_df_l = pd.DataFrame(history_data)
                        chart_df_l.replace("", pd.NA, inplace=True)
                         # Timestamp parsing repeated (could optimize, but safe)
                        chart_df_l['timestamp'] = pd.to_datetime(chart_df_l['timestamp'], errors='coerce')
                        if chart_df_l['timestamp'].dt.tz is None:
                             chart_df_l['timestamp'] = chart_df_l['timestamp'].dt.tz_localize('UTC')
                        chart_df_l['timestamp'] = chart_df_l['timestamp'].dt.tz_convert('Asia/Taipei')

                        chart_df_l['length'] = pd.to_numeric(chart_df_l['length'], errors='coerce')
                        chart_df_l = chart_df_l.dropna(subset=['timestamp', 'length'])

                        if not chart_df_l.empty:
                            l_max_limit = sp['len_max']
                            l_min_limit = sp['len_min']

                            y_cols_l = ['length']
                            if l_max_limit is not None:
                                chart_df_l['Upper Limit'] = float(l_max_limit)
                                y_cols_l.append('Upper Limit')
                            if l_min_limit is not None:
                                chart_df_l['Lower Limit'] = float(l_min_limit)
                                y_cols_l.append('Lower Limit')
                            
                            chart_long_l = chart_df_l.melt('timestamp', value_vars=y_cols_l, var_name='Type', value_name='Value')
                            
                            l_min_val = chart_long_l['Value'].min()
                            l_max_val = chart_long_l['Value'].max()
                            l_padding = (l_max_val - l_min_val) * 0.1 if l_max_val != l_min_val else 5

                            base_l = alt.Chart(chart_long_l).encode(
                                x=alt.X('timestamp', title='時間', axis=alt.Axis(format='%m/%d %H:%M')),
                                y=alt.Y('Value', title='長度 (mm)', 
                                        scale=alt.Scale(domain=[l_min_val - l_padding, l_max_val + l_padding])),
                                color=alt.Color('Type', title='類別', 
                                                scale=alt.Scale(domain=['length', 'Upper Limit', 'Lower Limit'],
                                                              range=['#00D4FF', '#457B9D', '#457B9D'])),
                                tooltip=[alt.Tooltip('timestamp', format='%Y-%m-%d %H:%M'), alt.Tooltip('Type'), alt.Tooltip('Value', format='.1f')]
                            )
                            st.altair_chart(base_l.mark_line().interactive(), use_container_width=True)
                        else:
                            st.caption("無有效長度歷史數據")
                    else:
                        st.caption("尚無數據")


    # --- Display Standard Info ---
    st.divider()
    
    # We construct the display string manually to handle "93 / 95"
    def format_val_display(col_name):
        val = current_part_data.get(col_name)
        if isinstance(val, list):
             # Try clean formatting if float
             return " / ".join([f"{v:g}" if isinstance(v, (float, int)) else str(v) for v in val])
        return f"{val}"

    info_col1, info_col2, info_col3 = st.columns(3)
    
    # Tolerance display is tricky for dual. We'll simplify or show multiple.
    # For now, let's just show the Standard Weight text.
    info_col1.metric("標準重量", format_val_display('重量'))
    info_col2.metric("原料編號", f"{current_part_data['原料編號']}")
    
    has_length_field = False 
    # Check if ANY spec has length > 0
    if any(s['len_std'] is not None and s['len_std'] > 0 for s in specs):
        has_length_field = True
             
    if has_length_field:
        info_col3.metric("標準長度", format_val_display('標準長度'))

    # --- Inspection Form ---
    st.subheader("巡檢輸入")
    inspection_type = st.radio("巡檢階段", ["首件", "中件", "末件"], horizontal=True)

    # Dictionary to hold user inputs: { index: {'weight': val, 'length': val} }
    user_inputs = {}
    
    cols_input = st.columns(len(specs))
    
    for idx, sp in enumerate(specs):
        with cols_input[idx]:
            st.markdown(f"**{sp['label'].strip(' ()') or '規格'}**")
            # Weight Input
            w_input = st.number_input(f"實測重量{sp['label']} (g)", min_value=0.0, step=0.1, format="%.1f", key=f"w_in_{idx}")
            
            # Length Input (Only if needed for this specific spec)
            l_input = None
            if sp['len_std'] is not None and sp['len_std'] > 0:
                l_input = st.number_input(f"實測長度{sp['label']} (mm)", min_value=0.0, step=0.1, format="%.1f", key=f"l_in_{idx}")
                
            user_inputs[idx] = {'weight': w_input, 'length': l_input}

            # Immediate Validation Feedback - Weight
            if w_input > 0:
                if sp['min'] is not None and sp['max'] is not None:
                    if not (sp['min'] <= w_input <= sp['max']):
                         st.error(f"⚠️ 重量異常! (標準: {sp['min']} ~ {sp['max']})")
                    else:
                         st.success("重量 OK")
            
            # Immediate Validation Feedback - Length
            if l_input is not None and l_input > 0:
                if sp['len_min'] is not None and sp['len_max'] is not None:
                     if not (sp['len_min'] <= l_input <= sp['len_max']):
                         st.error(f"⚠️ 長度異常! (標準: {sp['len_min']} ~ {sp['len_max']})")
                     else:
                         st.success("長度 OK")

    # --- Common Validation ---
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
        # Check if ALL weights are entered (if they are required)
        # Assuming we need both inputs if dual.
        any_missing_weight = any(user_inputs[i]['weight'] == 0 for i in user_inputs)
        
        if any_missing_weight:
            st.warning("請輸入所有重量數據")
        elif not material_ok:
            st.warning("原料確認為 NG，請確認正確料號")
        elif img_file is None:
            st.warning("請拍攝照片")
        else:
            with st.spinner("資料上傳中 (可能需要上傳兩筆數據)..."):
                
                # Shared Data
                tz = datetime.timezone(datetime.timedelta(hours=8))
                timestamp = datetime.datetime.now(tz)
                ts_str = timestamp.strftime("%Y%m%d_%H%M%S")
                key_control_str = ", ".join(control_points_log) if control_points_log else "N/A"
                
                all_success = True
                fail_msg = ""
                
                # Iterate and submit per spec
                for idx, sp in enumerate(specs):
                    # Prepare specific data
                    target_part_no = f"{selected_part_no}{sp['suffix']}"
                    m_weight = user_inputs[idx]['weight']
                    m_length = user_inputs[idx]['length']
                    
                    # Status Check
                    current_status = "OK"
                    if sp['min'] is not None and sp['max'] is not None:
                        if not (sp['min'] <= m_weight <= sp['max']):
                            current_status = "NG"
                    
                    # Construct Filename (unique per entry? or shared?)
                    # If we share image, filename can be shared or suffixed.
                    # Best to suffix filename too so they don't overwrite if using simple storage, 
                    # but GAS script usually handles unique IDs. 
                    # Let's suffix filename to be safe: ...part_no_1_... .jpg
                    filename = f"{selected_model}_{target_part_no}_{inspection_type}_{ts_str}.jpg"
                    
                    row_data = {
                        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        "model": selected_model,
                        "part_no": target_part_no, # Suffixed
                        "inspection_type": inspection_type,
                        "weight": m_weight,
                        "length": m_length if m_length is not None else "",
                        "material_ok": "OK" if material_ok else "NG",
                        "change_point": change_point,
                        "result": current_status,
                        "key_control_status": key_control_str
                    }
                    
                    # Reuse the same image file object! 
                    # Important: upload_and_append reads the file. If it reads to end, next call reads nothing.
                    # We must reset cursor.
                    if idx > 0 and hasattr(img_file, 'seek'):
                        img_file.seek(0)
                        
                    success, message = drive_integration.upload_and_append(img_file, filename, row_data)
                    if not success:
                        all_success = False
                        fail_msg += f"[{target_part_no} 失敗: {message}] "
            
            if all_success:
                st.success("數據提交成功! (Dual Mode Complete)" if is_dual else "數據提交成功!")
                st.balloons()
            else:
                st.error(f"部分或全部提交失敗: {fail_msg}")

    # --- Bottom: Abnormal Images ---
    # --- Defect History Image (Bottom) ---
    # --- Defect History Images (Bottom) ---
    st.divider()
    
    # Collect available defect images
    defect_images = []
    # 1. Main legacy column (mapped from 異常履歷寫真1)
    d1 = current_part_data.get('異常履歷寫真')
    if pd.notna(d1) and str(d1).strip(): defect_images.append(("1", str(d1).strip()))
    
    # 2. Extra columns
    for i in range(2, 4):
        col = f"異常履歷寫真{i}"
        val = current_part_data.get(col)
        if pd.notna(val) and str(val).strip():
            defect_images.append((str(i), str(val).strip()))

    if defect_images:
        with st.expander("⚠️ 過去異常履歷 (Defect History)", expanded=True):
            cols_defect = st.columns(len(defect_images))
            for idx, (label, fname) in enumerate(defect_images):
                img_path = os.path.join("quality_images", fname)
                with cols_defect[idx]:
                    if os.path.exists(img_path):
                        st.image(img_path, caption=f"異常履歷-{label}: {fname}", use_container_width=True)
                    else:
                        st.caption(f"履歷{label} 找不到檔案: {fname}")
    else:
        st.caption("無異常履歷記錄")

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
        
        # Add Image Link Column (Raw URL for LinkColumn)
        if 'image_url' in df_dash.columns:
            # Filter out empty URLs or non-strings
            df_dash['image_url'] = df_dash['image_url'].astype(str)
            df_dash['image_url'] = df_dash['image_url'].replace('nan', None).replace('', None)
            display_cols.append('image_url')

        st.dataframe(
            df_dash[display_cols].sort_values(by='timestamp', ascending=False),
            use_container_width=True,
            column_config={
                "timestamp": st.column_config.DatetimeColumn("時間", format="YYYY/MM/DD HH:mm"),
                "image_url": st.column_config.LinkColumn("照片佐證", display_text="📷 查看照片"),
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
