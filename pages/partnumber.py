# pages/partnumber.py

import streamlit as st
import pandas as pd
import base64
import os

# --- CẤU HÌNH ---
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1 - Tra Cứu PN", layout="wide", initial_sidebar_state="collapsed")

# --- HÀM HỖ TRỢ ---
def get_base64_encoded_file(file_path):
    """Mã hóa file ảnh sang base64."""
    path_to_check = file_path
    if "pages/" not in path_to_check:
        if not os.path.exists(path_to_check):
            path_to_check = os.path.join(os.path.dirname(__file__), file_path)
    
    if not os.path.exists(path_to_check) or os.path.getsize(path_to_check) == 0:
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    try:
        with open(path_to_check, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return "iVBORw0KGgoAAAANHHEAAAABJRU5ErkJggg=="

@st.cache_data(show_spinner="Đang tải dữ liệu...")
def load_and_clean(excel_file, sheet):
    """Tải và làm sạch dữ liệu từ sheet Excel."""
    try:
        excel_path = os.path.join(os.path.dirname(__file__), excel_file.replace("pages/", ""))
        df = pd.read_excel(excel_path, sheet_name=sheet)
        df.columns = df.columns.str.strip().str.upper()
        df = df.replace(r'^\s*$', pd.NA, regex=True).dropna(how="all")
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].fillna("").astype(str).str.strip()
            if col in ["A/C", "DESCRIPTION", "ITEM", "PART NUMBER"] and df[col].eq("").all():
                return pd.DataFrame()
        return df
    except Exception as e:
        return pd.DataFrame()

# --- BIẾN VÀ ĐƯỜNG DẪN ---
CHOOSE_PROMPT = "-- CHỌN --"
excel_file = "pages/A787.xlsx"

try:
    pn_bg_pc_base64    = get_base64_encoded_file("pages/PC.jpg")
    pn_bg_mobile_base64 = get_base64_encoded_file("pages/mobile.jpg")
    logo_base64        = get_base64_encoded_file("pages/logo.jpg")
except Exception as e:
    st.error(f"❌ Lỗi khi đọc file ảnh: {str(e)}")
    st.stop()

# --- CSS ---
hide_streamlit_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;700&display=swap');
#MainMenu, footer, header {{visibility: hidden;}}

.main {{
    padding: 0;
    margin: 0;
    background-color: transparent !important;
    z-index: 10 !important;
}}

.stApp {{
    background-color: #1a1a2e !important;
    font-family: 'Oswald', sans-serif !important;
}}

/* Banner nền PC - full width, height 120px cố định */
#banner-pc {{
    display: block;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 120px;
    background: url("data:image/jpeg;base64,{pn_bg_pc_base64}") no-repeat center center;
    background-size: cover;
    z-index: 100;
}}

/* Banner nền mobile */
@media (max-width: 768px) {{
    #banner-pc {{
        background: url("data:image/jpeg;base64,{pn_bg_mobile_base64}") no-repeat center center;
        background-size: cover;
        height: 120px;
    }}
}}

/* Logo căn giữa bên dưới banner */
#logo-container {{
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 130px;
    margin-bottom: 10px;
    z-index: 90;
}}

#logo-container img {{
    max-height: 120px;
    max-width: 80%;
    object-fit: contain;
    filter: drop-shadow(0 4px 12px rgba(0,0,0,0.6));
}}

/* Đẩy nội dung chính xuống dưới banner + logo */
.main > div:first-child {{
    padding-top: 10px !important;
    padding-left: 20px;
    padding-right: 20px;
}}

/* ✅ TIÊU ĐỀ PHỤ TĨNH */
#sub-static-title {{
    position: static;
    margin-top: 10px;
    margin-bottom: 30px;
    z-index: 90;
    background: transparent !important;
    text-align: center;
}}

#sub-static-title h2 {{
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    color: #FFEA00;
    text-align: center;
    text-shadow: 0 0 15px #FFEA00, 0 0 30px rgba(255,234,0,0.8);
    margin-bottom: 20px;
}}

.result-title h3 {{
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    color: #FFEA00;
    text-align: center;
    text-shadow: 0 0 15px #FFEA00, 0 0 30px rgba(255,234,0,0.8);
    margin-bottom: 20px;
}}

