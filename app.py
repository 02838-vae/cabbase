import streamlit as st
import base64
import os

st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

video_file = "airplane.mp4"
bg_file = "cabbase.jpg"
audio_file = "background.mp3"

def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

if "show_main" not in st.session_state:
    st.session_state.show_main = False

if not st.session_state.show_main:
    if os.path.exists(video_file):
        video_data = get_base64(video_file)
        st.markdown(f"""
        <style>
        html, body {{ margin:0; padding:0; height:100%; overflow:hidden; background:black; }}
        .video-container {{
            position: fixed; inset:0; width:100%; height:100%;
            display:flex; justify-content:center; align-items:center;
            background:black; z-index:9999;
        }}
        .video-bg {{ width:100%; height:100%; object-fit:cover; }}
        .video-text {{
            position:absolute; bottom:12vh; width:100%; text-align:center;
            font-family:'Special Elite', cursive; font-size:clamp(24px,5vw,44px);
            font-weight:bold; color:#fff;
            text-shadow: 0 0 20px rgba(255,255,255,0.8),
                         0 0 40px rgba(180,220,255,0.6),
                         0 0 60px rgba(255,255,255,0.4);
            opacity:0;
            animation: appear 3s ease-in forwards, floatFade 3s ease-in 5s forwards;
        }}
        @keyframes appear {{
            0% {{opacity:0; filter:blur(8px); transform:translateY(40px);}}
            100%{{opacity:1; filter:blur(0); transform:translateY(0);}}
        }}
        @keyframes floatFade {{
            0% {{opacity:1; filter:blur(0); transform:translateY(0);}}
            100%{{opacity:0; filter:blur(12px); transform:translateY(-30px) scale(1.05);}}
        }}
        </style>
        <div class="video-container" id="videoContainer">
            <video id="introVideo" class="video-bg" autoplay muted playsinline>
                <source src="data:video/mp4;base64,{video_data}" type="video/mp4">
            </video>
            <div class="video-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        </div>
        <script>
            const vid = document.getElementById('introVideo');
            vid.onended = () => {{
                const container = document.getElementById('videoContainer');
                container.style.display='none';
                // Gọi Streamlit rerun
                window.parent.postMessage({{isStreamlitMessage:true,type:'stRerun'}},'*')
            }};
        </script>
        """, unsafe_allow_html=True)
    else:
        st.error("❌ Không tìm thấy file airplane.mp4")
    st.stop()

# ===== TRANG CHÍNH =====
# background vintage
if not os.path.exists(bg_file):
    st.error("Không tìm thấy cabbase.jpg")
    st.stop()

img_base64 = get_base64(bg_file)
st.markdown(f"""
<style>
.stApp {{
    background: linear-gradient(rgba(245,242,200,0.4), rgba(245,242,200,0.4)),
                url("data:image/jpeg;base64,{img_base64}") no-repeat center center fixed;
    background-size: cover;
}}
header[data-testid="stHeader"] {{ display:none; }}
.block-container {{ padding-top:2rem; }}
.main-title {{
    font-family:'Special Elite', cursive;
    font-size: clamp(36px,5vw,48px);
    font-weight:bold; text-align:center;
    color:#3e2723; margin-top:50px;
    text-shadow:2px 2px 0 #fff,0 0 25px #f0d49b,0 0 50px #bca27a;
}}
</style>
""", unsafe_allow_html=True)

# Nhạc góc trên trái
if os.path.exists(audio_file):
    audio_base64 = get_base64(audio_file)
    st.markdown(f"""
    <audio autoplay loop controls style="position:fixed; top:10px; left:10px; width:200px; z-index:9999;">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
    </audio>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">📜 TỔ BẢO DƯỠNG SỐ 1</div>', unsafe_allow_html=True)
st.write("Chào mừng bạn đến với website ✈️")
