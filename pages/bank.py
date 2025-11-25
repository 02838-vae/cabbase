# -*- coding: utf-8 -*-
import streamlit as st
from docx import Document
import re
import math
import pandas as pd
import base64
import os
import random 

# --- LOGIC VIDEO INTRO (SAO CHÉP TỪ APP.PY) ---

# Khởi tạo session state (Bắt buộc phải có)
if 'video_ended' not in st.session_state:
    st.session_state.video_ended = False
if 'first_load' not in st.session_state:
    st.session_state.first_load = True

# --- HÀM KIỂM TRA VÀ HIỂN THỊ VIDEO INTRO ---
def check_and_show_intro():
    # Kiểm tra và Reset URL khi refresh (Logic của bạn)
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        query_params = st.query_params.to_dict()
        if 'skip_intro' not in query_params:
            st.query_params.clear()

    # --- VIDEO INTRO LOGIC (Phần hiển thị video) ---
    if not st.session_state.video_ended:
        st.subheader("Chào mừng đến với ứng dụng")
        
        # Thêm toàn bộ mã HTML/CSS/JS cho video player của bạn ở đây
        # Ví dụ:
        # st.markdown("""...""", unsafe_allow_html=True)
        # st.markdown(get_video_html("videos/intro.mp4"), unsafe_allow_html=True)
        
        # Giả lập nút bấm để qua intro (Nếu bạn có nút)
        # if st.button("Bỏ qua Intro"):
        #     st.session_state.video_ended = True
        #     st.rerun()

        # THAY THẾ TOÀN BỘ MÃ HIỂN THỊ VIDEO CỦA BẠN VÀO ĐÂY.
        # Ví dụ:
        # st.markdown(
        #     """<video width="100%" autoplay onended="document.getElementById('video-placeholder').style.display='none'; window.st_rerun_trigger = true;" id="myVideo"><source src="data:video/mp4;base64,..." type="video/mp4"></video>""", 
        #     unsafe_allow_html=True
        # )
        
        # Rất quan trọng: Dùng st.stop() để ngăn không cho nội dung trang chính render
        st.stop()
        # Lưu ý: Hàm này cần phải được gọi trước bất kỳ nội dung nào khác của trang
        
    return st.session_state.video_ended


# --- CHẠY LOGIC INTRO ---
# check_and_show_intro()

# ====================================================
# ⚙️ HÀM HỖ TRỢ VÀ FILE I/O
# ====================================================
def clean_text(s: str) -> str:
    if s is None:
        return ""
    
    # GIỮ NGUYÊN các pattern điền chỗ trống:
    # - 2-10 dấu chấm (có thể có space xen kẽ): .... hoặc . . . .
    # - 2-10 gạch dưới (có thể có space xen kẽ): ____ hoặc __ __
    # - Ngoặc chứa các ký tự trên: (____) hoặc (__  __) → chuẩn hóa thành (____) 
    
    temp_s = s
    placeholders = {}
    counter = 0
    
    # BƯỚC 1: Xử lý ngoặc có nhiều space/ký tự → chuẩn hóa thành 4 spaces
    # VD: (__           __) → (____)
    temp_s = re.sub(r'\([\s._-]{2,}\)', '(    )', temp_s)  # Ngoặc đơn
    temp_s = re.sub(r'\[[\s._-]{2,}\]', '[    ]', temp_s)  # Ngoặc vuông
    
    # BƯỚC 2: Lưu các pattern điền chỗ trống còn lại
    standalone_patterns = [
        r'(?<!\S)([._])(?:\s*\1){1,9}(?!\S)',  # 2-10 dấu . hoặc _ liên tiếp (có thể có space)
        r'-{2,10}',  # 2-10 gạch ngang liên tiếp
        r'\([\s]{2,}\)',  # Ngoặc đơn có spaces (đã chuẩn hóa ở bước 1)
        r'\[[\s]{2,}\]',  # Ngoặc vuông có spaces
    ]
    
    for pattern in standalone_patterns:
        for match in re.finditer(pattern, temp_s):
            matched_text = match.group()
            placeholder = f"__PLACEHOLDER_{counter}__"
            placeholders[placeholder] = matched_text
            temp_s = temp_s.replace(matched_text, placeholder, 1)
            counter += 1
    
    # BƯỚC 3: Xóa khoảng trắng thừa (2+ spaces → 1 space)
    temp_s = re.sub(r'\s{2,}', ' ', temp_s)
    
    # BƯỚC 4: Khôi phục các pattern đã lưu
    for placeholder, original in placeholders.items():
        temp_s = temp_s.replace(placeholder, original)
    
    return temp_s.strip()

