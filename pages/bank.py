import streamlit as st
from docx import Document
import re
import math
import pandas as pd
import base64

# ====================================================
# ⚙️ HÀM CHUNG
# ====================================================
def clean_text(s: str) -> str:
    if s is None:
        return ""
    return re.sub(r'\s+', ' ', s).strip()

def read_docx_paragraphs(source):
    try:
        doc = Document(source)
    except Exception as e:
        st.error(f"Không thể đọc file .docx: {e}")
        return []
    [cite_start]return [p.text.strip() for p in doc.paragraphs if p.text.strip()] [cite: 1, 2]


# ====================================================
# 🧩 PARSER NGÂN HÀNG KỸ THUẬT (CABBANK)
# ====================================================
def parse_cabbank(source):
    paras = read_docx_paragraphs(source)
    if not paras:
        return []

    questions = []
    [cite_start]current = {"question": "", "options": [], "answer": ""} [cite: 2]
    opt_pat = re.compile(r'(?P<star>\*)?\s*(?P<letter>[A-Da-d])[\.\)]\s+')

    for p in paras:
        matches = list(opt_pat.finditer(p))
        if not matches:
            if current["options"]:
                [cite_start]questions.append(current) [cite: 3]
                [cite_start]current = {"question": clean_text(p), "options": [], "answer": ""} [cite: 3]
            else:
                current["question"] += " " + clean_text(p)
            continue

        pre_text = p[:matches[0].start()].strip()
        if pre_text:
            if current["options"]:
                [cite_start]questions.append(current) [cite: 4]
                [cite_start]current = {"question": clean_text(pre_text), "options": [], "answer": ""} [cite: 4]
            else:
                [cite_start]current["question"] = clean_text(pre_text) [cite: 4]

        for i, m in enumerate(matches):
            [cite_start]s, e = m.end(), matches[i + 1].start() if i + 1 < len(matches) else len(p) [cite: 5]
            opt_body = clean_text(p[s:e])
            [cite_start]opt = f"{m.group('letter').lower()}. {opt_body}" [cite: 6]
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
    paras = read_docx_paragraphs(source)
    if not paras:
        return []

    questions = []
    [cite_start]current = {"question": "", "options": [], "answer": ""} [cite: 7]
    opt_pat = re.compile(r'(?<![A-Za-z0-9/])(?P<star>\*)?\s*(?P<letter>[A-Da-d])[\.\)]\s+')

    for p in paras:
        if re.match(r'^\s*Ref', p, re.I):
            continue

        matches = list(opt_pat.finditer(p))
        if not matches:
            if current["options"]:
                if current["question"] and current["options"]:
                    if not current["answer"]:
                        [cite_start]current["answer"] = current["options"][0] [cite: 8]
                    [cite_start]questions.append(current) [cite: 8]
                [cite_start]current = {"question": clean_text(p), "options": [], "answer": ""} [cite: 8]
            else:
                [cite_start]current["question"] += " " + clean_text(p) [cite: 9]
            continue

        first_match = matches[0]
        pre_text = p[:first_match.start()].strip()
        if pre_text:
            if current["options"]:
                if current["question"] and current["options"]:
                    if not current["answer"]:
                        [cite_start]current["answer"] = current["options"][0] [cite: 10]
                    [cite_start]questions.append(current) [cite: 10]
                [cite_start]current = {"question": clean_text(pre_text), "options": [], "answer": ""} [cite: 10]
            else:
                [cite_start]current["question"] += " " + clean_text(pre_text) [cite: 11]

        for i, m in enumerate(matches):
            s = m.end()
            e = matches[i+1].start() if i+1 < len(matches) else len(p)
            opt_body = clean_text(p[s:e])
            letter = m.group("letter").lower()
            [cite_start]option = f"{letter}. {opt_body}" [cite: 12]
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

# === ẢNH NỀN ===
# ⚠️ HÃY THAY THẾ CHUỖI BASE64 NÀY BẰNG CHUỖI THỰC TẾ CỦA bank_PC.jpg
img_pc_base64 = "..." 

# ⚠️ HÃY THAY THẾ CHUỖI BASE64 NÀY BẰNG CHUỖI THỰC TẾ CỦA bank_mobile.jpg
img_mobile_base64 = "..."

# === CSS: rõ nét, dễ nhìn trên mobile (ĐÃ CHỈNH SỬA) ===
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&family=Crimson+Text&display=swap');

/* --- CẤU HÌNH CHUNG --- */
[data-testid="stAppViewContainer"] {{
    [cite_start]background-size: cover; [cite: 14]
    [cite_start]background-position: center; [cite: 14]
    [cite_start]background-attachment: fixed; [cite: 14]
}}
[data-testid="stAppViewContainer"]::before {{
    content: "";
    position: absolute; inset: 0;
    background: rgba(255,248,235,0.85);
    backdrop-filter: blur(3px);
    [cite_start]z-index: 0; [cite: 15]
}}

/* --- ẢNH NỀN CHO PC/MÀN HÌNH RỘNG HƠN (>= 768px) --- */
@media (min-width: 768px) {{
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpeg;base64,{img_pc_base64}");
    }}
}}

/* --- ẢNH NỀN CHO MOBILE/MÀN HÌNH NHỎ HƠN (< 768px) --- */
@media (max-width: 767px) {{
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpeg;base64,{img_mobile_base64}");
    }}
}}

