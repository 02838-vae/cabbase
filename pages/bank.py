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
# THAY THẾ googletrans bằng translate
from translate import Translator # <-- THAY THẾ THƯ VIỆN

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
    # VD: (__           __) → (    )
    temp_s = re.sub(r'\([\\s._-]{2,}\)', '(    )', temp_s)  # Ngoặc đơn
    temp_s = re.sub(r'\[[\\s._-]{2,}\]', '[    ]', temp_s)  # Ngoặc vuông
    temp_s = re.sub(r'\{[\\s._-]{2,}\}', '{    }', temp_s)  # Ngoặc nhọn

    # BƯỚC 2: Tạm thời thay thế các pattern điền chỗ trống
    def replace_placeholder(match):
        nonlocal counter
        key = f"__PLACEHOLDER_{counter}__"
        placeholders[key] = match.group(0)
        counter += 1
        return key

    # Regex cho các pattern điền chỗ trống đã chuẩn hóa
    temp_s = re.sub(r'\([ ]{4}\)|\(\.\.\.\.\)|\[[ ]{4}\]|\[\.\.\.\.\]|{[ ]{4}}|{\.\.\.\.}', replace_placeholder, temp_s)
    temp_s = re.sub(r'[._-]([\\s]*[._-]){2,9}', replace_placeholder, temp_s) # Dấu chấm/gạch dưới 2-10 lần

    # BƯỚC 3: Xử lý làm sạch thông thường
    
    # 1. Chuẩn hóa space:
    # - Loại bỏ space dư thừa ở đầu/cuối
    temp_s = temp_s.strip()
    # - Thay thế nhiều space bằng 1 space
    temp_s = re.sub(r'\\s+', ' ', temp_s)
    # 2. Xử lý dấu câu (loại bỏ space trước dấu câu):
    temp_s = re.sub(r'\\s+([.,!?:;])', r'\\1', temp_s)
    # 3. Chuẩn hóa dấu nháy đơn
    temp_s = temp_s.replace("’", "'").replace("‘", "'")
    
    # BƯỚC 4: Phục hồi các pattern điền chỗ trống
    for key, value in placeholders.items():
        temp_s = temp_s.replace(key, value)
        
    return temp_s

