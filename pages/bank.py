import streamlit as st
import base64
import os
import re
import time

# --- CẤU HÌNH BAN ĐẦU ---
st.set_page_config(
    page_title="Tổ Bảo Dưỡng Số 1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CÁC HÀM TIỆN ÍCH ---
def get_base64_encoded_file(file_path):
    """Đọc file và trả về Base64 encoded string."""
    path_to_check = os.path.join(os.path.dirname(__file__), file_path)
    if not os.path.exists(path_to_check) or os.path.getsize(path_to_check) == 0:
        return None
    try:
        with open(path_to_check, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    except Exception as e:
        return None

# Mã hóa các file media (bắt buộc)
try:
    bg_pc_base64     = get_base64_encoded_file("PC.jpg")
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
    logo_base64      = get_base64_encoded_file("logo.jpg")

    missing_files = []
    if not bg_pc_base64:     missing_files.append("PC.jpg")
    if not bg_mobile_base64: missing_files.append("mobile.jpg")

    if missing_files:
        st.error("⚠️ Thiếu các file sau trong thư mục:")
        st.write(" - " + "\n - ".join(missing_files))
        st.stop()

except Exception as e:
    st.error(f"❌ Lỗi khi đọc file: {str(e)}")
    st.stop()

if not logo_base64:
    logo_base64 = ""

# --- PHẦN 1: NHÚNG FONT ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Rye&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# --- PHẦN 2: CSS CHÍNH ---
hide_streamlit_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rye&display=swap');

#MainMenu, footer, header {{visibility: hidden;}}

.main {{ padding: 0; margin: 0; }}

div.block-container {{
    padding: 0;
    margin: 0;
    max-width: 100% !important;
}}

/* Áp dụng font Rye toàn trang, trừ câu hỏi và đáp án */
*:not(.stRadio label):not(.stRadio label *):not(.stMarkdown p):not(.stMarkdown p *) {{
    font-family: 'Rye', serif !important;
}}

/* Streamlit theme reset */
body, .stApp, section.main,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stBottom"],
[data-testid="stHeader"],
[data-testid="stDecoration"],
.block-container, .main {{
    background: transparent !important;
    background-color: transparent !important;
    background-image: none !important;
}}

/* Reveal grid */
.reveal-grid {{
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    display: grid;
    grid-template-columns: repeat(20, 1fr);
    grid-template-rows: repeat(12, 1fr);
    z-index: 500;
    pointer-events: none;
}}

.grid-cell {{
    background-color: #111;
    opacity: 1;
    transition: opacity 0.5s ease-out;
}}

@media (max-width: 768px) {{
    .reveal-grid {{
        grid-template-columns: repeat(10, 1fr);
        grid-template-rows: repeat(20, 1fr);
    }}
}}

@keyframes fadeInUI {{ to {{ opacity: 1; }} }}
@keyframes rotate {{ to {{ transform: translate(-50%, -50%) rotate(360deg); }} }}

/* === LOGO === */
#bank-logo-container {{
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 100;
    text-align: center;
    pointer-events: none;
}}

#bank-logo-container img {{
    height: 120px;
    width: auto;
    object-fit: contain;
    filter: drop-shadow(0 2px 8px rgba(0,0,0,0.6));
}}

@media (max-width: 768px) {{
    #bank-logo-container {{ top: 12px; }}
    #bank-logo-container img {{ height: auto; max-width: 55vw; }}
}}

/* ================================================ */
/* === CSS CHO NAVIGATION BUTTONS === */
/* ================================================ */

.nav-buttons-wrapper {{
    position: fixed;
    top: 50%;
    left: 0;
    width: 100%;
    transform: translateY(-50%);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 80px;
    z-index: 10000;
    opacity: 0;
    pointer-events: none;
    animation: fadeInNav 1s ease-out 1s forwards;
}}

@keyframes fadeInNav {{
    to {{ opacity: 1; pointer-events: all; }}
}}

.nav-buttons-wrapper .stColumn {{ display: contents !important; }}
.nav-buttons-wrapper [data-testid="column"] {{ display: contents !important; }}

.nav-buttons-wrapper a {{
    all: unset;
    display: flex !important;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    cursor: pointer;
    position: relative;
    transform-origin: center;
    padding: 1rem 2rem;
    border-radius: 9999px;
    min-width: 280px;
    text-decoration: none;
    --black-700: hsla(0, 0%, 12%, 1);
    --border_radius: 9999px;
    --transtion: 0.3s ease-in-out;
    --active: 0;
    --hover-color: hsl(40, 60%, 85%);
    --text-color: hsl(0, 0%, 100%);
    transform: scale(calc(1 + (var(--active, 0) * 0.2)));
    transition: transform var(--transtion);
}}

.nav-buttons-wrapper a::before {{
    content: "";
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 100%; height: 100%;
    background-color: var(--black-700);
    border-radius: var(--border_radius);
    box-shadow:
        inset 0 0.5px hsl(0, 0%, 100%),
        inset 0 -1px 2px 0 hsl(0, 0%, 0%),
        0px 4px 10px -4px hsla(0, 0%, 0%, calc(1 - var(--active, 0))),
        0 0 0 calc(var(--active, 0) * 0.375rem) var(--hover-color);
    transition: all var(--transtion);
    z-index: 0;
}}