def read_docx_paragraphs(source):
    """
    Hàm đọc paragraphs từ file .docx với cơ chế tìm kiếm đa dạng:
    1. Thư mục chứa bank.py
    2. Thư mục làm việc hiện tại
    3. Thư mục pages/ (ngang hàng với bank.py)
    """
    try:
        # Cơ chế 1: Thư mục chứa file bank.py
        doc = Document(os.path.join(os.path.dirname(__file__), source))
    except Exception:
        try:
             # Cơ chế 2: Thư mục làm việc hiện tại
             doc = Document(source)
        except Exception:
            try:
                # Cơ chế 3: Thư mục con 'pages/'
                doc = Document(f"pages/{source}")
            except Exception as e:
                # Nếu tất cả đều thất bại, hiển thị lỗi trong console/log
                print(f"Lỗi không tìm thấy file DOCX: {source}. Chi tiết: {e}")
                return []
    
    # Giữ nguyên p.text.strip() và filtering để loại bỏ các dòng trống không chứa ký tự nào.
    return [p.text.strip() for p in doc.paragraphs if p.text.strip()]

def get_base64_encoded_file(file_path):
    fallback_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    try:
        # Cơ chế tìm kiếm file ảnh: Ưu tiên trong thư mục hiện tại/chứa script
        path_to_check = os.path.join(os.path.dirname(__file__), file_path)
        if not os.path.exists(path_to_check) or os.path.getsize(path_to_check) == 0:
            path_to_check = file_path 
        
        if not os.path.exists(path_to_check) or os.path.getsize(path_to_check) == 0:
            return fallback_base64
            
        with open(path_to_check, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"Lỗi đọc file ảnh {file_path}: {e}")
        return fallback_base64

# ====================================================
# 🧩 PARSER 1: NGÂN HÀNG KỸ THUẬT (CABBANK)
# ====================================================
def parse_cabbank(source):
    paras = read_docx_paragraphs(source)
    if not paras: return []

    questions = []
    current = {"question": "", "options": [], "answer": ""}
    opt_pat = re.compile(r'(?P<star>\*)?\s*(?P<letter>[A-Da-d])[\.\)]\s+')

    for p in paras:
        matches = list(opt_pat.finditer(p))
        if not matches:
            if current["options"]:
                if current["question"] and current["options"]:
                    if not current["answer"] and current["options"]:
                        current["answer"] = current["options"][0]
                    questions.append(current)
                current = {"question": clean_text(p), "options": [], "answer": ""}
            else:
                if current["question"]: current["question"] += " " + clean_text(p)
                else: current["question"] = clean_text(p)
            continue

        pre_text = p[:matches[0].start()].strip()
        if pre_text:
            if current["options"]:
                if current["question"] and current["options"]:
                    if not current["answer"] and current["options"]:
                        current["answer"] = current["options"][0]
                    questions.append(current)
                current = {"question": clean_text(pre_text), "options": [], "answer": ""}
            else:
                if current["question"]: current["question"] += " " + clean_text(pre_text)
                else: current["question"] = clean_text(pre_text)

        for i, m in enumerate(matches):
            s = m.end()
            e = matches[i + 1].start() if i + 1 < len(matches) else len(p)
            opt_body = clean_text(p[s:e])
            letter = m.group('letter').lower()
            opt = f"{letter}. {opt_body}"
            current["options"].append(opt)
            if m.group("star"): current["answer"] = opt

    if current["question"] and current["options"]:
        if not current["answer"] and current["options"]:
            current["answer"] = current["options"][0]
        questions.append(current)
    return questions

# ====================================================
# 🧩 PARSER 2: NGÂN HÀNG LUẬT (LAWBANK)
# ====================================================
def parse_lawbank(source):
    paras = read_docx_paragraphs(source)
    if not paras: return []

    questions = []
    current = {"question": "", "options": [], "answer": ""}
    opt_pat = re.compile(r'(?<![A-Za-z0-9/])(?P<star>\*)?\s*(?P<letter>[A-Da-d])[\.\)]\s+')

    for p in paras:
        if re.match(r'^\s*Ref', p, re.I): continue
        matches = list(opt_pat.finditer(p))
        
        if not matches:
            if current["options"]:
                if current["question"] and current["options"]:
                    if not current["answer"] and current["options"]:
                        current["answer"] = current["options"][0]
                    questions.append(current)
                current = {"question": clean_text(p), "options": [], "answer": ""}
            else:
                if current["question"]: current["question"] += " " + clean_text(p)
                else: current["question"] = clean_text(p)
            continue

        first_match = matches[0]
        pre_text = p[:first_match.start()].strip()
        if pre_text:
            if current["options"]:
                if current["question"] and current["options"]:
                    if not current["answer"] and current["options"]:
                        current["answer"] = current["options"][0]
                    questions.append(current)
                current = {"question": clean_text(pre_text), "options": [], "answer": ""}
            else:
                if current["question"]: current["question"] += " " + clean_text(pre_text)
                else: current["question"] = clean_text(pre_text)

        for i, m in enumerate(matches):
            s = m.end()
            e = matches[i+1].start() if i+1 < len(matches) else len(p)
            opt_body = clean_text(p[s:e])
            letter = m.group("letter").lower()
            option = f"{letter}. {opt_body}"
            current["options"].append(option)
            if m.group("star"): current["answer"] = option

    if current["question"] and current["options"]:
        if not current["answer"] and current["options"]:
            current["answer"] = current["options"][0]
        questions.append(current)
    return questions

