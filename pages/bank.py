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
    # VD: (__           __) → (____)
    temp_s = re.sub(r'\([\\s._-]{2,}\\)', '(    )', temp_s)  # Ngoặc đơn
    temp_s = re.sub(r'\\[[\\s._-]{2,}\\]', '[    ]', temp_s)  # Ngoặc vuông
    temp_s = re.sub(r'\\{[\\s._-]{2,}\\}', '{    }', temp_s)  # Ngoặc nhọn
    
    # BƯỚC 2: Tạm thay thế các placeholder (chỗ trống) để không bị xóa trong bước 3
    # 1. Chỗ trống (4 spaces trong ngoặc)
    temp_s = re.sub(r'\\([\\s._-]{4})\\)|\\{[\\s._-]{4}\\}|\\[\\s._-]{4}\\]', 
                    lambda m: f"__PLACEHOLDER_{counter}__", temp_s)
    
    # 2. Dấu ba chấm hoặc gạch dưới không có ngoặc 
    # (chỉ giữ lại 4 ký tự liên tiếp để đơn giản hóa)
    temp_s = re.sub(r'[._-]{4,}', 
                    lambda m: f"__PLACEHOLDER_{counter}__", temp_s)

    # BƯỚC 3: Loại bỏ các ký tự đặc biệt không mong muốn (giữ lại tiếng Việt, số, cơ bản)
    # Loại bỏ ký tự đặc biệt, giữ lại: chữ cái (kể cả tiếng Việt), số, khoảng trắng, và các dấu cơ bản .,:;?!()[]{}'"-_/&
    # CŨ: s = re.sub(r'[^\\w\\s\\.,:;?!()\'"\\-]', '', s)
    # LÀM SẠCH VỚI TEMP_S
    cleaned_s = re.sub(r'[^a-zA-Z0-9áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵĐđ\\s\\.,:;?!()\'"\\[\\]\\{\\}\\-\\+\\*/=]', '', temp_s)
    
    # BƯỚC 4: Khôi phục placeholder
    for i in range(counter):
        cleaned_s = cleaned_s.replace(f"__PLACEHOLDER_{i}__", '____')
        
    # Chuẩn hóa khoảng trắng
    cleaned_s = re.sub(r'\\s+', ' ', cleaned_s).strip()
    
    return cleaned_s

