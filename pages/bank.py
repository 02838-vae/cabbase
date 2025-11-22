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
    # - 2-10 dấu chấm (có thể có space xen kẽ): .... hoặc . . [cite_start]. [cite: 1, 2]
    # [cite_start]- 2-10 gạch dưới (có thể có space xen kẽ): ____ hoặc __ __ [cite: 2]
    # [cite_start]- Ngoặc chứa các ký tự trên: (____) hoặc (__  __) → chuẩn hóa thành (____) [cite: 2]
    
    temp_s = s
    placeholders = {}
    counter = 0
    
    # BƯỚC 1: Xử lý ngoặc có nhiều space/ký tự → chuẩn hóa thành 4 spaces
    # [cite_start]VD: (__          __) → (____) [cite: 3]
    [cite_start]temp_s = re.sub(r'\([\s._-]{2,}\)', '(    )', temp_s)  # Ngoặc đơn [cite: 3]
    [cite_start]temp_s = re.sub(r'\[[\s._-]{2,}\]', '[    ]', temp_s)  # Ngoặc vuông [cite: 3]
    
    # [cite_start]BƯỚC 2: Lưu các pattern điền chỗ trống còn lại [cite: 4]
    standalone_patterns = [
        [cite_start]r'(?<!\S)([._])(?:\s*\1){1,9}(?!\S)',  # 2-10 dấu . hoặc _ liên tiếp (có thể có space) [cite: 4]
        [cite_start]r'-{2,10}',  # 2-10 gạch ngang liên tiếp [cite: 4]
        [cite_start]r'\([\s]{2,}\)',  # Ngoặc đơn có spaces (đã chuẩn hóa ở bước 1) [cite: 4]
        [cite_start]r'\[[\s]{2,}\]',  # Ngoặc vuông có spaces [cite: 4]
    ]
    
    for pattern in standalone_patterns:
        for match in re.finditer(pattern, temp_s):
            matched_text = match.group()
            [cite_start]placeholder = f"__PLACEHOLDER_{counter}__" [cite: 5]
            [cite_start]placeholders[placeholder] = matched_text [cite: 5]
            [cite_start]temp_s = temp_s.replace(matched_text, placeholder, 1) [cite: 5]
            [cite_start]counter += 1 [cite: 5]
    
    # [cite_start]BƯỚC 3: Xóa khoảng trắng thừa (2+ spaces → 1 space) [cite: 5]
    [cite_start]temp_s = re.sub(r'\s{2,}', ' ', temp_s) [cite: 5]
    
    # [cite_start]BƯỚC 4: Khôi phục các pattern đã lưu [cite: 6]
    for placeholder, original in placeholders.items():
        [cite_start]temp_s = temp_s.replace(placeholder, original) [cite: 6]
    
    [cite_start]return temp_s.strip() [cite: 6]

def read_docx_paragraphs(source):
    """
    Hàm đọc paragraphs từ file .docx với cơ chế tìm kiếm đa dạng:
    1. Thư mục chứa bank.py
    2. Thư mục làm việc hiện tại
    3. Thư mục pages/ (ngang hàng với bank.py)
    """
    try:
        # [cite_start]Cơ chế 1: Thư mục chứa file bank.py [cite: 7]
        [cite_start]doc = Document(os.path.join(os.path.dirname(__file__), source)) [cite: 7]
    except Exception:
        try:
             # [cite_start]Cơ chế 2: Thư mục làm việc hiện tại [cite: 7]
             [cite_start]doc = Document(source) [cite: 7]
        except Exception:
            try:
                # [cite_start]Cơ chế 3: Thư mục con 'pages/' [cite: 8]
                [cite_start]doc = Document(f"pages/{source}") [cite: 8]
            except Exception as e:
                # Nếu tất cả đều thất bại, hiển thị lỗi trong console/log
                [cite_start]print(f"Lỗi không tìm thấy file DOCX: {source}. Chi tiết: {e}") [cite: 9]
                [cite_start]return [] [cite: 9]
    
    # Giữ nguyên p.text.strip() và filtering để loại bỏ các dòng trống không chứa ký tự nào.
    [cite_start]return [p.text.strip() for p in doc.paragraphs if p.text.strip()] [cite: 9]

def get_base64_encoded_file(file_path):
    fallback_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    try:
        # Cơ chế tìm kiếm file ảnh: Ưu tiên trong thư mục hiện tại/chứa script
        [cite_start]path_to_check = os.path.join(os.path.dirname(__file__), file_path) [cite: 9]
        if not os.path.exists(path_to_check) or os.path.getsize(path_to_check) == 0:
            [cite_start]path_to_check = file_path [cite: 10]
        
        if not os.path.exists(path_to_check) or os.path.getsize(path_to_check) == 0:
            [cite_start]return fallback_base64 [cite: 10]
            
        with open(path_to_check, "rb") as f:
            [cite_start]return base64.b64encode(f.read()).decode("utf-8") [cite: 11]
    except Exception as e:
        [cite_start]print(f"Lỗi đọc file ảnh {file_path}: {e}") [cite: 11]
        [cite_start]return fallback_base64 [cite: 11]