def read_docx(uploaded_file):
    questions = []
    current_group = None
    
    # Ghi file tạm thời để docx có thể đọc được
    with open("temp.docx", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    doc = Document("temp.docx")
    
    # Xóa file tạm
    os.remove("temp.docx")
    
    # Regex để tìm câu hỏi và đáp án
    # Câu hỏi: bắt đầu bằng số (có chấm), có thể có space sau số, và có nội dung
    question_pattern = re.compile(r'^(\\d+)\\.[\t ]*(.*)', re.IGNORECASE)
    # Đáp án: bắt đầu bằng chữ cái (có chấm hoặc đóng ngoặc), có thể có space sau chữ cái, và có nội dung
    answer_pattern = re.compile(r'^([A-Za-z])(?:[.\\)])[\t ]*(.*)', re.IGNORECASE)

    current_question = None
    
    # Đọc theo đoạn (paragraph)
    for paragraph in doc.paragraphs:
        text = clean_text(paragraph.text)
        
        # 1. Tìm Nhóm Câu hỏi (Group)
        # Nhóm được định dạng là: Group <Số>: <Tiêu đề> (VD: Group 1: General English)
        if text.lower().startswith("group"):
            match = re.search(r'Group[\\s:]*(\\d+)[\\s:]*(.*)', text, re.IGNORECASE)
            if match:
                group_number = int(match.group(1))
                group_title = clean_text(match.group(2))
                current_group = {
                    "id": group_number,
                    "title": group_title if group_title else f"Nhóm {group_number}",
                    "questions": []
                }
                questions.append(current_group)
                current_question = None # Reset câu hỏi khi bắt đầu nhóm mới
                continue

        # Bỏ qua các đoạn trống hoặc quá ngắn
        if not text or len(text) < 2:
            continue
            
        # 2. Tìm Câu hỏi (Question)
        match_q = question_pattern.match(text)
        if match_q:
            # Nếu chưa có nhóm, tạo nhóm mặc định
            if not current_group:
                current_group = {
                    "id": 0,
                    "title": "Nhóm Mặc Định",
                    "questions": []
                }
                questions.append(current_group)
                
            question_number = int(match_q.group(1))
            question_content = match_q.group(2).strip()

            # Lấy đáp án đúng từ highlight trong docx
            correct_answer_text = None
            
            # Chỉ xét các Run trong paragraph có chứa câu hỏi
            for run in paragraph.runs:
                # Kiểm tra nếu có highlight màu vàng (WD_COLOR_INDEX.YELLOW)
                if run.font.highlight == WD_COLOR_INDEX.YELLOW:
                    # Làm sạch text của run đó
                    highlighted_text = clean_text(run.text)
                    
                    # Cố gắng tìm đáp án (A, B, C, D...) trong phần highlight
                    match_highlight_ans = answer_pattern.match(highlighted_text)
                    if match_highlight_ans:
                        correct_answer_text = match_highlight_ans.group(1).upper() # Chỉ lấy chữ cái
                        break
                    
            current_question = {
                "number": question_number,
                "content": question_content,
                "options": {},
                "correct_answer": correct_answer_text, # Đáp án đúng là chữ cái (A, B, C...)
                "explanation": None,
                "is_multichoice": False, # Sẽ cập nhật sau
                "full_text": text # Giữ lại text đầy đủ để tìm lời giải
            }
            current_group["questions"].append(current_question)
            continue
            
        # 3. Tìm Đáp án (Option)
        match_a = answer_pattern.match(text)
        if current_question and match_a:
            option_key = match_a.group(1).upper() # A, B, C, D...
            option_content = match_a.group(2).strip()
            
            # Thêm đáp án vào câu hỏi hiện tại
            current_question["options"][option_key] = option_content
            current_question["is_multichoice"] = True
            
            # Cập nhật đáp án đúng nếu tìm thấy trong highlight của đáp án (trường hợp hiếm)
            # Dùng lại logic highlight
            for run in paragraph.runs:
                if run.font.highlight == WD_COLOR_INDEX.YELLOW:
                    # Nếu đáp án này được highlight, đây là đáp án đúng
                    current_question["correct_answer"] = option_key
                    break
            
            continue
            
        # 4. Tìm Lời giải (Explanation)
        # Giả định lời giải nằm ngay sau câu hỏi và/hoặc đáp án, và không có định dạng đặc biệt
        # Logic đơn giản: Nếu có câu hỏi hiện tại, và đoạn văn bản tiếp theo không phải là câu hỏi/đáp án/group mới, 
        # thì đó là một phần của lời giải.
        if current_question:
            # Kiểm tra xem có phải là bắt đầu của Lời giải không
            if text.lower().startswith("answer:"):
                # Cắt bỏ prefix "Answer:" hoặc "Explanation:"
                explanation_content = re.sub(r'^(Answer|Explanation)[\\s:]*', '', text, flags=re.IGNORECASE).strip()
            else:
                # Nếu không có prefix, coi nó là lời giải
                explanation_content = text

            if current_question["explanation"]:
                current_question["explanation"] += " " + explanation_content # Nối thêm vào lời giải
            else:
                current_question["explanation"] = explanation_content

    # Lọc lại để loại bỏ các nhóm không có câu hỏi
    filtered_questions = [group for group in questions if group["questions"]]

    # Sau khi đọc xong, xóa các key "full_text" không cần thiết
    for group in filtered_questions:
        for q in group["questions"]:
            if "full_text" in q:
                del q["full_text"]
                
    return filtered_questions

# ====================================================
# 🌍 HÀM DỊCH
# ====================================================
# Khởi tạo Translator (chỉ 1 lần)
# Sử dụng 'libre' hoặc 'mymemory' thay vì 'google' nếu gặp lỗi API
@st.cache_resource
def get_translator():
    # Thử các backend khác nhau nếu Google Translate bị hạn chế
    try:
        # Thử Google Translator (default)
        return Translator(to_lang="vi") 
    except Exception as e:
        st.warning(f"Không thể kết nối với dịch vụ Google Translate mặc định. Đang thử dịch vụ thay thế. Lỗi: {e}")
        try:
            # Thử LibreTranslate (cần cài thêm thư viện, nhưng có thể hoạt động tốt hơn)
            # Cần cài: pip install translate[libre]
            return Translator(to_lang="vi", provider="libre")
        except Exception as e_libre:
            st.error(f"Không thể kết nối với dịch vụ LibreTranslate. Lỗi: {e_libre}")
            # Nếu cả hai đều lỗi, trả về một đối tượng giả
            class DummyTranslator:
                def translate(self, text):
                    return f"[LỖI DỊCH THUẬT] {text}"
            return DummyTranslator()


def translate_text(text: str, translator: Translator) -> str:
    if not text:
        return ""
    try:
        # Giới hạn độ dài để tránh lỗi API
        if len(text) > 4500:
            text = text[:4500] + "..."
            
        # Dịch và trả về
        return translator.translate(text)
    except Exception as e:
        # st.error(f"Lỗi khi dịch: {e}")
        return f"[LỖI DỊCH THUẬT] Không thể dịch đoạn văn này. (Lỗi: {e})"

# ====================================================
# 📝 HÀM HIỂN THỊ
# ====================================================

# CSS tùy chỉnh để làm đẹp giao diện
def set_custom_css():
    st.markdown("""
        <style>
            /* Màu nền và chữ */
            body {
                color: #262730;
                background-color: #f0f2f6;
            }
            /* Tiêu đề ứng dụng */
            .main .stApp {
                background-color: #f0f2f6;
            }
            /* Tiêu đề nhóm câu hỏi */
            .group-title {
                font-size: 1.5rem;
                font-weight: bold;
                color: #0d6efd; /* Xanh dương */
                padding-bottom: 10px;
                border-bottom: 2px solid #0d6efd;
                margin-top: 20px;
                margin-bottom: 15px;
            }
            /* Khung chứa câu hỏi */
            .question-box {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
                background-color: #ffffff;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            }
            /* Nội dung câu hỏi */
            .question-content {
                font-size: 1.1rem;
                font-weight: 500;
                margin-bottom: 10px;
                line-height: 1.6;
            }
            /* Đáp án */
            .option-correct {
                background-color: #d4edda; /* Xanh lá nhạt - Đúng */
                color: #155724;
                border-left: 5px solid #28a745; /* Xanh lá đậm */
                padding: 8px;
                border-radius: 4px;
                margin: 5px 0;
            }
            .option-incorrect {
                background-color: #f8d7da; /* Đỏ nhạt - Sai */
                color: #721c24;
                border-left: 5px solid #dc3545; /* Đỏ đậm */
                padding: 8px;
                border-radius: 4px;
                margin: 5px 0;
            }
            .option-default {
                background-color: #f1f1f1; /* Xám nhạt - Chưa chọn */
                padding: 8px;
                border-radius: 4px;
                margin: 5px 0;
                cursor: pointer;
            }
            .option-selected {
                background-color: #cce5ff; /* Xanh dương nhạt - Đã chọn */
                border-left: 5px solid #007bff;
                padding: 8px;
                border-radius: 4px;
                margin: 5px 0;
                font-weight: 500;
            }
            /* Lời giải thích */
            .explanation-box {
                margin-top: 15px;
                padding: 10px;
                border-left: 4px solid #ffc107; /* Vàng */
                background-color: #fffbe6; /* Vàng nhạt */
                border-radius: 4px;
                font-style: italic;
                color: #856404;
            }
            /* Dịch thuật */
            .translation-box {
                margin-top: 10px;
                padding: 10px;
                border: 1px dashed #007bff;
                background-color: #e9f7ff;
                border-radius: 4px;
                font-size: 0.95rem;
            }
            /* Nút submit */
            .stButton>button {
                background-color: #28a745; /* Xanh lá */
                color: white !important;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                transition: background-color 0.3s;
            }
            .stButton>button:hover {
                background-color: #1e7e34;
            }
            /* Phân cách giữa các câu hỏi/nhóm */
            .question-separator {
                border-top: 2px dashed #ddd;
                margin: 30px 0;
            }
            
            /* === BỔ SUNG: CUSTOM SCROLLBAR === */
            /* WebKit (Chrome, Edge, Safari) */
            .stApp ::-webkit-scrollbar {
                width: 12px; /* Tăng bề rộng thanh cuộn */
                height: 12px; /* Tăng chiều cao thanh cuộn ngang (nếu có) */
            }
            .stApp ::-webkit-scrollbar-track {
                background: #111111; /* Màu nền tối hơn */
            }
            .stApp ::-webkit-scrollbar-thumb {
                background-color: #FFEA00; /* Màu vàng nổi bật */
                border-radius: 6px;
                border: 3px solid #111111;
            }
            .stApp ::-webkit-scrollbar-thumb:hover {
                background-color: #FFF066;
            }

            /* Firefox */
            .stApp {
                scrollbar-width: thin; /* 'auto' hoặc 'thin' */
                scrollbar-color: #FFEA00 #111111; /* thumb color track color */
            }
            /* === HẾT BỔ SUNG === */
        </style>
    """, unsafe_allow_html=True)

def display_question(q, index, mode="group_practice", show_answer=False, user_selection=None):
    """Hiển thị một câu hỏi.
    
    Args:
        q (dict): Thông tin câu hỏi.
        index (int): Chỉ số câu hỏi (để tạo key duy nhất).
        mode (str): "group_practice" (có nút submit) hoặc "all" (chỉ hiển thị).
        show_answer (bool): Hiển thị đáp án và lời giải.
        user_selection (str): Đáp án người dùng đã chọn (chỉ dùng trong group_practice).
    """
    
    # Tạo key cho trạng thái dịch thuật của câu hỏi này
    translation_key = f"translation_{index}"
    
    # Khung chứa câu hỏi
    st.markdown('<div class="question-box">', unsafe_allow_html=True)
    
    # Nội dung câu hỏi
    st.markdown(f'<div class="question-content"><b>{q["number"]}.</b> {q["content"]}</div>', unsafe_allow_html=True)
    
    # ---------------- Dịch thuật ----------------
    # Nút Dịch (chỉ hiển thị trong mode group_practice và all)
    if mode in ["group_practice", "all"]:
        # Khởi tạo state cho việc dịch thuật nếu chưa có
        if "active_translation_key" not in st.session_state:
            st.session_state.active_translation_key = None

        is_current_translation_active = (st.session_state.active_translation_key == translation_key)
        
        # Nút Dịch/Ẩn dịch
        label = "Dịch Tiếng Việt 🇻🇳" if not is_current_translation_active else "Ẩn Dịch 🇬🇧"
        if st.button(label, key=f"btn_translate_{index}", help="Dịch câu hỏi và đáp án sang Tiếng Việt"):
            if is_current_translation_active:
                st.session_state.active_translation_key = None # Ẩn dịch
            else:
                st.session_state.active_translation_key = translation_key # Bật dịch
            st.rerun() # Dịch cần rerun để cập nhật giao diện
            
        # Hiển thị bản dịch
        if is_current_translation_active:
            with st.spinner("Đang dịch..."):
                translator = get_translator()
                
                # Nối nội dung câu hỏi và tất cả đáp án
                text_to_translate = q["content"]
                for k, v in q["options"].items():
                    text_to_translate += f"\n{k}. {v}"
                
                # Dịch
                translation_result = translate_text(text_to_translate, translator)
                
                # Tách kết quả dịch
                lines = translation_result.split('\n')
                translated_content = lines[0] # Dòng đầu tiên là nội dung câu hỏi
                translated_options = lines[1:] # Các dòng còn lại là đáp án

                st.markdown('<div class="translation-box">', unsafe_allow_html=True)
                st.markdown(f"**Nội dung dịch:** {translated_content}")
                
                if translated_options:
                    st.markdown("**Đáp án dịch:**")
                    for line in translated_options:
                        st.write(line) # Dùng st.write để hiển thị đẹp hơn
                st.markdown('</div>', unsafe_allow_html=True)


    # ---------------- Đáp án ----------------
    if q["is_multichoice"]:
        option_keys = sorted(q["options"].keys())
        
        for option_key in option_keys:
            option_content = q["options"][option_key]
            is_correct = (option_key == q["correct_answer"])
            
            # 1. Chế độ hiển thị đáp án (mode "all" hoặc sau khi submit)
            if show_answer:
                if is_correct:
                    css_class = "option-correct"
                    icon = "✅"
                else:
                    # Nếu là đáp án người dùng đã chọn nhưng sai
                    if user_selection == option_key:
                        css_class = "option-incorrect"
                        icon = "❌"
                    else:
                        css_class = "option-default"
                        icon = ""
                
                st.markdown(f'<div class="{css_class}">{icon} <b>{option_key}.</b> {option_content}</div>', unsafe_allow_html=True)
                
            # 2. Chế độ luyện tập (mode "group_practice" - chưa submit)
            else:
                # Tạo một nút radio hoặc checkbox
                radio_key = f"q_{index}_option_{option_key}"
                
                # Xác định style dựa trên lựa chọn của người dùng (nếu có)
                if user_selection == option_key:
                    css_class = "option-selected"
                else:
                    css_class = "option-default"
                    
                # Logic lựa chọn (Chỉ áp dụng trong group_practice mode)
                if mode == "group_practice":
                    
                    # Nút/Div click
                    is_selected = (user_selection == option_key)
                    
                    # Dùng button giả lập radio
                    if st.button(f"**{option_key}.** {option_content}", key=f"btn_q{index}_{option_key}", help=f"Chọn đáp án {option_key}"):
                        # Cập nhật lựa chọn vào session_state
                        st.session_state.current_group_selections[q["number"]] = option_key
                        st.rerun() # Rerun để cập nhật UI
                    
                    # Tạm thời chấp nhận st.button mặc định hoặc dùng st.radio.
                    
                    pass # Logic lựa chọn được xử lý bằng st.radio trong hàm gọi

        # Nếu là mode luyện tập, dùng radio để chọn
        if mode == "group_practice" and not show_answer:
            
            # Đặt tất cả radio trong một cột riêng để tránh conflict
            selection = st.radio(
                "Lựa chọn của bạn:",
                options=option_keys,
                key=f"selection_q_{q['number']}",
                index=option_keys.index(user_selection) if user_selection in option_keys else None,
                format_func=lambda x: f"{x}. {q['options'][x]}", # Không dùng format_func này, dùng trực tiếp dưới đây
                label_visibility="collapsed"
            )
            
            # Cập nhật lựa chọn người dùng
            if selection:
                st.session_state.current_group_selections[q["number"]] = selection

            # Phải hiển thị từng option một cách thủ công với CSS để có hiệu ứng đẹp hơn (đang làm)
            # Tạm thời dùng st.radio chuẩn

        # Hiển thị đáp án đúng (trong mode "all" hoặc sau khi submit)
        if show_answer and q["correct_answer"]:
            correct_key = q["correct_answer"]
            correct_content = q["options"].get(correct_key, "Không tìm thấy nội dung đáp án.")
            
            # st.markdown(f"**Đáp án đúng:** {correct_key}. {correct_content}", unsafe_allow_html=True)
            pass # Đã hiển thị qua CSS class .option-correct

    # ---------------- Lời giải ----------------
    if show_answer and q["explanation"]:
        # Dịch lời giải
        explanation_text = q["explanation"]
        
        # Nếu đang bật dịch câu hỏi, dịch luôn lời giải
        if st.session_state.active_translation_key == translation_key:
            with st.spinner("Đang dịch lời giải..."):
                translator = get_translator()
                translated_explanation = translate_text(explanation_text, translator)
            
            st.markdown('<div class="explanation-box">', unsafe_allow_html=True)
            st.markdown(f"**Lời giải:** {explanation_text}")
            st.markdown(f"**Lời giải (Dịch):** {translated_explanation}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.markdown('<div class="explanation-box">', unsafe_allow_html=True)
            st.markdown(f"**Lời giải:** {explanation_text}")
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # Đóng question-box

# Hàm để hiển thị tất cả câu hỏi liên tục
def display_all_questions(groups):
    st.header("📚 Tất Cả Câu Hỏi Trong Ngân Hàng")
    
    question_index = 1 # Chỉ số duy nhất cho key
    for group in groups:
        st.markdown(f'<div class="group-title">{group["id"]}. {group["title"]}</div>', unsafe_allow_html=True)
        for q in group["questions"]:
            # Hiển thị đáp án và lời giải luôn trong chế độ "all"
            display_question(q, question_index, mode="all", show_answer=True, user_selection=None)
            question_index += 1
            st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)

# Hàm để hiển thị chế độ luyện tập theo nhóm
def display_group_practice(groups):
    
    # Lấy nhóm hiện tại
    current_group_idx = st.session_state.current_group_idx
    group = groups[current_group_idx]
    
    st.header(f"🧠 Luyện Tập Nhóm {group['id']}: {group['title']}")
    
    questions = group["questions"]
    
    # ---------------- Nút Chuyển Nhóm ----------------
    col1, col2, col3 = st.columns([1, 2, 1])
    
    # Nút Quay lại
    with col1:
        if current_group_idx > 0:
            if st.button("⬅️ Nhóm trước", key="prev_group"):
                st.session_state.current_group_idx -= 1
                st.session_state.submitted = False # Reset trạng thái khi chuyển nhóm
                st.session_state.current_group_selections = {} # Reset lựa chọn
                st.session_state.active_translation_key = None # Reset dịch
                st.rerun()

    # Tên nhóm (giữa)
    with col2:
        st.markdown(f"<p style='text-align: center; font-size: 1.1rem; font-weight: bold;'>{current_group_idx + 1} / {len(groups)}</p>", unsafe_allow_html=True)

    # Nút Tiếp tục
    with col3:
        if current_group_idx < len(groups) - 1:
            if st.button("➡️ Nhóm sau", key="next_group_top"):
                st.session_state.current_group_idx += 1
                st.session_state.submitted = False # Reset trạng thái khi chuyển nhóm
                st.session_state.current_group_selections = {} # Reset lựa chọn
                st.session_state.active_translation_key = None # Reset dịch
                st.rerun()
        elif st.session_state.submitted:
            st.success("🎉 Đã hoàn thành nhóm cuối cùng!")
            
    st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)

    # ---------------- Hiển thị Câu hỏi ----------------
    
    # Khởi tạo lựa chọn cho nhóm hiện tại nếu chưa có
    if "current_group_selections" not in st.session_state:
        st.session_state.current_group_selections = {}

    # Dùng st.form để nhóm các câu hỏi lại và có nút submit duy nhất
    with st.form(key=f"group_form_{group['id']}"):
        
        # Hiển thị từng câu hỏi
        for i, q in enumerate(questions):
            
            # Lấy lựa chọn của người dùng cho câu hỏi này
            user_selection = st.session_state.current_group_selections.get(q["number"])
            
            # Hiển thị câu hỏi (Dùng st.radio để chọn đáp án)
            # Chỉ hiển thị đáp án khi đã submit
            display_question(
                q, 
                index=q["number"], 
                mode="group_practice", 
                show_answer=st.session_state.submitted, 
                user_selection=user_selection
            )
            
            # Thêm radio button (hoặc logic lựa chọn) ở đây
            # Dùng key là số thứ tự câu hỏi trong ngân hàng để duy trì state
            option_keys = sorted(q["options"].keys())
            
            # Bỏ qua nếu không phải câu hỏi trắc nghiệm
            if not q["is_multichoice"] or not option_keys:
                continue

            # Tùy chỉnh hiển thị các lựa chọn bằng st.radio
            # Tạo một list các label tùy chỉnh
            options_labels = [f"**{k}.** {q['options'][k]}" for k in option_keys]
            
            # Tìm index của lựa chọn hiện tại
            current_index = option_keys.index(user_selection) if user_selection in option_keys else None

            # Dùng st.radio để chọn đáp án
            # Đặt radio group trong một cột nhỏ để tránh chiếm hết chiều rộng
            col_radio = st.container()
            with col_radio:
                # Nếu đã submit, ẩn radio đi (vì đáp án đã hiển thị)
                if not st.session_state.submitted:
                    selection = st.radio(
                        "Lựa chọn:",
                        options=option_keys,
                        key=f"selection_group_{group['id']}_q_{q['number']}",
                        index=current_index,
                        format_func=lambda x: f"**{x}.** {q['options'][x]}",
                        label_visibility="collapsed"
                    )
                    
                    # Cập nhật lựa chọn người dùng nếu có thay đổi
                    if selection:
                        st.session_state.current_group_selections[q["number"]] = selection

            st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)

        # ---------------- Nút Submit ----------------
        submitted = st.form_submit_button("Nộp Bài / Xem Kết Quả" if not st.session_state.submitted else "Luyện Tập Lại")
        
    # ---------------- Logic Sau Submit ----------------
    if submitted:
        if not st.session_state.submitted:
            # Lần đầu submit: Chuyển sang chế độ xem kết quả
            st.session_state.submitted = True
            
            # Tính điểm
            score = 0
            total = len(questions)
            for q in questions:
                user_ans = st.session_state.current_group_selections.get(q["number"])
                if user_ans and user_ans == q["correct_answer"]:
                    score += 1
            
            st.session_state.current_group_score = score
            st.session_state.current_group_total = total
            
            st.success(f"Kết Quả Nhóm **{group['id']}**: **{score} / {total}** câu đúng!")
            st.info("Bây giờ bạn có thể xem lại đáp án và lời giải chi tiết cho từng câu.")
            
        else:
            # Lần 2 submit (hoặc click vào nút "Luyện Tập Lại"): Reset và luyện tập lại
            st.session_state.submitted = False
            st.session_state.current_group_selections = {} # Xóa lựa chọn
            st.session_state.active_translation_key = None # Reset dịch
            
        st.rerun() # Rerun để cập nhật giao diện (hiển thị/ẩn đáp án)