def read_and_parse_docx(file_path):
    doc = Document(file_path)
    questions = []
    current_question = None
    group_name = "Chưa phân nhóm"
    
    # Hàm để kiểm tra xem một run có được highlight không (màu khác "none")
    def is_highlighted(run):
        # Kiểm tra màu highlight (WD_COLOR_INDEX)
        # 0: None, 1: Black, 2: Blue, 3: Cyan, 4: Green, 5: Magenta, 6: Red, 7: Yellow
        # 8: White, 9: Dark Blue, 10: Teal, 11: Gray-50, 12: Light Blue, 13: Violet, 14: Dark Red
        # 15: Pink, 16: Yellow-Green, 17: Dark Yellow, 18: Light Gray, 19: Dark Gray, 20: Gold
        # Đáp án thường được highlight màu Vàng (YELLOW)
        return run.highlight_color is not None and run.highlight_color != WD_COLOR_INDEX.NONE

    # Hàm trích xuất văn bản từ paragraph
    def get_paragraph_text(p):
        text = ""
        for run in p.runs:
            run_text = run.text
            # Kiểm tra và thêm ký hiệu đáp án đúng (S)
            if is_highlighted(run):
                run_text += " (S)"
            text += run_text
        return text

    for p in doc.paragraphs:
        # Kiểm tra tiêu đề nhóm:
        # Nếu có style Title/Heading hoặc BOLD, và bắt đầu bằng "Nhóm", "Chủ đề", "Phần"
        if p.style.name.startswith('Heading') or ('Nhóm' in p.text and p.text.istitle() or p.text.isupper()):
             # Nếu không phải là câu hỏi (Q:), thì đây là tên nhóm mới
            if not re.match(r'^[qQ][\\.:]\\s*', p.text.strip()):
                group_name = clean_text(p.text).replace(' (S)', '').strip()
                continue
            
        text = clean_text(get_paragraph_text(p))
        
        # 1. Bắt đầu câu hỏi mới: Bắt đầu bằng Q: hoặc Câu: (Không phân biệt hoa thường)
        q_match = re.match(r'^[qQ][\\.:]\\s*(.*)', text)
        if q_match:
            # Nếu có câu hỏi đang dang dở, lưu lại trước
            if current_question:
                questions.append(current_question)
            
            # Bắt đầu câu hỏi mới
            current_question = {
                'id': len(questions) + 1,
                'group': group_name,
                'question_text': q_match.group(1).replace('(S)', '').strip(),
                'answers': [],
                'correct_answer': None,
                'explanation': None
            }
            continue
            
        # 2. Bắt đầu đáp án
        a_match = re.match(r'^([A-Za-z0-9])\\.[\\s\\t]*(.*)', text)
        if a_match and current_question:
            choice_label = a_match.group(1)
            answer_text = a_match.group(2).strip()
            
            is_correct = False
            # Kiểm tra nếu đáp án có chứa ký hiệu (S) được thêm vào từ highlight
            if answer_text.endswith('(S)'):
                is_correct = True
                answer_text = answer_text[:-3].strip() # Xóa (S)
            
            # Thêm vào danh sách đáp án
            current_question['answers'].append({
                'label': choice_label,
                'text': answer_text
            })
            
            # Cập nhật đáp án đúng
            if is_correct:
                if current_question['correct_answer'] is None:
                    current_question['correct_answer'] = choice_label
                else:
                    # Xử lý trường hợp đa đáp án đúng nếu cần (hiện tại chỉ lấy đáp án đầu tiên được highlight)
                    pass 
            continue

        # 3. Bắt đầu phần giải thích
        if re.match(r'^(Giải thích|GT|Explain|Hint|Gợi ý)[\\.:]?\\s*', text):
            # Nếu là phần Giải thích, thêm vào câu hỏi hiện tại
            if current_question:
                current_question['explanation'] = text.replace('(S)', '').strip()
            continue
            
        # 4. Văn bản khác (thường là phần tiếp theo của câu hỏi, đáp án, hoặc giải thích)
        if current_question:
            if current_question['answers']:
                # Nếu câu trước là đáp án, thì đây là phần nối tiếp của đáp án đó
                last_answer = current_question['answers'][-1]
                if not last_answer['text'].endswith('.'): # Nếu không kết thúc bằng dấu chấm (giả định)
                    last_answer['text'] += " " + text.replace('(S)', '').strip()
            elif current_question['explanation']:
                # Nếu câu trước là giải thích, thì đây là phần nối tiếp của giải thích đó
                current_question['explanation'] += " " + text.replace('(S)', '').strip()
            else:
                # Nếu câu trước là câu hỏi, thì đây là phần nối tiếp của câu hỏi đó
                current_question['question_text'] += " " + text.replace('(S)', '').strip()


    # Lưu lại câu hỏi cuối cùng
    if current_question:
        questions.append(current_question)
        
    # Xử lý: Nếu không có đáp án đúng được highlight, chọn đáp án A làm mặc định
    for q in questions:
        if q['correct_answer'] is None and q['answers']:
            q['correct_answer'] = q['answers'][0]['label']
            
    # Lọc câu hỏi không có đáp án hoặc không có nội dung
    questions = [q for q in questions if q['answers'] and q['question_text']]
    
    return questions

def group_questions(questions):
    groups = {}
    for q in questions:
        group_name = q.get('group', 'Chưa phân nhóm')
        if group_name not in groups:
            groups[group_name] = []
        groups[group_name].append(q)
    return groups