@media (max-width: 768px) {{
    #sub-static-title h2, .result-title h3 {{
        font-size: 1.2rem;
        white-space: nowrap;
    }}
}}

/* --- CSS CHO DROPDOWN & BẢNG KẾT QUẢ --- */
div.stSelectbox label p, div[data-testid*="column"] label p {{
    color: #00FF00 !important;
    font-size: 1.25rem !important;
    font-weight: bold;
    text-shadow: 0 0 5px rgba(0,255,0,0.5);
}}

.stSelectbox div[data-baseweb="select"] {{
    background-color: rgba(0, 0, 0, 0.7);
    border: 1px solid #00FF00;
    border-radius: 8px;
}}

.stSelectbox div[data-baseweb="select"] div[data-testid="stTextInput"] {{
    color: #FFFFFF !important;
}}

.custom-table th {{
    background-color: #1E8449 !important;
    color: #FFFFFF !important;
    padding: 14px;
    border: 2px solid #2ECC71;
    font-size: 1.1rem;
    font-weight: bold;
    text-align: center !important;
    font-family: 'Oswald', sans-serif;
}}

.custom-table td {{
    padding: 12px;
    text-align: center !important;
    border: 1px solid #333333;
    vertical-align: middle;
    font-size: 1rem;
    color: #000000;
    background-color: #FFFFFF !important;
    font-family: Arial, sans-serif;
}}

.table-container {{
    display: flex;
    justify-content: flex-start;
    width: 100%;
    margin-top: 20px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    padding-bottom: 15px;
}}

.custom-table {{
    min-width: 100%;
    width: max-content;
    margin: 0;
    border-collapse: collapse;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
}}

</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- BANNER NỀN CỐ ĐỊNH ---
st.markdown('<div id="banner-pc"></div>', unsafe_allow_html=True)

# --- LOGO Ở GIỮA, PHÍA TRÊN ---
st.markdown(
    f'<div id="logo-container"><img src="data:image/jpeg;base64,{logo_base64}" alt="Logo"></div>',
    unsafe_allow_html=True
)

# --- TIÊU ĐỀ PHỤ ---
st.markdown('<div id="sub-static-title"><h2>TRA CỨU PART NUMBER</h2></div>', unsafe_allow_html=True)

# --- DROPDOWN & XỬ LÝ DỮ LIỆU ---
try:
    if not os.path.exists(excel_file):
        st.error(f"❌ Không tìm thấy file Excel: {excel_file}")
        st.stop()

    excel_path = os.path.join(os.path.dirname(__file__), excel_file.replace("pages/", ""))
    sheet_names = pd.ExcelFile(excel_path).sheet_names
except Exception as e:
    st.error(f"❌ Lỗi khi đọc file Excel: {str(e)}")
    st.stop()

sheet_options = [CHOOSE_PROMPT] + sheet_names

st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
df_base = pd.DataFrame()
df_filtered = pd.DataFrame()
aircraft = CHOOSE_PROMPT
desc = CHOOSE_PROMPT
item = CHOOSE_PROMPT

with col1:
    zone = st.selectbox("📂 Zone", sheet_options, key="zone_select")
zone_selected = (zone and zone != CHOOSE_PROMPT)
if zone_selected:
    df_base = load_and_clean(excel_file, zone)
    df_filtered = df_base.copy()

ac_exists = "A/C" in df_base.columns
aircraft_selected = False
if zone_selected and ac_exists:
    aircraft_options = [CHOOSE_PROMPT] + sorted(df_base["A/C"].dropna().unique().tolist())
    with col2:
        aircraft = st.selectbox("✈️ Loại máy bay", aircraft_options, key="aircraft_select")
    aircraft_selected = (aircraft and aircraft != CHOOSE_PROMPT)
    if aircraft_selected:
        df_filtered = df_base[df_base["A/C"] == aircraft].copy()
elif zone_selected:
    aircraft_selected = True
    df_filtered = df_base.copy()

