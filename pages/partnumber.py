pages/partnumber.py

import streamlit as st import pandas as pd import base64 import os

--- CẤU HÌNH ---

st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1 - Tra Cứu PN", layout="wide", initial_sidebar_state="collapsed")

--- HÀM HỖ TRỢ ---

def get_base64_encoded_file(file_path): """Mã hóa file ảnh sang base64.""" path_to_check = file_path if "pages/" not in path_to_check: if not os.path.exists(path_to_check): path_to_check = os.path.join(os.path.dirname(file), file_path) if not os.path.exists(path_to_check) or os.path.getsize(path_to_check) == 0: return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=" try: with open(path_to_check, "rb") as f: return base64.b64encode(f.read()).decode("utf-8") except Exception: return "iVBORw0KGgoAAAANHHEAAAABJRU5ErkJggg=="

@st.cache_data(show_spinner="Đang tải dữ liệu...") def load_and_clean(excel_file, sheet): try: excel_path = os.path.join(os.path.dirname(file), excel_file.replace("pages/", "")) df = pd.read_excel(excel_path, sheet_name=sheet) df.columns = df.columns.str.strip().str.upper() df = df.replace(r'^\s*$', pd.NA, regex=True).dropna(how="all") for col in df.columns: if df[col].dtype == "object": df[col] = df[col].fillna("").astype(str).str.strip() if col in ["A/C", "DESCRIPTION", "ITEM", "PART NUMBER"] and df[col].eq("").all(): return pd.DataFrame() return df except Exception: return pd.DataFrame()

--- BIẾN VÀ FILE ---

CHOOSE_PROMPT = "-- CHỌN --" excel_file = "pages/A787.xlsx"

try: pn_bg_pc_base64 = get_base64_encoded_file("pages/PN_PC.jpg") pn_bg_mobile_base64 = get_base64_encoded_file("pages/PN_mobile.jpg") except: st.error("❌ Lỗi khi đọc ảnh nền") st.stop()

--- CSS ---

hide_streamlit_style = f"""

<style>
#MainMenu, footer, header {{visibility: hidden;}}

.stApp {{
    background: url("data:image/jpeg;base64,{pn_bg_pc_base64}") no-repeat center top fixed !important;
    background-size: cover !important;
}}

.main > div:first-child {{ padding-top: 350px !important; }}

@media (max-width: 768px) {{
    .stApp {{
        background: url("data:image/jpeg;base64,{pn_bg_mobile_base64}") no-repeat center top scroll !important;
        background-size: cover !important;
    }}
    .main > div:first-child {{ padding-top: 200px !important; }}
}}

/* --- TIÊU ĐỀ CHẠY --- */
#main-title-container {{
    position: fixed;
    top: 5vh;
    left: 0;
    width: 100%;
    height: 10vh;
    overflow: hidden;
    z-index: 20;
}}

#main-title-container h1 {{
    font-size: 3.5vw;
    margin: 0;
    font-weight: 900;
    white-space: nowrap;
    animation: scrollText 15s linear infinite;
}}

@keyframes scrollText {{
    0% {{ transform: translate(100vw, 0); }}
    100% {{ transform: translate(-100%, 0); }}
}}

/* --- TIÊU ĐỀ PHỤ (ĐÃ HẠ THẤP HƠN) --- */
#sub-static-title {{
    position: static;
    margin-top: 220px; /* ⬅⬅⬅ TĂNG LÊN ĐỂ TIÊU ĐỀ XUỐNG THẤP */
    margin-bottom: 30px;
    text-align: center;
}}

#sub-static-title h2 {{
    font-size: 2rem;
    color: #FFEA00;
    text-shadow: 0 0 15px #FFEA00;
}}
</style>"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

--- NÚT HOME ---

st.markdown("""

<div id="back-to-home-btn-container" style="position: fixed; top: 15px; left: 15px; z-index:1000;">
    <a id="manual-home-btn" href="/?skip_intro=1" target="_self" style="background:black; color:#FFEA00; padding:10px 20px; border-radius:8px; border:2px solid #FFEA00; text-decoration:none; font-weight:bold;">🏠 Về Trang Chủ</a>
</div>
""", unsafe_allow_html=True)--- TIÊU ĐỀ CHẠY ---

st.markdown('<div id="main-title-container"><h1>Tổ Bảo Dưỡng Số 1</h1></div>', unsafe_allow_html=True)

--- TIÊU ĐỀ PHỤ (ĐÃ HẠ THẤP) ---

st.markdown('<div id="sub-static-title"><h2>TRA CỨU PART NUMBER</h2></div>', unsafe_allow_html=True)

--- DROPDOWN ---

try: excel_path = os.path.join(os.path.dirname(file), excel_file.replace("pages/", "")) sheet_names = pd.ExcelFile(excel_path).sheet_names except: st.error("❌ Không đọc được file Excel!") st.stop()

sheet_options = [CHOOSE_PROMPT] + sheet_names

col1, col2, col3, col4 = st.columns(4) df_base = pd.DataFrame() df_filtered = pd.DataFrame() aircraft = CHOOSE_PROMPT desc = CHOOSE_PROMPT item = CHOOSE_PROMPT

with col1: zone = st.selectbox("📂 Zone", sheet_options) zone_selected = zone != CHOOSE_PROMPT

if zone_selected: df_base = load_and_clean(excel_file, zone) df_filtered = df_base.copy()

ac_exists = "A/C" in df_base.columns if zone_selected and ac_exists: aircraft_options = [CHOOSE_PROMPT] + sorted(df_base["A/C"].unique().tolist()) with col2: aircraft = st.selectbox("✈️ Loại máy bay", aircraft_options) if aircraft != CHOOSE_PROMPT: df_filtered = df_filtered[df_filtered["A/C"] == aircraft] else: aircraft = CHOOSE_PROMPT

if "DESCRIPTION" in df_filtered.columns: desc_options = [CHOOSE_PROMPT] + sorted(df_filtered["DESCRIPTION"].unique().tolist()) with col3: desc = st.selectbox("🔑 Mô tả chi tiết", desc_options) if desc != CHOOSE_PROMPT: df_filtered = df_filtered[df_filtered["DESCRIPTION"] == desc]

if "ITEM" in df_filtered.columns: item_options = [CHOOSE_PROMPT] + sorted(df_filtered["ITEM"].unique().tolist()) with col4: item = st.selectbox("🔌 Item", item_options) if item != CHOOSE_PROMPT: df_filtered = df_filtered[df_filtered["ITEM"] == item]

st.markdown("---")

--- KẾT QUẢ ---

if len(df_filtered) > 0: st.markdown('<h3 style="text-align:center; color:#FFEA00; text-shadow:0 0 15px #FFEA00;">KẾT QUẢ TRA CỨU</h3>', unsafe_allow_html=True)

df_display = df_filtered.copy().reset_index(drop=True)
df_display.insert(0, "STT", range(1, len(df_display)+1))

st.dataframe(df_display, use_container_width=True)

else: st.info("💡 Vui lòng chọn đủ thông tin để hiển thị kết quả.")
