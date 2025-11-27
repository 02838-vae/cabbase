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
# THAY THẾ googletrans bằng translate
from translate import Translator # <-- THAY THẾ THƯ VIỆN

# ====================================================
# ⚙️ HÀM HỖ TRỢ VÀ FILE I/O
# ====================================================
def clean_text(s: str) -> str:
    """
    Chuẩn hóa chuỗi văn bản bằng cách loại bỏ các ký tự đặc biệt,
    giữ lại các pattern điền chỗ trống, và loại bỏ khoảng trắng dư thừa.
    """
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
    temp_s = re.sub(r'\((\s|[_.-]){2,}\)', '(    )', temp_s)  
    
    # BƯỚC 2: Tạm thời thay thế các pattern điền chỗ trống để tránh bị clean:
    # 1. Gạch dưới hoặc dấu chấm liên tục (2-10 lần, có thể có space)
    fill_in_patterns = re.findall(r'([._-]\s*){2,10}', temp_s)
    for p in set(fill_in_patterns):
        if p.strip() != '':
            key = f"__PLACEHOLDER_{counter}__"
            placeholders[key] = p
            temp_s = temp_s.replace(p, key)
            counter += 1

    # 2. Ngoặc chuẩn hóa (____)
    temp_s = re.sub(r'\(\s{4}\)', '__PLACEHOLDER_PAREN__', temp_s)
    
    # BƯỚC 3: Clean văn bản chính
    # Loại bỏ các ký tự không phải chữ, số, hoặc dấu câu cơ bản
    # Giữ lại: Chữ cái (a-z, A-Z), số (0-9), space, dấu câu (.,;?!:'"-)
    cleaned_s = re.sub(r'[^\w\s.,;?!:\'"\-\(\)\[\]/]', '', temp_s, flags=re.UNICODE).strip()
    
    # Chuẩn hóa khoảng trắng (nhiều space thành 1)
    cleaned_s = re.sub(r'\s+', ' ', cleaned_s).strip()
    
    # BƯỚC 4: Khôi phục lại các pattern điền chỗ trống
    cleaned_s = cleaned_s.replace('__PLACEHOLDER_PAREN__', '(    )')
    for key, val in placeholders.items():
        cleaned_s = cleaned_s.replace(key, val)

    return cleaned_s.strip()

def translate_text(text: str) -> str:
    """Sử dụng thư viện 'translate' để dịch văn bản sang tiếng Việt."""
    try:
        # Sử dụng thư viện 'translate', mặc định dùng Glosbe
        # Đảm bảo thư viện đã được cài: pip install translate
        translator = Translator(to_lang="vi", from_lang="en")
        translation = translator.translate(text)
        return translation
    except Exception as e:
        st.error(f"Lỗi khi dịch: {e}")
        return "Không thể dịch văn bản lúc này."