# ====================================================
# 🧩 PARSER 1: NGÂN HÀNG KỸ THUẬT (CABBANK)
# ====================================================
def parse_cabbank(source):
    paras = read_docx_paragraphs(source)
    if not paras: return []

    questions = []
    current = {"question": "", "options": [], "answer": ""}
    [cite_start]opt_pat = re.compile(r'(?P<star>\*)?\s*(?P<letter>[A-Da-d])[\.\)]\s+') [cite: 11]

    for p in paras:
        [cite_start]matches = list(opt_pat.finditer(p)) [cite: 11]
        [cite_start]if not matches: [cite: 12]
            [cite_start]if current["options"]: [cite: 12]
                [cite_start]if current["question"] and current["options"]: [cite: 12]
                    [cite_start]if not current["answer"] and current["options"]: [cite: 12]
                        [cite_start]current["answer"] = current["options"][0] [cite: 12]
                [cite_start]questions.append(current) [cite: 13]
                [cite_start]current = {"question": clean_text(p), "options": [], "answer": ""} [cite: 13]
            else:
                [cite_start]if current["question"]: current["question"] += " " + clean_text(p) [cite: 13]
                [cite_start]else: current["question"] = clean_text(p) [cite: 13]
            [cite_start]continue [cite: 13]

        [cite_start]pre_text = p[:matches[0].start()].strip() [cite: 14]
        [cite_start]if pre_text: [cite: 14]
            [cite_start]if current["options"]: [cite: 14]
                [cite_start]if current["question"] and current["options"]: [cite: 14]
                    [cite_start]if not current["answer"] and current["options"]: [cite: 14]
                        [cite_start]current["answer"] = current["options"][0] [cite: 14]
                [cite_start]questions.append(current) [cite: 15]
                [cite_start]current = {"question": clean_text(pre_text), "options": [], "answer": ""} [cite: 15]
            else:
                [cite_start]if current["question"]: current["question"] += " " + clean_text(pre_text) [cite: 15]
                [cite_start]else: current["question"] = clean_text(pre_text) [cite: 15]

        [cite_start]for i, m in enumerate(matches): [cite: 16]
            [cite_start]s = m.end() [cite: 16]
            [cite_start]e = matches[i + 1].start() if i + 1 < len(matches) else len(p) [cite: 16]
            [cite_start]opt_body = clean_text(p[s:e]) [cite: 16]
            [cite_start]letter = m.group('letter').lower() [cite: 16]
            [cite_start]opt = f"{letter}. {opt_body}" [cite: 17]
            [cite_start]current["options"].append(opt) [cite: 17]
            [cite_start]if m.group("star"): current["answer"] = opt [cite: 17]

    [cite_start]if current["question"] and current["options"]: [cite: 17]
        [cite_start]if not current["answer"] and current["options"]: [cite: 17]
            [cite_start]current["answer"] = current["options"][0] [cite: 17]
        [cite_start]questions.append(current) [cite: 17]
    [cite_start]return questions [cite: 17]

# ====================================================
# 🧩 PARSER 2: NGÂN HÀNG LUẬT (LAWBANK)
# ====================================================
def parse_lawbank(source):
    paras = read_docx_paragraphs(source)
    [cite_start]if not paras: return [] [cite: 17]

    [cite_start]questions = [] [cite: 18]
    [cite_start]current = {"question": "", "options": [], "answer": ""} [cite: 18]
    [cite_start]opt_pat = re.compile(r'(?<![A-Za-z0-9/])(?P<star>\*)?\s*(?P<letter>[A-Da-d])[\.\)]\s+') [cite: 18]

    for p in paras:
        [cite_start]if re.match(r'^\s*Ref', p, re.I): continue [cite: 18]
        [cite_start]matches = list(opt_pat.finditer(p)) [cite: 18]
        
        [cite_start]if not matches: [cite: 18]
            [cite_start]if current["options"]: [cite: 18]
                [cite_start]if current["question"] and current["options"]: [cite: 19]
                    [cite_start]if not current["answer"] and current["options"]: [cite: 19]
                        [cite_start]current["answer"] = current["options"][0] [cite: 19]
                    [cite_start]questions.append(current) [cite: 19]
                [cite_start]current = {"question": clean_text(p), "options": [], "answer": ""} [cite: 19]
            [cite_start]else: [cite: 20]
                [cite_start]if current["question"]: current["question"] += " " + clean_text(p) [cite: 20]
                [cite_start]else: current["question"] = clean_text(p) [cite: 20]
            [cite_start]continue [cite: 20]

        [cite_start]first_match = matches[0] [cite: 20]
        [cite_start]pre_text = p[:first_match.start()].strip() [cite: 20]
        [cite_start]if pre_text: [cite: 20]
            [cite_start]if current["options"]: [cite: 21]
                [cite_start]if current["question"] and current["options"]: [cite: 21]
                    [cite_start]if not current["answer"] and current["options"]: [cite: 21]
                        [cite_start]current["answer"] = current["options"][0] [cite: 21]
                    [cite_start]questions.append(current) [cite: 21]
                [cite_start]current = {"question": clean_text(pre_text), "options": [], "answer": ""} [cite: 22]
            else:
                [cite_start]if current["question"]: current["question"] += " " + clean_text(pre_text) [cite: 22]
                [cite_start]else: current["question"] = clean_text(pre_text) [cite: 22]

        [cite_start]for i, m in enumerate(matches): [cite: 22]
            [cite_start]s = m.end() [cite: 23]
            [cite_start]e = matches[i+1].start() if i+1 < len(matches) else len(p) [cite: 23]
            [cite_start]opt_body = clean_text(p[s:e]) [cite: 23]
            [cite_start]letter = m.group("letter").lower() [cite: 23]
            [cite_start]option = f"{letter}. {opt_body}" [cite: 24]
            [cite_start]current["options"].append(option) [cite: 24]
            [cite_start]if m.group("star"): current["answer"] = option [cite: 24]

    [cite_start]if current["question"] and current["options"]: [cite: 24]
        [cite_start]if not current["answer"] and current["options"]: [cite: 24]
            [cite_start]current["answer"] = current["options"][0] [cite: 24]
        [cite_start]questions.append(current) [cite: 24]
    [cite_start]return questions [cite: 24]

