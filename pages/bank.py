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
    # Xử lý các ký tự đặc biệt của Word
    s = s.replace(u'\xa0', u' ')
    return re.sub(r'\s+', ' ', s).strip()

def read_docx_paragraphs(source):
    try:
        doc = Document(os.path.join(os.path.dirname(__file__), source))
    except Exception as e:
        try:
             doc = Document(source)
        except Exception:
            try:
                doc = Document(f"pages/{source}")
            except Exception:
                return []
    return [p.text.strip() for p in doc.paragraphs if p.text.strip()]

def get_base64_encoded_file(file_path):
    fallback_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    try:
        path_to_check = os.path.join(os.path.dirname(__file__), file_path)
        if not os.path.exists(path_to_check) or os.path.getsize(path_to_check) == 0:
            path_to_check = file_path 
        
        if not os.path.exists(path_to_check) or os.path.getsize(path_to_check) == 0:
            return fallback_base64
            
        with open(path_to_check, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
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
# 🧩 PARSER 3: PHỤ LỤC 1 (FIXED - SMART BOUNDARY SCAN)
# ====================================================
def parse_pl1(source):
    """
    Parser thông minh khắc phục lỗi dính câu (VD: Câu 44 bị nuốt vào 43).
    Sử dụng thuật toán 'Anchor Scanning': Tìm đáp án đúng (*) làm neo,
    sau đó quét lên/xuống để tìm giới hạn câu hỏi.
    """
    paras = read_docx_paragraphs(source)
    if not paras: return []
    
    lines = [clean_text(p) for p in paras if clean_text(p)]
    questions = []
    
    # Tìm tất cả các vị trí dòng chứa đáp án đúng (*)
    # Đây là các 'Neo' (Anchor) chắc chắn nhất
    anchor_indices = [i for i, line in enumerate(lines) if "(*)" in line]

    if not anchor_indices:
        return []

    # Hàm kiểm tra một dòng có phải là dấu hiệu bắt đầu câu hỏi mới không
    def is_new_question_signal(text):
        # 1. Bắt đầu bằng số thứ tự (VD: "44.", "1.")
        if re.match(r'^\d+[\.\)]', text): return True
        # 2. Các từ khóa bắt đầu câu hỏi phổ biến
        if text.lower().startswith(("choose", "select", "match", "what", "where", "when", "who", "how", "which")): return True
        # 3. Là một câu hoàn chỉnh (có dấu chấm/hỏi) VÀ KHÔNG phải là đáp án A/B/C
        # (Giúp tách "Bird strikes..." ra khỏi option D của câu trước)
        if (text.endswith('.') or text.endswith('?')) and not re.match(r'^[A-F][\.\)]', text) and len(text) > 20:
            return True
        return False

    for k, idx in enumerate(anchor_indices):
        # `idx` là vị trí của dòng chứa (*), tức là một trong các đáp án
        
        # --- BƯỚC 1: TÌM GIỚI HẠN DƯỚI (End of Options) ---
        # Quét xuống dưới từ `idx` để tìm các đáp án sai đi kèm (nếu có)
        # Dừng lại nếu gặp dấu hiệu câu hỏi mới hoặc gặp Anchor tiếp theo
        end_idx = idx
        next_anchor_idx = anchor_indices[k+1] if k + 1 < len(anchor_indices) else len(lines)
        
        # Chỉ quét tối đa đến trước Anchor kế tiếp
        scan_limit = min(idx + 6, next_anchor_idx) 
        
        for j in range(idx + 1, scan_limit):
            line = lines[j]
            # Nếu dòng này trông giống câu hỏi mới -> Dừng ngay
            if is_new_question_signal(line):
                break
            # Nếu dòng này trông giống đáp án (ngắn, hoặc bắt đầu bằng chữ cái) -> Gộp vào
            end_idx = j

        # --- BƯỚC 2: TÌM GIỚI HẠN TRÊN (Start of Options & Question) ---
        # Quét ngược lên từ `idx`
        # Dừng lại khi tìm thấy dòng Câu hỏi (Question Text)
        start_idx = idx
        prev_anchor_end = -1 # Cần logic để không lấn sang câu trước (chưa implement sâu, dùng heuristic)

        # Quét ngược tối đa 6 dòng
        scan_up_limit = max(0, idx - 6)
        
        # Tìm dòng được cho là "Câu hỏi"
        q_idx = -1
        
        for j in range(idx - 1, scan_up_limit - 1, -1):
            line = lines[j]
            
            # Nếu gặp dấu hiệu câu hỏi rõ ràng (Số thứ tự, Choose...) -> Đây là câu hỏi
            if is_new_question_signal(line):
                q_idx = j
                break
            
            # Nếu dòng này có vẻ là đáp án (A., B., hoặc ngắn) -> Tiếp tục quét ngược
            # Nếu dòng này quá dài và không có A., B. -> Khả năng là câu hỏi (trường hợp mất số)
            if not re.match(r'^[A-F][\.\)]', line) and len(line) > 20 and not line.endswith('...'):
                q_idx = j
                break
                
        # Nếu không tìm thấy dấu hiệu rõ ràng, lấy dòng ngay trên dòng đáp án đầu tiên làm câu hỏi
        if q_idx == -1:
            q_idx = max(0, idx - 3) # Fallback an toàn
            # Tinh chỉnh: Nếu dòng fallback lại là đáp án của câu trước (có *) -> sai
            # Logic Anchor xử lý việc này: ta xử lý từng cụm

        # Nếu q_idx trùng hoặc nằm sau Anchor trước đó -> Cần điều chỉnh
        # (Ở đây ta giả định anchor_indices đã sắp xếp, ta chỉ lấy text trong khoảng hợp lý)
        
        # Chốt vùng dữ liệu
        # Options từ q_idx + 1 đến end_idx
        # Question là lines[q_idx]
        
        # Tuy nhiên, cần cẩn thận trường hợp q_idx chính là idx (lỗi câu 45: câu hỏi chứa *)
        if q_idx == idx: 
             # Nếu thuật toán nhận diện dòng chứa (*) là câu hỏi -> Lùi lên 1 dòng nữa làm câu hỏi
             q_idx = max(0, idx - 1)

        question_text = lines[q_idx]
        # Xóa số thứ tự (VD: "44. ")
        question_text = re.sub(r'^\d+[\.\)]\s*', '', question_text).strip()
        
        # Thu thập options từ q_idx + 1 đến end_idx
        raw_opts = lines[q_idx+1 : end_idx+1]
        
        # Xử lý Options (Gán nhãn A, B, C, D)
        final_opts = []
        final_ans = ""
        labels = ["A", "B", "C", "D", "E", "F"]
        
        # Nếu danh sách options rỗng (có thể do parsing lỗi), ít nhất thêm dòng chứa (*) vào
        if not raw_opts:
            raw_opts = [lines[idx]]

        for m, opt in enumerate(raw_opts):
            is_correct = "(*)" in opt
            clean = opt.replace("(*)", "").strip()
            
            # Tự động thêm nhãn nếu thiếu
            if not re.match(r'^[A-F][\.\)]', clean):
                lbl = labels[m] if m < len(labels) else "-"
                clean = f"{lbl}. {clean}"
            
            final_opts.append(clean)
            if is_correct:
                final_ans = clean
        
        # Kiểm tra hợp lệ trước khi thêm
        if question_text and final_opts:
            # Tránh trùng lặp câu hỏi nếu logic quét bị chồng lấn
            is_duplicate = False
            if questions and questions[-1]["question"] == question_text:
                is_duplicate = True
            
            if not is_duplicate:
                questions.append({
                    "question": question_text,
                    "options": final_opts,
                    "answer": final_ans
                })

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
            st.radio("", q["options"], key=f"{test_key_prefix}_q_{i}")
            st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True) 
        if st.button("✅ Nộp bài Test", key=f"{test_key_prefix}_submit_btn"):
            st.session_state[f"{test_key_prefix}_submitted"] = True
            st.rerun()
            
    else:
        st.markdown('<div class="result-title"><h3>🎉 KẾT QUẢ BÀI TEST</h3></div>', unsafe_allow_html=True)
        test_batch = st.session_state[f"{test_key_prefix}_questions"]
        score = 0
        for i, q in enumerate(test_batch, start=1):
            selected_opt = st.session_state.get(f"{test_key_prefix}_q_{i}")
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
            st.error(f"😢 **KHÔNG ĐẠT (FAIL)**.")

        if st.button("🔄 Làm lại Bài Test", key=f"{test_key_prefix}_restart_btn"):
            for i in range(1, total_q + 1):
                st.session_state.pop(f"{test_key_prefix}_q_{i}", None) 
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
    position: fixed; top: 10px; left: 10px; 
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
    height: 120px; overflow: hidden; pointer-events: none;
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
    position: absolute; left: 0; top: 5px; 
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

