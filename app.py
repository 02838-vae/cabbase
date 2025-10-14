import streamlit as st
import time

st.set_page_config(page_title="Airplane Intro", layout="wide")

# Mỗi lần load lại luôn phát video
st.session_state.intro_done = False

# CSS full-screen video + chữ hiệu ứng
st.markdown("""
<style>
html, body, [class*="stAppViewContainer"], [class*="stApp"], [class*="stMainBlockContainer"] {
    height: 100%;
    margin: 0;
    padding: 0;
    overflow: hidden;
}
video {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
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

# Hiển thị video intro
st.markdown(
    """
    <video autoplay muted playsinline>
        <source src="airplane.mp4" type="video/mp4">
    </video>
    <div class="overlay-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    """,
    unsafe_allow_html=True
)

# ⏳ Chờ video kết thúc (thay 10 = độ dài video giây)
time.sleep(10)
st.session_state.intro_done = True
st.switch_page("pages/main_page.py")
