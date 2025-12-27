# -*- coding: utf-8 -*-
import streamlit as st
from docx import Document
# THÊM IMPORT ĐỂ XỬ LÝ ĐỊNH DẠNG (HIGHLIGHT)
from docx.enum.text import WD_COLOR_INDEX 
import re
import math
import pandas as pd
import base64
import os
import random 
from deep_translator import GoogleTranslator

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
        for match in re.finditer(pattern, temp_s): # Đã sửa: finditer thành re.finditer (Fix NameError cũ)
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

def find_file_path(source):
    """Hàm tìm đường dẫn file với cơ chế tìm kiếm đa dạng."""
    paths = [
        os.path.join(os.path.dirname(__file__), source),
        source,
        f"pages/{source}"
    ]
    for path in paths:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            return path
    return None

def read_docx_paragraphs(source):
    """
    Hàm đọc paragraphs chỉ lấy TEXT (sử dụng cho cabbank, lawbank, PL1)
    """
    path = find_file_path(source)
    if not path:
        print(f"Lỗi không tìm thấy file DOCX: {source}")
        return []
    
    try:
        doc = Document(path)
        return [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    except Exception as e:
        print(f"Lỗi đọc file DOCX (chỉ text): {source}. Chi tiết: {e}")
        return []

# HÀM ĐỌC FILE MỚI: DÙNG CHO PL2 (CHỈ LẤY TEXT)
def read_pl2_data(source):
    """
    Hàm đọc paragraphs chỉ lấy TEXT (tương tự read_docx_paragraphs),
    để parse_pl2 có thể dùng logic (*).
    """
    path = find_file_path(source)
    if not path:
        print(f"Lỗi không tìm thấy file DOCX: {source}")
        return []
    
    data = []
    
    try:
        doc = Document(path)
    except Exception as e:
        print(f"Lỗi đọc file DOCX (chỉ text): {source}. Chi tiết: {e}")
        return []

    for p in doc.paragraphs:
        p_text_stripped = p.text.strip()
        if not p_text_stripped:
            continue
        
        # BỎ LOGIC HIGHLIGHT VÀNG, CHỈ LẤY TEXT VÀ ĐẶT CỜ HIGHLIGHT = FALSE
        data.append({
            "full_text": p_text_stripped,
            "has_yellow_highlight": False 
        })
        
    return data

def get_base64_encoded_file(file_path):
    fallback_base64 = "iVBORw0KGgoAAAANSUhEUAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    path_to_check = find_file_path(file_path)
    if not path_to_check:
        return fallback_base64
        
    try:
        with open(path_to_check, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"Lỗi đọc file ảnh {file_path}: {e}")
        return fallback_base64

# ====================================================
# 🌐 HÀM DỊCH THUẬT (ĐÃ CẬP NHẬT DÙNG deep_translator)
# ====================================================

# Thay thế import
from deep_translator import GoogleTranslator

@st.cache_resource
def get_translator():
    """Khởi tạo Translator với deep_translator"""
    try:
        return GoogleTranslator(source='auto', target='vi')
    except Exception as e:
        print(f"Lỗi khởi tạo translator: {e}")
        return None

# HÀM MỚI: Dịch văn bản thuần túy (Dùng cho đoạn văn)
def translate_passage_content(text):
    """
    Dịch văn bản thuần túy và cố gắng bảo toàn định dạng xuống dòng.
    """
    translator = get_translator()
    if translator is None or not text.strip():
        return f"**[LỖI]** Không thể khởi tạo translator." if not text.strip() else ""
    try:
        # Dịch nguyên khối, deep_translator thường bảo toàn line breaks nếu input có
        translated_text = translator.translate(text)
        return translated_text
    except Exception as e:
        print(f"Lỗi dịch thuật passage: {e}")
        return f"**[LỖI DỊCH THUẬT ĐOẠN VĂN]** Không thể dịch nội dung. Chi tiết: {type(e).__name__}"


# HÀM MỚI: Dùng để xây dựng chuỗi dịch cho Q/A
def build_translation_text_for_qa(q):
    """Xây dựng chuỗi văn bản đầy đủ để gửi đi dịch (chỉ Question và Options)."""
    question_text = q['question']
    options_text = '; '.join(q['options'])
    return f"Câu hỏi: {question_text}\nĐáp án: {options_text}"


# HÀM GỐC: Đã được đổi tên thành `translate_question_and_options`
def translate_question_and_options(text):
    """
    Dịch câu hỏi và đáp án sử dụng deep_translator.
    (Input là chuỗi đã được build_translation_text_for_qa định dạng)
    """
    translator = get_translator()
    
    if translator is None:
        return f"**[LỖI]** Không thể khởi tạo translator."
    
    try:
        # 1. Logic dịch Options (Dùng chung)
        def _translate_options(options_raw_text):
            a_translated_list = []
            options = [opt.strip() for opt in options_raw_text.split(';') if opt.strip()]
            for i, option_content in enumerate(options):
                if not option_content: a_translated_list.append(""); continue
                
                original_prefix_match = re.match(r'^([a-d]\.|\s*)\s*', option_content, re.IGNORECASE)
                original_prefix_with_space = original_prefix_match.group(0) if original_prefix_match else ""
                original_prefix = original_prefix_with_space.strip() if original_prefix_with_space.strip() else f"{i+1}."
                
                content_to_translate = option_content[len(original_prefix_with_space):].strip()
                if not content_to_translate: a_translated_list.append(original_prefix); continue
                
                translated_text = translator.translate(content_to_translate)
                stripped_translated_text = translated_text.strip()
                
                if stripped_translated_text.lower().startswith("một "): stripped_translated_text = stripped_translated_text[len("một "):]
                stripped_translated_text = re.sub(r'^\s*([a-d]\.|\d+\.)\s*', '', stripped_translated_text, flags=re.IGNORECASE).strip()
                if not stripped_translated_text: stripped_translated_text = translated_text.strip()
                
                a_translated_list.append(f"{original_prefix} {stripped_translated_text}")
            
            return "\n".join([f"- {opt}" for opt in a_translated_list])
        # --------------------------------------------------

        # Tách Câu hỏi và Đáp án từ input text
        q_parts = text.split('\nĐáp án: ')
        q_content = q_parts[0].replace('Câu hỏi: ', '').strip()
        a_content_raw = q_parts[1].strip() if len(q_parts) > 1 else ""
        
        q_translated = translator.translate(q_content)
        a_translated_text = _translate_options(a_content_raw)
        
        return f"**[Bản dịch Tiếng Việt]**\n\n- **Câu hỏi:** {q_translated}\n- **Các đáp án:** \n{a_translated_text}"
        
    except Exception as e:
        print(f"Lỗi dịch thuật: {e}")
        return f"**[LỖI DỊCH THUẬT]**\n- Không thể dịch nội dung. Chi tiết: {type(e).__name__}\n- Câu hỏi gốc:\n{text}"

# Đặt lại tên hàm cũ (translate_text) để tương thích với các hàm hiển thị
translate_text = translate_question_and_options
# ====================================================

# ====================================================
# 🧩 PARSER 1: NGÂN HÀNG KỸ THUẬT (CABBANK)
# ====================================================
# ... (parse_cabbank remains unchanged)
def parse_cabbank(source):
    """
    Parser cho định dạng CABBANK (Dùng dấu * trước option đúng)
    """
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
# ... (parse_lawbank remains unchanged)
def parse_lawbank(source):
    """
    Parser cho định dạng LAWBANK (Dùng dấu * trước option đúng)
    """
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
# 🧩 PARSER 3: PHỤ LỤC 1 (Dùng dấu (*))
# ====================================================
# ... (parse_pl1 remains unchanged)
def parse_pl1(source):
    """
    Parser cho định dạng PL1 (sử dụng dấu (*) để nhận diện đáp án đúng)
    """
    paras = read_docx_paragraphs(source)
    if not paras: return []

    questions = []
    current = {"question": "", "options": [], "answer": ""}
    
    q_start_pat = re.compile(r'^\s*(\d+)[\.\)]\s*') 
    phrase_start_pat = re.compile(r'Choose the correct group of words', re.I)
    opt_prefix_pat = re.compile(r'^\s*[A-Ca-c]([\.\)]|\s+)\s*') 
    labels = ["a", "b", "c"]
    MAX_OPTIONS = 3

    def finalize_current_question(q_dict, q_list):
        if q_dict["question"]:
            if not q_dict["answer"] and q_dict["options"]:
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
        
        must_switch_q = (
            is_first_line or                            
            is_q_start_phrased or                       
            (is_question_started and is_max_options_reached)
        )
        
        if must_switch_q:
            current = finalize_current_question(current, questions)
            q_text = clean_p
            if is_explicitly_numbered:
                q_text = q_start_pat.sub('', clean_p).strip()
            current["question"] = q_text
            
        else:
            if is_question_started and not is_max_options_reached:
                is_correct = False
                
                # SỬ DỤNG DẤU (*)
                if "(*)" in clean_p:
                    is_correct = True
                    clean_p = clean_p.replace("(*)", "").strip() 
                
                match_prefix = opt_prefix_pat.match(clean_p)
                if match_prefix:
                    clean_p = clean_p[match_prefix.end():].strip()
                    
                idx = len(current["options"])
                    
                if idx < len(labels):
                    label = labels[idx]
                    opt_text = f"{label}. {clean_p}"
                    current["options"].append(opt_text)
                    
                    if is_correct:
                        current["answer"] = opt_text
            
            elif is_question_started:
                 current["question"] += " " + clean_p
        
            elif not is_question_started and not current["options"]:
                current["question"] = clean_p

    current = finalize_current_question(current, questions)
        
    return questions

# ====================================================
# 🧩 PARSER 4: PHỤ LỤC 2 (Dùng dấu (*))
# ====================================================
# ... (parse_pl2 remains unchanged)
def parse_pl2(source):
    """
    Parser cho định dạng PL2 (Sử dụng ký hiệu (*) để nhận diện đáp án đúng)
    """
    data = read_pl2_data(source) # SỬ DỤNG HÀM ĐỌC ĐÃ SỬA CHỈ LẤY TEXT
    if not data: return []

    questions = []
    current = {"question": "", "options": [], "answer": ""}
    
    q_start_pat = re.compile(r'^\s*(\d+)[\.\)]\s*') 
    phrase_start_pat = re.compile(r'Choose the correct group of words', re.I)
    opt_prefix_pat = re.compile(r'^\s*[A-Ca-c]([\.\)]|\s+)\s*') 
    labels = ["a", "b", "c"]
    MAX_OPTIONS = 3

    def finalize_current_question(q_dict, q_list):
        if q_dict["question"]:
            if not q_dict["answer"] and q_dict["options"]:
                q_dict["answer"] = q_dict["options"][0] 
            q_list.append(q_dict)
        return {"question": "", "options": [], "answer": ""}
    
    for p_data in data:
        clean_p = clean_text(p_data["full_text"])
        if not clean_p: continue
        
        is_q_start_phrased = phrase_start_pat.search(clean_p)
        is_explicitly_numbered = q_start_pat.match(clean_p) 
        is_max_options_reached = len(current["options"]) >= MAX_OPTIONS
        is_question_started = current["question"]
        is_first_line = not is_question_started and not current["options"]
        
        must_switch_q = (
            is_first_line or                            
            is_q_start_phrased or                       
            (is_question_started and is_max_options_reached)
        )
        
        if must_switch_q:
            current = finalize_current_question(current, questions)
            q_text = clean_p
            if is_explicitly_numbered:
                q_text = q_start_pat.sub('', clean_p).strip()
            current["question"] = q_text
            
        else:
            if is_question_started and not is_max_options_reached:
                is_correct = False
                
                # SỬ DỤNG LOGIC DẤU (*)
                if "(*)" in clean_p:
                    is_correct = True
                    clean_p = clean_p.replace("(*)", "").strip() # Loại bỏ ký hiệu sau khi phát hiện
                
                match_prefix = opt_prefix_pat.match(clean_p)
                if match_prefix:
                    clean_p = clean_p[match_prefix.end():].strip()
                    
                idx = len(current["options"])
                if idx < len(labels):
                    label = labels[idx]
                    opt_text = f"{label}. {clean_p}"
                    current["options"].append(opt_text)
                    
                    if is_correct:
                        current["answer"] = opt_text
            
            elif is_question_started:
                 current["question"] += " " + clean_p
        
            elif not is_question_started and not current["options"]:
                current["question"] = clean_p

    current = finalize_current_question(current, questions)
        
    return questions

# ====================================================
# 🧩 PARSER 5: PHỤ LỤC 3 - BÀI ĐỌC HIỂU (PASSAGE-BASED) - ĐÃ SỬA LỖI PARAGRAPH 2
# ====================================================
# ... (parse_pl3_passage_bank remains unchanged)
def parse_pl3_passage_bank(source):
    """
    Parser cho định dạng PL3 (Bài đọc hiểu)
    - Fix: Xử lý đúng cho câu hỏi điền chỗ trống (Paragraph 2) bằng cách tạo câu hỏi tường minh.
    """
    path = find_file_path(source)
    if not path:
        print(f"Lỗi không tìm thấy file DOCX: {source}")
        return []
    
    questions = []
    current_group = None
    group_content = ""
    current_q_num = 0
    
    # Regex cho tiêu đề đoạn văn mới
    paragraph_start_pat = re.compile(r'^\s*Paragraph\s*(\d+)\s*\.\s*', re.I)
    # Regex cho số thứ tự câu hỏi
    q_start_pat = re.compile(r'^\s*(?P<q_num>\d+)\s*[\.\)]\s*', re.I)
    # Regex cho đáp án, bao gồm ký tự (*)
    opt_pat_single = re.compile(r'^\s*(?P<letter>[A-Da-d])[\.\)]\s*(?P<text>.*?)(\s*\(\*\))?$', re.I)
    
    try:
        doc = Document(path)
    except Exception as e:
        print(f"Lỗi đọc file DOCX: {source}. Chi tiết: {e}")
        return []

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if not text: continue
        
        is_new_paragraph_group = paragraph_start_pat.match(text)
        match_q_start = q_start_pat.match(text)
        
        # 1. BẮT ĐẦU NHÓM ĐOẠN VĂN MỚI
        if is_new_paragraph_group:
            # Lưu câu hỏi/group cũ nếu có
            if current_group is not None and current_group.get('question'):
                questions.append(current_group)
            
            group_name = is_new_paragraph_group.group(0).strip()
            current_group = {
                'group_name': group_name,
                'paragraph_content': "",
                'question': "",
                'options': {},
                'correct_answer': "",
                'number': 0
            }
            group_content = "" # Reset nội dung đoạn văn
            current_q_num = 0 # Reset số thứ tự câu hỏi
            continue
            
        if current_group is None:
            # Bỏ qua nếu chưa bắt đầu Paragraph X .
            continue
            
        # 2. BẮT ĐẦU CÂU HỎI MỚI
        if match_q_start:
            # Lưu câu hỏi cũ nếu có
            if current_group.get('question') and current_group.get('options'):
                 questions.append(current_group)
            
            q_num_str = match_q_start.group('q_num')
            remaining_text = text[match_q_start.end():].strip()
            
            # --- XÁC ĐỊNH LOẠI CÂU HỎI & NỘI DUNG ---
            # Type B: Fill-in-the-blank (Passage content contains patterns like (1), (2)...)
            # Check for fill-in-the-blank context inside the collected passage content
            is_fill_in_blank = bool(re.search(r'\(\s*\d+\s*\)', group_content))
            
            if is_fill_in_blank:
                # Type B: Question is implicit, remaining text is the first option (A.)
                q_text = f"Chọn đáp án thích hợp cho ô trống **({q_num_str})** trong đoạn văn trên."
                first_option_text = remaining_text # This is the first option (A.)
            else:
                # Type A: Reading Comp. Remaining text is the question body.
                q_text = remaining_text
                first_option_text = ""
            
            # Bắt đầu câu hỏi mới
            current_group = {
                'group_name': current_group['group_name'],
                # Gán nội dung đoạn văn đã thu thập
                'paragraph_content': group_content.strip(), 
                'question': clean_text(q_text),
                'options': {},
                'correct_answer': "",
                # Gán số thứ tự câu hỏi cục bộ (local number)
                'number': int(q_num_str) 
            }
            current_q_num = int(q_num_str)
            
            # Process the first option (if Fill-in-the-blank mode)
            if is_fill_in_blank and first_option_text:
                match_opt = opt_pat_single.match(first_option_text)
                if match_opt:
                    letter = match_opt.group('letter').upper()
                    opt_text_raw = match_opt.group('text').strip()
                    is_correct = match_opt.group(3) is not None
                    
                    opt_text = clean_text(opt_text_raw.replace("(*)", "").strip())
                    full_opt_text = f"{letter}. {opt_text}"
                    
                    current_group['options'][letter] = full_opt_text
                    if is_correct:
                        current_group['correct_answer'] = letter
            
        # 3. ĐANG TRONG CÂU HỎI (Option hoặc phần tiếp theo của câu hỏi)
        elif current_q_num > 0:
            match_opt = opt_pat_single.match(text)
            if match_opt:
                # Xử lý các options B., C. cho cả hai loại câu hỏi
                letter = match_opt.group('letter').upper()
                opt_text_raw = match_opt.group('text').strip()
                is_correct = match_opt.group(3) is not None
                
                # Loại bỏ ký tự thừa (*), sau đó clean text
                opt_text = clean_text(opt_text_raw.replace("(*)", "").strip())
                
                # Lấy toàn bộ text để hiển thị (bao gồm cả ký tự A. B. C.)
                full_opt_text = f"{letter}. {opt_text}"
                
                # Dùng chữ cái làm key để dễ dàng tìm đáp án đúng
                current_group['options'][letter] = full_opt_text
                
                if is_correct:
                    current_group['correct_answer'] = letter
            else:
                # Nếu không phải option, thêm vào câu hỏi (chỉ áp dụng cho Reading Comp - Type A)
                current_group['question'] += " " + clean_text(text)
                
        # 4. ĐANG THU THẬP NỘI DUNG ĐOẠN VĂN
        elif current_group is not None and current_q_num == 0 and not is_new_paragraph_group:
            # Dùng paragraph.text + "\n" để giữ nguyên bố cục xuống dòng
            group_content += paragraph.text + "\n"
        
    # Lưu câu hỏi cuối cùng
    if current_group is not None and current_group.get('question'):
        questions.append(current_group)

    # Chuẩn hóa cấu trúc để tương thích với các hàm hiển thị khác
    final_questions = []
    
    # Gán số thứ tự toàn cục (global number) cho mỗi câu hỏi
    global_q_counter = 1 
    for q in questions:
        if not q.get('correct_answer') and len(q.get('options', {})) > 0:
             # Nếu không có (*), coi option đầu là đúng (hoặc bỏ qua nếu cần nghiêm ngặt hơn)
             q['correct_answer'] = list(q['options'].keys())[0]
        
        # Nếu vẫn không có đáp án hoặc không có options, bỏ qua
        if not q.get('correct_answer') or not q.get('options'):
            continue
        
        # Chuyển options từ dict sang list of strings (chỉ values)
        options_list = list(q['options'].values()) 
        
        final_questions.append({
            'question': q['question'],
            'options': options_list, 
            'answer': q['options'][q['correct_answer']], # Lưu đáp án đúng dưới dạng string (A. Text)
            'number': q['number'], # Số thứ tự câu hỏi cục bộ (1, 2, 3...)
            'global_number': global_q_counter, # Bổ sung số thứ tự toàn cục
            # Sử dụng 'group' thay cho 'group_name' để tương thích với display_all_questions/test_mode 
            'group': q['group_name'], 
            'paragraph_content': q['paragraph_content'] # Nội dung đoạn văn
        })
        global_q_counter += 1

    return final_questions
def parse_pl4_passage_bank(source):
    path = find_file_path(source)
    if not path: return []
    
    questions = []
    doc = Document(path)
    
    current_paragraph_text = ""
    current_questions_in_para = []
    
    # Regex
    para_header_pat = re.compile(r'^\s*Paragraph\s*\d+', re.I)
    q_start_pat = re.compile(r'^\s*(?P<q_num>\d+)\s*[\.\)]\s*(?P<content>.*)', re.I)
    opt_pat = re.compile(r'^\s*(?P<letter>[A-Da-d])[\.\)]\s*(?P<text>.*?)(\s*\(\*\))?$', re.I)

    lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Nếu gặp tiêu đề Paragraph mới
        if para_header_pat.match(line):
            # Lưu nhóm cũ trước khi sang nhóm mới
            if current_paragraph_text and current_questions_in_para:
                for q in current_questions_in_para:
                    q['paragraph_content'] = current_paragraph_text
                    questions.append(q)
            
            current_paragraph_text = ""
            current_questions_in_para = []
            group_name = line
            i += 1
            
            # Đọc nội dung đoạn văn cho đến khi gặp câu hỏi đầu tiên
            while i < len(lines) and not q_start_pat.match(lines[i]):
                current_paragraph_text += lines[i] + "\n"
                i += 1
            continue

        # Nếu gặp câu hỏi
        q_match = q_start_pat.match(line)
        if q_match:
            q_num = q_match.group('q_num')
            q_text = q_match.group('content')
            
            # Check nếu là dạng điền từ (đoạn văn có chứa (1), (2)...)
            if f"({q_num})" in current_paragraph_text or f" {q_num}. " in current_paragraph_text:
                actual_q_text = f"Chọn đáp án đúng cho vị trí **({q_num})**"
                # Nếu dòng câu hỏi chứa luôn Option A
                opt_inline = opt_pat.match(q_text)
                options = {}
                ans = ""
                if opt_inline:
                    letter = opt_inline.group('letter').upper()
                    txt = opt_inline.group('text').replace("(*)", "").strip()
                    options[letter] = f"{letter}. {txt}"
                    if "(*)" in q_text: ans = options[letter]
                    q_text = "" # Đã dùng làm option
                else:
                    q_text = actual_q_text
            
            new_q = {
                'group': group_name if 'group_name' in locals() else "Bài đọc",
                'question': q_text,
                'options': options if 'options' in locals() else {},
                'answer': ans if 'ans' in locals() else "",
                'number': int(q_num)
            }
            
            i += 1
            # Đọc các Option tiếp theo
            while i < len(lines):
                opt_match = opt_pat.match(lines[i])
                if opt_match:
                    letter = opt_match.group('letter').upper()
                    txt = opt_match.group('text').replace("(*)", "").strip()
                    new_q['options'][letter] = f"{letter}. {txt}"
                    if "(*)" in lines[i]:
                        new_q['answer'] = new_q['options'][letter]
                    i += 1
                elif q_start_pat.match(lines[i]) or para_header_pat.match(lines[i]):
                    break
                else:
                    new_q['question'] += " " + lines[i]
                    i += 1
            
            # Chuyển dict options thành list
            new_q['options'] = list(new_q['options'].values())
            current_questions_in_para.append(new_q)
        else:
            i += 1

    # Lưu đoạn cuối cùng
    if current_paragraph_text and current_questions_in_para:
        for q in current_questions_in_para:
            q['paragraph_content'] = current_paragraph_text
            questions.append(q)
            
    return questions

          
# ====================================================
# 🌟 HÀM: LOGIC DỊCH ĐỘC QUYỀN (EXCLUSIVE TRANSLATION)
# ====================================================
if 'active_translation_key' not in st.session_state: st.session_state.active_translation_key = None
# Thêm trạng thái cho dịch đoạn văn
if 'active_passage_translation' not in st.session_state: st.session_state.active_passage_translation = None
if 'passage_translations_cache' not in st.session_state: st.session_state.passage_translations_cache = {}

def on_translate_toggle(key_clicked):
    """Callback function để quản lý chế độ Dịch ĐỘC QUYỀN (Q&A)."""
    toggle_key = f"toggle_{key_clicked}"
    # Check the state of the toggle in session state (it is the state *after* the click)
    is_on_after_click = st.session_state.get(toggle_key, False)
    
    if is_on_after_click:
        # User turned this specific toggle ON -> Make it the active key
        st.session_state.active_translation_key = key_clicked
    elif st.session_state.active_translation_key == key_clicked:
        # User turned this specific toggle OFF -> Clear the active key
        st.session_state.active_translation_key = None
    
def on_passage_translate_toggle(passage_id_clicked):
    """Callback function để quản lý chế độ Dịch ĐỘC QUYỀN (Passage)."""
    toggle_key = f"toggle_passage_{passage_id_clicked}"
    is_on_after_click = st.session_state.get(toggle_key, False)

    if is_on_after_click:
        # User turned this specific toggle ON -> Make it the active passage key
        st.session_state.active_passage_translation = passage_id_clicked
    elif st.session_state.active_passage_translation == passage_id_clicked:
        # User turned this specific toggle OFF -> Clear the active key
        st.session_state.active_passage_translation = None

# ====================================================
# 🌟 HÀM: XEM TOÀN BỘ CÂU HỎI (CẬP NHẬT CHỨC NĂNG DỊCH)
# ====================================================
def display_all_questions(questions):
    st.markdown('<div class="result-title"><h3>📚 TOÀN BỘ NGÂN HÀNG CÂU HỎI</h3></div>', unsafe_allow_html=True)
    if not questions:
        st.warning("Không có câu hỏi nào để hiển thị.")
        return
    
    # Logic hiển thị đoạn văn (nếu có)
    current_passage_id = None
    
    for i, q in enumerate(questions, start=1):
        q_key = f"all_q_{i}_{hash(q['question'])}" 
        translation_key = f"trans_{q_key}"
        is_active = (translation_key == st.session_state.active_translation_key)
        
        # --- BỔ SUNG: HIỂN THỊ ĐOẠN VĂN (CHO PL3) ---
        passage_content = q.get('paragraph_content', '').strip()
        group_name = q.get('group', '')
        
        if passage_content:
             # Dùng group_name + content để tạo ID duy nhất cho đoạn văn
            passage_id = f"passage_{group_name}_{hash(passage_content)}"
            is_passage_active = (passage_id == st.session_state.active_passage_translation)

            if passage_id != current_passage_id:
                # 1. In đậm, đổi màu tiêu đề
                st.markdown(f'<div class="paragraph-title">**{group_name}**</div>', unsafe_allow_html=True) 
                
                # 2. Hiển thị nội dung đoạn văn gốc
                st.markdown(f'<div class="paragraph-content-box">{passage_content}</div>', unsafe_allow_html=True)
                
                # 3. Thêm Nút Dịch Đoạn Văn
                st.toggle(
                    "🌐 Dịch đoạn văn sang Tiếng Việt", 
                    value=is_passage_active, 
                    key=f"toggle_passage_{passage_id}",
                    on_change=on_passage_translate_toggle,
                    args=(passage_id,)
                )
                
                # 4. Hiển thị Bản Dịch Đoạn Văn
                if is_passage_active:
                    translated_passage = st.session_state.passage_translations_cache.get(passage_id)
                    if not isinstance(translated_passage, str):
                        # GỌI HÀM DỊCH CHỈ ĐOẠN VĂN
                        translated_passage = translate_passage_content(passage_content)
                        st.session_state.passage_translations_cache[passage_id] = translated_passage

                    # Sử dụng st.markdown + CSS để ép kiểu 'pre-wrap'
                    st.markdown(f"""
                    <div data-testid="stAlert" class="stAlert stAlert-info">
                        <div style="font-size: 18px; line-height: 1.6; color: white; padding: 10px;">
                            <strong style="color: #FFD700;">[Bản dịch Đoạn văn]</strong>
                            <div class="paragraph-content-box" style="white-space: pre-wrap; margin-bottom: 0px; padding: 10px; background-color: rgba(0, 0, 0, 0.5); border-left: 3px solid #00d4ff;">
                            {translated_passage}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                current_passage_id = passage_id
        # --- KẾT THÚC BỔ SUNG ---
        
        # Hiển thị câu hỏi (SỬ DỤNG SỐ THỨ TỰ CỤC BỘ NẾU LÀ PL3, NẾU KHÔNG DÙNG SỐ THỨ TỰ TOÀN CỤC)
        if q.get('group', '').startswith('Paragraph'):
            # Dùng số thứ tự cục bộ (number) nếu là bài đọc hiểu
            display_num = q.get('number', i) 
        else:
             # Dùng số thứ tự toàn cục (i) cho các ngân hàng khác
            display_num = i 
            
        st.markdown(f'<div class="bank-question-text">{display_num}. {q["question"]}</div>', unsafe_allow_html=True)

        # Nút Dịch Q&A ở dưới
        st.toggle(
            "🌐 Dịch Câu hỏi & Đáp án sang Tiếng Việt", 
            value=is_active, 
            key=f"toggle_{translation_key}",
            on_change=on_translate_toggle,
            args=(translation_key,)
        )

        # Hiển thị Bản Dịch Q&A
        if is_active:
            # Check if translated content is already cached
            translated_content = st.session_state.translations.get(translation_key)
            
            # If not cached or is not a string (default True/False state)
            if not isinstance(translated_content, str):
                # GỌI HÀM MỚI ĐỂ GỬI CHỈ CÂU HỎI VÀ ĐÁP ÁN ĐI DỊCH
                full_text_to_translate = build_translation_text_for_qa(q) 
                st.session_state.translations[translation_key] = translate_text(full_text_to_translate)
                translated_content = st.session_state.translations[translation_key]

            st.info(translated_content, icon="🌐")
            
        # Hiển thị Đáp án
        for opt in q["options"]:
            # Dùng clean_text để so sánh, bỏ qua khoảng trắng, ký tự ẩn
            if clean_text(opt) == clean_text(q["answer"]):
                # Đáp án đúng: Xanh lá (Thêm ký tự (*))
                color_style = "color:#00ff00;" 
                opt_display = opt + " (*)"
            else:
                # Đáp án thường: Trắng (Bỏ shadow)
                color_style = "color:#FFFFFF;"
                opt_display = opt
                
            st.markdown(f'<div class="bank-answer-text" style="{color_style}">{opt_display}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)

# ====================================================
# 🌟 HÀM: TEST MODE (CẬP NHẬT CHỨC NĂNG DỊCH)
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
    
    score = 0 # Khởi tạo biến score ở đây

    if not st.session_state[f"{test_key_prefix}_started"]:
        st.markdown('<div class="result-title"><h3>📝 LÀM BÀI TEST 50 CÂU</h3></div>', unsafe_allow_html=True)
        
        if st.button("🚀 Bắt đầu Bài Test", key=f"{test_key_prefix}_start_btn"):
            st.session_state[f"{test_key_prefix}_questions"] = get_random_questions(questions, TOTAL_QUESTIONS)
            st.session_state[f"{test_key_prefix}_started"] = True
            st.session_state[f"{test_key_prefix}_submitted"] = False
            st.session_state.current_mode = "test" 
            st.rerun()
        return

    # Logic hiển thị đoạn văn trong Test Mode (chỉ hiển thị 1 lần cho mỗi đoạn)
    test_batch = st.session_state[f"{test_key_prefix}_questions"]
    current_passage_id = None

    if not st.session_state[f"{test_key_prefix}_submitted"]:
        st.markdown('<div class="result-title"><h3>⏳ ĐANG LÀM BÀI TEST</h3></div>', unsafe_allow_html=True)
        for i, q in enumerate(test_batch, start=1):
            q_key = f"{test_key_prefix}_q_{i}_{hash(q['question'])}" 
            translation_key = f"trans_{q_key}"
            is_active = (translation_key == st.session_state.active_translation_key)
            
            # --- BỔ SUNG: HIỂN THỊ ĐOẠN VĂN (CHO PL3) ---
            passage_content = q.get('paragraph_content', '').strip()
            group_name = q.get('group', '')
            
            if passage_content:
                passage_id = f"passage_{group_name}_{hash(passage_content)}"
                is_passage_active = (passage_id == st.session_state.active_passage_translation)

                if passage_id != current_passage_id:
                     # 1. In đậm, đổi màu tiêu đề
                    st.markdown(f'<div class="paragraph-title">**{group_name}**</div>', unsafe_allow_html=True) 
                    
                    # 2. Hiển thị nội dung đoạn văn gốc
                    st.markdown(f'<div class="paragraph-content-box">{passage_content}</div>', unsafe_allow_html=True)
                    
                    # 3. Thêm Nút Dịch Đoạn Văn
                    st.toggle(
                        "🌐 Dịch đoạn văn sang Tiếng Việt", 
                        value=is_passage_active, 
                        key=f"toggle_passage_{passage_id}",
                        on_change=on_passage_translate_toggle,
                        args=(passage_id,)
                    )
                    
                    # 4. Hiển thị Bản Dịch Đoạn Văn
                    if is_passage_active:
                        translated_passage = st.session_state.passage_translations_cache.get(passage_id)
                        if not isinstance(translated_passage, str):
                            # GỌI HÀM DỊCH CHỈ ĐOẠAN VĂN
                            translated_passage = translate_passage_content(passage_content)
                            st.session_state.passage_translations_cache[passage_id] = translated_passage

                        st.markdown(f"""
                        <div data-testid="stAlert" class="stAlert stAlert-info">
                            <div style="font-size: 18px; line-height: 1.6; color: white; padding: 10px;">
                                <strong style="color: #FFD700;">[Bản dịch Đoạn văn]</strong>
                                <div class="paragraph-content-box" style="white-space: pre-wrap; margin-bottom: 0px; padding: 10px; background-color: rgba(0, 0, 0, 0.5); border-left: 3px solid #00d4ff;">
                                {translated_passage}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("---")
                    current_passage_id = passage_id
            # --- KẾT THÚC BỔ SUNG ---

            # Hiển thị câu hỏi (SỬ DỤNG SỐ THỨ TỰ CỤC BỘ NẾU LÀ PL3, NẾU KHÔNG DÙNG SỐ THỨ TỰ TOÀN CỤC)
            if q.get('group', '').startswith('Paragraph'):
                # Dùng số thứ tự cục bộ (number) nếu là bài đọc hiểu
                display_num = q.get('number', i) 
            else:
                # Dùng số thứ tự toàn cục (i) cho các ngân hàng khác
                display_num = i
            st.markdown(f'<div class="bank-question-text">{display_num}. {q["question"]}</div>', unsafe_allow_html=True)

            # Nút Dịch Q&A ở dưới
            st.toggle(
                "🌐 Dịch Câu hỏi & Đáp án sang Tiếng Việt", 
                value=is_active, 
                key=f"toggle_{translation_key}",
                on_change=on_translate_toggle,
                args=(translation_key,)
            )

            # Hiển thị Bản Dịch Q&A
            if is_active:
                translated_content = st.session_state.translations.get(translation_key)
                
                if not isinstance(translated_content, str):
                    # GỌI HÀM MỚI ĐỂ GỬI CHỈ CÂU HỎI VÀ ĐÁP ÁN ĐI DỊCH
                    full_text_to_translate = build_translation_text_for_qa(q)
                    st.session_state.translations[translation_key] = translate_text(full_text_to_translate)
                    translated_content = st.session_state.translations[translation_key]

                st.info(translated_content, icon="🌐")

            # Hiển thị Radio Button
            default_val = st.session_state.get(q_key, q["options"][0] if q["options"] else None)
            st.radio("", q["options"], index=q["options"].index(default_val) if default_val in q["options"] else 0, key=q_key)
            st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
            
        if st.button("✅ Nộp bài Test", key=f"{test_key_prefix}_submit_btn"):
            st.session_state[f"{test_key_prefix}_submitted"] = True
            st.session_state.active_translation_key = None # Tắt dịch Q&A khi nộp
            st.session_state.active_passage_translation = None # Tắt dịch Passage khi nộp
            st.rerun()
            
    else:
        st.markdown('<div class="result-title"><h3>🎉 KẾT QUẢ BÀI TEST</h3></div>', unsafe_allow_html=True)
        
        for i, q in enumerate(test_batch, start=1):
            q_key = f"{test_key_prefix}_q_{i}_{hash(q['question'])}" 
            selected_opt = st.session_state.get(q_key)
            correct = clean_text(q["answer"])
            is_correct = clean_text(selected_opt) == correct
            translation_key = f"trans_{q_key}"
            is_active = (translation_key == st.session_state.active_translation_key)

            # --- BỔ SUNG: HIỂN THỊ ĐOẠN VĂN (CHO PL3) ---
            passage_content = q.get('paragraph_content', '').strip()
            group_name = q.get('group', '')
            
            if passage_content:
                passage_id = f"passage_{group_name}_{hash(passage_content)}"
                is_passage_active = (passage_id == st.session_state.active_passage_translation)

                if passage_id != current_passage_id:
                     # 1. In đậm, đổi màu tiêu đề
                    st.markdown(f'<div class="paragraph-title">**{group_name}**</div>', unsafe_allow_html=True) 
                    
                    # 2. Hiển thị nội dung đoạn văn gốc
                    st.markdown(f'<div class="paragraph-content-box">{passage_content}</div>', unsafe_allow_html=True)
                    
                    # 3. Thêm Nút Dịch Đoạn Văn
                    st.toggle(
                        "🌐 Dịch đoạn văn sang Tiếng Việt", 
                        value=is_passage_active, 
                        key=f"toggle_passage_{passage_id}",
                        on_change=on_passage_translate_toggle,
                        args=(passage_id,)
                    )
                    
                    # 4. Hiển thị Bản Dịch Đoạn Văn
                    if is_passage_active:
                        translated_passage = st.session_state.passage_translations_cache.get(passage_id)
                        if not isinstance(translated_passage, str):
                            # GỌI HÀM DỊCH CHỈ ĐOẠN VĂN
                            translated_passage = translate_passage_content(passage_content)
                            st.session_state.passage_translations_cache[passage_id] = translated_passage

                        st.markdown(f"""
                        <div data-testid="stAlert" class="stAlert stAlert-info">
                            <div style="font-size: 18px; line-height: 1.6; color: white; padding: 10px;">
                                <strong style="color: #FFD700;">[Bản dịch Đoạn văn]</strong>
                                <div class="paragraph-content-box" style="white-space: pre-wrap; margin-bottom: 0px; padding: 10px; background-color: rgba(0, 0, 0, 0.5); border-left: 3px solid #00d4ff;">
                                {translated_passage}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("---")
                    current_passage_id = passage_id
            # --- KẾT THÚC BỔ SUNG ---

            # Hiển thị câu hỏi (SỬ DỤNG SỐ THỨ TỰ CỤC BỘ NẾU LÀ PL3, NẾU KHÔNG DÙNG SỐ THỨ TỰ TOÀN CỤC)
            if q.get('group', '').startswith('Paragraph'):
                # Dùng số thứ tự cục bộ (number) nếu là bài đọc hiểu
                display_num = q.get('number', i) 
            else:
                # Dùng số thứ tự toàn cục (i) cho các ngân hàng khác
                display_num = i
            st.markdown(f'<div class="bank-question-text">{display_num}. {q["question"]}</div>', unsafe_allow_html=True)

            # Nút Dịch Q&A ở dưới
            st.toggle(
                "🌐 Dịch Câu hỏi & Đáp án sang Tiếng Việt", 
                value=is_active, 
                key=f"toggle_{translation_key}",
                on_change=on_translate_toggle,
                args=(translation_key,)
            )

            # Hiển thị Bản Dịch Q&A
            if is_active:
                translated_content = st.session_state.translations.get(translation_key)
                
                if not isinstance(translated_content, str):
                    # GỌI HÀM MỚI ĐỂ GỬI CHỈ CÂU HỎI VÀ ĐÁP ÁN ĐI DỊCH
                    full_text_to_translate = build_translation_text_for_qa(q)
                    st.session_state.translations[translation_key] = translate_text(full_text_to_translate)
                    translated_content = st.session_state.translations[translation_key]

                st.info(translated_content, icon="🌐")
            
            # Hiển thị Đáp án (KẾT QUẢ)
            for opt in q["options"]:
                opt_clean = clean_text(opt)
                opt_display = opt # Khởi tạo giá trị hiển thị

                if opt_clean == correct:
                    color_style = "color:#00ff00;"
                    opt_display += " (*)" # BỔ SUNG: Thêm ký tự (*)
                elif opt_clean == clean_text(selected_opt):
                    color_style = "color:#ff3333;"
                else:
                    color_style = "color:#FFFFFF;"
                    
                st.markdown(f'<div class="bank-answer-text" style="{color_style}">{opt_display}</div>', unsafe_allow_html=True)

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

# === CSS CẬP NHẬT CHO ĐOẠN VĂN (PARAGRAPH) ===
css_style = f"""
<style>
/* Đã thống nhất font nội dung là Oswald, tiêu đề là Playfair Display */
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

/* Số 1 */
.number-one {{
    font-family: 'Oswald', sans-serif !important;
    font-size: 1em !important; 
    font-weight: 700;
    display: inline-block;
}}

.main > div:first-child {{
    padding-top: 40px !important; padding-bottom: 2rem !important;
}}

/* SUB-TITLE & RESULT TITLE */
#sub-static-title, .result-title {{
    margin-top: 150px;
    margin-bottom: 30px; text-align: center;
}}
#sub-static-title h2, .result-title h3 {{
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    color: #FFEA00;
    text-shadow: 0 0 15px #FFEA00;
}}

