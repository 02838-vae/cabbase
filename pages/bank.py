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
    Hàm đọc paragraphs chỉ lấy TEXT (sử dụng cho cabbank, lawbank, PL1, PL3)
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
# 🌐 HÀM DỊCH THUẬT (ĐÃ CẬP NHẬT DÙNG translate)
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

def translate_text(text):
    """Dịch văn bản sử dụng deep_translator (ĐÃ SỬA LỖI "Một...")"""
    translator = get_translator()
    
    if translator is None:
        return f"**[LỖI]** Không thể khởi tạo translator.\n{text}"
    
    try:
        # Nếu là câu hỏi có đoạn văn (PL3)
        if text.startswith("Câu hỏi: 📝 "):
            parts = text.split('\nĐáp án: ')
            q_content_raw = parts[0].replace('Câu hỏi: ', '').strip()
            a_content_raw = parts[1].strip() if len(parts) > 1 else ""
            
            # Tách đoạn văn và câu hỏi chính
            if "\n\n" in q_content_raw:
                passage_part, question_part = q_content_raw.split("\n\n", 1)
                passage_part = passage_part.replace("📝 ", "").strip()
            else:
                passage_part = ""
                question_part = q_content_raw.replace("📝 ", "").strip()
            
            # Dịch đoạn văn (Passage)
            if passage_part:
                passage_translated = translator.translate(passage_part)
                # Đảm bảo không bị thêm prefix
                passage_translated = re.sub(r'^\s*([a-d]\.|\d+\.)\s*', '', passage_translated, flags=re.IGNORECASE).strip()
            else:
                passage_translated = ""

            # Dịch câu hỏi chính
            q_translated = translator.translate(question_part)
            q_translated = re.sub(r'^\s*([a-d]\.|\d+\.)\s*', '', q_translated, flags=re.IGNORECASE).strip()
            
            # Ghép lại
            q_full_translated = ""
            if passage_translated:
                q_full_translated += f"**Đoạn văn:** {passage_translated}\n\n"
            q_full_translated += f"**Câu hỏi:** {q_translated}"
            
        # Nếu là câu hỏi thường (PL1, PL2, CABBANK, LAWBANK)
        else:
            parts = text.split('\nĐáp án: ')
            q_content = parts[0].replace('Câu hỏi: ', '').strip()
            a_content_raw = parts[1].strip() if len(parts) > 1 else ""
            
            # Dịch câu hỏi
            q_translated = translator.translate(q_content)
            # Dùng output format chung
            q_full_translated = f"**Câu hỏi:** {q_translated}"
            
            
        options = [opt.strip() for opt in a_content_raw.split(';') if opt.strip()]
        
        # Dịch từng đáp án (Logic giữ nguyên)
        a_translated_list = []
        for i, option_content in enumerate(options):
            if not option_content:
                a_translated_list.append("")
                continue
            
            # 1. Tách prefix và nội dung chính để CHỈ DỊCH NỘI DUNG
            original_prefix_match = re.match(r'^([a-d]\.|\s*)\s*', option_content, re.IGNORECASE)
            original_prefix_with_space = original_prefix_match.group(0) if original_prefix_match else ""
            # Lấy prefix để gắn lại
            original_prefix = original_prefix_with_space.strip() if original_prefix_with_space.strip() else f"{i+1}."
            
            # Lấy nội dung chính (body)
            content_to_translate = option_content[len(original_prefix_with_space):].strip()
            
            if not content_to_translate:
                a_translated_list.append(original_prefix)
                continue

            # 2. CHỈ DỊCH NỘI DUNG CHÍNH
            translated_text = translator.translate(content_to_translate)
            
            # 3. Loại bỏ ký tự thừa do translator tự thêm (VD: "Một", "A.", "1.")
            stripped_translated_text = translated_text.strip()
            
            # Loại bỏ "Một " hoặc "một " ở đầu bản dịch (Fix lỗi người dùng báo cáo)
            if stripped_translated_text.lower().startswith("một "):
                stripped_translated_text = stripped_translated_text[len("một "):]
                
            # Loại bỏ các prefix kiểu chữ cái/số + dấu chấm (VD: "A. ", "1. ") 
            # mà translator có thể thêm vào khi dịch body
            stripped_translated_text = re.sub(r'^\s*([a-d]\.|\d+\.)\s*', '', stripped_translated_text, flags=re.IGNORECASE).strip()
            
            # Đảm bảo không bị rỗng
            if not stripped_translated_text:
                stripped_translated_text = translated_text.strip()
            
            # 4. Gắn prefix gốc và nội dung đã dịch
            a_translated_list.append(f"{original_prefix} {stripped_translated_text}")
        
        a_translated_text = "\n".join([f"- {opt}" for opt in a_translated_list])
        
        return f"**[Bản dịch Tiếng Việt]**\n\n- {q_full_translated}\n- **Các đáp án:** \n{a_translated_text}"
        
    except Exception as e:
        print(f"Lỗi dịch thuật: {e}")
        return f"**[LỖI DỊCH THUẬT]**\n- Không thể dịch nội dung. Chi tiết: {type(e).__name__}\n- Câu hỏi gốc:\n{text}"