def load_questions_from_docx(uploaded_file):
    """
    Đọc file DOCX, trích xuất câu hỏi và đáp án dựa trên định dạng 
    (Câu hỏi ở dạng bình thường, Đáp án đúng được highlight màu vàng).
    """
    questions = []
    try:
        doc = Document(uploaded_file)
        current_question = None
        q_counter = 0

        for para in doc.paragraphs:
            text = para.text.strip()
            
            # Kiểm tra xem có phải là câu hỏi mới không (bắt đầu bằng số và dấu chấm)
            # Dùng regex để tìm: Bắt đầu bằng 1. hoặc 1)
            is_new_question = re.match(r'^\s*(\d+)[.)]\s*.*', text, re.IGNORECASE)

            if is_new_question:
                # Nếu đang có câu hỏi dở dang, lưu lại
                if current_question:
                    questions.append(current_question)

                # Bắt đầu câu hỏi mới
                q_counter += 1
                current_question = {
                    "index": q_counter,
                    "question": clean_text(text),
                    "options": [],
                    "correct_answer": None
                }
            
            elif current_question:
                # Nếu không phải câu hỏi mới, kiểm tra xem có phải đáp án không
                # Đáp án thường bắt đầu bằng chữ cái (A., B), số La Mã (I., II.) hoặc dấu gạch ngang (-)
                is_option_match = re.match(r'^\s*([A-Za-z]\.|[A-Za-z]\)|I\.|II\.|-)\s*.*', text)

                if is_option_match or len(para.runs) > 0:
                    
                    option_text = ""
                    is_correct = False

                    # Duyệt qua các run (phần text có cùng định dạng)
                    for run in para.runs:
                        option_text += run.text

                        # Kiểm tra xem run có được highlight màu vàng không (đáp án đúng)
                        if run.highlight_color == WD_COLOR_INDEX.YELLOW:
                            is_correct = True
                            
                    # Nếu có text và có vẻ là một option (có ký tự đầu hoặc được highlight)
                    if option_text.strip():
                        cleaned_option = clean_text(option_text)
                        
                        # Chuẩn hóa đáp án: Loại bỏ ký tự A., B., C., D.
                        cleaned_option = re.sub(r'^\s*([A-Za-z]\.|[A-Za-z]\)|I\.|II\.|-)\s*', '', cleaned_option).strip()
                        
                        if cleaned_option:
                            current_question["options"].append({
                                "text": cleaned_option,
                                "is_correct": is_correct
                            })
                            if is_correct:
                                current_question["correct_answer"] = cleaned_option

        # Lưu câu hỏi cuối cùng nếu có
        if current_question:
            questions.append(current_question)

    except Exception as e:
        st.error(f"Lỗi khi đọc file DOCX: {e}")
        return []

    # Loại bỏ các câu hỏi không có đáp án đúng
    valid_questions = [q for q in questions if q["correct_answer"] and q["options"]]
    return valid_questions

def get_download_link(data, filename, text):
    """Tạo link download cho file"""
    b64 = base64.b64encode(data.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{text}</a>'
    return href

# ====================================================
# 💾 STATE MANAGEMENT
# ====================================================
def init_session_state():
    """Khởi tạo các biến trong session state."""
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = "group" # group | all | test
    if 'current_group_idx' not in st.session_state:
        st.session_state.current_group_idx = 0
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {} # {q_index: selected_answer_text}
    if 'active_translation_key' not in st.session_state:
        st.session_state.active_translation_key = None # Key của câu hỏi đang được dịch
    if 'test_mode_questions' not in st.session_state:
        st.session_state.test_mode_questions = []

def on_translate_toggle(translation_key):
    """Callback function khi nút Dịch được bật/tắt."""
    if st.session_state[f"toggle_{translation_key}"]:
        # Bật: Lưu key mới
        st.session_state.active_translation_key = translation_key
    else:
        # Tắt: Xóa key nếu nó đang là key hoạt động
        if st.session_state.active_translation_key == translation_key:
            st.session_state.active_translation_key = None

def submit_answers():
    """Xử lý khi người dùng nhấn nút 'Nộp bài'."""
    st.session_state.submitted = True

# ====================================================
# 🖥️ HIỂN THỊ CÂU HỎI
# ====================================================

def display_question(q, i, submitted=False, is_test=False):
    """Hiển thị một câu hỏi và các đáp án."""
    
    # Khóa dịch cho câu hỏi này
    translation_key = f"q_{q['index']}"
    is_active = st.session_state.active_translation_key == translation_key
    
    # Hiển thị câu hỏi (Dùng CSS đã cập nhật: Đen, Đậm)
    st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True)
    
    # Nút Dịch (Toggle) nằm ngay dưới câu hỏi, căn lề trái (Yêu cầu 4)
    st.toggle(
        "Dịch", 
        value=is_active, 
        key=f"toggle_{translation_key}",
        on_change=on_translate_toggle,
        args=(translation_key,)
    )

    # Hiển thị Bản dịch (Yêu cầu 3: Màu chữ Vàng kim trong st.info nhờ CSS)
    if is_active:
        translation = translate_text(q["question"])
        st.info(f'**Bản dịch (Vietnamese):**\n\n{translation}')

    # Hiển thị các tùy chọn đáp án
    options_key_prefix = f"q_{q['index']}"
    
    # Trộn ngẫu nhiên các đáp án để luyện tập hiệu quả hơn
    options = q['options'][:] 
    
    if not submitted:
        # Nếu chưa nộp bài, lưu lựa chọn của người dùng vào session state
        default_index = -1
        
        # Tạo radio button
        selected_option_text = st.radio(
            "Chọn đáp án:",
            options=[opt['text'] for opt in options],
            key=options_key_prefix,
            index=default_index,
            label_visibility="collapsed"
        )
        
        # Lưu lựa chọn vào user_answers
        if selected_option_text is not None:
            st.session_state.user_answers[q['index']] = selected_option_text

    else:
        # Đã nộp bài: Hiển thị đáp án và kết quả
        user_selected = st.session_state.user_answers.get(q['index'])
        
        for opt in options:
            is_user_selected = (user_selected == opt['text'])
            is_correct_option = (opt['text'] == q['correct_answer'])
            
            # Thiết lập màu sắc (background, chữ)
            color = "#FFFFFF" # Mặc định nền trắng
            text_color = "#000000" # Mặc định chữ đen
            prefix = "•"

            if is_correct_option:
                color = "#D4EDDA" # Xanh nhạt (Nền đúng)
                text_color = "#155724" # Xanh đậm (Chữ đúng)
                prefix = "✅"
            elif is_user_selected:
                color = "#F8D7DA" # Đỏ nhạt (Nền sai)
                text_color = "#721C24" # Đỏ đậm (Chữ sai)
                prefix = "❌"

            # Hiển thị đáp án (Dùng CSS đã cập nhật: Đậm, Bỏ hiệu ứng)
            st.markdown(
                f'<div class="bank-answer-text" style="background-color: {color}; color: {text_color};">'
                f'{prefix} {opt["text"]}</div>',
                unsafe_allow_html=True
            )
    
    st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)


