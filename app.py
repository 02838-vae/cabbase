import streamlit as st
import time
import os

st.set_page_config(page_title="Airplane Intro", layout="wide")

# --- Kiểm tra file tồn tại ---
if not os.path.exists("airplane.mp4"):
    st.error("❌ Không tìm thấy file airplane.mp4 trong thư mục hiện tại!")
    st.stop()

# --- Trạng thái intro ---
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

if not st.session_state.intro_done:
    # CSS full-screen và hiệu ứng chữ
    st.markdown("""
    <style>
    .stApp {
        height: 100vh;
        overflow: hidden;
    }
    .video-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -1;
    }
    video {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .overlay-text {
        position: fixed;
        bottom: 10%;
        width: 100%;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        color: white;
        text-shadow: 2px 2px 10px black;
        opacity: 0;
        animation: fadeInOut 5s ease-in-out forwards;
        animation-delay: 1s;
    }
    @keyframes fadeInOut {
        0% {opacity: 0;}
        20% {opacity: 1;}
        80% {opacity: 1;}
        100% {opacity: 0;}
    }
    </style>
    """, unsafe_allow_html=True)

    # Hiển thị video (Streamlit sẽ auto render tag <video>)
    video_file = open("airplane.mp4", "rb")
    video_bytes = video_file.read()
    st.markdown('<div class="video-container"></div>', unsafe_allow_html=True)
    st.video(video_bytes)

    # Hiệu ứng chữ
    st.markdown('<div class="overlay-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>', unsafe_allow_html=True)

    # Đợi hết video (thay 10 = số giây video thật)
    time.sleep(10)
    st.session_state.intro_done = True
    st.rerun()

# --- Trang chính ---
else:
    st.markdown(
        """
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
        """,
        unsafe_allow_html=True
    )
    st.markdown("<div class='main-box'>", unsafe_allow_html=True)
    st.title("🌟 Trang Chính")
    st.write("Chào mừng bạn đến với ứng dụng của chúng tôi!")
    st.markdown("</div>", unsafe_allow_html=True)
