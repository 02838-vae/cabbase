# pages/partnumber.py

import streamlit as st
import pandas as pd
import base64
import os
import html as html_module

# --- CẤU HÌNH ---
st.set_page_config(page_title="Tra cứu PN", layout="wide", initial_sidebar_state="collapsed")

# --- HÀM HỖ TRỢ ---
def get_base64_encoded_file(file_path):
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
    try:
        excel_path = os.path.join(os.path.dirname(__file__), excel_file.replace("pages/", ""))
        df = pd.read_excel(excel_path, sheet_name=sheet)
        df.columns = df.columns.str.strip().str.upper()
        df = df.replace(r'^\s*$', pd.NA, regex=True).dropna(how="all")
        for fcol in ["A/C", "DESCRIPTION", "ITEM"]:
            if fcol in df.columns:
                df[fcol] = df[fcol].ffill()
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].fillna("").astype(str).str.strip()
            if col in ["A/C", "DESCRIPTION", "ITEM", "PART NUMBER"] and df[col].eq("").all():
                return pd.DataFrame()
        return df
    except Exception:
        return pd.DataFrame()

# --- BIẾN VÀ ĐƯỜNG DẪN ---
CHOOSE_PROMPT = "-- CHỌN --"
excel_file = "pages/A787.xlsx"

# --- CSS TỐI GIẢN ---
st.markdown("""
<style>
/* BASE */
html, body, .stApp {
    background: #ffffff !important;
    color: #1a1a1a !important;
    font-family: 'Arial', 'Helvetica', sans-serif !important;
}
[data-testid="stAppViewContainer"], [data-testid="stMainBlock"], .main {
    background: #ffffff !important;
}

/* ẨN UI */
#MainMenu, footer, header { visibility: hidden; height: 0; }
[data-testid="stHeader"] { display: none; }
[data-testid="stSidebar"], [data-testid="stSidebarNav"],
[data-testid="collapsedControl"], section[data-testid="stSidebar"] {
    display: none !important; width: 0 !important;
    min-width: 0 !important; visibility: hidden !important;
}

/* PADDING */
.main { padding: 0 !important; margin: 0 !important; }
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
}

/* TEXT */
.stApp p, .stApp span, .stApp div, .stApp label,
[data-testid="stMarkdownContainer"] *, [data-testid="stWidgetLabel"] * {
    color: #1a1a1a !important;
    font-family: 'Arial', 'Helvetica', sans-serif !important;
}

/* SELECTBOX label */
div.stSelectbox label, div.stSelectbox label p, div.stSelectbox label span,
[data-testid="stSelectbox"] label p {
    color: #1a1a1a !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
}
.stSelectbox div[data-baseweb="select"] {
    background-color: #ffffff !important;
    border: 2px solid #1d6fc4 !important;
    border-radius: 8px !important;
    outline: none !important;
    box-shadow: none !important;
}
.stSelectbox div[data-baseweb="select"]:focus-within,
.stSelectbox div[data-baseweb="select"]:focus,
.stSelectbox div[data-baseweb="select"] *:focus {
    border-color: #1d6fc4 !important;
    outline: none !important;
    box-shadow: none !important;
}
[data-baseweb="select"]:focus-within {
    border-color: #1d6fc4 !important;
    outline: none !important;
    box-shadow: none !important;
}
.stSelectbox div[data-baseweb="select"] *,
.stSelectbox div[data-baseweb="select"] span,
.stSelectbox div[data-baseweb="select"] div,
.stSelectbox div[data-baseweb="select"] input {
    color: #1a1a1a !important;
    background-color: #ffffff !important;
    font-size: 0.95rem !important;
}
[data-baseweb="popover"] *, [data-baseweb="menu"] *,
[role="listbox"] *, [role="option"] *, li[role="option"] * {
    color: #1a1a1a !important;
    background-color: #ffffff !important;
    font-size: 0.95rem !important;
}
[role="option"]:hover, [role="option"]:hover * {
    background-color: #f3f4f6 !important;
}

/* KẾT QUẢ TITLE */
.result-title { text-align: center; margin: 20px 0 12px 0; }
.result-title h3 {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1a1a1a;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* BẢNG KẾT QUẢ */
.table-container {
    overflow-x: auto;
    margin-top: 8px;
    border-radius: 8px;
    border: 2px solid #1d6fc4;
}
.custom-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Arial', 'Helvetica', sans-serif;
    font-size: 14px;
    color: #1a1a1a;
}
.custom-table th {
    background-color: #ffffff;
    color: #1d6fc4;
    font-weight: 700;
    padding: 10px 14px;
    text-align: center;
    border-bottom: 2px solid #1d6fc4;
    border-right: 1px solid #1d6fc4;
    white-space: nowrap;
    font-size: 13px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.custom-table th:last-child { border-right: none; }
.custom-table td {
    padding: 9px 14px;
    text-align: center;
    border-bottom: 1px solid #e0ecf8;
    border-right: 1px solid #e0ecf8;
    color: #1a1a1a;
    vertical-align: middle;
}
.custom-table td:last-child { border-right: none; }
.custom-table tbody tr:hover { background-color: #f0f6ff; }
.custom-table tbody tr:last-child td { border-bottom: none; }

/* PROMPT BOX */
.prompt-box {
    text-align: center;
    background-color: #ffffff;
    border: 2px solid #1d6fc4;
    padding: 12px 28px;
    border-radius: 8px;
    margin: 20px auto;
    max-width: fit-content;
}
.prompt-box p {
    font-size: 1rem;
    margin: 0;
    color: #1d6fc4 !important;
    font-weight: 600;
}

/* MOBILE */
@media (max-width: 768px) {
    .custom-table { font-size: 12px; }
    .custom-table th, .custom-table td { padding: 7px 8px; }
    .result-title h3 { font-size: 1rem; }
}
</style>
""", unsafe_allow_html=True)

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
    descs_options = [CHOOSE_PROMPT] + list(dict.fromkeys(
        v for v in df_filtered["DESCRIPTION"].tolist()
        if v != "" and str(v).strip().lower() not in ("nan", "none", "")
    ))
    with col3:
        desc = st.selectbox("🔑 Mô tả chi tiết", descs_options, key="desc_select")
    desc_selected = (desc and desc != CHOOSE_PROMPT)
    if desc_selected:
        df_filtered = df_filtered[df_filtered["DESCRIPTION"] == desc].copy()