# ====================================================
# 🧩 PARSER 3: PHỤ LỤC 1 (ĐÃ SỬA LỖI LOGIC VÀ GIỚI HẠN 3 ĐÁP ÁN)
# ====================================================
def parse_pl1(source):
    """
    [cite_start]Parser cho định dạng PL1 (cải tiến để xử lý câu hỏi không đánh số, giới hạn 3 đáp án) [cite: 25]
    - [cite_start]Chỉ có 3 đáp án (a, b, c) cho mỗi câu hỏi. [cite: 25]
    - [cite_start]Logic chuyển câu mới được siết chặt để xử lý lỗi số trong đáp án (ví dụ: '5 inch...'). [cite: 26]
    - [cite_start]Xóa prefix A., B., C. nếu có trong đáp án thô và tự động gán nhãn a., b., c., đồng thời khắc phục lỗi xóa chữ cái đầu tiên của đáp án (Fix 2). [cite: 27]
    """
    [cite_start]paras = read_docx_paragraphs(source) [cite: 28]
    [cite_start]if not paras: return [] [cite: 28]

    [cite_start]questions = [] [cite: 28]
    [cite_start]current = {"question": "", "options": [], "answer": ""} [cite: 28]
    
    # [cite_start]Regex bắt đầu câu hỏi CÓ ĐÁNH SỐ: Số + dấu chấm hoặc dấu đóng ngoặc (ví dụ: 40., 41)) [cite: 28]
    [cite_start]q_start_pat = re.compile(r'^\s*(\d+)[\.\)]\s*') [cite: 28]
    # [cite_start]Regex bắt đầu câu hỏi CÓ CỤM TỪ [cite: 28]
    [cite_start]phrase_start_pat = re.compile(r'Choose the correct group of words', re.I) [cite: 28]
    
    # FIX 2: Regex cho prefix đáp án cần loại bỏ. [cite_start]Phải có dấu chấm/ngoặc HOẶC ít nhất một khoảng trắng sau chữ cái. [cite: 29]
    [cite_start]opt_prefix_pat = re.compile(r'^\s*[A-Ca-c]([\.\)]|\s+)\s*') [cite: 29]
    
    [cite_start]labels = ["a", "b", "c"] # Chỉ có 3 đáp án [cite: 29]
    [cite_start]MAX_OPTIONS = 3 # Giới hạn tối đa 3 đáp án [cite: 29]

    def finalize_current_question(q_dict, q_list):
        """Lưu câu hỏi hiện tại và reset dictionary."""
        if q_dict["question"]:
            [cite_start]if not q_dict["answer"] and q_dict["options"]: [cite: 30]
                # [cite_start]Nếu không tìm thấy đáp án (*), mặc định lấy A (tức options[0]) là đúng [cite: 30]
                [cite_start]q_dict["answer"] = q_dict["options"][0] [cite: 30]
            [cite_start]q_list.append(q_dict) [cite: 30]
        [cite_start]return {"question": "", "options": [], "answer": ""} [cite: 30]
    
    for p in paras:
        [cite_start]clean_p = clean_text(p) [cite: 31]
        [cite_start]if not clean_p: continue [cite: 31]
        
        [cite_start]is_q_start_phrased = phrase_start_pat.search(clean_p) [cite: 31]
        [cite_start]is_explicitly_numbered = q_start_pat.match(clean_p) [cite: 31]
        [cite_start]is_max_options_reached = len(current["options"]) >= MAX_OPTIONS [cite: 31]
        [cite_start]is_question_started = current["question"] [cite: 31]
        [cite_start]is_first_line = not is_question_started and not current["options"] [cite: 31]
        
        # [cite_start]--- NEW QUESTION LOGIC (Fixing the Q40/3.5 issue) --- [cite: 32]
        must_switch_q = (
            [cite_start]is_first_line or                             # Case 1: Start of doc [cite: 32]
            [cite_start]is_q_start_phrased or                        # Case 2: Explicit phrase [cite: 33]
            (is_question_started and is_max_options_reached) [cite_start]# Case 3: Max options reached [cite: 33]
        )
        # Note: Bỏ điều kiện chuyển câu dựa trên is_explicitly_numbered 
        # [cite_start]khi chưa đủ options để tránh nhầm đáp án (ví dụ: "3.5 INCH...") là câu hỏi mới. [cite: 33, 34]
        # [cite_start]--- APPLY SWITCH DECISION --- [cite: 34]
        [cite_start]if must_switch_q: [cite: 34]
            
            # [cite_start]1. Lưu câu hỏi cũ (nếu có) [cite: 34]
            [cite_start]current = finalize_current_question(current, questions) [cite: 34]
            
            # [cite_start]2. Khởi tạo câu hỏi mới [cite: 35]
            [cite_start]q_text = clean_p [cite: 35]
            [cite_start]if is_explicitly_numbered: [cite: 35]
                # [cite_start]Loại bỏ số thứ tự ở đầu câu hỏi nếu có (VD: "40. ") [cite: 35]
                [cite_start]q_text = q_start_pat.sub('', clean_p).strip() [cite: 35]
            
            # [cite_start]Reset và set question text [cite: 36]
            [cite_start]current["question"] = q_text [cite: 36]
            
        else:
            # [cite_start]--- OPTION LOGIC --- [cite: 36]
            
            # Nếu đã có câu hỏi VÀ chưa đủ MAX_OPTIONS, thì dòng này là một đáp án/lựa chọn
            [cite_start]if is_question_started and not is_max_options_reached: [cite: 37]
                [cite_start]is_correct = False [cite: 37]
                
                # [cite_start]Kiểm tra dấu hiệu đáp án đúng (*) [cite: 37]
                [cite_start]if "(*)" in clean_p: [cite: 37]
                    [cite_start]is_correct = True [cite: 38]
                    # [cite_start]Xóa dấu (*) [cite: 38]
                    [cite_start]clean_p = clean_p.replace("(*)", "").strip() [cite: 38]
                
                # [cite_start]Loại bỏ prefix A., B., C. (và các biến thể có space/.) - Fix 2 [cite: 39]
                [cite_start]match_prefix = opt_prefix_pat.match(clean_p) [cite: 39]
                [cite_start]if match_prefix: [cite: 39]
                    [cite_start]clean_p = clean_p[match_prefix.end():].strip() [cite: 39]
                    
                # [cite_start]Tự động gán nhãn a, b, c [cite: 40]
                [cite_start]idx = len(current["options"]) [cite: 40]
                [cite_start]if idx < len(labels): [cite: 40]
                    [cite_start]label = labels[idx] [cite: 40]
                    [cite_start]opt_text = f"{label}. {clean_p}" [cite: 41]
                    [cite_start]current["options"].append(opt_text) [cite: 41]
                    
                    [cite_start]if is_correct: [cite: 41]
                        # [cite_start]Ghi nhận đây là đáp án đúng [cite: 42]
                        [cite_start]current["answer"] = opt_text [cite: 42]
            
            # [cite_start]Nếu đã đủ 3 đáp án (hoặc không phải option) nhưng không chuyển câu, thêm vào Question text. [cite: 42]
            [cite_start]elif is_question_started: [cite: 42]
                 [cite_start]current["question"] += " " + clean_p [cite: 42]
            
            # [cite_start]Xử lý trường hợp dòng đầu tiên không phải là câu hỏi có đánh số/phrase (đã bị bỏ qua bởi must_switch_q) [cite: 43]
            [cite_start]elif not is_question_started and not current["options"]: [cite: 43]
                [cite_start]current["question"] = clean_p [cite: 43]

    # [cite_start]Lưu câu cuối cùng [cite: 43]
    [cite_start]current = finalize_current_question(current, questions) [cite: 43]
        
    [cite_start]return questions [cite: 43]

