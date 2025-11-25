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
    
    # GIỮ NGUYÊN các pattern điền chỗ trống:
    # - 2-10 dấu chấm (có thể có space xen kẽ): .... hoặc . . .
    # - 2-10 gạch dưới (có thể có space xen kẽ): ____ hoặc __ __
    # - Ngoặc chứa các ký tự trên: (____) hoặc (__  __) → chuẩn hóa thành (____) 
    
    temp_s = s
    placeholders = {}
    counter = 0
    
    # BƯỚC 1: Xử lý ngoặc có nhiều space/ký tự → chuẩn hóa thành 4 spaces
    # VD: (__          __) → (____)
    temp_s = re.sub(r'\([\s._-]{2,}\)', '(    )', temp_s)  # Ngoặc đơn
    temp_s = re.sub(r'\[[\s._-]{2,}\]', '[    ]', temp_s)  # Ngoặc vuông
    
    # BƯỚC 2: Lưu các pattern điền chỗ trống còn lại
    standalone_patterns = [
        r'(?<!\S)([._])(?:\s*\1){1,9}(?!\S)',  # 2-10 dấu chấm/gạch dưới đứng một mình
        r'(\([_.-]{2,}\))',                   # Ngoặc chứa 2+ dấu chấm/gạch dưới (đã chuẩn hóa)
        r'(\[[_.-]{2,}\])'                    # Ngoặc vuông chứa 2+ dấu chấm/gạch dưới (đã chuẩn hóa)
    ]
    
    for pattern in standalone_patterns:
        matches = re.findall(pattern, temp_s)
        for match in matches:
            # Nếu là pattern dấu chấm/gạch dưới, match[0] là ký tự đầu tiên
            if isinstance(match, tuple):
                placeholder = match[0] + match[0] 
                full_match = match[0] + ''.join(re.findall(r'(?:\s*' + re.escape(match[0]) + r')', temp_s[temp_s.find(match[0])+1:]))
            else:
                placeholder = match 
                full_match = match
                
            key = f"__PH{counter}__"
            placeholders[key] = placeholder
            temp_s = temp_s.replace(full_match, key, 1)
            counter += 1

    # BƯỚC 3: Loại bỏ tất cả non-alphanumeric, whitespace và chuyển thành lowercase
    s_cleaned = re.sub(r'[^a-zA-Z0-9]', '', temp_s.lower())
    
    # BƯỚC 4: Hoàn trả các pattern điền chỗ trống
    for key, placeholder in placeholders.items():
        s_cleaned = s_cleaned.replace(re.sub(r'[^a-zA-Z0-9]', '', key.lower()), placeholder)
        
    return s_cleaned

def extract_questions_from_docx(docx_file):
    """
    Trích xuất câu hỏi và đáp án từ file DOCX theo format định sẵn:
    Câu hỏi 
    A. Đáp án 1
    B. Đáp án 2
    ...
    [Answer] Đáp án Đúng
    """
    doc = Document(docx_file)
    questions = []
    current_question = None
    options = []
    answer = None

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # Pattern kiểm tra đáp án: Bắt đầu bằng chữ cái + '.' hoặc ')', VD: A. , B)
        option_match = re.match(r'^[A-Z]\s*[.)]\s*(.*)', text)
        
        # Pattern kiểm tra đáp án đúng: [Answer] hoặc [ANSWER]
        answer_match = re.match(r'\[[Aa][Nn][Ss][Ww][Ee][Rr]\]\s*(.*)', text)

        if answer_match:
            # Gặp đáp án đúng
            answer_text = answer_match.group(1).strip()
            if current_question and answer_text:
                # Tìm đáp án đúng trong list options dựa trên clean_text
                found_answer = None
                for opt in options:
                    if clean_text(opt) == clean_text(answer_text):
                        found_answer = opt
                        break
                
                if found_answer:
                    questions.append({
                        "question": current_question,
                        "options": options,
                        "answer": found_answer
                    })
                
                # Reset
                current_question = None
                options = []
                answer = None
            else:
                st.warning(f"Bỏ qua đáp án đúng không có câu hỏi: {text}")

        elif option_match:
            # Gặp tùy chọn đáp án
            if current_question:
                options.append(option_match.group(1).strip())
            else:
                st.warning(f"Bỏ qua tùy chọn đáp án không có câu hỏi: {text}")

        else:
            # Gặp câu hỏi mới (khi options và answer đã reset)
            if current_question is None:
                current_question = text
            else:
                # Nếu đang có câu hỏi mà lại gặp text không phải option/answer, coi là phần tiếp theo của câu hỏi
                current_question += " " + text
                
    return questions

