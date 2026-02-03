import streamlit as st
import pandas as pd
import data_manager
import datetime
import altair as alt
import json
import drive_integration
import streamlit.components.v1 as components
import os

# --- Helper: Image Integrity Check ---
@st.cache_data(show_spinner=False)
def check_image_availability(image_path):
    """
    Verifies if the image exists and is not empty (iCloud sync issue).
    Returns the path if valid, None otherwise.
    """
    if not image_path: return None
    
    # 1. Check existence
    if not os.path.exists(image_path):
        return None
        
    # 2. Check size (Fix for iCloud empty placeholders)
    try:
        if os.path.getsize(image_path) == 0:
            return None
    except OSError:
        return None
        
    return image_path

# --- Page Config ---
st.set_page_config(
    page_title="瑞全智慧巡檢",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Mobile Optimization / Aesthetics
# --- Apply Apple UI CSS ---
st.markdown("""
<style>
    /* --- 1. Global Reset & Apple Dark Mode Base --- */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&display=swap');

    .stApp {
        background-color: #000000; /* Deep Black for OLED feel */
        color: #f5f5f7; /* Apple Off-White */
        font-family: 'Noto Sans TC', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* --- 2. Typography --- */
    h1, h2, h3, .stMarkdown, .stButton, p, label, input, button, textarea, div {
        font-family: 'Noto Sans TC', sans-serif !important;
    }

    h1, h2, h3 {
        color: #f5f5f7 !important;
        font-weight: 700;
        letter-spacing: -0.02em; /* Tight Apple Headers */
    }
    
    h1 { font-size: 2.5rem !important; }
    h2 { font-size: 1.8rem !important; }
    h3 { font-size: 1.4rem !important; }

    /* --- 3. iOS "Island" Cards (Glassmorphism) --- */
    div[data-testid="stMetric"] {
        background: rgba(28, 28, 30, 0.6); /* #1c1c1e with opacity */
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 18px; /* Apple Rounded Corners */
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        text-align: center;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        color: #86868b !important; /* Apple Subtext Gray */
        font-weight: 500;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        color: #f5f5f7 !important;
        font-weight: 600;
    }

    /* --- 4. Inputs (Flat & Clean) --- */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div, .stTextArea textarea {
        background-color: #1c1c1e !important;
        color: #f5f5f7 !important;
        border: none !important;
        border-radius: 10px !important;
        height: 3.2rem !important;
        font-size: 1.1rem !important;
        padding-left: 15px !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
        box-shadow: 0 0 0 2px #0A84FF !important; /* System Blue Focus Ring */
    }

    /* --- 5. Segmented Controls (Radio Buttons) --- */
    .stRadio > label { font-size: 1.1rem !important; color: #86868b !important; margin-bottom: 8px; }
    .stRadio div[role='radiogroup'] {
        background: #1c1c1e;
        padding: 4px;
        border-radius: 12px;
        display: inline-flex;
        gap: 0px;
    }
    .stRadio div[role='radiogroup'] > label { 
        background-color: transparent !important;
        padding: 8px 20px !important;
        border-radius: 8px !important;
        border: none !important;
        color: #86868b !important;
        transition: all 0.2s ease;
        margin: 0 !important;
        box-shadow: none !important;
    }
    .stRadio div[role='radiogroup'] > label:hover {
        color: #f5f5f7 !important;
    }
    .stRadio div[role='radiogroup'] > label[data-checked='true'] {
        background-color: #636366 !important; /* Selected Gray */
        color: #ffffff !important;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
    }

    /* Sidebar Radio Override */
    section[data-testid="stSidebar"] div[role='radiogroup'] {
        background: transparent !important;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    section[data-testid="stSidebar"] div[role='radiogroup'] > label {
        width: 100% !important;
        background: transparent !important;
        text-align: left !important;
        padding: 10px 10px !important;
    }
    section[data-testid="stSidebar"] div[role='radiogroup'] > label[data-checked='true'] {
        background-color: rgba(10, 132, 255, 0.2) !important; /* Transparent Blue */
        color: #0A84FF !important;
    }

    /* --- 6. Buttons (Apple Blue Pills) --- */
    div.stButton > button:first-child {
        background-color: #0A84FF !important; /* System Blue */
        color: white !important;
        font-size: 1.2rem !important;
        height: 3.5rem !important;
        border-radius: 40px !important;
        border: none !important;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(10, 132, 255, 0.3);
        transition: all 0.2s;
        width: 100%;
    }
    div.stButton > button:first-child:active {
        transform: scale(0.97);
        opacity: 0.8;
    }
    div.stButton > button:first-child:hover {
        background-color: #0077ED !important;
    }

    /* --- 7. Status Alerts --- */
    .stSuccess, .stError, .stInfo, .stWarning {
        background-color: rgba(28, 28, 30, 0.8) !important;
        backdrop-filter: blur(10px);
        border-radius: 12px !important;
        border: none !important;
        color: #f5f5f7 !important;
    }
    
    /* ENLARGE INPUTS for Mobile */
    div[data-testid="stNumberInput"] input {
        font-size: 20px !important;
        height: 50px !important;
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
    # Run periodically to catch re-renders
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
if st.sidebar.button("🔄 手動更新數據 (Refresh)", use_container_width=True):
    drive_integration.fetch_history.clear()
    drive_integration.fetch_all_data.clear()
    st.toast("已強制更新與 Google Sheet 同步", icon="✅")
    st.rerun()

st.sidebar.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
        Designed by 何常豪
    </div>
    """, 
    unsafe_allow_html=True
)

if mode == "📝 巡檢輸入":
    # --- Session State Management ---
    if 'inspection_started' not in st.session_state:
        st.session_state['inspection_started'] = False
    
    # --- State 1: Landing Page (Selection) ---
    if not st.session_state['inspection_started']:
        # Title
        st.markdown("""
            <h1 style='text-align: center; margin-bottom: 30px;'>
                瑞全智慧巡檢系統
            </h1>
        """, unsafe_allow_html=True)
        
        # Container for Selection
        # 1. Model & Part Selection (Top)
        with st.container():
            col_model, col_part = st.columns([1, 1])
            
            with col_model:
                st.subheader("1️⃣ 選擇車型")
                car_models = df['車型'].unique()
                default_model_idx = 0
                if 'saved_model' in st.session_state and st.session_state['saved_model'] in car_models:
                    default_model_idx = list(car_models).index(st.session_state['saved_model'])
                
                selected_model_landing = st.selectbox("車型", car_models, index=default_model_idx, key="landing_model")

            # Filter Parts based on Model
            model_filtered_df = data_manager.get_filtered_data(df, car_model=selected_model_landing)
            available_parts = ["全部"] + list(model_filtered_df['品番'].unique())
            
            with col_part:
                st.subheader("2️⃣ 選擇品番 (可選)")
                selected_part_filter = st.selectbox("品番篩選", available_parts, key="landing_part_filter")

        # Apply Part Filter to Grid Data
        if selected_part_filter != "全部":
            filtered_df = model_filtered_df[model_filtered_df['品番'] == selected_part_filter]
        else:
            filtered_df = model_filtered_df
        
        # 2. Product Grid View
        st.markdown("---")
        st.subheader(f"📦 {selected_model_landing} 產品列表 (點擊選擇)")
        
        # Initialize selection state if not present
        if 'temp_selected_part' not in st.session_state:
            st.session_state['temp_selected_part'] = None

        # Grid Layout
        # Increased to 5 columns for smaller images as requested
        cols = st.columns(5)
        
        for idx, row in filtered_df.iterrows():
            part_no = row['品番']
            part_name = row.get('品名', 'N/A')
            img_name = row.get('產品圖片')
            
            with cols[idx % 5]:
                with st.container():
                    # Image
                    if pd.notna(img_name) and str(img_name).strip():
                        img_path = os.path.join("quality_images", str(img_name).strip())
                        valid_img = check_image_availability(img_path)
                        if valid_img:
                            st.image(valid_img, use_container_width=True)
                        else:
                            st.image("https://via.placeholder.com/300x200?text=No+Image", use_container_width=True)
                    else:
                         st.image("https://via.placeholder.com/300x200?text=No+Image", use_container_width=True)
                    
                    # Label
                    st.markdown(f"**{part_no}**")
                    st.caption(f"{part_name}")
                    
                    # Select and Start Button
                    if st.button("登入巡檢資料", key=f"btn_{part_no}", use_container_width=True):
                        st.session_state['saved_model'] = selected_model_landing
                        st.session_state['saved_part'] = part_no
                        st.session_state['inspection_started'] = True
                        st.rerun()

    # --- State 2: Inspection Form ---
    else:
        # Retrieve selections
        selected_model = st.session_state.get('saved_model')
        selected_part_no = st.session_state.get('saved_part')
        
        # Safety Check (if state lost)
        if not selected_model or not selected_part_no:
             st.session_state['inspection_started'] = False
             st.rerun()

        # Navigation Bar
        nav_col1, nav_col2 = st.columns([1, 4])
        with nav_col1:
            if st.button("⬅️ 返回選擇", use_container_width=True):
                st.session_state['inspection_started'] = False
                st.rerun()
        with nav_col2:
            st.markdown(f"### 巡檢: {selected_model} - {selected_part_no}")

        # --- Re-fetch Data for Form ---
        filtered_df = data_manager.get_filtered_data(df, car_model=selected_model)
        # Ensure we get the specific part
        current_part_data = filtered_df[filtered_df['品番'] == selected_part_no].iloc[0]

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


        
        # [3] Product Image (Standard) - KEEPING as per user habit
        product_img_filename = current_part_data.get('產品圖片')
        if pd.notna(product_img_filename) and str(product_img_filename).strip():
            img_path = os.path.join("quality_images", str(product_img_filename).strip())
            valid_img_path = check_image_availability(img_path)

            with st.expander("🖼️ 產品標準圖 (Standard Image)", expanded=True):
                if valid_img_path:
                    # Compressed view
                    c1, c2, c3 = st.columns([1, 2, 1])
                    with c2:
                        st.image(valid_img_path, caption=f"標準圖: {product_img_filename}", use_container_width=True)
                else:
                    st.warning(f"找不到圖片檔案或檔案損壞: {product_img_filename}")

        # [2] History Trend Charts
        chart_cols = st.columns(len(specs))
        
        for idx, sp in enumerate(specs):
            with chart_cols[idx]:
                chart_title = f"{selected_part_no}{sp['label']}"
                # Weight Chart
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
                                chart_df['Limit H'] = float(w_max_limit)
                                y_cols.append('Limit H')
                            if w_min_limit is not None:
                                chart_df['Limit L'] = float(w_min_limit)
                                y_cols.append('Limit L')
                            
                            chart_long = chart_df.melt('timestamp', value_vars=y_cols, var_name='MetricType', value_name='Value')
                            y_min_val = chart_long['Value'].min(); y_max_val = chart_long['Value'].max()
                            padding = (y_max_val - y_min_val) * 0.1 if y_max_val != y_min_val else 5
                            
                            color_domain = ['Limit H', 'Limit L', 'weight']
                            color_range = ['#FF6C6C', '#FF6C6C', '#457B9D'] 
                            
                            base = alt.Chart(chart_long).encode(
                                x=alt.X('timestamp', title=None, axis=alt.Axis(format='%m/%d', ticks=False)),
                                y=alt.Y('Value', title='g', scale=alt.Scale(domain=[y_min_val - padding, y_max_val + padding])),
                                color=alt.Color('MetricType', legend=None, scale=alt.Scale(domain=color_domain, range=color_range)),
                                tooltip=['timestamp', 'Value', 'MetricType']
                            )
                            
                            line_w = base.transform_filter(alt.datum.MetricType == 'weight').mark_line(strokeWidth=3)
                            point_w = base.transform_filter(alt.datum.MetricType == 'weight').mark_point(size=60, filled=True)
                            line_limits = base.transform_filter((alt.datum.MetricType == 'Limit H') | (alt.datum.MetricType == 'Limit L')).mark_line(strokeDash=[5, 5], opacity=0.8)

                            st.altair_chart((line_w + point_w + line_limits).interactive(), use_container_width=True)
                        else:
                            st.caption("無數據")
                    else:
                        st.caption("無數據")
                
                # Length Chart
                if sp['len_std'] is not None and sp['len_std'] > 0:
                        with st.expander(f"📏 長度歷史: {chart_title}", expanded=False):
                            st.caption("長度趨勢圖 (請參考詳細數據)")


        # --- [NEW] Historical Images Gallery ---
        # Fetch all data and filter for images of this product
        # 1. Fetch
        # Note: fetch_all_data() might be heavy, but it's the only way to get image URLs currently
        with st.expander("📸 歷史檢測照片 (Inspection History Images)", expanded=False):
            with st.spinner("載入歷史照片中..."):
                all_records = drive_integration.fetch_all_data()
                
            if all_records:
                df_history = pd.DataFrame(all_records)
                # Filter by Model and Part No (or suffixes)
                # Check column existence
                if 'part_no' in df_history.columns and 'image_url' in df_history.columns:
                    # Filter logic
                    # Match exact part_no OR part_no + suffix (e.g. 62511-VU010 match 62511-VU010_1)
                    # We can use the 'specs' to know the target part numbers
                    target_parts = [f"{selected_part_no}{sp['suffix']}" for sp in specs]
                    
                    df_filtered_imgs = df_history[
                        df_history['part_no'].isin(target_parts) &
                        df_history['image_url'].notna() &
                        (df_history['image_url'] != "")
                    ].copy()
                    
                    if not df_filtered_imgs.empty:
                        # Sort by timestamp (newest first)
                        if 'timestamp' in df_filtered_imgs.columns:
                            df_filtered_imgs['timestamp'] = pd.to_datetime(df_filtered_imgs['timestamp'], errors='coerce')
                            df_filtered_imgs = df_filtered_imgs.sort_values(by='timestamp', ascending=False)
                        
                        # Limit to latest 12
                        df_filtered_imgs = df_filtered_imgs.head(12)
                        
                        # Display
                        img_cols = st.columns(3)
                        for i, row in enumerate(df_filtered_imgs.itertuples()):
                            col = img_cols[i % 3]
                            try:
                                ts_display = row.timestamp.strftime('%m/%d %H:%M') if pd.notnull(row.timestamp) else "N/A"
                            except: ts_display = "N/A"
                            
                            col.image(row.image_url, caption=f"{ts_display} ({row.result})", use_container_width=True)
                    else:
                        st.info("此產品尚無歷史照片")
                else:
                    st.caption("無法讀取歷史資料 (資料欄位缺失)")
            else:
                st.caption("無歷史資料")


        # [1] Standard Info Cards (Reference Info)
        st.info("ℹ️ 標準規格參考")
        
        # Custom Card Helper (Apple Style)
        # Redefined here because we are in a new block
        def display_info_card(col_obj, label, value_html):
            col_obj.markdown(f"""
            <div style="
                background: rgba(28, 28, 30, 0.6);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 18px; /* Apple Rounded Corners */
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
                text-align: center;
                margin-bottom: 10px;
            ">
                <div style="color: #86868b; font-size: 0.9rem; margin-bottom: 3px; font-weight: 500;">{label}</div>
                <div style="color: #f5f5f7; font-size: 1.3rem; font-weight: 600; word-wrap: break-word; line-height: 1.2;">
                    {value_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

        def get_formatted_value_html(std_col, max_col, min_col, unit=""):
            std_val = current_part_data.get(f'clean_{std_col}')
            max_val = current_part_data.get(f'clean_{max_col}')
            min_val = current_part_data.get(f'clean_{min_col}')

            if not isinstance(std_val, list): std_val = [std_val]
            if not isinstance(max_val, list): max_val = [max_val]
            if not isinstance(min_val, list): min_val = [min_val]
            
            display_parts = []
            count = max(len(std_val), len(max_val), len(min_val))
            is_dual_local = (count > 1)
            
            for i in range(count):
                s = std_val[i] if i < len(std_val) else None
                mx = max_val[i] if i < len(max_val) else None
                mn = min_val[i] if i < len(min_val) else None
                
                s_str = f"{s:g}" if isinstance(s, (float, int)) else str(s)
                
                val_str = s_str
                if mx is not None and mn is not None:
                    val_str += f'<span style="font-size: 0.8em; color: #ccc;"> ({mn:g}-{mx:g})</span>'
                
                if is_dual_local:
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

        # [4] Defect History Images (Static)
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
                    valid_img_path = check_image_availability(img_path)
                    
                    with dh_cols[col_idx]:
                        if valid_img_path:
                            st.image(valid_img_path, caption=f"履歷-{label}", use_container_width=True)
                        else:
                            st.caption(f"履歷{label} 讀取失敗")

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


        # [5] Inputs & Operation
        st.divider()
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

            # Validation Msg
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

        # Actions
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
                                "result": current_status
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
                        
                        # --- Smart Cache Clearing ---
                        drive_integration.fetch_history.clear()
                        drive_integration.fetch_all_data.clear()
                        st.toast("✅ 已清除快取，重新載入最新數據", icon="🔄")
                        
                    else:
                        st.error(f"提交失敗: {fail_msg}")

elif mode == "📊 數據戰情室":
    st.header("📊 生產品質戰情室")
    st.caption("即時同步 Google Sheet 雲端數據")
    
    # --- Dashboard Navigation ---
    dash_page = st.sidebar.radio("功能切換", ["📈 重量趨勢追蹤", "🛡️ 變化點管理中心"], key="dash_nav")

    with st.spinner("正在連線至總部資料庫，請稍候..."):
        raw_data = drive_integration.fetch_all_data()

    if not raw_data:
        st.warning("目前無數據或無法連線至 Google Sheet (請確認 GAS V4 是否部署成功)。")
    else:
        df_dash = pd.DataFrame(raw_data)
        
        # --- Timezone Fix ---
        if 'timestamp' in df_dash.columns:
            df_dash['timestamp'] = pd.to_datetime(df_dash['timestamp'], errors='coerce')
            if df_dash['timestamp'].dt.tz is None:
                 df_dash['timestamp'] = df_dash['timestamp'].dt.tz_localize('UTC')
            df_dash['timestamp'] = df_dash['timestamp'].dt.tz_convert('Asia/Taipei')

        # --- Schema Safety Check (Fix for Cache/Legacy Data) ---
        if 'status' not in df_dash.columns:
            df_dash['status'] = "未審核"
        if 'manager_comment' not in df_dash.columns:
            df_dash['manager_comment'] = ""
        
        # Ensure values are not NaN (fillna)
        df_dash['status'] = df_dash['status'].fillna("未審核")
        df_dash['manager_comment'] = df_dash['manager_comment'].fillna("")
            
        # ==========================================
        # 1. Weight Trend Tracking (Original Dashboard)
        # ==========================================
        if dash_page == "📈 重量趨勢追蹤":
            # --- Filters ---
            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1:
                models_dash = ["全部"] + list(df_dash['model'].unique())
                filter_model = st.selectbox("篩選車型", models_dash)
            with col_d2:
                 if filter_model != "全部":
                     parts_dash = ["全部"] + list(df_dash[df_dash['model'] == filter_model]['part_no'].unique())
                 else:
                     parts_dash = ["全部"] + list(df_dash['part_no'].unique())
                 filter_part = st.selectbox("篩選品番", parts_dash)
                 
                 # [FEATURE] Show small product image if filtered
                 if filter_part != "全部":
                     img_path = f"quality_images/{filter_part}_main.jpg"
                     if check_image_availability(img_path):
                         st.image(img_path, width=200, caption=filter_part)
            with col_d3:
                 results_dash = ["全部"] + list(df_dash['result'].unique())
                 filter_result = st.selectbox("篩選結果", results_dash)
            
            # Apply filters
            df_view = df_dash.copy()
            if filter_model != "全部": df_view = df_view[df_view['model'] == filter_model]
            if filter_part != "全部": df_view = df_view[df_view['part_no'] == filter_part]
            if filter_result != "全部": df_view = df_view[df_view['result'] == filter_result]
            
            st.dataframe(df_view, use_container_width=True)
            
            if not df_view.empty:
                st.subheader("📈 重量趨勢圖")
                chart = alt.Chart(df_view).mark_line(point=True).encode(
                    x=alt.X('timestamp', title='時間', axis=alt.Axis(format='%m/%d %H:%M')),
                    y=alt.Y('weight', title='重量 (g)'),
                    color='part_no',
                    tooltip=['timestamp', 'model', 'part_no', 'weight', 'result']
                ).interactive()
                st.altair_chart(chart, use_container_width=True)

        # ==========================================
        # 2. Change Point Management Center
        # ==========================================
        elif dash_page == "🛡️ 變化點管理中心":
            st.subheader("🛡️ 變化點管理中心")
            
            # Filter Logic: Only rows with Change Points
            df_cp = df_dash[df_dash['change_point'].ne("") & df_dash['change_point'].notna()].copy()
            
            # Sort by Time Descending
            df_cp = df_cp.sort_values(by='timestamp', ascending=False)
            
            # Filter Logic: Status
            status_filter = st.radio("狀態篩選", ["待處理 (未審核/審核中)", "全部 (含結案)"], horizontal=True)
            
            if status_filter == "待處理 (未審核/審核中)":
                df_cp = df_cp[~df_cp['status'].isin(["結案", "Closed"])]
            
            st.info(f"共發現 {len(df_cp)} 筆變化點記錄")
            
            for index, row in df_cp.iterrows():
                # Define Status Colors
                stat_color = "red"
                if row['status'] == "審核中": stat_color = "orange"
                elif row['status'] in ["結案", "Closed"]: stat_color = "green"
                
                with st.expander(f":{stat_color}[{row['status']}] {row['timestamp'].strftime('%Y-%m-%d %H:%M')} - {row['model']} {row['part_no']}", expanded=True):
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.markdown(f"**變化點內容:**")
                        st.error(row['change_point'])
                        st.caption(f"巡檢結果: {row['result']}")
                    
                    with c2:
                        # Image logic
                        if pd.notna(row.get('image')) and str(row.get('image')).strip():
                             st.markdown(f"📄 照片ID: `{row.get('image')}`")
                    
                    st.divider()
                    
                    # --- Manager Actions ---
                    m_col1, m_col2, m_col3 = st.columns([1, 2, 1])
                    
                    # Unique Key using timestamp + part_no to avoid conflicts
                    u_key = f"{row['timestamp']}_{row['part_no']}"
                    
                    with m_col1:
                        # Status Selector
                        current_stat = row.get('status', '未審核')
                        if not current_stat: current_stat = '未審核'
                        
                        target_index = 0
                        opts = ["未審核", "審核中", "結案"]
                        if current_stat in opts:
                            target_index = opts.index(current_stat)
                        
                        new_status = st.selectbox("審核狀態", opts, index=target_index, key=f"stat_{u_key}")
                    
                    with m_col2:
                         # Comment Input
                         current_comment = row.get('manager_comment', '')
                         if pd.isna(current_comment): current_comment = ""
                         new_comment = st.text_input("主管留言", value=str(current_comment), key=f"comm_{u_key}")
                    
                    with m_col3:
                        st.write("") # Spacer
                        if st.button("💾 更新狀態", key=f"btn_upd_{u_key}", use_container_width=True):
                            # Use ISO format for robust date parsing in GAS
                            ts_str_for_api = row['timestamp'].isoformat()
                            
                            with st.spinner("更新中..."):
                                success, msg = drive_integration.update_status(ts_str_for_api, new_status, new_comment)
                                if success:
                                    st.toast("✅ 狀態已更新!", icon="💾")
                                    st.rerun()
                                else:
                                    st.error(f"更新失敗: {msg}")

