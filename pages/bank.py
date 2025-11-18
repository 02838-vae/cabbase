# -*- coding: utf-8 -*-
import streamlit as st
from docx import Document
import re
import math
import pandas as pd
import base64
import os
import random

# ====================================================
# ⚙️ HÀM HỖ TRỢ VÀ FILE I/O
# ====================================================
def clean_text(s: str) -> str:
    if s is None:
        return ""
    return re.sub(r'\s+', ' ', s).strip()

def read_docx_paragraphs(source):
    try:
        # Giả định file nằm cùng thư mục với script
        doc = Document(os.path.join(os.path.dirname(__file__), source))
    except Exception as e:
        # Nếu không tìm thấy file, thử đọc trực tiếp (trường hợp chạy local)
        try:
             doc = Document(source)
        except Exception:
            return []
    return [p.text.strip() for p in doc.paragraphs if p.text.strip()]

def get_base64_encoded_file(file_path):
    """Mã hóa file ảnh sang base64 để sử dụng trong CSS."""
    fallback_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    try:
        # Tìm file trong cùng thư mục với script
        path_to_check = os.path.join(os.path.dirname(__file__), file_path)
        
        # Nếu không tìm thấy, thử đường dẫn tuyệt đối (trường hợp chạy local)
        if not os.path.exists(path_to_check) or os.path.getsize(path_to_check) == 0:
            path_to_check = file_path # Thử đường dẫn gốc
        
        if not os.path.exists(path_to_check) or os.path.getsize(path_to_check) == 0:
            return fallback_base64
            
        with open(path_to_check, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
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
            # Nếu đã có options, nghĩa là đã hết các đáp án -> lưu câu hỏi và bắt đầu câu mới
            if current["options"]:
                if current["question"] and current["options"]:
                    # Đảm bảo có đáp án, nếu không có thì lấy đáp án đầu tiên
                    if not current["answer"] and current["options"]:
                        current["answer"] = current["options"][0]
                    questions.append(current)
                current = {"question": clean_text(p), "options": [], "answer": ""}
            else:
                # Vẫn đang ở phần câu hỏi (chưa có options)
                if current["question"]:
                    current["question"] += " " + clean_text(p)
                else:
                    current["question"] = clean_text(p)
            continue

        # Có matches - nghĩa là có các đáp án a, b, c, d
        pre_text = p[:matches[0].start()].strip()
        
        if pre_text:
            # Có text trước đáp án đầu tiên
            if current["options"]:
                # Đã có options từ trước -> lưu câu cũ và bắt đầu câu mới
                if current["question"] and current["options"]:
                    if not current["answer"] and current["options"]:
                        current["answer"] = current["options"][0]
                    questions.append(current)
                current = {"question": clean_text(pre_text), "options": [], "answer": ""}
            else:
                # Chưa có options -> đây là phần cuối của câu hỏi
                if current["question"]:
                    current["question"] += " " + clean_text(pre_text)
                else:
                    current["question"] = clean_text(pre_text)

        # Xử lý tất cả các đáp án trong dòng này
        for i, m in enumerate(matches):
            s = m.end()
            e = matches[i + 1].start() if i + 1 < len(matches) else len(p)
            opt_body = clean_text(p[s:e])
            letter = m.group('letter').lower()
            opt = f"{letter}. {opt_body}"
            current["options"].append(opt)
            if m.group("star"):
                current["answer"] = opt

    # Lưu câu hỏi cuối cùng
    if current["question"] and current["options"]:
        if not current["answer"] and current["options"]:
            current["answer"] = current["options"][0]
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
        # Bỏ qua dòng Ref (tài liệu tham khảo)
        if re.match(r'^\s*Ref', p, re.I):
            continue

        matches = list(opt_pat.finditer(p))
        
        if not matches:
            # Không có đáp án trong dòng này
            if current["options"]:
                # Đã có options rồi -> lưu câu hỏi cũ và bắt đầu câu mới
                if current["question"] and current["options"]:
                    if not current["answer"] and current["options"]:
                        current["answer"] = current["options"][0]
                    questions.append(current)
                current = {"question": clean_text(p), "options": [], "answer": ""}
            else:
                # Vẫn đang ở phần câu hỏi
                if current["question"]:
                    current["question"] += " " + clean_text(p)
                else:
                    current["question"] = clean_text(p)
            continue

        # Có matches - có các đáp án
        first_match = matches[0]
        pre_text = p[:first_match.start()].strip()
        
        if pre_text:
            # Có text trước đáp án đầu tiên
            if current["options"]:
                # Đã có options -> lưu câu cũ và bắt đầu câu mới
                if current["question"] and current["options"]:
                    if not current["answer"] and current["options"]:
                        current["answer"] = current["options"][0]
                    questions.append(current)
                current = {"question": clean_text(pre_text), "options": [], "answer": ""}
            else:
                # Chưa có options -> đây là phần cuối câu hỏi
                if current["question"]:
                    current["question"] += " " + clean_text(pre_text)
                else:
                    current["question"] = clean_text(pre_text)

        # Xử lý tất cả các đáp án trong dòng
        for i, m in enumerate(matches):
            s = m.end()
            e = matches[i+1].start() if i+1 < len(matches) else len(p)
            opt_body = clean_text(p[s:e])
            letter = m.group("letter").lower()
            option = f"{letter}. {opt_body}"
            current["options"].append(option)
            if m.group("star"):
                current["answer"] = option

    # Lưu câu hỏi cuối cùng
    if current["question"] and current["options"]:
        if not current["answer"] and current["options"]:
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

# === CSS ĐÃ TỐI ƯU CHO FONT VÀ KHOẢNG CÁCH ===
css_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Oswald:wght@400;500;600;700&display=swap');

/* ✅ KEYFRAMES */
@keyframes colorShift {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

@keyframes scrollRight {{
    0% {{ transform: translateX(100%); }}
    100% {{ transform: translateX(-100%); }}
}}

/* ======================= FULL SCREEN & BACKGROUND ======================= */
html, body, .stApp {{
    height: 100% !important;
    min-height: 100vh !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: auto;
    position: relative;
}}

/* BACKGROUND - ÁP DỤNG FILTER ĐÚNG CÁCH */
.stApp {{
    background: url("data:image/jpeg;base64,{img_pc_base64}") no-repeat center top fixed !important;
    background-size: cover !important;
    font-family: 'Oswald', sans-serif !important;
    filter: sepia(0.1) brightness(0.95) contrast(1.05) saturate(1.1) !important;
}}

/* Mobile Background */
@media (max-width: 767px) {{
    .stApp {{
        background: url("data:image/jpeg;base64,{img_mobile_base64}") no-repeat center top scroll !important;
        background-size: cover !important;
    }}
}}

/* NỘI DUNG KHÔNG BỊ LÀM MỜ */
[data-testid="stAppViewContainer"],
[data-testid="stMainBlock"],
.main,
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
footer,
#MainMenu {{
    background-color: transparent !important;
    height: 0 !important;
    display: none !important;
    visibility: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
}}

