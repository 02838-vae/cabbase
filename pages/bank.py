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
    # Điều chỉnh regex để hỗ trợ dấu chấm/đóng ngoặc sau chữ cái
    opt_pat = re.compile(r'(?P<star>\*)?\s*(?P<letter>[A-Da-d])[\.\)]\s+')

    for p in paras:
        matches = list(opt_pat.finditer(p))
        
        if not matches:
            # Nếu không có matches
            if current["options"]:
                # Đã có options, nghĩa là đã hết các đáp án -> lưu câu hỏi và bắt đầu câu mới
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

        # Có matches - có các đáp án a, b, c, d
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
    # Điều chỉnh regex để hỗ trợ dấu chấm/đóng ngoặc sau chữ cái và không bắt các từ/số liền trước
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
# 🌟 HÀM MỚI - XEM TOÀN BỘ NGÂN HÀNG CÂU HỎI
# ====================================================
def display_all_questions(questions):
    st.markdown('<div class="result-title"><h3>📚 TOÀN BỘ NGÂN HÀNG CÂU HỎI</h3></div>', unsafe_allow_html=True)
    if not questions:
        st.warning("Không có câu hỏi nào để hiển thị.")
        return

    for i, q in enumerate(questions, start=1):
        st.markdown(f"<p style='color: #FFEA00; font-weight: 700;'>{i}. {q['question']}</p>", unsafe_allow_html=True)
        
        # Hiển thị các lựa chọn, tô màu đáp án đúng
        for opt in q["options"]:
            style = "color:#f9f9f9; font-family: 'Oswald', sans-serif; font-weight:400; text-shadow: none; padding: 2px 12px; margin: 1px 0;"
            if clean_text(opt) == clean_text(q["answer"]):
                style = "color:#00ff00; font-family: 'Oswald', sans-serif; font-weight:600; text-shadow: 0 0 3px rgba(0, 255, 0, 0.8); padding: 2px 12px; margin: 1px 0;"
            
            st.markdown(f"<div style='{style}'>{opt}</div>", unsafe_allow_html=True)
        
        st.markdown("---") # Phân cách câu hỏi

# ====================================================
# 🌟 HÀM MỚI - LÀM BÀI TEST 50 CÂU
# ====================================================
def get_random_questions(questions, count=50):
    """Lấy ngẫu nhiên 'count' câu hỏi từ danh sách."""
    if len(questions) <= count:
        return questions
    return random.sample(questions, count)

