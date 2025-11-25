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
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

# Thử mã hóa file logo
logo_base64 = get_base64_encoded_file("../assets/logo.jpg") or get_base64_encoded_file("logo.jpg")

# --- CSS TÙY CHỈNH ---
st.markdown("""
<style>
    /* Ẩn Streamlit Header, Footer và Menu */
    #MainMenu, footer, header {visibility: hidden;}
    .stApp {background-color: #0d1117; color: white;}
    
    /* Điều chỉnh padding container */
    .stApp .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }

    /* Tiêu đề chính */
    #main-title-container {
        text-align: center;
        color: #FFFFFF;
        font-family: 'Arial Black', Gadget, sans-serif;
        text-shadow: 2px 2px 4px #000000;
        background: -webkit-linear-gradient(90deg, #00FF00, #FFFF00, #00FF00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: clamp(2.5rem, 5vw, 4rem);
        line-height: 1.1;
    }
    .number-one {
        font-size: clamp(3rem, 6vw, 5rem);
        color: #00FF00; 
        text-shadow: 0 0 10px #00FF00, 0 0 20px #00FF00, 0 0 30px #00FF00; 
        margin-left: 10px;
    }
    
    /* Sub-title */
    #sub-static-title h2 {
        text-align: center;
        color: #00FF00;
        text-shadow: 0 0 5px #000, 0 0 10px #00FF00;
        border-bottom: 3px solid #00FF00;
        padding-bottom: 10px;
        margin-bottom: 20px;
        font-size: 1.8rem;
    }
    
    /* Header (FIX 2) */
    #header-content-wrapper {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        margin-bottom: 10px;
        border-bottom: 1px solid #00FF00;
    }
    
    #back-to-home-btn-container {
        flex-shrink: 0;
    }
    
    #manual-home-btn {
        background-color: #333;
        color: #00FF00 !important;
        padding: 8px 15px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        font-size: 1rem;
        transition: all 0.2s;
        border: 2px solid #00FF00;
        box-shadow: 0 0 5px #00FF00;
    }
    
    #manual-home-btn:hover {
        background-color: #00FF00;
        color: #0d1117 !important;
        box-shadow: 0 0 10px #00FF00;
    }

    /* Các thành phần tra cứu */
    .stSelectbox, .stTextInput, .stButton {
        margin-bottom: 15px;
    }

    /* Kết quả */
    .result-container {
        padding: 20px;
        background-color: #1f2a38;
        border-radius: 10px;
        margin-top: 20px;
        border: 1px solid #00FF00;
        box-shadow: 0 0 15px rgba(0, 255, 0, 0.4);
    }
    .result-item {
        border-bottom: 1px dashed #444;
        padding: 10px 0;
    }
    .result-item:last-child {
        border-bottom: none;
    }
    .result-item strong {
        color: #00FF00;
        text-shadow: 0 0 5px #00FF00;
    }
    .result-item p {
        margin: 5px 0;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)


# ====================================================
# 🧭 HEADER & BODY
# ====================================================
# FIX 2: Thêm Header với nút Home (href="/?skip_intro=1" target="_self")
st.markdown("""
<div id="header-content-wrapper">
    <div id="back-to-home-btn-container">
        <a id="manual-home-btn" href="/?skip_intro=1" target="_self">🏠 Về Trang Chủ</a>
    </div>
    <div id="main-title-container"><h1>TỔ BẢO DƯỠNG SỐ <span class="number-one">1</span></h1></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div id="sub-static-title"><h2>TRA CỨU PART NUMBER</h2></div>', unsafe_allow_html=True)

# --- UPLOAD & XỬ LÝ DATA ---
uploaded_file = st.file_uploader("Upload file Excel PN (pn_data.xlsx):", type="xlsx", help="File Excel phải có các cột: Zone, Aircraft, Description, Item, PN, Location, Image, Remark.")

if "data_df" not in st.session_state:
    st.session_state.data_df = pd.DataFrame()

if uploaded_file is not None:
    @st.cache_data(show_spinner="Đang đọc file Excel...")
    def load_data(file):
        try:
            df = pd.read_excel(file)
            # Chuẩn hóa tên cột và làm sạch data
            df.columns = [col.strip() for col in df.columns]
            required_cols = ['Zone', 'Aircraft', 'Description', 'Item', 'PN', 'Location', 'Image', 'Remark']
            for col in required_cols:
                if col not in df.columns:
                    st.error(f"Lỗi: File Excel thiếu cột bắt buộc '{col}'. Vui lòng kiểm tra lại cấu trúc file.")
                    return pd.DataFrame()
            
            # Thay thế NaN bằng chuỗi rỗng và chuyển sang kiểu string cho các cột category
            for col in ['Zone', 'Aircraft', 'Description', 'Item']:
                df[col] = df[col].astype(str).fillna('')
            
            return df
        except Exception as e:
            st.error(f"Lỗi khi đọc file Excel: {e}")
            return pd.DataFrame()

    df = load_data(uploaded_file)
    st.session_state.data_df = df
else:
    st.info("Vui lòng upload file Excel chứa dữ liệu Part Number để bắt đầu tra cứu.")
    df = st.session_state.data_df

# --- GIAO DIỆN TRA CỨU ---

if not df.empty:
    
    st.subheader("BƯỚC 1: Chọn tiêu chí tra cứu")
    
    # Lọc danh sách duy nhất cho từng cấp độ
    zone_options = sorted(df['Zone'].unique().tolist())
    zone_options.insert(0, "Tất cả")
    
    # --- Cấp độ 1: ZONE ---
    zone_selected = st.selectbox(
        "Chọn Zone:", 
        options=zone_options,
        key="zone_select"
    )

    filtered_df = df.copy()
    if zone_selected != "Tất cả":
        filtered_df = filtered_df[filtered_df['Zone'] == zone_selected]

    # --- Cấp độ 2: AIRCRAFT ---
    aircraft_options = sorted(filtered_df['Aircraft'].unique().tolist())
    aircraft_exists = len(aircraft_options) > 1 or (len(aircraft_options) == 1 and aircraft_options[0] != '')
    if aircraft_exists:
        aircraft_options.insert(0, "Tất cả")
        aircraft_selected = st.selectbox(
            "Chọn Loại máy bay (Aircraft):",
            options=aircraft_options,
            key="aircraft_select"
        )
        if aircraft_selected != "Tất cả":
            filtered_df = filtered_df[filtered_df['Aircraft'] == aircraft_selected]
    else:
        aircraft_selected = "Tất cả"


    # --- Cấp độ 3: DESCRIPTION ---
    desc_options = sorted(filtered_df['Description'].unique().tolist())
    desc_exists = len(desc_options) > 1 or (len(desc_options) == 1 and desc_options[0] != '')
    if desc_exists:
        desc_options.insert(0, "Tất cả")
        desc_selected = st.selectbox(
            "Chọn Mô tả chi tiết (Description):",
            options=desc_options,
            key="desc_select"
        )
        if desc_selected != "Tất cả":
            filtered_df = filtered_df[filtered_df['Description'] == desc_selected]
    else:
        desc_selected = "Tất cả"

    # --- Cấp độ 4: ITEM ---
    item_options = sorted(filtered_df['Item'].unique().tolist())
    item_exists = len(item_options) > 1 or (len(item_options) == 1 and item_options[0] != '')
    if item_exists:
        item_options.insert(0, "Tất cả")
        item_selected = st.selectbox(
            "Chọn Item:",
            options=item_options,
            key="item_select"
        )
        if item_selected != "Tất cả":
            filtered_df = filtered_df[filtered_df['Item'] == item_selected]
    else:
        item_selected = "Tất cả"

    # --- Tìm kiếm PN nhanh ---
    st.subheader("BƯỚC 2: Tìm kiếm nhanh (Tùy chọn)")
    search_term = st.text_input("Tìm kiếm theo PN, Location hoặc Remark (từ khóa):", key="search_term")
    
    if search_term:
        search_term = search_term.strip().lower()
        filtered_df = filtered_df[
            filtered_df['PN'].astype(str).str.lower().str.contains(search_term) |
            filtered_df['Location'].astype(str).str.lower().str.contains(search_term) |
            filtered_df['Remark'].astype(str).str.lower().str.contains(search_term)
        ]

    # --- HIỂN THỊ KẾT QUẢ ---
    
    results_df = filtered_df.drop_duplicates(subset=['Zone', 'Aircraft', 'Description', 'Item', 'PN', 'Location'])
    
    # Xác định các tiêu chí đã được chọn để quyết định hiển thị kết quả
    all_criteria_met = (zone_selected != "Tất cả") and \
                       (not aircraft_exists or aircraft_selected != "Tất cả") and \
                       (not desc_exists or desc_selected != "Tất cả") and \
                       (not item_exists or item_selected != "Tất cả")
    
    
    if results_df.empty:
        st.markdown("---\n")
        st.warning("⚠️ **Không tìm thấy kết quả phù hợp** với các tiêu chí đã chọn.")
    
    elif all_criteria_met or search_term:
        st.subheader(f"🔍 Kết quả tra cứu ({len(results_df)} mục)")
        st.markdown("---")

        html_parts = []
        for index, row in results_df.iterrows():
            # Mã hóa ảnh từ đường dẫn trong cột Image
            image_path = row['Image'] if pd.notna(row['Image']) and row['Image'] != '' else None
            image_b64 = None
            if image_path:
                image_b64 = get_base64_encoded_file(image_path)
            
            image_html = ""
            if image_b64:
                image_html = f"""
                <div style='text-align: center; margin-top: 15px;'>
                    <img src="data:image/jpeg;base64,{image_b64}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);" alt="Hình ảnh PN">
                </div>
                """
            
            html_parts.append(f"""
            <div class="result-container">
                <div class="result-item">
                    <p><strong>Part Number:</strong> <span style="font-size: 1.2rem; color: #FFFFE0;">{row['PN']}</span></p>
                </div>
                <div class="result-item">
                    <p><strong>Zone:</strong> {row['Zone']}</p>
                </div>
                <div class="result-item">
                    <p><strong>Aircraft:</strong> {row['Aircraft']}</p>
                </div>
                <div class="result-item">
                    <p><strong>Description:</strong> {row['Description']}</p>
                </div>
                <div class="result-item">
                    <p><strong>Item:</strong> {row['Item']}</p>
                </div>
                <div class="result-item">
                    <p><strong>Location:</strong> {row['Location']}</p>
                </div>
                <div class="result-item">
                    <p><strong>Remark:</strong> {row['Remark']}</p>
                </div>
                {image_html}
            </div>
            """)

        st.markdown(''.join(html_parts), unsafe_allow_html=True)
    else:
        st.markdown("---")
        prompt_text = "Zone"
        ac_exists = aircraft_exists # dùng tên ngắn hơn cho dễ đọc
        desc_exists = desc_exists
        item_exists = item_exists
        
        if zone_selected and zone_selected != "Tất cả":
            prompt_text = "Loại máy bay"
        if zone_selected and aircraft_selected != "Tất cả" and ac_exists and desc_exists and desc_selected == "Tất cả":
            prompt_text = "Mô tả chi tiết"
        if zone_selected and aircraft_selected != "Tất cả" and item_exists and (desc_selected != "Tất cả" or not desc_exists) and item_selected == "Tất cả":
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
            """, unsafe_allow_html=True
        )

