# -*- coding: utf-8 -*-
import streamlit as st
from docx import Document
from docx.enum.text import WD_COLOR_INDEX 
import re
import math
import pandas as pd
import base64
import os
import random 
from translate import Translator 

# ====================================================
#  ⚙️  HÀM HỖ TRỢ VÀ FILE I/O
# ====================================================
def clean_text(s: str) -> str:
    if s is None:
        return ""
    
    temp_s = s
    placeholders = {}
    counter = 0
    
    # BƯỚC 1: Xử lý ngoặc có nhiều space/ký tự → chuẩn hóa thành 4 spaces
    temp_s = re.sub(r'\([\s._-]{2,}\)', '(    )', temp_s)
    temp_s = re.sub(r'\[[\s._-]{2,}\]', '[    ]', temp_s)
    
    # BƯỚC 2: Lưu các pattern điền chỗ trống còn lại
    standalone_patterns = [
        r'(?<!\S)([._])(?:\s*\1){1,9}(?!\S)',  
        r'-{2,10}',  
        r'\([\s]{2,}\)',  
        r'\[[\s]{2,}\]',  
    ]
    
    for pattern in standalone_patterns:
        for match in re.finditer(pattern, temp_s):
            matched_text = match.group()
            placeholder = f"__PLACEHOLDER_{counter}__"
            placeholders[placeholder] = matched_text
            temp_s = temp_s.replace(matched_text, placeholder, 1)
            counter += 1
    
    # BƯỚC 3: Xóa khoảng trắng thừa
    temp_s = re.sub(r'\s{2,}', ' ', temp_s)
    
    # BƯỚC 4: Khôi phục các pattern đã lưu
    for placeholder, original in placeholders.items():
        temp_s = temp_s.replace(placeholder, original)
    
    return temp_s.strip()

def find_file_path(source):
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

def read_pl2_data(source):
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
        data.append({"full_text": p_text_stripped, "has_yellow_highlight": False})
        
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
#  🌐  HÀM DỊCH THUẬT
# ====================================================
@st.cache_resource
def get_translator():
    try:
        translator = Translator(to_lang="vi") 
        return translator
    except Exception as e:
        print(f"Lỗi khởi tạo translate.Translator: {e}")
        return None

def translate_text(text):
    translator = get_translator()
    
    if translator is None:
        parts = text.split('\nĐáp án: ')
        q_content = parts[0].replace('Câu hỏi: ', '').strip()
        a_content_raw = parts[1].strip() if len(parts) > 1 else ""
        options = [opt.strip() for opt in a_content_raw.split(';') if opt.strip()]
        q_translated_text = f"Nội dung: *{q_content}*."
        a_translated_text = "\n".join([f"- {i+1}. Dịch của: {opt}" for i, opt in enumerate(options)])
        return f"""**[Bản dịch Tiếng Việt]**\n\n- **Câu hỏi:** {q_translated_text}\n- **Các đáp án:** \n{a_translated_text}"""
    
    try:
        parts = text.split('\nĐáp án: ')
        q_content = parts[0].replace('Câu hỏi: ', '').strip()
        a_content_raw = parts[1].strip() if len(parts) > 1 else ""
        options = [opt.strip() for opt in a_content_raw.split(';') if opt.strip()]
        
        q_translated = translator.translate(q_content)
        
        a_translated_list = []
        for i, option_content in enumerate(options):
            if not option_content:
                a_translated_list.append("")
                continue
            
            original_prefix_match = re.match(r'^([a-d]\.|\s*)\s*', option_content, re.IGNORECASE)
            original_prefix = original_prefix_match.group(0).strip() if original_prefix_match and original_prefix_match.group(0).strip() else f"{i+1}."
            translated_text = translator.translate(option_content)
            
            stripped_translated_text = translated_text.lstrip(original_prefix).strip()
            if not stripped_translated_text:
                 stripped_translated_text = translated_text
            
            a_translated_list.append(f"{original_prefix} {stripped_translated_text}")
        
        a_translated_text = "\n".join([f"- {opt}" for opt in a_translated_list])
        
        return f"**[Bản dịch Tiếng Việt]**\n\n- **Câu hỏi:** {q_translated}\n- **Các đáp án:** \n{a_translated_text}"
    except Exception as e:
        print(f"LỖI DỊCH THUẬT 'translate': {e}")
        return f"**[LỖI DỊCH THUẬT]**\n- Không thể dịch nội dung. Chi tiết lỗi đã được ghi lại (Exception: {type(e).__name__}).\n- Câu hỏi gốc:\n{text}"