/* === BỔ SUNG CSS CHO ĐOẠN VĂN (PL3) === */

/* Tiêu đề Paragraph X . (In đậm, màu cam) */
.paragraph-title {{
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    font-weight: 900;
    color: #FFA500; /* Màu cam nổi bật */
    text-shadow: 0 0 8px rgba(255, 165, 0, 0.5);
    margin-top: 20px;
    margin-bottom: 10px;
    padding: 5px 15px;
    background-color: rgba(30, 30, 30, 0.8);
    border-radius: 8px;
    display: inline-block;
}}

/* Nội dung đoạn văn (Giữ nguyên bố cục xuống dòng) */
.paragraph-content-box {{
    /* Dùng 'white-space: pre-wrap' để giữ nguyên khoảng trắng và ngắt dòng */
    white-space: pre-wrap; 
    font-family: 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif !important;
    font-size: 20px !important; 
    line-height: 1.6;
    color: #F0F0F0; /* Màu trắng nhạt */
    padding: 15px;
    background-color: rgba(0, 0, 0, 0.7);
    border-radius: 8px;
    margin-bottom: 20px;
    border-left: 3px solid #FFA500;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
}}


/* STYLE CÂU HỎI - PC (NỀN ĐEN BAO VỪA CHỮ) */
.bank-question-text {{
    color: #FF8C00 !important;
    font-weight: 900 !important;
    letter-spacing: 0.5px !important;
    font-size: 22px !important; 
    font-family: 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif !important;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
    padding: 8px 15px;
    margin-bottom: 10px;
    line-height: 1.4 !important;
    background-color: rgba(0, 0, 0, 0.75);
    border-radius: 8px;
    display: inline-block; /* BAO VỪA CHỮ */
    max-width: 100%;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
}}