# ====================================================
# 🌟 HÀM: XEM TOÀN BỘ CÂU HỎI
# ====================================================
def display_all_questions(questions):
    st.markdown('<div class="result-title"><h3>📚 TOÀN BỘ NGÂN HÀNG CÂU HỎI</h3></div>', unsafe_allow_html=True)
    if not questions:
        [cite_start]st.warning("Không có câu hỏi nào để hiển thị.") [cite: 44]
        return
    
    for i, q in enumerate(questions, start=1):
        [cite_start]st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True) [cite: 45]
        
        for opt in q["options"]:
            # [cite_start]Dùng clean_text để so sánh, bỏ qua khoảng trắng, ký tự ẩn [cite: 45]
            [cite_start]if clean_text(opt) == clean_text(q["answer"]): [cite: 45]
                # [cite_start]Đáp án đúng: Xanh lá [cite: 46]
                [cite_start]color_style = "color:#00ff00; text-shadow: 0 0 3px rgba(0, 255, 0, 0.8);" [cite: 46]
            else:
                # [cite_start]Đáp án thường: Trắng [cite: 46]
                color_style = "color:#FFFFFF;"
            [cite_start]st.markdown(f'<div class="bank-answer-text" style="{color_style}">{opt}</div>', unsafe_allow_html=True) [cite: 47]
        
        [cite_start]st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True) [cite: 47]

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
        [cite_start]st.session_state[f"{test_key_prefix}_started"] = False [cite: 47]
    if f"{test_key_prefix}_submitted" not in st.session_state:
        [cite_start]st.session_state[f"{test_key_prefix}_submitted"] = False [cite: 48]
    if f"{test_key_prefix}_questions" not in st.session_state:
        [cite_start]st.session_state[f"{test_key_prefix}_questions"] = [] [cite: 48]

    [cite_start]if not st.session_state[f"{test_key_prefix}_started"]: [cite: 48]
        [cite_start]st.markdown('<div class="result-title"><h3>📝 LÀM BÀI TEST 50 CÂU</h3></div>', unsafe_allow_html=True) [cite: 48]
        [cite_start]st.info(f"Bài test sẽ gồm **{min(TOTAL_QUESTIONS, len(questions))}** câu hỏi được chọn ngẫu nhiên từ **{bank_name}**. Tỷ lệ đạt (PASS) là **{int(PASS_RATE*100)}%** ({int(TOTAL_QUESTIONS * PASS_RATE)} câu đúng).") [cite: 49]
        
        [cite_start]if st.button("🚀 Bắt đầu Bài Test", key=f"{test_key_prefix}_start_btn"): [cite: 49]
            [cite_start]st.session_state[f"{test_key_prefix}_questions"] = get_random_questions(questions, TOTAL_QUESTIONS) [cite: 49]
            [cite_start]st.session_state[f"{test_key_prefix}_started"] = True [cite: 49]
            [cite_start]st.session_state[f"{test_key_prefix}_submitted"] = False [cite: 49]
            [cite_start]st.session_state.current_mode = "test" [cite: 49]
            [cite_start]st.rerun() [cite: 50]
        [cite_start]return [cite: 50]

    [cite_start]if not st.session_state[f"{test_key_prefix}_submitted"]: [cite: 50]
        [cite_start]st.markdown('<div class="result-title"><h3>⏳ ĐANG LÀM BÀI TEST</h3></div>', unsafe_allow_html=True) [cite: 50]
        [cite_start]test_batch = st.session_state[f"{test_key_prefix}_questions"] [cite: 50]
        [cite_start]for i, q in enumerate(test_batch, start=1): [cite: 50]
            [cite_start]st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True) [cite: 50]
            # [cite_start]SỬA LỖI KEY: THÊM INDEX (i) ĐỂ ĐẢM BẢO TÍNH DUY NHẤT VÀ KHẮC PHỤC StreamlitDuplicateElementKey [cite: 51]
            [cite_start]q_key = f"{test_key_prefix}_q_{i}_{hash(q['question'])}" [cite: 51]
            # [cite_start]Đảm bảo radio button có giá trị mặc định để tránh lỗi [cite: 51]
            [cite_start]default_val = st.session_state.get(q_key, q["options"][0] if q["options"] else None) [cite: 51]
            [cite_start]st.radio("", q["options"], index=q["options"].index(default_val) if default_val in q["options"] else 0, key=q_key) [cite: 52]
            [cite_start]st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True) [cite: 52]
        [cite_start]if st.button("✅ Nộp bài Test", key=f"{test_key_prefix}_submit_btn"): [cite: 52]
            [cite_start]st.session_state[f"{test_key_prefix}_submitted"] = True [cite: 52]
            [cite_start]st.rerun() [cite: 52]
            
    else:
        [cite_start]st.markdown('<div class="result-title"><h3>🎉 KẾT QUẢ BÀI TEST</h3></div>', unsafe_allow_html=True) [cite: 52]
        [cite_start]test_batch = st.session_state[f"{test_key_prefix}_questions"] [cite: 52]
        [cite_start]score = 0 [cite: 52]
        
        [cite_start]for i, q in enumerate(test_batch, start=1): [cite: 53]
            # [cite_start]SỬ DỤNG KEY ĐÃ ĐƯỢC FIX [cite: 53]
            [cite_start]q_key = f"{test_key_prefix}_q_{i}_{hash(q['question'])}" [cite: 53]
            [cite_start]selected_opt = st.session_state.get(q_key) [cite: 53]
            [cite_start]correct = clean_text(q["answer"]) [cite: 53]
            [cite_start]is_correct = clean_text(selected_opt) == correct [cite: 53]

            [cite_start]st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True) [cite: 54]
            [cite_start]for opt in q["options"]: [cite: 54]
                [cite_start]opt_clean = clean_text(opt) [cite: 54]
                [cite_start]if opt_clean == correct: [cite: 54]
                    [cite_start]color_style = "color:#00ff00; text-shadow: 0 0 3px rgba(0, 255, 0, 0.8);" [cite: 54]
                [cite_start]elif opt_clean == clean_text(selected_opt): [cite: 55]
                    [cite_start]color_style = "color:#ff3333; text-shadow: 0 0 3px rgba(255, 0, 0, 0.8);" [cite: 55]
                [cite_start]else: [cite: 56]
                    [cite_start]color_style = "color:#FFFFFF;" [cite: 56]
                [cite_start]st.markdown(f'<div class="bank-answer-text" style="{color_style}">{opt}</div>', unsafe_allow_html=True) [cite: 57]

            [cite_start]if is_correct: score += 1 [cite: 57]
            [cite_start]st.info(f"Đáp án đúng: **{q['answer']}**", icon="💡") [cite: 57]
            [cite_start]st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True) [cite: 57]
        
        [cite_start]total_q = len(test_batch) [cite: 57]
        [cite_start]pass_threshold = total_q * PASS_RATE [cite: 57]
        [cite_start]st.markdown(f'<div class="result-title"><h3>🎯 KẾT QUẢ: {score}/{total_q}</h3></div>', unsafe_allow_html=True) [cite: 57]

        [cite_start]if score >= pass_threshold: [cite: 58]
            [cite_start]st.balloons() [cite: 58]
            [cite_start]st.success(f"🎊 **CHÚC MỪNG!** Bạn đã ĐẠT (PASS).") [cite: 58]
        else:
            [cite_start]st.error(f"😢 **KHÔNG ĐẠT (FAIL)**. Cần {math.ceil(pass_threshold)} câu đúng để Đạt.") [cite: 58]

        [cite_start]if st.button("🔄 Làm lại Bài Test", key=f"{test_key_prefix}_restart_btn"): [cite: 58]
            # [cite_start]Cần lặp lại với index để xoá key chính xác [cite: 59]
            [cite_start]for i, q in enumerate(test_batch, start=1): [cite: 59]
                [cite_start]st.session_state.pop(f"{test_key_prefix}_q_{i}_{hash(q['question'])}", None) [cite: 59]
            [cite_start]st.session_state.pop(f"{test_key_prefix}_questions", None) [cite: 59]
            [cite_start]st.session_state[f"{test_key_prefix}_started"] = False [cite: 59]
            [cite_start]st.session_state[f"{test_key_prefix}_submitted"] = False [cite: 59]
            [cite_start]st.rerun() [cite: 59]