def display_test_mode(questions, bank_name, key_prefix="test"):
    TOTAL_QUESTIONS = 50
    PASS_RATE = 0.75
    
    # Khởi tạo trạng thái cho Test Mode
    # Dùng key_prefix dựa trên bank_name để đảm bảo trạng thái độc lập
    bank_slug = bank_name.split()[-1].lower()
    test_key_prefix = f"{key_prefix}_{bank_slug}"
    
    if f"{test_key_prefix}_started" not in st.session_state:
        st.session_state[f"{test_key_prefix}_started"] = False
    if f"{test_key_prefix}_submitted" not in st.session_state:
        st.session_state[f"{test_key_prefix}_submitted"] = False
    if f"{test_key_prefix}_questions" not in st.session_state:
        st.session_state[f"{test_key_prefix}_questions"] = []

    # Bắt đầu bài test
    if not st.session_state[f"{test_key_prefix}_started"]:
        st.markdown('<div class="result-title"><h3>📝 LÀM BÀI TEST 50 CÂU</h3></div>', unsafe_allow_html=True)
        st.info(f"Bài test sẽ gồm **{min(TOTAL_QUESTIONS, len(questions))}** câu hỏi được chọn ngẫu nhiên từ **{bank_name}**. Tỷ lệ Đạt (PASS) là **{int(PASS_RATE*100)}%** ({int(TOTAL_QUESTIONS * PASS_RATE)} câu đúng).")
        
        if len(questions) < TOTAL_QUESTIONS:
             st.warning(f"Chỉ có {len(questions)} câu hỏi trong ngân hàng này. Bài test sẽ dùng toàn bộ các câu hỏi có sẵn.")
        
        if st.button("🚀 Bắt đầu Bài Test", key=f"{test_key_prefix}_start_btn"):
            st.session_state[f"{test_key_prefix}_questions"] = get_random_questions(questions, TOTAL_QUESTIONS)
            st.session_state[f"{test_key_prefix}_started"] = True
            st.session_state[f"{test_key_prefix}_submitted"] = False
            # Clear các trạng thái khác
            st.session_state.current_mode = "test" 
            st.rerun()
        return

    # Hiển thị bài test
    if not st.session_state[f"{test_key_prefix}_submitted"]:
        st.markdown('<div class="result-title"><h3>⏳ ĐANG LÀM BÀI TEST</h3></div>', unsafe_allow_html=True)
        test_batch = st.session_state[f"{test_key_prefix}_questions"]
        
        for i, q in enumerate(test_batch, start=1):
            # Lưu key trong session state theo index của câu hỏi (i)
            st.markdown(f"<p>{i}. {q['question']}</p>", unsafe_allow_html=True)
            st.radio("", q["options"], key=f"{test_key_prefix}_q_{i}")
            st.markdown("---") 
            
        if st.button("✅ Nộp bài Test", key=f"{test_key_prefix}_submit_btn"):
            st.session_state[f"{test_key_prefix}_submitted"] = True
            st.rerun()
            
    # Hiển thị kết quả bài test
    else:
        st.markdown('<div class="result-title"><h3>🎉 KẾT QUẢ BÀI TEST</h3></div>', unsafe_allow_html=True)
        test_batch = st.session_state[f"{test_key_prefix}_questions"]
        score = 0
        
        for i, q in enumerate(test_batch, start=1):
            selected_opt = st.session_state.get(f"{test_key_prefix}_q_{i}")
            correct = clean_text(q["answer"])
            is_correct = clean_text(selected_opt) == correct

            st.markdown(f"<p>{i}. {q['question']}</p>", unsafe_allow_html=True)
            
            # Hiển thị các lựa chọn với style theo kết quả
            for opt in q["options"]:
                opt_clean = clean_text(opt)
                style = "color:#f9f9f9; font-family: 'Oswald', sans-serif; font-weight:400; text-shadow: none; padding: 2px 12px; margin: 1px 0;" 
                
                if opt_clean == correct:
                    # Đáp án đúng (Màu xanh lá, đậm hơn)
                    style = "color:#00ff00; font-family: 'Oswald', sans-serif; font-weight:600; text-shadow: 0 0 3px rgba(0, 255, 0, 0.8); padding: 2px 12px; margin: 1px 0;"
                elif opt_clean == clean_text(selected_opt):
                    # Đáp án đã chọn (Màu đỏ, đậm hơn)
                    style = "color:#ff3333; font-family: 'Oswald', sans-serif; font-weight:600; text-decoration: underline; text-shadow: 0 0 3px rgba(255, 0, 0, 0.8); padding: 2px 12px; margin: 1px 0;"
                
                st.markdown(f"<div style='{style}'>{opt}</div>", unsafe_allow_html=True)

            if is_correct:
                score += 1
            
            st.info(f"Đáp án đúng: **{q['answer']}**", icon="💡")
            # Giảm khoảng cách giữa các câu trong kết quả
            st.markdown('<div style="margin: 5px 0;">---</div>', unsafe_allow_html=True) 
        
        # Đánh giá kết quả
        total_q = len(test_batch)
        pass_threshold = total_q * PASS_RATE
        
        st.markdown(f'<div class="result-title"><h3>🎯 KẾT QUẢ: {score}/{total_q}</h3></div>', unsafe_allow_html=True)

        if score >= pass_threshold:
            st.balloons()
            st.success(f"🎊 **CHÚC MỪNG!** Bạn đã ĐẠT (PASS) bài test với **{score}** câu đúng (>= {int(pass_threshold)} câu).")
        else:
            st.error(f"😔 **KHÔNG ĐẠT (FAIL)**. Bạn cần thêm {int(pass_threshold) - score} câu đúng nữa để đạt.")

        if st.button("🔄 Làm lại Bài Test", key=f"{test_key_prefix}_restart_btn"):
            for i in range(1, total_q + 1):
                # Xóa giá trị đã chọn
                st.session_state.pop(f"{test_key_prefix}_q_{i}", None) 
            st.session_state[f"{test_key_prefix}_started"] = False
            st.session_state[f"{test_key_prefix}_submitted"] = False
            st.session_state[f"{test_key_prefix}_questions"] = []
            st.rerun()

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

/* ======================= FULL SCREEN & BACKGROUND ======================= */
html, body, .stApp {{
    height: 100% !important;
    min-height: 100vh !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: auto;
    position: relative;
}}

