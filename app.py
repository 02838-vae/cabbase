import streamlit as st
import time
import base64
from pathlib import Path

st.set_page_config(page_title="Airplane Intro", layout="wide")

# --- Kiểm tra trạng thái ---
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

# --- Nếu chưa xem intro ---
if not st.session_state.intro_done:
    # Đọc file video và encode base64
    video_path = Path("airplane.mp4")
    if not video_path.exists():
        st.error("❌ Không tìm thấy file airplane.mp4 trong thư mục hiện tại!")
        st.stop()

    video_bytes = video_path.read_bytes()
    video_base64 = base64.b64encode(video_bytes).decode("utf-8")

    # CSS + HTML video autoplay full màn hình
    st.markdown(f"""
    <style>
    html, body, [class*="stAppViewContainer"], [class*="stApp"], [class*="stMainBlockContainer"] {{
        height: 100%;
        margin: 0;
        padding: 0;
        overflow: hidden;
    }}
    video {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        object-fit: cover;
        z-index: -1;
    }}
    .overlay-text {{
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
    }}
    @keyframes fadeInOut {{
        0% {{opacity: 0;}}
        20% {{opacity: 1;}}
        80% {{opacity: 1;}}
        100% {{opacity: 0;}}
    }}
    </style>

    <video autoplay muted playsinline>
        <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
        Your browser does not support the video tag.
    </video>
    <div class="overlay-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    """, unsafe_allow_html=True)

    # Sau X giây (thời lượng video thật)
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
    st.write("Video intro đã kết thúc và đây là trang chính.")
    st.markdown("</div>", unsafe_allow_html=True)