h1, h2 {{ visibility: hidden; height: 0; margin: 0; padding: 0; }}

/* ======================= NÚT VỀ TRANG CHỦ ======================= */
#back-to-home-btn-container {{
    position: static;
    margin: 15px 0 0 15px;
    z-index: 100;
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

/* ======================= TIÊU ĐỀ CHẠY LỚN ======================= */
#main-title-container {{
    position: static;
    margin-top: 20px;
    left: 0;
    width: 100%;
    height: 10vh;
    overflow: hidden;
    z-index: 100;
    pointer-events: none;
    background-color: transparent;
    display: flex;
    align-items: center;
}}

#main-title-container h1 {{
    visibility: visible !important;
    height: auto !important;
    font-family: 'Playfair Display', serif;
    font-size: 3.5vw;
    margin: 0;
    padding: 0;
    font-weight: 900;
    letter-spacing: 5px;
    white-space: nowrap;
    display: inline-block;
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
        top: 70px; 
    }}
    #main-title-container h1 {{
        font-size: 6.5vw;
        animation: scrollRight 12s linear infinite, colorShift 8s ease infinite;
    }}
}}

/* ======================= TẠO KHOẢNG TRỐNG CHO NỘI DUNG CHÍNH ======================= */
.main > div:first-child {{
    padding-top: 200px !important;
    padding-left: 1rem;
    padding-right: 1rem;
    padding-bottom: 2rem !important; 
}}