/* BACKGROUND - ÁP DỤNG FILTER VINTAGE/BLUR */
.stApp {{
    background: url("data:image/jpeg;base64,{img_pc_base64}") no-repeat center top fixed !important;
    background-size: cover !important;
    font-family: 'Oswald', sans-serif !important;
    /* Hiệu ứng Vintage: Mờ nhẹ (blur 1px), ngả màu sepia (0.5), độ tương phản thấp hơn (0.9), độ bão hòa cao hơn (1.2) */
    filter: blur(1px) sepia(0.5) brightness(0.9) contrast(0.95) saturate(1.2) !important;
    transition: filter 0.5s ease;
}}

/* Mobile Background */
@media (max-width: 767px) {{
    .stApp {{
        background: url("data:image/jpeg;base64,{img_mobile_base64}") no-repeat center top scroll !important;
        background-size: cover !important;
    }}
}}

/* NỘI DUNG KHÔNG BỊ LÀM MỜ VÀ NỔI LÊN TRÊN */
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
    filter: none !important; /* ĐÃ SỬA: Đảm bảo loại bỏ filter cho nội dung chính */
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

h1, h2 {{ visibility: hidden;
    height: 0; margin: 0; padding: 0; }}

/* ======================= HEADER CONTAINER (Mới) ======================= */
/* Container cố định cho nút và tiêu đề */
#fixed-header-container {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    z-index: 100;
    background-color: transparent; /* ĐÃ SỬA: Loại bỏ vùng nền đen */
    box-shadow: none; /* ĐÃ SỬA: Loại bỏ đổ bóng của vùng đen */
    padding: 10px 0;
}}

/* ======================= NÚT VỀ TRANG CHỦ (Tĩnh) ======================= */
#back-to-home-btn-container {{
    position: static;
    margin: 0 15px 10px 15px; /* Giảm margin dưới cho tiêu đề chạy lên */
    z-index: 110;
    pointer-events: auto;
}}

a#manual-home-btn {{
    background-color: #a89073; /* Màu nâu vintage */
    color: #FFEA00;
    border: 2px solid #FFEA00;
    padding: 8px 18px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 15px;
    transition: all 0.3s;
    cursor: pointer;
    font-family: 'Oswald', sans-serif;
    text-decoration: none;
    display: inline-block;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
}}

a#manual-home-btn:hover {{
    background-color: #FFEA00;
    color: black;
    transform: scale(1.05);
}}

/* ======================= TIÊU ĐỀ CHẠY LỚN (Nằm dưới nút) ======================= */
#main-title-container {{
    position: static;
    width: 100%;
    height: auto;
    overflow: hidden;
    pointer-events: none;
    background-color: transparent;
    display: flex;
    align-items: center;
    padding: 0 15px;
}}

#main-title-container h1 {{
    visibility: visible !important;
    height: auto !important;
    font-family: 'Playfair Display', serif;
    font-size: 3vw;
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
    width: 100%;
    /* Đảm bảo chạy hết chiều rộng */
    text-align: center;
}}

@media (max-width: 768px) {{
    #main-title-container h1 {{
        font-size: 6.5vw;
        animation: scrollRight 12s linear infinite, colorShift 8s ease infinite;
    }}
}}

/* ======================= TẠO KHOẢNG TRỐNG CHO NỘI DUNG CHÍNH ======================= */
/* Điều chỉnh padding top để nội dung chính nằm dưới fixed header */
.main > div:first-child {{
    padding-top: 150px !important;
    padding-left: 1rem;
    padding-right: 1rem;
    padding-bottom: 2rem !important; 
}}