item_exists = "ITEM" in df_filtered.columns
item_selected = False
if (aircraft_selected and zone_selected) and item_exists and (desc_selected or not desc_exists):
    items_options = [CHOOSE_PROMPT] + list(dict.fromkeys(
        v for v in df_filtered["ITEM"].tolist()
        if v != "" and str(v).strip().lower() not in ("nan", "none", "")
    ))
    with col4:
        item = st.selectbox("🔌 Item", items_options, key="item_select")
    item_selected = (item and item != CHOOSE_PROMPT)
    if item_selected:
        df_filtered = df_filtered[df_filtered["ITEM"] == item].copy()

# --- HIỂN THỊ KẾT QUẢ ---
all_criteria_met = (
    zone_selected and aircraft_selected
    and (desc_selected or not desc_exists)
    and (item_selected or not item_exists)
)

if zone_selected:
    if all_criteria_met:
        df_display = df_filtered.copy()
        for drop_col in ["DESCRIPTION", "ITEM", "A/C"]:
            if drop_col in df_display.columns:
                df_display = df_display.drop(columns=[drop_col])

        if len(df_display) > 0:
            st.markdown('<div class="result-title"><h3>Kết quả tra cứu</h3></div>', unsafe_allow_html=True)

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
            html_parts.append('</tr></thead><tbody>')

            import math
            for idx, row in df_display.iterrows():
                html_parts.append('<tr>')
                for col in df_display.columns:
                    val = row[col]
                    if val is None:
                        display_val = ""
                    elif isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
                        display_val = ""
                    else:
                        display_val = str(val).strip()
                        if display_val.lower() in ("nan", "none", "nat", "<na>"):
                            display_val = ""
                    safe_val = html_module.escape(str(display_val))
                    if col == "PART NUMBER":
                        style = "color: #1d6fc4; font-weight: 700; white-space: nowrap;"
                        html_parts.append(f'<td style="{style}">{safe_val}</td>')
                    elif col in ("NOTE", "NOTES", "PN INTERCHANGE", "PN INTERCHAGE"):
                        style = "max-width:260px; word-wrap:break-word; white-space:pre-wrap; text-align:left !important;"
                        html_parts.append(f'<td style="{style}">{safe_val}</td>')
                    else:
                        html_parts.append(f'<td>{safe_val}</td>')
                html_parts.append('</tr>')

            html_parts.append('</tbody></table></div>')
            st.markdown(''.join(html_parts), unsafe_allow_html=True)
        else:
            st.warning("⚠️ **Không tìm thấy kết quả phù hợp** với các tiêu chí đã chọn.")

    elif not all_criteria_met:
        prompt_text = "Zone"
        if zone_selected and not aircraft_selected and ac_exists:
            prompt_text = "Loại máy bay"
        elif zone_selected and aircraft_selected and desc_exists and not desc_selected:
            prompt_text = "Mô tả chi tiết"
        elif zone_selected and aircraft_selected and item_exists and (desc_selected or not desc_exists) and not item_selected:
            prompt_text = "Item"

        st.markdown(f"""
<div class="prompt-box">
    <p>💡 Vui lòng <strong>chọn {prompt_text}</strong> để tiếp tục tra cứu.</p>
</div>
""", unsafe_allow_html=True)

    else:
        st.warning("⚠️ **Không có dữ liệu Part Number** trong Zone này.")
