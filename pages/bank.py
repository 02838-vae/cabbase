# -*- coding: utf-8 -*-
import streamlit as st
from docx import Document
import re
import math
import pandas as pd
import base64
import os

# ====================================================
# ⚙️ HÀM HỖ TRỢ VÀ FILE I/O
# ... (Giữ nguyên các hàm hỗ trợ) ...

def clean_text(s: str) -> str:
    if s is None:
        return ""
    return re.sub(r'\s+', ' ', s).strip()

def read_docx_paragraphs(source):
    # Hàm đọc nội dung file docx
    try:
        doc = Document(os.path.join(os.path.dirname(__file__), source))
    except Exception as e:
        st.error(f"Không thể đọc file .docx: 
{e}")
        return []
    return [p.text.strip() for p in doc.paragraphs if p.text.strip()]

def get_base64_encoded_file(file_path):
    """Mã hóa file ảnh sang base64 để sử dụng trong CSS."""
    fallback_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    try:
        path_to_check = os.path.join(os.path.dirname(__file__), file_path)
        if not os.path.exists(path_to_check) or os.path.getsize(path_to_check) == 0:
            return fallback_base64
            
     
   with open(path_to_check, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"Lỗi khi mã hóa ảnh {file_path}: {str(e)}")
        return fallback_base64

# ... (Giữ nguyên parsers) ...

# ====================================================
# 🖥️ GIAO DIỆN STREAMLIT
# ====================================================
st.set_page_config(page_title="Ngân hàng trắc nghiệm", layout="wide")

# === KHAI BÁO VÀ CHUYỂN ĐỔI ẢNH NỀN SANG BASE64 ===
PC_IMAGE_FILE = "bank_PC.jpg"
MOBILE_IMAGE_FILE = "bank_mobile.jpg"

img_pc_base64 = get_base64_encoded_file(PC_IMAGE_FILE)
img_mobile_base64 = get_base64_encoded_file(MOBILE_IMAGE_FILE)


# === 
CSS: FIXED ALL ISSUES ======================================
st.markdown(f"""
<style>
/* Đã thêm font-family chung cho nội dung để đồng bộ */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Crimson+Text:wght@400;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;700&display=swap');

/* ✅ KEYFRAMES cho màu chữ và chạy từ phải qua trái */
@keyframes colorShift {{
    0% {{ background-position: 0% 50%;
}}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%;
}}
}}

@keyframes scrollRight {{
    0% {{ transform: translateX(100%); }}
    100% {{ transform: translateX(-100%);
}}
}}

/* ✅ FIX SỐ "1" CÙNG SIZE VỚI CHỮ */
@keyframes colorShiftUniform {{
    0% {{ background-position: 0% 50%;
}}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%;
}}
}}


/* ======================= FULL SCREEN FIX & BACKGROUND ======================= */

/* 1. Root elements: Đảm bảo full height */
html, body, .stApp {{
    height: 100% !important;
min-height: 100vh !important; 
    margin: 0 !important;
    padding: 0 !important;
    overflow: auto; 
    position: relative;
}}

/* 2. ✅ BACKGROUND MỜ HƠN VÀ NGẢ VÀNG XƯA CŨ */
.stApp::before {{
    content: '';
    position: fixed;
top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: url("data:image/jpeg;base64,{img_pc_base64}") no-repeat center top fixed;
    background-size: cover;
/* ✅ TĂNG ĐỘ MỜ VÀ THÊM MÀU VÀNG XƯA */
    filter: sepia(0.35) brightness(0.7) contrast(0.95) saturate(1.2) blur(2px);
z-index: -1;
}}

/* Overlay tối hơn để text nổi bật */
.stApp::after {{
    content: '';
    position: fixed;
top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(rgba(40, 30, 20, 0.4), rgba(30, 20, 10, 0.5));
    z-index: -1;
}}

.stApp {{
    background-color: transparent !important;
}}

/* 3. Background Mobile */
@media (max-width: 767px) {{
    .stApp::before {{
        background: url("data:image/jpeg;base64,{img_mobile_base64}") no-repeat center top scroll;
background-size: cover;
        background-attachment: scroll;
    }}
}}

/* 4. **NỘI DUNG SẮC NÉT**: Đưa nội dung lên Z-index cao hơn nền */
[data-testid="stAppViewContainer"],
[data-testid="stMainBlock"],
.st-emotion-cache-1oe02fs, 
.st-emotion-cache-1gsv8h, 
.st-emotion-cache-1aehpbu, 
.st-emotion-cache-1avcm0n {{
    background-color: transparent !important;
margin: 0 !important;
    padding: 0 !important; 
    z-index: 10; 
    position: relative;
    min-height: 100vh !important;
    filter: none !important;
}}

/* 5. Ẩn Header, Toolbar, Footer và Status Widget */
[data-testid="stHeader"], 
[data-testid="stToolbar"],
[data-testid="stStatusWidget"],
footer {{
    background-color: transparent !important;
height: 0 !important;
    display: none !important;
    visibility: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
}}

/* Ẩn các tiêu đề mặc định */
h1, h2 {{ visibility: hidden; height: 0; margin: 0; padding: 0;
}} 

/* ======================= TIÊU ĐỀ CHẠY (FIXED POSITION) ======================= */

/* ✅ TIÊU ĐỀ CHẠY TỪ PHẢI QUA TRÁI VÀ ĐỔI MÀU */
#main-title-container {{
    position: fixed;
top: 0;
    left: 0;
    width: 100%;
    height: 10vh;
    overflow: hidden;
    z-index: 50; 
    pointer-events: none; 
    background-color: transparent;
    display: flex;
    align-items: center;
}}

#main-title-container h1 {{
    visibility: visible;
    height: auto;
    font-family: 'Playfair Display', serif; /* Giữ nguyên font Playfair cho tiêu đề chính */
    font-size: 3.5vw;
    margin: 0;
    padding: 0;
font-weight: 900;
    letter-spacing: 5px;
    white-space: nowrap;
    display: inline-block;
    /* ✅ CHẠY TỪ PHẢI QUA TRÁI */
    animation: scrollRight 15s linear infinite;
/* ✅ ĐỔI MÀU LIÊN TỤC */
    background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
background-size: 400% 400%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    color: transparent;
    animation: scrollRight 15s linear infinite, colorShift 10s ease infinite;
text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.8);
}}

@media (max-width: 768px) {{
    #main-title-container {{
        height: 8vh;
}}
    
    #main-title-container h1 {{
        font-size: 6.5vw;
animation: scrollRight 12s linear infinite, colorShift 8s ease infinite;
    }}
}}

/* ======================= TẠO KHOẢNG TRỐNG CHO NỘI DUNG CHÍNH ======================= */
[data-testid="stMainBlock"] > div:nth-child(1) {{
    padding-top: 12vh !important;
padding-left: 1rem;
    padding-right: 1rem;
    padding-bottom: 2rem !important; 
}}

/* ======================= TIÊU ĐỀ PHỤ TĨNH & KẾT QUẢ ======================= */
#sub-static-title, .result-title {{
    position: static;
margin-top: 20px;
    margin-bottom: 30px;
    z-index: 90;
    background: transparent !important;
    text-align: center;
}}

#sub-static-title h2, .result-title h3 {{
    visibility: visible; 
    height: auto;
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    color: #FFEA00;
text-align: center;
    text-shadow: 0 0 15px #FFEA00, 0 0 30px rgba(255,234,0,0.8); 
    margin-bottom: 20px;
    filter: none !important;
}}

@media (max-width: 768px) {{
    #sub-static-title h2, .result-title h3 {{
        font-size: 1.5rem;
white-space: wrap; 
    }}
}}

/* ======================= ✅ CHỮ RÕ NÉT VÀ NỔI BẬT ======================= */

/* Câu hỏi & Nội dung - XÓA NỀN BAO QUANH, ĐỒNG BỘ FONT */
div[data-testid="stMarkdownContainer"] p {{
    color: #ffffff !important;
font-weight: 700 !important;
    font-size: 1.2em !important;
    font-family: 'Crimson Text', serif; /* Đã đồng bộ font cho nội dung chính */
text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.95), 0 0 10px rgba(0, 0, 0, 0.8) !important;
    filter: none !important;
-webkit-font-smoothing: antialiased !important;
    -moz-osx-font-smoothing: grayscale !important;
    background-color: transparent; /* <--- ĐÃ CHUYỂN SANG TRONG SUỐT (YÊU CẦU 3) */
    padding: 10px 15px;
    border-radius: 8px;
    margin-bottom: 10px;
}}

/* Câu trả lời (Radio button label) - XÓA NỀN BAO QUANH, ĐỒNG BỘ FONT */
.stRadio label {{
    color: #f9f9f9 !important;
font-size: 1.1em !important;
    font-weight: 600 !important;
    font-family: 'Crimson Text', serif; /* Đã đồng bộ font */
text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.9), 0 0 8px rgba(0, 0, 0, 0.7) !important;
    filter: none !important;
-webkit-font-smoothing: antialiased !important;
    -moz-osx-font-smoothing: grayscale !important;
    background-color: transparent; /* <--- ĐÃ CHUYỂN SANG TRONG SUỐT (YÊU CẦU 3) */
    padding: 8px 12px; /* Giữ padding để dễ bấm chọn */
    border-radius: 6px;
    display: inline-block;
margin: 5px 0;
}}

/* Nút bấm (Style vintage) - ĐỒNG BỘ FONT */
.stButton>button {{
    background-color: #a89073 !important; 
    color: #ffffff !important;
border-radius: 8px;
    font-size: 1.1em !important;
    font-weight: 600 !important;
    font-family: 'Crimson Text', serif; /* Đã đồng bộ font */
    box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.4);
transition: all 0.2s ease;
    border: none !important;
    padding: 10px 20px !important;
}}
.stButton>button:hover {{
    background-color: #8c765f !important;
box-shadow: 3px 3px 8px rgba(0, 0, 0, 0.6);
}}

/* SelectBox và Text Input - ĐỒNG BỘ FONT */
.stSelectbox label, .stTextInput label {{
    color: #ffffff !important;
font-weight: 600 !important;
    text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.9) !important;
    filter: none !important;
    font-family: 'Crimson Text', serif; /* <--- ĐÃ ĐỒNG BỘ FONT (YÊU CẦU 2) */
}}

/* Tab labels - ĐỒNG BỘ FONT */
.stTabs [data-baseweb="tab"] {{
    color: #ffffff !important;
    font-weight: 600 !important;
    font-family: 'Crimson Text', serif; /* <--- ĐÃ ĐỒNG BỘ FONT (YÊU CẦU 2) */
text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.9) !important;
}}

/* Info/Success/Error boxes */
.stAlert {{
    background-color: rgba(0, 0, 0, 0.3) !important;
color: #ffffff !important;
    font-weight: 600 !important;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.8) !important;
}}

/* Thêm rule cho Streamlit SelectBox container để hỗ trợ dàn ngang tốt hơn */
[data-testid="stHorizontalBlock"] [data-testid="stSelectbox"] {{
    flex: 1;
    min-width: 0;
}}


</style>
""", unsafe_allow_html=True)


# ====================================================
# 🏷️ GIAO DIỆN HEADER CỐ ĐỊNH VÀ TIÊU ĐỀ
# ====================================================

# --- ✅ HIỂN THỊ TIÊU ĐỀ CHẠY LỚN (CHẠY TỪ PHẢI QUA TRÁI VÀ ĐỔI MÀU) ---
main_title_text = "Tổ Bảo Dưỡng Số 1"
st.markdown(f'<div id="main-title-container"><h1>{main_title_text}</h1></div>', unsafe_allow_html=True)

# --- TIÊU ĐỀ PHỤ "NGÂN HÀNG TRẮC NGHIỆM" ---
st.markdown('<div id="sub-static-title"><h2>NGÂN HÀNG TRẮC NGHIỆM</h2></div>', unsafe_allow_html=True)


# ====================================================
# 🧭 NỘI DUNG ỨNG DỤNG (ĐÃ CHỈNH SỬA LOGIC DÙNG st.columns)
# ====================================================

# Khởi tạo trạng thái
if "current_group_idx" not in st.session_state:
    st.session_state.current_group_idx = 0
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# --- Lựa chọn Ngân hàng (Yêu cầu 4) ---
col_bank, col_group = st.columns(2)

with col_bank:
    bank_choice = st.selectbox("Chọn ngân hàng:", ["Ngân hàng Kỹ thuật", "Ngân hàng Luật"], 
key="bank_selector")
source = "cabbank.docx" if "Kỹ thuật" in bank_choice else "lawbank.docx"

# Load questions
questions = parse_cabbank(source) if "Kỹ thuật" in bank_choice else parse_lawbank(source)
if not questions:
    st.error("❌ Không đọc được câu hỏi nào.
Vui lòng đảm bảo file .docx có sẵn.")
    st.stop() 

# --- Xử lý Reset khi đổi Ngân hàng ---
if st.session_state.get('last_bank_choice') != bank_choice:
    st.session_state.current_group_idx = 0
    st.session_state.submitted = False
    st.session_state.last_bank_choice = bank_choice
    st.rerun()

# --- Xử lý Nhóm câu hỏi ---
tab1, tab2 = st.tabs(["🧠 Làm bài", "🔍 Tra cứu toàn bộ câu hỏi"])

# ========== TAB 1 (Làm bài) ==========
with tab1:
    group_size = 10
    total = len(questions)

    if total > 0:
        groups 
= [f"Câu {i*group_size+1}-{min((i+1)*group_size, total)}" for i in range(math.ceil(total/group_size))]
        
        if st.session_state.current_group_idx >= len(groups):
            st.session_state.current_group_idx = 0
        
        # Selectbox Nhóm câu hỏi (Yêu cầu 4)
        with col_group:
            # Dropdown chỉ hiện khi đã có questions (đã chọn Ngân hàng)
            selected = st.selectbox("Chọn nhóm câu:", groups, index=st.session_state.current_group_idx, key="group_selector")
        
        new_idx = groups.index(selected)
        if st.session_state.current_group_idx != new_idx:
        
    st.session_state.current_group_idx = new_idx
            st.session_state.submitted = False

        idx = st.session_state.current_group_idx
        start, end = idx * group_size, min((idx+1) * group_size, total)
        batch = questions[start:end]

        if batch:
            if not st.session_state.submitted:
                for i, q in 
enumerate(batch, start=start+1):
                    st.markdown(f"<p>{i}.
{q['question']}</p>", unsafe_allow_html=True)
                    st.radio("", q["options"], key=f"q_{i}")
                    st.markdown("---")
                if st.button("✅ Nộp bài"):
                    st.session_state.submitted = True
                
    st.rerun()
            else:
                score = 0
                for i, q in enumerate(batch, start=start+1):
                    selected_opt = st.session_state.get(f"q_{i}")
                    correct = clean_text(q["answer"])
 
                   is_correct = clean_text(selected_opt) == correct

                    st.markdown(f"<p>{i}. {q['question']}</p>", unsafe_allow_html=True)

                    for opt in q["options"]:
                        opt_clean = clean_text(opt)
      
                  
                        if opt_clean == correct:
                            # Đã bỏ màu nền, chỉ giữ text-shadow cho nổi bật
                            style = "color:#00ff00;
font-weight:700; text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.95), 0 0 10px rgba(0, 255, 0, 0.6);"
                        elif opt_clean == clean_text(selected_opt):
                            # Đã bỏ màu nền, chỉ giữ text-shadow cho nổi bật
                            style = "color:#ff3333;
font-weight:700; text-decoration: underline; text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.95), 0 0 10px rgba(255, 0, 0, 0.6);"
                        else:
                            style = "color:#f9f9f9;
text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.9);"
                        st.markdown(f"<div style='{style}'>{opt}</div>", unsafe_allow_html=True)

                    if is_correct:
                        st.success(f"✅ Đúng — {q['answer']}")
                   
     score += 1
                    else:
                        st.error(f"❌ Sai — Đáp án đúng: {q['answer']}")
                    st.markdown("---")

                st.markdown(f'<div class="result-title"><h3>🎯 KẾT QUẢ: {score}/{len(batch)}</h3></div>', unsafe_allow_html=True)
  
              
                col_reset, col_next = st.columns(2)

                with col_reset:
                    if st.button("🔁 Làm lại nhóm này"):
                        for 