@media (max-width: 768px) {{
    .main > div:first-child {{
        padding-top: 130px !important;
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
    /* ĐÃ SỬA: Điều chỉnh text-shadow để font chữ rõ nét hơn, không bị quá nhòe */
    text-shadow: 0 0 5px rgba(0, 0, 0, 0.8); 
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

/* ======================= STYLE CÂU HỎI & ĐÁP ÁN ======================= */
div[data-testid="stMarkdownContainer"] p {{
    color: #ffffff !important;
    font-weight: 400 !important; 
    font-size: 1.2em !important;
    font-family: 'Oswald', sans-serif !important; 
    text-shadow: none !important; 
    background-color: transparent; 
    padding: 5px 15px; 
    border-radius: 8px;
    margin-bottom: 5px; 
}}

.stRadio label {{
    color: #f9f9f9 !important;
    font-size: 1.1em !important;
    font-weight: 400 !important;
    font-family: 'Oswald', sans-serif !important; 
    text-shadow: none !important;
    background-color: transparent; 
    padding: 2px 12px; 
    border-radius: 6px;
    display: inline-block;
    margin: 1px 0 !important;
}}

/* NÚT BẤM */
.stButton>button {{
    background-color: #a89073 !important;
    color: #ffffff !important;
    border-radius: 8px;
    font-size: 1.1em !important;
    font-weight: 600 !important;
    font-family: 'Oswald', sans-serif !important; 
    box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.4);
    transition: all 0.2s ease;
    border: none !important;
    padding: 10px 20px !important;
    width: 100%; 
}}

.stButton>button:hover {{
    background-color: #8c765f !important;
    box-shadow: 3px 3px 8px rgba(0, 0, 0, 0.6);
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

st.markdown("""
<div id="fixed-header-container">
    <div id="back-to-home-btn-container">
        <a id="manual-home-btn" href="/?skip_intro=1" target="_self">
            🏠 Về Trang Chủ
        </a>
    </div>
    <div id="main-title-container">
        <h1>Tổ Bảo Dưỡng Số 1</h1>
    </div>
</div>
""", unsafe_allow_html=True)

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
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "group"
if "last_bank_choice" not in st.session_state:
    st.session_state.last_bank_choice = "----" # KHỞI TẠO AN TOÀN BẰNG CHUỖI

# --- 1. Lựa chọn Ngân hàng ---
# Thêm giá trị mặc định "----"
BANK_OPTIONS = ["----", "Ngân hàng Kỹ thuật", "Ngân hàng Luật"]
bank_choice = st.selectbox(
    "Chọn ngân hàng:", 
    BANK_OPTIONS,
    index=BANK_OPTIONS.index(st.session_state.get('bank_choice_val', '----')),
    key="bank_selector_master"
)
# Lưu giá trị đã chọn để duy trì trạng thái dropdown
st.session_state.bank_choice_val = bank_choice

# --- Xử lý Reset khi đổi Ngân hàng ---
if st.session_state.get('last_bank_choice') != bank_choice and bank_choice != "----":
    # Reset toàn bộ trạng thái liên quan đến hiển thị nội dung
    st.session_state.current_group_idx = 0
    st.session_state.submitted = False
    st.session_state.current_mode = "group" # Quay về chế độ nhóm
    
    # Lấy tên ngân hàng cũ một cách an toàn để xóa trạng thái test
    last_bank_name = st.session_state.get('last_bank_choice')
    
    # Đảm bảo last_bank_name là một chuỗi có thể split được
    if not isinstance(last_bank_name, str) or last_bank_name == "----":
        last_bank_name = "null bank" 
        
    bank_slug_old = last_bank_name.split()[-1].lower()
    
    # Reset trạng thái Test Mode cũ
    st.session_state.pop(f"test_{bank_slug_old}_started", None)
    st.session_state.pop(f"test_{bank_slug_old}_submitted", None)
    st.session_state.pop(f"test_{bank_slug_old}_questions", None)
    
    st.session_state.last_bank_choice = bank_choice
    st.rerun()

# --- 2. Xử lý logic hiển thị các thành phần còn lại ---
if bank_choice != "----":
    source = "cabbank.docx" if "Kỹ thuật" in bank_choice else "lawbank.docx"

    # Load questions
    questions = parse_cabbank(source) if "Kỹ thuật" in bank_choice else parse_lawbank(source)
    if not questions:
        st.error(f"❌ Không đọc được câu hỏi nào từ file **{source}**.")
        st.stop() 
    
    total = len(questions)
    
    # --- 2.1. Dropdown Chọn nhóm câu (chế độ Luyện tập theo nhóm) ---
    if st.session_state.current_mode == "group":
        st.markdown('<div class="result-title" style="margin-top: 0px;"><h3>Luyện tập theo nhóm (10 câu/nhóm)</h3></div>', unsafe_allow_html=True)
        
        group_size = 10
        if total > 0:
            groups = [f"Câu {i*group_size+1}-{min((i+1)*group_size, total)}" for i in range(math.ceil(total/group_size))]
            
            if st.session_state.current_group_idx >= len(groups):
                st.session_state.current_group_idx = 0
            
            selected = st.selectbox("Chọn nhóm câu:", groups, index=st.session_state.current_group_idx, key="group_selector")
            
            new_idx = groups.index(selected)
            if st.session_state.current_group_idx != new_idx:
                st.session_state.current_group_idx = new_idx
                st.session_state.submitted = False
                st.session_state.current_mode = "group" # Đảm bảo chế độ là group
                st.rerun()

            idx = st.session_state.current_group_idx
            start, end = idx * group_size, min((idx+1) * group_size, total)
            batch = questions[start:end]
            
            # --- 2.2. Hiển thị 2 nút chức năng mới (Dàn cột dọc) ---
            st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
            col_all_bank, col_test = st.columns(2)
            
            with col_all_bank:
                if st.button("📖 Hiển thị toàn bộ ngân hàng", key="btn_show_all"):
                    st.session_state.current_mode = "all"
                    st.rerun()

            with col_test:
                if st.button("🏆 Làm bài Test 50 câu", key="btn_start_test"):
                    # Chỉ chuyển mode, logic test sẽ chạy ở cuối
                    st.session_state.current_mode = "test"
                    # Reset trạng thái test cũ (nếu có)
                    bank_slug_new = bank_choice.split()[-1].lower()
                    test_key_prefix = f"test_{bank_slug_new}"
                    st.session_state.pop(f"{test_key_prefix}_started", None)
                    st.session_state.pop(f"{test_key_prefix}_submitted", None)
                    st.session_state.pop(f"{test_key_prefix}_questions", None)
                    st.rerun()

            st.markdown("---")
            
            # --- 2.3. Logic hiển thị bài làm theo nhóm (như cũ) ---
            if batch:
                if not st.session_state.submitted:
                    # Giao diện làm bài
                    for i, q in enumerate(batch, start=start+1):
                        st.markdown(f"<p>{i}. {q['question']}</p>", unsafe_allow_html=True)
                        st.radio("", q["options"], key=f"q_{i}")
                        st.markdown("---")
                    if st.button("✅ Nộp bài", key="submit_group"):
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
                            style = "color:#f9f9f9; font-family: 'Oswald', sans-serif; font-weight:400; text-shadow: none; padding: 2px 12px; margin: 1px 0;" 
                            
                            if opt_clean == correct:
                                style = "color:#00ff00; font-family: 'Oswald', sans-serif; font-weight:600; text-shadow: 0 0 3px rgba(0, 255, 0, 0.8); padding: 2px 12px; margin: 1px 0;"
                            elif opt_clean == clean_text(selected_opt):
                                style = "color:#ff3333; font-family: 'Oswald', sans-serif; font-weight:600; text-decoration: underline; text-shadow: 0 0 3px rgba(255, 0, 0, 0.8); padding: 2px 12px; margin: 1px 0;"
                            
                            st.markdown(f"<div style='{style}'>{opt}</div>", unsafe_allow_html=True)

                        if is_correct:
                            st.success(f"✅ Đúng — Đáp án: {q['answer']}")
                            score += 1
                        else:
                            st.error(f"❌ Sai — Đáp án đúng: {q['answer']}")
                        
                        st.markdown('<div style="margin: 5px 0;">---</div>', unsafe_allow_html=True) 

                    st.markdown(f'<div class="result-title"><h3>🎯 KẾT QUẢ: {score}/{len(batch)}</h3></div>', unsafe_allow_html=True)

                    col_reset, col_next = st.columns(2)

                    with col_reset:
                        if st.button("🔄 Làm lại nhóm này", key="reset_group"):
                            for i in range(start+1, end+1):
                                st.session_state.pop(f"q_{i}", None) 
                            st.session_state.submitted = False
                            st.rerun()
                  
                    with col_next:
                        if st.session_state.current_group_idx < len(groups) - 1:
                            if st.button("➡️ Tiếp tục nhóm sau", key="next_group"):
                                st.session_state.current_group_idx += 1
                                st.session_state.submitted = False
                                st.rerun()
                        else:
                            st.info("🎉 Đã hoàn thành tất cả các nhóm câu hỏi!")
            else:
                st.warning("Không có câu hỏi trong nhóm này.")
        else:
            st.warning("Không có câu hỏi nào trong ngân hàng này.")

    # --- 3. Xử lý logic hiển thị các chế độ khác ---
    elif st.session_state.current_mode == "all":
        # Nút Quay lại để trở về chế độ Group
        if st.button("⬅️ Quay lại chế độ Luyện tập theo nhóm"):
            st.session_state.current_mode = "group"
            st.rerun()
        st.markdown("---")
        display_all_questions(questions)
        
    elif st.session_state.current_mode == "test":
        # Nút Quay lại để trở về chế độ Group
        if st.button("⬅️ Quay lại chế độ Luyện tập theo nhóm"):
            st.session_state.current_mode = "group"
            st.rerun()
        st.markdown("---")
        display_test_mode(questions, bank_choice)