# ====================================================
# 🧩 PARSER 3: PHỤ LỤC 1 (ĐÃ SỬA LỖI LOGIC VÀ GIỚI HẠN 3 ĐÁP ÁN)
# ====================================================
def parse_pl1(source):
    """
    Parser cho định dạng PL1 (cải tiến để xử lý câu hỏi không đánh số, giới hạn 3 đáp án)
    - Chỉ có 3 đáp án (a, b, c) cho mỗi câu hỏi.
    - Logic chuyển câu mới được siết chặt để xử lý lỗi số trong đáp án (ví dụ: '5 inch...').
    - Xóa prefix A., B., C. nếu có trong đáp án thô và tự động gán nhãn a., b., c., đồng thời khắc phục lỗi xóa chữ cái đầu tiên của đáp án (Fix 2).
    """
    paras = read_docx_paragraphs(source)
    if not paras: return []

    questions = []
    current = {"question": "", "options": [], "answer": ""}
    
    # Regex bắt đầu câu hỏi CÓ ĐÁNH SỐ: Số + dấu chấm hoặc dấu đóng ngoặc (ví dụ: 40., 41))
    q_start_pat = re.compile(r'^\s*(\d+)[\.\)]\s*') 
    # Regex bắt đầu câu hỏi CÓ CỤM TỪ
    phrase_start_pat = re.compile(r'Choose the correct group of words', re.I)
    
    # FIX 2: Regex cho prefix đáp án cần loại bỏ. Phải có dấu chấm/ngoặc HOẶC ít nhất một khoảng trắng sau chữ cái.
    opt_prefix_pat = re.compile(r'^\s*[A-Ca-c]([\.\)]|\s+)\s*') 
    
    labels = ["a", "b", "c"] # Chỉ có 3 đáp án
    MAX_OPTIONS = 3 # Giới hạn tối đa 3 đáp án

    def finalize_current_question(q_dict, q_list):
        """Lưu câu hỏi hiện tại và reset dictionary."""
        if q_dict["question"]:
            if not q_dict["answer"] and q_dict["options"]:
                # Nếu không tìm thấy đáp án (*), mặc định lấy A (tức options[0]) là đúng
                q_dict["answer"] = q_dict["options"][0] 
            q_list.append(q_dict)
        return {"question": "", "options": [], "answer": ""}
    
    for p in paras:
        clean_p = clean_text(p)
        if not clean_p: continue
        
        is_q_start_phrased = phrase_start_pat.search(clean_p)
        is_explicitly_numbered = q_start_pat.match(clean_p) 
        is_max_options_reached = len(current["options"]) >= MAX_OPTIONS
        is_question_started = current["question"]
        is_first_line = not is_question_started and not current["options"]
        
        # --- NEW QUESTION LOGIC (Fixing the Q40/3.5 issue) ---
        must_switch_q = (
            is_first_line or                             # Case 1: Start of doc
            is_q_start_phrased or                        # Case 2: Explicit phrase
            (is_question_started and is_max_options_reached) # Case 3: Max options reached
        )
        # Note: Bỏ điều kiện chuyển câu dựa trên is_explicitly_numbered 
        # khi chưa đủ options để tránh nhầm đáp án (ví dụ: "3.5 INCH...") là câu hỏi mới.
        # --- APPLY SWITCH DECISION ---
        if must_switch_q:
            
            # 1. Lưu câu hỏi cũ (nếu có)
            current = finalize_current_question(current, questions)
            
            # 2. Khởi tạo câu hỏi mới
            q_text = clean_p
            if is_explicitly_numbered:
                # Loại bỏ số thứ tự ở đầu câu hỏi nếu có (VD: "40. ")
                q_text = q_start_pat.sub('', clean_p).strip()
            
            # Reset và set question text
            current["question"] = q_text
            
        else:
            # --- OPTION LOGIC ---
            
            # Nếu đã có câu hỏi VÀ chưa đủ MAX_OPTIONS, thì dòng này là một đáp án/lựa chọn
            if is_question_started and not is_max_options_reached:
                is_correct = False
                
                # Kiểm tra dấu hiệu đáp án đúng (*)
                if "(*)" in clean_p:
                    is_correct = True
                    # Xóa dấu (*)
                    clean_p = clean_p.replace("(*)", "").strip() 
                
                # Loại bỏ prefix A., B., C. (và các biến thể có space/.) - Fix 2
                match_prefix = opt_prefix_pat.match(clean_p)
                if match_prefix:
                    clean_p = clean_p[match_prefix.end():].strip()
                    
                # Tự động gán nhãn a, b, c
                idx = len(current["options"])
                if idx < len(labels):
                    label = labels[idx]
                    opt_text = f"{label}. {clean_p}"
                    current["options"].append(opt_text)
                    
                    if is_correct:
                        # Ghi nhận đây là đáp án đúng
                        current["answer"] = opt_text
            
            # Nếu đã đủ 3 đáp án (hoặc không phải option) nhưng không chuyển câu, thêm vào Question text.
            elif is_question_started:
                 current["question"] += " " + clean_p
        
            elif not is_question_started and not current["options"]:
                current["question"] = clean_p

    # Lưu câu cuối cùng
    current = finalize_current_question(current, questions)
        
    return questions