i in range(start+1, end+1):
                            st.session_state.pop(f"q_{i}", None)
                        st.session_state.submitted = False
                        st.rerun()
                
  
              with col_next:
                    if st.session_state.current_group_idx < len(groups) - 1:
                        if st.button("➡️ Tiếp tục nhóm sau"):
                            st.session_state.current_group_idx += 1
 
                           st.session_state.submitted = False 
                            st.rerun()
                    else:
                      
  st.info("🎉 Đã hoàn thành tất cả các nhóm câu hỏi!")
        else:
             st.warning("Không có câu hỏi trong nhóm này.")


# ========== TAB 2 (Tra cứu) ==========
with tab2:
    st.markdown("### 🔎 Tra cứu toàn bộ câu hỏi trong ngân hàng")
    if len(questions) > 0:
        df = pd.DataFrame([
            {
            
    "STT": i+1,
                "Câu hỏi": q["question"],
                "Đáp án A": q["options"][0] if len(q["options"])>0 else "",
                "Đáp án B": q["options"][1] if len(q["options"])>1 else "",
                "Đáp án C": q["options"][2] if len(q["options"])>2 else "",
        
        "Đáp án D": q["options"][3] if len(q["options"])>3 else "",
                "Đáp án đúng": q["answer"]
            } for i, q in enumerate(questions)
        ])

        keyword = st.text_input("🔍 Tìm theo từ khóa:").strip().lower()
        df_filtered = df[df.apply(lambda r: keyword in " ".join(r.values.astype(str)).lower(), axis=1)] if keyword else df

       
 st.write(f"Hiển thị {len(df_filtered)}/{len(df)} câu hỏi")
        st.dataframe(df_filtered, use_container_width=True)

        csv = df_filtered.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ Tải danh sách (CSV)", csv, "ngan_hang_cau_hoi.csv", "text/csv")
    else:
        st.info("Không có dữ liệu câu hỏi để tra cứu.")
}
