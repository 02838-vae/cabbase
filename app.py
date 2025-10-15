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

/* === RESET TOÀN BỘ TRẮNG ĐẦU TRANG === */
html, body, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"], [data-testid="stMainBlockContainer"] {{
    margin: 0 !important;
    padding: 0 !important;
    background: transparent !important;
    height: 100%;
}}

header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], footer {{
    display: none !important;
}}

.block-container {{
    padding-top: 0 !important;
    margin-top: 0 !important;
    background: transparent !important;
}}

/* === BACKGROUND CHÍNH === */
.stApp {{
    font-family: 'Special Elite', cursive !important;
    background:
        linear-gradient(rgba(245, 242, 230, 0.6), rgba(245, 242, 230, 0.6)),
        url("data:image/jpeg;base64,{img_base64}") no-repeat center center fixed;
    background-size: cover !important;
    background-attachment: fixed !important;
    background-repeat: no-repeat !important;
}}

/* Overlay họa tiết vintage */
.stApp::after {{
    content: "";
    position: fixed;
    inset: 0;
    background: url("https://www.transparenttextures.com/patterns/aged-paper.png");
    opacity: 0.18;
    pointer-events: none;
    z-index: 0;
}}

/* ===== TIÊU ĐỀ ===== */
.main-title {{
    font-size: 48px;
    font-weight: bold;
    text-align: center;
    color: #3e2723;
    margin-top: 20px;
    text-shadow: 2px 2px 0 #fff, 0 0 25px #f0d49b, 0 0 50px #bca27a;
    z-index: 2;
}}
.sub-title {{
    font-size: 34px;
    text-align: center;
    color: #6d4c41;
    margin-top: 5px;
    margin-bottom: 25px;
    letter-spacing: 1px;
    animation: glowTitle 3s ease-in-out infinite alternate;
    z-index: 2;
}}
@keyframes glowTitle {{
    from {{ text-shadow: 0 0 10px #bfa67a, 0 0 20px #d2b48c, 0 0 30px #e6d5a8; color: #4e342e; }}
    to {{ text-shadow: 0 0 20px #f8e1b4, 0 0 40px #e0b97d, 0 0 60px #f7e7ce; color: #5d4037; }}
}}

/* ===== FORM ===== */
.stSelectbox label {{
    font-weight: bold !important;
    font-size: 22px !important;
    color: #4e342e !important;
}}
.stSelectbox div[data-baseweb="select"] {{
    font-size: 18px !important;
    color: #3e2723 !important;
    background: rgba(255, 255, 255, 0.8) !important;
    border: 2px dashed #5d4037 !important;
    border-radius: 8px !important;
    min-height: 50px !important;
    transition: transform 0.2s ease;
}}
.stSelectbox div[data-baseweb="select"]:hover {{
    transform: scale(1.02);
    box-shadow: 0 0 12px rgba(100, 80, 60, 0.3);
}}
.stSelectbox span {{
    font-size: 18px !important;
}}

/* ===== BẢNG KẾT QUẢ ===== */
table.dataframe {{
    width: 100%;
    border-collapse: collapse;
    background: rgba(255,255,255,0.88);
    backdrop-filter: blur(2px);
    font-size: 18px;
}}
table.dataframe thead th {{
    background: #6d4c41;
    color: #fff8e1;
    padding: 14px;
    border: 2px solid #3e2723;
    font-size: 19px;
    text-align: center;
}}
table.dataframe tbody td {{
    border: 1.8px solid #5d4037;
    padding: 12px;
    font-size: 18px;
    color: #3e2723;
    text-align: center;
}}
table.dataframe tbody tr:nth-child(even) td {{
    background: rgba(248, 244, 236, 0.85);
}}
table.dataframe tbody tr:hover td {{
    background: rgba(241, 224, 198, 0.9);
    transition: 0.3s;
}}
.highlight-msg {{
    font-size: 20px;
    font-weight: bold;
    color: #3e2723;
    background: rgba(239, 235, 233, 0.9);
    padding: 12px 18px;
    border-left: 6px solid #6d4c41;
    border-radius: 8px;
    margin: 18px 0;
    text-align: center;
}}
</style>
""", unsafe_allow_html=True)


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
            </p>
        </div>
        """
        st.markdown(html_audio, unsafe_allow_html=True)
        st.audio(audio_bytes, format="audio/mp3", start_time=0)
except FileNotFoundError:
    st.warning("⚠️ Không tìm thấy file background.mp3 — vui lòng thêm file vào cùng thư mục.")