# ====================================================
# 🖥️ GIAO DIỆN STREAMLIT
# ====================================================
[cite_start]st.set_page_config(page_title="Ngân hàng trắc nghiệm", layout="wide") [cite: 59]

[cite_start]PC_IMAGE_FILE = "bank_PC.jpg" [cite: 59]
[cite_start]MOBILE_IMAGE_FILE = "bank_mobile.jpg" [cite: 60]
[cite_start]img_pc_base64 = get_base64_encoded_file(PC_IMAGE_FILE) [cite: 60]
[cite_start]img_mobile_base64 = get_base64_encoded_file(MOBILE_IMAGE_FILE) [cite: 60]

# === CSS (ĐÃ CHỈNH SỬA) ===
css_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;700&display=swap');
@keyframes colorShift {{
    0% {{ background-position: 0% 50%; }}
    [cite_start]50% {{ background-position: 100% 50%; }} [cite: 62]
    100% {{ background-position: 0% 50%; }}
}}
@keyframes scrollRight {{
    0% {{ transform: translateX(100%); [cite_start]}} [cite: 63]
    100% {{ transform: translateX(-100%); }}
}}

html, body, .stApp {{
    [cite_start]height: 100% !important; [cite: 64]
    [cite_start]min-height: 100vh !important; [cite: 64]
    margin: 0 !important;
    padding: 0 !important;
    overflow: auto;
    [cite_start]position: relative; [cite: 65]
}}

/* BACKGROUND */
.stApp {{
    [cite_start]background: none !important; [cite: 65]
}}

.stApp::before {{
    content: "";
    [cite_start]position: fixed; [cite: 66]
    [cite_start]top: 0; [cite: 66]
    [cite_start]left: 0; [cite: 66]
    [cite_start]width: 100%; [cite: 66]
    [cite_start]height: 100%; [cite: 66]
    background: url("data:image/jpeg;base64,{img_pc_base64}") no-repeat center top fixed;
    background-size: cover;
    filter: sepia(0.5) brightness(0.9) blur(0px);
    [cite_start]z-index: -1; [cite: 67]
    [cite_start]pointer-events: none; [cite: 67]
}}

@media (max-width: 767px) {{
    .stApp::before {{
        background: url("data:image/jpeg;base64,{img_mobile_base64}") no-repeat center top scroll;
        [cite_start]background-size: cover; [cite: 68]
    }}
}}

/* Nội dung nổi lên trên nền */
[data-testid="stAppViewContainer"],
[data-testid="stMainBlock"],
.main {{
    [cite_start]background-color: transparent !important; [cite: 69]
}}

/* Ẩn UI */
[cite_start]#MainMenu, footer, header {{visibility: hidden; height: 0;}} [cite: 69]
[cite_start][data-testid="stHeader"] {{display: none;}} [cite: 69]

/* BUTTON HOME */
#back-to-home-btn-container {{
    [cite_start]position: fixed; [cite: 69]
    [cite_start]top: 10px; left: 10px; [cite: 70]
    [cite_start]width: auto !important; z-index: 1500; [cite: 70]
    [cite_start]display: inline-block; [cite: 70]
}}
a#manual-home-btn {{
    [cite_start]background-color: rgba(0, 0, 0, 0.85); [cite: 71]
    [cite_start]color: #FFEA00; [cite: 71]
    [cite_start]border: 2px solid #FFEA00; [cite: 71]
    [cite_start]padding: 5px 10px; [cite: 71]
    [cite_start]border-radius: 8px; [cite: 72]
    [cite_start]font-weight: bold; [cite: 72]
    [cite_start]font-size: 14px; [cite: 72]
    [cite_start]transition: all 0.3s; [cite: 72]
    [cite_start]font-family: 'Oswald', sans-serif; [cite: 72]
    [cite_start]text-decoration: none; [cite: 72]
    [cite_start]display: inline-block; [cite: 72]
    [cite_start]white-space: nowrap; [cite: 72]
    [cite_start]box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5); [cite: 73]
}}
a#manual-home-btn:hover {{
    [cite_start]background-color: #FFEA00; [cite: 73]
    [cite_start]color: black; [cite: 73]
    [cite_start]transform: scale(1.05); [cite: 73]
}}

/* TITLE CHÍNH */
#main-title-container {{
    [cite_start]position: relative; left: 0; top: 0; width: 100%; [cite: 74]
    [cite_start]height: 120px; overflow: hidden; [cite: 74]
    [cite_start]pointer-events: none; [cite: 75]
    [cite_start]background-color: transparent; padding-top: 20px; z-index: 1200; [cite: 75]
}}
#main-title-container h1 {{
    [cite_start]visibility: visible !important; [cite: 75]
    [cite_start]height: auto !important; [cite: 76]
    [cite_start]font-family: 'Playfair Display', serif; [cite: 76]
    [cite_start]font-size: 5vh; [cite: 76]
    [cite_start]margin: 0; padding: 10px 0; [cite: 76]
    [cite_start]font-weight: 900; letter-spacing: 5px; white-space: nowrap; [cite: 76]
    [cite_start]display: inline-block; [cite: 76]
    [cite_start]background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3); [cite: 77]
    [cite_start]background-size: 400% 400%; [cite: 77]
    -webkit-background-clip: text; [cite_start]-webkit-text-fill-color: transparent; color: transparent; [cite: 77]
    [cite_start]animation: scrollRight 15s linear infinite, colorShift 8s ease infinite; [cite: 78]
    [cite_start]text-shadow: 2px 2px 8px rgba(255, 255, 255, 0.3); [cite: 78]
    [cite_start]position: absolute; [cite: 78]
    [cite_start]left: 0; top: 5px; [cite: 79]
    [cite_start]line-height: 1.5 !important; [cite: 79]
}}

