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
        print(f"Lỗi khi mã hóa ảnh {file_path}: {str(e)}")
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


# === CSS: FIX LỖI TRIỆT ĐỂ (ANIMATION, FILTER, KHOẢNG TRẮNG, MÀU CHỮ) ======================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Crimson+Text:wght@400;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;700&display=swap');

/* ✅ FIX ANIMATION KEYFRAMES */
@keyframes scrollText {{
    0% {{ transform: translate(100vw, 0); }}
    100% {{ transform: translate(-100%, 0); }}
}}

@keyframes colorShift {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}


/* ======================= FULL SCREEN FIX & BACKGROUND ======================= */

/* 1. Root elements: Ensure full height và remove default margins/padding */
html, body, .stApp {{
    height: 100% !important;
    min-height: 100vh !important; 
    margin: 0 !important;
    padding: 0 !important;
    overflow: auto; 
}}

/* 2. Áp dụng background PC, Overlay đen mờ (rgba(0,0,0,0.2)) */
.stApp {{
    background: linear-gradient(rgba(0, 0, 0, 0.2), rgba(0, 0, 0, 0.2)), 
                url("data:image/jpeg;base64,{img_pc_base64}") no-repeat center top fixed !important;
    background-size: cover !important;
    /* ✅ FIX BACKGROUND: Thêm lại blur(1px) và giữ tông Vintage */
    filter: sepia(0.1) brightness(0.95) contrast(1.05) saturate(1.1) blur(1px) !important; 
}}

/* 3. Background Mobile */
@media (max-width: 767px) {{
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.2), rgba(0, 0, 0, 0.2)), 
                    url("data:image/jpeg;base64,{img_mobile_base64}") no-repeat center top scroll !important;
        background-size: cover !important;
        background-attachment: scroll !important;
    }}
}}

/* 4. **FIX KHOẢNG TRỐNG VÀ TƯƠNG TÁC**: Transparent background, margin/padding 0, Z-index. */
[data-testid="stAppViewContainer"], /* Container chính bao bọc nội dung */
[data-testid="stMainBlock"], /* Khối nội dung chính */
.st-emotion-cache-1oe02fs, 
.st-emotion-cache-1gsv8h, 
.st-emotion-cache-1aehpbu, 
.st-emotion-cache-1avcm0n {{
    background-color: transparent !important;
    margin: 0 !important;
    padding: 0 !important; 
    z-index: 10; 
    min-height: 100vh !important; /* Đảm bảo cả các container bên trong cũng có chiều cao tối thiểu */
}}

/* 5. Ẩn Header, Toolbar, Footer và Status Widget */
[data-testid="stHeader"], 
[data-testid="stToolbar"],
[data-testid="stStatusWidget"],
footer {{
    background-color: transparent !important;
    height: 0 !important;
    display: none !important;
    visibility: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
}}

/* Ẩn các tiêu đề mặc định */
h1, h2 {{ visibility: hidden; height: 0; margin: 0; padding: 0; }} 

/* ======================= TIÊU ĐỀ CHẠY (FIXED POSITION) ======================= */

/* ✅ TIÊU ĐỀ CHẠY CONTAINER (FIXED) */
#main-title-container {{
    position: fixed; 
    top: 0;
    left: 0;
    width: 100%;
    height: 10vh;
    overflow: hidden;
    z-index: 5; 
    pointer-events: none; /* Cho phép click xuyên qua */
    opacity: 1;
    transition: opacity 2s;
    background-color: transparent; 
    display: flex;
    align-items: center;
}}

#main-title-container h1 {{
    visibility: visible;
    height: auto;
    font-family: 'Playfair Display', serif;
    font-size: 3.5vw;
    margin: 0;
    padding: 0;
    font-weight: 900;
    font-feature-settings: "lnum" 1;
    letter-spacing: 5px;
    white-space: nowrap;
    display: inline-block;
    background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
    background-size: 400% 400%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    color: transparent;
    /* ✅ FIX ANIMATION: Đảm bảo animation được gọi */
    animation: colorShift 10s ease infinite, scrollText 15s linear infinite;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}}

@media (max-width: 768px) {{
    #main-title-container {{
        height: 8vh;
    }}
    
    #main-title-container h1 {{
        font-size: 6.5vw;
        animation-duration: 8s;
    }}
}}

/* ======================= TẠO KHOẢNG TRỐNG CHO NỘI DUNG CHÍNH ======================= */
/* Thêm padding top để tránh bị tiêu đề FIXED che mất và padding bottom để tránh khoảng trắng cuối */
[data-testid="stMainBlock"] > div:nth-child(1) {{
    padding-top: 12vh !important; 
    padding-left: 1rem;
    padding-right: 1rem;
    padding-bottom: 2rem !important; /* ✅ Thêm padding dưới cùng */
}}

/* ======================= TIÊU ĐỀ PHỤ TĨNH & KẾT QUẢ (ĐỒNG BỘ) ======================= */
#sub-static-title, .result-title {{
    position: static;
    margin-top: 20px;
    margin-bottom: 30px;
    z-index: 90;
    background: transparent !important;
    text-align: center;
}}

