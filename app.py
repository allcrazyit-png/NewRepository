import streamlit as st
import pandas as pd
import data_manager
import datetime
import altair as alt
import json
import drive_integration
import streamlit.components.v1 as components
import os
import time

# --- Helper: Image Integrity Check ---
# Helper: Image Integrity Check
# [Fix] Removed cache to prevent false negatives when files are synced
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
    initial_sidebar_state="expanded"
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

    /* --- 5. Segmented Controls (Radio Buttons - Larger) --- */
    .stRadio > label { font-size: 1.5rem !important; color: #86868b !important; margin-bottom: 12px; }
    .stRadio div[role='radiogroup'] {
        background: #1c1c1e;
        padding: 6px;
        border-radius: 14px;
        display: inline-flex;
        gap: 0px;
    }
    .stRadio div[role='radiogroup'] > label { 
        background-color: transparent !important;
        padding: 12px 24px !important;
        border-radius: 10px !important;
        border: none !important;
        color: #86868b !important;
        transition: all 0.2s ease;
        margin: 0 !important;
        box-shadow: none !important;
        font-size: 1.3rem !important; /* Radio Option Text */
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
        font-size: 1.1rem !important; /* Keep Sidebar Checkbox smaller */
    }
    section[data-testid="stSidebar"] div[role='radiogroup'] > label[data-checked='true'] {
        background-color: rgba(10, 132, 255, 0.2) !important; /* Transparent Blue */
        color: #0A84FF !important;
    }

    /* --- 6. Buttons (Apple Blue Pills - Larger) --- */
    div.stButton > button:first-child {
        background-color: #0A84FF !important; /* System Blue */
        color: white !important;
        font-size: 1.4rem !important;
        height: 4.0rem !important;
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
        font-size: 1.2rem !important;
    }
    
    /* --- 6. Scrollbars (Sleek) --- */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #000; }
    ::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #555; }

    /* --- 7. Tab Styling (Larger & Clearer) --- */
    button[data-baseweb="tab"] {
        font-size: 1.5rem !important; /* Larger text ~24px */
        font-weight: 600 !important;
        padding: 16px 32px !important;
        gap: 10px;
        border-radius: 10px !important;
        color: #86868b !important; /* Default Gray */
        background-color: transparent !important;
    }
    button[data-baseweb="tab"]:hover {
        color: #f5f5f7 !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #0A84FF !important; /* Active Blue */
        background-color: rgba(10, 132, 255, 0.1) !important;
        border-bottom: 3px solid #0A84FF !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        padding-bottom: 8px;
    }

    /* ENLARGE INPUTS for Mobile */
    div[data-testid="stNumberInput"] input {
        font-size: 28px !important;
        height: 60px !important;
        padding-top: 10px !important;
        padding-bottom: 10px !important;
    }
    /* Enlarge Metric Labels */
    label[data-testid="stWidgetLabel"] p {
        font-size: 1.3rem !important;
    }
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
# --- Mode Selection ---
# [Refactor]
st.sidebar.title("🔧 巡檢系統")
st.sidebar.caption("v.20250204.39-ui-interaction") # Version Tag
mode = st.sidebar.radio("功能選擇", ["📝 巡檢輸入", "📊 數據戰情室"], index=0)

# --- Sidebar Footer ---
st.sidebar.markdown("---")
if st.sidebar.button("🔄 手動更新數據 (Refresh)", use_container_width=True):
    drive_integration.fetch_history.clear()
    drive_integration.fetch_all_data.clear()
    data_manager.load_data.clear() # Fix: Also clear CSV cache
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

            # [Restored & Moved] Key Control Points (重點管制 1~3+)
            # Moved below Product Image as requested
            kcp_list = []
            
            # 1. Check single column "重點管制"
            val_single = current_part_data.get('重點管制')
            if pd.notna(val_single) and str(val_single).strip():
                kcp_list.append(str(val_single).strip())

            # 2. Check numbered columns "重點管制1" ~ "重點管制3"
            for i in range(1, 6): # Check up to 5 just in case
                col_name = f"重點管制{i}"
                val = current_part_data.get(col_name)
                if pd.notna(val) and str(val).strip():
                    kcp_list.append(str(val).strip())
            
            # 3. Fallback to "重點管理項目"
            if not kcp_list:
                val_legacy = current_part_data.get('重點管理項目')
                if pd.notna(val_legacy) and str(val_legacy).strip():
                    kcp_list.append(str(val_legacy).strip())

            # Display with Softer Color (Blue) as requested
            if kcp_list:
                with st.expander("⭐ 重點管制項目 (Key Control Points)", expanded=False):
                    for item in kcp_list:
                        st.info(f"• {item}")

        # [Refactor] Tabs for Inspection
        tab1, tab2, tab3 = st.tabs(["📝 輸入作業", "🛡️ 該品變化點", "📊 趨勢與履歷"])

        with tab1:
            # [Design] Removed spacer for cleaner/tighter layout "盡量簡單"
            
            # [1] Inputs & Operation
            # [Feature] Work Mode Selector
            mode_cols = st.columns([2, 1])
            with mode_cols[0]:
                 work_mode = st.radio("作業模式", ["📏 標準巡檢 (量測+異常)", "⚡ 僅記錄變化點"], horizontal=True)
            quick_log_mode = (work_mode == "⚡ 僅記錄變化點")
            
            if quick_log_mode:
                st.info("ℹ️ 快速模式：將自動填入標準值，僅需記錄異常。")
                inspection_type = "變更點 (CP)"
            else:
                inspection_type = st.radio("巡檢階段", ["首件", "中件", "末件"], horizontal=True)

            # --- Material Check (Moved to Top) ---
            if not quick_log_mode:
                mat_name = current_part_data.get('原料名稱')
                if pd.isna(mat_name) or str(mat_name).strip() == "":
                    mat_name = current_part_data.get('原料編號', 'N/A')
                
                # Combined Label (No Header)
                material_check = st.radio(f"原料確認 (標準: {mat_name})", ["OK", "NG"], horizontal=True, index=0, key="mat_check_radio")
                
                # Validation Logic handled at Submit
                material_ok = (material_check == "OK")
            else:
                material_ok = True # Auto pass in Quick Mode

            st.divider()

            user_inputs = {}
            # Input Loop
            for idx, sp in enumerate(specs):
                # [UI Polish] Clean Input Layout
                with st.container():
                    # Header for the specific cavity
                    st.markdown(f"#### 🟢 穴號: {sp['suffix'] or '單穴'}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        # Weight Input
                        w_std_val = sp.get('std', '-')
                        w_min = sp.get('min', '-')
                        w_max = sp.get('max', '-')
                        
                        w_label = "重量 (g)"
                        w_help = f"標準: {w_std_val} | 規格: {w_min} ~ {w_max}"
                        
                        # Show spec hint locally
                        st.caption(f"🎯 標準: {w_std_val} | 📏範圍: {w_min} ~ {w_max}")
                        
                        if quick_log_mode:
                             w_input = 0.0
                        else:
                             w_input = st.number_input(
                                w_label,
                                min_value=0.0,
                                max_value=200.0,
                                step=0.01,
                                format="%.2f",
                                key=f"w_in_{idx}",
                                help=w_help
                            )

                    with c2:
                        # Length Input
                        len_std_val = sp.get('len_std')
                        l_label = "長度 (mm)"
                        l_help = "選填欄位"
                        l_caption = "📏 選填"
                        
                        if len_std_val is not None:
                             l_min = sp.get('len_min')
                             l_max = sp.get('len_max')
                             l_help = f"標準: {len_std_val} | 規格: {l_min} ~ {l_max}"
                             l_caption = f"🎯 標準: {len_std_val} | 範圍: {l_min} ~ {l_max}"
                        
                        st.caption(l_caption)
                        
                        if quick_log_mode:
                            l_input = 0.0
                        else:
                            l_input = st.number_input(
                                l_label,
                                min_value=0.0,
                                max_value=500.0,
                                step=0.01,
                                format="%.2f",
                                key=f"l_in_{idx}",
                                help=l_help,
                                value=None
                            )

                    user_inputs[idx] = {'weight': w_input, 'length': l_input}

                    # Validation Msg
                    if w_input > 0:
                         if sp['min'] is not None and sp['max'] is not None:
                             if not (sp['min'] <= w_input <= sp['max']):
                                 st.error(f"⚠️ 重量 NG")
                             else:
                                 st.success("重量 OK")
                    if l_input is not None and l_input > 0:
                          if sp['len_min'] is not None and sp['len_max'] is not None:
                               if not (sp['len_min'] <= l_input <= sp['len_max']):
                                   st.error(f"⚠️ 長度 NG")
                               else:
                                   st.success("長度 OK")
                    
                    st.divider()

            # Material Check (Moved to Top)
            # Placeholder for deleted block

            st.markdown("##### 📝 變化點說明")
            
            # [Design] Simplified to Checkbox
            is_issue = st.checkbox("⚠️ 回報異常 (Report Issue)", value=quick_log_mode)
            
            change_point = ""
            if is_issue:
                change_point = st.text_area("請輸入異常說明", placeholder="例如: 模具損傷、原料更換...", height=100)
                if not change_point.strip():
                    st.caption("⚠️ 請輸入說明，若空白將視為無異常")
            else:
                if not quick_log_mode:
                    st.markdown("<span style='color: #888; font-size: 0.9em;'>✅ 無變化點 (Standard)</span>", unsafe_allow_html=True)

            # Photo Input
            input_method = st.radio("影像輸入", ["📸 網頁相機", "📂 上傳照片"], index=1, horizontal=True)
            img_files = []
            if input_method == "📸 網頁相機":
                cam_file = st.camera_input("拍照")
                if cam_file: img_files = [cam_file]
            else:
                uploaded_files = st.file_uploader("上傳照片", type=["jpg", "png"], accept_multiple_files=True)
                if uploaded_files: img_files = uploaded_files

            # --- Submit Button ---
            submit_btn = st.button("🚀 提交巡檢報告", use_container_width=True)
            
            if submit_btn:
                any_missing_weight = False
                if not quick_log_mode:
                     any_missing_weight = any(user_inputs[i]['weight'] == 0 for i in user_inputs)

                if (any_missing_weight) and not quick_log_mode:
                    st.warning("⚠️ 請填寫所有重量數據 (Quick Mode 可跳過)")
                elif not material_ok:
                    st.error("❌ 原料狀態異常，請復歸後再提交")
                else:
                    with st.spinner("資料上傳中 (Uploading)..."):
                        try:
                            # [Fix] Force Asia/Taipei Time for Upload
                            import pytz
                            tz_tw = pytz.timezone('Asia/Taipei')
                            timestamp_str = datetime.datetime.now(tz_tw).strftime("%Y-%m-%d %H:%M:%S")
                            success_count = 0
                            
                            # Log Logic: One row per spec (L/R)
                            for idx, sp in enumerate(specs):
                                u_in = user_inputs[idx]
                                
                                # Prepare inputs
                                final_weight = u_in['weight']
                                final_len = u_in['length'] if u_in['length'] is not None else ""
                                
                                # Status Determination
                                final_res = "PASS"
                                if quick_log_mode:
                                     final_res = "CP" # Change Point
                                else:
                                     # Weight Check
                                     if sp['min'] is not None and sp['max'] is not None:
                                         if not (sp['min'] <= final_weight <= sp['max']): final_res = "NG"
                                     # Length Check
                                     if sp['len_min'] is not None and sp['len_max'] is not None and final_len != "":
                                         if not (sp['len_min'] <= final_len <= sp['len_max']): final_res = "NG"
                                
                                # CP Status for Manager
                                initial_status = "未審核" if change_point.strip() else "無異常"

                                row_data = {
                                    "timestamp": timestamp_str,
                                    "model": selected_model,
                                    "part_no": f"{selected_part_no}{sp['suffix']}",
                                    "part_name": current_part_data.get('品名', ''),
                                    "inspection_type": inspection_type,
                                    "material_ok": "OK" if material_ok else "NG", # Fix: Key must match GAS expectation
                                    "weight": final_weight,
                                    "width": "", 
                                    "length": final_len,
                                    "result": final_res,
                                    "change_point": change_point if idx == 0 else "", 
                                    "status": initial_status,
                                    "manager_comment": ""
                                }
                                
                                # Fix: Correct argument order for upload_and_append
                                # Signature: (image_file, filename, row_data)
                                current_img = None
                                img_filename = ""
                                
                                if idx == 0 and img_files:
                                    current_img = img_files[0]
                                    # Safe filename: PartNo_Timestamp.jpg
                                    safe_ts = row_data['timestamp'].replace(":", "").replace(" ", "_")
                                    img_filename = f"{row_data['part_no']}_{safe_ts}.jpg"

                                ok = drive_integration.upload_and_append(current_img, img_filename, row_data)
                                if ok: success_count += 1
                                
                            if success_count == len(specs):
                                st.success("✅ 提交成功!")
                                drive_integration.fetch_history.clear()
                                drive_integration.fetch_all_data.clear()
                                time.sleep(1)
                                st.session_state['inspection_started'] = False
                                st.rerun()
                            else:
                                st.error("部份資料上傳失敗，請重試")
                                
                        except Exception as e:
                            st.error(f"系統錯誤: {str(e)}")

        with tab2:
            st.subheader(f"🛡️ {selected_part_no} - 變化點記錄")
            
            # Fetch and Organize History
            target_suffixes = [s['suffix'] for s in specs]
            all_cp_rows = []
            
            for s in specs:
                h_target = f"{selected_part_no}{s['suffix']}"
                h_data = drive_integration.fetch_history(h_target)
                
                # [Debug] Show query status
                # st.caption(f"🔍 Debug: Querying '{h_target}'... Found {len(h_data) if h_data else 0} records")
                
                if h_data:
                    for r in h_data:
                        r['part_no'] = h_target # Ensure key
                        all_cp_rows.append(r)
                        
            if all_cp_rows:
                df_local_cp = pd.DataFrame(all_cp_rows)
                
                # Filter useful CP
                if 'change_point' in df_local_cp.columns:
                    df_local_cp = df_local_cp[df_local_cp['change_point'].ne("") & df_local_cp['change_point'].notna()]
                
                if 'timestamp' in df_local_cp.columns:
                    # [Fix] Force conversion to Taipei Time because GAS returns UTC ISO strings
                    df_local_cp['timestamp'] = pd.to_datetime(df_local_cp['timestamp'], errors='coerce', utc=True).dt.tz_convert('Asia/Taipei')
                    df_local_cp = df_local_cp.sort_values(by='timestamp', ascending=False)
                
                # Split Open / Closed
                if 'status' not in df_local_cp.columns: df_local_cp['status'] = '未審核'
                df_local_cp['status'] = df_local_cp['status'].fillna("未審核")
                
                open_issues = df_local_cp[~df_local_cp['status'].isin(["結案", "Closed", "無異常"])]
                closed_issues = df_local_cp[df_local_cp['status'].isin(["結案", "Closed", "無異常"])]
                
                # 1. Open Issues Section
                if not open_issues.empty:
                    st.error(f"⚠️ 尚有 {len(open_issues)} 筆未結案異常！")
                    
                    # Group by timestamp for display
                    # Use a list of (ts, group_df) sorted by ts descending
                    grouped_open = open_issues.groupby('timestamp', sort=False) 
                    # sort=False because we already sorted df_local_cp
                    
                    for ts, group in grouped_open:
                        cavity_count = len(group)
                        
                        # Find best row (prioritize one with Manager Comment)
                        best_row = group.iloc[0]
                        rows_with_cmt = group[group['manager_comment'].astype(str).str.strip() != ""]
                        if not rows_with_cmt.empty:
                            best_row = rows_with_cmt.iloc[0]

                        row = best_row
                        stat = row.get('status', '未審核')
                        s_icon = "🔴" if stat == "未審核" else "🟡"
                        ts_str = row['timestamp'].strftime('%Y-%m-%d %H:%M') if pd.notna(row['timestamp']) else "N/A"
                        
                        part_display = row.get('part_no')
                        if cavity_count > 1:
                            part_display = f"{str(part_display).split('_')[0]} (共{cavity_count}穴)"

                        st.markdown(f"#### {s_icon} [{stat}] {row.get('change_point')}")
                        st.caption(f"📅 {ts_str} | Part: {part_display}")
                        
                        # Manager Comment
                        mgr_cmt = row.get('manager_comment')
                        if pd.notna(mgr_cmt) and str(mgr_cmt).strip():
                            st.info(f"👨‍💼 主管: {str(mgr_cmt).strip()}")
                        st.divider()
                else:
                    st.success("✅ 目前無未結案異常")

                # 2. History Section
                st.subheader("📜 歷史記錄 (已結案)")
                if not closed_issues.empty:
                    with st.expander("查看已結案記錄", expanded=False):
                        grouped_closed = closed_issues.groupby('timestamp', sort=False)
                        for ts, group in grouped_closed:
                            row = group.iloc[0]
                            cavity_count = len(group)
                            
                            stat = row.get('status', '結案')
                            ts_str = row['timestamp'].strftime('%Y-%m-%d') if pd.notna(row['timestamp']) else "N/A"
                            
                            part_display = row.get('part_no')
                            if cavity_count > 1:
                                part_display = f"{str(part_display).split('_')[0]} (共{cavity_count}穴)"
                                
                            st.markdown(f"🟢 **{row.get('change_point')}**")
                            st.caption(f"[{stat}] {ts_str} | {part_display}")
                            
                            mgr_cmt = row.get('manager_comment')
                            if pd.notna(mgr_cmt) and str(mgr_cmt).strip():
                                st.caption(f"👨‍💼 主管: {str(mgr_cmt).strip()}")
                                
                            st.divider()
                else:
                    st.caption("無已結案記錄")
            else:
                st.info("此產品目前無相關變化點記錄。")

        with tab3:
            st.subheader(f"📊 {selected_part_no} - 趨勢與履歷")
            
            # [Trend Chart Logic]
            chart_cols = st.columns(len(specs))
            
            for idx, sp in enumerate(specs):
                with chart_cols[idx]:
                    chart_title = f"{selected_part_no}{sp['label']}"
                    suffix = sp['suffix']
                    history_target_no = f"{selected_part_no}{suffix}"
                    
                    st.markdown(f"**{chart_title}**")
                    
                    # Fetch
                    history_data = drive_integration.fetch_history(history_target_no)
                    
                    # [Debug] Check data
                    valid_chart_data = False
                    if history_data:
                        chart_df = pd.DataFrame(history_data)
                        
                        # Data Cleaning
                        if 'weight' in chart_df.columns and 'timestamp' in chart_df.columns:
                            chart_df['weight'] = pd.to_numeric(chart_df['weight'], errors='coerce')
                            chart_df['timestamp'] = pd.to_datetime(chart_df['timestamp'], errors='coerce')
                            chart_df = chart_df.dropna(subset=['weight', 'timestamp'])
                            
                            # Filter: Only show real measurements (>0)
                            chart_df = chart_df[chart_df['weight'] > 0]
                            
                            if not chart_df.empty:
                                valid_chart_data = True
                                
                                # Add Limits
                                w_max_limit = sp['max']
                                w_min_limit = sp['min']
                                y_cols = ['weight']
                                if w_max_limit is not None:
                                    chart_df['Limit H'] = float(w_max_limit)
                                    y_cols.append('Limit H')
                                if w_min_limit is not None:
                                    chart_df['Limit L'] = float(w_min_limit)
                                    y_cols.append('Limit L')
                                
                                # Convert to Local Time for Display
                                if chart_df['timestamp'].dt.tz is None:
                                     chart_df['timestamp'] = chart_df['timestamp'].dt.tz_localize('UTC')
                                chart_df['timestamp'] = chart_df['timestamp'].dt.tz_convert('Asia/Taipei')

                                chart_long = chart_df.melt('timestamp', value_vars=y_cols, var_name='MetricType', value_name='Value')
                                
                                # Scaling
                                y_min_val = chart_long['Value'].min()
                                y_max_val = chart_long['Value'].max()
                                padding = (y_max_val - y_min_val) * 0.2 if y_max_val != y_min_val else 1.0
                                
                                color_domain = ['Limit H', 'Limit L', 'weight']
                                color_range = ['#FF6C6C', '#FF6C6C', '#457B9D'] 
                                
                                base = alt.Chart(chart_long).encode(
                                    x=alt.X('timestamp', title=None, axis=alt.Axis(format='%m/%d', ticks=False)),
                                    y=alt.Y('Value', title='g', scale=alt.Scale(domain=[y_min_val - padding, y_max_val + padding])),
                                    color=alt.Color('MetricType', legend=None, scale=alt.Scale(domain=color_domain, range=color_range)),
                                    tooltip=['timestamp', 'Value', 'MetricType']
                                )
                                
                                line_w = base.transform_filter(alt.datum.MetricType == 'weight').mark_line(strokeWidth=3, point=True)
                                line_limits = base.transform_filter((alt.datum.MetricType == 'Limit H') | (alt.datum.MetricType == 'Limit L')).mark_line(strokeDash=[5, 5], opacity=0.8)

                                st.altair_chart((line_w + line_limits).interactive(), use_container_width=True)
                    
                    if not valid_chart_data:
                         st.info("尚無有效量測數據 (僅顯示重量 > 0 之記錄)")
            
            st.divider()
            
            # [Defect Images Logic]
            st.subheader("⚠️ 過去異常履歷 (Reference)")
            defect_images = []
            d1 = current_part_data.get('異常履歷寫真')
            if pd.notna(d1) and str(d1).strip(): defect_images.append(("1", str(d1).strip()))
            for i in range(2, 4):
                col = f"異常履歷寫真{i}"
                val = current_part_data.get(col)
                if pd.notna(val) and str(val).strip():
                    defect_images.append((str(i), str(val).strip()))

            if defect_images:
                dh_cols = st.columns(5)
                for idx, (label, fname) in enumerate(defect_images):
                    col_idx = idx % 5
                    img_path = os.path.join("quality_images", fname)
                    valid_img_path = check_image_availability(img_path)
                    
                    with dh_cols[col_idx]:
                        if valid_img_path:
                            st.image(valid_img_path, caption=f"履歷-{label}", use_container_width=True)
                        else:
                            st.caption(f"履歷{label} 讀取失敗")
            else:
                st.caption("無異常履歷照片")


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
        if 'status' not in df_dash.columns: df_dash['status'] = "未審核"
        if 'manager_comment' not in df_dash.columns: df_dash['manager_comment'] = ""
        df_dash['status'] = df_dash['status'].fillna("未審核")
        df_dash['manager_comment'] = df_dash['manager_comment'].fillna("")
        if 'change_point' not in df_dash.columns: df_dash['change_point'] = ""

        # ==========================================
        # 1. Weight Trend Tracking
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
                 
                 # [Fix] Decoupled State for Interaction
                 if 'dash_target_part' not in st.session_state:
                     st.session_state['dash_target_part'] = "全部"
                 
                 # Calculate Index
                 current_target = st.session_state['dash_target_part']
                 try:
                     f_index = parts_dash.index(current_target)
                 except ValueError:
                     f_index = 0
                 
                 # Render Widget with UI Key
                 filter_part_ui = st.selectbox("篩選品番", parts_dash, index=f_index, key="_dash_part_ui")
                 
                 # Sync UI -> State
                 if filter_part_ui != st.session_state['dash_target_part']:
                     st.session_state['dash_target_part'] = filter_part_ui
                     st.rerun()
                 
                 filter_part = filter_part_ui # Local var for legacy use below
                 
                 # Show small product image if filtered
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
            
            # [Filter] Hide Change Point records (Pure CP has weight=0)
            # [Refactor] Don't filter global view, only filter for Chart
            if 'weight' in df_view.columns:
                 df_view['weight'] = pd.to_numeric(df_view['weight'], errors='coerce')
                 # df_view = df_view[df_view['weight'] > 0] <--- Removed to show CP in Table
            
            # [Double Check] Explicitly hide 'CP' result if any leaked
            if 'result' in df_view.columns:
                 df_view = df_view[df_view['result'] != 'CP']
                 
            # Sort by Newest
            if 'timestamp' in df_view.columns:
                 df_view = df_view.sort_values(by='timestamp', ascending=False)
            
            # Process Image Links
            if 'image' in df_view.columns:
                def make_drive_link(val):
                    val_str = str(val).strip().replace('"', '').replace("'", "")
                    if not val_str or val_str.lower() == 'nan': return None
                    if val_str.startswith('http'): return val_str
                    return f"https://drive.google.com/file/d/{val_str}/preview"
                df_view['image'] = df_view['image'].apply(make_drive_link)

            # [View] Revert to showing all columns (User Request)
            # [View] Interactive Table with Click-to-Filter
            event = st.dataframe(
                df_view, 
                use_container_width=True,
                column_config={
                    "image": st.column_config.LinkColumn("巡檢照片", display_text="📸 查看"),
                    "timestamp": st.column_config.DatetimeColumn("時間", format="MM/DD HH:mm"),
                    "weight": st.column_config.NumberColumn("重量 (g)", format="%.2f")
                },
                on_select="rerun",
                selection_mode="single-row"
            )
            
            # [Interaction] Click Row to Filter Part
            # [Interaction] Click Row to Filter Part
            if len(event.selection.rows) > 0:
                s_idx = event.selection.rows[0]
                target_p = df_view.iloc[s_idx]['part_no']
                
                # Update Source of Truth
                if target_p != st.session_state.get('dash_target_part'):
                     st.session_state['dash_target_part'] = target_p
                     st.toast(f"🔍 已篩選: {target_p}")
                     st.rerun()
            
            if not df_view.empty:
                st.subheader("📈 重量趨勢圖")
                
                # [Fix] Hide Chart if "All" is selected
                current_filter = st.session_state.get('dash_target_part', '全部')
                if current_filter == "全部":
                    st.info("👈 請在左側選單選擇單一品番，或在下方表格點選，以查看趨勢圖。")
                    chart_df = pd.DataFrame()
                else:
                    chart_df = df_view.copy() 
                    # Filter for Chart Only (Hide 0 weight)
                    if 'weight' in chart_df.columns:
                        chart_df = chart_df[chart_df['weight'] > 0]
                
                if not chart_df.empty:
                    y_cols = ['weight']
                    if filter_part != "全部":
                        # [Fix] Fuzzy Match for Suffixes (e.g., Part_1, Part_2)
                        part_spec = df[df['品番'] == filter_part]
                        if part_spec.empty:
                            if '_' in filter_part:
                                base_part_underscore = filter_part.rsplit('_', 1)[0]
                                part_spec = df[df['品番'] == base_part_underscore]
                        if part_spec.empty:
                             base_part_space = filter_part.split(' ')[0]
                             part_spec = df[df['品番'] == base_part_space]
                        
                        if not part_spec.empty:
                            spec_row = part_spec.iloc[0]
                            limit_h = spec_row.get('clean_重量上限')
                            limit_l = spec_row.get('clean_重量下限')
                            if isinstance(limit_h, list): limit_h = limit_h[0]
                            if isinstance(limit_l, list): limit_l = limit_l[0]
                            if limit_h is not None:
                                chart_df['Limit H'] = float(limit_h)
                                y_cols.append('Limit H')
                            if limit_l is not None:
                                 chart_df['Limit L'] = float(limit_l)
                                 y_cols.append('Limit L')

                    chart_long = chart_df.melt('timestamp', value_vars=y_cols, var_name='MetricType', value_name='Value')
                    y_min_val = chart_long['Value'].min(); y_max_val = chart_long['Value'].max()
                    padding = (y_max_val - y_min_val) * 0.1 if y_max_val != y_min_val else 5
                    
                    color_domain = ['Limit H', 'Limit L', 'weight']
                    color_range = ['#FF6C6C', '#FF6C6C', '#457B9D'] 
                    
                    base = alt.Chart(chart_long).encode(
                        x=alt.X('timestamp', title='時間', axis=alt.Axis(format='%m/%d %H:%M')),
                        y=alt.Y('Value', title='重量 (g)', scale=alt.Scale(domain=[y_min_val - padding, y_max_val + padding])),
                        color=alt.Color('MetricType', legend=None, scale=alt.Scale(domain=color_domain, range=color_range)),
                        tooltip=['timestamp', 'Value', 'MetricType']
                    )
                    
                    line_w = base.transform_filter(alt.datum.MetricType == 'weight').mark_line(point=True)
                    line_limits = base.transform_filter((alt.datum.MetricType == 'Limit H') | (alt.datum.MetricType == 'Limit L')).mark_line(strokeDash=[5, 5], opacity=0.8)
                    
                    st.altair_chart((line_w + line_limits).interactive(), use_container_width=True)
                else:
                    if filter_part != "全部":
                        st.info(f"ℹ️ 產品 [{filter_part}] 目前無「重量數據」。(記錄可能均為快速模式/CP，重量=0)")
                    else:
                        st.write("") # Should be covered above, but safe fallback
        
        # [Legacy/Duplicate Code Removed]
        # Previous versions had a fallback block here that caused "Change Point Board" to appear twice.
        # It has been deleted.

        # ==========================================
        # 2. Change Point Management Center
        # ==========================================
        elif dash_page == "🛡️ 變化點管理中心":
            st.subheader("🛡️ 變化點管理中心")
            
            # Filter Logic
            df_cp = df_dash[df_dash['change_point'].ne("") & df_dash['change_point'].notna()].copy()
            df_cp = df_cp.sort_values(by='timestamp', ascending=False)
            
            # --- Filters ---
            st.markdown("##### 🔍 篩選條件")
            f_col1, f_col2, f_col3, f_col4 = st.columns(4)
            with f_col1:
                today = datetime.date.today()
                start_date = st.date_input("開始日期", today - datetime.timedelta(days=30))
                end_date = st.date_input("結束日期", today)
            with f_col2:
                models_cp = ["全部"] + list(df_cp['model'].unique())
                filter_cp_model = st.selectbox("車型 (Model)", models_cp, key="cp_model_filter")
            with f_col3:
                if filter_cp_model != "全部":
                    parts_cp = ["全部"] + list(df_cp[df_cp['model'] == filter_cp_model]['part_no'].unique())
                else:
                    parts_cp = ["全部"] + list(df_cp['part_no'].unique())
                # [Fix] Added key for dashboard interaction
                filter_cp_part = st.selectbox("品番 (Part No)", parts_cp, key="cp_part_filter")
            with f_col4:
                status_opts = ["未審核", "審核中", "結案", "Closed", "無異常"]
                filter_cp_status = st.multiselect("狀態 (Status)", status_opts, default=["未審核", "審核中"])

            # Apply Filters
            if 'timestamp' in df_cp.columns:
                 df_cp['date'] = df_cp['timestamp'].dt.date
                 df_cp = df_cp[(df_cp['date'] >= start_date) & (df_cp['date'] <= end_date)]
            if filter_cp_model != "全部": df_cp = df_cp[df_cp['model'] == filter_cp_model]
            if filter_cp_part != "全部": df_cp = df_cp[df_cp['part_no'] == filter_cp_part]
            if filter_cp_status: df_cp = df_cp[df_cp['status'].isin(filter_cp_status)]
            else:
                st.warning("請選擇至少一種狀態")
                df_cp = df_cp.iloc[0:0] 
            
            # [Feature] Group by Timestamp (Deduplicate Multi-Cavity)
            # If multiple rows have same timestamp, show only one representative
            if not df_cp.empty:
                # Identify duplicates
                dup_counts = df_cp.groupby('timestamp').size()
                
                # Create a display copy, keeping only the first occurrence per timestamp
                df_display = df_cp.drop_duplicates(subset=['timestamp']).copy()
                
                st.info(f"共發現 {len(df_display)} 筆異常事件 (已合併多穴資料)")
            else:
                df_display = df_cp # Empty
            
            for index, row in df_display.iterrows():
                # Check if this is a multi-cavity group
                ts_key = row['timestamp']
                is_multi = False
                cavity_count = 1
                if ts_key in dup_counts:
                    cavity_count = dup_counts[ts_key]
                    if cavity_count > 1: is_multi = True
                
                stat_color = "red"; stat_icon = "🔴"
                if row['status'] == "審核中": stat_color = "orange"; stat_icon = "🟡"
                elif row['status'] in ["結案", "Closed", "無異常"]: stat_color = "green"; stat_icon = "🟢"
                
                # Display Title
                part_display = row['part_no']
                if is_multi:
                    part_display = f"{row['part_no'].split('_')[0]} (共{cavity_count}穴)"
                
                with st.expander(f"{stat_icon} :{stat_color}[{row['status']}] {row['timestamp'].strftime('%Y-%m-%d %H:%M')} - {row['model']} {part_display}", expanded=True):
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.markdown(f"**變化點內容:**")
                        st.error(row['change_point'])
                        st.caption(f"巡檢結果: {row['result']}")
                    with c2:
                        prod_img_path = f"quality_images/{row['part_no']}_main.jpg"
                        if check_image_availability(prod_img_path): st.image(prod_img_path, width=120, caption="產品示意圖")
                        
                        raw_img = str(row.get('image', '')).strip().replace('"', '').replace("'", "")
                        if raw_img and raw_img.lower() != "nan":
                             if raw_img.startswith("http"): img_url = raw_img
                             else: img_url = f"https://drive.google.com/file/d/{raw_img}/preview"
                             st.markdown(f"📸 [查看巡檢照片]({img_url})")
                    
                    st.divider()
                    
                    # Manager Actions
                    m_col1, m_col2, m_col3 = st.columns([1, 2, 1])
                    u_key = f"{row['timestamp']}_{row['part_no']}"
                    
                    with m_col1:
                        current_stat = row.get('status', '未審核')
                        if not current_stat: current_stat = '未審核'
                        target_index = 0
                        opts = ["未審核", "審核中", "結案", "無異常"]
                        if current_stat in opts: target_index = opts.index(current_stat)
                        new_status = st.selectbox("審核狀態", opts, index=target_index, key=f"stat_{u_key}")
                    
                    with m_col2:
                         # [Feature] Change Point Description (Editable)
                         current_cp_desc = row.get('change_point', '')
                         if pd.isna(current_cp_desc): current_cp_desc = ""
                         new_cp_desc = st.text_input("異常內容 / 變化點", value=str(current_cp_desc), key=f"cp_{u_key}")

                         # [Feature] Manager Comment
                         current_comment = row.get('manager_comment', '')
                         if pd.isna(current_comment): current_comment = ""
                         new_comment = st.text_area("👨‍💼 主管留言 / 處理對策", value=str(current_comment), height=100, key=f"comm_{u_key}")
                         
                         # [Feature] Batch Update Checkbox
                         batch_label = "同步更新同批次 (一模多穴)"
                         if is_multi: batch_label += f" [偵測到 {cavity_count} 筆關聯資料]"
                         
                         apply_batch = st.checkbox(batch_label, value=True, key=f"batch_{u_key}")
                    
                    with m_col3:
                        st.write("") 
                        if st.button("💾 更新", key=f"btn_upd_{u_key}", use_container_width=True):
                            # [Fix] Use simple String format "YYYY-MM-DD HH:MM:SS" to match Sheet display / GAS formatting
                            ts_str_for_api = row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                            target_part = row['part_no']
                            with st.spinner("更新中..."):
                                success, msg = drive_integration.update_status_v2(
                                    ts_str_for_api, 
                                    new_status, 
                                    new_comment, 
                                    target_part, 
                                    apply_batch,
                                    new_cp_desc # Pass new Change Point content
                                )
                                if success:
                                    st.success("更新成功!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"更新失敗: {msg}")