def group_questions(questions, group_size=20):
    """Chia câu hỏi thành các nhóm có kích thước bằng group_size."""
    groups = []
    for i in range(0, len(questions), group_size):
        groups.append(questions[i:i + group_size])
    return groups

# ====================================================
# 🌟 HÀM: XEM TOÀN BỘ CÂU HỎI
# ====================================================
def display_all_questions(questions):
    st.markdown('<div class="result-title"><h3>📚 TOÀN BỘ NGÂN HÀNG CÂU HỎI</h3></div>', unsafe_allow_html=True)
    if not questions:
        st.warning("Không có câu hỏi nào để hiển thị.")
        return 

    # Định nghĩa SHARP_OUTLINE (Đổ bóng đen sắc nét)
    SHARP_OUTLINE = "-1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000"

    for i, q in enumerate(questions, start=1):
        st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True)
        for opt in q["options"]:
            # Dùng clean_text để so sánh, bỏ qua khoảng trắng, ký tự ẩn
            if clean_text(opt) == clean_text(q["answer"]):
                # FIX 4: Đáp án đúng, chỉ dùng màu xanh lá và text-shadow, BỎ BOX/BACKGROUND
                color_style = f"color:#00ff00; text-shadow: {SHARP_OUTLINE}, 0 0 3px rgba(0, 255, 0, 0.8);"
                # Chỉ dùng thẻ <p> tag đơn giản, không dùng div/style tạo box
                st.markdown(f'<p style="font-weight: 700; font-size: 1.1rem; margin: 5px 0; {color_style}">{opt}</p>', unsafe_allow_html=True)
            else:
                # Đáp án thường
                color_style = f"color:white; text-shadow: {SHARP_OUTLINE};"
                st.markdown(f'<p style="font-weight: 500; font-size: 1.1rem; margin: 5px 0; {color_style}">{opt}</p>', unsafe_allow_html=True)

    st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)

