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
        padding: 10px 20px !important; /* Reduced padding to fit tight spaces */
        border-radius: 50px !important; /* Rounded Pills */
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: #e0e0e0 !important;
        transition: all 0.3s ease;
        flex: 1 1 0px; /* Force equal width */
        min-width: 0;
        justify-content: center;
        text-align: center;
        white-space: nowrap !important; /* Prevent text wrapping (N G split) */
        overflow: hidden;
        text-overflow: ellipsis;
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

    /* --- SIDEBAR OVERRIDE (Reset to Vertical List) --- */
    section[data-testid="stSidebar"] div[role='radiogroup'] {
        flex-direction: column !important;
        gap: 5px !important;
    }
    section[data-testid="stSidebar"] div[role='radiogroup'] > label {
        width: 100% !important;
        flex: none !important;
        border-radius: 10px !important;
        text-align: left !important;
        padding: 10px 15px !important;
        white-space: normal !important; /* Allow wrapping in sidebar */
        background: transparent !important;
        border: 1px solid transparent !important;
    }
    section[data-testid="stSidebar"] div[role='radiogroup'] > label:hover {
        background: rgba(255, 255, 255, 0.1) !important;
    }
    section[data-testid="stSidebar"] div[role='radiogroup'] > label[data-checked='true'] {
        background: rgba(255, 255, 255, 0.2) !important; /* Subtle highlight */
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        box-shadow: none !important;
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

# --- Sidebar Footer ---
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
        Designed by 何常豪
    </div>
    """, 
    unsafe_allow_html=True
)

if mode == "📝 巡檢輸入":
    # --- Top Navigation / Filter ---
    # --- Top Navigation / Filter ---
    # Title with Gradient Effect for Professional Look
    st.markdown("""
        <h1 style='text-align: center; margin-bottom: 20px;'>
            <span style='background: linear-gradient(90deg, #00d4ff, #005bea); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                瑞全智慧巡檢系統
            </span>
        </h1>
    """, unsafe_allow_html=True)

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
                # [Request] Limit image size (too big)
                # Use columns to center and constrain width (approx 33% - User Request "Smaller")
                c1, c2, c3 = st.columns([1, 1, 1])
                with c2:
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

    # --- Split Layout Implementation ---
    # Create two main columns: Left (Inputs) and Right (Reference Info)
    c_left, c_right = st.columns([1, 1], gap="medium")

    # --- RIGHT COLUMN: Reference Information ---
    with c_right:
        st.info("ℹ️ 標準規格與歷史參考")
        
        # --- Display Standard Info Cards ---
        # Custom Card Helper
        def display_info_card(col_obj, label, value_html):
            col_obj.markdown(f"""
            <div style="
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 10px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                text-align: center;
                margin-bottom: 10px;
            ">
                <div style="color: #a0a0a0; font-size: 0.9rem; margin-bottom: 3px;">{label}</div>
                <div style="color: #00d4ff; font-size: 1.2rem; font-weight: bold; word-wrap: break-word; line-height: 1.2;">
                    {value_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Helper to format value with tolerance
        def get_formatted_value_html(std_col, max_col, min_col, unit=""):
            std_val = current_part_data.get(f'clean_{std_col}')
            max_val = current_part_data.get(f'clean_{max_col}')
            min_val = current_part_data.get(f'clean_{min_col}')

            if not isinstance(std_val, list): std_val = [std_val]
            if not isinstance(max_val, list): max_val = [max_val]
            if not isinstance(min_val, list): min_val = [min_val]
            
            display_parts = []
            count = max(len(std_val), len(max_val), len(min_val))
            is_dual = (count > 1)
            
            for i in range(count):
                s = std_val[i] if i < len(std_val) else None
                mx = max_val[i] if i < len(max_val) else None
                mn = min_val[i] if i < len(min_val) else None
                
                s_str = f"{s:g}" if isinstance(s, (float, int)) else str(s)
                
                val_str = s_str
                if mx is not None and mn is not None:
                    # Use span for smaller font on tolerance
                    val_str += f'<span style="font-size: 0.8em; color: #ccc;"> ({mn:g}-{mx:g})</span>'
                
                if is_dual:
                    prefix = "R: " if i == 0 else "L: "
                    display_parts.append(f"<div><span style='font-size:0.6em; color:#888'>{prefix}</span>{val_str}</div>")
                else:
                    display_parts.append(val_str)
                    
            return "".join(display_parts)

        ric1, ric2, ric3 = st.columns(3)
        
        # 1. Standard Weight
        val_weight = get_formatted_value_html('重量', '重量上限', '重量下限')
        display_info_card(ric1, "標準重量 (g)", val_weight)
        
        # 2. Material Name
        mat_name = current_part_data.get('原料名稱')
        if pd.isna(mat_name) or str(mat_name).strip() == "":
            mat_name = current_part_data.get('原料編號', 'N/A')
        display_info_card(ric2, "原料名稱", f"{mat_name}")
        
        # 3. Standard Length
        has_length_field = False 
        if any(s['len_std'] is not None and s['len_std'] > 0 for s in specs):
            has_length_field = True
                 
        if has_length_field:
            val_len = get_formatted_value_html('標準長度', '長度上限', '長度下限')
            display_info_card(ric3, "標準長度 (mm)", val_len)
        else:
            display_info_card(ric3, "標準長度 (mm)", "<span style='color:#555;'>N/A</span>")

        # --- Product Image (Standard) ---
        product_img_filename = current_part_data.get('產品圖片')
        if pd.notna(product_img_filename) and str(product_img_filename).strip():
            import os
            img_path = os.path.join("quality_images", str(product_img_filename).strip())
            
            with st.expander("🖼️ 產品標準圖 (Standard Image)", expanded=False):
                if os.path.exists(img_path):
                    # Center the image
                    st.image(img_path, caption=f"標準圖: {product_img_filename}", use_container_width=True)
                else:
                    st.warning(f"找不到圖片檔案: {product_img_filename}")

        # --- Defect History Images ---
        defect_images = []
        d1 = current_part_data.get('異常履歷寫真')
        if pd.notna(d1) and str(d1).strip(): defect_images.append(("1", str(d1).strip()))
        for i in range(2, 4):
            col = f"異常履歷寫真{i}"
            val = current_part_data.get(col)
            if pd.notna(val) and str(val).strip():
                defect_images.append((str(i), str(val).strip()))

        if defect_images:
            with st.expander("⚠️ 過去異常履歷 (Defect History)", expanded=True):
                dh_cols = st.columns(3)
                for idx, (label, fname) in enumerate(defect_images):
                    col_idx = idx % 3
                    img_path = os.path.join("quality_images", fname)
                    with dh_cols[col_idx]:
                        if os.path.exists(img_path):
                            st.image(img_path, caption=f"履歷-{label}", use_container_width=True)
                        else:
                            st.caption(f"履歷{label} 失效")
        else:
            st.caption("✅ 此零件無過去異常履歷")

        # --- Key Control Points (Reference only) ---
        st.markdown("##### ⚠️ 重點管制項目")
        valid_cps = []
        for i in range(1, 4):
            col_name = f"重點管制{i}"
            val = current_part_data.get(col_name)
            if pd.notna(val) and str(val).strip():
                valid_cps.append(str(val).strip())
                
        if valid_cps:
            for cp in valid_cps:
                st.markdown(f"- 🔴 **{cp}**")
            control_points_log = ["Viewed"] 
        else:
            st.caption("無重點管制項目")
            control_points_log = []

        # --- History Trend Charts ---
        # Use nested columns for charts
        cols_chart = st.columns(len(specs))
        
        for idx, sp in enumerate(specs):
            with cols_chart[idx]:
                chart_title = f"{selected_part_no}{sp['label']}"
                # Weight Chart
                with st.expander(f"📊 重量Trend: {chart_title}", expanded=False):
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
                                chart_df['Limit H'] = float(w_max_limit)
                                y_cols.append('Limit H')
                            if w_min_limit is not None:
                                chart_df['Limit L'] = float(w_min_limit)
                                y_cols.append('Limit L')
                            
                            chart_long = chart_df.melt('timestamp', value_vars=y_cols, var_name='Type', value_name='Value')
                            y_min_val = chart_long['Value'].min(); y_max_val = chart_long['Value'].max()
                            padding = (y_max_val - y_min_val) * 0.1 if y_max_val != y_min_val else 5
                            
                            base = alt.Chart(chart_long).encode(
                                x=alt.X('timestamp', title=None, axis=alt.Axis(format='%m/%d', ticks=False)),
                                y=alt.Y('Value', title='g', scale=alt.Scale(domain=[y_min_val - padding, y_max_val + padding])),
                                color=alt.Color('Type', legend=None, scale=alt.Scale(range=['#FF6C6C', '#457B9D', '#457B9D'])),
                                tooltip=['timestamp', 'Value']
                            )
                            st.altair_chart((base.mark_line() + base.mark_point(size=30)).interactive(), use_container_width=True)
                        else:
                            st.caption("無數據")
                    else:
                        st.caption("無數據")
                
                # Length Chart if needed
                if sp['len_std'] is not None and sp['len_std'] > 0:
                     # (Simplified logic for length chart to save space, user can expand if used)
                     with st.expander(f"📏 長度Trend: {chart_title}", expanded=False):
                         st.caption("長度趨勢圖 (請參考詳細數據)")


    # --- LEFT COLUMN: Inputs & Operation ---
    with c_left:
        st.subheader("📝 巡檢輸入作業")
        
        inspection_type = st.radio("巡檢階段", ["首件", "中件", "末件"], horizontal=True)

        user_inputs = {}
        # Input Loop
        for idx, sp in enumerate(specs):
            st.markdown(f"**{sp['label'].strip(' ()') or '規格'}**")
            
            def get_hint(mn, mx):
                 return f" ({mn}~{mx})" if (mn is not None and mx is not None) else ""

            # Weight
            w_hint = get_hint(sp['min'], sp['max'])
            w_input = st.number_input(f"重量 (g){w_hint}", min_value=0.0, step=0.1, format="%.1f", key=f"w_in_{idx}")
            
            # Length
            l_input = None
            if sp['len_std'] is not None and sp['len_std'] > 0:
                l_hint = get_hint(sp['len_min'], sp['len_max'])
                l_input = st.number_input(f"長度 (mm){l_hint}", min_value=0.0, step=0.1, format="%.1f", key=f"l_in_{idx}")
                
            user_inputs[idx] = {'weight': w_input, 'length': l_input}

            # Validation Msg in Expandable to save space? Or just small text.
            # Use columns for compact feedback
            msg_cols = st.columns([1, 1])
            # Weight Msg
            if w_input > 0:
                if sp['min'] is not None and sp['max'] is not None:
                     if not (sp['min'] <= w_input <= sp['max']):
                         st.error(f"⚠️ 重量NG")
                     else:
                         st.success("重量 OK")
            # Length Msg
            if l_input is not None and l_input > 0:
                if sp['len_min'] is not None and sp['len_max'] is not None:
                     if not (sp['len_min'] <= l_input <= sp['len_max']):
                         st.error(f"⚠️ 長度NG")
                     else:
                         st.success("長度 OK")
            st.markdown("---")

        # Material Check
        st.markdown("##### 📦 原料確認")
        material_check = st.radio("原料狀態", ["OK", "NG"], horizontal=True, key="mat_check_radio")
        material_ok = (material_check == "OK")

        # Change Point
        change_point = st.text_area("變化點說明 (選填)", placeholder="如有異常請說明...", height=100)

        # Photo Input
        input_method = st.radio("影像輸入", ["📸 網頁相機", "📂 上傳照片"], index=1, horizontal=True)
        img_files = []
        if input_method == "📸 網頁相機":
            cam_file = st.camera_input("拍照")
            if cam_file: img_files = [cam_file]
        else:
            uploaded_files = st.file_uploader("上傳照片", type=["jpg", "png"], accept_multiple_files=True)
            if uploaded_files: img_files = uploaded_files

        # Submit Button
        st.write("") # Spacer
        if st.button("🚀 提交巡檢數據", use_container_width=True, type="primary"):
            # Check inputs
            any_missing_weight = any(user_inputs[i]['weight'] == 0 for i in user_inputs)
            
            if any_missing_weight:
                st.warning("請輸入所有重量數據")
            elif not material_ok:
                st.warning("原料確認為 NG!")
            else:
                with st.spinner("資料上傳中..."):
                    
                    tz = datetime.timezone(datetime.timedelta(hours=8))
                    timestamp = datetime.datetime.now(tz)
                    ts_str = timestamp.strftime("%Y%m%d_%H%M%S")
                    key_control_str = ", ".join(control_points_log) if control_points_log else "N/A"
                    all_success = True
                    fail_msg = ""
                    primary_img = img_files[0] if img_files else None
                    
                    for idx, sp in enumerate(specs):
                        target_part_no = f"{selected_part_no}{sp['suffix']}"
                        m_weight = user_inputs[idx]['weight']
                        m_length = user_inputs[idx]['length']
                        
                        current_status = "OK"
                        if sp['min'] is not None and sp['max'] is not None:
                            if not (sp['min'] <= m_weight <= sp['max']):
                                current_status = "NG"
                        
                        filename = f"{selected_model}_{target_part_no}_{inspection_type}_{ts_str}.jpg"
                        row_data = {
                            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                            "model": selected_model,
                            "part_no": target_part_no,
                            "inspection_type": inspection_type,
                            "weight": m_weight,
                            "length": m_length if m_length is not None else "",
                            "material_ok": "OK" if material_ok else "NG",
                            "change_point": change_point,
                            "result": current_status,
                            "key_control_status": key_control_str
                        }
                        
                        img_to_send = primary_img
                        if is_dual and idx > 0: img_to_send = None 
                        if img_to_send and hasattr(img_to_send, 'seek'):
                             try: img_to_send.seek(0)
                             except: pass
                            
                        success, message = drive_integration.upload_and_append(img_to_send, filename, row_data)
                        if not success:
                            all_success = False
                            fail_msg += f"[{target_part_no} Err] "
                
                if all_success:
                    st.success("提交成功!")
                    st.balloons()
                else:
                    st.error(f"提交失敗: {fail_msg}")

    # --- Bottom: Abnormal Images (Removed - Moved to Top) ---

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
            # Dynamic Part No Filter based on Model (Use Master Data 'df' to group molds)
            # This allows selecting "Base Part No" and showing all suffixes (_1, _2)
            if filter_model != "全部":
                if '車型' in df.columns and '品番' in df.columns:
                     available_parts = df[df['車型'] == filter_model]['品番'].unique()
                else:
                     available_parts = []
                parts_dash = ["全部"] + list(available_parts)
            else:
                parts_dash = ["全部"] + list(df['品番'].unique())
            
            filter_part = st.selectbox("篩選品番 (模具)", parts_dash)
            
        with col_d3:
            filter_result = st.radio("篩選結果", ["全部", "NG Only"], horizontal=True)

        # Apply Filters
        if filter_model != "全部":
            df_dash = df_dash[df_dash['model'] == filter_model]
        if filter_part != "全部":
            # Match Base Part No OR Base Part No + Suffix (e.g. _1, _2)
            # Using startswith is risky if Part A is prefix of Part B.
            # Safer: exact match or startswith(part + '_')
            df_dash = df_dash[
                df_dash['part_no'].apply(lambda x: str(x) == filter_part or str(x).startswith(str(filter_part) + '_'))
            ]
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

        # --- Data Grid & Photo Preview [Request 4] ---
        st.subheader("📋 詳細履歷表 (點擊選取可檢視大圖)")
        
        # Select columns to display
        display_cols = ['timestamp', 'model', 'part_no', 'weight', 'result', '詳細管制狀態', 'change_point']
        
        # Add Image Link Column (Raw URL for LinkColumn)
        if 'image_url' in df_dash.columns:
            # Filter out empty URLs or non-strings
            df_dash['image_url'] = df_dash['image_url'].astype(str)
            df_dash['image_url'] = df_dash['image_url'].replace('nan', None).replace('', None)
            display_cols.append('image_url')

        # Enable Selection
        event = st.dataframe(
            df_dash[display_cols].sort_values(by='timestamp', ascending=False),
            use_container_width=True,
            column_config={
                "timestamp": st.column_config.DatetimeColumn("時間", format="YYYY/MM/DD HH:mm"),
                "image_url": st.column_config.LinkColumn("照片佐證", display_text="📷 查看照片"),
                "result": st.column_config.TextColumn("判定", help="OK or NG"),
                "change_point": st.column_config.TextColumn("變化點", width="medium"),
                "詳細管制狀態": st.column_config.TextColumn("重點管制細節", width="large"),
            },
            selection_mode="single-row",
            on_select="rerun"
        )
        
        # Show Selected Image
        if len(event.selection.rows) > 0:
            selected_idx = event.selection.rows[0]
            # Need to find the actual row in sorted/filtered df? 
            # Re-sort to match display
            sorted_df = df_dash.sort_values(by='timestamp', ascending=False)
            selected_row = sorted_df.iloc[selected_idx]
            
            st.divider()
            st.markdown(f"### 📷 選取項目的照片: {selected_row['part_no']}")
            
            img_url = selected_row.get('image_url')
            if img_url and str(img_url).startswith('http'):
                st.image(img_url, caption="現場拍攝照片", use_container_width=True)
            else:
                st.info("此筆記錄無照片")

        # --- Charts ---
        st.subheader("趨勢分析")
        chart_bar = alt.Chart(df_dash).mark_bar().encode(
            x='model',
            y='count()',
            color='result'
        )
        st.altair_chart(chart_bar, use_container_width=True)