def display_all_questions(questions):
    """Hiển thị tất cả câu hỏi trong ngân hàng."""
    st.title("📚 Toàn bộ Ngân hàng Câu hỏi")
    st.info(f"Tổng cộng: {len(questions)} câu hỏi.")
    st.session_state.submitted = True # Luôn hiển thị đáp án khi xem toàn bộ
    
    for i, q in enumerate(questions):
        display_question(q, i + 1, submitted=True)


def display_test_mode(questions):
    """Hiển thị chế độ làm bài kiểm tra 10 câu ngẫu nhiên."""
    st.title("📝 Bài Kiểm tra Nhanh (10 Câu Ngẫu nhiên)")
    
    # Lấy danh sách 10 câu ngẫu nhiên
    if not st.session_state.test_mode_questions or st.session_state.submitted:
        # Chỉ trộn lần đầu hoặc sau khi nộp bài
        st.session_state.test_mode_questions = random.sample(questions, min(10, len(questions)))
        st.session_state.submitted = False
        st.session_state.user_answers = {}
    
    if len(st.session_state.test_mode_questions) == 0:
        st.warning("Không đủ câu hỏi để tạo bài kiểm tra.")
        return

    st.info(f"Có {len(st.session_state.test_mode_questions)} câu hỏi.")
    
    for i, q in enumerate(st.session_state.test_mode_questions):
        display_question(q, i + 1, submitted=st.session_state.submitted, is_test=True)

    if not st.session_state.submitted:
        if st.button("Nộp bài & Xem kết quả", key="submit_test_mode", on_click=submit_answers):
            st.rerun()
    else:
        # Tính điểm
        correct_count = 0
        for q in st.session_state.test_mode_questions:
            user_selected = st.session_state.user_answers.get(q['index'])
            if user_selected == q['correct_answer']:
                correct_count += 1
        
        st.success(f"**Kết quả của bạn:** {correct_count}/{len(st.session_state.test_mode_questions)} câu đúng! 🎉")
        
        if st.button("Làm bài kiểm tra mới", key="new_test"):
            st.session_state.submitted = False
            st.session_state.test_mode_questions = [] # Buộc phải trộn câu hỏi mới
            st.rerun()