# Hàm để hiển thị chế độ làm bài kiểm tra
def display_test_mode(groups, bank_choice):
    st.header("⏱️ Chế Độ Thi Thử")
    
    # Trạng thái thi thử
    if "test_questions" not in st.session_state:
        st.session_state.test_questions = []
    if "test_selections" not in st.session_state:
        st.session_state.test_selections = {}
    if "test_submitted" not in st.session_state:
        st.session_state.test_submitted = False
    if "test_score" not in st.session_state:
        st.session_state.test_score = 0
    if "test_total" not in st.session_state:
        st.session_state.test_total = 0
        
    # Chuẩn bị bộ câu hỏi
    all_questions = [q for group in groups for q in group['questions'] if q['is_multichoice']]
    
    if not all_questions:
        st.warning("Ngân hàng này không có câu hỏi trắc nghiệm để làm bài thi thử.")
        return

    # Nếu chưa bắt đầu thi hoặc chọn ngân hàng mới, thiết lập bài thi
    if not st.session_state.test_questions or st.session_state.current_bank_choice != bank_choice:
        st.session_state.current_bank_choice = bank_choice
        
        # Cấu hình bài thi
        default_num = min(50, len(all_questions))
        num_questions = st.slider("Chọn số lượng câu hỏi cho bài thi:", 
                                  min_value=1, 
                                  max_value=len(all_questions), 
                                  value=default_num,
                                  step=1)
        
        if st.button("Bắt Đầu Bài Thi", key="start_test"):
            # Chọn ngẫu nhiên câu hỏi
            st.session_state.test_questions = random.sample(all_questions, num_questions)
            st.session_state.test_selections = {}
            st.session_state.test_submitted = False
            st.session_state.test_score = 0
            st.session_state.test_total = num_questions
            st.rerun()
        return

    # ---------------- Đang làm bài ----------------
    
    test_questions = st.session_state.test_questions
    test_total = len(test_questions)
    
    if not st.session_state.test_submitted:
        st.info(f"Bạn đang làm bài thi gồm **{test_total}** câu hỏi. Hãy chọn đáp án và nhấn **Nộp Bài** khi hoàn thành.")
        
        with st.form(key="test_form"):
            for i, q in enumerate(test_questions):
                # Dùng số thứ tự trong bài thi làm ID
                question_id = i + 1 
                
                st.markdown('<div class="question-box">', unsafe_allow_html=True)
                st.markdown(f'<div class="question-content"><b>{question_id}.</b> {q["content"]}</div>', unsafe_allow_html=True)

                option_keys = sorted(q["options"].keys())
                
                # Tìm index của lựa chọn hiện tại
                current_selection = st.session_state.test_selections.get(question_id)
                current_index = option_keys.index(current_selection) if current_selection in option_keys else None

                selection = st.radio(
                    "Lựa chọn:",
                    options=option_keys,
                    key=f"test_selection_q_{question_id}",
                    index=current_index,
                    format_func=lambda x: f"**{x}.** {q['options'][x]}",
                    label_visibility="collapsed"
                )
                
                # Cập nhật lựa chọn người dùng
                if selection:
                    st.session_state.test_selections[question_id] = selection

                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
                
            submitted = st.form_submit_button("Nộp Bài Kiểm Tra")
            
            if submitted:
                # Tính điểm và chuyển sang chế độ xem kết quả
                score = 0
                for i, q in enumerate(test_questions):
                    question_id = i + 1
                    user_ans = st.session_state.test_selections.get(question_id)
                    if user_ans and user_ans == q["correct_answer"]:
                        score += 1
                        
                st.session_state.test_score = score
                st.session_state.test_submitted = True
                st.rerun()
                
    # ---------------- Xem Kết Quả ----------------
    else:
        # Hiển thị kết quả tổng quan
        st.success(f"**🎉 Kết Quả Bài Thi:** Bạn đạt được **{st.session_state.test_score} / {st.session_state.test_total}** câu đúng!")
        st.info("Dưới đây là đáp án và lời giải chi tiết:")
        
        for i, q in enumerate(test_questions):
            question_id = i + 1
            user_selection = st.session_state.test_selections.get(question_id)
            
            # Hiển thị câu hỏi với đáp án
            display_question(
                q, 
                index=f"test_q_{question_id}", # Dùng key khác để tránh conflict với mode group
                mode="test", 
                show_answer=True, 
                user_selection=user_selection
            )
            st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
            
        if st.button("Làm Lại Bài Thi Mới", key="reset_test"):
            st.session_state.test_questions = []
            st.session_state.test_selections = {}
            st.session_state.test_submitted = False
            st.session_state.test_score = 0
            st.session_state.test_total = 0
            st.session_state.current_bank_choice = None # Đặt lại để chọn lại số lượng câu hỏi
            st.rerun()