/* SỐ 1 */
.number-one {{
    [cite_start]font-family: 'Oswald', sans-serif !important; [cite: 79]
    [cite_start]font-size: 1em !important; [cite: 80]
    [cite_start]font-weight: 700; [cite: 80]
    [cite_start]display: inline-block; [cite: 80]
}}

@media (max-width: 768px) {{
    #back-to-home-btn-container {{ top: 5px; left: 5px; [cite_start]}} [cite: 81]
    #main-title-container {{ height: 100px; padding-top: 10px; [cite_start]}} [cite: 81]
    [cite_start]#main-title-container h1 {{ font-size: 8vw; [cite: 81]
    line-height: 1.5 !important; [cite_start]}} [cite: 82]
    [cite_start].main > div:first-child {{ padding-top: 20px !important; [cite: 82]
    }}
}}

.main > div:first-child {{
    [cite_start]padding-top: 40px !important; padding-bottom: 2rem !important; [cite: 84]
}}

/* FIX YÊU CẦU 2: TITLE LỚN NHƯNG VẪN 1 HÀNG */
#sub-static-title, .result-title {{
    [cite_start]margin-top: 150px; [cite: 84]
    [cite_start]margin-bottom: 30px; text-align: center; [cite: 85]
}}
#sub-static-title h2, .result-title h3 {{
    [cite_start]font-family: 'Playfair Display', serif; [cite: 85]
    [cite_start]font-size: 2rem; [cite: 86]
    /* Desktop */
    [cite_start]color: #FFEA00; [cite: 86]
    [cite_start]text-shadow: 0 0 15px #FFEA00; [cite: 87]
}}
@media (max-width: 768px) {{
    #sub-static-title h2, .result-title h3 {{
        /* Tăng lên 4.8vw và giảm spacing để chữ to hơn mà vẫn 1 dòng */
        [cite_start]font-size: 4.8vw !important; [cite: 87]
        [cite_start]letter-spacing: -0.5px; [cite: 88]
        [cite_start]white-space: nowrap; [cite: 88]
    }}
}}

/* STYLE CÂU HỎI & ĐÁP ÁN */
.bank-question-text {{
    [cite_start]color: #FFDD00 !important; [cite: 89]
    [cite_start]font-weight: 700 !important; [cite: 89]
    [cite_start]font-size: 22px !important; [cite: 89]
    [cite_start]font-family: 'Oswald', sans-serif !important; [cite: 89]
    [cite_start]text-shadow: 0 0 5px rgba(255, 221, 0, 0.5); [cite: 90]
    [cite_start]padding: 5px 15px; margin-bottom: 10px; line-height: 1.4 !important; [cite: 90]
}}

/* ĐÃ SỬA: Tăng font-weight để chữ trắng nổi bật hơn */
.bank-answer-text {{
    [cite_start]font-family: 'Oswald', sans-serif !important; [cite: 91]
    [cite_start]font-weight: 700 !important; [cite: 91]
    [cite_start]font-size: 22px !important; [cite: 91]
    [cite_start]padding: 5px 15px; margin: 2px 0; [cite: 91]
    [cite_start]line-height: 1.5 !important; [cite: 92]
    [cite_start]display: block; [cite: 92]
}}

/* 💥 CHỈNH SỬA CHO ST.RADIO LABEL (CHẾ ĐỘ LÀM BÀI) */
.stRadio label {{
    [cite_start]color: #FFFFFF !important; [cite: 93]
    /* Màu trắng tuyệt đối */
    [cite_start]font-size: 22px !important; [cite: 93]
    [cite_start]font-weight: 700 !important; [cite: 94]
    /* Tăng độ dày chữ */
    [cite_start]font-family: 'Oswald', sans-serif !important; [cite: 94]
    [cite_start]padding: 2px 12px; [cite: 95]
    /* THÊM TEXT-SHADOW ĐỂ CHỮ TRẮNG NỔI BẬT HƠN TRÊN NỀN ẢNH */
    text-shadow: 0 0 5px rgba(255, 255, 255, 0.5), 0 0 2px rgba(0, 0, 0, 0.8);
}}
div[data-testid="stMarkdownContainer"] p {{
    [cite_start]font-size: 22px !important; [cite: 95]
}}

