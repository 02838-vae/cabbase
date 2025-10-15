import streamlit as st
import base64
import os
import time

st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide", initial_sidebar_state="collapsed")

# ===== HÀM PHỤ TRỢ =====
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# ===== TRẠNG THÁI =====
if "show_main" not in st.session_state:
    st.session_state.show_main = False
if "video_played" not in st.session_state:
    st.session_state.video_played = False

video_file = "airplane.mp4"

# ===== MÀN HÌNH VIDEO INTRO =====
if not st.session_state.show_main:
    if os.path.exists(video_file):
        video_data = get_base64(video_file)
        st.markdown(f"""
        <style>
        html, body, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"] {{
            margin: 0 !important;
            padding: 0 !important;
            background: black !important;
            overflow: hidden !important;
            height: 100vh !important;
        }}
        [data-testid="stHeader"] {{ display: none !important; }}
        .video-container {{
            position: fixed;
            inset: 0;
            width: 100vw;
            height: 100vh;
            background: black;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9998;
            overflow: hidden;
        }}
        .video-bg {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: center center;
        }}
        .intro-text {{
            position: absolute;
            bottom: 12vh;
            width: 100%;
            text-align: center;
            font-family: 'Special Elite', cursive;
            font-size: 44px;
            font-weight: bold;
            color: #ffffff;
            text-shadow:
                0 0 20px rgba(255,255,255,0.8),
                0 0 40px rgba(180,220,255,0.6),
                0 0 60px rgba(255,255,255,0.4);
            opacity: 0;
            animation:
                appear 3s ease-in forwards,
                floatFade 3s ease-in 5s forwards;
        }}
        @keyframes appear {{
            0% {{ opacity: 0; filter: blur(8px); transform: translateY(40px); }}
            100% {{ opacity: 1; filter: blur(0); transform: translateY(0); }}
        }}
        @keyframes floatFade {{
            0% {{ opacity: 1; }}
            100% {{ opacity: 0; transform: translateY(-30px) scale(1.05); }}
        }}
        </style>

        <div class="video-container">
            <video class="video-bg" autoplay muted playsinline>
                <source src="data:video/mp4;base64,{video_data}" type="video/mp4">
            </video>
            <div class="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.video_played:
            st.session_state.video_played = True
            time.sleep(8.5)
            st.session_state.show_main = True
            st.rerun()
        st.stop()
    else:
        st.error("❌ Không tìm thấy file airplane.mp4")
        st.stop()

# ===== TRANG CHÍNH =====
img_base64 = get_base64("cabbase.jpg") if os.path.exists("cabbase.jpg") else ""

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Special+Elite&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"] {{
    height: 100%;
    margin: 0;
    padding: 0;
}}

.stApp {{
    font-family: 'Special Elite', cursive !important;
    background:
        linear-gradient(rgba(250, 245, 230, 0.25), rgba(250, 245, 230, 0.25)),
        url("data:image/jpeg;base64,{img_base64}") no-repeat center center fixed;
    background-size: cover;
    backdrop-filter: blur(1px);
}}

[data-testid="stHeader"], [data-testid="stToolbar"] {{
    display: none !important;
}}

.block-container {{
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    margin: 0 auto !important;
}}

.main-box {{
    background-color: rgba(255, 255, 255, 0.5);
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 0 25px rgba(0,0,0,0.2);
    max-width: 900px;
    margin: 6rem auto;
    text-align: center;
    backdrop-filter: blur(3px);
}}

.main-title {{
    font-size: 48px;
    font-weight: bold;
    color: #3e2723;
    text-shadow: 2px 2px 5px rgba(255,255,255,0.8);
}}

.sub-text {{
    font-size: 22px;
    color: #5d4037;
    margin-top: 15px;
}}
</style>
""", unsafe_allow_html=True)

# ===== GIAO DIỆN CHÍNH =====
st.markdown("<div class='main-box'>", unsafe_allow_html=True)
st.markdown("<div class='main-title'>✈️ TỔ BẢO DƯỠNG SỐ 1</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-text'>Chào mừng bạn đến với trang thông tin của chúng tôi!</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ===== NHẠC NỀN =====
try:
    with open("background.mp3", "rb") as f:
        audio_bytes = f.read()
        html_audio = """
        <div style='text-align:center; margin-top:-40px;'>
            <p style='font-family:Special Elite; color:#3e2723; font-size:17px;'>
                &#127925; Nhạc nền (hãy nhấn Play để thưởng thức)
            </p>
        </div>
        """
        st.markdown(html_audio, unsafe_allow_html=True)
        st.audio(audio_bytes, format="audio/mp3", start_time=0)
except FileNotFoundError:
    st.warning("⚠️ Không tìm thấy file background.mp3 — vui lòng thêm file vào cùng thư mục.")