# Hàm mã hóa file ảnh thành base64
def get_base64_encoded_file(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        st.error(f"Lỗi: Không tìm thấy file ảnh {image_path}. Vui lòng kiểm tra lại.")
        return ""

def translate_text(text, target_language='en'):
    # Hạn chế dịch những đoạn quá dài hoặc quá ngắn
    if not text or len(text) < 5 or len(text) > 5000:
        return ""
    
    try:
        # Sử dụng thư viện 'translate'
        translator = Translator(to_lang=target_language, from_lang='vi')
        translation = translator.translate(text)
        return translation
    except Exception as e:
        #st.warning(f"Lỗi dịch: {e}")
        return f"[Lỗi dịch: {e}]"


# ====================================================
# 🎨 GIAO DIỆN HIỂN THỊ
# ====================================================
def display_question(q, mode, q_index=None, submitted=False, is_test_mode=False, user_answer=None, key_prefix="q"):
    q_key = f"{key_prefix}-{q['id']}"
    
    # 1. HIỂN THỊ CÂU HỎI
    question_title = f"<span class='number-one'>Câu {q_index or q['id']}:</span> {q['question_text']}"
    st.markdown(f"<div class='bank-question-text'>{question_title}</div>", unsafe_allow_html=True)

    # 2. KHỐI DỊCH THUẬT (Translate)
    # Tên key duy nhất cho nút toggle của câu hỏi này
    translation_toggle_key = f"translate_toggle_{q_key}"
    
    # Lấy trạng thái dịch từ session state
    is_translated = st.session_state.get('active_translation_key') == q_key
    
    # Nút bật/tắt dịch
    if st.toggle("Bật dịch sang Tiếng Anh", value=is_translated, key=translation_toggle_key):
        # Nếu bật, lưu key câu hỏi này vào session state
        st.session_state.active_translation_key = q_key
    else:
        # Nếu tắt, và đây là câu hỏi đang được dịch, xóa key
        if st.session_state.get('active_translation_key') == q_key:
            st.session_state.active_translation_key = None
            
    # HIỂN THỊ KHỐI DỊCH
    if st.session_state.get('active_translation_key') == q_key:
        with st.spinner("Đang dịch..."):
            # Dịch câu hỏi
            translated_q_text = translate_text(q['question_text'])
            st.warning(f"**Câu hỏi (EN):** {translated_q_text}")
            
            # Dịch các đáp án
            translated_answers = []
            for ans in q['answers']:
                translated_ans_text = translate_text(ans['text'])
                translated_answers.append(f"**{ans['label']}**: {translated_ans_text}")
                
            st.info("**Đáp án (EN):** " + " | ".join(translated_answers))
            
            # Dịch giải thích nếu có
            if q.get('explanation'):
                translated_explanation = translate_text(q['explanation'])
                st.success(f"**Giải thích (EN):** {translated_explanation}")

    # 3. KHỐI ĐÁP ÁN VÀ TRẢ LỜI
    # Xây dựng dictionary đáp án
    options = {ans['label']: ans['text'] for ans in q['answers']}
    
    # Trong chế độ Test, dùng Radio button
    if is_test_mode:
        
        # Nếu đã có câu trả lời từ trước, dùng nó
        default_index = None
        if user_answer in options:
            default_index = list(options.keys()).index(user_answer)
        
        # Lấy nhãn đáp án đã chọn
        selected_label = st.radio(
            "Chọn đáp án:",
            options=list(options.keys()),
            format_func=lambda x: f"{x}. {options[x]}",
            index=default_index, # Chọn đáp án nếu có
            key=f"radio_{q_key}"
        )
        
        # Trả về đáp án người dùng đã chọn
        return selected_label
        
    # Trong chế độ Luyện tập (Group/All), chỉ hiển thị đáp án và kết quả
    else:
        # Tạo key duy nhất cho radio button
        radio_key = f"radio_{q_key}"
        
        # Lấy nhãn đáp án đã chọn từ radio
        selected_label = st.radio(
            "Chọn đáp án:",
            options=list(options.keys()),
            format_func=lambda x: f"{x}. {options[x]}",
            key=radio_key
        )
        
        # 4. HIỂN THỊ KẾT QUẢ/GIẢI THÍCH
        if submitted:
            is_correct = selected_label == q['correct_answer']
            
            # Ẩn Radio và chỉ hiển thị kết quả
            if is_correct:
                st.success(f"✔️ **Đúng rồi!** Đáp án **{selected_label}** là chính xác.")
            else:
                st.error(f"❌ **Sai rồi.** Đáp án của bạn là **{selected_label}**. Đáp án đúng là **{q['correct_answer']}**.")
            
            # Hiển thị giải thích
            if q.get('explanation'):
                st.info(f"💡 **Giải thích:** {q['explanation']}")
            
            # 5. Đánh dấu đáp án đúng
            correct_index = list(options.keys()).index(q['correct_answer'])
            
            # Tạo lại radio với index của đáp án đúng, và disable
            st.radio(
                "Đáp án:",
                options=list(options.keys()),
                format_func=lambda x: f"{x}. {options[x]}",
                index=correct_index,
                disabled=True, # Tắt để chỉ hiển thị
                key=f"radio_result_{q_key}",
                label_visibility="collapsed"
            )
            
        return selected_label # Trả về đáp án đã chọn (cho mode Group/All)

def display_all_questions(questions):
    st.subheader("📋 Tất cả Câu hỏi", divider="blue")
    
    # 1. Nút Submit
    submit_col, empty_col = st.columns([1, 4])
    with submit_col:
        # Tạo nút "Xem đáp án"
        if st.button("👁️ Xem đáp án", key="submit_all_qs"):
            st.session_state.submitted = True
        
    st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
    
    # 2. Hiển thị từng câu hỏi
    for i, q in enumerate(questions):
        q_index = i + 1
        display_question(q, mode="all", q_index=q_index, 
                         submitted=st.session_state.submitted, 
                         key_prefix="all")
        
        # Phân cách câu hỏi
        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)

