# pages/partnumber.py

import streamlit as st
import pandas as pd
import base64
import os

# --- CẤU HÌNH ---
st.set_page_config(page_title="Tra Cứu PN", layout="wide", initial_sidebar_state="collapsed")

# --- HÀM HỖ TRỢ ---
def get_base64_encoded_file(file_path):
    """Mã hóa file ảnh sang base64."""
    # Sửa đường dẫn để tìm file trong thư mục pages/ hoặc thư mục gốc
    path_to_check = file_path
    if "pages/" not in path_to_check:
        # Thử tìm trong thư mục gốc nếu nó là logo.jpg
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
        # Đường dẫn file excel, giả định nó nằm trong thư mục pages/
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
excel_file = "pages/A787.xlsx" # Giả định file excel nằm cùng cấp với thư mục pages/

try:
    # Cần đảm bảo các file này nằm trong thư mục 'pages/'
    pn_bg_pc_base64 = get_base64_encoded_file("pages/PC.jpg")
    pn_bg_mobile_base64 = get_base64_encoded_file("pages/mobile.jpg")
    logo_base64 = get_base64_encoded_file("pages/logo.jpg")
except Exception as e:
    st.error(f"❌ Lỗi khi đọc file ảnh nền: {str(e)}")
    st.stop()

# --- CSS ---
hide_streamlit_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rye&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;700&display=swap');
#MainMenu, footer, header {{visibility: hidden;}}

.main {{
    padding: 0;
    margin: 0;
    background-color: transparent !important;
    z-index: 10 !important;
}}

/* ✅ BACKGROUND - màu nền tối làm fallback */
.stApp {{
    background-color: #1a1a2e !important;
    font-family: 'Oswald', sans-serif !important;
}}

/* ✅ BANNER NỀN PC - fixed, height 120px */
#bg-banner {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 120px;
    background-image: url("data:image/jpeg;base64,{pn_bg_pc_base64}");
    background-repeat: no-repeat;
    background-position: center center;
    background-size: 100% 100%;
    z-index: 50;
}}

/* ✅ MOBILE: mobile.jpg full chiều rộng, height 120px */
@media (max-width: 768px) {{
    #bg-banner {{
        background-image: url("data:image/jpeg;base64,{pn_bg_mobile_base64}");
        background-repeat: no-repeat;
        background-position: center center;
        background-size: 100% 100%;
        height: 120px;
        width: 100vw;
    }}
}}

/* Đẩy nội dung xuống dưới banner */
.main > div:first-child {{
    padding-top: 150px !important;
    padding-left: 20px;
    padding-right: 20px;
}}

/* ✅ KEYFRAMES ÁNH SÁNG VÀNG CHẠY VÒNG QUANH */
@keyframes borderGlow {{
    0%   {{ box-shadow: 4px 0 16px 4px #FFD700, 0 0 0 3px #FFD700; border-color: #FFD700; }}
    25%  {{ box-shadow: 0 4px 16px 4px #FFA500, 0 0 0 3px #FFA500; border-color: #FFA500; }}
    50%  {{ box-shadow: -4px 0 16px 4px #FFEA00, 0 0 0 3px #FFEA00; border-color: #FFEA00; }}
    75%  {{ box-shadow: 0 -4px 16px 4px #FF8C00, 0 0 0 3px #FF8C00; border-color: #FF8C00; }}
    100% {{ box-shadow: 4px 0 16px 4px #FFD700, 0 0 0 3px #FFD700; border-color: #FFD700; }}
}}

@keyframes rotateBorder {{
    0%   {{ background-position: 0% 50%; }}
    50%  {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

@keyframes glowPulse {{
    0%, 100% {{
        filter: drop-shadow(0 0 8px #FFD700) drop-shadow(0 0 20px #FFD700) drop-shadow(0 0 40px #FFA500);
    }}
    50% {{
        filter: drop-shadow(0 0 16px #FFEA00) drop-shadow(0 0 40px #FFEA00) drop-shadow(0 0 70px #FF8C00);
    }}
}}

/* ✅ LOGO - fixed trên cùng, giữa trang */
#logo-container {{
    position: fixed;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    z-index: 200;
    text-align: center;
    height: 120px;
    display: flex;
    align-items: center;
    justify-content: center;
    pointer-events: none;
}}

/* Khung viền logo với ánh sáng vàng chạy vòng */
#logo-frame {{
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 5px;
    border-radius: 14px;
    border: 3px solid #FFD700;
    animation: borderGlow 2s linear infinite;
    background: rgba(0,0,0,0.35);
}}

/* Vòng sáng xoay bằng pseudo conic-gradient qua JS thay thế */
#logo-frame::before {{
    content: '';
    position: absolute;
    inset: -4px;
    border-radius: 16px;
    background: conic-gradient(
        from 0deg,
        transparent 0deg,
        #FFD700 60deg,
        #FFEA00 90deg,
        #FFA500 120deg,
        transparent 180deg,
        transparent 360deg
    );
    animation: spin 1.8s linear infinite;
    z-index: -1;
}}

#logo-frame::after {{
    content: '';
    position: absolute;
    inset: 2px;
    border-radius: 12px;
    background: rgba(0,0,0,0.5);
    z-index: -1;
}}

@keyframes spin {{
    from {{ transform: rotate(0deg); }}
    to   {{ transform: rotate(360deg); }}
}}

#logo-container img {{
    height: 100px;
    width: auto;
    object-fit: contain;
    border-radius: 10px;
    display: block;
    position: relative;
    z-index: 1;
}}

@media (max-width: 768px) {{
    #logo-container img {{
        height: 75px;
    }}
    #logo-frame {{
        border-radius: 10px;
    }}
}}

/* ✅ TIÊU ĐỀ PHỤ - FONT CAO BỒI (Rye) */
#sub-static-title {{
    position: static;
    margin-top: 10px;
    margin-bottom: 25px;
    z-index: 90;
    background: transparent !important;
    text-align: center;
}}

