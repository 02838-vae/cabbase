import streamlit as st
import base64
import time
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO

st.set_page_config(page_title="Airplane Intro", layout="wide")

# ===== HELPERS =====
def get_base64(file_path):
    with open(file_path,"rb") as f:
        return base64.b64encode(f.read()).decode()

def process_background(image_path, blur=1.5, brightness=0.9):
    img = Image.open(image_path).convert("RGB")
    img = ImageEnhance.Brightness(img).enhance(brightness)
    img = img.filter(ImageFilter.GaussianBlur(blur))
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode()

# ===== STATE =====
if "show_main" not in st.session_state:
    st.session_state.show_main = False
if "video_played" not in st.session_state:
    st.session_state.video_played = False

video_file = "airplane.mp4"
background_img = "cabbase.jpg"

# ===== VIDEO INTRO =====
if not st.session_state.show_main:
    if not os.path.exists(video_file):
        st.error("Không tìm thấy airplane.mp4")
        st.stop()
    video_data = get_base64(video_file)

    st.markdown(f"""
    <style>
    html, body, [data-testid="stAppViewContainer"] {{
        margin:0; padding:0; height:100vh; width:100vw; overflow:hidden; background:black;
    }}
    [data-testid="stHeader"] {{display:none !important;}}
    video {{
        width:100vw; height:100vh; object-fit:cover; object-position:center center;
    }}
    .intro-text {{
        position:absolute; bottom:12vh; width:100%;
        text-align:center; font-family:'Special Elite', cursive;
        font-size:clamp(20px,5vw,44px); color:white;
        text-shadow:0 0 20px rgba(255,255,255,0.8);
        animation: fadein 3s forwards, fadeout 2s 5s forwards;
    }}
    @keyframes fadein {{0%{{opacity:0;}}100%{{opacity:1;}}}}
    @keyframes fadeout {{0%{{opacity:1;}}100%{{opacity:0;}}}}
    </style>

    <div style="position:relative; width:100vw; height:100vh;">
        <video autoplay muted playsinline>
            <source src="data:video/mp4;base64,{video_data}" type="video/mp4">
        </video>
        <div class="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.video_played:
        st.session_state.video_played = True
        time.sleep(8.5)  # Thời lượng video
        st.session_state.show_main = True
        st.experimental_rerun()
    st.stop()

# ===== MAIN PAGE =====
if os.path.exists(background_img):
    bg_base64 = process_background(background_img, blur=2, brightness=0.9)
else:
    bg_base64 = ""

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Special+Elite&display=swap');
html, body, [data-testid="stAppViewContainer"] {{margin:0; padding:0;}}
.stApp {{
    font-family:'Special Elite', cursive !important;
    background: linear-gradient(rgba(245,242,200,0.5), rgba(245,242,200,0.5)),
                url("data:image/jpeg;base64,{bg_base64}") no-repeat center center fixed;
    background-size:cover;
}}
header[data-testid="stHeader"]{{display:none !important;}}
.main-title {{
    font-size:clamp(28px,6vw,54px);
    font-weight:bold; text-align:center; color:#3e2723;
    margin-top:50px;
    text-shadow:2px 2px 0 #fff,0 0 25px #f0d49b,0 0 50px #bca27a;
}}
.audio-top-left {{
    position:fixed; top:10px; left:10px; width:160px; z-index:1000;
    opacity:0.85;
}}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📜 TỔ BẢO DƯỠNG SỐ 1</div>', unsafe_allow_html=True)

# ===== BACKGROUND MUSIC =====
if os.path.exists("background.mp3"):
    audio_bytes = open("background.mp3","rb").read()
    audio_base64 = base64.b64encode(audio_bytes).decode()
    st.markdown(f"""
    <div class="audio-top-left">
        <audio controls autoplay loop style="width:100%;">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
    </div>
    """, unsafe_allow_html=True)
