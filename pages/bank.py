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
# ====================================================
def clean_text(s: str) -> str:
    if s is None:
        return ""
    # Thay thế ký tự ngắt dòng/tab ẩn bằng khoảng trắng
    return re.sub(r'\s+', ' ', s).strip()

def read_docx_paragraphs(source):
    # Hàm đọc nội dung file docx
    try:
        # Giả định file docx nằm trong cùng thư mục
        doc = Document(os.path.join(os.path.dirname(__file__), source))
    except Exception as e:
        # st.error(f"Không thể đọc file .docx: {e}")
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
        # print(f"Lỗi khi mã hóa ảnh {file_path}: {str(e)}")
        return fallback_base64

# ====================================================
# 🧩 PARSER NGÂN HÀNG KỸ THUẬT (CABBANK)
# ====================================================
def parse_cabbank(source):
    paras = read_docx_paragraphs(source)
    if not paras:
        return []

    questions = []
    current = {"question": "", "options": [], "answer": ""}
  
    opt_pat = re.compile(r'(?P<star>\*)?\s*(?P<letter>[A-Da-d])[\.\)]\s+')

    for p in paras:
        matches = list(opt_pat.finditer(p))
        if not matches:
            if current["options"]:
                if current["question"] and current["options"]:
                    questions.append(current)
                current = {"question": clean_text(p), "options": [], "answer": ""}
            else:
                current["question"] += " " + clean_text(p)
            continue

        pre_text = p[:matches[0].start()].strip()
        if pre_text:
            if current["options"]:
                if current["question"] and current["options"]:
                    questions.append(current)
                current = {"question": clean_text(pre_text), "options": [], "answer": ""}
            else:
                current["question"] = clean_text(pre_text)

        for i, m in enumerate(matches):
            s, e = m.end(), matches[i + 1].start() if i + 1 < len(matches) else len(p)
            opt_body = clean_text(p[s:e])
            opt = f"{m.group('letter').lower()}. {opt_body}"
            current["options"].append(opt)
            if m.group("star"):
                current["answer"] = opt

    if current["question"] and current["options"]:
        questions.append(current)

    return questions


# ====================================================
# 🧩 PARSER NGÂN HÀNG LUẬT (LAWBANK)
# ====================================================
def parse_lawbank(source):
    paras = read_docx_paragraphs(source)
    if not paras:
        return []

    questions = []
 
    current = {"question": "", "options": [], "answer": ""}
    opt_pat = re.compile(r'(?<![A-Za-z0-9/])(?P<star>\*)?\s*(?P<letter>[A-Da-d])[\.\)]\s+')

    for p in paras:
        if re.match(r'^\s*Ref', p, re.I):
            continue

        matches = list(opt_pat.finditer(p))
        if not matches:
            if current["options"]:
                if current["question"] and current["options"]:
                    if not current["answer"]:
                        current["answer"] = current["options"][0]
                    questions.append(current)
                current = {"question": clean_text(p), "options": [], "answer": ""}
            else:
                current["question"] += " " + clean_text(p)
            continue

        first_match = matches[0]
        pre_text = p[:first_match.start()].strip()
        if pre_text:
            if current["options"]:
                if current["question"] and current["options"]:
                    if not current["answer"]:
                        current["answer"] = current["options"][0]
                    questions.append(current)
                current = {"question": clean_text(pre_text), "options": [], "answer": ""}
            else:
                current["question"] += " " + clean_text(pre_text)

        for i, m in enumerate(matches):
            s = m.end()
            e = matches[i+1].start() if i+1 < len(matches) else len(p)
            opt_body = clean_text(p[s:e])
            letter = m.group("letter").lower()
       
            option = f"{letter}. {opt_body}"
            current["options"].append(option)
            if m.group("star"):
                current["answer"] = option

        if current["question"] and current["options"]:
            if not current["answer"]:
                current["answer"] = current["options"][0]
            questions.append(current)
            current = {"question": "", "options": [], "answer": ""}


    if current["question"] and current["options"]:
        if not current["answer"]:
            current["answer"] = current["options"][0]
        questions.append(current)

    return questions