# ====================================================
# 🌟 HÀM: XEM TOÀN BỘ CÂU HỎI
# ====================================================
def display_all_questions(questions):
    st.markdown('<div class="result-title"><h3>📚 TOÀN BỘ NGÂN HÀNG CÂU HỎI</h3></div>', unsafe_allow_html=True)
    if not questions:
        st.warning("Không có câu hỏi nào để hiển thị.")
        return
    
    for i, q in enumerate(questions, start=1):
        st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True)
        
        for opt in q["options"]:
            # Dùng clean_text để so sánh, bỏ qua khoảng trắng, ký tự ẩn
            if clean_text(opt) == clean_text(q["answer"]):
                # Đáp án đúng: Xanh lá
                color_style = "color:#00ff00; text-shadow: 0 0 3px rgba(0, 255, 0, 0.8);"
            else:
                # Đáp án thường: Trắng
                color_style = "color:#FFFFFF;"
            st.markdown(f'<div class="bank-answer-text" style="{color_style}">{opt}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)

# ====================================================
# 🌟 HÀM: TEST MODE
# ====================================================
def get_random_questions(questions, count=50):
    if len(questions) <= count: return questions
    return random.sample(questions, count)

def display_test_mode(questions, bank_name, key_prefix="test"):
    TOTAL_QUESTIONS = 50
    PASS_RATE = 0.75
    bank_slug = bank_name.split()[-1].lower()
    test_key_prefix = f"{key_prefix}_{bank_slug}"
    
    if f"{test_key_prefix}_started" not in st.session_state:
        st.session_state[f"{test_key_prefix}_started"] = False
    if f"{test_key_prefix}_submitted" not in st.session_state:
        st.session_state[f"{test_key_prefix}_submitted"] = False
    if f"{test_key_prefix}_questions" not in st.session_state:
        st.session_state[f"{test_key_prefix}_questions"] = []

    if not st.session_state[f"{test_key_prefix}_started"]:
        st.markdown('<div class="result-title"><h3>📝 LÀM BÀI TEST 50 CÂU</h3></div>', unsafe_allow_html=True)
        st.info(f"Bài test sẽ gồm **{min(TOTAL_QUESTIONS, len(questions))}** câu hỏi được chọn ngẫu nhiên từ **{bank_name}**. Tỷ lệ đạt (PASS) là **{int(PASS_RATE*100)}%** ({int(TOTAL_QUESTIONS * PASS_RATE)} câu đúng).")
        
        if st.button("🚀 Bắt đầu Bài Test", key=f"{test_key_prefix}_start_btn"):
            st.session_state[f"{test_key_prefix}_questions"] = get_random_questions(questions, TOTAL_QUESTIONS)
            st.session_state[f"{test_key_prefix}_started"] = True
            st.session_state[f"{test_key_prefix}_submitted"] = False
            st.session_state.current_mode = "test" 
            st.rerun()
        return

    if not st.session_state[f"{test_key_prefix}_submitted"]:
        st.markdown('<div class="result-title"><h3>⏳ ĐANG LÀM BÀI TEST</h3></div>', unsafe_allow_html=True)
        test_batch = st.session_state[f"{test_key_prefix}_questions"]
        for i, q in enumerate(test_batch, start=1):
            st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True)
            # SỬA LỖI KEY: THÊM INDEX (i) ĐỂ ĐẢM BẢO TÍNH DUY NHẤT VÀ KHẮC PHỤC StreamlitDuplicateElementKey
            q_key = f"{test_key_prefix}_q_{i}_{hash(q['question'])}" 
            # Đảm bảo radio button có giá trị mặc định để tránh lỗi
            default_val = st.session_state.get(q_key, q["options"][0] if q["options"] else None)
            st.radio("", q["options"], index=q["options"].index(default_val) if default_val in q["options"] else 0, key=q_key)
            st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True) 
        if st.button("✅ Nộp bài Test", key=f"{test_key_prefix}_submit_btn"):
            st.session_state[f"{test_key_prefix}_submitted"] = True
            st.rerun()
            
    else:
        st.markdown('<div class="result-title"><h3>🎉 KẾT QUẢ BÀI TEST</h3></div>', unsafe_allow_html=True)
        test_batch = st.session_state[f"{test_key_prefix}_questions"]
        score = 0
        
        for i, q in enumerate(test_batch, start=1):
            # SỬ DỤNG KEY ĐÃ ĐƯỢC FIX
            q_key = f"{test_key_prefix}_q_{i}_{hash(q['question'])}" 
            selected_opt = st.session_state.get(q_key)
            correct = clean_text(q["answer"])
            is_correct = clean_text(selected_opt) == correct

            st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True)
            for opt in q["options"]:
                opt_clean = clean_text(opt)
                if opt_clean == correct:
                    color_style = "color:#00ff00; text-shadow: 0 0 3px rgba(0, 255, 0, 0.8);"
                elif opt_clean == clean_text(selected_opt):
                    color_style = "color:#ff3333; text-shadow: 0 0 3px rgba(255, 0, 0, 0.8);"
                else:
                    color_style = "color:#FFFFFF;"
                st.markdown(f'<div class="bank-answer-text" style="{color_style}">{opt}</div>', unsafe_allow_html=True)

            if is_correct: score += 1
            st.info(f"Đáp án đúng: **{q['answer']}**", icon="💡")
            st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True) 
        
        total_q = len(test_batch)
        pass_threshold = total_q * PASS_RATE
        st.markdown(f'<div class="result-title"><h3>🎯 KẾT QUẢ: {score}/{total_q}</h3></div>', unsafe_allow_html=True)

        if score >= pass_threshold:
            st.balloons()
            st.success(f"🎊 **CHÚC MỪNG!** Bạn đã ĐẠT (PASS).")
        else:
            st.error(f"😢 **KHÔNG ĐẠT (FAIL)**. Cần {math.ceil(pass_threshold)} câu đúng để Đạt.")

        if st.button("🔄 Làm lại Bài Test", key=f"{test_key_prefix}_restart_btn"):
            # Cần lặp lại với index để xoá key chính xác
            for i, q in enumerate(test_batch, start=1):
                st.session_state.pop(f"{test_key_prefix}_q_{i}_{hash(q['question'])}", None)
            st.session_state.pop(f"{test_key_prefix}_questions", None)
            st.session_state[f"{test_key_prefix}_started"] = False
            st.session_state[f"{test_key_prefix}_submitted"] = False
            st.rerun()

