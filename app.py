import streamlit as st

st.set_page_config(page_title="Airplane Intro", layout="wide")

# --- CSS cho toàn màn hình video và text hiệu ứng ---
st.markdown("""
<style>
html, body, [class*="stAppViewContainer"], [class*="stApp"] {
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

# --- HTML5 Video với onended event ---
video_html = """
<video autoplay muted playsinline onended="window.location.href='pages/main_page'">
    <source src="airplane.mp4" type="video/mp4">
    Your browser does not support the video tag.
</video>
<div class="overlay-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
"""

st.markdown(video_html, unsafe_allow_html=True)
