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
# \u2699\ufe0f HAM HO TRO VA FILE I/O
# ====================================================
def clean_text(s: str) -> str:
    if s is None:
        return ""
    return re.sub(r'\s+', ' ', s).strip()

def read_docx_paragraphs(source):
    try:
        # 1. Thu duong dan tuong doi (vi du: cabbank.docx)
        doc = Document(os.path.join(os.path.dirname(__file__), source))
    except Exception as e:
        try:
            # 2. Thu duong dan co ban (vi du: pages/PL1.docx)
            doc = Document(source)
        except Exception:
            try:
                # 3. Thu duong dan "pages/source" (chu yeu cho fallback)
                doc = Document(f"pages/{source}")
            except Exception:
                return []
    # Thay the p.text.strip() de tranh loi encoding
    return [p.text.strip() for p.paragraphs if p.text.strip()]

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
# \uD83D\uDCD7 PARSER 1: NGAN HANG KY THUAT (CABBANK)
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
# \uD83D\uDCD7 PARSER 2: NGAN HANG LUAT (LAWBANK)
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
# \uD83D\uDCD7 PARSER 3: PHU LUC 1 (DINH DANG DAC BIET)
# ====================================================
def parse_pl1(source):
    """
    Parser cho dinh dang PL1:
    - Cau hoi bat dau bang so (1. ...)
    - Dap an la cac dong tiep theo (tu dong gan A, B, C, D)
    - Dap an dung co dau (*) o cuoi
    """
    paras = read_docx_paragraphs(source)
    if not paras: return []

    questions = []
    current = {"question": "", "options": [], "answer": ""}
    
    # Regex bat dau cau hoi: So + dau cham (VD: "1.", "10.")
    q_start_pat = re.compile(r'^\d+[\.\)]\s+')
    
    # Danh sach nhan tu dong vi file Word bi an A,B,C
    labels = ["A", "B", "C", "D", "E", "F"]

    for p in paras:
        clean_p = clean_text(p)
        if not clean_p: continue
        
        # Kiem tra xem co phai bat dau cau hoi moi khong
        if q_start_pat.match(clean_p):
            # Luu cau hoi cu truoc khi sang cau moi
            if current["question"]:
                # Neu chua co dap an dung, mac dinh lay A (hoac xu ly loi)
                if not current["answer"] and current["options"]:
                    current["answer"] = current["options"][0]
                questions.append(current)
            
            # Loai bo so thu tu o dau cau hoi de hien thi dep hon
            q_text = q_start_pat.sub('', clean_p)
            current = {"question": q_text, "options": [], "answer": ""}
        
        else:
            # Neu khong phai cau hoi, thi la dap an
            if current["question"]: # Chi xu ly neu da co cau hoi
                is_correct = False
                # Kiem tra dau hieu dap an dung (*)
                if "(*)" in clean_p:
                    is_correct = True
                clean_p = clean_p.replace("(*)", "").strip() # Xoa dau (*) di
                
                # Tu dong gan nhan A, B, C, D
                idx = len(current["options"])
                if idx < len(labels):
                    label = labels[idx]
                    opt_text = f"{label}. {clean_p}"
                    current["options"].append(opt_text)
                    
                    if is_correct:
                        current["answer"] = opt_text

    # Luu cau cuoi cung
    if current["question"]:
        if not current["answer"] and current["options"]:
            current["answer"] = current["options"][0]
        questions.append(current)
        
    return questions