# ====================================================
# 🖥️ GIAO DIỆN STREAMLIT
# ====================================================
st.set_page_config(page_title="Ngân hàng trắc nghiệm", layout="wide")

PC_IMAGE_FILE = "bank_PC.jpg"
MOBILE_IMAGE_FILE = "bank_mobile.jpg"
img_pc_base64 = get_base64_encoded_file(PC_IMAGE_FILE)
img_mobile_base64 = get_base64_encoded_file(MOBILE_IMAGE_FILE)

# === CSS ===
css_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;700&display=swap');
@keyframes colorShift {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}
@keyframes scrollRight {{
    0% {{ transform: translateX(100%); }}
    100% {{ transform: translateX(-100%); }}
}}

html, body, .stApp {{
    height: 100% !important;
    min-height: 100vh !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: auto;
    position: relative;
}}

/* BACKGROUND */
.stApp {{
    background: none !important;
}}

.stApp::before {{
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: url("data:image/jpeg;base64,{img_pc_base64}") no-repeat center top fixed;
    background-size: cover;
    filter: sepia(0.5) brightness(0.9) blur(0px);
    z-index: -1; 
    pointer-events: none;
}}

@media (max-width: 767px) {{
    .stApp::before {{
        background: url("data:image/jpeg;base64,{img_mobile_base64}") no-repeat center top scroll;
        background-size: cover;
    }}
}}