#sub-static-title h2, .result-title h3 {{
    visibility: visible; 
    height: auto;
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    color: #FFEA00; 
    text-align: center;
    text-shadow: 0 0 15px #FFEA00, 0 0 30px rgba(255,234,0,0.8); 
    margin-bottom: 20px;
}}

@media (max-width: 768px) {{
    #sub-static-title h2, .result-title h3 {{
        font-size: 1.5rem; 
        white-space: wrap; 
    }}
}}

/* ======================= STYLING NỘI DUNG CHÍNH (FIX MÀU CHỮ) ======================= */

/* Câu hỏi & Nội dung (Màu chữ dễ nhìn) */
div[data-testid="stMarkdownContainer"] p {{
    /* ✅ FIX MÀU CHỮ: Trắng ngả vàng */
    color: #f7f7e7 !important; 
    font-weight: 600;
    font-size: 1.1em;
    font-family: 'Crimson Text', serif;
    /* Thêm bóng chữ để nổi bật */
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.8);
}}

/* Câu trả lời (Radio button label) */
.stRadio label {{
    /* ✅ FIX MÀU CHỮ: Trắng ngả vàng */
    color: #f7f7e7 !important;
    font-size: 1.05em !important;
    font-weight: 500;
    font-family: 'Crimson Text', serif;
    /* Thêm bóng chữ để nổi bật */
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.8);
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
# 🏷️ GIAO DIỆN HEADER CỐ ĐỊNH VÀ TIÊU ĐỀ
# ====================================================

# --- ✅ HIỂN THỊ TIÊU ĐỀ CHẠY LỚN (VỊ TRÍ FIXED) ---
main_title_text = "Tổ Bảo Dưỡng Số 1"
st.markdown(f'<div id="main-title-container"><h1>{main_title_text}</h1></div>', unsafe_allow_html=True)

# --- TIÊU ĐỀ PHỤ "NGÂN HÀNG TRẮC NGHIỆM" (STYLE ĐÃ ĐỒNG BỘ) ---
st.markdown('<div id="sub-static-title"><h2>NGÂN HÀNG TRẮC NGHIỆM</h2></div>', unsafe_allow_html=True)


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
    # Lưu lại lựa chọn ngân hàng hiện tại
    st.session_state.last_bank_choice = bank_choice
    st.rerun()

# --- Xử lý Nhóm câu hỏi ---
tab1, tab2 = st.tabs(["🧠 Làm bài", "🔍 Tra cứu toàn bộ câu hỏi"])

# ========== TAB 1 (Làm bài) ==========
with tab1:
    group_size = 10
    total = len(questions)

    if total > 0:
        groups = [f"Câu {i*group_size+1}-{min((i+1)*group_size, total)}" for i in range(math.ceil(total/group_size))]
        
        # Đảm bảo index nằm trong giới hạn và cập nhật selectbox
        if st.session_state.current_group_idx >= len(groups):
            st.session_state.current_group_idx = 0
        
        # Selectbox sẽ hiển thị tên nhóm dựa trên index hiện tại
        selected = st.selectbox("Chọn nhóm câu:", groups, index=st.session_state.current_group_idx, key="group_selector")
        
        # Cập nhật lại current_group_idx nếu người dùng chọn bằng tay qua selectbox
        new_idx = groups.index(selected)
        if st.session_state.current_group_idx != new_idx:
            st.session_state.current_group_idx = new_idx
            st.session_state.submitted = False # Khi chọn nhóm mới, reset trạng thái nộp bài

        idx = st.session_state.current_group_idx
        start, end = idx * group_size, min((idx+1) * group_size, total)
        batch = questions[start:end]

        if batch:
            if not st.session_state.submitted:
                # HIỂN THỊ CÂU HỎI
                for i, q in enumerate(batch, start=start+1):
                    # Sử dụng màu chữ mới
                    st.markdown(f"<p>{i}. {q['question']}</p>", unsafe_allow_html=True)
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

                    st.markdown(f"<p>{i}. {q['question']}</p>", unsafe_allow_html=True)

                    for opt in q["options"]:
                        opt_clean = clean_text(opt)
                        
                        if opt_clean == correct:
                            style = "color:#006400; font-weight:700; text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.8);" # Đáp án đúng (Xanh lá)
                        elif opt_clean == clean_text(selected_opt):
                            style = "color:#cc0000; font-weight:700; text-decoration: underline; text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.8);" # Đáp án sai người dùng chọn (Đỏ)
                        else:
                            style = "color:#f7f7e7; text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.8);" # Các đáp án còn lại (Trắng ngả vàng)
                        st.markdown(f"<div style='{style}'>{opt}</div>", unsafe_allow_html=True)

                    if is_correct:
                        st.success(f"✅ Đúng — {q['answer']}")
                        score += 1
                    else:
                        st.error(f"❌ Sai — Đáp án đúng: {q['answer']}")
                    st.markdown("---")

                # ✅ SỬ DỤNG STYLE TIÊU ĐỀ KẾT QUẢ MỚI
                st.markdown(f'<div class="result-title"><h3>🎯 KẾT QUẢ: {score}/{len(batch)}</h3></div>', unsafe_allow_html=True)
                
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
                            # Logic fix: Tăng index và reset trạng thái nộp bài
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