@media (max-width: 768px) {{
    .main > div:first-child {{
        padding-top: 180px !important;
    }}
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
    visibility: visible !important;
    height: auto !important;
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
    }}
}}

/* ======================= STYLE DROPDOWN (Giá trị bên trong đã là Oswald) ======================= */
div.stSelectbox label p, div[data-testid*="column"] label p {{
    color: #00FF00 !important; 
    font-size: 1.25rem !important;
    font-weight: bold;
    text-shadow: 0 0 5px rgba(0,255,0,0.5);
    font-family: 'Oswald', sans-serif !important; 
}}

.stSelectbox div[data-baseweb="select"] {{
    background-color: rgba(0, 0, 0, 0.7);
    border: 1px solid #00FF00;
    border-radius: 8px;
}}

.stSelectbox div[data-baseweb="select"] div[data-testid="stTextInput"] {{
    color: #FFFFFF !important;
}}

/* ======================= STYLE CÂU HỎI & ĐÁP ÁN (ĐÃ CHỈNH SỬA) ======================= */
/* CHỈNH SỬA: Font Oswald, Bỏ làm đậm (400), Giảm padding/margin (khoảng cách) */
div[data-testid="stMarkdownContainer"] p {{
    color: #ffffff !important;
    font-weight: 400 !important; /* Bỏ làm đậm */
    font-size: 1.2em !important;
    font-family: 'Oswald', sans-serif !important; /* Thay font */
    text-shadow: none !important; 
    background-color: transparent; 
    padding: 5px 15px; /* Giảm padding trên/dưới */
    border-radius: 8px;
    margin-bottom: 5px; /* Giảm khoảng cách giữa các câu */
}}

.stRadio label {{
    color: #f9f9f9 !important;
    font-size: 1.1em !important;
    font-weight: 400 !important; /* Bỏ làm đậm */
    font-family: 'Oswald', sans-serif !important; /* Thay font */
    text-shadow: none !important;
    background-color: transparent; 
    padding: 2px 12px; /* Giảm padding trên/dưới */
    border-radius: 6px;
    display: inline-block;
    margin: 1px 0 !important; /* Giảm khoảng cách giữa các lựa chọn */
}}

/* NÚT BẤM */
.stButton>button {{
    background-color: #a89073 !important;
    color: #ffffff !important;
    border-radius: 8px;
    font-size: 1.1em !important;
    font-weight: 600 !important;
    font-family: 'Oswald', sans-serif !important; /* Đổi font nút bấm */
    box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.4);
    transition: all 0.2s ease;
    border: none !important;
    padding: 10px 20px !important;
}}

.stButton>button:hover {{
    background-color: #8c765f !important;
    box-shadow: 3px 3px 8px rgba(0, 0, 0, 0.6);
}}

/* DÀN NGANG DROPDOWN */
[data-testid="stHorizontalBlock"] [data-testid="stSelectbox"] {{
    flex: 1;
    min-width: 0;
}}

/* Giảm khoảng cách giữa các câu hỏi/phân cách */
.stMarkdown > div > hr {{
    margin-top: 10px;
    margin-bottom: 10px;
}}