.nav-buttons-wrapper a::after {{
    content: "";
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 90%; height: 90%;
    background-color: hsla(40, 60%, 85%, 0.75);
    background-image:
        radial-gradient(at 51% 89%, hsla(45, 60%, 90%, 1) 0px, transparent 50%),
        radial-gradient(at 100% 100%, hsla(35, 60%, 80%, 1) 0px, transparent 50%),
        radial-gradient(at 22% 91%, hsla(35, 60%, 80%, 1) 0px, transparent 50%);
    background-position: top;
    opacity: var(--active, 0);
    border-radius: var(--border_radius);
    transition: opacity var(--transtion);
    z-index: 2;
}}

.nav-buttons-wrapper a:hover,
.nav-buttons-wrapper a:focus-visible {{
    --active: 1;
    box-shadow: 0 0 15px 5px var(--hover-color), 0 0 0 0.375rem var(--hover-color);
}}

.nav-buttons-wrapper a span {{
    position: relative;
    z-index: 10;
    background-image: linear-gradient(90deg, var(--text-color) 0%, hsla(0, 0%, 100%, var(--active, 0.5)) 120%);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    color: transparent;
    font-weight: 600;
    letter-spacing: 1px;
    white-space: nowrap;
    font-size: 1.1rem;
    line-height: 1.1rem;
    font-family: 'Rye', serif !important;
}}

.nav-buttons-wrapper a svg {{
    position: relative;
    z-index: 10;
    width: 1.75rem; height: 1.75rem;
    color: var(--text-color);
    flex-shrink: 0;
}}

@media (max-width: 768px) {{
    .nav-buttons-wrapper {{
        bottom: 80px; top: auto;
        left: 50%;
        width: calc(100% - 40px);
        max-width: 450px;
        transform: translateX(-50%);
        flex-direction: column;
        gap: 15px;
        padding: 0;
    }}
    .nav-buttons-wrapper a {{ width: 100%; min-width: unset; padding: 0.8rem 1.5rem; }}
    .nav-buttons-wrapper a svg {{ width: 1.5rem; height: 1.5rem; }}
}}
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- HIỆU ỨNG REVEAL ---
grid_cells_html = ""
for i in range(240):
    grid_cells_html += '<div class="grid-cell"></div>'

reveal_grid_html = f"""
<div class="reveal-grid" id="reveal-grid-main">
    {grid_cells_html}
</div>
<script>
(function() {{
    function startReveal() {{
        const revealGrid = document.getElementById('reveal-grid-main');
        if (!revealGrid) {{ return; }}
        const cells = revealGrid.querySelectorAll('.grid-cell');
        const shuffledCells = Array.from(cells).sort(() => Math.random() - 0.5);
        shuffledCells.forEach((cell, index) => {{
            setTimeout(() => {{ cell.style.opacity = 0; }}, index * 10);
        }});
        setTimeout(() => {{ revealGrid.style.display = 'none'; }}, shuffledCells.length * 10 + 600);
    }}
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', startReveal);
    }} else {{
        startReveal();
    }}
}})();
</script>
"""
st.markdown(reveal_grid_html, unsafe_allow_html=True)

# --- INJECT BACKGROUND ---
st.components.v1.html(f"""
<script>
(function() {{
    var PC  = '{bg_pc_base64}';
    var MOB = '{bg_mobile_base64}';

    function go() {{
        var doc = window.parent.document;
        var isMob = window.parent.innerWidth <= 768;
        var url = 'data:image/jpeg;base64,' + (isMob ? MOB : PC);

        var d = doc.getElementById('__stbg');
        if (!d) {{
            d = doc.createElement('div');
            d.id = '__stbg';
            doc.body.appendChild(d);
        }}
        d.setAttribute('style',
            'position:fixed!important;top:0!important;left:0!important;' +
            'width:100vw!important;height:100vh!important;' +
            'background-image:url(' + url + ')!important;' +
            'background-size:cover!important;background-position:center!important;' +
            'filter:sepia(60%) grayscale(20%) brightness(85%) contrast(110%);' +
            'z-index:1!important;pointer-events:none!important;');

        var sid = '__stbgcss';
        var s = doc.getElementById(sid);
        if (!s) {{ s = doc.createElement('style'); s.id = sid; doc.head.appendChild(s); }}
        s.textContent = [
            'body','html','.stApp','section.main','.main',
            '[data-testid="stAppViewContainer"]',
            '[data-testid="stMain"]',
            '[data-testid="stBottom"]',
            '[data-testid="stHeader"]',
            '[data-testid="stDecoration"]',
            '.block-container',
            '.stApp > div',
            '[data-testid="stAppViewContainer"] > div'
        ].join(',') + '{{background:transparent!important;background-color:transparent!important;background-image:none!important;}}';
    }}

    go();
    [50,200,600,1500,3000].forEach(function(t){{ setTimeout(go, t); }});
}})();
</script>
""", height=0)

# --- LOGO ---
st.markdown(f'<div id="bank-logo-container"><img src="data:image/jpeg;base64,{logo_base64}" alt="Logo"/></div>', unsafe_allow_html=True)

# --- NAVIGATION BUTTONS ---
st.markdown("""
<div class="nav-buttons-wrapper">
    <a href="/partnumber" class="nav-button" target="_blank">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"></path>
        </svg>
        <span>TRA CỨU PART NUMBER</span>
    </a>
    <a href="/bank" class="nav-button" target="_blank">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <span>NGÂN HÀNG TRẮC NGHIỆM</span>
    </a>
</div>
""", unsafe_allow_html=True)