# ====================================================

# ====================================================
# 🧩 PARSER 1: NGÂN HÀNG KỸ THUẬT (CABBANK)
# ====================================================
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
# 🧩 PARSER 5: PHỤ LỤC 3 (ĐOẠN VĂN - Dùng dấu (*)) <--- BỔ SUNG MỚI
# ====================================================
def parse_pl3(source):
    """
    Parser cho định dạng PL3 (Đoạn văn - Câu hỏi).
    Cấu trúc: **Paragraph X**. -> Nội dung đoạn văn -> Câu hỏi 1., 2., 3... với đáp án A, B, C (đáp án đúng có (*))
    """
    paras = read_docx_paragraphs(source)
    if not paras: return []

    questions = []
    current_paragraph_content = "" # Lưu nội dung đoạn văn hiện tại
    current_paragraph_title = "" # Lưu tiêu đề paragraph (VD: "Paragraph 1")
    current_q = {"question": "", "options": [], "answer": ""}
    
    # REGEX - CẬP NHẬT ĐỂ KHỚP VỚI ĐỊNH DẠNG THỰC TẾ
    # Tìm dòng bắt đầu bằng "**Paragraph X**" hoặc "Paragraph X."
    paragraph_pat = re.compile(r'^\*{0,2}\s*Paragraph\s+\d+\s*\*{0,2}[\.\s]*', re.I) 
    # Tìm câu hỏi bắt đầu bằng số (1., 2., 3...)
    q_start_pat = re.compile(r'^\s*(\d+)[\.\)]\s*') 
    # Tìm đáp án (A., B., C., D.)
    opt_prefix_pat = re.compile(r'^\s*[A-Da-d][\.\)]\s*') 
    labels = ["a", "b", "c", "d"]
    MAX_OPTIONS = 4

    def finalize_current_question(q_dict, q_list):
        """Hoàn thành và lưu câu hỏi hiện tại"""
        if q_dict["question"].strip():
            # Gắn nội dung đoạn văn vào đầu câu hỏi
            if current_paragraph_content.strip():
                # Dùng ký hiệu đặc biệt để đánh dấu (dùng cho việc hiển thị sau này)
                full_paragraph = current_paragraph_title + "\n\n" + current_paragraph_content.strip()
                q_dict["question"] = "📖 " + full_paragraph + "\n\n" + q_dict["question"].strip()
            
            # Nếu không có đáp án đúng, mặc định chọn đáp án đầu tiên
            if not q_dict["answer"] and q_dict["options"]:
                q_dict["answer"] = q_dict["options"][0]
            
            q_list.append(q_dict)
        return {"question": "", "options": [], "answer": ""}
    
    in_paragraph_content = False # Đang đọc nội dung đoạn văn (chưa gặp câu hỏi)
    
    for p in paras:
        clean_p = clean_text(p)
        if not clean_p: continue
        
        # 1. PHÁT HIỆN TIÊU ĐỀ ĐOẠN VĂN MỚI (Paragraph X)
        paragraph_match = paragraph_pat.match(clean_p)
        if paragraph_match:
            # Hoàn thành câu hỏi trước đó (nếu có)
            current_q = finalize_current_question(current_q, questions)
            
            # Reset và bắt đầu đoạn văn mới
            current_paragraph_title = clean_p.strip()
            current_paragraph_content = ""
            in_paragraph_content = True  # Bắt đầu đọc nội dung đoạn văn
            current_q = {"question": "", "options": [], "answer": ""}
            continue
        
        # 2. PHÁT HIỆN BẮT ĐẦU CÂU HỎI (1., 2., 3...)
        q_match = q_start_pat.match(clean_p)
        if q_match and current_paragraph_title:  # Chỉ nhận diện câu hỏi khi đã có paragraph
            # Hoàn thành câu hỏi trước
            current_q = finalize_current_question(current_q, questions)
            
            # Bắt đầu câu hỏi mới
            q_text = q_start_pat.sub('', clean_p).strip()
            current_q["question"] = q_text
            current_q["options"] = []
            current_q["answer"] = ""
            in_paragraph_content = False  # Đã vào phần câu hỏi, không còn là nội dung đoạn văn
            continue
        
        # 3. XỬ LÝ ĐÁP ÁN (A., B., C., D.)
        if current_q["question"] and len(current_q["options"]) < MAX_OPTIONS:
            is_correct = False
            temp_p = clean_p
            
            # Kiểm tra dấu (*) đánh dấu đáp án đúng
            if "(*)" in temp_p:
                is_correct = True
                temp_p = temp_p.replace("(*)", "").strip()
            
            # Kiểm tra prefix đáp án (A., B., C., D.)
            opt_match = opt_prefix_pat.match(temp_p)
            if opt_match:
                temp_p = temp_p[opt_match.end():].strip()
                
                idx = len(current_q["options"])
                if idx < len(labels):
                    label = labels[idx]
                    opt_text = f"{label}. {temp_p}"
                    current_q["options"].append(opt_text)
                    
                    if is_correct:
                        current_q["answer"] = opt_text
                continue
        
        # 4. XỬ LÝ NỘI DUNG CHUNG (nội dung đoạn văn hoặc phần mở rộng của câu hỏi)
        if in_paragraph_content:
            # Đang đọc nội dung đoạn văn (chưa gặp câu hỏi)
            if current_paragraph_content:
                current_paragraph_content += " " + clean_p
            else:
                current_paragraph_content = clean_p
        elif current_q["question"]:
            # Đang có câu hỏi -> nối thêm vào câu hỏi (trường hợp câu hỏi dài nhiều dòng)
            current_q["question"] += " " + clean_p

    # Hoàn thành câu hỏi cuối cùng
    current_q = finalize_current_question(current_q, questions)
    
    return questions
