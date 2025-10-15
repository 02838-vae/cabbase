import streamlit as st
import pandas as pd
import base64
import os
import time

st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

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

# ===== MÀN HÌNH VIDEO INTRO (FULL SCREEN) =====
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
        [data-testid="stHeader"] {{
            display: none !important;
        }}
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
            z-index: 9997;
            transition: object-fit 0.3s ease, object-position 0.3s ease;
        }}
        /* ⚙️ Điều chỉnh cho điện thoại */
        @media (max-width: 768px) {{
            .video-bg {{
                object-fit: contain !important;
                object-position: center center !important;
                transform: scale(1.05);
                background-color: black;
            }}
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
            z-index: 9999;
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

# ===== CSS PHONG CÁCH VINTAGE (NỀN RÕ + FONT TO) =====
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Special+Elite&display=swap');

.stApp {{
    font-family: 'Special Elite', cursive !important;
    background:
        linear-gradient(rgba(245, 242, 230, 0.5), rgba(245, 242, 230, 0.5)),
        url("data:image/jpeg;base64,{img_base64}") no-repeat center center fixed;
    background-size: cover;
}}
.stApp::after {{
    content: "";
    position: fixed;
    inset: 0;
    background: url("https://www.transparenttextures.com/patterns/aged-paper.png");
    opacity: 0.2;
    pointer-events: none;
    z-index: -1;
}}

header[data-testid="stHeader"] {{ display: none; }}
.block-container {{ padding-top: 0 !important; }}

/* ===== TIÊU ĐỀ ===== */
.main-title {{
    font-size: 48px;
    font-weight: bold;
    text-align: center;
    color: #3e2723;
    margin-top: 25px;
    text-shadow: 2px 2px 0 #fff, 0 0 25px #f0d49b, 0 0 50px #bca27a;
}}
.sub-title {{
    font-size: 34px;
    text-align: center;
    color: #6d4c41;
    margin-top: 5px;
    margin-bottom: 25px;
    letter-spacing: 1px;
    animation: glowTitle 3s ease-in-out infinite alternate;
}}
@keyframes glowTitle {{
    from {{ text-shadow: 0 0 10px #bfa67a, 0 0 20px #d2b48c, 0 0 30px #e6d5a8; color: #4e342e; }}
    to {{ text-shadow: 0 0 20px #f8e1b4, 0 0 40px #e0b97d, 0 0 60px #f7e7ce; color: #5d4037; }}
}}


# ===== TIÊU ĐỀ =====
st.markdown('<div class="main-title">📜 TỔ BẢO DƯỠNG SỐ 1</div>', unsafe_allow_html=True)

# ===== NHẠC NỀN =====
try:
    with open("background.mp3", "rb") as f:
        audio_bytes = f.read()
        st.markdown("""
        <div style='text-align:center; margin-top:5px;'>
            <p style='font-family:Special Elite; color:#3e2723; font-size:17px;'>
                🎵 Nhạc nền (hãy nhấn Play để thưởng thức)
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.audio(audio_bytes, format="audio/mp3", start_time=0)
except FileNotFoundError:
    st.warning("⚠️ Không tìm thấy file background.mp3 — vui lòng thêm file vào cùng thư mục.")
