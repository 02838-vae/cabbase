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
    # Hàm đọc nội dung file docx
    try:
        # Giả định file docx nằm cùng thư mục với script
        doc = Document(os.path.join(os.path.dirname(__file__), source))
    except Exception as e:
        st.error(f"Không thể đọc file .docx: {e}")
        return []
    return [p.text.strip() for p in doc.paragraphs if p.text.strip()]

def get_base64_encoded_file(file_path):
    """Mã hóa file ảnh sang base64 để sử dụng trong CSS."""
    fallback_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    try:
        path_to_check = os.path.join(os.path.dirname(__file__), file_path)
        if not os.path.exists(path_to_check) or os.path.getsize(path_to_check) == 0:
            return fallback_base64
            
        with open(path_to_check, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        # print(f"Lỗi khi mã hóa ảnh {file_path}: {str(e)}") # Bỏ in lỗi
        return fallback_base64

# ====================================================
# 🧩 PARSER NGÂN HÀNG KỸ THUẬT (CABBANK)
# ====================================================
def parse_cabbank(source):
    # [Giữ nguyên logic parser cabbank]
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
    # [Giữ nguyên logic parser lawbank]
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
            current = {"question": "", "options": [], "answer": ""}


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


# === CSS: FIX FULL SCREEN & STYLING (TINH CHỈNH MẠNH) ====================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Crimson+Text:wght@400;700&display=swap');

/* ======================= AGGRESSIVE FULL SCREEN FIX (Quan trọng) ======================= */

/* Target the Streamlit wrapper (stAppViewContainer) */
[data-testid="stAppViewContainer"] {{
    min-height: 100vh !important;
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100vw !important;
    width: 100vw !important; /* Buộc full width */
}}

/* Target the main content block */
[data-testid="stMainBlock"] {{
    padding: 0 !important;
    margin: 0 !important;
    width: 100% !important;
}}

/* Các wrappers khác */
.st-emotion-cache-1gsv8h, .st-emotion-cache-1aehpbu {{ 
    padding: 0 !important;
    margin: 0 !important;
}}

/* ======================= BACKGROUND & VINTAGE (Adjusted) ======================= */
[data-testid="stAppViewContainer"] {{
    background-size: cover; 
    background-position: center;
    background-attachment: fixed;
    /* TĂNG NGẢ VÀNG VÀ LÀM MỜ NỀN */
    filter: sepia(25%) grayscale(5%) brightness(0.9); 
}}

/* Lớp phủ (Overlay) - Tăng độ mờ/tối */
[data-testid="stAppViewContainer"]::before {{
    content: "";
    position: absolute; inset: 0;
    /* TĂNG OPACITY để làm mờ background và tăng độ tương phản */
    background: rgba(255, 255, 255, 0.4); 
    backdrop-filter: blur(2px); /* Mờ hơn */
    z-index: 0;
}}

/* ======================= HEADER & MARQUEE FIXED ======================= */

/* Tiêu đề chạy - Cố định trên cùng, ĐẢM BẢO KHÔNG BIẾN MẤT */
.running-title-fixed {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 35px; 
    padding: 5px 0;
    background-color: rgba(0, 0, 0, 0.9); /* Nền đen đậm */
    color: #FFD700; 
    z-index: 1000;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.5);
    overflow: hidden; 
}}
.running-title {{
    font-size: 1.15em;
    font-weight: bold;
    color: #FFD700; 
    text-shadow: 0 0 5px rgba(255, 255, 0, 0.8);
    font-family: 'Playfair Display', serif;
    white-space: nowrap;
}}

/* Tạo khoảng trống phía trên cho nội dung chính */
.main-content-start {{
    padding-top: 50px; /* Lớn hơn chiều cao của header cố định */
}}