h1 {{
    text-align: center;
    font-family: 'Playfair Display', serif;
    font-size: 2.5em;
    color: #2a1f0f;
    margin-top: 0.2em;
    [cite_start]z-index: 1; [cite: 16]
}}
/* Tăng độ tương phản câu hỏi và đáp án */
.stRadio label {{
    color: #1a1a1a !important;
    [cite_start]font-size: 1.1em !important; [cite: 17]
    [cite_start]font-weight: 500; [cite: 17]
}}
div[data-testid="stMarkdownContainer"] p {{
    [cite_start]color: #1a1a1a !important; [cite: 18]
}}
.stSelectbox label {{
    font-size: 1.2em;
    color: #2a1f0f;
}}
.stButton>button {{
    background-color: #b0854c !important;
    [cite_start]color: white !important; [cite: 19]
    border-radius: 10px;
    font-size: 1.05em;
    font-family: 'Crimson Text', serif;
}}
.stButton>button:hover {{
    background-color: #8a693c !important;
    [cite_start]transform: scale(1.03); [cite: 20]
}}
</style>
""", unsafe_allow_html=True)


# ====================================================
# 🏷️ GIAO DIỆN CHÍNH
# ====================================================
st.markdown("<h1>📜 Ngân hàng trắc nghiệm</h1>", unsafe_allow_html=True)

bank_choice = st.selectbox("Chọn ngân hàng:", ["Ngân hàng Kỹ thuật", "Ngân hàng Luật"])
source = "cabbank.docx" if "Kỹ thuật" in bank_choice else "lawbank.docx"

questions = parse_cabbank(source) if "Kỹ thuật" in bank_choice else parse_lawbank(source)
if not questions:
    st.error("❌ Không đọc được câu hỏi nào.")
    st.stop()


# ====================================================
# 🧭 TAB: LÀM BÀI / TRA CỨU
# ====================================================
tab1, tab2 = st.tabs(["🧠 Làm bài", "🔍 Tra cứu toàn bộ câu hỏi"])

# ========== TAB 1 ==========
with tab1:
    group_size = 10
    total = len(questions)
    [cite_start]groups = [f"Câu {i*group_size+1}-{min((i+1)*group_size, total)}" for i in range(math.ceil(total/group_size))] [cite: 21]
    selected = st.selectbox("Chọn nhóm câu:", groups)
    idx = groups.index(selected)
    start, end = idx * group_size, min((idx+1) * group_size, total)
    batch = questions[start:end]

    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    if not st.session_state.submitted:
        for i, q in enumerate(batch, start=start+1):
            [cite_start]st.markdown(f"<p style='color:#1a1a1a; font-size:1.15em; font-weight:600;'>{i}. {q['question']}</p>", unsafe_allow_html=True) [cite: 22]
            st.radio("", q["options"], key=f"q_{i}")
            st.markdown("---")
        if st.button("✅ Nộp bài"):
            st.session_state.submitted = True
            st.rerun()
    else:
        score = 0
        for i, q in enumerate(batch, start=start+1):
            [cite_start]selected = st.session_state.get(f"q_{i}") [cite: 23]
            correct = clean_text(q["answer"])
            is_correct = clean_text(selected) == correct

            st.markdown(f"<p style='color:#1a1a1a; font-size:1.15em; font-weight:600;'>{i}. {q['question']}</p>", unsafe_allow_html=True)

            for opt in q["options"]:
                opt_clean = clean_text(opt)
                
                [cite_start]if opt_clean == correct: [cite: 24]
                    [cite_start]style = "color:#006400; font-weight:700;" [cite: 25]
                elif opt_clean == clean_text(selected):
                    [cite_start]style = "color:#cc0000; font-weight:700; text-decoration: underline;" [cite: 26]
                else:
                    style = "color:#1a1a1a;"
                st.markdown(f"<div style='{style}'>{opt}</div>", unsafe_allow_html=True)

            if is_correct:
                st.success(f"✅ Đúng — {q['answer']}")
                [cite_start]score += 1 [cite: 27]
            else:
                st.error(f"❌ Sai — Đáp án đúng: {q['answer']}")
            st.markdown("---")

        st.subheader(f"🎯 Kết quả: {score}/{len(batch)}")

        if st.button("🔁 Làm lại nhóm này"):
            for i in range(start+1, end+1):
                [cite_start]st.session_state.pop(f"q_{i}", None) [cite: 28]
            st.session_state.submitted = False
            st.rerun()


# ========== TAB 2 ==========
with tab2:
    st.markdown("### 🔎 Tra cứu toàn bộ câu hỏi trong ngân hàng")
    df = pd.DataFrame([
        {
            "STT": i+1,
            "Câu hỏi": q["question"],
            [cite_start]"Đáp án A": q["options"][0] if len(q["options"])>0 else "", [cite: 29]
            [cite_start]"Đáp án B": q["options"][1] if len(q["options"])>1 else "", [cite: 29]
            [cite_start]"Đáp án C": q["options"][2] if len(q["options"])>2 else "", [cite: 29]
            [cite_start]"Đáp án D": q["options"][3] if len(q["options"])>3 else "", [cite: 29]
            [cite_start]"Đáp án đúng": q["answer"] [cite: 29]
        [cite_start]} for i, q in enumerate(questions) [cite: 30]
    ])

    keyword = st.text_input("🔍 Tìm theo từ khóa:").strip().lower()
    df_filtered = df[df.apply(lambda r: keyword in " ".join(r.values.astype(str)).lower(), axis=1)] if keyword else df

    st.write(f"Hiển thị {len(df_filtered)}/{len(df)} câu hỏi")
    st.dataframe(df_filtered, use_container_width=True)

    csv = df_filtered.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ Tải danh sách (CSV)", csv, "ngan_hang_cau_hoi.csv", "text/csv")