# ====================================================
#  🧩  PARSERS
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

def parse_pl1(source):
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

def parse_pl2(source):
    data = read_pl2_data(source)
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
#  🌟  HÀM: LOGIC DỊCH ĐỘC QUYỀN (EXCLUSIVE TRANSLATION)
# ====================================================
if 'active_translation_key' not in st.session_state: st.session_state.active_translation_key = None
def on_translate_toggle(key_clicked):
    toggle_key = f"toggle_{key_clicked}"
    is_on_after_click = st.session_state.get(toggle_key, False)
    
    if is_on_after_click:
        st.session_state.active_translation_key = key_clicked
    elif st.session_state.active_translation_key == key_clicked:
        st.session_state.active_translation_key = None
    
    st.rerun()

# ====================================================
#  🌟  HÀM: XEM TOÀN BỘ CÂU HỎI
# ====================================================
def display_all_questions(questions):
    st.markdown('<div class="result-title"><h3> 📚  TOÀN BỘ NGÂN HÀNG CÂU HỎI</h3></div>', unsafe_allow_html=True)
    if not questions:
        st.warning("Không có câu hỏi nào để hiển thị.")
        return
    
    for i, q in enumerate(questions, start=1):
        q_key = f"all_q_{i}_{hash(q['question'])}" 
        translation_key = f"trans_{q_key}"
        is_active = (translation_key == st.session_state.active_translation_key)
        
        col_q_text, col_translate = st.columns([0.9, 0.1])
        
        with col_q_text:
            st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True)
        
        with col_translate:
            st.toggle(
                "Dịch", 
                value=is_active, 
                key=f"toggle_{translation_key}",
                on_change=on_translate_toggle,
                args=(translation_key,)
            )
        
        if is_active:
            translated_content = st.session_state.translations.get(translation_key)
            if not isinstance(translated_content, str):
                full_text_to_translate = f"Câu hỏi: {q['question']}\nĐáp án: {'; '.join(q['options'])}"
                st.session_state.translations[translation_key] = translate_text(full_text_to_translate)
                translated_content = st.session_state.translations[translation_key]
            st.markdown(f'<div class="translation-box">🌐 {translated_content}</div>', unsafe_allow_html=True) 
            
        for opt in q["options"]:
            if clean_text(opt) == clean_text(q["answer"]):
                color_style = "color:#00ff00;"
            else:
                color_style = "color:#FFFFFF;"
            st.markdown(f'<div class="bank-answer-text" style="{color_style}">{opt}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)

# ====================================================
#  🌟  HÀM: TEST MODE
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
        st.markdown('<div class="result-title"><h3> 📝  LÀM BÀI TEST 50 CÂU</h3></div>', unsafe_allow_html=True)
        
        if st.button(" 🚀  Bắt đầu Bài Test", key=f"{test_key_prefix}_start_btn"):
            st.session_state[f"{test_key_prefix}_questions"] = get_random_questions(questions, TOTAL_QUESTIONS)
            st.session_state[f"{test_key_prefix}_started"] = True
            st.session_state[f"{test_key_prefix}_submitted"] = False
            st.session_state.current_mode = "test" 
            st.rerun()
        return
        
    if not st.session_state[f"{test_key_prefix}_submitted"]:
        st.markdown('<div class="result-title"><h3> ⏳  ĐANG LÀM BÀI TEST</h3></div>', unsafe_allow_html=True)
        test_batch = st.session_state[f"{test_key_prefix}_questions"]
       
        for i, q in enumerate(test_batch, start=1):
            q_key = f"{test_key_prefix}_q_{i}_{hash(q['question'])}" 
            translation_key = f"trans_{q_key}"
            is_active = (translation_key == st.session_state.active_translation_key)
            
            col_q_text, col_translate = st.columns([0.9, 0.1])
            
            with col_q_text:
                st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True)
            with col_translate:
                st.toggle(
                    "Dịch", 
                    value=is_active, 
                    key=f"toggle_{translation_key}",
                    on_change=on_translate_toggle,
                    args=(translation_key,)
                )
                
            if is_active:
                translated_content = st.session_state.translations.get(translation_key)
                if not isinstance(translated_content, str):
                    full_text_to_translate = f"Câu hỏi: {q['question']}\nĐáp án: {'; '.join(q['options'])}"
                    st.session_state.translations[translation_key] = translate_text(full_text_to_translate)
                    translated_content = st.session_state.translations[translation_key]
                st.markdown(f'<div class="translation-box">🌐 {translated_content}</div>', unsafe_allow_html=True) 
      
            default_val = st.session_state.get(q_key, q["options"][0] if q["options"] else None)
            st.radio("", q["options"], index=q["options"].index(default_val) if default_val in q["options"] else 0, key=q_key)
            st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True) 
            
        if st.button(" ✅  Nộp bài Test", key=f"{test_key_prefix}_submit_btn"):
            st.session_state[f"{test_key_prefix}_submitted"] = True
            st.rerun()
            
    else:
        st.markdown('<div class="result-title"><h3> 🎉  KẾT QUẢ BÀI TEST</h3></div>', unsafe_allow_html=True)
        test_batch = st.session_state[f"{test_key_prefix}_questions"]
        score = 0
        
        for i, q in enumerate(test_batch, start=1):
            q_key = f"{test_key_prefix}_q_{i}_{hash(q['question'])}" 
            selected_opt = st.session_state.get(q_key)
            correct = clean_text(q["answer"])
            is_correct = clean_text(selected_opt) == correct
            translation_key = f"trans_{q_key}"
            is_active = (translation_key == st.session_state.active_translation_key)
            
            col_q_text, col_translate = st.columns([0.9, 0.1])
            
            with col_q_text:
                st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True)
            with col_translate:
                st.toggle(
                    "Dịch", 
                    value=is_active, 
                    key=f"toggle_{translation_key}",
                    on_change=on_translate_toggle,
                    args=(translation_key,)
                )
                
            if is_active:
                translated_content = st.session_state.translations.get(translation_key)
                if not isinstance(translated_content, str):
                    full_text_to_translate = f"Câu hỏi: {q['question']}\nĐáp án: {'; '.join(q['options'])}"
                    st.session_state.translations[translation_key] = translate_text(full_text_to_translate)
                    translated_content = st.session_state.translations[translation_key]
                st.markdown(f'<div class="translation-box">🌐 {translated_content}</div>', unsafe_allow_html=True) 
      
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
            st.info(f"Đáp án đúng: **{q['answer']}**", icon=" 💡 ")
            st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True) 
        
        total_q = len(test_batch)
        pass_threshold = total_q * PASS_RATE
        st.markdown(f'<div class="result-title"><h3> 🎯  KẾT QUẢ: {score}/{total_q}</h3></div>', unsafe_allow_html=True)
   
        if score >= pass_threshold:
            st.balloons()
            st.success(f" 🎊  **CHÚC MỪNG!** Bạn đã ĐẠT (PASS).")
        else:
            st.error(f" 😢  **KHÔNG ĐẠT (FAIL)**. Cần {math.ceil(pass_threshold)} câu đúng để Đạt.")
            
        if st.button(" 🔄  Làm lại Bài Test", key=f"{test_key_prefix}_restart_btn"):
            for i, q in enumerate(test_batch, start=1):
                st.session_state.pop(f"{test_key_prefix}_q_{i}_{hash(q['question'])}", None)
            st.session_state.pop(f"{test_key_prefix}_questions", None)
            st.session_state[f"{test_key_prefix}_started"] = False
            st.session_state[f"{test_key_prefix}_submitted"] = False
            st.rerun()

