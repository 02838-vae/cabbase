# -*- coding: utf-8 -*-
import streamlit as st
from docx import Document
import re
import math
import pandas as pd
import base64
import os

# ====================================================
# ⚙️ HÀM HỖ TRỢ VÀ FILE I/O
# ====================================================
def clean_text(s: str) -> str:
    if s is None:
        return ""
    return re.sub(r'\s+', ' ', s).strip()

def read_docx_paragraphs(source):
    try:
        # Đường dẫn file docx giả định nằm cùng thư mục với script
        doc = Document(os.path.join(os.path.dirname(__file__), source))
    except Exception as e:
        st.error(f"Không thể đọc file .docx: {e}")
        return []
    return [p.text.strip() for p in doc.paragraphs if p.text.strip()]

def get_base64_encoded_file(file_path):
    """Mã hóa file ảnh sang base64 để sử dụng trong CSS."""
    # Base64 cho ảnh 1x1 trong suốt (fallback)
    fallback_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    try:
        # Thử tìm file trong cùng thư mục với script
        path_to_check = os.path.join(os.path.dirname(__file__), file_path)
        if not os.path.exists(path_to_check):
             path_to_check = file_path

        if not os.path.exists(path_to_check) or os.path.getsize(path_to_check) == 0:
            return fallback_base64
            
        with open(path_to_check, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"Lỗi khi mã hóa ảnh {file_path}: {str(e)}")
        return fallback_base64

# ====================================================
# 🧩 PARSER NGÂN HÀNG KỸ THUẬT (CABBANK)
# ====================================================
def parse_cabbank(source):
    # Sử dụng lại logic parser từ file gốc
    paras = read_docx_paragraphs(source)
    if not paras:
        return []

    questions = []
    current = {"question": "", "options": [], "answer": ""}
    opt_pat = re.compile(r'(?P<star>\*)?\s*(?P<letter>[A-Da-d])[\.\)]\s+')

    for p in paras:
        matches = list(opt_pat.finditer(p))
        if not matches:
            if current["options"]:
                questions.append(current)
                current = {"question": clean_text(p), "options": [], "answer": ""}
            else:
                current["question"] += " " + clean_text(p)
            continue

        pre_text = p[:matches[0].start()].strip()
        if pre_text:
            if current["options"]:
                questions.append(current)
                current = {"question": clean_text(pre_text), "options": [], "answer": ""}
            else:
                current["question"] = clean_text(pre_text)

        for i, m in enumerate(matches):
            s, e = m.end(), matches[i + 1].start() if i + 1 < len(matches) else len(p)
            opt_body = clean_text(p[s:e])
            opt = f"{m.group('letter').lower()}. {opt_body}"
            current["options"].append(opt)
            if m.group("star"):
                current["answer"] = opt

    if current["question"] and current["options"]:
        questions.append(current)

    return questions


# ====================================================
# 🧩 PARSER NGÂN HÀNG LUẬT (LAWBANK)
# ====================================================
def parse_lawbank(source):
    # Sử dụng lại logic parser từ file gốc
    paras = read_docx_paragraphs(source)
    if not paras:
        return []

    questions = []
    current = {"question": "", "options": [], "answer": ""}
    opt_pat = re.compile(r'(?<![A-Za-z0-9/])(?P<star>\*)?\s*(?P<letter>[A-Da-d])[\.\)]\s+')

    for p in paras:
        if re.match(r'^\s*Ref', p, re.I):
            continue

        matches = list(opt_pat.finditer(p))
        if not matches:
            if current["options"]:
                if current["question"] and current["options"]:
                    if not current["answer"]:
                        current["answer"] = current["options"][0]
                    questions.append(current)
                current = {"question": clean_text(p), "options": [], "answer": ""}
            else:
                current["question"] += " " + clean_text(p)
            continue

        first_match = matches[0]
        pre_text = p[:first_match.start()].strip()
        if pre_text:
            if current["options"]:
                if current["question"] and current["options"]:
                    if not current["answer"]:
                        current["answer"] = current["options"][0]
                    questions.append(current)
                current = {"question": clean_text(pre_text), "options": [], "answer": ""}
            else:
                current["question"] += " " + clean_text(pre_text)

        for i, m in enumerate(matches):
            s = m.end()
            e = matches[i+1].start() if i+1 < len(matches) else len(p)
            opt_body = clean_text(p[s:e])
            letter = m.group("letter").lower()
            option = f"{letter}. {opt_body}"
            current["options"].append(option)
            if m.group("star"):
                current["answer"] = option

    if current["question"] and current["options"]:
        if not current["answer"]:
            current["answer"] = current["options"][0]
        questions.append(current)

    return questions


# ====================================================
# 🖥️ GIAO DIỆN STREAMLIT
# ====================================================
st.set_page_config(page_title="Ngân hàng trắc nghiệm", layout="wide")

# === KHAI BÁO VÀ CHUYỂN ĐỔI ẢNH NỀN SANG BASE64 ===
PC_IMAGE_FILE = "bank_PC.jpg"
MOBILE_IMAGE_FILE = "bank_mobile.jpg"