# ====================================================
# 🚀 CHƯƠNG TRÌNH CHÍNH
# ====================================================

def main():
    st.set_page_config(
        page_title="Streamlit Question Bank Practice",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Áp dụng CSS
    set_custom_css()

    st.title("📚 Streamlit Question Bank Practice")
    st.markdown("Ứng dụng luyện tập câu hỏi từ file Word (.docx) của Gemini.")

    # ---------------- Khởi tạo Session State ----------------
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "current_group_idx" not in st.session_state:
        st.session_state.current_group_idx = 0
    if "submitted" not in st.session_state:
        st.session_state.submitted = False # Trạng thái đã nộp bài trong mode group practice
    if "current_group_selections" not in st.session_state:
        st.session_state.current_group_selections = {} # Lựa chọn của người dùng trong nhóm hiện tại
    if "current_mode" not in st.session_state:
        st.session_state.current_mode = "group" # Chế độ: "group", "all", "test"
    if "active_translation_key" not in st.session_state:
        st.session_state.active_translation_key = None # Key của câu hỏi đang được dịch
    if "current_bank_choice" not in st.session_state:
        st.session_state.current_bank_choice = None # Tên file bank đang được chọn

    # ---------------- Sidebar ----------------
    with st.sidebar:
        st.header("Upload Ngân Hàng Câu Hỏi (.docx)")
        uploaded_file = st.file_uploader("Chọn file DOCX", type="docx")
        
        # ---------------- Xử lý file upload ----------------
        if uploaded_file is not None:
            # Nếu file mới được upload (hoặc tên file khác), reset mọi trạng thái
            if st.session_state.current_bank_choice != uploaded_file.name:
                st.session_state.current_bank_choice = uploaded_file.name
                st.session_state.current_group_idx = 0
                st.session_state.submitted = False
                st.session_state.current_group_selections = {}
                st.session_state.current_mode = "group"
                st.session_state.active_translation_key = None
                
                # Reset trạng thái thi thử
                st.session_state.test_questions = []
                st.session_state.test_selections = {}
                st.session_state.test_submitted = False
                
                with st.spinner(f"Đang đọc file '{uploaded_file.name}'..."):
                    try:
                        questions_data = read_docx(uploaded_file)
                        st.session_state.questions = questions_data
                        st.session_state.current_group_idx = 0
                        st.success("Tải lên và xử lý file thành công!")
                        st.rerun() # Rerun để cập nhật nội dung chính
                    except Exception as e:
                        st.error(f"Lỗi khi xử lý file DOCX: {e}")
                        st.session_state.questions = []
                        st.session_state.current_bank_choice = None

            # Nếu đã có file được xử lý
            if st.session_state.questions:
                
                st.header("Chế Độ Luyện Tập")
                
                # Nút chuyển chế độ
                col_m1, col_m2, col_m3 = st.columns(3)
                
                # Luyện tập theo nhóm
                with col_m1:
                    if st.button("Luyện theo Nhóm", key="mode_group", disabled=(st.session_state.current_mode == "group")):
                        st.session_state.current_mode = "group"
                        st.session_state.active_translation_key = None 
                        st.rerun()
                
                # Xem tất cả
                with col_m2:
                    if st.button("Xem Tất Cả", key="mode_all", disabled=(st.session_state.current_mode == "all")):
                        st.session_state.current_mode = "all"
                        st.session_state.active_translation_key = None
                        st.rerun()
                        
                # Thi thử
                with col_m3:
                    if st.button("Thi Thử", key="mode_test", disabled=(st.session_state.current_mode == "test")):
                        st.session_state.current_mode = "test"
                        st.session_state.active_translation_key = None
                        st.rerun()
                        
                st.markdown("---")
                
                # Hiển thị tóm tắt
                total_groups = len(st.session_state.questions)
                total_questions = sum(len(g["questions"]) for g in st.session_state.questions)
                st.metric("Tổng số câu hỏi", total_questions)
                st.metric("Tổng số nhóm", total_groups)
                
                # Trong chế độ luyện tập theo nhóm, cho phép chọn nhóm
                if st.session_state.current_mode == "group":
                    group_titles = [f"Nhóm {g['id']}: {g['title']} ({len(g['questions'])} câu)" for g in st.session_state.questions]
                    selected_group_title = st.selectbox(
                        "Chuyển đến nhóm:",
                        options=group_titles,
                        index=st.session_state.current_group_idx,
                        key="group_select_box"
                    )
                    
                    # Cập nhật index nếu người dùng thay đổi
                    new_idx = group_titles.index(selected_group_title)
                    if new_idx != st.session_state.current_group_idx:
                        st.session_state.current_group_idx = new_idx
                        st.session_state.submitted = False
                        st.session_state.current_group_selections = {}
                        st.session_state.active_translation_key = None
                        st.rerun()

    # ---------------- Nội dung chính ----------------
    questions = st.session_state.questions
    
    if not questions:
        if st.session_state.current_bank_choice is None:
            st.info("Vui lòng tải lên một file DOCX để bắt đầu luyện tập.")
        else:
            st.error("Không thể đọc hoặc không tìm thấy câu hỏi nào trong file đã tải lên. Vui lòng kiểm tra định dạng.")
        return

    # Lựa chọn chế độ hiển thị
    if st.session_state.current_mode == "group":
        groups = questions
        
        if st.session_state.current_group_idx < len(groups):
            display_group_practice(groups)
            
            # Nút chuyển nhóm dưới cùng
            st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
            col_b1, col_b2 = st.columns([1, 1])
            with col_b1:
                if st.session_state.current_group_idx > 0:
                    if st.button("⬅️ Quay lại nhóm trước", key="prev_group_bottom"):
                        st.session_state.current_group_idx -= 1
                        st.session_state.submitted = False
                        st.session_state.current_group_selections = {}
                        st.session_state.active_translation_key = None
                        st.rerun()
            with col_b2:
                if st.session_state.current_group_idx < len(groups) - 1:
                    if st.button("➡️ Tiếp tục nhóm sau", key="next_group"):
                        st.session_state.current_group_idx += 1
                        st.session_state.submitted = False
                        st.session_state.current_group_selections = {}
                        st.session_state.active_translation_key = None # Reset dịch khi chuyển nhóm
                        st.rerun()
                else: st.info("🎉 Đã hoàn thành tất cả các nhóm câu hỏi!")
        else: st.warning("Không có câu hỏi trong nhóm này.")

    elif st.session_state.current_mode == "all":
        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
        display_all_questions(questions)
        
    elif st.session_state.current_mode == "test":
        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
        display_test_mode(questions, st.session_state.current_bank_choice)

if __name__ == "__main__":
    main()
