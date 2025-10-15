import streamlit as st
import pandas as pd
import base64
import os
import time

st.set_page_config(page_title="Airplane Intro", layout="wide", initial_sidebar_state="collapsed")
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

# Ẩn toàn bộ sidebar và toolbar
st.markdown("""
    <style>
    [data-testid="stSidebar"], [data-testid="stToolbar"], header, footer {display: none !important;}
    html, body, [class*="stAppViewContainer"], [class*="stApp"], [class*="stMainBlockContainer"] {
        margin: 0;
        padding: 0;
        height: 100%;
        overflow: hidden;
        background: black;
    }
    </style>
""", unsafe_allow_html=True)

# Quản lý trạng thái intro
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

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

# ---------- TRANG CHÍNH ----------
st.session_state.intro_done = True

st.markdown("""
    <style>
    .stApp {
        background: url("cabbase.jpg") no-repeat center center fixed;
        background-size: cover;
    }
    .main-box {
        background-color: rgba(255, 255, 255, 0.8);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 0 20px rgba(0,0,0,0.3);
        max-width: 900px;
        margin: 5rem auto;
    }
    </style>
""", unsafe_allow_html=True)
img_base64 = get_base64("cabbase.jpg") if os.path.exists("airplane.jpg") else ""

st.markdown("<div class='main-box'>", unsafe_allow_html=True)
st.title("TỔ BẢO DƯỠNG SỐ 1")
st.write("Video intro đã kết thúc — Chào mừng bạn đến với website ✈️")
st.markdown("</div>", unsafe_allow_html=True)