# ====================================================
# 🌟 HÀM: CHẾ ĐỘ THI/KIỂM TRA (RANDOM)
# ====================================================
def display_test_mode(all_questions, bank_name, num_questions=20):
    test_key_prefix = "test_mode"
    st.markdown(f'<div class="result-title"><h3>📝 BÀI KIỂM TRA: {bank_name}</h3></div>', unsafe_allow_html=True)
    
    if not all_questions:
        st.warning("Không có câu hỏi nào để tạo bài kiểm tra.")
        return

    # Lấy hoặc tạo batch câu hỏi cho lần đầu tiên
    if f"{test_key_prefix}_batch" not in st.session_state:
        # Xáo trộn và chọn N câu hỏi
        st.session_state[f"{test_key_prefix}_batch"] = random.sample(all_questions, min(num_questions, len(all_questions)))
    
    test_batch = st.session_state[f"{test_key_prefix}_batch"]
    
    # Hiển thị form câu hỏi
    if not st.session_state.get(f"{test_key_prefix}_submitted", False):
        st.info(f"Vui lòng trả lời {len(test_batch)} câu hỏi dưới đây. Sau khi hoàn thành, nhấn nút **Nộp Bài**.")
        
        with st.form(key=f"{test_key_prefix}_form"):
            for i, q in enumerate(test_batch, start=1):
                # Tạo key duy nhất cho câu hỏi
                q_key = f"{test_key_prefix}_q_{i}_{hash(q['question'])}" 
                
                # Xáo trộn đáp án cho bài test
                shuffled_options = random.sample(q["options"], len(q["options"]))
                
                st.markdown(f'<div class="bank-question-text"><strong>{i}. {q["question"]}</strong></div>', unsafe_allow_html=True)
                
                # Streamlit radio button để chọn đáp án
                selected_answer = st.radio(
                    label="Chọn đáp án:",
                    options=shuffled_options,
                    key=q_key,
                    index=None, # Bắt đầu chưa chọn gì
                    label_visibility="collapsed"
                )
                # Lưu đáp án đã chọn vào session state
                if selected_answer is not None:
                    st.session_state[q_key] = selected_answer
                
                st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)

            submitted = st.form_submit_button("Nộp Bài và Xem Kết Quả")

            if submitted:
                # Kiểm tra xem người dùng đã trả lời hết chưa
                all_answered = True
                for i, q in enumerate(test_batch, start=1):
                    q_key = f"{test_key_prefix}_q_{i}_{hash(q['question'])}"
                    if st.session_state.get(q_key) is None:
                        all_answered = False
                        break
                
                if all_answered:
                    st.session_state[f"{test_key_prefix}_submitted"] = True
                    st.rerun()
                else:
                    st.error("⚠️ Vui lòng trả lời tất cả các câu hỏi trước khi nộp bài.")
    
    # --- PHẦN KẾT QUẢ ---
    if st.session_state.get(f"{test_key_prefix}_submitted", False):
        st.markdown('<div class="result-title"><h3>🎉 KẾT QUẢ BÀI TEST</h3></div>', unsafe_allow_html=True)
        score = 0
        SHARP_OUTLINE = "-1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000"

        for i, q in enumerate(test_batch, start=1):
            q_key = f"{test_key_prefix}_q_{i}_{hash(q['question'])}"
            user_answer = st.session_state.get(q_key)

            # Highlight đáp án đúng
            correct_opt_html = ""
            for opt in q["options"]:
                if clean_text(opt) == clean_text(q["answer"]):
                    # FIX 4: Chỉ dùng màu xanh lá và text-shadow, BỎ BOX/BACKGROUND
                    correct_color_style = f"color:#00ff00; text-shadow: {SHARP_OUTLINE}, 0 0 3px rgba(0, 255, 0, 0.8);"
                    correct_opt_html = f'<p style="font-weight: 700; margin: 0; {correct_color_style}">{opt}</p>'
                    break

            # Hiển thị câu hỏi
            st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True)
            
            # Hiển thị kết quả & đáp án người dùng
            if clean_text(user_answer) == clean_text(q["answer"]):
                score += 1
                result_text = '<font color="#00ff00">✅ **Chính xác!**</font>'
                user_style = f"color:#00ff00; font-weight: 700; text-shadow: {SHARP_OUTLINE}, 0 0 3px rgba(0, 255, 0, 0.8);"
                
                st.markdown(f'<p style="font-weight: 500; margin: 5px 0;">{result_text}</p>', unsafe_allow_html=True)
                # FIX 4: Không dùng box cho câu trả lời của người dùng.
                st.markdown(f'<p style="{user_style}">Đáp án của bạn: {user_answer}</p>', unsafe_allow_html=True)

            else:
                result_text = '<font color="#ff3333">❌ **Sai.** Đáp án đúng:</font>'
                user_style = f"color:#ff3333; font-weight: 700; text-shadow: {SHARP_OUTLINE}, 0 0 3px rgba(255, 0, 0, 0.8);"
                
                st.markdown(f'<p style="font-weight: 500; margin: 5px 0;">{result_text}</p>', unsafe_allow_html=True)
                # FIX 4: Không dùng box cho câu trả lời của người dùng.
                st.markdown(f'<p style="{user_style}">Đáp án của bạn: {user_answer}</p>', unsafe_allow_html=True)
                # Hiển thị đáp án đúng (đã bỏ box)
                st.markdown(correct_opt_html, unsafe_allow_html=True) 

            st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
        
        # Hiển thị tổng kết
        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
        st.markdown(f"""
            <div style='
                text-align: center; 
                padding: 15px; 
                background-color: #1f2a38; 
                border-radius: 10px;
                border: 2px solid #00FF00;
            '>
                <h2 style='color: #00FF00; margin: 0; text-shadow: 0 0 10px #00FF00;'>
                    SCORE: {score}/{len(test_batch)}
                </h2>
                <p style='color: white; margin: 5px 0 0;'>
                    Tỷ lệ: {score/len(test_batch)*100:.2f}%
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)

        # Nút Luyện tập lại
        col_retry, col_back = st.columns([1, 1])
        with col_retry:
            if st.button("🔄 Luyện tập lại (Bài mới)", key="retry_test"):
                # Reset state cho bài test
                st.session_state.pop(f"{test_key_prefix}_batch", None)
                st.session_state.pop(f"{test_key_prefix}_submitted", None)
                # Xóa câu trả lời cũ
                for i, q in enumerate(test_batch, start=1):
                    st.session_state.pop(f"{test_key_prefix}_q_{i}_{hash(q['question'])}", None)
                st.rerun()
        
        with col_back:
             if st.button("⬅️ Quay lại chế độ Luyện tập theo nhóm", key="back_to_group"):
                # Reset state cho bài test
                st.session_state.pop(f"{test_key_prefix}_batch", None)
                st.session_state.pop(f"{test_key_prefix}_submitted", None)
                st.session_state.current_mode = "group"
                st.rerun()


# ====================================================
# 🎨 CẤU HÌNH GIAO DIỆN VÀ MAIN APP
# ====================================================

# --- CẤU HÌNH BAN ĐẦU ---
st.set_page_config(page_title="Ngân Hàng Câu Hỏi", layout="wide", initial_sidebar_state="collapsed")

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

    /* Tiêu đề kết quả/chế độ */
    .result-title h3 {
        text-align: center;
        color: #FFFFE0;
        text-shadow: 0 0 5px #000;
        background-color: #1f2a38;
        padding: 10px;
        border-radius: 8px;
        border-left: 5px solid #00FF00;
        margin-bottom: 20px;
    }

    /* Câu hỏi */
    .bank-question-text {
        font-size: 1.2rem;
        font-weight: 600;
        margin-top: 15px;
        margin-bottom: 10px;
        padding-left: 10px;
        color: #FFFFFF;
        text-shadow: 0 0 3px #000;
    }
    
    /* Đáp án (bỏ box theo FIX 4) */
    .stRadio > label {
        padding: 5px 0;
        font-size: 1.1rem;
        color: white;
        font-weight: 500;
        text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;
    }

    /* Phân cách */
    .question-separator {
        border-top: 1px dashed #444;
        margin: 20px 0;
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

st.markdown('<div id="sub-static-title"><h2>NGÂN HÀNG CÂU HỎI</h2></div>', unsafe_allow_html=True)

# --- UPLOAD FILE ---
uploaded_file = st.file_uploader("Upload file ngân hàng câu hỏi (.docx):", type="docx")

if "questions" not in st.session_state:
    st.session_state.questions = []
if "groups" not in st.session_state:
    st.session_state.groups = []
if "current_group_idx" not in st.session_state:
    st.session_state.current_group_idx = 0
if "current_mode" not in st.session_state:
    # group: Luyện tập theo nhóm, test: Bài kiểm tra (random), all: Xem toàn bộ
    st.session_state.current_mode = "group"
if "bank_name" not in st.session_state:
    st.session_state.bank_name = ""

if uploaded_file is not None:
    # Kiểm tra xem file đã được upload và xử lý chưa
    if st.session_state.bank_name != uploaded_file.name:
        with st.spinner(f"Đang xử lý file {uploaded_file.name}..."):
            try:
                st.session_state.questions = extract_questions_from_docx(uploaded_file)
                st.session_state.groups = group_questions(st.session_state.questions, group_size=20)
                st.session_state.current_group_idx = 0
                st.session_state.bank_name = uploaded_file.name
                # Reset test mode
                st.session_state.pop("test_mode_batch", None)
                st.session_state.pop("test_mode_submitted", None)

            except Exception as e:
                st.error(f"Lỗi khi đọc file DOCX: {e}")
                st.session_state.questions = []
                st.session_state.groups = []
                st.session_state.bank_name = ""
    
    questions = st.session_state.questions
    groups = st.session_state.groups
    bank_name = st.session_state.bank_name

    # --- CHỌN CHẾ ĐỘ ---
    mode_cols = st.columns(3)
    
    with mode_cols[0]:
        if st.button("👥 Luyện tập theo nhóm (20 câu)", use_container_width=True):
            st.session_state.current_mode = "group"
            st.session_state.current_group_idx = 0 # Quay lại nhóm đầu tiên
            # Reset tất cả các câu trả lời
            for key in list(st.session_state.keys()):
                if key.startswith("q_") or key.startswith("test_mode"):
                    st.session_state.pop(key, None)
            st.session_state.submitted = False
            st.rerun()

    with mode_cols[1]:
        if st.button("📝 Bài kiểm tra (Random 20)", use_container_width=True):
            st.session_state.current_mode = "test"
            # Reset test mode
            st.session_state.pop("test_mode_batch", None)
            st.session_state.pop("test_mode_submitted", None)
            st.rerun()

    with mode_cols[2]:
        if st.button("📚 Xem toàn bộ đáp án", use_container_width=True):
            st.session_state.current_mode = "all"
            st.rerun()
            
    st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
    
    # --- HIỂN THỊ NỘI DUNG THEO CHẾ ĐỘ ---
    if st.session_state.current_mode == "group":
        if questions:
            if groups:
                
                current_group_idx = st.session_state.current_group_idx
                current_group = groups[current_group_idx]
                start_index = current_group_idx * 20
                
                st.markdown(f'<div class="result-title"><h3> Nhóm: {current_group_idx + 1} / {len(groups)} (Câu {start_index + 1} - {start_index + len(current_group)}) </h3></div>', unsafe_allow_html=True)

                if "submitted" not in st.session_state:
                    st.session_state.submitted = False

                if not st.session_state.submitted:
                    # Chế độ luyện tập: Form để trả lời
                    with st.form(key=f"group_{current_group_idx}_form"):
                        for i, q in enumerate(current_group, start=start_index + 1):
                            q_key = f"q_{i}_{hash(q['question'])}" 
                            # Xáo trộn đáp án
                            shuffled_options = random.sample(q["options"], len(q["options"]))

                            st.markdown(f'<div class="bank-question-text"><strong>{i}. {q["question"]}</strong></div>', unsafe_allow_html=True)
                            
                            selected_answer = st.radio(
                                label="Chọn đáp án:",
                                options=shuffled_options,
                                key=q_key,
                                index=None, # Bắt đầu chưa chọn gì
                                label_visibility="collapsed"
                            )
                            # Lưu đáp án đã chọn
                            if selected_answer is not None:
                                st.session_state[q_key] = selected_answer

                            st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
                        
                        submitted = st.form_submit_button("Nộp Bài và Xem Kết Quả")

                        if submitted:
                            # Kiểm tra xem đã trả lời hết chưa
                            all_answered = True
                            for i, q in enumerate(current_group, start=start_index + 1):
                                q_key = f"q_{i}_{hash(q['question'])}"
                                if st.session_state.get(q_key) is None:
                                    all_answered = False
                                    break
                            
                            if all_answered:
                                st.session_state.submitted = True
                                st.rerun()
                            else:
                                st.error("⚠️ Vui lòng trả lời tất cả các câu hỏi trong nhóm này trước khi nộp bài.")
                else:
                    # Chế độ xem kết quả: Hiển thị đáp án
                    score = 0
                    SHARP_OUTLINE = "-1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000"

                    for i, q in enumerate(current_group, start=start_index + 1):
                        q_key = f"q_{i}_{hash(q['question'])}"
                        user_answer = st.session_state.get(q_key)
                        
                        # Highlight đáp án đúng
                        correct_opt_html = ""
                        for opt in q["options"]:
                            if clean_text(opt) == clean_text(q["answer"]):
                                # FIX 4: Chỉ dùng màu xanh lá và text-shadow, BỎ BOX/BACKGROUND
                                correct_color_style = f"color:#00ff00; text-shadow: {SHARP_OUTLINE}, 0 0 3px rgba(0, 255, 0, 0.8);"
                                correct_opt_html = f'<p style="font-weight: 700; margin: 0; {correct_color_style}">{opt}</p>'
                                break

                        # Hiển thị câu hỏi
                        st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True)
                        
                        # Hiển thị kết quả & đáp án người dùng
                        if clean_text(user_answer) == clean_text(q["answer"]):
                            score += 1
                            result_text = '<font color="#00ff00">✅ **Chính xác!**</font>'
                            user_style = f"color:#00ff00; font-weight: 700; text-shadow: {SHARP_OUTLINE}, 0 0 3px rgba(0, 255, 0, 0.8);"
                            
                            st.markdown(f'<p style="font-weight: 500; margin: 5px 0;">{result_text}</p>', unsafe_allow_html=True)
                            # FIX 4: Không dùng box cho câu trả lời của người dùng.
                            st.markdown(f'<p style="{user_style}">Đáp án của bạn: {user_answer}</p>', unsafe_allow_html=True)
                        else:
                            result_text = '<font color="#ff3333">❌ **Sai.** Đáp án đúng:</font>'
                            user_style = f"color:#ff3333; font-weight: 700; text-shadow: {SHARP_OUTLINE}, 0 0 3px rgba(255, 0, 0, 0.8);"
                            
                            st.markdown(f'<p style="font-weight: 500; margin: 5px 0;">{result_text}</p>', unsafe_allow_html=True)
                            # FIX 4: Không dùng box cho câu trả lời của người dùng.
                            st.markdown(f'<p style="{user_style}">Đáp án của bạn: {user_answer}</p>', unsafe_allow_html=True)
                            # Hiển thị đáp án đúng (đã bỏ box)
                            st.markdown(correct_opt_html, unsafe_allow_html=True) 

                        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)

                    # Hiển thị tổng kết
                    st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
                    st.markdown(f"""
                        <div style='
                            text-align: center; 
                            padding: 15px; 
                            background-color: #1f2a38; 
                            border-radius: 10px;
                            border: 2px solid #00FF00;
                        '>
                            <h2 style='color: #00FF00; margin: 0; text-shadow: 0 0 10px #00FF00;'>
                                SCORE: {score}/{len(current_group)}
                            </h2>
                            <p style='color: white; margin: 5px 0 0;'>
                                Tỷ lệ: {score/len(current_group)*100:.2f}%
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
                    
                    # Nút điều hướng nhóm
                    col_prev, col_retry, col_next = st.columns([1, 1, 1])
                    with col_prev:
                        if st.session_state.current_group_idx > 0:
                            if st.button("⬅️ Quay lại nhóm trước", key="prev_group"):
                                st.session_state.current_group_idx -= 1
                                # Reset câu trả lời cho nhóm này (dùng index của nhóm cũ)
                                start = (st.session_state.current_group_idx) * 20
                                batch = groups[st.session_state.current_group_idx]
                                for i, q in enumerate(batch, start=start+1):
                                    st.session_state.pop(f"q_{i}_{hash(q['question'])}", None) 
                                st.session_state.submitted = False
                                st.rerun()
                        else: st.info("Đây là nhóm đầu tiên.")
                    
                    with col_retry:
                        if st.button("🔄 Luyện tập lại nhóm này", key="retry_group"):
                            # Reset câu trả lời cho nhóm hiện tại
                            start = st.session_state.current_group_idx * 20
                            batch = groups[st.session_state.current_group_idx]
                            for i, q in enumerate(batch, start=start+1):
                                st.session_state.pop(f"q_{i}_{hash(q['question'])}", None) 
                            st.session_state.submitted = False
                            st.rerun()
                    with col_next:
                        if st.session_state.current_group_idx < len(groups) - 1:
                            if st.button("➡️ Tiếp tục nhóm sau", key="next_group"):
                                st.session_state.current_group_idx += 1
                                st.session_state.submitted = False
                                st.rerun()
                        else: st.info("🎉 Đã hoàn thành tất cả các nhóm câu hỏi!")
            else: st.warning("Không có câu hỏi trong nhóm này.")
        else: st.warning("Không có câu hỏi nào trong ngân hàng này.")

    elif st.session_state.current_mode == "all":
        # Nút quay lại (nếu cần)
        if st.button("⬅️ Quay lại chế độ Luyện tập theo nhóm"):
            st.session_state.current_mode = "group"
            st.rerun()
        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
        # FIX 4 đã được áp dụng trong hàm này
        display_all_questions(questions)
        
    elif st.session_state.current_mode == "test":
        # Nút quay lại (nếu cần)
        if st.button("⬅️ Quay lại chế độ Luyện tập theo nhóm"):
            st.session_state.current_mode = "group"
            st.rerun()
        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
        # FIX 4 đã được áp dụng trong hàm này
        display_test_mode(questions, bank_name, num_questions=20)
        
else:
    st.info("Vui lòng upload file DOCX chứa ngân hàng câu hỏi để bắt đầu.")