#sub-static-title h2 {{
    font-family: 'Rye', cursive !important;
    font-size: 2.2rem;
    color: #FFEA00;
    text-align: center;
    text-shadow: 0 0 15px #FFEA00, 0 0 30px rgba(255,234,0,0.8), 2px 2px 4px rgba(0,0,0,0.9);
    margin-bottom: 20px;
    letter-spacing: 3px;
}}

/* ✅ TIÊU ĐỀ KẾT QUẢ - FONT CAO BỒI (Rye) */
.result-title h3 {{
    font-family: 'Rye', cursive !important;
    font-size: 2rem;
    color: #FFEA00;
    text-align: center;
    text-shadow: 0 0 15px #FFEA00, 0 0 30px rgba(255,234,0,0.8), 2px 2px 4px rgba(0,0,0,0.9);
    margin-bottom: 20px;
    letter-spacing: 2px;
}}

@media (max-width: 768px) {{
    #sub-static-title h2 {{
        font-size: 1.3rem;
        letter-spacing: 1px;
    }}
    .result-title h3 {{
        font-size: 1.2rem;
    }}
}}

/* --- CSS CHO DROPDOWN LABEL - FONT CAO BỒI --- */
div.stSelectbox label p, div[data-testid*="column"] label p {{
    color: #FFD700 !important;
    font-size: 1.1rem !important;
    font-weight: bold;
    font-family: 'Rye', cursive !important;
    text-shadow: 0 0 6px rgba(255,215,0,0.7), 1px 1px 3px rgba(0,0,0,0.9);
}}

.stSelectbox div[data-baseweb="select"] {{
    background-color: rgba(0, 0, 0, 0.75);
    border: 1px solid #FFD700;
    border-radius: 8px;
}}

.stSelectbox div[data-baseweb="select"] div[data-testid="stTextInput"] {{
    color: #FFFFFF !important;
    font-family: 'Rye', cursive !important;
}}

/* Nội dung bên trong dropdown */
div[data-baseweb="select"] span,

div[data-baseweb="select"] div {{
    font-family: 'Rye', cursive !important;
    color: #FFFFFF !important;
}}

/* ✅ BẢNG KẾT QUẢ */
.custom-table th {{
    background-color: #1E8449 !important;
    color: #FFFFFF !important;
    padding: 14px;
    border: 2px solid #2ECC71;
    font-size: 1.05rem;
    font-weight: bold;
    text-align: center !important;
    font-family: 'Rye', cursive !important;
    letter-spacing: 1px;
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

# --- LOGIC CHÍNH ---

# ✅ BANNER NỀN CỐ ĐỊNH + LOGO GIỮA CÓ VIỀN SÁNG VÀNG XOAY
st.markdown(f"""
<div id="bg-banner"></div>
<div id="logo-container">
    <div id="logo-frame">
        <img src="data:image/jpeg;base64,{logo_base64}" alt="Logo" />
    </div>
</div>
""", unsafe_allow_html=True)

# --- TIÊU ĐỀ TRA CỨU PART NUMBER ---
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