def Luyện_tập_theo_nhóm(questions):
    """Hiển thị chế độ luyện tập theo nhóm."""
    st.title("📚 Luyện tập theo Nhóm")

    total = len(questions)
    
    # [CẬP NHẬT THEO YÊU CẦU 1] Tăng lên 30 câu/nhóm
    group_size = 30 
    
    if total > 0:
        groups = [f"Câu {i*group_size+1}-{min((i+1)*group_size, total)}" for i in range(math.ceil(total/group_size))]
        
        # Chọn nhóm
        group_idx = st.session_state.current_group_idx
        
        st.session_state.current_group_idx = st.selectbox(
            "Chọn nhóm câu hỏi:",
            options=range(len(groups)),
            format_func=lambda i: groups[i],
            index=group_idx
        )
        
        # Nếu thay đổi nhóm, reset submitted state
        if group_idx != st.session_state.current_group_idx:
            st.session_state.submitted = False
            st.session_state.user_answers = {}
            st.session_state.active_translation_key = None
            st.rerun()

        # Lấy câu hỏi cho nhóm hiện tại
        start_index = st.session_state.current_group_idx * group_size
        end_index = min((st.session_state.current_group_idx + 1) * group_size, total)
        current_group_questions = questions[start_index:end_index]
        
        if current_group_questions:
            st.info(f"Đang hiển thị nhóm: {groups[st.session_state.current_group_idx]} (Số lượng: {len(current_group_questions)} câu)")
            
            # Hiển thị câu hỏi
            for i, q in enumerate(current_group_questions):
                # i + start_index + 1 là số thứ tự câu hỏi trong toàn bộ ngân hàng
                display_question(q, i + start_index + 1, submitted=st.session_state.submitted)

            # Nút Nộp bài / Xem kết quả
            if not st.session_state.submitted:
                if st.button("Nộp bài & Xem kết quả", key="submit_group", on_click=submit_answers):
                    st.rerun()
            else:
                st.success("Đã nộp bài. Đáp án đúng được tô màu xanh.")
                
                col_prev, col_next = st.columns([1, 1])

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
                    elif st.session_state.current_group_idx == len(groups) - 1:
                        st.info("🎉 Đã hoàn thành tất cả các nhóm câu hỏi!")
        else: 
            st.warning("Không có câu hỏi trong nhóm này.")
    else: 
        st.warning("Không có câu hỏi nào trong ngân hàng này.")

# ====================================================
# 🚀 MAIN APP LOGIC
# ====================================================

