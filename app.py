import streamlit as st
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

video_file = "airplane.mp4"

# Ẩn sidebar, header, footer
st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stToolbar"], header, footer {display: none !important;}
html, body, [class*="stAppViewContainer"], [class*="stApp"], [class*="stMainBlockContainer"] {
    margin: 0; padding: 0; height: 100%; overflow: hidden; background: black;
}
</style>
""", unsafe_allow_html=True)

# ===== MÀN HÌNH INTRO =====
if not st.session_state.show_main:
    if os.path.exists(video_file):
        video_data = get_base64(video_file)

        st.markdown(f"""
        <style>
        .video-container {{
            position: fixed;
            inset: 0;
            width: 100vw;
            height: 100vh;
            background: black;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            z-index: 9998;
        }}
        .video-bg {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .intro-text {{
            position: absolute;
            bottom: 12vh;
            width: 100%;
            text-align: center;
            font-size: 42px;
            font-weight: bold;
            color: #fff;
            text-shadow: 0 0 15px rgba(255,255,255,0.8);
            opacity: 0;
            animation:
                appear 3s ease-in forwards,
                floatFade 3s ease-in 5s forwards;
        }}
        @keyframes appear {{
            0% {{opacity:0;transform:translateY(40px);filter:blur(6px);}}
            100% {{opacity:1;transform:translateY(0);filter:blur(0);}}
        }}
        @keyframes floatFade {{
            0% {{opacity:1;transform:translateY(0);}}
            100% {{opacity:0;transform:translateY(-30px);filter:blur(10px);}}
        }}
        </style>

        <div class="video-container">
            <video class="video-bg" autoplay muted playsinline>
                <source src="data:video/mp4;base64,{video_data}" type="video/mp4">
            </video>
            <div class="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        </div>
        """, unsafe_allow_html=True)

        time.sleep(8.5)
        st.session_state.show_main = True
        st.rerun()
    else:
        st.error("❌ Không tìm thấy file airplane.mp4")
        st.stop()

# ===== TRANG CHÍNH =====
img_base64 = get_base64("cabbase.jpg")

st.markdown(f"""
<style>
[data-testid="stAppViewContainer"] {{
    background: url("data:image/jpeg;base64,{img_base64}") no-repeat center center fixed;
    background-size: cover;
    filter: brightness(0.9) sepia(0.15) saturate(1.1);
}}

.main-box {{
    backdrop-filter: blur(6px) brightness(1.1);
    background-color: rgba(255, 255, 255, 0.15);
    padding: 2rem 3rem;
    border-radius: 20px;
    box-shadow: 0 0 25px rgba(0,0,0,0.4);
    max-width: 900px;
    margin: 10vh auto;
    color: #fff;
    text-align: center;
    font-family: "Georgia", serif;
}}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-box'>", unsafe_allow_html=True)
st.title("TỔ BẢO DƯỠNG SỐ 1 ✈️")
st.write("Chào mừng bạn đến với trang chính — nơi bắt đầu hành trình khám phá bầu trời 🌍")
st.markdown("</div>", unsafe_allow_html=True)
