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


# === CSS: FIX FULL SCREEN, VINTAGE NHẸ & HEADER THEO PARTNUMBER.PY ===
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&family=Crimson+Text&display=swap');

/* --- FIX FULL SCREEN TỐI ĐA (Quan trọng) --- */

/* Loại bỏ padding và margin của các container chính */
.st-emotion-cache-1gsv8h, .st-emotion-cache-1aehpbu {{ /* stApp và Root */
    padding: 0 !important;
    margin: 0 !important;
}}

/* Đảm bảo Main Content bao phủ toàn bộ chiều cao cửa sổ */
.st-emotion-cache-18ni5p {{ /* stAppViewContainer - chứa toàn bộ ứng dụng */
    min-height: 100vh;
    padding: 0 !important;
    margin: 0 !important;
}}

/* Đảm bảo MainBlock không có padding trên/dưới */
.st-emotion-cache-z5fcl4 {{ /* stMainBlock */
    padding-top: 0rem !important;
    padding-bottom: 0rem !important;
    padding-left: 1rem;
    padding-right: 1rem;
}}

/* --- BACKGROUND FIX: Vintage nhẹ và rõ nét hơn --- */
[data-testid="stAppViewContainer"] {{
    background-size: cover; 
    background-position: center;
    background-attachment: fixed;
    /* Vintage nhẹ hơn */
    filter: sepia(15%) grayscale(5%); 
}}

/* Lớp phủ (Overlay) - Rất trong suốt để ảnh nền rõ */
[data-testid="stAppViewContainer"]::before {{
    content: "";
    position: absolute; inset: 0;
    /* Màu trắng trong suốt, opacity thấp */
    background: rgba(255, 255, 255, 0.25); 
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
    background-color: rgba(0, 0, 0, 0.8); /* Nền đen đậm hơn */
    z-index: 1000;
    position: sticky; 
    top: 0;
    width: 100%;
}}

/* Tiêu đề chạy - Tổ bảo dưỡng số 1 (Giống partnumber.py) */
.running-title-box {{
    flex-grow: 1;
    overflow: hidden;
    white-space: nowrap;
    text-align: left;
    max-width: 60%;
    padding: 2px 0;
}}
.running-title {{
    font-size: 1.1em;
    font-weight: bold;
    color: #FFD700; /* Vàng Gold */
    text-shadow: 0 0 5px rgba(255, 255, 0, 0.8);
    font-family: 'Playfair Display', serif;
}}

/* Tiêu đề Ngân hàng trắc nghiệm (Giống tiêu đề Tra cứu trong partnumber.py) */
.main-title-box {{
    flex-shrink: 0;
    padding: 5px 15px;
    border: 1px solid #FFD700; /* Viền vàng */
    border-radius: 8px;
    background-color: rgba(0, 0, 0, 0.5); /* Nền đen mờ */
    text-align: right;
}}
.main-title-small {{
    font-family: 'Playfair Display', serif;
    font-size: 1.1em; /* Thu nhỏ tiêu đề chính */
    margin: 0;
    color: #FFD700; /* Vàng Gold */
    text-shadow: 0 0 5px rgba(255, 255, 0, 0.5);
    font-weight: 700;
}}
/* Ẩn H1/H2 mặc định để tránh xung đột với header tùy chỉnh */
h1, h2 {{ display: none; }} 

/* --- STYLING NỘI DUNG CHÍNH --- */
/* Đảm bảo nội dung chính có padding để không chạm vào lề */
[data-testid="stMainBlock"] > div:nth-child(1) {{
    padding-left: 1rem;
    padding-right: 1rem;
}}

.stRadio label, div[data-testid="stMarkdownContainer"] p {{
    color: #1a1a1a !important; /* Màu chữ gần như đen */
}}
.stButton>button {{
    background-color: #a89073 !important; 
    color: #f7f7f7 !important;
}}
</style>
""", unsafe_allow_html=True)


# ====================================================
# 🏷️ GIAO DIỆN CHÍNH (SỬ DỤNG HEADER MỚI)
# ====================================================
# TIÊU ĐỀ CHẠY VÀ TIÊU ĐỀ CHÍNH TRÊN 1 HÀNG
st.markdown(f"""
<div class="custom-header-row">
    <div class="running-title-box">
        <marquee behavior="scroll" direction="left" scrollamount="6">
            <span class="running-title">TỔ BẢO DƯỠNG SỐ 1 - ⚜️ CHỦ ĐỘNG, SÁNG TẠO, VƯỢT KHÓ ⚜️ - TỔ BẢO DƯỠNG SỐ 1</span>
        </marquee>
    </div>
    <div class="main-title-box">
        <p class="main-title-small">NGÂN HÀNG TRẮC NGHIỆM</p>
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