/* STYLE ĐÁP ÁN - PC (TRẮNG ĐẬM HƠN) */
.bank-answer-text {{
    font-family: 'Oswald', sans-serif !important;
    font-weight: 900 !important;
    font-size: 22px !important; 
    padding: 5px 15px;
    margin: 2px 0;
    line-height: 1.5 !important; 
    display: block;
    color: #FFFFFF !important;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.9); /* SHADOW ĐẬM HƠN */
}}

/* RADIO BUTTONS (CHỌN ĐÁP ÁN) */
.stRadio label {{
    color: #FFFFFF !important;
    font-size: 22px !important; 
    font-weight: 900 !important; /* ĐẬM HƠN */
    font-family: 'Oswald', sans-serif !important;
    padding: 2px 12px;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.9) !important; /* SHADOW ĐẬM HƠN */
    background-color: transparent !important;
    border: none !important;
    display: block !important;
    margin: 4px 0 !important;
    letter-spacing: 0.5px !important;
}}

.stRadio label:hover {{
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.9) !important;
}}

.stRadio label span, 
.stRadio label p,
.stRadio label div {{
    color: #FFFFFF !important;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.9) !important;
    letter-spacing: 0.5px !important;
}}

div[data-testid="stMarkdownContainer"] p {{
    font-size: 22px !important; 
}}