def display_test_mode(questions, bank_choice):
    st.subheader("⏱️ Chế độ Làm bài Test", divider="red")
    
    # Khởi tạo kết quả bài làm nếu chưa có
    if 'test_answers' not in st.session_state:
        st.session_state.test_answers = {}
    
    # 1. Hiển thị từng câu hỏi và thu thập đáp án
    user_answers = {}
    st.markdown(f"**Tổng số câu hỏi:** {len(questions)}")
    st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)

    for i, q in enumerate(questions):
        q_index = i + 1
        
        # Lấy câu trả lời đã lưu nếu có
        current_answer = st.session_state.test_answers.get(str(q['id']))
        
        # Hiển thị và lấy đáp án người dùng chọn
        selected_label = display_question(
            q, 
            mode="test", 
            q_index=q_index,
            is_test_mode=True, 
            user_answer=current_answer,
            key_prefix="test"
        )
        
        # Lưu đáp án vào session state ngay lập tức
        st.session_state.test_answers[str(q['id'])] = selected_label
        user_answers[q['id']] = selected_label
        
        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
        
    # 2. Nút Submit và chấm điểm
    submit_col, empty_col = st.columns([1, 4])
    with submit_col:
        if st.button("✅ Nộp bài & Xem kết quả", key="submit_test"):
            st.session_state.test_submitted = True
            
    if st.session_state.test_submitted:
        
        # 3. Chấm điểm
        score = 0
        total_questions = len(questions)
        
        for q in questions:
            user_ans = st.session_state.test_answers.get(str(q['id']))
            if user_ans == q['correct_answer']:
                score += 1
        
        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
        
        # 4. HIỂN THỊ KẾT QUẢ CHUNG
        st.markdown("<div class='result-title'><h3>🎉 KẾT QUẢ BÀI TEST CỦA BẠN</h3></div>", unsafe_allow_html=True)
        
        st.info(f"**Tên ngân hàng:** {bank_choice}")
        st.info(f"**Tổng số câu hỏi:** {total_questions}")
        
        # Dùng st.metric để làm nổi bật điểm số
        st.metric(label="Điểm số:", 
                  value=f"{score}/{total_questions}", 
                  delta=f"{score/total_questions:.1%}", 
                  delta_color="normal")
        
        # 5. Hiển thị đáp án chi tiết
        st.markdown("#### Xem lại Đáp án Chi tiết:", unsafe_allow_html=True)
        
        for i, q in enumerate(questions):
            q_index = i + 1
            user_ans = st.session_state.test_answers.get(str(q['id']))
            is_correct = user_ans == q['correct_answer']
            
            # Hiển thị câu hỏi
            question_title = f"<span class='number-one'>Câu {q_index}:</span> {q['question_text']}"
            st.markdown(f"<div class='bank-question-text'>{question_title}</div>", unsafe_allow_html=True)
            
            # Hiển thị trạng thái
            if is_correct:
                st.success(f"✔️ **Đúng.** Đáp án bạn chọn: **{user_ans}**")
            else:
                st.error(f"❌ **Sai.** Đáp án bạn chọn: **{user_ans}**. Đáp án đúng: **{q['correct_answer']}**")
            
            # Hiển thị giải thích
            if q.get('explanation'):
                st.markdown(f"**Giải thích:** {q['explanation']}")
            
            st.markdown("---") # Phân cách