def main():
    """Hàm chính chạy ứng dụng Streamlit."""
    
    st.set_page_config(layout="wide", page_title="Bank Câu hỏi Trắc nghiệm")
    
    # [CẬP NHẬT THEO YÊU CẦU 2 & 3] CSS
    css_code = """
    <style>
        /* CSS để ẩn Streamlit default menu/footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Import font */
        @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@200..700&display=swap');
        
        /* Question Separator */
        .question-separator {
            border-top: 2px solid #EEEEEE;
            margin: 20px 0;
        }

        /* TEXT CÂU HỎI - ĐÃ CẬP NHẬT THEO YÊU CẦU: Đen, Đậm hơn, Bỏ hiệu ứng, Nền trắng */
        .bank-question-text {
            font-family: 'Oswald', sans-serif !important;
            font-size: 22px !important;
            font-weight: 900 !important; /* CẬP NHẬT: Đậm hơn */
            color: #000000 !important; /* CẬP NHẬT: Màu đen */
            line-height: 1.5;
            text-shadow: none !important; /* CẬP NHẬT: Không hiệu ứng */
            padding: 8px 15px;
            background-color: #FFFFFF !important; /* THÊM: Background trắng */
            border-radius: 8px; 
            border: 1px solid #DDDDDD;
        }
        
        /* TEXT ĐÁP ÁN - ĐÃ CẬP NHẬT THEO YÊU CẦU: Đậm hơn, Bỏ hiệu ứng */
        .bank-answer-text {
            font-family: 'Oswald', sans-serif !important;
            font-size: 22px !important;
            font-weight: 900 !important; /* CẬP NHẬT: Đậm hơn */
            line-height: 1.5;
            padding: 4px 25px;
            text-shadow: none !important; /* CẬP NHẬT: Không hiệu ứng */
            margin: 4px 0;
            transition: all 0.3s;
            display: block; 
            border-radius: 4px;
        }
        
        /* Màu chữ trong khung dịch tiếng Việt (st.info/stAlert) */
        div[data-testid*="stAlert"] div[data-testid="stMarkdownContainer"] * {
            color: #FFD700 !important; /* Màu vàng kim để nhìn rõ hơn */
        }
    </style>
    """
    st.markdown(css_code, unsafe_allow_html=True)
    
    init_session_state()

    st.header("📝 Ứng dụng Luyện tập Trắc nghiệm từ File DOCX")
    st.markdown("---")

    # Sidebar: Upload và chọn chế độ
    with st.sidebar:
        st.header("Tải File & Chế độ")
        uploaded_file = st.file_uploader(
            "Tải file ngân hàng câu hỏi (.docx)", 
            type=["docx"], 
            key="file_uploader"
        )

        if uploaded_file != st.session_state.uploaded_file:
            # File mới được upload: Load lại dữ liệu và reset trạng thái
            st.session_state.uploaded_file = uploaded_file
            if uploaded_file is not None:
                st.session_state.questions = load_questions_from_docx(uploaded_file)
            else:
                st.session_state.questions = []
            
            # Reset tất cả trạng thái khi file thay đổi
            st.session_state.current_mode = "group"
            st.session_state.current_group_idx = 0
            st.session_state.submitted = False
            st.session_state.user_answers = {}
            st.session_state.active_translation_key = None
            st.session_state.test_mode_questions = []
            st.rerun() # Buộc rerun để cập nhật dữ liệu

        questions = st.session_state.questions
        
        if questions:
            st.success(f"Đã load thành công {len(questions)} câu hỏi.")
            
            st.subheader("Chọn Chế độ Luyện tập:")
            if st.button("📚 Luyện tập theo Nhóm (30 câu/nhóm)", key="mode_group"):
                st.session_state.current_mode = "group"
                st.session_state.submitted = False
                st.session_state.active_translation_key = None
                st.rerun()
            
            if st.button("📝 Bài Kiểm tra Nhanh (10 câu ngẫu nhiên)", key="mode_test"):
                st.session_state.current_mode = "test"
                st.session_state.submitted = False
                st.session_state.active_translation_key = None
                st.rerun()
                
            if st.button("👁️ Xem Toàn bộ Ngân hàng", key="mode_all"):
                st.session_state.current_mode = "all"
                st.session_state.submitted = True # Luôn hiển thị đáp án
                st.session_state.active_translation_key = None
                st.rerun()

        else:
            if st.session_state.uploaded_file is not None:
                st.error("Không tìm thấy câu hỏi hoặc file bị lỗi định dạng.")
            else:
                st.info("Vui lòng tải lên file DOCX để bắt đầu.")

    # Main content area: Hiển thị chế độ luyện tập
    if st.session_state.questions:
        if st.session_state.current_mode == "group":
            Luyện_tập_theo_nhóm(st.session_state.questions)

        elif st.session_state.current_mode == "all":
            if st.button("⬅️ Quay lại chế độ Luyện tập theo nhóm"):
                st.session_state.current_mode = "group"
                st.session_state.active_translation_key = None 
                st.rerun()
            st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
            display_all_questions(st.session_state.questions)
            
        elif st.session_state.current_mode == "test":
            if st.button("⬅️ Quay lại chế độ Luyện tập theo nhóm"):
                st.session_state.current_mode = "group"
                st.session_state.active_translation_key = None 
                st.rerun()
            st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
            display_test_mode(st.session_state.questions)

if __name__ == "__main__":
    main()