img_pc_base64 = get_base64_encoded_file(PC_IMAGE_FILE)
img_mobile_base64 = get_base64_encoded_file(MOBILE_IMAGE_FILE)


# === CSS: FIX FULL SCREEN, RÕ NÉT HƠN VÀ HEADER VÀNG ===
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&family=Crimson+Text&display=swap');

/* --- FIX FULL SCREEN TỐI ĐA (Loại bỏ padding/margin mặc định) --- */
/* Target root container và các thành phần chính để loại bỏ padding */
.st-emotion-cache-1gsv8h, 
.st-emotion-cache-1aehpbu, 
[data-testid="stMainBlock"], 
.main {{ 
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100vw !important;
}}
/* Loại bỏ khoảng trắng trên cùng và dưới cùng của main content wrapper */
[data-testid="stAppViewContainer"] > .main {{
    padding-top: 0rem !important;
    padding-bottom: 0rem !important;
}}
/* Đảm bảo sidebar đồng màu với lớp phủ */
[data-testid="stSidebar"] {{
    background-color: rgba(255, 255, 255, 0.95);
}}

/* --- BACKGROUND FIX: Rõ nét hơn, ít ngả vàng --- */
[data-testid="stAppViewContainer"] {{
    background-size: cover; 
    background-position: center;
    background-attachment: fixed;
    /* Giảm filter xuống mức rất nhẹ */
    filter: sepia(10%) grayscale(2%); 
}}

/* Lớp phủ (Overlay) */
[data-testid="stAppViewContainer"]::before {{
    content: "";
    position: absolute; inset: 0;
    /* Màu trắng trong suốt, giảm opacity tối đa để ảnh nền rõ nét */
    background: rgba(255, 255, 255, 0.4); 
    backdrop-filter: blur(1px);
    z-index: 0;
}}

/* --- ÁP DỤNG ẢNH NỀN --- */
/* PC/MÀN HÌNH RỘNG HƠN (>= 768px) */
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/jpeg;base64,{img_pc_base64}");
}}

/* MOBILE/MÀN HÌNH NHỎ HƠN (< 768px) */
@media (max-width: 767px) {{
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpeg;base64,{img_mobile_base64}");
    }}
}}

/* --- HEADER & MARQUEE STYLING (Vàng, 1 hàng) --- */
.custom-header-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 5px 15px;
    background-color: rgba(0, 0, 0, 0.6); /* Nền đen mờ cho tiêu đề */
    color: #FFD700; /* Màu vàng Gold */
    z-index: 1000;
    position: sticky; /* Giữ header cố định trên cùng */
    top: 0;
    width: 100%;
}}
.marquee-col {{
    flex-grow: 1;
    overflow: hidden;
    white-space: nowrap;
    text-align: left;
    max-width: 50%; /* Giới hạn chiều rộng cho marquee */
}}
.main-title-col {{
    flex-shrink: 0;
    text-align: right;
    margin-left: 15px;
}}
.running-title {{
    font-size: 1.1em;
    font-weight: bold;
    color: #FFD700; /* Vàng */
    text-shadow: 0 0 3px black;
}}
.main-title-small {{
    font-family: 'Playfair Display', serif;
    font-size: 1.4em; /* Thu nhỏ tiêu đề chính */
    margin: 0;
    color: #FFD700; /* Vàng */
    text-shadow: 0 0 5px rgba(255, 255, 0, 0.5);
}}
/* Ẩn H1/H2 mặc định để tránh xung đột với header tùy chỉnh */
h1, h2 {{ display: none; }} 

/* --- STYLING NỘI DUNG CHÍNH --- */
.stRadio label {{
    color: #333333 !important;
    font-size: 1.1em !important;
    font-weight: 500;
}}
div[data-testid="stMarkdownContainer"] p {{
    color: #333333 !important;
}}
.stSelectbox label {{
    font-size: 1.2em;
    color: #4a3e2e;
}}
.stButton>button {{
    background-color: #a89073 !important; 
    color: #f7f7f7 !important;
    border-radius: 8px;
    font-size: 1.05em;
    font-family: 'Crimson Text', serif;
    box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
    transition: all 0.2s ease;
}}
.stButton>button:hover {{
    background-color: #8c765f !important;
    transform: translateY(-1px);
    box-shadow: 3px 3px 7px rgba(0, 0, 0, 0.3);
}}
</style>
""", unsafe_allow_html=True)


# ====================================================
# 🏷️ GIAO DIỆN CHÍNH (SỬ DỤNG HEADER MỚI)
# ====================================================
# TIÊU ĐỀ CHẠY VÀ TIÊU ĐỀ CHÍNH TRÊN 1 HÀNG
st.markdown("""
<div class="custom-header-row">
    <div class="marquee-col">
        <marquee behavior="scroll" direction="left" scrollamount="4">
            <span class="running-title">Tổ bảo dưỡng số 1</span>
        </marquee>
    </div>
    <div class="main-title-col">
        <h1 class="main-title-small">📜 Ngân hàng trắc nghiệm</h1>
    </div>