# ====================================================
# 🚀 HÀM CHÍNH (MAIN FUNCTION)
# ====================================================
def main():
    
    # Khởi tạo Session State
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'groups' not in st.session_state:
        st.session_state.groups = {}
    if 'current_group_idx' not in st.session_state:
        st.session_state.current_group_idx = 0
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False # Cho chế độ Group/All
    if 'test_submitted' not in st.session_state:
        st.session_state.test_submitted = False # Cho chế độ Test
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = "group" # group, all, test
    if 'test_answers' not in st.session_state:
        st.session_state.test_answers = {}
    if 'active_translation_key' not in st.session_state:
        st.session_state.active_translation_key = None # Dùng để quản lý khối dịch thuật


    # ====================================================
    # 🖥️ THIẾT LẬP GIAO DIỆN VÀ CSS
    # ====================================================
    st.set_page_config(page_title="Ngân hàng trắc nghiệm", layout="wide")

    # Tên file ảnh giả định (cần đặt trong cùng thư mục)
    PC_IMAGE_FILE = "bank_PC.jpg"
    MOBILE_IMAGE_FILE = "bank_mobile.jpg"
    
    # Kiểm tra và tạo file giả định nếu không tồn tại (để tránh lỗi khi chạy lần đầu)
    if not os.path.exists(PC_IMAGE_FILE):
        # Tạo file ảnh đen giả định (20x20 pixel)
        import numpy as np
        from PIL import Image
        img = Image.fromarray(np.zeros((20, 20, 3), dtype=np.uint8))
        img.save(PC_IMAGE_FILE)
    if not os.path.exists(MOBILE_IMAGE_FILE):
        import numpy as np
        from PIL import Image
        img = Image.fromarray(np.zeros((20, 20, 3), dtype=np.uint8))
        img.save(MOBILE_IMAGE_FILE)
        
    img_pc_base64 = get_base64_encoded_file(PC_IMAGE_FILE)
    img_mobile_base64 = get_base64_encoded_file(MOBILE_IMAGE_FILE)

    # === CSS (ĐÃ CHỈNH SỬA) ===
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

    /* ------------------------------------ */
    /* SCROLLBAR TÙY CHỈNH (YÊU CẦU 2)        */
    /* ------------------------------------ */

    /* Áp dụng cho khối cuộn chính (toàn trang) */
    .stApp, html, body {{
        scrollbar-width: thin; /* Firefox */
        scrollbar-color: #764ba2 #0a0a0a; /* Thumb color / Track color - Firefox */
    }}

    /* Các thuộc tính cho Webkit (Chrome, Safari, Edge) */
    .stApp::-webkit-scrollbar, 
    html::-webkit-scrollbar, 
    body::-webkit-scrollbar {{
        width: 15px !important; /* Độ rộng của thanh cuộn */
        height: 15px !important; /* Chiều cao của thanh cuộn ngang */
    }}

    /* TRACK - Nền của thanh cuộn */
    .stApp::-webkit-scrollbar-track, 
    html::-webkit-scrollbar-track, 
    body::-webkit-scrollbar-track {{
        background: #0a0a0a !important; /* Nền tối */
        border-radius: 10px !important;
    }}

    /* THUMB - Phần cuộn được kéo */
    .stApp::-webkit-scrollbar-thumb, 
    html::-webkit-scrollbar-thumb, 
    body::-webkit-scrollbar-thumb {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; /* Gradient màu hiện đại */
        border-radius: 10px !important;
        border: 3px solid #0a0a0a !important; /* Đường viền để tách khỏi track */
        box-shadow: 0 0 10px rgba(102, 126, 234, 0.5); /* Tạo hiệu ứng bóng */
        transition: all 0.3s ease;
    }}

    /* THUMB: Hover State */
    .stApp::-webkit-scrollbar-thumb:hover, 
    html::-webkit-scrollbar-thumb:hover, 
    body::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
    }}

    /* CORNER (góc giao nhau giữa thanh dọc và ngang) */
    .stApp::-webkit-scrollbar-corner, 
    html::-webkit-scrollbar-corner, 
    body::-webkit-scrollbar-corner {{
        background: #0a0a0a !important;
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
        color: #FFFFFF !important;
        font-weight: 900 !important;
        font-size: 22px !important; 
        font-family: 'Oswald', sans-serif !important;
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
    .stToggle label p {{
        font-size: 14px !important;
        font-weight: 700 !important;
        padding: 0;
        margin: 0;
        line-height: 1 !important;
    }}
    .stToggle > label > div[data-testid="stMarkdownContainer"] {{
        margin-top: 10px !important; 
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
        
        /* Nút trên mobile (YÊU CẦU 1: CĂN GIỮA) */
        .stButton>button {{
            font-size: 1em !important;
            padding: 10px 18px !important;
            width: 80% !important; /* ĐIỀU CHỈNH: Giảm width để căn giữa chuẩn hơn */
            margin: 10px auto !important; /* ĐIỀU CHỈNH: Thêm margin auto để căn giữa */
            display: block !important; /* ĐIỀU CHỈNH: Cần block để margin auto hoạt động */
        }}
        
        /* ĐIỀU CHỈNH: Căn giữa nội dung cột (nút) trên mobile */
        /* Áp dụng cho cột bao quanh nút */
        div[data-testid^="stColumn"] {{
            text-align: center !important; 
        }}
    }}
    </style>
    """

    st.markdown(css_style, unsafe_allow_html=True)
    
    # ----------------------------------------------------
    # 📤 UPLOAD FILE VÀ XỬ LÝ
    # ----------------------------------------------------
    if not st.session_state.questions:
        st.markdown("<div id='main-title-container'><h1>BANK TRẮC NGHIỆM ONLINE</h1></div>", unsafe_allow_html=True)
        st.markdown("<div id='sub-static-title'><h2>Vui lòng upload file Ngân hàng câu hỏi (.docx)</h2></div>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Chọn file .docx", type="docx")
        
        if uploaded_file is not None:
            # Lưu file vào session state
            st.session_state.uploaded_file = uploaded_file.name
            
            # Xử lý file
            with st.spinner(f"Đang đọc và phân tích file **{uploaded_file.name}**..."):
                try:
                    # Lưu file tạm thời
                    temp_file_path = f"temp_{uploaded_file.name}"
                    with open(temp_file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                        
                    # Phân tích
                    questions = read_and_parse_docx(temp_file_path)
                    st.session_state.questions = questions
                    st.session_state.groups = group_questions(questions)
                    st.session_state.current_group_idx = 0 # Reset về nhóm đầu tiên
                    st.session_state.submitted = False
                    st.session_state.test_submitted = False
                    st.session_state.test_answers = {}
                    st.session_state.current_mode = "group"
                    
                    # Xóa file tạm
                    os.remove(temp_file_path)
                    
                    st.success(f"✅ Đã tải thành công **{len(questions)}** câu hỏi, được chia thành **{len(st.session_state.groups)}** nhóm.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi khi xử lý file: {e}")
                    st.session_state.questions = []
                    st.session_state.uploaded_file = None
                    
    # ----------------------------------------------------
    # 💻 HIỂN THỊ NỘI DUNG CHÍNH
    # ----------------------------------------------------
    if st.session_state.questions:
        questions = st.session_state.questions
        groups = st.session_state.groups
        group_names = list(groups.keys())
        bank_choice = st.session_state.uploaded_file
        
        # Tiêu đề
        st.markdown("<div id='main-title-container'><h1>BANK TRẮC NGHIỆM ONLINE</h1></div>", unsafe_allow_html=True)
        st.markdown(f"<div id='sub-static-title'><h2>📂 Ngân hàng: {bank_choice}</h2></div>", unsafe_allow_html=True)

        # Thanh chuyển đổi chế độ
        mode_cols = st.columns(3)
        with mode_cols[0]:
            if st.button("📚 Luyện tập theo nhóm", disabled=(st.session_state.current_mode == "group")):
                st.session_state.current_mode = "group"
                st.session_state.submitted = False
                st.session_state.active_translation_key = None
                st.rerun()
        with mode_cols[1]:
            if st.button("📋 Xem tất cả", disabled=(st.session_state.current_mode == "all")):
                st.session_state.current_mode = "all"
                st.session_state.submitted = False
                st.session_state.active_translation_key = None
                st.rerun()
        with mode_cols[2]:
            if st.button("📝 Làm bài TEST", disabled=(st.session_state.current_mode == "test")):
                st.session_state.current_mode = "test"
                st.session_state.submitted = False
                st.session_state.test_submitted = False
                st.session_state.test_answers = {} # Reset câu trả lời
                st.session_state.active_translation_key = None
                st.rerun()

        # ----------------------------------------------------
        # HIỂN THỊ THEO CHẾ ĐỘ
        # ----------------------------------------------------
        if st.session_state.current_mode == "group":
            
            # Chọn nhóm
            st.subheader("📚 Luyện tập theo nhóm", divider="blue")
            
            # Dùng selectbox để chọn nhóm
            st.session_state.current_group_idx = st.selectbox(
                "Chọn nhóm câu hỏi:",
                options=range(len(group_names)),
                format_func=lambda i: f"Nhóm {i+1}: {group_names[i]} ({len(groups[group_names[i]])} câu)",
                index=st.session_state.current_group_idx,
                key="group_selectbox"
            )
            
            current_group_name = group_names[st.session_state.current_group_idx]
            current_questions = groups[current_group_name]
            
            st.info(f"Đang luyện tập nhóm: **{current_group_name}** ({len(current_questions)} câu)")
            
            if current_questions:
                
                # 1. Nút Submit
                submit_col, empty_col = st.columns([1, 4])
                with submit_col:
                    if st.button("👁️ Xem đáp án", key="submit_group_qs"):
                        st.session_state.submitted = True
                    
                st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)

                # 2. Hiển thị câu hỏi trong nhóm
                for i, q in enumerate(current_questions):
                    q_index = i + 1
                    display_question(q, mode="group", q_index=q_index, 
                                     submitted=st.session_state.submitted, 
                                     key_prefix=f"group_{st.session_state.current_group_idx}")
                    
                    st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
                    
                # 3. Nút chuyển nhóm
                col_prev, col_next = st.columns(2)
                with col_prev:
                    if st.session_state.current_group_idx > 0:
                        if st.button("⬅️ Quay lại nhóm trước", key="prev_group"):
                            st.session_state.current_group_idx -= 1
                            st.session_state.submitted = False
                            st.session_state.active_translation_key = None
                            st.rerun()
                with col_next:
                    if st.session_state.current_group_idx < len(groups) - 1:
                        if st.button("➡️ Tiếp tục nhóm sau", key="next_group"):
                            st.session_state.current_group_idx += 1
                            st.session_state.submitted = False
                            st.session_state.active_translation_key = None
                            st.rerun()
                    else: st.info("🎉 Đã hoàn thành tất cả các nhóm câu hỏi!")
            else: st.warning("Không có câu hỏi trong nhóm này.")
        
        elif st.session_state.current_mode == "all":
            st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
            display_all_questions(questions)
            
        elif st.session_state.current_mode == "test":
            st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
            display_test_mode(questions, bank_choice)
        
if __name__ == "__main__":
    main()
