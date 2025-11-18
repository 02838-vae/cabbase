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
# 🧩 PARSER CHUNG CHO CẢ HAI NGÂN HÀNG (ĐÃ SỬA LỖI PHÂN TÍCH)
# ====================================================
def parse_quiz(source, bank_type):
    paras = read_docx_paragraphs(source)
    if not paras:
        return []

    questions = []
    current = {"question": "", "options": [], "answer": ""}
    # Universal option pattern: Tìm kiếm dấu * tùy chọn, theo sau là chữ cái A-D, dấu . hoặc )
    opt_pat = re.compile(r'(?P<star>\*)?\s*(?P<letter>[A-Da-d])[\.\)]\s*') 

    for p in paras:
        p = clean_text(p)
        if not p: continue
        
        # Bỏ qua dòng "Ref" trong Ngân hàng Luật
        if bank_type == "Law" and re.match(r'^Ref', p, re.I):
            continue

        matches = list(opt_pat.finditer(p))

        if matches:
            # Case 1: Đoạn văn chứa một hoặc nhiều đánh dấu đáp án.
            
            # 1. Trích xuất văn bản trước đáp án đầu tiên (potential question text or continuation of the last option)
            pre_text = p[:matches[0].start()].strip()
            
            if current["options"]:
                # Nếu đã có đáp án trước đó, văn bản này là phần nối tiếp của ĐÁP ÁN CUỐI CÙNG
                current["options"][-1] = clean_text(current["options"][-1] + " " + pre_text)
            elif pre_text:
                # Nếu chưa có đáp án, văn bản này là phần nối tiếp của CÂU HỎI
                current["question"] = clean_text(current["question"] + " " + pre_text)

            # 2. Trích xuất các đáp án từ matches
            for i, m in enumerate(matches):
                s = m.end()
                e = matches[i + 1].start() if i + 1 < len(matches) else len(p)
                opt_body = clean_text(p[s:e])
                
                # Chỉ thêm đáp án nếu nội dung không rỗng
                if opt_body:
                    opt = f"{m.group('letter').lower()}. {opt_body}"
                    current["options"].append(opt)
                    if m.group("star"):
                        current["answer"] = opt

            # 3. Xử lý phần văn bản còn lại sau đáp án cuối cùng (potential start of the next question)
            last_match = matches[-1]
            # Lấy toàn bộ văn bản còn lại sau khi kết thúc ký hiệu đáp án cuối cùng
            post_text = clean_text(p[last_match.end():]) 

            # Nếu có văn bản còn lại, câu hỏi hiện tại đã kết thúc
            if post_text:
                if current["question"] or current["options"]:
                    questions.append(current)
                
                # Bắt đầu câu hỏi mới với post_text là nội dung đầu tiên
                current = {"question": post_text, "options": [], "answer": ""} 
            
            # Nếu không có post_text, giữ nguyên current để chờ nội dung options/question tiếp theo
            
        else:
            # Case 2: Đoạn văn là văn bản thuần túy (không có đánh dấu đáp án).
            if current["options"]:
                # Nếu options đã được bắt đầu, đây là phần nối tiếp của ĐÁP ÁN CUỐI CÙNG (hỗ trợ options nhiều đoạn)
                current["options"][-1] = clean_text(current["options"][-1] + " " + p)
            elif current["question"]:
                # Nếu chỉ có câu hỏi, đây là phần nối tiếp của NỘI DUNG CÂU HỎI (hỗ trợ câu hỏi nhiều đoạn)
                current["question"] = clean_text(current["question"] + " " + p)
            else:
                # Nếu current trống, đây là dòng đầu tiên của một CÂU HỎI MỚI
                current["question"] = p
                
    # Final cleanup: Thêm câu hỏi cuối cùng nếu còn dữ liệu
    if current["question"] and current["options"]:
        questions.append(current)

    # Final check for missing answers
    for q in questions:
        # Nếu đáp án bị thiếu hoặc nội dung đáp án là thông báo lỗi từ parser cũ (phòng ngừa)
        if not q.get('answer') or "Không tìm thấy đáp án đúng" in q['answer']:
            q['answer'] = " (Không tìm thấy đáp án đúng được đánh dấu * trong file nguồn)"
            
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

# === CSS ĐÃ TỐI ƯU CHO FONT, KHOẢNG CÁCH VÀ KÍCH CỠ CHỮ ===
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

/* ======================= STYLE DROPDOWN ======================= */
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

/* ======================= STYLE CÂU HỎI & ĐÁP ÁN (ĐÃ GIẢM KÍCH CỠ) ======================= */
div[data-testid="stMarkdownContainer"] p {{
    color: #ffffff !important;
    font-weight: 400 !important;
    font-size: 1.1em !important; 
    font-family: 'Oswald', sans-serif !important;
    text-shadow: none !important; 
    background-color: transparent; 
    padding: 5px 15px;
    border-radius: 8px;
    margin-bottom: 5px;
}}

