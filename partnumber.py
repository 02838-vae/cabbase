import streamlit as st
import pandas as pd
import base64
import os

# --- CẤU HÌNH ---
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1 - Tra Cứu PN", layout="wide")

# --- HÀM HỖ TRỢ ---
def get_base64_encoded_file(file_path):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return ""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def load_and_clean(excel_file, sheet):  
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet)
        df.columns = df.columns.str.strip().str.upper()
        df = df.replace(r'^\s*$', pd.NA, regex=True).dropna(how="all")
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].fillna("").astype(str).str.strip()
        return df
    except Exception:
        return pd.DataFrame()

# --- NỀN ---
bg_pc_base64 = get_base64_encoded_file("PN_PC.jpg")
bg_mobile_base64 = get_base64_encoded_file("PN_mobile.jpg")

# --- CSS ---
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap');

#MainMenu, footer, header {{visibility: hidden;}}
div.block-container {{padding-top: 0; background-color: transparent !important;}}

/* === NỀN PC === */
.stAppViewContainer {{
    background: url("data:image/jpeg;base64,{bg_pc_base64}") no-repeat center top fixed !important;
    background-size: cover !important;
    font-family: 'Oswald', sans-serif !important;
}}

/* === HIỆU ỨNG CHỮ === */
@keyframes scrollText {{
    0% {{ transform: translateX(100vw); }}
    100% {{ transform: translateX(-100%); }}
}}
@keyframes colorShift {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

/* === TIÊU ĐỀ CHÍNH (CHẠY NHANH HƠN) === */
#main-animated-title-container {{
    width: 100%;
    height: 110px;
    overflow: hidden;
    text-align: center;
    margin-top: 35px;
}}
#main-animated-title-container h1 {{
    font-family: 'Oswald', sans-serif;
    font-size: 4.5rem;
    font-weight: 700;
    letter-spacing: 6px;
    text-transform: uppercase;
    white-space: nowrap; 
    display: inline-block;
    background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
    background-size: 400% 400%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: colorShift 8s ease infinite, scrollText 7s linear infinite; /* ✅ chạy nhanh hơn */
    text-shadow: 2px 2px 8px rgba(0,0,0,0.7);
    line-height: 1.3;
    padding-bottom: 10px;
}}

/* === TIÊU ĐỀ PHỤ (TRA CỨU...) TO HƠN, DỊCH XUỐNG HƠN) === */
#sub-static-title h2 {{
    font-family: 'Playfair Display', serif;
    font-size: 3rem;  /* ✅ tăng kích cỡ chữ */
    color: #FFD54F;
    text-align: center;
    text-shadow: 2px 2px 6px rgba(0,0,0,0.6);
    margin-top: 110px;  /* ✅ hạ thấp mạnh hơn */
    margin-bottom: 20px;
}}

/* === TIÊU ĐỀ DROPDOWN (PC) === */
h3.dropdown-label {{
    color: #FFD700;
    text-align: center;
    font-size: 1.6rem;
    font-weight: 800;
    text-shadow: 2px 2px 6px rgba(0,0,0,0.7);
    margin-bottom: 0.4rem;
}}

/* === MOBILE === */
@media (max-width: 768px) {{
    .stAppViewContainer {{
        background: url("data:image/jpeg;base64,{bg_mobile_base64}") no-repeat center top scroll !important;
        background-size: cover !important;
    }}

    #main-animated-title-container {{
        margin-top: 10px !important;
        overflow: hidden;
        height: auto;
    }}

    #main-animated-title-container h1 {{
        font-size: 6.5vw;
        letter-spacing: 3px;
        animation: colorShift 8s ease infinite, scrollText 6s linear infinite; /* ✅ nhanh hơn mobile */
        text-shadow: 2px 2px 7px rgba(0,0,0,0.8);
    }}

    #sub-static-title h2 {{
        font-size: 6vw;  /* ✅ to hơn */
        color: #FFD54F;
        margin-top: 90px;  /* ✅ dịch xuống thêm */
    }}

    h3.dropdown-label {{
        font-size: 4.5vw; /* ✅ dropdown to hơn xíu */
        line-height: 1.1;
        margin-bottom: 0.5rem;
    }}

    /* Giúp bảng có thể vuốt ngang */
    .table-container {{
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        white-space: nowrap;
    }}
}}

/* === BẢNG HTML === */
.table-container {{
    overflow-x: auto;
    margin: 20px 0;
    width: 100%;
}}

.custom-table {{
    width: 100%;
    border-collapse: collapse;
    margin: 20px auto;
    background-color: white;
    box-shadow: 0 0 15px rgba(0,0,0,0.3); 
    border-radius: 8px; 
    overflow: hidden; 
    table-layout: auto;
}}