</div>
""", unsafe_allow_html=True)

# Nội dung chính của ứng dụng bắt đầu ở đây
bank_choice = st.selectbox("Chọn ngân hàng:", ["Ngân hàng Kỹ thuật", "Ngân hàng Luật"], key="bank_selector")
source = "cabbank.docx" if "Kỹ thuật" in bank_choice else "lawbank.docx"

questions = parse_cabbank(source) if "Kỹ thuật" in bank_choice else parse_lawbank(source)
if not questions:
    st.error("❌ Không đọc được câu hỏi nào. Vui lòng đảm bảo file .docx có sẵn.")
    st.stop() 


# ====================================================
# 🧭 TAB: LÀM BÀI / TRA CỨU
# ====================================================
tab1, tab2 = st.tabs(["🧠 Làm bài", "🔍 Tra cứu toàn bộ câu hỏi"])

# ========== TAB 1 (Làm bài) ==========
with tab1:
    group_size = 10
    total = len(questions)

    # Đảm bảo total > 0 trước khi tính groups
    if total > 0:
        groups = [f"Câu {i*group_size+1}-{min((i+1)*group_size, total)}" for i in range(math.ceil(total/group_size))]
        
        # SỬA LỖI TRUY CẬP INDEX: sử dụng index=0 và key để đảm bảo giá trị hợp lệ
        selected = st.selectbox("Chọn nhóm câu:", groups, index=0, key="group_selector")
        
        try:
            idx = groups.index(selected)
        except ValueError:
            # Nếu giá trị cũ không còn trong danh sách mới, mặc định chọn 0
            idx = 0
            
        start, end = idx * group_size, min((idx+1) * group_size, total)
        batch = questions[start:end]

        if "submitted" not in st.session_state:
            st.session_state.submitted = False
        
        # Đảm bảo batch có nội dung trước khi hiển thị
        if batch:
            if not st.session_state.submitted:
                for i, q in enumerate(batch, start=start+1):
                    st.markdown(f"<p style='color:#1a1a1a; font-size:1.15em; font-weight:600;'>{i}. {q['question']}</p>", unsafe_allow_html=True)
                    st.radio("", q["options"], key=f"q_{i}")
                    st.markdown("---")
                if st.button("✅ Nộp bài"):
                    st.session_state.submitted = True
                    st.rerun()
            else:
                score = 0
                for i, q in enumerate(batch, start=start+1):
                    selected_opt = st.session_state.get(f"q_{i}")
                    correct = clean_text(q["answer"])
                    is_correct = clean_text(selected_opt) == correct

                    st.markdown(f"<p style='color:#1a1a1a; font-size:1.15em; font-weight:600;'>{i}. {q['question']}</p>", unsafe_allow_html=True)

                    for opt in q["options"]:
                        opt_clean = clean_text(opt)
                        
                        if opt_clean == correct:
                            style = "color:#006400; font-weight:700;" 
                        elif opt_clean == clean_text(selected_opt):
                            style = "color:#cc0000; font-weight:700; text-decoration: underline;" 
                        else:
                            style = "color:#1a1a1a;" 
                        st.markdown(f"<div style='{style}'>{opt}</div>", unsafe_allow_html=True)

                    if is_correct:
                        st.success(f"✅ Đúng — {q['answer']}")
                        score += 1
                    else:
                        st.error(f"❌ Sai — Đáp án đúng: {q['answer']}")
                    st.markdown("---")

                st.subheader(f"🎯 Kết quả: {score}/{len(batch)}")

                if st.button("🔁 Làm lại nhóm này"):
                    for i in range(start+1, end+1):
                        st.session_state.pop(f"q_{i}", None)
                    st.session_state.submitted = False
                    st.rerun()
        else:
             st.warning("Không có câu hỏi trong nhóm này.")


# ========== TAB 2 (Tra cứu) ==========
with tab2:
    st.markdown("### 🔎 Tra cứu toàn bộ câu hỏi trong ngân hàng")
    if len(questions) > 0:
        df = pd.DataFrame([
            {
                "STT": i+1,
                "Câu hỏi": q["question"],
                "Đáp án A": q["options"][0] if len(q["options"])>0 else "",
                "Đáp án B": q["options"][1] if len(q["options"])>1 else "",
                "Đáp án C": q["options"][2] if len(q["options"])>2 else "",
                "Đáp án D": q["options"][3] if len(q["options"])>3 else "",
                "Đáp án đúng": q["answer"]
            } for i, q in enumerate(questions)
        ])

        keyword = st.text_input("🔍 Tìm theo từ khóa:").strip().lower()
        df_filtered = df[df.apply(lambda r: keyword in " ".join(r.values.astype(str)).lower(), axis=1)] if keyword else df

        st.write(f"Hiển thị {len(df_filtered)}/{len(df)} câu hỏi")
        st.dataframe(df_filtered, use_container_width=True)

        csv = df_filtered.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ Tải danh sách (CSV)", csv, "ngan_hang_cau_hoi.csv", "text/csv")
    else:
        st.info("Không có dữ liệu câu hỏi để tra cứu.")
