import streamlit as st
import base64
import os
import time

# --- CONFIG ---
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

video_file = "airplane.mp4"
bg_file = "cabbase.jpg"
audio_file = "background.mp3"

VIDEO_DURATION_SECONDS = 5
FADE_DURATION_SECONDS = 4
TOTAL_DELAY_SECONDS = VIDEO_DURATION_SECONDS + FADE_DURATION_SECONDS

def get_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        return None

if "show_main" not in st.session_state:
    st.session_state.show_main = False
if "intro_ran" not in st.session_state:
    st.session_state.intro_ran = False

is_main_page = st.session_state.show_main
video_display_style = "display:none;" if is_main_page else "display:flex;"

# --- CSS FULLSCREEN & RESPONSIVE ---
st.markdown(f"""
<style>
html, body {{
    margin: 0; padding: 0; height: 100%; overflow: hidden; background: black;
}}
header[data-testid="stHeader"], footer {{ display: none !important; }}
section.main > div {{ padding: 0 !important; margin: 0 !important; }}
.block-container, .stApp {{
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
    height: 100vh !important;
    max-width: 100% !important;
}}

/* === VIDEO FULLSCREEN RESPONSIVE === */
.video-container {{
    position: fixed; inset: 0;
    width: 100vw; height: 100vh;
    display: flex; justify-content: center; align-items: center;
    background: black;
    z-index: 9999;
    {video_display_style}
}}
.video-bg {{
    width: 100%;
    height: 100%;
    max-width: 100vw;
    max-height: 100vh;
    object-fit: cover;
    transition: all 0.3s ease-in-out;
}}

/* 📱 Trên điện thoại, giảm scale để không bị tràn */
@media (max-width: 768px) {{
    .video-bg {{
        object-fit: contain;
        transform: scale(1.05);
    }}
}}

/* TEXT TRÊN VIDEO */
.video-text {{
    position: absolute;
    bottom: 12vh;
    width: 100%;
    text-align: center;
    font-family: 'Special Elite', cursive;
    font-size: clamp(22px, 4vw, 40px);
    font-weight: bold;
    color: #fff;
    text-shadow:
        0 0 20px rgba(255,255,255,0.8),
        0 0 40px rgba(180,220,255,0.6),
        0 0 60px rgba(255,255,255,0.4);
    opacity: 0;
    animation: appear 3s ease-in forwards, floatFade 3s ease-in 5s forwards;
}}

@keyframes appear {{
    0% {{ opacity: 0; filter: blur(8px); transform: translateY(40px); }}
    100% {{ opacity: 1; filter: blur(0); transform: translateY(0); }}
}}
@keyframes floatFade {{
    0% {{ opacity: 1; filter: blur(0); transform: translateY(0); }}
    100% {{ opacity: 0; filter: blur(12px); transform: translateY(-30px) scale(1.05); }}
}}
</style>
""", unsafe_allow_html=True)

# --- VIDEO INTRO ---
if not st.session_state.show_main and not st.session_state.intro_ran:
    video_data = get_base64(video_file)
    if video_data is None:
        st.error(f"❌ Không tìm thấy file {video_file}.")
        st.stop()

    st.markdown(f"""
    <div class="video-container" id="videoContainer">
        <video id="introVideo" class="video-bg" autoplay muted playsinline>
            <source src="data:video/mp4;base64,{video_data}" type="video/mp4">
        </video>
        <div class="video-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    </div>
    """, unsafe_allow_html=True)

    # Chờ video chạy hết rồi chuyển trang
    time.sleep(TOTAL_DELAY_SECONDS)
    st.session_state.show_main = True
    st.session_state.intro_ran = True
    st.rerun()

# --- TRANG CHÍNH ---
img_base64 = get_base64(bg_file)
if img_base64 is None:
    st.error(f"❌ Không tìm thấy file {bg_file}.")
    st.stop()

st.markdown(f"""
<style>
/* === BACKGROUND CHÍNH === */
.stApp {{
    background:
        linear-gradient(rgba(245,242,200,0.4), rgba(245,242,200,0.4)),
        url("data:image/jpeg;base64,{img_base64}") no-repeat center center;
    background-size: cover;              /* ✅ PC: full màn hình */
    background-attachment: fixed;        /* Giữ nền khi cuộn trên PC */
    min-height: 100vh !important;
    width: 100vw !important;
}}

/* 📱 MOBILE FIX */
@media (max-width: 768px) {{
    .stApp {{
        background-attachment: scroll !important;  /* ⚡ Tắt fixed trên mobile để mượt */
        background-size: contain !important;       /* Hiển thị toàn bộ ảnh */
        background-position: center center !important;
        background-repeat: no-repeat !important;
        background-color: black !important;        /* Nền đen nếu ảnh không lấp kín */
    }}
}}

.block-container {{
    padding-top: 2rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}}
.main-title {{
    font-family:'Special Elite', cursive;
    font-size: clamp(30px,5vw,48px);
    font-weight:bold; text-align:center;
    color:#3e2723; margin-top:50px;
    text-shadow:2px 2px 0 #fff,0 0 25px #f0d49b,0 0 50px #bca27a;
}}
</style>
""", unsafe_allow_html=True)