/* Tiêu đề Ngân hàng trắc nghiệm (Tông Vàng Cũ/partnumber.py) */
.main-title-box {{
    margin: 10px 15px 15px 15px;
    padding: 8px 15px;
    border: 1px solid #FFD700; /* Viền vàng */
    border-radius: 8px;
    background-color: rgba(0, 0, 0, 0.7); /* Nền đen mờ */
    text-align: center;
    max-width: 500px;
    margin-left: auto;
    margin-right: auto;
}}
.main-title-small {{
    font-family: 'Playfair Display', serif;
    font-size: 1.3em;
    margin: 0;
    color: #FFD700; /* Vàng Gold */
    text-shadow: 0 0 5px rgba(255, 255, 0, 0.5);
    font-weight: 700;
}}

/* Ẩn các tiêu đề mặc định của Streamlit */
h1, h2 {{ display: none; }} 

/* ======================= STYLING NỘI DUNG CHÍNH ======================= */

/* Nội dung chung có padding để không chạm vào lề */
[data-testid="stMainBlock"] > div:nth-child(1) {{
    padding-left: 1rem;
    padding-right: 1rem;
}}

/* Câu hỏi & Nội dung (Màu chữ dễ nhìn) */
div[data-testid="stMarkdownContainer"] p {{
    color: #1a1a1a !important; /* Đen đậm (High Contrast) */
    font-weight: 600;
    font-size: 1.1em;
}}

/* Câu trả lời (Radio button label) */
.stRadio label {{
    color: #1a1a1a !important;
    font-size: 1.05em !important;
    font-weight: 500;
    font-family: 'Crimson Text', serif;
}}

/* Nút bấm (Style vintage) */
.stButton>button {{
    background-color: #a89073 !important; 
    color: #f7f7f7 !important;
    border-radius: 8px;
    font-size: 1.05em;
    font-family: 'Crimson Text', serif;
    box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
    transition: all 0.2s ease;
    border: none !important;
}}
.stButton>button:hover {{
    background-color: #8c765f !important;
}}
</style>
""", unsafe_allow_html=True)


# ====================================================
# 🏷️ GIAO DIỆN HEADER CỐ ĐỊNH
# ====================================================
# TIÊU ĐỀ CHẠY CỐ ĐỊNH TRÊN CÙNG
st.markdown("""
<div class="running-title-fixed">
    <marquee behavior="scroll" direction="left" scrollamount="6" style="line-height: 25px;">
        <span class="running-title">TỔ BẢO DƯỠNG SỐ 1 - ⚜️ CHỦ ĐỘNG, SÁNG TẠO, VƯỢT KHÓ ⚜️ - TỔ BẢO DƯỠNG SỐ 1</span>
    </marquee>
</div>
""", unsafe_allow_html=True)

# Tạo khoảng trống để nội dung chính không bị header che mất
st.markdown('<div class="main-content-start"></div>', unsafe_allow_html=True)

# TIÊU ĐỀ NGÂN HÀNG TRẮC NGHIỆM
st.markdown("""
<div class="main-title-box">
    <p class="main-title-small">NGÂN HÀNG TRẮC NGHIỆM</p>