/* STYLE NÚT ACTION (ĐẸP VÀ BÓNG BẨY) */
.stButton>button {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: #ffffff !important;
    border-radius: 12px !important;
    font-size: 1.2em !important;
    font-weight: 700 !important;
    font-family: 'Oswald', sans-serif !important; 
    border: 2px solid rgba(255, 255, 255, 0.3) !important;
    padding: 12px 24px !important;
    width: 100% !important;
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    transition: all 0.3s ease !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}}

.stButton>button:hover {{
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
    box-shadow: 0 8px 25px rgba(118, 75, 162, 0.6) !important;
    transform: translateY(-2px) !important;
    border-color: rgba(255, 255, 255, 0.5) !important;
}}

.stButton>button:active {{
    transform: translateY(0) !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
}}

/* STYLE CHO NÚT DỊCH (st.toggle) */
div[data-testid="stCheckbox"] label p,
div[data-testid="stCheckbox"] label span,
div[data-testid="stCheckbox"] label div,
div[data-testid="stCheckbox"] label,
div[data-testid="stCheckbox"] p,
div[data-testid="stCheckbox"] span,
div[data-testid="stCheckbox"] div,
.stCheckbox label p,
.stCheckbox label span, 
.stCheckbox label,
.stCheckbox p,
.stCheckbox span {{
    color: #FFEA00 !important;
    font-size: 20px !important;
    font-weight: 700 !important;
}}