</style>
"""

st.markdown(css_style, unsafe_allow_html=True)

# ====================================================
# 🏷️ GIAO DIỆN HEADER CỐ ĐỊNH VÀ TIÊU ĐỀ
# ====================================================

# --- NÚT VỀ TRANG CHỦ (FIXED) ---
st.markdown("""
<div id="back-to-home-btn-container">
    <a id="manual-home-btn" href="/?skip_intro=1" target="_self">
        🏠 Về Trang Chủ
    </a>
</div>
""", unsafe_allow_html=True)

# --- TIÊU ĐỀ CHẠY LỚN (FIXED) ---
main_title_text = "Tổ Bảo Dưỡng Số 1"
st.markdown(f'<div id="main-title-container"><h1>{main_title_text}</h1></div>', unsafe_allow_html=True)

# --- TIÊU ĐỀ PHỤ ---
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
    st.error(f"❌ Không đọc được câu hỏi nào từ file **{source}**. Vui lòng đảm bảo file có sẵn.")
    st.stop() 

# --- Xử lý Reset khi đổi Ngân hàng ---
if st.session_state.get('last_bank_choice') != bank_choice:
    st.session_state.current_group_idx = 0
    st.session_state.submitted = False
    st.session_state.last_bank_choice = bank_choice
    st.rerun()

# --- Xử lý Nhóm câu hỏi ---
group_size = 10
total = len(questions)

if total > 0:
    groups = [f"Câu {i*group_size+1}-{min((i+1)*group_size, total)}" for i in range(math.ceil(total/group_size))]
    
    if st.session_state.current_group_idx >= len(groups):
        st.session_state.current_group_idx = 0
    
    with col_group:
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
            # Giao diện làm bài
            for i, q in enumerate(batch, start=start+1):
                st.markdown(f"<p>{i}. {q['question']}</p>", unsafe_allow_html=True)
                # Dùng key là f"q_{i}" để lưu giá trị chọn của từng câu
                st.radio("", q["options"], key=f"q_{i}")
                st.markdown("---") # Phân cách câu hỏi
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

                # Hiển thị các lựa chọn với style theo kết quả
                for opt in q["options"]:
                    opt_clean = clean_text(opt)
                    # Thêm font-family: 'Oswald', sans-serif và font-weight: 400
                    style = "color:#f9f9f9; font-family: 'Oswald', sans-serif; font-weight:400; text-shadow: none; padding: 2px 12px; margin: 1px 0;" 
                    
                    if opt_clean == correct:
                        # Đáp án đúng (Màu xanh lá, đậm hơn)
                        style = "color:#00ff00; font-family: 'Oswald', sans-serif; font-weight:600; text-shadow: 0 0 3px rgba(0, 255, 0, 0.8); padding: 2px 12px; margin: 1px 0;"
                    elif opt_clean == clean_text(selected_opt):
                        # Đáp án đã chọn (Màu đỏ, đậm hơn)
                        style = "color:#ff3333; font-family: 'Oswald', sans-serif; font-weight:600; text-decoration: underline; text-shadow: 0 0 3px rgba(255, 0, 0, 0.8); padding: 2px 12px; margin: 1px 0;"
                    
                    st.markdown(f"<div style='{style}'>{opt}</div>", unsafe_allow_html=True)

                if is_correct:
                    st.success(f"✅ Đúng — Đáp án: {q['answer']}")
                    score += 1
                else:
                    st.error(f"❌ Sai — Đáp án đúng: {q['answer']}")
                
                # Giảm khoảng cách giữa các câu trong kết quả
                st.markdown('<div style="margin: 5px 0;">---</div>', unsafe_allow_html=True) 

            st.markdown(f'<div class="result-title"><h3>🎯 KẾT QUẢ: {score}/{len(batch)}</h3></div>', unsafe_allow_html=True)

            col_reset, col_next = st.columns(2)

            with col_reset:
                if st.button("🔄 Làm lại nhóm này"):
                    for i in range(start+1, end+1):
                        # Xóa giá trị đã chọn
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