# ====================================================
# 🖥️ GIAO DIỆN STREAMLIT
# ====================================================
st.set_page_config(page_title="Ngân hàng trắc nghiệm", layout="wide")

# === KHAI BÁO VÀ CHUYỂN ĐỔI ẢNH NỀN SANG BASE64 ===
PC_IMAGE_FILE = "bank_PC.jpg"
MOBILE_IMAGE_FILE = "bank_mobile.jpg"

img_pc_base64 = get_base64_encoded_file(PC_IMAGE_FILE)
img_mobile_base64 = get_base64_encoded_file(MOBILE_IMAGE_FILE)


# === CSS ĐÃ TỐI ƯU VÀ FIX FONT CHỮ SÁNG CỐ ĐỊNH ===
css_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Crimson+Text:wght@400;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;700&display=swap');

/* ======================= FULL SCREEN FIX & BACKGROUND (Vintage Look) ======================= */
html, body, .stApp {{
    height: 100% !important;
    min-height: 100vh !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: auto; 
    position: relative;
}}

/* BACKGROUND CHÍNH - Giữ filter vintage nhưng không quá mạnh */
.stApp::before {{
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: url("data:image/jpeg;base64,{img_pc_base64}") no-repeat center top fixed;
    background-size: cover;
    /* Filter vintage nhẹ, KHÔNG LÀM MỜ NỘI DUNG */
    filter: sepia(0.1) brightness(0.95) contrast(1.05) saturate(1.1) blur(1px);
    z-index: -1;
}}

/* Overlay tối để text nổi bật hơn */
.stApp::after {{
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(rgba(10, 10, 10, 0.4), rgba(5, 5, 5, 0.5));
    z-index: -1;
}}

.stApp {{
    background-color: transparent !important;
}}

/* Background Mobile */
@media (max-width: 767px) {{
    .stApp::before {{
        background: url("data:image/jpeg;base64,{img_mobile_base64}") no-repeat center top scroll;
        background-size: cover;
        background-attachment: scroll;
    }}
}}

/* NỘI DUNG SẮC NÉT (Đã loại bỏ filter trên nội dung) */
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

/* Ẩn Streamlit UI components */
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
h1, h2 {{ visibility: hidden; height: 0; margin: 0; padding: 0; }}

/* ======================= NÚT VỀ TRANG CHỦ (Fixed) ======================= */
#back-to-home-btn-container {{
    position: fixed;
    top: 15px;
    left: 15px;
    z-index: 1001;
}}

a#manual-home-btn {{
    background-color: rgba(0, 0, 0, 0.85);
    color: #FFEA00;
    border: 2px solid #FFEA00;
    padding: 10px 20px;
    border-radius: 8px;
    font-weight: bold;
    font-size: 16px;
    transition: all 0.3s;
    cursor: pointer;
    font-family: 'Oswald', sans-serif;
    text-decoration: none;
    display: inline-block;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
}}

a#manual-home-btn:hover {{
    background-color: #FFEA00;
    color: black;
    transform: scale(1.05);
}}

/* ======================= TIÊU ĐỀ TĨNH (Fixed, Loại bỏ Animation) ======================= */
#main-title-container {{
    position: fixed;
    top: 75px; /* Dưới nút 'VỀ TRANG CHỦ' */
    left: 0;
    width: 100%;
    height: auto;
    text-align: center; /* Căn giữa */
    z-index: 50; 
    pointer-events: none; 
    background-color: transparent;
}}

#main-title-container h1 {{
    visibility: visible;
    height: auto;
    font-family: 'Playfair Display', serif;
    font-size: 3.5vw;
    margin: 0 auto; /* Căn giữa */
    padding: 0;
    font-weight: 900;
    letter-spacing: 5px;
    white-space: nowrap;
    display: inline-block;
    /* ✅ ĐƠN GIẢN HÓA MÀU SẮC */
    color: #00FF00 !important; 
    background: transparent !important;
    -webkit-text-fill-color: #00FF00 !important;
    text-shadow: 0 0 10px rgba(0,255,0,0.8); /* Giữ bóng nhẹ cho nổi bật */
}}

