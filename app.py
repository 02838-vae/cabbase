import streamlit as st
import base64
import os
import time

st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

# ===== HỖ TRỢ =====
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# ===== TRẠNG THÁI =====
if "show_main" not in st.session_state:
    st.session_state.show_main = False
if "video_played" not in st.session_state:
    st.session_state.video_played = False

video_file = "airplane.mp4"
bg_image_file = "cabbase.jpg"
audio_file = "background.mp3"

VIDEO_DURATION = 8.5  # thời lượng video intro (giây)

# ===== VIDEO INTRO =====
if not st.session_state.show_main:
    if os.path.exists(video_file):
        video_data = get_base64(video_file)
        st.markdown(f"""
        <style>
        html, body, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"] {{
            margin:0; padding:0; height:100vh; overflow:hidden; background:black;
        }}
        [data-testid="stHeader"] {{ display:none; }}
        .video-container {{
            position:fixed; inset:0; width:100vw; height:100vh;
            display:flex; justify-content:center; align-items:center; z-index:9998;
        }}
        .video-bg {{
            width:100%; height:100%; object-fit:cover; object-position:center center;
            z-index:9997;
        }}
        .intro-text {{
            position:absolute; bottom:12vh; width:100%; text-align:center;
            font-family:'Special Elite', cursive; font-weight:bold;
            color:#fff; font-size:4vw; z-index:9999;
            text-shadow:0 0 20px rgba(255,255,255,0.8),
                        0 0 40px rgba(180,220,255,0.6),0 0 60px rgba(255,255,255,0.4);
            opacity:0;
            animation: appear 3s ease-in forwards, floatFade 3s ease-in 5s forwards;
        }}
        @keyframes appear {{
            0% {{ opacity:0; transform: translateY(40px); }}
            100% {{ opacity:1; transform: translateY(0); }}
        }}
        @keyframes floatFade {{
            0% {{ opacity:1; transform: translateY(0); }}
            100% {{ opacity:0; transform: translateY(-30px) scale(1.05); }}
        }}
        @media(max-width:768px){{
            .intro-text {{ font-size:6vw; }}
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
            time.sleep(VIDEO_DURATION)
            st.session_state.show_main = True
            st.experimental_rerun()
        st.stop()
    else:
        st.error("❌ Không tìm thấy file airplane.mp4")
        st.stop()

# ===== TRANG CHÍNH =====
img_base64 = get_base64(bg_image_file) if os.path.exists(bg_image_file) else ""

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Special+Elite&display=swap');
.stApp {{
    font-family:'Special Elite', cursive;
    background: linear-gradient(rgba(245,242,180,0.5), rgba(245,242,180,0.5)),
                url("data:image/jpeg;base64,{img_base64}") no-repeat center center fixed;
    background-size:cover;
}}
.audio-box {{
    position: fixed; top:10px; left:10px; z-index:10000; width:200px;
}}
header[data-testid="stHeader"] {{ display:none; }}
.block-container {{ padding-top:0 !important; }}
.main-title {{
    font-size:48px; font-weight:bold; text-align:center;
    color:#3e2723; margin-top:25px;
    text-shadow:2px 2px 0 #fff,0 0 25px #f0d49b,0 0 50px #bca27a;
}}
</style>
""", unsafe_allow_html=True)

# ===== TIÊU ĐỀ =====
st.markdown('<div class="main-title">📜 TỔ BẢO DƯỠNG SỐ 1</div>', unsafe_allow_html=True)

# ===== NHẠC NỀN =====
if os.path.exists(audio_file):
    with open(audio_file, "rb") as f:
        audio_bytes = f.read()
        st.markdown('<div class="audio-box">', unsafe_allow_html=True)
        st.audio(audio_bytes, format="audio/mp3")  # bỏ key, start_time
        st.markdown('</div>', unsafe_allow_html=True)