# ====================================================
# \u2B50\ufe0f HAM: XEM TOAN BO CAU HOI
# ====================================================
def display_all_questions(questions):
    st.markdown('<div class="result-title"><h3>&#x1F4DA; TOAN BO NGAN HANG CAU HOI</h3></div>', unsafe_allow_html=True)
    if not questions:
        st.warning("Khong co cau hoi nao de hien thi.")
        return
    
    for i, q in enumerate(questions, start=1):
        st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True)
        
        for opt in q["options"]:
            if clean_text(opt) == clean_text(q["answer"]):
                # Dap an dung: Xanh la
                color_style = "color:#00ff00; text-shadow: 0 0 3px rgba(0, 255, 0, 0.8);"
            else:
                # Dap an thuong: Trang
                color_style = "color:#FFFFFF;"
            st.markdown(f'<div class="bank-answer-text" style="{color_style}">{opt}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)

# ====================================================
# \u2B50\ufe0f HAM: TEST MODE
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
        st.markdown('<div class="result-title"><h3>&#x1F4DD; LAM BAI TEST 50 CAU</h3></div>', unsafe_allow_html=True)
        st.info(f"Bai test se gom **{min(TOTAL_QUESTIONS, len(questions))}** cau hoi duoc chon ngau nhien tu **{bank_name}**. Ty le dat (PASS) la **{int(PASS_RATE*100)}%** ({int(TOTAL_QUESTIONS * PASS_RATE)} cau dung).")
        
        if st.button("\uD83D\uDE80 Bat dau Bai Test", key=f"{test_key_prefix}_start_btn"):
            st.session_state[f"{test_key_prefix}_questions"] = get_random_questions(questions, TOTAL_QUESTIONS)
            st.session_state[f"{test_key_prefix}_started"] = True
            st.session_state[f"{test_key_prefix}_submitted"] = False
            st.session_state.current_mode = "test" 
            st.rerun()
        return

    if not st.session_state[f"{test_key_prefix}_submitted"]:
        st.markdown('<div class="result-title"><h3>\u23F3 DANG LAM BAI TEST</h3></div>', unsafe_allow_html=True)
        test_batch = st.session_state[f"{test_key_prefix}_questions"]
        for i, q in enumerate(test_batch, start=1):
            st.markdown(f'<div class="bank-question-text">{i}. {q["question"]}</div>', unsafe_allow_html=True)
            st.radio("", q["options"], key=f"{test_key_prefix}_q_{i}")
            st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True) 
        if st.button("\u2705 Nop bai Test", key=f"{test_key_prefix}_submit_btn"):
            st.session_state[f"{test_key_prefix}_submitted"] = True
            st.rerun()
            
    else:
        st.markdown('<div class="result-title"><h3>\uD83C\uDF89 KET QUA BAI TEST</h3></div>', unsafe_allow_html=True)
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
            # FIX YEU CAU 4: Chuyen sang dung markdown de kiem soat dinh dang
            st.markdown(f"\uD83D\uDCA1 Dap an dung: **{q['answer']}**") 
            st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True) 
        
        total_q = len(test_batch)
        pass_threshold = total_q * PASS_RATE
        st.markdown(f'<div class="result-title"><h3>\uD83C\uDFAF KET QUA: {score}/{total_q}</h3></div>', unsafe_allow_html=True)

        if score >= pass_threshold:
            st.balloons()
            st.success(f"\uD83C\uDF8A **CHUC MUNG!** Ban da DAT (PASS).")
        else:
            st.error(f"\uD83D\uDE22 **KHONG DAT (FAIL)**.")

        if st.button("\u21BA\ufe0f Lam lai Bai Test", key=f"{test_key_prefix}_restart_btn"):
            for i in range(1, total_q + 1):
                st.session_state.pop(f"{test_key_prefix}_q_{i}", None) 
            st.session_state[f"{test_key_prefix}_started"] = False
            st.session_state[f"{test_key_prefix}_submitted"] = False
            st.rerun()

# ====================================================
# \uD83D\uDDA5\ufe0f GIAO DIEN STREAMLIT
# ====================================================
st.set_page_config(page_title="Ngan hang trac nghiem", layout="wide")

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

/* Noi dung noi len tren nen */
[data-testid="stAppViewContainer"],
[data-testid="stMainBlock"],
.main {{
    background-color: transparent !important;
}}

/* An UI */
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

/* TITLE CHINH */
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

/* SO 1 */
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

/* FIX YEU CAU 2: TITLE LON NHUNG VAN 1 HANG */
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
        /* Tang len 4.8vw va giam spacing de chu to hon ma van 1 dong */
        font-size: 4.8vw !important;
        letter-spacing: -0.5px;
        white-space: nowrap; 
    }}
}}