desc_exists = "DESCRIPTION" in df_filtered.columns
desc_selected = False
if aircraft_selected and zone_selected and desc_exists:
    descs_options = [CHOOSE_PROMPT] + sorted(df_filtered["DESCRIPTION"].dropna().unique().tolist())
    with col3:
        desc = st.selectbox("🔑 Mô tả chi tiết", descs_options, key="desc_select")
    desc_selected = (desc and desc != CHOOSE_PROMPT)
    if desc_selected:
        df_filtered = df_filtered[df_filtered["DESCRIPTION"] == desc].copy()

item_exists = "ITEM" in df_filtered.columns
item_selected = False
if (aircraft_selected and zone_selected) and item_exists and (desc_selected or not desc_exists):
    items_options = [CHOOSE_PROMPT] + sorted(df_filtered["ITEM"].dropna().unique().tolist())
    with col4:
        item = st.selectbox("🔌 Item", items_options, key="item_select")
    item_selected = (item and item != CHOOSE_PROMPT)
    if item_selected:
        df_filtered = df_filtered[df_filtered["ITEM"] == item].copy()

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("---")

# --- HIỂN THỊ KẾT QUẢ ---
all_criteria_met = zone_selected and aircraft_selected and (desc_selected or not desc_exists) and (item_selected or not item_exists)

if zone_selected:
    if all_criteria_met:
        df_display = df_filtered.copy()

        if "DESCRIPTION" in df_display.columns:
            df_display = df_display.drop(columns=["DESCRIPTION"])
        if "ITEM" in df_display.columns:
            df_display = df_display.drop(columns=["ITEM"])
        if "A/C" in df_display.columns:
            df_display = df_display.drop(columns=["A/C"])

        if len(df_display) > 0:
            st.markdown('<div class="result-title"><h3>KẾT QUẢ TRA CỨU</h3></div>', unsafe_allow_html=True)

            df_display = df_display.reset_index(drop=True)
            df_display.insert(0, "STT", range(1, len(df_display) + 1))

            if "PART NUMBER" in df_display.columns:
                pn_col = df_display.pop("PART NUMBER")
                df_display.insert(1, "PART NUMBER", pn_col)

            html_parts = ['<div class="table-container">']
            html_parts.append('<table class="custom-table">')

            html_parts.append('<thead><tr>')
            for col in df_display.columns:
                html_parts.append(f'<th>{str(col)}</th>')
            html_parts.append('</tr></thead>')

            html_parts.append('<tbody>')
            for idx, row in df_display.iterrows():
                html_parts.append('<tr>')
                for col in df_display.columns:
                    val = row[col]
                    style = "color: #FF69B4; font-weight: bold;" if col == "PART NUMBER" else ""
                    html_parts.append(f'<td style="{style}">{str(val)}</td>')
                html_parts.append('</tr>')
            html_parts.append('</tbody></table>')
            html_parts.append('</div>')

            st.markdown(''.join(html_parts), unsafe_allow_html=True)
        else:
            st.markdown("---")
            st.warning("⚠️ **Không tìm thấy kết quả phù hợp** với các tiêu chí đã chọn.")

    elif not all_criteria_met:
        st.markdown("---")
        prompt_text = "Zone"
        if zone_selected and not aircraft_selected and ac_exists:
            prompt_text = "Loại máy bay"
        elif zone_selected and aircraft_selected and desc_exists and not desc_selected:
            prompt_text = "Mô tả chi tiết"
        elif zone_selected and aircraft_selected and item_exists and (desc_selected or not desc_exists) and not item_selected:
            prompt_text = "Item"

        st.markdown(
            f"""
            <div style='
                text-align: center;
                background-color: rgba(0,255,0, 0.1);
                border: 1px solid #00FF00;
                padding: 10px 25px;
                border-radius: 12px;
                margin: 15px auto;
                max-width: fit-content;
            '>
                <p style='
                    font-size: 1.1rem;
                    margin: 0;
                    text-shadow: 0 0 5px #FFFFE0;
                '>
                    <font color="#FFFFE0">💡 Vui lòng <strong>chọn {prompt_text}</strong> để tiếp tục tra cứu.</font>
                </p>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.markdown("---")
        st.warning("⚠️ **Không có dữ liệu Part Number** trong Zone này.")
