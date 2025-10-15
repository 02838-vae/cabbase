import streamlit as st
import base64
import os
import time

# ===== CẤU HÌNH =====
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

# ===== VIDEO INTRO =====
if not st.session_state.show_main:
    if os.path.exists(video_file):
        video_data = get_base64(video_file)
        st.markdown(f"""
        <style>
        html, body, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"] {{
            margin:0!important; padding:0!important; background:black!important; overflow:hidden!important; height:100vh!important;
        }}
        [data-testid="stHeader"] {{ display:none!important; }}
        .video-container {{
            position: fixed; inset:0; width:100vw; height:100vh;
            background:black; display:flex; justify-content:center; align-items:center; z-index:9998; overflow:hidden;
        }}
        .video-bg {{ width:100%; height:100%; object-fit:cover; object-position:center center; z-index:9997; }}
        .intro-text {{
            position:absolute; bottom:12vh; width:100%; text-align:center;
            font-family:'Special Elite', cursive; font-size:44px; font-weight:bold; color:#fff;
            text-shadow:0 0 20px rgba(255,255,255,0.8), 0 0 40px rgba(180,220,255,0.6), 0 0 60px rgba(255,255,255,0.4);
            opacity:0; animation: appear 3s ease-in forwards, floatFade 3s ease-in 5s forwards; z-index:9999;
        }}
        @keyframes appear {{0%{{opacity:0; filter:blur(8px); transform:translateY(40px);}}100%{{opacity:1; filter:blur(0); transform:translateY(0);}}}}
        @keyframes floatFade {{0%{{opacity:1; filter:blur(0); transform:translateY(0);}}100%{{opacity:0; filter:blur(12px); transform:translateY(-30px) scale(1.05);}}}}
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
.stApp {{
    font-family: 'Special Elite', cursive !important;
    background:
        linear-gradient(rgba(245, 222, 179, 0.35), rgba(245, 222, 179, 0.35)),
        url("data:image/jpeg;base64,{img_base64}") no-repeat center bottom fixed;  /* đổi center center -> center bottom */
    background-size: cover;
    filter: sepia(0.25) brightness(0.9) contrast(1.05);
    backdrop-filter: blur(6px);
}}
header[data-testid="stHeader"] {{ display:none; }}
.block-container {{ padding-top:0!important; }}
.main-title {{ text-align:center; font-size:50px; font-weight:bold; color:#3e2723; text-shadow:2px 2px 4px #fff; margin-top:50px; }}
.audio-fixed {{
    position: fixed;
    top: 15px;
    left: 15px;
    width: 200px;
    z-index:10000;
}}
</style>
""", unsafe_allow_html=True)

# ===== THANH NHẠC MINI (HTML) =====
if os.path.exists("background.mp3"):
    audio_base64 = get_base64("background.mp3")
    st.markdown(f"""
    <audio class="audio-fixed" controls autoplay loop>
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
    </audio>
    """, unsafe_allow_html=True)

# ===== TIÊU ĐỀ =====
st.markdown('<div class="main-title">📜 TỔ BẢO DƯỠNG SỐ 1</div>', unsafe_allow_html=True)