/* Nội dung nổi lên trên nền */
[data-testid="stAppViewContainer"],
[data-testid="stMainBlock"],
.main {{
    background-color: transparent !important;
}}

/* Ẩn UI */
#MainMenu, footer, header {{visibility: hidden; height: 0;}}
[data-testid="stHeader"] {{display: none;}}

/* BUTTON HOME */
#back-to-home-btn-container {{
    position: fixed;
    top: 10px; left: 10px; 
    width: auto !important; z-index: 1500; 
    display: inline-block;
}}
a#manual-home-btn {{
    background-color: rgba(0, 0, 0, 0.85);
    color: #FFEA00;
    border: 2px solid #FFEA00;
    padding: 5px 10px;
    border-radius: 8px; 
    font-weight: bold;
    font-size: 14px; 
    transition: all 0.3s;
    font-family: 'Oswald', sans-serif;
    text-decoration: none;
    display: inline-block; 
    white-space: nowrap;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
}}
a#manual-home-btn:hover {{
    background-color: #FFEA00;
    color: black;
    transform: scale(1.05);
}}

/* TITLE CHÍNH */
#main-title-container {{
    position: relative; left: 0; top: 0; width: 100%;
    height: 120px; overflow: hidden;
    pointer-events: none;
    background-color: transparent; padding-top: 20px; z-index: 1200; 
}}
#main-title-container h1 {{
    visibility: visible !important;
    height: auto !important;
    font-family: 'Playfair Display', serif;
    font-size: 5vh; 
    margin: 0; padding: 10px 0;
    font-weight: 900; letter-spacing: 5px; white-space: nowrap;
    display: inline-block;
    background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
    background-size: 400% 400%;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; color: transparent;
    animation: scrollRight 15s linear infinite, colorShift 8s ease infinite;
    text-shadow: 2px 2px 8px rgba(255, 255, 255, 0.3);
    position: absolute;
    left: 0; top: 5px; 
    line-height: 1.5 !important;
}}

/* SỐ 1 */
.number-one {{
    font-family: 'Oswald', sans-serif !important;
    font-size: 1em !important; 
    font-weight: 700;
    display: inline-block;
}}

@media (max-width: 768px) {{
    #back-to-home-btn-container {{ top: 5px; left: 5px; }}
    #main-title-container {{ height: 100px; padding-top: 10px; }}
    #main-title-container h1 {{ font-size: 8vw; line-height: 1.5 !important; }}
    .main > div:first-child {{ padding-top: 20px !important; }}
}}

.main > div:first-child {{
    padding-top: 40px !important; padding-bottom: 2rem !important;
}}

/* FIX YÊU CẦU 2: TITLE LỚN NHƯNG VẪN 1 HÀNG */
#sub-static-title, .result-title {{
    margin-top: 150px;
    margin-bottom: 30px; text-align: center;
}}
#sub-static-title h2, .result-title h3 {{
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    /* Desktop */
    color: #FFEA00;
    text-shadow: 0 0 15px #FFEA00;
}}
@media (max-width: 768px) {{
    #sub-static-title h2, .result-title h3 {{
        /* Tăng lên 4.8vw và giảm spacing để chữ to hơn mà vẫn 1 dòng */
        font-size: 4.8vw !important;
        letter-spacing: -0.5px;
        white-space: nowrap; 
    }}
}}

/* STYLE CÂU HỎI & ĐÁP ÁN */
.bank-question-text {{
    color: #FFDD00 !important;
    font-weight: 700 !important;
    font-size: 22px !important; 
    font-family: 'Oswald', sans-serif !important;
    text-shadow: 0 0 5px rgba(255, 221, 0, 0.5);
    padding: 5px 15px; margin-bottom: 10px; line-height: 1.4 !important;
}}

/* ĐÃ SỬA: Tăng font-weight để chữ trắng nổi bật hơn */
.bank-answer-text {{
    font-family: 'Oswald', sans-serif !important;
    font-weight: 700 !important; 
    font-size: 22px !important; 
    padding: 5px 15px; margin: 2px 0;
    line-height: 1.5 !important; 
    display: block;
}}

/* ĐÃ SỬA: Tăng font-weight để chữ trắng nổi bật hơn */
.stRadio label {{
    color: #FFFFFF !important;
    /* Màu trắng tuyệt đối */
    font-size: 22px !important; 
    font-weight: 700 !important;
    /* Tăng độ dày chữ */
    font-family: 'Oswald', sans-serif !important; 
    padding: 2px 12px;
}}
div[data-testid="stMarkdownContainer"] p {{
    font-size: 22px !important; 
}}