.custom-table th {{
    background-color: #2E7D32;
    color: white;
    padding: 14px;
    text-align: center !important;
    font-weight: bold;
    border: 1px solid #ddd;
    font-size: 1.05rem;
    white-space: nowrap;
}}

.custom-table td {{
    padding: 12px;
    text-align: center !important;
    border: 1px solid #ddd;
    vertical-align: middle;
    font-size: 1rem;
    color: #000000;
    white-space: nowrap;
}}

.custom-table tr:nth-child(even) {{background-color: #f9f9f9;}}
.custom-table tr:hover {{background-color: #e0e0e0;}}
</style>
""", unsafe_allow_html=True)

# --- TIÊU ĐỀ ---
st.markdown('<div id="main-animated-title-container"><h1>TỔ BẢO DƯỠNG SỐ 1</h1></div>', unsafe_allow_html=True)
st.markdown('<div id="sub-static-title"><h2>🔎 TRA CỨU PART NUMBER</h2></div>', unsafe_allow_html=True)
st.markdown("---")

# --- TRA CỨU ---
excel_file = "A787.xlsx"
REQUIRED_COLS = ["A/C", "DESCRIPTION", "ITEM"]

if not os.path.exists(excel_file):
    st.error("❌ Không tìm thấy file A787.xlsx trong thư mục hiện tại.")
else:
    try:
        xls = pd.ExcelFile(excel_file)
        sheet_names = [name for name in xls.sheet_names if not name.startswith("Sheet")]

        selection = {"Zone": None, "A/C": None, "DESCRIPTION": None, "ITEM": None}
        current_df = pd.DataFrame()
        
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        cols = st.columns(4)
        
        with cols[0]:
            st.markdown("<h3 class='dropdown-label'>📂 Zone</h3>", unsafe_allow_html=True)
            zone_options = ["Chọn Zone..."] + sheet_names
            zone_selected = st.selectbox("", zone_options, label_visibility="collapsed")
            if zone_selected != "Chọn Zone...":
                selection["Zone"] = zone_selected

        if selection["Zone"]:
            current_df = load_and_clean(excel_file, selection["Zone"])
        else:
            current_df = pd.DataFrame() 

        available_cols = [col for col in REQUIRED_COLS if col in current_df.columns]

        col_labels = {
            "A/C": "✈️ Loại máy bay",
            "DESCRIPTION": "📑 Mô tả chi tiết",
            "ITEM": "🔢 Item"
        }

        for i, col_name in enumerate(REQUIRED_COLS):
            if col_name in available_cols:
                with cols[i + 1]:
                    st.markdown(f"<h3 class='dropdown-label'>{col_labels[col_name]}</h3>", unsafe_allow_html=True)
                    if not current_df.empty:
                        options = current_df[col_name].astype(str).str.strip().unique().tolist()
                        options = [opt for opt in options if opt != ""]
                        options.sort()
                    else:
                        options = []

                    if col_name == "A/C":
                        placeholder = "Chọn máy bay..."
                    elif col_name == "DESCRIPTION":
                        placeholder = "Chọn Mô tả..."
                    else:
                        placeholder = f"Chọn {col_labels[col_name].split()[-1]}..."

                    select_options = [placeholder] + options
                    selected = st.selectbox("", select_options, label_visibility="collapsed")
                    if selected != placeholder:
                        selection[col_name] = selected
                    if selection[col_name]:
                        current_df = current_df[current_df[col_name] == selection[col_name]]

        st.markdown("</div>", unsafe_allow_html=True)

        if selection["Zone"] and all(selection.get(col) for col in available_cols) and not current_df.empty:
            st.markdown("---")
            st.markdown("<h3 style='text-align:center; color:#2E7D32;'>📋 KẾT QUẢ TRA CỨU</h3>", unsafe_allow_html=True)
            
            df_display = current_df.drop(columns=available_cols, errors="ignore")
            df_display = df_display.dropna(axis=1, how="all")
            df_display = df_display.reset_index(drop=True)
            df_display.insert(0, "STT", range(1, len(df_display) + 1))

            html_parts = ['<div class="table-container"><table class="custom-table">']
            html_parts.append('<thead><tr>')
            for col in df_display.columns:
                html_parts.append(f'<th>{col}</th>')
            html_parts.append('</tr></thead><tbody>')
            for _, row in df_display.iterrows():
                html_parts.append('<tr>' + ''.join(f'<td>{str(v)}</td>' for v in row) + '</tr>')
            html_parts.append('</tbody></table></div>')
            st.markdown(''.join(html_parts), unsafe_allow_html=True)

        elif selection["Zone"] and all(selection.get(col) for col in available_cols) and current_df.empty:
            st.markdown("---")
            st.info("⚠️ Không tìm thấy kết quả nào phù hợp với lựa chọn của bạn.")
    except Exception as e:
        st.error(f"Lỗi khi xử lý dữ liệu: {e}")