# ====================================================
#  🖥️  GIAO DIỆN STREAMLIT
# ====================================================
st.set_page_config(page_title="Ngân hàng trắc nghiệm", layout="wide")
PC_IMAGE_FILE = "bank_PC.jpg"
MOBILE_IMAGE_FILE = "bank_mobile.jpg"
img_pc_base64 = get_base64_encoded_file(PC_IMAGE_FILE)
img_mobile_base64 = get_base64_encoded_file(MOBILE_IMAGE_FILE)

# --- CUSTOM CSS: ĐÃ SỬ DỤNG f'''...''' (TRIPLE SINGLE QUOTES) ---
css = f'''
<style>
#MainMenu, footer, header, [data-testid="stHeader"] {{visibility: hidden; height: 0; display: none;}}
#back-to-home-btn-container {{position: fixed; top: 10px; left: 10px; width: auto !important; z-index: 1500; display: inline-block;}}
a#manual-home-btn {{background-color: rgba(0, 0, 0, 0.85); color: #FFEA00; border: 2px solid #FFEA00; padding: 5px 10px; border-radius: 8px; font-weight: bold; font-size: 14px; transition: all 0.3s; font-family: 'Oswald', sans-serif; text-decoration: none; display: inline-block; white-space: nowrap; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);}}
a#manual-home-btn:hover {{background-color: #FFEA00; color: black; transform: scale(1.05);}}
#main-title-container {{position: relative; left: 0; top: 0; width: 100%; height: 120px; overflow: hidden; pointer-events: none; background-color: transparent; padding-top: 20px; z-index: 1200;}}
#main-title-container h1 {{visibility: visible !important; height: auto !important; font-family: 'Playfair Display', serif; font-size: 5vh; margin: 0; padding: 10px 0; font-weight: 900; letter-spacing: 5px; white-space: nowrap; display: inline-block; background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3); background-size: 400% 400%; -webkit-background-clip: text; -webkit-text-fill-color: transparent; color: transparent; animation: scrollRight 15s linear infinite, colorShift 8s ease infinite; text-shadow: 2px 2px 8px rgba(255, 255, 255, 0.3); position: absolute; left: 0;}}
[data-testid="stAppViewBlockContainer"] {{background-color: #0b1115; background-image: url('data:image/jpeg;base64,{img_pc_base64}'); background-size: cover; background-attachment: fixed; background-position: center center; padding-top: 1rem;}}
@media (max-width: 600px) {{[data-testid="stAppViewBlockContainer"] {{background-image: url('data:image/jpeg;base64,{img_mobile_base64}'); background-size: cover;}}}}
@keyframes scrollRight {{0% {{ transform: translateX(-50%); }} 50% {{ transform: translateX(50%); }} 100% {{ transform: translateX(-50%); }}}}
@keyframes colorShift {{0%, 100% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }}}}
.result-title h3 {{font-family: 'Playfair Display', serif; font-size: 2.5em !important; color: #FFEA00; text-align: center; margin: 20px 0; font-weight: 800; text-shadow: 0 0 10px rgba(255, 234, 0, 0.5);}}
.bank-question-text {{color: #b7a187 !important; font-family: 'Oswald', sans-serif !important; font-weight: 700 !important; font-size: 22px !important; text-shadow: none; padding: 5px 15px; margin-bottom: 10px; line-height: 1.4 !important;}}
.bank-answer-text {{font-family: 'Oswald', sans-serif !important; font-weight: 700 !important; font-size: 22px !important; padding: 5px 15px; margin: 2px 0; line-height: 1.5 !important; display: block;}}
.stRadio label {{color: #FFFFFF !important; font-size: 22px !important; font-weight: 700 !important; font-family: 'Oswald', sans-serif !important; padding: 2px 12px; text-shadow: none !important; background-color: transparent !important; border: none !important; display: block !important; margin: 4px 0 !important; letter-spacing: 0.5px !important;}}
.stRadio label:hover {{text-shadow: none !important;}}
.stRadio label span, .stRadio label p, .stRadio label div {{color: #FFFFFF !important; text-shadow: none !important; letter-spacing: 0.5px !important;}}
div[data-testid="stMarkdownContainer"] p {{font-size: 22px !important;}}
.stButton>button {{background-color: #b7a187 !important; color: #ffffff !important; border-radius: 8px; font-size: 1.1em !important; font-weight: 600 !important; font-family: 'Oswald', sans-serif !important; border: none !important; padding: 10px 20px !important; width: 100%;}}
.stToggle label p {{font-size: 14px !important; font-weight: 800 !important; color: #FFEA00 !important;}}
.translation-box {{background-color: #FFFACD; color: #000000 !important; border-left: 5px solid #FFEA00; padding: 15px; border-radius: 8px; margin: 10px 0; font-size: 22px; font-family: 'Oswald', sans-serif !important; white-space: pre-wrap;}}
.translation-box p, .translation-box strong, .translation-box li {{color: #000000 !important;}}
.question-separator {{border-bottom: 2px dashed #b7a187; margin: 25px 0; width: 100%;}}
.stAlert > div {{background-color: #0b1115 !important; color: #FFFFFF !important; border: 1px solid #FFEA00 !important;}}
</style>
'''