# ====================================================

# ====================================================
# 🌟 HÀM: LOGIC DỊCH ĐỘC QUYỀN (EXCLUSIVE TRANSLATION)
# ====================================================
if 'active_translation_key' not in st.session_state: st.session_state.active_translation_key = None

def on_translate_toggle(key_clicked):
    """Callback function để quản lý chế độ Dịch ĐỘC QUYỀN."""
    toggle_key = f"toggle_{key_clicked}"
    # Check the state of the toggle in session state (it is the state *after* the click)
    is_on_after_click = st.session_state.get(toggle_key, False)
    
    if is_on_after_click:
        # User turned this specific toggle ON -> Make it the active key
        st.session_state.active_translation_key = key_clicked
    elif st.session_state.active_translation_key == key_clicked:
        # User turned this specific toggle OFF -> Clear the active key
        st.session_state.active_translation_key = None
    
    # Bỏ st.rerun() để tránh warning "Calling st.rerun() within a callback is a no-op."

# ====================================================
# 🌟 HÀM: XEM TOÀN BỘ CÂU HỎI (CẬP NHẬT CHỨC NĂNG DỊCH)
# ====================================================
def display_all_questions(questions):
    st.markdown('<div class="result-title"><h3>📚 TOÀN BỘ NGÂN HÀNG CÂU HỎI</h3></div>', unsafe_allow_html=True)
    if not questions:
        st.warning("Không có câu hỏi nào để hiển thị.")
        return
    
    for i, q in enumerate(questions, start=1):
        q_key = f"all_q_{i}_{hash(q['question'])}" 
        translation_key = f"trans_{q_key}"
        is_active = (translation_key == st.session_state.active_translation_key)
        
        # Hiển thị câu hỏi
        # Xử lý hiển thị PL3
        if q["question"].startswith("📝 "):
            # Tách đoạn văn ra khỏi câu hỏi để hiển thị
            content_parts = q["question"].split("\n\n", 1)
            passage = content_parts[0].replace("📝 ", "").strip()
            question_text = content_parts[1].strip() if len(content_parts) > 1 else ""
            st.markdown(f'<div class="bank-question-text" style="color:#00D4FF !important;">**Đoạn văn:** {passage}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bank-question-text">{i}. {question_text}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True)

        # Nút Dịch ở dưới
        st.toggle(
            "🌐 Dịch sang Tiếng Việt", 
            value=is_active, 
            key=f"toggle_{translation_key}",
            on_change=on_translate_toggle,
            args=(translation_key,)
        )

        # Hiển thị Bản Dịch
        if is_active:
            # Check if translated content is already cached
            translated_content = st.session_state.translations.get(translation_key)
            
            # If not cached or is not a string (default True/False state)
            if not isinstance(translated_content, str):
                full_text_to_translate = f"Câu hỏi: {q['question']}\nĐáp án: {'; '.join(q['options'])}"
                st.session_state.translations[translation_key] = translate_text(full_text_to_translate)
                translated_content = st.session_state.translations[translation_key]

            st.info(translated_content, icon="🌐")
            
        # Hiển thị Đáp án
        for opt in q["options"]:
            # Dùng clean_text để so sánh, bỏ qua khoảng trắng, ký tự ẩn
            if clean_text(opt) == clean_text(q["answer"]):
                # Đáp án đúng: Xanh lá (Bỏ shadow)
                color_style = "color:#00ff00;" 
            else:
                # Đáp án thường: Trắng (Bỏ shadow)
                color_style = "color:#FFFFFF;"
            st.markdown(f'<div class="bank-answer-text" style="{color_style}">{opt}</div>', unsafe_allow_html=True)
        
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

    if not st.session_state[f"{test_key_prefix}_started"]:
        st.markdown('<div class="result-title"><h3>📝 LÀM BÀI TEST 50 CÂU</h3></div>', unsafe_allow_html=True)
        
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
            q_key = f"{test_key_prefix}_q_{i}_{hash(q['question'])}" 
            translation_key = f"trans_{q_key}"
            is_active = (translation_key == st.session_state.active_translation_key)
            
            # Hiển thị câu hỏi
            if q["question"].startswith("📝 "):
                content_parts = q["question"].split("\n\n", 1)
                passage = content_parts[0].replace("📝 ", "").strip()
                question_text = content_parts[1].strip() if len(content_parts) > 1 else ""
                st.markdown(f'<div class="bank-question-text" style="color:#00D4FF !important;">**Đoạn văn:** {passage}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="bank-question-text">{i}. {question_text}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True)

            # Nút Dịch ở dưới
            st.toggle(
                "🌐 Dịch sang Tiếng Việt", 
                value=is_active, 
                key=f"toggle_{translation_key}",
                on_change=on_translate_toggle,
                args=(translation_key,)
            )

            # Hiển thị Bản Dịch
            if is_active:
                translated_content = st.session_state.translations.get(translation_key)
                
                if not isinstance(translated_content, str):
                    full_text_to_translate = f"Câu hỏi: {q['question']}\nĐáp án: {'; '.join(q['options'])}"
                    st.session_state.translations[translation_key] = translate_text(full_text_to_translate)
                    translated_content = st.session_state.translations[translation_key]

                st.info(translated_content, icon="🌐")

            # Hiển thị Radio Button
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
            q_key = f"{test_key_prefix}_q_{i}_{hash(q['question'])}" 
            selected_opt = st.session_state.get(q_key)
            correct = clean_text(q["answer"])
            is_correct = clean_text(selected_opt) == correct
            translation_key = f"trans_{q_key}"
            is_active = (translation_key == st.session_state.active_translation_key)

            # Hiển thị câu hỏi
            if q["question"].startswith("📝 "):
                content_parts = q["question"].split("\n\n", 1)
                passage = content_parts[0].replace("📝 ", "").strip()
                question_text = content_parts[1].strip() if len(content_parts) > 1 else ""
                st.markdown(f'<div class="bank-question-text" style="color:#00D4FF !important;">**Đoạn văn:** {passage}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="bank-question-text">{i}. {question_text}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True)

            # Nút Dịch ở dưới
            st.toggle(
                "🌐 Dịch sang Tiếng Việt", 
                value=is_active, 
                key=f"toggle_{translation_key}",
                on_change=on_translate_toggle,
                args=(translation_key,)
            )

            # Hiển thị Bản Dịch
            if is_active:
                translated_content = st.session_state.translations.get(translation_key)
                
                if not isinstance(translated_content, str):
                    full_text_to_translate = f"Câu hỏi: {q['question']}\nĐáp án: {'; '.join(q['options'])}"
                    st.session_state.translations[translation_key] = translate_text(full_text_to_translate)
                    translated_content = st.session_state.translations[translation_key]

                st.info(translated_content, icon="🌐")
            
            # Hiển thị Đáp án (KẾT QUẢ)
            for opt in q["options"]:
                opt_clean = clean_text(opt)
                if opt_clean == correct:
                    color_style = "color:#00ff00;"
                elif opt_clean == clean_text(selected_opt):
                    color_style = "color:#ff3333;"
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
    font-family: 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif !important;
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
# Cập nhật giá trị mặc định cho doc_selected
if "doc_selected" not in st.session_state: st.session_state.doc_selected = "Phụ lục 1 : Ngữ pháp chung" 
if 'translations' not in st.session_state: st.session_state.translations = {} # KHỞI TẠO STATE DỊCH THUẬT
if 'active_translation_key' not in st.session_state: st.session_state.active_translation_key = None # KHỞI TẠO KEY DỊCH ĐỘC QUYỀN

# CẬP NHẬT LIST NGÂN HÀNG
BANK_OPTIONS = ["----", "Ngân hàng Kỹ thuật", "Ngân hàng Luật VAECO", "Ngân hàng Docwise"]
bank_choice = st.selectbox("Chọn ngân hàng:", BANK_OPTIONS, index=BANK_OPTIONS.index(st.session_state.get('bank_choice_val', '----')), key="bank_selector_master")
st.session_state.bank_choice_val = bank_choice

# Xử lý khi đổi ngân hàng (reset mode)
if st.session_state.get('last_bank_choice') != bank_choice and bank_choice != "----":
    st.session_state.current_group_idx = 0
    st.session_state.submitted = False
    st.session_state.current_mode = "group" 
    # Reset active translation key
    st.session_state.active_translation_key = None 
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
        # Cập nhật nhãn Phụ lục 2
        doc_options = ["Phụ lục 1 : Ngữ pháp chung", "Phụ lục 2 : Từ vựng, thuật ngữ", "Phụ lục 3 : Đoạn văn"] # <--- ĐÃ THÊM PHỤ LỤC 3
        doc_selected_new = st.selectbox("Chọn Phụ lục:", doc_options, index=doc_options.index(st.session_state.get('doc_selected', doc_options[0])), key="docwise_selector")
        
        # Xử lý khi đổi phụ lục (reset mode)
        if st.session_state.doc_selected != doc_selected_new:
            st.session_state.doc_selected = doc_selected_new
            st.session_state.current_group_idx = 0
            st.session_state.submitted = False
            st.session_state.current_mode = "group"
            st.rerun()

        if st.session_state.doc_selected == "Phụ lục 1 : Ngữ pháp chung":
            source = "PL1.docx" # File PL1.docx (Dùng parse_pl1)
        elif st.session_state.doc_selected == "Phụ lục 2 : Từ vựng, thuật ngữ": 
            source = "PL2.docx" # File PL2.docx (Dùng parse_pl2 đã sửa)
        elif st.session_state.doc_selected == "Phụ lục 3 : Đoạn văn": # <--- BỔ SUNG LOGIC CHỌN FILE PL3
            source = "PL3.docx" 
        
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
            elif source == "PL3.docx": # <--- BỔ SUNG LOGIC DÙNG PARSER MỚI
                questions = parse_pl3(source) 
    
    if not questions:
        # Cập nhật thông báo lỗi để phù hợp với logic (*) cho cả PL1 và PL2
        st.error(f"❌ Không đọc được câu hỏi nào từ file **{source}**. Vui lòng kiểm tra file và cấu trúc thư mục (đảm bảo file nằm trong thư mục gốc hoặc thư mục 'pages/'), và kiểm tra lại định dạng đáp án đúng (dùng dấu `(*)`).")
        st.stop() 
    
    total = len(questions)

    # --- MODE: GROUP ---
    if st.session_state.current_mode == "group":
        # Xác định kích thước nhóm
        group_size = 30 # Mặc định là 30 câu/nhóm
        is_pl3 = (bank_choice == "Ngân hàng Docwise" and st.session_state.doc_selected == "Phụ lục 3 : Đoạn văn")
        
        # Cập nhật tiêu đề
        if is_pl3:
             st.markdown('<div class="result-title" style="margin-top: 0px;"><h3>Luyện tập theo nhóm (2 Đoạn văn/nhóm)</h3></div>', unsafe_allow_html=True)
        else:
             st.markdown('<div class="result-title" style="margin-top: 0px;"><h3>Luyện tập theo nhóm (30 câu/nhóm)</h3></div>', unsafe_allow_html=True)

        if total > 0:
            # Xử lý nhóm cho PL3 (theo Đoạn văn) <--- LOGIC CHIA NHÓM MỚI
            if is_pl3:
                # Tìm index của câu hỏi đầu tiên của mỗi Paragraph
                # Điều kiện: câu hỏi bắt đầu bằng '📝 Paragraph'
                paragraph_start_indices = [i for i, q in enumerate(questions) if q['question'].strip().startswith("📝 Paragraph")]
                if not paragraph_start_indices: paragraph_start_indices = [0] # Đề phòng không tìm thấy Paragraph

                group_info = []
                num_paragraphs = len(paragraph_start_indices)
                
                # Chia nhóm 2 đoạn văn
                for i in range(0, num_paragraphs, 2):
                    start_para_index = paragraph_start_indices[i] 
                    
                    # Index kết thúc là index bắt đầu của đoạn văn i+2, hoặc tổng số câu hỏi nếu là 2 đoạn cuối.
                    end_para_index = paragraph_start_indices[i+2] if i + 2 < num_paragraphs else total
                    
                    start_para_num = i + 1
                    end_para_num = min(i + 2, num_paragraphs) # Đảm bảo không vượt quá tổng số đoạn văn

                    group_info.append({
                        "label": f"Đoạn văn {start_para_num}-{end_para_num}",
                        "start": start_para_index,
                        "end": end_para_index
                    })
                
                groups = [g["label"] for g in group_info]
                
            # Xử lý nhóm cho các ngân hàng khác (theo số câu cố định)
            else:
                groups = [f"Câu {i*group_size+1}-{min((i+1)*group_size, total)}" for i in range(math.ceil(total/group_size))]
                group_info = [{"label": groups[i], "start": i*group_size, "end": min((i+1)*group_size, total)} for i in range(len(groups))]

            # Logic chọn nhóm (Giữ nguyên)
            if st.session_state.current_group_idx >= len(groups): st.session_state.current_group_idx = 0
            selected = st.selectbox("Chọn nhóm câu:", groups, index=st.session_state.current_group_idx, key="group_selector")
            
            # Xử lý khi chuyển nhóm câu
            new_idx = groups.index(selected)
            if st.session_state.current_group_idx != new_idx:
                st.session_state.current_group_idx = new_idx
                st.session_state.submitted = False
                st.session_state.active_translation_key = None # Reset dịch khi chuyển nhóm
                st.rerun()

            # Lấy batch câu hỏi
            current_group = group_info[st.session_state.current_group_idx]
            start, end = current_group["start"], current_group["end"]
            batch = questions[start:end]
            
            st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
            col_all_bank, col_test = st.columns(2)
            with col_all_bank:
                if st.button("📖 Hiển thị toàn bộ ngân hàng", key="btn_show_all"):
                    st.session_state.current_mode = "all"
                    st.session_state.active_translation_key = None # Reset dịch khi chuyển mode
                    st.rerun()
            with col_test:
                # Đổi tên nút test
                if st.button("Làm bài test", key="btn_start_test"):
                    st.session_state.current_mode = "test"
                    st.session_state.active_translation_key = None # Reset dịch khi chuyển mode
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
                        translation_key = f"trans_{q_key}"
                        is_active = (translation_key == st.session_state.active_translation_key)
                        
                        # Hiển thị câu hỏi (ĐÃ CẬP NHẬT LOGIC HIỂN THỊ PL3)
                        if q["question"].startswith("📝 "):
                            content_parts = q["question"].split("\n\n", 1)
                            passage = content_parts[0].replace("📝 ", "").strip()
                            question_text = content_parts[1].strip() if len(content_parts) > 1 else ""
                            st.markdown(f'<div class="bank-question-text" style="color:#00D4FF !important;">**Đoạn văn:** {passage}</div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="bank-question-text">{i}. {question_text}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True)

                        # Nút Dịch ở dưới
                        st.toggle(
                            "🌐 Dịch sang Tiếng Việt", 
                            value=is_active, 
                            key=f"toggle_{translation_key}",
                            on_change=on_translate_toggle,
                            args=(translation_key,)
                        )

                        # Hiển thị Bản Dịch
                        if is_active:
                            # Check if translated content is already cached
                            translated_content = st.session_state.translations.get(translation_key)
                            
                            # If not cached or is not a string (default True/False state)
                            if not isinstance(translated_content, str):
                                full_text_to_translate = f"Câu hỏi: {q['question']}\nĐáp án: {'; '.join(q['options'])}"
                                st.session_state.translations[translation_key] = translate_text(full_text_to_translate)
                                translated_content = st.session_state.translations[translation_key]

                            st.info(translated_content, icon="🌐")

                        # Hiển thị Radio Button
                        default_val = st.session_state.get(q_key, q["options"][0] if q["options"] else None)
                        st.radio("", q["options"], index=q["options"].index(default_val) if default_val in q["options"] else 0, key=q_key)
                        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
                    if st.button("✅ Nộp bài", key="submit_group"):
                        st.session_state.submitted = True
                        st.session_state.active_translation_key = None # Tắt dịch khi nộp bài
                        st.rerun()
                else:
                    score = 0
                    for i, q in enumerate(batch, start=start+1):
                        q_key = f"q_{i}_{hash(q['question'])}" 
                        selected_opt = st.session_state.get(q_key)
                        correct = clean_text(q["answer"])
                        is_correct = clean_text(selected_opt) == correct
                        translation_key = f"trans_{q_key}"
                        is_active = (translation_key == st.session_state.active_translation_key)

                      # Hiển thị câu hỏi (ĐÃ CẬP NHẬT LOGIC HIỂN THỊ PL3)
                        if q["question"].startswith("📝 "):
                            content_parts = q["question"].split("\n\n", 1)
                            passage = content_parts[0].replace("📝 ", "").strip()
                            question_text = content_parts[1].strip() if len(content_parts) > 1 else ""
                            st.markdown(f'<div class="bank-question-text" style="color:#00D4FF !important;">**Đoạn văn:** {passage}</div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="bank-question-text">{i}. {question_text}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True)

                        # Nút Dịch ở dưới
                        st.toggle(
                            "🌐 Dịch sang Tiếng Việt", 
                            value=is_active, 
                            key=f"toggle_{translation_key}",
                            on_change=on_translate_toggle,
                            args=(translation_key,)
                        )

                        # Hiển thị Bản Dịch
                        if is_active:
                            # Check if translated content is already cached
                            translated_content = st.session_state.translations.get(translation_key)
                            
                            # If not cached or is not a string (default True/False state)
                            if not isinstance(translated_content, str):
                                full_text_to_translate = f"Câu hỏi: {q['question']}\nĐáp án: {'; '.join(q['options'])}"
                                st.session_state.translations[translation_key] = translate_text(full_text_to_translate)
                                translated_content = st.session_state.translations[translation_key]

                            st.info(translated_content, icon="🌐")

                        # Hiển thị Đáp án (KẾT QUẢ)
                        for opt in q["options"]:
                            opt_clean = clean_text(opt)
                            if opt_clean == correct:
                                color_style = "color:#00ff00;" # Xanh lá, bỏ shadow
                            elif opt_clean == clean_text(selected_opt):
                                color_style = "color:#ff3333;" # Đỏ, bỏ shadow
                            else:
                                color_style = "color:#FFFFFF;" # Trắng chân phương
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
                            st.session_state.active_translation_key = None # Reset dịch khi làm lại
                            st.rerun()
                    with col_next:
                        if st.session_state.current_group_idx < len(groups) - 1:
                            if st.button("➡️ Tiếp tục nhóm sau", key="next_group"):
                                st.session_state.current_group_idx += 1
                                st.session_state.submitted = False
                                st.session_state.active_translation_key = None # Reset dịch khi chuyển nhóm
                                st.rerun()
                        else: st.info("🎉 Đã hoàn thành tất cả các nhóm câu hỏi!")
            else: st.warning("Không có câu hỏi trong nhóm này.")
        else: st.warning("Không có câu hỏi nào trong ngân hàng này.")

    elif st.session_state.current_mode == "all":
        if st.button("⬅️ Quay lại chế độ Luyện tập theo nhóm"):
            st.session_state.current_mode = "group"
            st.session_state.active_translation_key = None # Reset dịch khi chuyển mode
            st.rerun()
        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
        display_all_questions(questions)
        
    elif st.session_state.current_mode == "test":
        if st.button("⬅️ Quay lại chế độ Luyện tập theo nhóm"):
            st.session_state.current_mode = "group"
            st.session_state.active_translation_key = None # Reset dịch khi chuyển mode
            st.rerun()
        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
        display_test_mode(questions, bank_choice)