.stRadio label {{
    color: #f9f9f9 !important;
    font-size: 1.0em !important; 
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
}}

.stButton>button:hover {{
    background-color: #8c765f !important;
    box-shadow: 3px 3px 8px rgba(0, 0, 0, 0.6);
}}

/* DÃN NGANG DROPDOWN */
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
if "last_bank_choice" not in st.session_state:
    st.session_state.last_bank_choice = None


# --- Lựa chọn Ngân hàng & Nhóm câu hỏi (Dàn ngang) ---
col_bank, col_group = st.columns(2)

with col_bank:
    bank_choice = st.selectbox("Chọn ngân hàng:", ["Ngân hàng Kỹ thuật", "Ngân hàng Luật"], 
key="bank_selector")

bank_type = "Tech" if "Kỹ thuật" in bank_choice else "Law"
source = "cabbank.docx" if bank_type == "Tech" else "lawbank.docx"

# Load questions bằng hàm parse_quiz mới
questions = parse_quiz(source, bank_type)
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
    
    # Đảm bảo index nằm trong giới hạn
    if st.session_state.current_group_idx >= len(groups) or st.session_state.current_group_idx < 0:
        st.session_state.current_group_idx = 0
    
    current_index = st.session_state.current_group_idx
    
    with col_group:
        selected = st.selectbox("Chọn nhóm câu:", groups, index=current_index)

    # Kiểm tra nếu selectbox thay đổi (tức là người dùng chọn nhóm mới)
    new_idx = groups.index(selected)
    if st.session_state.current_group_idx != new_idx:
        st.session_state.current_group_idx = new_idx
        st.session_state.submitted = False
        # Streamlit sẽ tự rerender khi st.selectbox thay đổi

    idx = st.session_state.current_group_idx
    start, end = idx * group_size, min((idx+1) * group_size, total)
    batch = questions[start:end]

    if batch:
        if not st.session_state.submitted:
            # Giao diện làm bài
            for i, q in enumerate(batch, start=start+1):
                st.markdown(f"<p>{i}. {q['question']}</p>", unsafe_allow_html=True)
                # Dùng key là f"q_{i}" để lưu giá trị chọn của từng câu
                
                # Hiển thị lỗi nếu thiếu đáp án
                if not q['options']:
                    st.error("Câu hỏi này không có đáp án nào được tìm thấy trong file nguồn.")
                    st.markdown("---")
                    continue
                
                st.radio("", q["options"], key=f"q_{i}")
                st.markdown("---") # Phân cách câu hỏi
            
            if st.button("✅ Nộp bài"):
                st.session_state.submitted = True
                st.rerun()
        else:
            # Giao diện kết quả
            score = 0
            for i, q in enumerate(batch, start=start+1):
                if not q['options']:
                    st.markdown(f"<p>{i}. {q['question']}</p>", unsafe_allow_html=True)
                    st.error("Câu hỏi này không có đáp án nào được tìm thấy.")
                    st.markdown('<div style="margin: 5px 0;">---</div>', unsafe_allow_html=True)
                    continue
                    
                selected_opt = st.session_state.get(f"q_{i}")
                correct = clean_text(q["answer"])
                is_correct = clean_text(selected_opt) == correct and "Không tìm thấy" not in correct

                st.markdown(f"<p>{i}. {q['question']}</p>", unsafe_allow_html=True)

                # Hiển thị các lựa chọn với style theo kết quả
                for opt in q["options"]:
                    opt_clean = clean_text(opt)
                    style = "color:#f9f9f9; font-family: 'Oswald', sans-serif; font-weight:400; text-shadow: none; padding: 2px 12px; margin: 1px 0; font-size: 1.0em;" 
                    
                    if opt_clean == correct:
                        # Đáp án đúng
                        style = "color:#00ff00; font-family: 'Oswald', sans-serif; font-weight:600; text-shadow: 0 0 3px rgba(0, 255, 0, 0.8); padding: 2px 12px; margin: 1px 0; font-size: 1.0em;"
                    elif opt_clean == clean_text(selected_opt):
                        # Đáp án đã chọn
                        style = "color:#ff3333; font-family: 'Oswald', sans-serif; font-weight:600; text-decoration: underline; text-shadow: 0 0 3px rgba(255, 0, 0, 0.8); padding: 2px 12px; margin: 1px 0; font-size: 1.0em;"
                    
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
                    # Logic chuyển trang đã được xác nhận là đúng: cập nhật index và reran.
                    if st.button("➡️ Tiếp tục nhóm sau"):
                        st.session_state.current_group_idx += 1
                        st.session_state.submitted = False
                        st.rerun() # Buộc Streamlit cập nhật
                else:
                    st.info("🎉 Đã hoàn thành tất cả các nhóm câu hỏi!")
    else:
        st.warning("Không có câu hỏi trong nhóm này.")