.stButton>button {{
    [cite_start]background-color: #b7a187 !important; [cite: 96]
    [cite_start]color: #ffffff !important; [cite: 96]
    [cite_start]border-radius: 8px; [cite: 96]
    [cite_start]font-size: 1.1em !important; [cite: 96]
    [cite_start]font-weight: 600 !important; [cite: 96]
    [cite_start]font-family: 'Oswald', sans-serif !important; [cite: 96]
    [cite_start]border: none !important; [cite: 96]
    [cite_start]padding: 10px 20px !important; [cite: 97]
    [cite_start]width: 100%; [cite: 97]
}}
.stButton>button:hover {{ background-color: #a89073 !important; [cite_start]}} [cite: 97]
.question-separator {{
    [cite_start]margin: 15px 0; height: 1px; [cite: 97]
    [cite_start]background: linear-gradient(to right, transparent, #FFDD00, transparent); opacity: 0.5; [cite: 98]
}}
div.stSelectbox label p {{
    [cite_start]color: #33FF33 !important; [cite: 99]
    [cite_start]font-size: 1.25rem !important; [cite: 99]
    [cite_start]font-family: 'Oswald', sans-serif !important; [cite: 99]
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
    <div id="main-title-container"><h1>TỔ BẢO DƯỠNG SỐ <span class="number-one">1</span></h1></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div id="sub-static-title"><h2>NGÂN HÀNG TRẮC NGHIỆM</h2></div>', unsafe_allow_html=True)

[cite_start]if "current_group_idx" not in st.session_state: st.session_state.current_group_idx = 0 [cite: 99]
[cite_start]if "submitted" not in st.session_state: st.session_state.submitted = False [cite: 99]
[cite_start]if "current_mode" not in st.session_state: st.session_state.current_mode = "group" [cite: 99]
[cite_start]if "last_bank_choice" not in st.session_state: st.session_state.last_bank_choice = "----" [cite: 99]
[cite_start]if "doc_selected" not in st.session_state: st.session_state.doc_selected = "Phụ Lục 1" [cite: 99]

# CẬP NHẬT LIST NGÂN HÀNG
[cite_start]BANK_OPTIONS = ["----", "Ngân hàng Kỹ thuật", "Ngân hàng Luật VAECO", "Ngân hàng Docwise"] [cite: 100]
[cite_start]bank_choice = st.selectbox("Chọn ngân hàng:", BANK_OPTIONS, index=BANK_OPTIONS.index(st.session_state.get('bank_choice_val', '----')), key="bank_selector_master") [cite: 100]
[cite_start]st.session_state.bank_choice_val = bank_choice [cite: 100]

# Xử lý khi đổi ngân hàng (reset mode)
[cite_start]if st.session_state.get('last_bank_choice') != bank_choice and bank_choice != "----": [cite: 100]
    [cite_start]st.session_state.current_group_idx = 0 [cite: 100]
    [cite_start]st.session_state.submitted = False [cite: 100]
    [cite_start]st.session_state.current_mode = "group" [cite: 100]
    [cite_start]last_bank_name = st.session_state.get('last_bank_choice') [cite: 100]
    [cite_start]if not isinstance(last_bank_name, str) or last_bank_name == "----": last_bank_name = "null bank" [cite: 100]
    # Xoá session state của bài test cũ
    [cite_start]bank_slug_old = last_bank_name.split()[-1].lower() [cite: 100]
    [cite_start]st.session_state.pop(f"test_{bank_slug_old}_started", None) [cite: 101]
    [cite_start]st.session_state.pop(f"test_{bank_slug_old}_submitted", None) [cite: 101]
    [cite_start]st.session_state.pop(f"test_{bank_slug_old}_questions", None) [cite: 101]
    [cite_start]st.session_state.last_bank_choice = bank_choice [cite: 101]
    [cite_start]st.rerun() [cite: 101]

[cite_start]if bank_choice != "----": [cite: 101]
    # [cite_start]XỬ LÝ LOGIC NGUỒN DỮ LIỆU [cite: 101]
    [cite_start]source = "" [cite: 101]
    [cite_start]is_docwise = False [cite: 101]
    
    [cite_start]if "Kỹ thuật" in bank_choice: [cite: 101]
        [cite_start]source = "cabbank.docx" [cite: 101]
    [cite_start]elif "Luật VAECO" in bank_choice: [cite: 101]
        [cite_start]source = "lawbank.docx" [cite: 101]
    [cite_start]elif "Docwise" in bank_choice: [cite: 101]
        [cite_start]is_docwise = True [cite: 102]
        # [cite_start]Dropdown phụ cho Docwise [cite: 102]
        [cite_start]doc_options = ["Phụ Lục 1"] [cite: 102]
        [cite_start]doc_selected_new = st.selectbox("Chọn Phụ lục:", doc_options, key="docwise_selector") [cite: 102]
        
        # [cite_start]Xử lý khi đổi phụ lục (reset mode) [cite: 102]
        [cite_start]if st.session_state.doc_selected != doc_selected_new: [cite: 102]
            [cite_start]st.session_state.doc_selected = doc_selected_new [cite: 103]
            [cite_start]st.session_state.current_group_idx = 0 [cite: 103]
            [cite_start]st.session_state.submitted = False [cite: 103]
            [cite_start]st.session_state.current_mode = "group" [cite: 103]
            [cite_start]st.rerun() [cite: 103]

        [cite_start]if st.session_state.doc_selected == "Phụ Lục 1": [cite: 103]
            [cite_start]source = "PL1.docx" # File PL1.docx [cite: 103]
        
    # [cite_start]LOAD CÂU HỎI [cite: 103]
    [cite_start]questions = [] [cite: 103]
    [cite_start]if source: [cite: 104]
        [cite_start]if "Kỹ thuật" in bank_choice: [cite: 104]
            [cite_start]questions = parse_cabbank(source) [cite: 104]
        [cite_start]elif "Luật VAECO" in bank_choice: [cite: 104]
            [cite_start]questions = parse_lawbank(source) [cite: 104]
        [cite_start]elif is_docwise: [cite: 104]
            [cite_start]questions = parse_pl1(source) [cite: 104]
    
    [cite_start]if not questions: [cite: 104]
        [cite_start]st.error(f"❌ Không đọc được câu hỏi nào từ file **{source}**. Vui lòng kiểm tra file và cấu trúc thư mục (đảm bảo file nằm trong thư mục gốc hoặc thư mục 'pages/').") [cite: 105]
        [cite_start]st.stop() [cite: 105]
    
    [cite_start]total = len(questions) [cite: 105]
    [cite_start]st.success(f"Đã tải thành công **{total}** câu hỏi từ **{bank_choice}**.") [cite: 105]

    # [cite_start]--- MODE: GROUP --- [cite: 105]
    [cite_start]if st.session_state.current_mode == "group": [cite: 105]
        [cite_start]st.markdown('<div class="result-title" style="margin-top: 0px;"><h3>Luyện tập theo nhóm (10 câu/nhóm)</h3></div>', unsafe_allow_html=True) [cite: 105]
        [cite_start]group_size = 10 [cite: 106]
        [cite_start]if total > 0: [cite: 106]
            [cite_start]groups = [f"Câu {i*group_size+1}-{min((i+1)*group_size, total)}" for i in range(math.ceil(total/group_size))] [cite: 106]
            [cite_start]if st.session_state.current_group_idx >= len(groups): st.session_state.current_group_idx = 0 [cite: 106]
            [cite_start]selected = st.selectbox("Chọn nhóm câu:", groups, index=st.session_state.current_group_idx, key="group_selector") [cite: 106]
            
            # [cite_start]Xử lý khi chuyển nhóm câu [cite: 107]
            [cite_start]new_idx = groups.index(selected) [cite: 107]
            [cite_start]if st.session_state.current_group_idx != new_idx: [cite: 107]
                [cite_start]st.session_state.current_group_idx = new_idx [cite: 107]
                [cite_start]st.session_state.submitted = False [cite: 107]
                [cite_start]st.rerun() [cite: 107]

            [cite_start]idx = st.session_state.current_group_idx [cite: 108]
            [cite_start]start, end = idx * group_size, min((idx+1) * group_size, total) [cite: 108]
            [cite_start]batch = questions[start:end] [cite: 108]
            
            [cite_start]st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True) [cite: 108]
            [cite_start]col_all_bank, col_test = st.columns(2) [cite: 108]
            [cite_start]with col_all_bank: [cite: 108]
                [cite_start]if st.button("📖 Hiển thị toàn bộ ngân hàng", key="btn_show_all"): [cite: 109]
                    [cite_start]st.session_state.current_mode = "all" [cite: 109]
                    [cite_start]st.rerun() [cite: 109]
            [cite_start]with col_test: [cite: 109]
                [cite_start]if st.button("Làm bài test 50 câu", key="btn_start_test"): [cite: 109]
                    [cite_start]st.session_state.current_mode = "test" [cite: 110]
                    [cite_start]bank_slug_new = bank_choice.split()[-1].lower() [cite: 110]
                    [cite_start]test_key_prefix = f"test_{bank_slug_new}" [cite: 110]
                    # [cite_start]Reset session state cho bài test trước khi bắt đầu [cite: 110]
                    [cite_start]st.session_state.pop(f"{test_key_prefix}_started", None) [cite: 111]
                    [cite_start]st.session_state.pop(f"{test_key_prefix}_submitted", None) [cite: 111]
                    [cite_start]st.session_state.pop(f"{test_key_prefix}_questions", None) [cite: 111]
                    [cite_start]st.rerun() [cite: 111]
            [cite_start]st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True) [cite: 111]
            
            [cite_start]if batch: [cite: 111]
                [cite_start]if not st.session_state.submitted: [cite: 112]
                    [cite_start]for i, q in enumerate(batch, start=start+1): [cite: 112]
                        [cite_start]q_key = f"q_{i}_{hash(q['question'])}" # Dùng hash để tránh trùng key [cite: 112]
                        [cite_start]st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True) [cite: 113]
                        # [cite_start]Đảm bảo radio button có giá trị mặc định để tránh lỗi [cite: 113]
                        [cite_start]default_val = st.session_state.get(q_key, q["options"][0] if q["options"] else None) [cite: 113]
                        [cite_start]st.radio("", q["options"], index=q["options"].index(default_val) if default_val in q["options"] else 0, key=q_key) [cite: 114]
                        [cite_start]st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True) [cite: 114]
                    [cite_start]if st.button("✅ Nộp bài", key="submit_group"): [cite: 114]
                        [cite_start]st.session_state.submitted = True [cite: 115]
                        [cite_start]st.rerun() [cite: 115]
                else:
                    [cite_start]score = 0 [cite: 115]
                    [cite_start]for i, q in enumerate(batch, start=start+1): [cite: 115]
                        [cite_start]q_key = f"q_{i}_{hash(q['question'])}" [cite: 116]
                        [cite_start]selected_opt = st.session_state.get(q_key) [cite: 116]
                        [cite_start]correct = clean_text(q["answer"]) [cite: 116]
                        [cite_start]is_correct = clean_text(selected_opt) == correct [cite: 116]
                        [cite_start]st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True) [cite: 117]
                        [cite_start]for opt in q["options"]: [cite: 117]
                            [cite_start]opt_clean = clean_text(opt) [cite: 117]
                            [cite_start]if opt_clean == correct: [cite: 117]
                                [cite_start]color_style = "color:#00ff00; text-shadow: 0 0 3px rgba(0, 255, 0, 0.8);" [cite: 118]
                            [cite_start]elif opt_clean == clean_text(selected_opt): [cite: 119]
                                [cite_start]color_style = "color:#ff3333; text-shadow: 0 0 3px rgba(255, 0, 0, 0.8);" [cite: 119]
                            [cite_start]else: [cite: 120]
                                [cite_start]color_style = "color:#FFFFFF;" [cite: 120]
                            [cite_start]st.markdown(f'<div class="bank-answer-text" style="{color_style}">{opt}</div>', unsafe_allow_html=True) [cite: 121]
                        
                        if is_correct: 
                            [cite_start]st.success(f"✅ Đúng – Đáp án: {q['answer']}") [cite: 121]
                            [cite_start]score += 1 [cite: 122]
                        else: 
                            [cite_start]st.error(f"❌ Sai – Đáp án đúng: {q['answer']}") [cite: 122]
                        [cite_start]st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True) [cite: 123] 

                    [cite_start]st.markdown(f'<div class="result-title"><h3>🎯 KẾT QUẢ: {score}/{len(batch)}</h3></div>', unsafe_allow_html=True) [cite: 123]
                    [cite_start]col_reset, col_next = st.columns(2) [cite: 123]
                    [cite_start]with col_reset: [cite: 123]
                        [cite_start]if st.button("🔄 Làm lại nhóm này", key="reset_group"): [cite: 124]
                            # [cite_start]Xoá session state của các radio button trong nhóm [cite: 124]
                            [cite_start]for i, q in enumerate(batch, start=start+1): [cite: 124]
                                [cite_start]st.session_state.pop(f"q_{i}_{hash(q['question'])}", None) [cite: 125]
                            [cite_start]st.session_state.submitted = False [cite: 125]
                            [cite_start]st.rerun() [cite: 125]
                    [cite_start]with col_next: [cite: 125]
                        [cite_start]if st.session_state.current_group_idx < len(groups) - 1: [cite: 126]
                            [cite_start]if st.button("➡️ Tiếp tục nhóm sau", key="next_group"): [cite: 126]
                                [cite_start]st.session_state.current_group_idx += 1 [cite: 126]
                                [cite_start]st.session_state.submitted = False [cite: 127]
                                [cite_start]st.rerun() [cite: 127]
                        [cite_start]else: st.info("🎉 Đã hoàn thành tất cả các nhóm câu hỏi!") [cite: 127]
            [cite_start]else: st.warning("Không có câu hỏi trong nhóm này.") [cite: 128]
        [cite_start]else: st.warning("Không có câu hỏi nào trong ngân hàng này.") [cite: 128]

    [cite_start]elif st.session_state.current_mode == "all": [cite: 128]
        [cite_start]if st.button("⬅️ Quay lại chế độ Luyện tập theo nhóm"): [cite: 128]
            [cite_start]st.session_state.current_mode = "group" [cite: 129]
            [cite_start]st.rerun() [cite: 129]
        [cite_start]st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True) [cite: 129]
        [cite_start]display_all_questions(questions) [cite: 129]
        
    [cite_start]elif st.session_state.current_mode == "test": [cite: 129]
        [cite_start]if st.button("⬅️ Quay lại chế độ Luyện tập theo nhóm"): [cite: 129]
            [cite_start]st.session_state.current_mode = "group" [cite: 129]
            [cite_start]st.rerun() [cite: 129]
        [cite_start]st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True) [cite: 129]
        display_test_mode(questions, bank_choice)