st.markdown(css, unsafe_allow_html=True)

# ====================================================
#  🖥️  LOGIC APP
# ====================================================
if 'questions' not in st.session_state: st.session_state.questions = []
if 'current_mode' not in st.session_state: st.session_state.current_mode = "group"
if 'submitted' not in st.session_state: st.session_state.submitted = False
if 'current_group_idx' not in st.session_state: st.session_state.current_group_idx = 0
if 'translations' not in st.session_state: st.session_state.translations = {}
if 'active_translation_key' not in st.session_state: st.session_state.active_translation_key = None

BANK_OPTIONS = ["----", "Ngân hàng Kỹ thuật", "Ngân hàng Luật VAECO", "Ngân hàng Docwise"]
bank_choice = st.selectbox("Chọn ngân hàng:", BANK_OPTIONS, index=BANK_OPTIONS.index(st.session_state.get('bank_choice_val', '----')), key="bank_selector_master")
st.session_state.bank_choice_val = bank_choice

if st.session_state.get('last_bank_choice') != bank_choice and bank_choice != "----":
    st.session_state.current_group_idx = 0
    st.session_state.submitted = False
    st.session_state.current_mode = "group"
    st.session_state.active_translation_key = None 
    last_bank_name = st.session_state.get('last_bank_choice')
    if not isinstance(last_bank_name, str) or last_bank_name == "----": last_bank_name = "null bank"
    bank_slug_old = last_bank_name.split()[-1].lower()
    st.session_state.pop(f"test_{bank_slug_old}_started", None)
    st.session_state.pop(f"test_{bank_slug_old}_submitted", None)
    st.session_state.pop(f"test_{bank_slug_old}_questions", None)
    st.session_state.last_bank_choice = bank_choice
    st.rerun()