@media (max-width: 768px) {{
    #main-title-container {{ top: 70px; }}
    #main-title-container h1 {{
        font-size: 6.5vw;
    }}
}}

/* ======================= TẠO KHOẢNG TRỐNG CHO NỘI DUNG CHÍNH ======================= */
[data-testid="stMainBlock"] > div:nth-child(1) {{
    padding-top: 20vh !important; 
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

/* ======================= STYLE DROPDOWN ======================= */
/* Label (Tiêu đề dropdown): Màu xanh #00FF00 */
div.stSelectbox label p, div[data-testid*="column"] label p {{
    color: #00FF00 !important; 
    font-size: 1.25rem !important;
    font-weight: bold;
    text-shadow: 0 0 5px rgba(0,255,0,0.5);
    font-family: 'Oswald', sans-serif !important; 
}}

/* Khung dropdown */
.stSelectbox div[data-baseweb="select"] {{
    background-color: rgba(0, 0, 0, 0.7);
    border: 1px solid #00FF00; /* Viền xanh */
    border-radius: 8px;
}}

/* Text trong dropdown */
.stSelectbox div[data-baseweb="select"] div[data-testid="stTextInput"] {{
    color: #FFFFFF !important;
}}

/* ======================= STYLE CÂU HỎI & ĐÁP ÁN (FIX SÁNG CỐ ĐỊNH & KHOẢNG CÁCH) ======================= */

/* Câu hỏi & Nội dung: ✅ Xóa text-shadow */
div[data-testid="stMarkdownContainer"] p {{
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1.2em !important;
    font-family: 'Crimson Text', serif; 
    text-shadow: none !important; /* ✅ XÓA ĐỔ BÓNG HOÀN TOÀN để chữ sắc nét và cố định */
    background-color: transparent; 
    padding: 10px 15px;
    border-radius: 8px;
    margin-bottom: 10px;
}}

/* Câu trả lời (Radio button label): ✅ Xóa text-shadow, giảm padding/margin */
.stRadio label {{
    color: #f9f9f9 !important;
    font-size: 1.1em !important;
    font-weight: 600 !important;
    font-family: 'Crimson Text', serif; 
    text-shadow: none !important; /* ✅ XÓA ĐỔ BÓNG HOÀN TOÀN */
    background-color: transparent; 
    padding: 4px 12px; /* GIẢM PADDING */
    border-radius: 6px;
    display: inline-block;
    margin: 2px 0 !important; /* ✅ GIẢM MARGIN: Đảm bảo các câu trả lời gần nhau */
}}

/* Nút bấm */
.stButton>button {{
    background-color: #a89073 !important;
    color: #ffffff !important;
    border-radius: 8px;
    font-size: 1.1em !important;
    font-weight: 600 !important;
    font-family: 'Crimson Text', serif; 
    box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.4);
    transition: all 0.2s ease;
    border: none !important;
    padding: 10px 20px !important;
}}
.stButton>button:hover {{
    background-color: #8c765f !important;
    box-shadow: 3px 3px 8px rgba(0, 0, 0, 0.6);
}}

/* Dàn ngang dropdown */
[data-testid="stHorizontalBlock"] [data-testid="stSelectbox"] {{
    flex: 1;
    min-width: 0;
}}

</style>
"""

st.markdown(css_style, unsafe_allow_html=True)


# ====================================================
# 🏷️ GIAO DIỆN HEADER CỐ ĐỊNH VÀ TIÊU ĐỀ
# ====================================================

# --- NÚT VỀ TRANG CHỦ ---
st.markdown("""
<div id="back-to-home-btn-container">
    <a id="manual-home-btn" href="/?skip_intro=1" target="_self">
        🏠 Về Trang Chủ
    </a>
</div>
""", unsafe_allow_html=True)

# --- HIỂN THỊ TIÊU ĐỀ CHẠY LỚN (ĐÃ CHUYỂN THÀNH TĨNH VÀ CĂN GIỮA) ---
main_title_text = "Tổ Bảo Dưỡng Số 1"
st.markdown(f'<div id="main-title-container"><h1>{main_title_text}</h1></div>', unsafe_allow_html=True)

# --- TIÊU ĐỀ PHỤ "NGÂN HÀNG TRẮC NGHIỆM" ---
st.markdown('<div id="sub-static-title"><h2>NGÂN HÀNG TRẮC NGHIỆM</h2></div>', unsafe_allow_html=True)


# ====================================================
# 🧭 NỘI DUNG ỨNG DỤNG
# ====================================================

# Khởi tạo trạng thái
if "current_group_idx" not in st.session_state:
    st.session_state.current_group_idx = 0
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# --- Lựa chọn Ngân hàng & Nhóm câu hỏi (Dàn ngang) ---
col_bank, col_group = st.columns(2)

with col_bank:
    bank_choice = st.selectbox("Chọn ngân hàng:", ["Ngân hàng Kỹ thuật", "Ngân hàng Luật"], 
key="bank_selector")
source = "cabbank.docx" if "Kỹ thuật" in bank_choice else "lawbank.docx"

# Load questions
questions = parse_cabbank(source) if "Kỹ thuật" in bank_choice else parse_lawbank(source)
if not questions:
    st.error("❌ Không đọc được câu hỏi nào. Vui lòng đảm bảo file .docx (cabbank.docx hoặc lawbank.docx) có sẵn.")
    st.stop() 

# --- Xử lý Reset khi đổi Ngân hàng ---
if st.session_state.get('last_bank_choice') != bank_choice:
    st.session_state.current_group_idx = 0
    st.session_state.submitted = False
    st.session_state.last_bank_choice = bank_choice
    st.rerun()

# --- Xử lý Nhóm câu hỏi (Nội dung chính) ---
group_size = 10
total = len(questions)

if total > 0:
    groups = [f"Câu {i*group_size+1}-{min((i+1)*group_size, total)}" for i in range(math.ceil(total/group_size))]
    
    if st.session_state.current_group_idx >= len(groups):
        st.session_state.current_group_idx = 0
    
    # Selectbox Nhóm câu hỏi - Đặt trong cột thứ hai để dàn ngang
    with col_group:
        selected = st.selectbox("Chọn nhóm câu:", groups, index=st.session_state.current_group_idx, key="group_selector")
    
    new_idx = groups.index(selected)
    if st.session_state.current_group_idx != new_idx:
        st.session_state.current_group_idx = new_idx
        st.session_state.submitted = False
        # Không cần rerun ở đây

    idx = st.session_state.current_group_idx
    start, end = idx * group_size, min((idx+1) * group_size, total)
    batch = questions[start:end]

    if batch:
        if not st.session_state.submitted:
            # Giao diện làm bài
            for i, q in enumerate(batch, start=start+1):
                st.markdown(f"<p>{i}. {q['question']}</p>", unsafe_allow_html=True)
                st.radio("", q["options"], key=f"q_{i}")
                st.markdown("---")
            if st.button("✅ Nộp bài"):
                st.session_state.submitted = True
            
            st.rerun()
        else:
            # Giao diện kết quả
            score = 0
            for i, q in enumerate(batch, start=start+1):
                selected_opt = st.session_state.get(f"q_{i}")
                correct = clean_text(q["answer"])

                is_correct = clean_text(selected_opt) == correct

                st.markdown(f"<p>{i}. {q['question']}</p>", unsafe_allow_html=True)

                for opt in q["options"]:
                    opt_clean = clean_text(opt)
  
                    # Đảm bảo font sáng sủa và sắc nét
                    style = "color:#f9f9f9; text-shadow: none;" 
                    if opt_clean == correct:
                        style = "color:#00ff00; font-weight:700; text-shadow: 0 0 3px rgba(0, 255, 0, 0.8);" # Giữ bóng nhẹ chỉ trên đáp án đúng
                    elif opt_clean == clean_text(selected_opt):
                        style = "color:#ff3333; font-weight:700; text-decoration: underline; text-shadow: 0 0 3px rgba(255, 0, 0, 0.8);" # Giữ bóng nhẹ chỉ trên đáp án sai
                    
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
                    for i in range(start+1, end+1):
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