/* TITLE LỚN (4.8vw) */
#sub-static-title, .result-title {{
    margin-top: 150px; margin-bottom: 30px; text-align: center;
}}
#sub-static-title h2, .result-title h3 {{
    font-family: 'Playfair Display', serif;
    font-size: 2rem; /* Desktop */
    color: #FFEA00;
    text-shadow: 0 0 15px #FFEA00; 
}}
@media (max-width: 768px) {{
    #sub-static-title h2, .result-title h3 {{
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

.bank-answer-text {{
    font-family: 'Oswald', sans-serif !important;
    font-weight: 400 !important; 
    font-size: 22px !important; 
    padding: 5px 15px; margin: 2px 0;
    line-height: 1.5 !important; 
    display: block; 
}}

.stRadio label {{
    color: #f9f9f9 !important;
    font-size: 22px !important; 
    font-weight: 400 !important; 
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
    color: #33FF33 !important; font-size: 1.25rem !important;
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
    <div id="main-title-container"><h1>TỔ BẢO DƯỠNG SỐ <span class="number-one">1</span></h1></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div id="sub-static-title"><h2>NGÂN HÀNG TRẮC NGHIỆM</h2></div>', unsafe_allow_html=True)

if "current_group_idx" not in st.session_state: st.session_state.current_group_idx = 0
if "submitted" not in st.session_state: st.session_state.submitted = False
if "current_mode" not in st.session_state: st.session_state.current_mode = "group"
if "last_bank_choice" not in st.session_state: st.session_state.last_bank_choice = "----" 

# FIX: CẬP NHẬT LIST NGÂN HÀNG
BANK_OPTIONS = ["----", "Ngân hàng Kỹ thuật", "Ngân hàng Luật VAECO", "Ngân hàng Docwise"]
bank_choice = st.selectbox("Chọn ngân hàng:", BANK_OPTIONS, index=BANK_OPTIONS.index(st.session_state.get('bank_choice_val', '----')), key="bank_selector_master")
st.session_state.bank_choice_val = bank_choice

if st.session_state.get('last_bank_choice') != bank_choice and bank_choice != "----":
    st.session_state.current_group_idx = 0
    st.session_state.submitted = False
    st.session_state.current_mode = "group" 
    last_bank_name = st.session_state.get('last_bank_choice')
    if not isinstance(last_bank_name, str) or last_bank_name == "----": last_bank_name = "null bank" 
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
        doc_selected = st.selectbox("Chọn Phụ lục:", doc_options)
        
        if doc_selected == "Phụ Lục 1":
            source = "PL1.docx"

    # LOAD CÂU HỎI
    if is_docwise:
        # Dùng parser mới cho PL1
        questions = parse_pl1(source)
    elif "Kỹ thuật" in bank_choice:
        questions = parse_cabbank(source)
    else:
        questions = parse_lawbank(source)

    if not questions:
        st.error(f"❌ Không đọc được câu hỏi nào từ file **{source}**.")
        st.stop() 
    
    total = len(questions)
    
    # --- MODE: GROUP ---
    if st.session_state.current_mode == "group":
        st.markdown('<div class="result-title" style="margin-top: 0px;"><h3>Luyện tập theo nhóm (10 câu/nhóm)</h3></div>', unsafe_allow_html=True)
        group_size = 10
        if total > 0:
            groups = [f"Câu {i*group_size+1}-{min((i+1)*group_size, total)}" for i in range(math.ceil(total/group_size))]
            if st.session_state.current_group_idx >= len(groups): st.session_state.current_group_idx = 0
            selected = st.selectbox("Chọn nhóm câu:", groups, index=st.session_state.current_group_idx, key="group_selector")
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
                if st.button("Làm bài test", key="btn_start_test"):
                    st.session_state.current_mode = "test"
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
                        st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True)
                        st.radio("", q["options"], key=f"q_{i}")
                        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
                    if st.button("✅ Nộp bài", key="submit_group"):
                        st.session_state.submitted = True
                        st.rerun()
                else:
                    score = 0
                    for i, q in enumerate(batch, start=start+1):
                        selected_opt = st.session_state.get(f"q_{i}")
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
                            for i in range(start+1, end+1): st.session_state.pop(f"q_{i}", None) 
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