if bank_choice != "----":
    source = ""
    is_docwise = False
    if "Kỹ thuật" in bank_choice:
        source = "cabbank.docx"
        parser = parse_cabbank
    elif "Luật VAECO" in bank_choice:
        source = "lawbank.docx"
        parser = parse_lawbank
    elif "Docwise" in bank_choice:
        is_docwise = True
        doc_options = ["Phụ lục 1 : Ngữ pháp chung", "Phụ lục 2 : Từ vựng, thuật ngữ"]
        doc_selected_new = st.selectbox("Chọn Phụ lục:", doc_options, index=doc_options.index(st.session_state.get('doc_selected', doc_options[0])), key="docwise_selector")
        
        if st.session_state.doc_selected != doc_selected_new:
            st.session_state.doc_selected = doc_selected_new
            st.session_state.current_group_idx = 0
            st.session_state.submitted = False
            st.session_state.current_mode = "group"
            st.rerun()
            
        if st.session_state.doc_selected == "Phụ lục 1 : Ngữ pháp chung":
            source = "PL1.docx"
            parser = parse_pl1
        else:
            source = "PL2.docx"
            parser = parse_pl2
            
    st.session_state.questions = parser(source)
    questions = st.session_state.questions
    
    if not questions and source:
        st.error(f" ❌ Không đọc được câu hỏi nào từ file **{source}**. Vui lòng kiểm tra file và cấu trúc thư mục (đảm bảo file nằm trong thư mục gốc hoặc thư mục 'pages/'), và kiểm tra lại định dạng đáp án đúng (dùng dấu `(*)`).")
        st.stop()
        
    total = len(questions)
    
    # --- MODE: GROUP ---
    if st.session_state.current_mode == "group":
        st.markdown('<div class="result-title" style="margin-top: 0px;"><h3>Luyện tập theo nhóm (30 câu/nhóm)</h3></div>', unsafe_allow_html=True)
        group_size = 30
        
        if total > 0:
            groups = [f"Câu {i*group_size+1}-{min((i+1)*group_size, total)}" for i in range(math.ceil(total/group_size))]
            if st.session_state.current_group_idx >= len(groups): st.session_state.current_group_idx = 0
            
            selected = st.selectbox("Chọn nhóm câu:", groups, index=st.session_state.current_group_idx, key="group_selector")
            
            new_idx = groups.index(selected)
            if st.session_state.current_group_idx != new_idx:
                st.session_state.current_group_idx = new_idx
                st.session_state.submitted = False
                st.session_state.active_translation_key = None
                st.rerun()
                
            idx = st.session_state.current_group_idx
            start, end = idx * group_size, min((idx+1) * group_size, total)
            batch = questions[start:end]
            
            st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
            
            col_all_bank, col_test = st.columns(2)
            with col_all_bank:
                if st.button(" 📖 Hiển thị toàn bộ ngân hàng", key="btn_show_all"):
                    st.session_state.current_mode = "all"
                    st.session_state.active_translation_key = None
                    st.rerun()
            with col_test:
                if st.button("Làm bài test", key="btn_start_test"):
                    st.session_state.current_mode = "test"
                    st.session_state.active_translation_key = None
                    bank_slug_new = bank_choice.split()[-1].lower()
                    test_key_prefix = f"test_{bank_slug_new}"
                    st.session_state.pop(f"{test_key_prefix}_started", None)
                    st.session_state.pop(f"{test_key_prefix}_submitted", None)
                    st.session_state.pop(f"{test_key_prefix}_questions", None)
                    st.rerun()
            
            st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
            
            if batch:
                if not st.session_state.submitted:
                    for i, q in enumerate(batch, start=start+1):
                        q_key = f"q_{i}_{hash(q['question'])}" 
                        translation_key = f"trans_{q_key}"
                        is_active = (translation_key == st.session_state.active_translation_key)
                        
                        col_q_text, col_translate = st.columns([0.9, 0.1])
                        with col_q_text:
                            st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True)
                        with col_translate:
                            st.toggle(
                                "Dịch", 
                                value=is_active, 
                                key=f"toggle_{translation_key}",
                                on_change=on_translate_toggle,
                                args=(translation_key,)
                            )

                        if is_active:
                            translated_content = st.session_state.translations.get(translation_key)
                            if not isinstance(translated_content, str):
                                full_text_to_translate = f"Câu hỏi: {q['question']}\nĐáp án: {'; '.join(q['options'])}"
                                st.session_state.translations[translation_key] = translate_text(full_text_to_translate)
                                translated_content = st.session_state.translations[translation_key]
                            st.markdown(f'<div class="translation-box">🌐 {translated_content}</div>', unsafe_allow_html=True) 
                            
                        default_val = st.session_state.get(q_key, q["options"][0] if q["options"] else None)
                        st.radio("", q["options"], index=q["options"].index(default_val) if default_val in q["options"] else 0, key=q_key)
                        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
                        
                    if st.button(" ✅  Nộp bài", key="submit_group"):
                        st.session_state.submitted = True
                        st.session_state.active_translation_key = None
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

                        col_q_text, col_translate = st.columns([0.9, 0.1])
                        with col_q_text:
                            st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True)
                        with col_translate:
                            st.toggle(
                                "Dịch", 
                                value=is_active, 
                                key=f"toggle_{translation_key}",
                                on_change=on_translate_toggle,
                                args=(translation_key,)
                            )
                        
                        if is_active:
                            translated_content = st.session_state.translations.get(translation_key)
                            if not isinstance(translated_content, str):
                                full_text_to_translate = f"Câu hỏi: {q['question']}\nĐáp án: {'; '.join(q['options'])}"
                                st.session_state.translations[translation_key] = translate_text(full_text_to_translate)
                                translated_content = st.session_state.translations[translation_key]
                            st.markdown(f'<div class="translation-box">🌐 {translated_content}</div>', unsafe_allow_html=True) 

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
                        st.info(f"Đáp án đúng: **{q['answer']}**", icon=" 💡 ")
                        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
                    
                    st.markdown(f'<div class="result-title"><h3> 🎯  KẾT QUẢ NHÓM: {score}/{len(batch)}</h3></div>', unsafe_allow_html=True)
                    
                    col_restart, col_next = st.columns(2)
                    with col_restart:
                        if st.button(" 🔄  Làm lại nhóm này", key="restart_group"):
                            for i, q in enumerate(batch, start=start+1):
                                st.session_state.pop(f"q_{i}_{hash(q['question'])}", None)
                            st.session_state.submitted = False
                            st.session_state.active_translation_key = None
                            st.rerun()
                    with col_next:
                        if st.session_state.current_group_idx < len(groups) - 1:
                            if st.button(" ➡️  Tiếp tục nhóm sau", key="next_group"):
                                st.session_state.current_group_idx += 1
                                st.session_state.submitted = False
                                st.session_state.active_translation_key = None
                                st.rerun()
                        else: st.info(" 🎉  Đã hoàn thành tất cả các nhóm câu hỏi!")
            else: st.warning("Không có câu hỏi trong nhóm này.")
        else: st.warning("Không có câu hỏi nào trong ngân hàng này.")
        
    elif st.session_state.current_mode == "all":
        if st.button(" ⬅️  Quay lại chế độ Luyện tập theo nhóm"):
            st.session_state.current_mode = "group"
            st.session_state.active_translation_key = None
            st.rerun()
        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
        display_all_questions(questions)
        
    elif st.session_state.current_mode == "test":
        if st.button(" ⬅️  Quay lại chế độ Luyện tập theo nhóm"):
            st.session_state.current_mode = "group"
            st.session_state.active_translation_key = None
            st.rerun()
        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
        display_test_mode(questions, bank_choice)