.stToggle label p {{
    font-size: 20px !important;
    font-weight: 700 !important;
    padding: 0;
    margin: 0;
    line-height: 1 !important;
    color: #FFEA00 !important;
}}
.stToggle label,
.stToggle label span,
.stToggle label div,
.stToggle label > div[data-testid="stMarkdownContainer"],
.stToggle label > div[data-testid="stMarkdownContainer"] p,
.stToggle label > div[data-testid="stMarkdownContainer"] span,
.stToggle label * {{
    color: #FFEA00 !important;
    font-size: 20px !important;
    font-weight: 700 !important;
}}
.stToggle > label > div[data-testid="stMarkdownContainer"] {{
    margin-top: 10px !important; 
}}

/* Force màu vàng cho toggle text */
[data-testid="stMarkdownContainer"] > p {{
    color: inherit !important;
}}
.stToggle [data-testid="stMarkdownContainer"] > p {{
    color: #FFEA00 !important;
}}

div.stSelectbox label p {{
    color: #33FF33 !important;
    font-size: 1.25rem !important;
    font-family: 'Oswald', sans-serif !important;
}}

/* STYLE CHO KHUNG DỊCH - ÁP DỤNG CHO CẢ PC & MOBILE */
div[data-testid="stAlert"] {{
    background-color: rgba(30, 30, 30, 0.95) !important;
    border-left: 4px solid #00d4ff !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3) !important;
}}