.stButton>button {{
    background-color: #b7a187 !important;
    color: #ffffff !important;
    border-radius: 8px;
    font-size: 1.1em !important;
    font-weight: 600 !important;
    font-family: 'Oswald', sans-serif !important; 
    border: none !important;
    padding: 10px 20px !important;
    width: 100%; 
}}
.stButton>button:hover {{ background-color: #a89073 !important; }}
.question-separator {{
    margin: 15px 0; height: 1px;
    background: linear-gradient(to right, transparent, #FFDD00, transparent); opacity: 0.5;
}}
div.stSelectbox label p {{
    color: #33FF33 !important;
    font-size: 1.25rem !important;
    font-family: 'Oswald', sans-serif !important;
}}
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# ====================================================
# 🧭 HEADER & BODY
# ====================================================
st.markdown("""
<div id="header-content-wrapper">
    <div id="back-to-home-btn-container">
        <a id="manual-home-btn" href="/?skip_intro=1" target="_self">🏠 Về Trang Chủ</a>
    </div>
    <div id="main-title-container"><h1>Tổ Bảo Dưỡng Số <span class="number-one">1</span></h1></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div id="sub-static-title"><h2>NGÂN HÀNG TRẮC NGHIỆM</h2></div>', unsafe_allow_html=True)

if "current_group_idx" not in st.session_state: st.session_state.current_group_idx = 0
if "submitted" not in st.session_state: st.session_state.submitted = False
if "current_mode" not in st.session_state: st.session_state.current_mode = "group"
if "last_bank_choice" not in st.session_state: st.session_state.last_bank_choice = "----" 
if "doc_selected" not in st.session_state: st.session_state.doc_selected = "Phụ Lục 1" 

# CẬP NHẬT LIST NGÂN HÀNG
BANK_OPTIONS = ["----", "Ngân hàng Kỹ thuật", "Ngân hàng Luật VAECO", "Ngân hàng Docwise"]
bank_choice = st.selectbox("Chọn ngân hàng:", BANK_OPTIONS, index=BANK_OPTIONS.index(st.session_state.get('bank_choice_val', '----')), key="bank_selector_master")
st.session_state.bank_choice_val = bank_choice

# Xử lý khi đổi ngân hàng (reset mode)
if st.session_state.get('last_bank_choice') != bank_choice and bank_choice != "----":
    st.session_state.current_group_idx = 0
    st.session_state.submitted = False
    st.session_state.current_mode = "group" 
    last_bank_name = st.session_state.get('last_bank_choice')
    if not isinstance(last_bank_name, str) or last_bank_name == "----": last_bank_name = "null bank" 
    # Xoá session state của bài test cũ
    bank_slug_old = last_bank_name.split()[-1].lower()
    st.session_state.pop(f"test_{bank_slug_old}_started", None)
    st.session_state.pop(f"test_{bank_slug_old}_submitted", None)
    st.session_state.pop(f"test_{bank_slug_old}_questions", None)
    st.session_state.last_bank_choice = bank_choice
    st.rerun()

if bank_choice != "----":
    # XỬ LÝ LOGIC NGUỒN DỮ LIỆU
    source = ""
    is_docwise = False
    
    if "Kỹ thuật" in bank_choice:
        source = "cabbank.docx"
    elif "Luật VAECO" in bank_choice:
        source = "lawbank.docx"
    elif "Docwise" in bank_choice:
        is_docwise = True
        # Dropdown phụ cho Docwise
        doc_options = ["Phụ Lục 1"]
        doc_selected_new = st.selectbox("Chọn Phụ lục:", doc_options, key="docwise_selector")
        
        # Xử lý khi đổi phụ lục (reset mode)
        if st.session_state.doc_selected != doc_selected_new:
            st.session_state.doc_selected = doc_selected_new
            st.session_state.current_group_idx = 0
            st.session_state.submitted = False
            st.session_state.current_mode = "group"
            st.rerun()

        if st.session_state.doc_selected == "Phụ Lục 1":
            source = "PL1.docx" # File PL1.docx
        
    # LOAD CÂU HỎI
    questions = []
    if source:
        if "Kỹ thuật" in bank_choice:
            questions = parse_cabbank(source)
        elif "Luật VAECO" in bank_choice:
            questions = parse_lawbank(source)
        elif is_docwise:
            questions = parse_pl1(source)
    
    if not questions:
        st.error(f"❌ Không đọc được câu hỏi nào từ file **{source}**. Vui lòng kiểm tra file và cấu trúc thư mục (đảm bảo file nằm trong thư mục gốc hoặc thư mục 'pages/').")
        st.stop() 
    
    total = len(questions)
    st.success(f"Đã tải thành công **{total}** câu hỏi từ **{bank_choice}**.")

    # --- MODE: GROUP ---
    if st.session_state.current_mode == "group":
        st.markdown('<div class="result-title" style="margin-top: 0px;"><h3>Luyện tập theo nhóm (10 câu/nhóm)</h3></div>', unsafe_allow_html=True)
        group_size = 10
        if total > 0:
            groups = [f"Câu {i*group_size+1}-{min((i+1)*group_size, total)}" for i in range(math.ceil(total/group_size))]
            if st.session_state.current_group_idx >= len(groups): st.session_state.current_group_idx = 0
            selected = st.selectbox("Chọn nhóm câu:", groups, index=st.session_state.current_group_idx, key="group_selector")
            
            # Xử lý khi chuyển nhóm câu
            new_idx = groups.index(selected)
            if st.session_state.current_group_idx != new_idx:
                st.session_state.current_group_idx = new_idx
                st.session_state.submitted = False
                st.rerun()

            idx = st.session_state.current_group_idx
            start, end = idx * group_size, min((idx+1) * group_size, total)
            batch = questions[start:end]
            
            st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
            col_all_bank, col_test = st.columns(2)
            with col_all_bank:
                if st.button("📖 Hiển thị toàn bộ ngân hàng", key="btn_show_all"):
                    st.session_state.current_mode = "all"
                    st.rerun()
            with col_test:
                if st.button("Làm bài test 50 câu", key="btn_start_test"):
                    st.session_state.current_mode = "test"
                    bank_slug_new = bank_choice.split()[-1].lower()
                    test_key_prefix = f"test_{bank_slug_new}"
                    # Reset session state cho bài test trước khi bắt đầu
                    st.session_state.pop(f"{test_key_prefix}_started", None)
                    st.session_state.pop(f"{test_key_prefix}_submitted", None)
                    st.session_state.pop(f"{test_key_prefix}_questions", None)
                    st.rerun()
            st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
            
            if batch:
                if not st.session_state.submitted:
                    for i, q in enumerate(batch, start=start+1):
                        q_key = f"q_{i}_{hash(q['question'])}" # Dùng hash để tránh trùng key
                        st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True)
                        # Đảm bảo radio button có giá trị mặc định để tránh lỗi
                        default_val = st.session_state.get(q_key, q["options"][0] if q["options"] else None)
                        st.radio("", q["options"], index=q["options"].index(default_val) if default_val in q["options"] else 0, key=q_key)
                        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
                    if st.button("✅ Nộp bài", key="submit_group"):
                        st.session_state.submitted = True
                        st.rerun()
                else:
                    score = 0
                    for i, q in enumerate(batch, start=start+1):
                        q_key = f"q_{i}_{hash(q['question'])}" 
                        selected_opt = st.session_state.get(q_key)
                        correct = clean_text(q["answer"])
                        is_correct = clean_text(selected_opt) == correct
                        st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True)
                        for opt in q["options"]:
                            opt_clean = clean_text(opt)
                            if opt_clean == correct:
                                color_style = "color:#00ff00; text-shadow: 0 0 3px rgba(0, 255, 0, 0.8);"
                            elif opt_clean == clean_text(selected_opt):
                                color_style = "color:#ff3333; text-shadow: 0 0 3px rgba(255, 0, 0, 0.8);"
                            else:
                                color_style = "color:#FFFFFF;"
                            st.markdown(f'<div class="bank-answer-text" style="{color_style}">{opt}</div>', unsafe_allow_html=True)
                        
                        if is_correct: 
                            st.success(f"✅ Đúng – Đáp án: {q['answer']}")
                            score += 1
                        else: 
                            st.error(f"❌ Sai – Đáp án đúng: {q['answer']}")
                        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True) 

                    st.markdown(f'<div class="result-title"><h3>🎯 KẾT QUẢ: {score}/{len(batch)}</h3></div>', unsafe_allow_html=True)
                    col_reset, col_next = st.columns(2)
                    with col_reset:
                        if st.button("🔄 Làm lại nhóm này", key="reset_group"):
                            # Xoá session state của các radio button trong nhóm
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
        if st.button("⬅️ Quay lại chế độ Luyện tập theo nhóm"):
            st.session_state.current_mode = "group"
            st.rerun()
        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
        display_all_questions(questions)
        
    elif st.session_state.current_mode == "test":
        if st.button("⬅️ Quay lại chế độ Luyện tập theo nhóm"):
            st.session_state.current_mode = "group"
            st.rerun()
        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
        display_test_mode(questions, bank_choice)