/* STYLE CAU HOI & DAP AN */
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
    /* FIX YEU CAU 2: Dam bao mau chu la trang */
    color: #FFFFFF !important; 
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
    margin: 15px 0;
    height: 1px;
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
# \uD83D\uDDFA\ufe0f HEADER & BODY
# ====================================================
st.markdown("""
<div id="header-content-wrapper">
    <div id="back-to-home-btn-container">
        <a id="manual-home-btn" href="/?skip_intro=1" target="_self">&#x1F3E0; Ve Trang Chu</a>
    </div>
    <div id="main-title-container"><h1>TO BAO DUONG SO <span class="number-one">1</span></h1></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div id="sub-static-title"><h2>NGAN HANG TRAC NGHIEM</h2></div>', unsafe_allow_html=True)

if "current_group_idx" not in st.session_state: st.session_state.current_group_idx = 0
if "submitted" not in st.session_state: st.session_state.submitted = False
if "current_mode" not in st.session_state: st.session_state.current_mode = "group"
if "last_bank_choice" not in st.session_state: st.session_state.last_bank_choice = "----" 

# CAP NHAT LIST NGAN HANG (Loai bo dau de tranh loi encoding)
BANK_OPTIONS = ["----", "Ngan hang Ky thuat", "Ngan hang Luat VAECO", "Ngan hang Docwise"]
bank_choice = st.selectbox("Chon ngan hang:", BANK_OPTIONS, index=BANK_OPTIONS.index(st.session_state.get('bank_choice_val', '----')), key="bank_selector_master")
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
    # XU LY LOGIC NGUON DU LIEU
    source = ""
    is_docwise = False
    
    if "Ky thuat" in bank_choice:
        source = "cabbank.docx"
    elif "Luat VAECO" in bank_choice:
        source = "lawbank.docx"
    elif "Docwise" in bank_choice:
        is_docwise = True
        # Dropdown phu cho Docwise
        doc_options = ["Phu Luc 1"]
        doc_selected = st.selectbox("Chon Phu luc:", doc_options)
        
        if doc_selected == "Phu Luc 1":
            # \uD83D\uDE80 FIX YEU CAU 1: Doi duong dan source de doc dung file trong thu muc pages
            source = "pages/PL1.docx" 

    # LOAD CAU HOI
    if is_docwise:
        # Docwise dung parser dac biet PL1
        questions = parse_pl1(source)
    elif "Ky thuat" in bank_choice:
        questions = parse_cabbank(source)
    else:
        questions = parse_lawbank(source)

    if not questions:
        st.error(f"\u274C Khong doc duoc cau hoi nao tu file **{source}**.")
        st.stop() 
    
    total = len(questions)
    
    # --- MODE: GROUP ---
    if st.session_state.current_mode == "group":
        st.markdown('<div class="result-title" style="margin-top: 0px;"><h3>Luyen tap theo nhom (10 cau/nhom)</h3></div>', unsafe_allow_html=True)
        group_size = 10
        if total > 0:
            groups = [f"Cau {i*group_size+1}-{min((i+1)*group_size, total)}" for i in range(math.ceil(total/group_size))]
            if st.session_state.current_group_idx >= len(groups): st.session_state.current_group_idx = 0
            selected = st.selectbox("Chon nhom cau:", groups, index=st.session_state.current_group_idx, key="group_selector")
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
                if st.button("\uD83D\uDCD6 Hien thi toan bo ngan hang", key="btn_show_all"):
                    st.session_state.current_mode = "all"
                    st.rerun()
            with col_test:
                if st.button("Lam bai test", key="btn_start_test"):
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
                    if st.button("\u2705 Nop bai", key="submit_group"):
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
                            # FIX YEU CAU 3: Khong in dam, in dam dap an dung
                            st.markdown(f"\u2705 Dung &ndash; Dap an: **{q['answer']}**") 
                            score += 1
                        else: 
                            # FIX YEU CAU 3: Khong in dam, in dam dap an dung
                            st.markdown(f"\u274C Sai &ndash; Dap an dung: **{q['answer']}**") 
                        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True) 

                    st.markdown(f'<div class="result-title"><h3>\uD83C\uDFAF KET QUA: {score}/{len(batch)}</h3></div>', unsafe_allow_html=True)
                    col_reset, col_next = st.columns(2)
                    with col_reset:
                        if st.button("\u21BA\ufe0f Lam lai nhom nay", key="reset_group"):
                            for i in range(start+1, end+1): st.session_state.pop(f"q_{i}", None) 
                            st.session_state.submitted = False
                            st.rerun()
                    with col_next:
                        if st.session_state.current_group_idx < len(groups) - 1:
                            if st.button("\u27A1\ufe0f Tiep tuc nhom sau", key="next_group"):
                                st.session_state.current_group_idx += 1
                                st.session_state.submitted = False
                                st.rerun()
                        else: 
                            st.info("\uD83C\uDF89 Da hoan thanh tat ca cac nhom cau hoi!")
            else: st.warning("Khong co cau hoi trong nhom nay.")
        else: st.warning("Khong co cau hoi nao trong ngan hang nay.")

    elif st.session_state.current_mode == "all":
        if st.button("\u2B05\ufe0f Quay lai che do Luyen tap theo nhom"):
            st.session_state.current_mode = "group"
            st.rerun()
        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
        display_all_questions(questions)
        
    elif st.session_state.current_mode == "test":
        if st.button("\u2B05\ufe0f Quay lai che do Luyen tap theo nhom"):
            st.session_state.current_mode = "group"
            st.rerun()
        st.markdown('<div class="question-separator"></div>', unsafe_allow_html=True)
        display_test_mode(questions, bank_choice)