div[data-testid="stAlert"] *,
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] strong,
div[data-testid="stAlert"] em,
div[data-testid="stAlert"] li,
div[data-testid="stAlert"] span,
div[data-testid="stAlert"] div {{
    color: #FFFFFF !important;
    font-size: 18px !important;
    line-height: 1.6 !important;
}}

div[data-testid="stAlert"] strong {{
    color: #FFD700 !important;
    font-weight: 900 !important;
}}

/* MOBILE RESPONSIVE */
@media (max-width: 768px) {{
    #back-to-home-btn-container {{ top: 5px; left: 5px; }}
    #main-title-container {{ height: 100px; padding-top: 10px; }}
    #main-title-container h1 {{ font-size: 8vw; line-height: 1.5 !important; }}
    .main > div:first-child {{ padding-top: 20px !important; }}
    
    /* Chỉnh kích thước tiêu đề trên mobile - FIX HIỂN THỊ ĐẦY ĐỦ */
    #sub-static-title h2, 
    .result-title h3 {{
        font-size: 1.1rem !important; /* NHỎ HƠN ĐỂ VỪA 1 HÀNG */
        white-space: normal !important; /* CHO PHÉP XUỐNG DÒNG */
        overflow: visible !important;
        text-overflow: clip !important;
        padding: 0 10px !important;
        line-height: 1.3 !important;
    }}
    
    /* Màu vàng cho câu hỏi trên mobile */
    .bank-question-text {{
        color: #FFFF00 !important;
        background-color: rgba(0, 0, 0, 0.75) !important;
        display: inline-block !important; /* BAO VỪA CHỮ */
    }}
    
    /* Nút trên mobile */
    .stButton>button {{
        font-size: 1em !important;
        padding: 10px 18px !important;
    }}
    
    /* Cập nhật mobile cho đoạn văn */
    .paragraph-title {{
        font-size: 1.2rem;
        padding: 5px 10px;
        margin-top: 10px;
    }}
    .paragraph-content-box {{
        font-size: 16px !important; 
        line-height: 1.4;
        padding: 10px;
    }}
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
        <a id="manual-home-btn" 
           href="/?skip_intro=1" 
           onclick="window.location.href = this.href; return false;" 
           target="_self">🏠 Về Trang Chủ</a>
    </div>
    <div id="main-title-container"><h1>Tổ Bảo Dưỡng Số <span class="number-one">1</span></h1></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div id="sub-static-title"><h2>NGÂN HÀNG TRẮC NGHIỆM</h2></div>', unsafe_allow_html=True)

if "current_group_idx" not in st.session_state: st.session_state.current_group_idx = 0
if "submitted" not in st.session_state: st.session_state.submitted = False
if "current_mode" not in st.session_state: st.session_state.current_mode = "group"
if "last_bank_choice" not in st.session_state: st.session_state.last_bank_choice = "----" 
if "doc_selected" not in st.session_state: st.session_state.doc_selected = "Phụ lục 1 : Ngữ pháp chung" 
if 'translations' not in st.session_state: st.session_state.translations = {} # KHỞI TẠO STATE DỊCH THUẬT Q&A
if 'active_translation_key' not in st.session_state: st.session_state.active_translation_key = None # KHỞI TẠO KEY DỊCH Q&A ĐỘC QUYỀN
if 'active_passage_translation' not in st.session_state: st.session_state.active_passage_translation = None # KHỞI TẠO KEY DỊCH ĐOẠN VĂN ĐỘC QUYỀN
if 'passage_translations_cache' not in st.session_state: st.session_state.passage_translations_cache = {} # CACHE DỊCH ĐOẠN VĂN
if 'current_passage_id_displayed' not in st.session_state: st.session_state.current_passage_id_displayed = None 
if 'group_mode_title' not in st.session_state: st.session_state.group_mode_title = "Luyện tập theo nhóm (30 câu/nhóm)"

# CẬP NHẬT LIST NGÂN HÀNG
BANK_OPTIONS = ["----", "Ngân hàng Kỹ thuật", "Ngân hàng Luật VAECO", "Ngân hàng Docwise"]
bank_choice = st.selectbox("Chọn ngân hàng:", BANK_OPTIONS, index=BANK_OPTIONS.index(st.session_state.get('bank_choice_val', '----')), key="bank_selector_master")
st.session_state.bank_choice_val = bank_choice

# Xử lý khi đổi ngân hàng (reset mode)
if st.session_state.get('last_bank_choice') != bank_choice and bank_choice != "----":
    st.session_state.current_group_idx = 0
    st.session_state.submitted = False
    st.session_state.current_mode = "group" 
    # Reset active translation keys
    st.session_state.active_translation_key = None 
    st.session_state.active_passage_translation = None 
    st.session_state.current_passage_id_displayed = None # Reset passage display
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
        # Cập nhật nhãn Phụ lục 2 và BỔ SUNG PHỤ LỤC 3
        doc_options = ["Phụ lục 1 : Ngữ pháp chung", "Phụ lục 2 : Từ vựng, thuật ngữ", "Phụ lục 3 : Bài đọc hiểu", "Phụ lục 4 : Luật và qui trình"]
        doc_selected_new = st.selectbox("Chọn Phụ lục:", doc_options, index=doc_options.index(st.session_state.get('doc_selected', doc_options[0])), key="docwise_selector")
        
        # Xử lý khi đổi phụ lục (reset mode)
        if st.session_state.doc_selected != doc_selected_new:
            st.session_state.doc_selected = doc_selected_new
            st.session_state.current_group_idx = 0
            st.session_state.submitted = False
            st.session_state.current_mode = "group"
            st.session_state.active_translation_key = None 
            st.session_state.active_passage_translation = None 
            st.session_state.current_passage_id_displayed = None # Reset passage display
            st.rerun()

        if st.session_state.doc_selected == "Phụ lục 1 : Ngữ pháp chung":
            source = "PL1.docx" # File PL1.docx (Dùng parse_pl1)
        elif st.session_state.doc_selected == "Phụ lục 2 : Từ vựng, thuật ngữ": 
            source = "PL2.docx" # File PL2.docx (Dùng parse_pl2 đã sửa)
        elif st.session_state.doc_selected == "Phụ lục 3 : Bài đọc hiểu": 
            source = "PL3.docx" # File PL3.docx (Dùng parse_pl3_passage_bank mới)
        elif st.session_state.doc_selected == "Phụ lục 4 : Luật và qui trình": 
            source = "PL4.docx" # File PL3.docx (Dùng parse_pl4_passage_bank mới)
        
    # LOAD CÂU HỎI
    questions = []
    if source:
        if "Kỹ thuật" in bank_choice:
            questions = parse_cabbank(source)
        elif "Luật VAECO" in bank_choice:
            questions = parse_lawbank(source)
        elif is_docwise:
            if source == "PL1.docx":
                questions = parse_pl1(source) # Sử dụng parser cũ (dùng (*))
            elif source == "PL2.docx":
                questions = parse_pl2(source) # Sử dụng parser mới (dùng (*))
            elif source == "PL3.docx":
                questions = parse_pl3_passage_bank(source) # <-- Dùng parser đã sửa cho PL3
            elif source == "PL4.docx":
                questions = parse_pl4_passage_bank(source)
    
    if not questions:
        # Cập nhật thông báo lỗi để phù hợp với logic (*) cho cả PL1 và PL2
        st.error(f"❌ Không đọc được câu hỏi nào từ file **{source}**. Vui lòng kiểm tra file và cấu trúc thư mục (đảm bảo file nằm trong thư mục gốc hoặc thư mục 'pages/'), và kiểm tra lại định dạng đáp án đúng (dùng dấu `(*)`).")
        st.stop() 
    
    total = len(questions)

    # === LOGIC NHÓM CÂU HỎI THEO MODE (PL3 TÙY CHỈNH) - ĐÃ SỬA THEO YÊU CẦU MỚI ===
    group_size = 30 # Mặc định 30 câu/nhóm
    custom_groups = [] # Chỉ dùng cho PL3
    is_pl3_grouping = False

    if is_docwise and source == "PL3.docx":
        is_pl3_grouping = True
        passage_groups = {}
        
        # Nhóm câu hỏi theo tên Paragraph
        for q in questions:
            # group_key: "Paragraph 1 ."
            group_key = q.get('group', 'Không có đoạn văn')
            if group_key not in passage_groups:
                passage_groups[group_key] = []
            
            passage_groups[group_key].append(q)
            
        # ----------------------------------------------------
        # LOGIC MỚI: NHÓM 2 PARAGRAPH THÀNH 1 NHÓM
        # ----------------------------------------------------
        passage_names = list(passage_groups.keys())
        
        # Duyệt qua danh sách tên Paragraph theo bước nhảy 2
        for i in range(0, len(passage_names), 2):
            p1_name = passage_names[i]
            p2_name = passage_names[i+1] if i + 1 < len(passage_names) else None
            
            questions_in_pair = passage_groups[p1_name]
            
            # Xử lý Paragraph thứ 2
            if p2_name:
                questions_in_pair.extend(passage_groups[p2_name])
                
                # Bóc tách số thứ tự khỏi chuỗi "Paragraph X ."
                p1_match = re.search(r'Paragraph\s*(\d+)', p1_name, re.I)
                p2_match = re.search(r'Paragraph\s*(\d+)', p2_name, re.I)
                
                p1_num = p1_match.group(1) if p1_match else p1_name
                p2_num = p2_match.group(1) if p2_match else p2_name
                
                base_group_label = f"Paragraph {p1_num} & {p2_num}"
            else:
                # Xử lý Paragraph lẻ cuối cùng (ví dụ: "Paragraph 11")
                p1_match = re.search(r'Paragraph\s*(\d+)', p1_name, re.I)
                p1_num = p1_match.group(1) if p1_match else p1_name
                base_group_label = f"Paragraph {p1_num}"
            
            # TẠO LABEL CUỐI CÙNG (CHỈ DÙNG TÊN PARAGRAPH)
            final_group_label = base_group_label # <--- ĐÃ SỬA THEO YÊU CẦU CỦA USER
            
            if questions_in_pair:
                # Dù có câu hỏi hay không, vẫn dùng base_group_label (ví dụ: "Paragraph 1 & 2")
                pass
            else:
                 # Trường hợp không có câu hỏi nào (chỉ để dự phòng, hiếm xảy ra)
                final_group_label = base_group_label

            custom_groups.append({
                'label': final_group_label,
                'questions': questions_in_pair
            })
        
        groups = [g['label'] for g in custom_groups]
        st.session_state.group_mode_title = "Luyện tập theo đoạn văn (2 đoạn/nhóm)"
    else:
        # Nhóm câu hỏi theo số lượng (30 câu/nhóm) cho các ngân hàng khác
        groups = [f"Câu {i*group_size+1}-{min((i+1)*group_size, total)}" for i in range(math.ceil(total/group_size))]
        st.session_state.group_mode_title = f"Luyện tập theo nhóm ({group_size} câu/nhóm)"
        
    # --- MODE: GROUP ---
    if st.session_state.current_mode == "group":
        # Cập nhật tiêu đề nhóm câu hỏi
        st.markdown(f'<div class="result-title" style="margin-top: 0px;"><h3>{st.session_state.group_mode_title}</h3></div>', unsafe_allow_html=True)
        
        if total > 0:
            if st.session_state.current_group_idx >= len(groups): st.session_state.current_group_idx = 0
            selected = st.selectbox("Chọn nhóm câu:", groups, index=st.session_state.current_group_idx, key="group_selector")
            
            # Xử lý khi chuyển nhóm câu
            new_idx = groups.index(selected)
            if st.session_state.current_group_idx != new_idx:
                st.session_state.current_group_idx = new_idx
                st.session_state.submitted = False
                st.session_state.active_translation_key = None # Reset dịch Q&A
                st.session_state.active_passage_translation = None # Reset dịch Passage
                st.session_state.current_passage_id_displayed = None # Reset passage display
                st.rerun()

            idx = st.session_state.current_group_idx
            
            if is_pl3_grouping:
                batch = custom_groups[idx]['questions']
                start = 0 # Not relevant in this new grouping mode
            else:
                # Logic lấy batch cũ (30 câu/nhóm)
                start = idx * group_size
                end = min((idx+1) * group_size, total)
                batch = questions[start:end]

            # Set starting index for questions in non-PL3 mode
            start_i = start + 1 
            
            st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
            col_all_bank, col_test = st.columns(2)
            with col_all_bank:
                if st.button("📖 Hiển thị toàn bộ ngân hàng", key="btn_show_all"):
                    st.session_state.current_mode = "all"
                    st.session_state.active_translation_key = None # Reset dịch Q&A
                    st.session_state.active_passage_translation = None # Reset dịch Passage
                    st.session_state.current_passage_id_displayed = None # Reset passage display
                    st.rerun()
            with col_test:
                # Đổi tên nút test
                if st.button("Làm bài test", key="btn_start_test"):
                    st.session_state.current_mode = "test"
                    st.session_state.active_translation_key = None # Reset dịch Q&A
                    st.session_state.active_passage_translation = None # Reset dịch Passage
                    st.session_state.current_passage_id_displayed = None # Reset passage display
                    bank_slug_new = bank_choice.split()[-1].lower()
                    test_key_prefix = f"test_{bank_slug_new}"
                    # Reset session state cho bài test trước khi bắt đầu
                    st.session_state.pop(f"{test_key_prefix}_started", None)
                    st.session_state.pop(f"{test_key_prefix}_submitted", None)
                    st.session_state.pop(f"{test_key_prefix}_questions", None)
                    st.rerun()
            st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
            
            
            # --- BẮT ĐẦU VÒNG LẶP CÂU HỎI ---
            if batch:
                current_passage_id_in_group_mode = None
                
                if not st.session_state.submitted:
                    # Luyện tập
                    for i_local, q in enumerate(batch):
                        i_global = q.get('global_number', start + i_local + 1) # Sử dụng global_number nếu có
                        q_key = f"q_{i_global}_{hash(q['question'])}" 
                        translation_key = f"trans_{q_key}"
                        is_active = (translation_key == st.session_state.active_translation_key)
                        
                        # --- CẬP NHẬT: HIỂN THỊ ĐOẠN VĂN (CHO PL3) TRƯỚC CÂU HỎI ---
                        passage_content = q.get('paragraph_content', '').strip()
                        group_name = q.get('group', '')
                        
                        if passage_content:
                            passage_id = f"passage_{group_name}_{hash(passage_content)}"
                            is_passage_active = (passage_id == st.session_state.active_passage_translation)

                            if passage_id != current_passage_id_in_group_mode:
                                # 1. In đậm, đổi màu tiêu đề
                                st.markdown(f'<div class="paragraph-title">**{group_name}**</div>', unsafe_allow_html=True) 
                                
                                # 2. Hiển thị nội dung đoạn văn gốc
                                st.markdown(f'<div class="paragraph-content-box">{passage_content}</div>', unsafe_allow_html=True)
                                
                                # 3. Thêm Nút Dịch Đoạn Văn
                                st.toggle(
                                    "🌐 Dịch đoạn văn sang Tiếng Việt", 
                                    value=is_passage_active, 
                                    key=f"toggle_passage_{passage_id}",
                                    on_change=on_passage_translate_toggle,
                                    args=(passage_id,)
                                )
                                
                                # 4. Hiển thị Bản Dịch Đoạn Văn
                                if is_passage_active:
                                    translated_passage = st.session_state.passage_translations_cache.get(passage_id)
                                    if not isinstance(translated_passage, str):
                                        # GỌI HÀM DỊCH CHỈ ĐOẠN VĂN
                                        translated_passage = translate_passage_content(passage_content)
                                        st.session_state.passage_translations_cache[passage_id] = translated_passage

                                    st.markdown(f"""
                                    <div data-testid="stAlert" class="stAlert stAlert-info">
                                        <div style="font-size: 18px; line-height: 1.6; color: white; padding: 10px;">
                                            <strong style="color: #FFD700;">[Bản dịch Đoạn văn]</strong>
                                            <div class="paragraph-content-box" style="white-space: pre-wrap; margin-bottom: 0px; padding: 10px; background-color: rgba(0, 0, 0, 0.5); border-left: 3px solid #00d4ff;">
                                            {translated_passage}
                                            </div>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)

                                st.markdown("---") 
                                
                                current_passage_id_in_group_mode = passage_id
                        # -----------------------------------------------------------------
                        
                        # Fix KeyError: 'number' (Sử dụng global number nếu có, nếu không thì dùng number của paragraph)
                        if q.get('group', '').startswith('Paragraph'):
                            # Dùng số thứ tự cục bộ (number) nếu là bài đọc hiểu
                            display_num = q.get('number', i_global) 
                        else:
                            # Dùng số thứ tự toàn cục (i_global) cho các ngân hàng khác
                            display_num = i_global 
                        
                        # Hiển thị câu hỏi
                        st.markdown(f'<div class="bank-question-text">{display_num}. {q["question"]}</div>', unsafe_allow_html=True) 

                        # Nút Dịch Q&A ở dưới
                        st.toggle(
                            "🌐 Dịch Câu hỏi & Đáp án sang Tiếng Việt", 
                            value=is_active, 
                            key=f"toggle_{translation_key}",
                            on_change=on_translate_toggle,
                            args=(translation_key,)
                        )

                        # Hiển thị Bản Dịch Q&A
                        if is_active:
                            # Check if translated content is already cached
                            translated_content = st.session_state.translations.get(translation_key)
                            
                            # If not cached or is not a string (default True/False state)
                            if not isinstance(translated_content, str):
                                # GỌI HÀM MỚI ĐỂ GỬI CHỈ CÂU HỎI VÀ ĐÁP ÁN ĐI DỊCH
                                full_text_to_translate = build_translation_text_for_qa(q) 
                                st.session_state.translations[translation_key] = translate_text(full_text_to_translate)
                                translated_content = st.session_state.translations[translation_key]

                            st.info(translated_content, icon="🌐")

                        # Hiển thị Radio Button
                        default_val = st.session_state.get(q_key, q["options"][0] if q["options"] else None)
                        st.radio("", q["options"], index=q["options"].index(default_val) if default_val in q["options"] else 0, key=q_key)
                        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
                    if st.button("✅ Nộp bài", key="submit_group"):
                        st.session_state.submitted = True
                        st.session_state.active_translation_key = None # Tắt dịch Q&A khi nộp
                        st.session_state.active_passage_translation = None # Tắt dịch Passage khi nộp
                        st.rerun()
                else:
                    # Chế độ xem đáp án
                    score = 0
                    for i_local, q in enumerate(batch):
                        i_global = q.get('global_number', start + i_local + 1)
                        q_key = f"q_{i_global}_{hash(q['question'])}" 
                        selected_opt = st.session_state.get(q_key)
                        correct = clean_text(q["answer"])
                        is_correct = clean_text(selected_opt) == correct
                        translation_key = f"trans_{q_key}"
                        is_active = (translation_key == st.session_state.active_translation_key)
                        
                        # --- CẬP NHẬT: HIỂN THỊ ĐOẠN VĂN (CHO PL3) TRƯỚC CÂU HỎI ---
                        passage_content = q.get('paragraph_content', '').strip()
                        group_name = q.get('group', '')
                        
                        if passage_content:
                            passage_id = f"passage_{group_name}_{hash(passage_content)}"
                            is_passage_active = (passage_id == st.session_state.active_passage_translation)

                            if passage_id != current_passage_id_in_group_mode:
                                # 1. In đậm, đổi màu tiêu đề
                                st.markdown(f'<div class="paragraph-title">**{group_name}**</div>', unsafe_allow_html=True) 
                                
                                # 2. Hiển thị nội dung đoạn văn gốc
                                st.markdown(f'<div class="paragraph-content-box">{passage_content}</div>', unsafe_allow_html=True)
                                
                                # 3. Thêm Nút Dịch Đoạn Văn
                                st.toggle(
                                    "🌐 Dịch đoạn văn sang Tiếng Việt", 
                                    value=is_passage_active, 
                                    key=f"toggle_passage_{passage_id}",
                                    on_change=on_passage_translate_toggle,
                                    args=(passage_id,)
                                )
                                
                                # 4. Hiển thị Bản Dịch Đoạn Văn
                                if is_passage_active:
                                    translated_passage = st.session_state.passage_translations_cache.get(passage_id)
                                    if not isinstance(translated_passage, str):
                                        # GỌI HÀM DỊCH CHỈ ĐOẠN VĂN
                                        translated_passage = translate_passage_content(passage_content)
                                        st.session_state.passage_translations_cache[passage_id] = translated_passage

                                    st.markdown(f"""
                                    <div data-testid="stAlert" class="stAlert stAlert-info">
                                        <div style="font-size: 18px; line-height: 1.6; color: white; padding: 10px;">
                                            <strong style="color: #FFD700;">[Bản dịch Đoạn văn]</strong>
                                            <div class="paragraph-content-box" style="white-space: pre-wrap; margin-bottom: 0px; padding: 10px; background-color: rgba(0, 0, 0, 0.5); border-left: 3px solid #00d4ff;">
                                            {translated_passage}
                                            </div>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)

                                st.markdown("---") 
                                
                                current_passage_id_in_group_mode = passage_id
                        # -----------------------------------------------------------------

                        # Hiển thị câu hỏi: FIX KeyError: 'number'
                        if q.get('group', '').startswith('Paragraph'):
                            # Dùng số thứ tự cục bộ (number) nếu là bài đọc hiểu
                            display_num = q.get('number', i_global) 
                        else:
                            # Dùng số thứ tự toàn cục (i_global) cho các ngân hàng khác
                            display_num = i_global 
                        st.markdown(f'<div class="bank-question-text">{display_num}. {q["question"]}</div>', unsafe_allow_html=True) 

                        # Nút Dịch Q&A ở dưới
                        st.toggle(
                            "🌐 Dịch Câu hỏi & Đáp án sang Tiếng Việt", 
                            value=is_active, 
                            key=f"toggle_{translation_key}",
                            on_change=on_translate_toggle,
                            args=(translation_key,)
                        )

                        # Hiển thị Bản Dịch Q&A
                        if is_active:
                            # Check if translated content is already cached
                            translated_content = st.session_state.translations.get(translation_key)
                            
                            # If not cached or is not a string (default True/False state)
                            if not isinstance(translated_content, str):
                                # GỌI HÀM MỚI ĐỂ GỬI CHỈ CÂU HỎI VÀ ĐÁP ÁN ĐI DỊCH
                                full_text_to_translate = build_translation_text_for_qa(q)
                                st.session_state.translations[translation_key] = translate_text(full_text_to_translate)
                                translated_content = st.session_state.translations[translation_key]

                            st.info(translated_content, icon="🌐")

                        # Hiển thị Đáp án (KẾT QUẢ)
                        for opt in q["options"]:
                            opt_clean = clean_text(opt)
                            opt_display = opt # Khởi tạo giá trị hiển thị

                            if opt_clean == correct:
                                color_style = "color:#00ff00;" # Xanh lá
                                opt_display += " (*)" # BỔ SUNG: Thêm ký tự (*)
                            elif opt_clean == clean_text(selected_opt):
                                color_style = "color:#ff3333;" # Đỏ
                            else:
                                color_style = "color:#FFFFFF;" # Trắng chân phương
                            st.markdown(f'<div class="bank-answer-text" style="{color_style}">{opt_display}</div>', unsafe_allow_html=True)
                        
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
                            for i_local, q in enumerate(batch):
                                i_global = q.get('global_number', start + i_local + 1)
                                st.session_state.pop(f"q_{i_global}_{hash(q['question'])}", None) 
                            st.session_state.submitted = False
                            st.session_state.active_translation_key = None # Reset dịch Q&A
                            st.session_state.active_passage_translation = None # Reset dịch Passage
                            st.rerun()
                    with col_next:
                        if st.session_state.current_group_idx < len(groups) - 1:
                            if st.button("➡️ Tiếp tục nhóm sau", key="next_group"):
                                st.session_state.current_group_idx += 1
                                st.session_state.submitted = False
                                st.session_state.active_translation_key = None # Reset dịch Q&A
                                st.session_state.active_passage_translation = None # Reset dịch Passage
                                st.rerun()
                        else: st.info("🎉 Đã hoàn thành tất cả các nhóm câu hỏi!")
            else: st.warning("Không có câu hỏi trong nhóm này.")
        else: st.warning("Không có câu hỏi nào trong ngân hàng này.")

    elif st.session_state.current_mode == "all":
        if st.button("⬅️ Quay lại chế độ Luyện tập theo nhóm"):
            st.session_state.current_mode = "group"
            st.session_state.active_translation_key = None # Reset dịch Q&A
            st.session_state.active_passage_translation = None # Reset dịch Passage
            st.session_state.current_passage_id_displayed = None # Reset passage display
            st.rerun()
        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
        display_all_questions(questions)
        
    elif st.session_state.current_mode == "test":
        if st.button("⬅️ Quay lại chế độ Luyện tập theo nhóm"):
            st.session_state.current_mode = "group"
            st.session_state.active_translation_key = None # Reset dịch Q&A
            st.session_state.active_passage_translation = None # Reset dịch Passage
            st.session_state.current_passage_id_displayed = None # Reset passage display
            st.rerun()
        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
        display_test_mode(questions, bank_choice)