</div>
""", unsafe_allow_html=True)


# ====================================================
# 🧭 NỘI DUNG ỨNG DỤNG
# ====================================================
# Khởi tạo trạng thái
if "current_group_idx" not in st.session_state:
    st.session_state.current_group_idx = 0
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# --- Lựa chọn Ngân hàng ---
bank_choice = st.selectbox("Chọn ngân hàng:", ["Ngân hàng Kỹ thuật", "Ngân hàng Luật"], key="bank_selector")
source = "cabbank.docx" if "Kỹ thuật" in bank_choice else "lawbank.docx"

# Load questions
questions = parse_cabbank(source) if "Kỹ thuật" in bank_choice else parse_lawbank(source)
if not questions:
    st.error("❌ Không đọc được câu hỏi nào. Vui lòng đảm bảo file .docx có sẵn.")
    st.stop() 

# --- Xử lý Reset khi đổi Ngân hàng ---
if st.session_state.get('last_bank_choice') != bank_choice:
    st.session_state.current_group_idx = 0
    st.session_state.submitted = False
    st.session_state.last_bank_choice = bank_choice
    # Rerun để áp dụng bank mới ngay lập tức
    st.rerun() 

# --- Xử lý Nhóm câu hỏi ---
tab1, tab2 = st.tabs(["🧠 Làm bài", "🔍 Tra cứu toàn bộ câu hỏi"])

# ========== TAB 1 (Làm bài) ==========
with tab1:
    group_size = 10
    total = len(questions)

    if total > 0:
        groups = [f"Câu {i*group_size+1}-{min((i+1)*group_size, total)}" for i in range(math.ceil(total/group_size))]
        
        # Đảm bảo index nằm trong giới hạn
        if st.session_state.current_group_idx >= len(groups):
            st.session_state.current_group_idx = 0
        
        # Selectbox
        selected = st.selectbox("Chọn nhóm câu:", groups, index=st.session_state.current_group_idx, key="group_selector")
        
        # Kiểm tra nếu người dùng chọn nhóm khác qua selectbox, thì reset trạng thái nộp bài
        new_idx = groups.index(selected)
        if st.session_state.current_group_idx != new_idx:
            st.session_state.current_group_idx = new_idx
            st.session_state.submitted = False 
            st.rerun() # Rerun để tải nhóm câu mới

        idx = st.session_state.current_group_idx
        start, end = idx * group_size, min((idx+1) * group_size, total)
        batch = questions[start:end]

        if batch:
            if not st.session_state.submitted:
                # HIỂN THỊ CÂU HỎI
                for i, q in enumerate(batch, start=start+1):
                    # Sử dụng màu chữ mới
                    st.markdown(f"<p style='color:#1a1a1a; font-size:1.15em; font-weight:600;'>{i}. {q['question']}</p>", unsafe_allow_html=True)
                    st.radio("", q["options"], key=f"q_{i}")
                    st.markdown("---")
                if st.button("✅ Nộp bài"):
                    st.session_state.submitted = True
                    st.rerun()
            else:
                # HIỂN THỊ KẾT QUẢ
                score = 0
                for i, q in enumerate(batch, start=start+1):
                    selected_opt = st.session_state.get(f"q_{i}")
                    correct = clean_text(q["answer"])
                    is_correct = clean_text(selected_opt) == correct

                    st.markdown(f"<p style='color:#1a1a1a; font-size:1.15em; font-weight:600;'>{i}. {q['question']}</p>", unsafe_allow_html=True)

                    for opt in q["options"]:
                        opt_clean = clean_text(opt)
                        
                        if opt_clean == correct:
                            style = "color:#006400; font-weight:700;" # Đáp án đúng (Xanh lá)
                        elif opt_clean == clean_text(selected_opt):
                            style = "color:#cc0000; font-weight:700; text-decoration: underline;" # Đáp án sai người dùng chọn (Đỏ)
                        else:
                            style = "color:#1a1a1a;" # Các đáp án còn lại (Đen đậm)
                        st.markdown(f"<div style='{style}'>{opt}</div>", unsafe_allow_html=True)

                    if is_correct:
                        st.success(f"✅ Đúng — {q['answer']}")
                        score += 1
                    else:
                        st.error(f"❌ Sai — Đáp án đúng: {q['answer']}")
                    st.markdown("---")

                st.subheader(f"🎯 Kết quả: {score}/{len(batch)}")
                
                # --- NÚT HÀNH ĐỘNG ---
                col_reset, col_next = st.columns(2)

                with col_reset:
                    if st.button("🔁 Làm lại nhóm này"):
                        # Xóa kết quả chọn và reset trạng thái nộp bài
                        for i in range(start+1, end+1):
                            st.session_state.pop(f"q_{i}", None)
                        st.session_state.submitted = False
                        st.rerun()
                
                with col_next:
                    if st.session_state.current_group_idx < len(groups) - 1:
                        if st.button("➡️ Tiếp tục nhóm sau"):
                            # FIX LOGIC: Tăng index và reset trạng thái nộp bài
                            st.session_state.current_group_idx += 1
                            st.session_state.submitted = False 
                            st.rerun()
                    else:
                        st.info("🎉 Đã hoàn thành tất cả các nhóm câu hỏi!")
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
