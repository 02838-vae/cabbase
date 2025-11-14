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
            # Giả định file gốc là ở thư mục cha của thư mục hiện tại (nếu đang ở pages)
            path_to_check = os.path.join(os.path.dirname(os.path.dirname(__file__)), file_path)
        
    if not os.path.exists(path_to_check) or os.path.getsize(path_to_check) == 0:
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=" # Transparent 1x1
    try:
        with open(path_to_check, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        st.error(f"Lỗi khi đọc file {file_path}: {str(e)}")
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="


# --- KHAI BÁO MEDIA ---
pn_bg_base64 = get_base64_encoded_file("bg_partnumber.jpg")
pn_bg_mobile_base64 = get_base64_encoded_file("bg_partnumber_mobile.jpg")


# --- CSS CHÍNH CHO TRANG PART NUMBER (ĐÃ SỬA VỊ TRÍ TIÊU ĐỀ) ---
css = f"""
/* 1. Reset và Font */
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@100;300;400;700&display=swap');
* {{
    font-family: 'Roboto', sans-serif;
}}

/* 2. Background chính */
.stApp {{
    background: url("data:image/jpeg;base64,{pn_bg_base64}") no-repeat center top fixed !important;
    background-size: cover !important;
}}

/* 3. Tùy chỉnh Streamlit mặc định */
#MainMenu, footer {{visibility: hidden;}}
.stSidebar, .st-emotion-cache-1c9vj0f, .st-emotion-cache-1c9vj0f {{ /* Ẩn sidebar và các thành phần không cần thiết */
    visibility: hidden !important;
    width: 0 !important;
}}

/* ✅ SỬA ĐỔI: ĐẨY NỘI DUNG XUỐNG THẤP HƠN */
.main > div:first-child {{
    padding-top: 450px !important; /* ✅ ĐÃ TĂNG: Đẩy nội dung (bao gồm tiêu đề phụ) xuống thấp hơn */
    padding-left: 20px;
    padding-right: 20px;
}}

@media (max-width: 768px) {{
    .stApp {{
        background: url("data:image/jpeg;base64,{pn_bg_mobile_base64}") no-repeat center top scroll !important;
        background-size: cover !important;
    }}
    .main > div:first-child {{ 
        padding-top: 300px !important; /* ✅ ĐÃ TĂNG: Đẩy nội dung xuống thấp hơn trên Mobile */
    }}
}}

/* ✅ TIÊU ĐỀ PHỤ TĨNH */
#sub-static-title {{
    position: static;
    margin-top: 20px;
    margin-bottom: 30px;
    z-index: 90;
    background: transparent !important;
    text-align: center;
}}
#sub-static-title h2 {{
    font-size: 3rem;
    color: #00FF00;
    text-shadow: 0 0 10px #00FF00, 0 0 5px #000;
    margin: 0;
}}

/* ✅ NÚT VỀ TRANG CHỦ */
#back-to-home-btn-container {{
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 1000;
}}

/* Style cơ bản cho nút */
#manual-home-btn {{
    text-decoration: none;
    background-color: #000;
    color: #00FF00;
    padding: 10px 20px;
    border-radius: 8px;
    border: 2px solid #00FF00;
    font-weight: bold;
    box-shadow: 0 0 10px #00FF00;
    transition: all 0.3s;
}}
#manual-home-btn:hover {{
    background-color: #00FF00;
    color: #000;
    box-shadow: 0 0 20px #00FF00;
}}
"""
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# --- TIÊU ĐỀ PHỤ - ĐẨY XUỐNG THẤP HƠN ---
st.markdown('<div id="sub-static-title"><h2>TRA CỨU PART NUMBER</h2></div>', unsafe_allow_html=True)

# ✅ NÚT VỀ TRANG CHỦ - BỎ HIỆU ỨNG REVEAL VÀ VIDEO 
# Link đã có /?skip_intro=1 để báo cho trang chính bỏ qua intro
st.markdown(""" 
<div id="back-to-home-btn-container"> 
<a id="manual-home-btn" href="/?skip_intro=1" target="_self"> 🏠 Về Trang Chủ </a> 
</div> 
""", unsafe_allow_html=True)


# --- LOGIC TRA CỨU PART NUMBER (GIỮ NGUYÊN) ---

# Giả lập dữ liệu tra cứu (thay thế bằng file Excel/CSV của bạn)
data = {
    'Zone': ['F41', 'F41', 'F42', 'F42', 'F43'],
    'Aircraft': ['A320', 'A321', 'A320', 'A321', 'A320'],
    'Description': ['FLAP TRACK', 'FLAP TRACK', 'LANDING GEAR DOOR', 'LANDING GEAR DOOR', 'WHEEL'],
    'Item': ['Track 1', 'Track 2', 'LGD L/H', 'LGD R/H', 'Wheel Main'],
    'Part_Number': ['PN-F41-A320-1', 'PN-F41-A321-2', 'PN-F42-A320-3', 'PN-F42-A321-4', 'PN-F43-A320-5']
}
df = pd.DataFrame(data)

st.markdown("""
<div style="background: rgba(0, 0, 0, 0.7); padding: 20px; border-radius: 10px; margin-top: 20px; border: 1px solid rgba(0, 255, 0, 0.5);">
    <h3 style="color: #00FF00; margin-top: 0;">Bộ lọc Tra Cứu</h3>
""", unsafe_allow_html=True)

# Lấy danh sách các giá trị duy nhất
zones = df['Zone'].unique().tolist()
aircrafts = df['Aircraft'].unique().tolist()

col1, col2, col3, col4 = st.columns(4)

# 1. Chọn Zone
zone_selected = col1.selectbox("Chọn Zone", [''] + zones, index=0)

# Khởi tạo các biến để kiểm tra điều kiện
df_filtered = df
aircraft_selected = None
desc_selected = None
item_selected = None

# Lọc theo Zone
if zone_selected:
    df_filtered = df_filtered[df_filtered['Zone'] == zone_selected]
    ac_exists = not df_filtered['Aircraft'].empty
    
    # 2. Chọn Loại máy bay (nếu Zone đã chọn)
    if ac_exists:
        available_aircrafts = df_filtered['Aircraft'].unique().tolist()
        aircraft_selected = col2.selectbox("Chọn Loại máy bay", [''] + available_aircrafts, index=0)

        # Lọc theo Aircraft
        if aircraft_selected:
            df_filtered = df_filtered[df_filtered['Aircraft'] == aircraft_selected]
            desc_exists = not df_filtered['Description'].empty

            # 3. Chọn Mô tả chi tiết (nếu Aircraft đã chọn)
            if desc_exists:
                available_desc = df_filtered['Description'].unique().tolist()
                desc_selected = col3.selectbox("Chọn Mô tả chi tiết", [''] + available_desc, index=0)
                
                # Lọc theo Description
                if desc_selected:
                    df_filtered = df_filtered[df_filtered['Description'] == desc_selected]
            
            item_exists = not df_filtered['Item'].empty
            
            # 4. Chọn Item (nếu Mô tả đã chọn hoặc không có Mô tả)
            if item_exists:
                available_items = df_filtered['Item'].unique().tolist()
                item_selected = col4.selectbox("Chọn Item", [''] + available_items, index=0)

                # Lọc theo Item
                if item_selected:
                    df_filtered = df_filtered[df_filtered['Item'] == item_selected]


st.markdown("</div>", unsafe_allow_html=True)

# --- HIỂN THỊ KẾT QUẢ ---
all_criteria_met = (zone_selected and aircraft_selected) and \
                   (not desc_exists or (desc_exists and desc_selected)) and \
                   (not item_exists or (item_exists and item_selected))

if st.button("🔍 Tra Cứu", type="primary"):
    st.markdown("---")
    
    if all_criteria_met:
        st.markdown(f'<h4 style="color: #00FF00;">Kết quả tra cứu cho **{zone_selected} / {aircraft_selected}**</h4>', unsafe_allow_html=True)
        
        if not df_filtered.empty:
            # Chỉ hiển thị các cột quan trọng
            df_display = df_filtered[['Zone', 'Aircraft', 'Description', 'Item', 'Part_Number']].reset_index(drop=True)
            
            # Tùy chỉnh hiển thị DataFrame
            st.dataframe(
                df_display,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Part_Number": st.column_config.TextColumn(
                        "Part Number",
                        help="Part Number cần tìm",
                        max_chars=50,
                        width="medium"
                    ),
                }
            )
        else:
            st.markdown("---\r\n            st.warning(\"⚠️ **Không tìm thấy kết quả phù hợp** với các tiêu chí đã chọn.\")

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
# ... (Phần code còn lại của bạn) ...
