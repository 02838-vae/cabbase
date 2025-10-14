import streamlit as st
import time

st.set_page_config(page_title="Airplane Intro", layout="wide")

# --- Quản lý trạng thái ---
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

# --- CSS toàn màn hình video và text ---
st.markdown("""
<style>
html, body, [class*="stAppViewContainer"], [class*="stApp"], [class*="stMainBlockContainer"] {
    height: 100%;
    margin: 0;
    padding: 0;
    overflow: hidden;
}
.stVideo {
    position: fixed !important;
    top: 0;
    left: 0;
    width: 100vw !important;
    height: 100vh !important;
    object-fit: cover;
    z-index: -1;
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

# --- Hiển thị intro ---
if not st.session_state.intro_done:
    # Phát video intro
    st.video("airplane.mp4")

    # Dòng chữ hiệu ứng
    st.markdown("<div class='overlay-text'>KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>", unsafe_allow_html=True)

    # Đợi hết video (thay 10 bằng độ dài thực tế)
    time.sleep(10)

    # Đánh dấu intro xong và rerun
    st.session_state.intro_done = True
    st.rerun()

# --- Trang chính ---
else:
    # CSS background ảnh
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
    st.write("Video intro đã kết thúc và đây là nội dung chính.")
    st.markdown("</div>", unsafe_allow_html=True)
