import streamlit as st
import base64
import os
from io import BytesIO
from PIL import Image, ImageEnhance, ImageFilter

st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

# ===== HELPER =====
def get_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

def process_background(image_path, blur_strength=1.5, brightness=0.9):
    img = Image.open(image_path).convert("RGB")
    img = ImageEnhance.Brightness(img).enhance(brightness)
    img = img.filter(ImageFilter.GaussianBlur(blur_strength))
    buffered = BytesIO()
    img.save(buffered, format="JPEG", quality=90)
    return base64.b64encode(buffered.getvalue()).decode()

# ===== STATE =====
if "show_main" not in st.session_state:
    st.session_state.show_main = False

video_file = "airplane.mp4"
background_img = "cabbase.jpg"

# ===== VIDEO INTRO =====
if not st.session_state.show_main:
    if os.path.exists(video_file):
        video_data = get_base64(video_file)
        st.markdown(f"""
        <style>
        html, body, [data-testid="stAppViewContainer"] {{
            margin:0; padding:0; height:100vh; overflow:hidden; background:black;
        }}
        [data-testid="stHeader"] {{ display:none !important; }}
        #videoDiv {{
            position:fixed; inset:0; width:100%; height:100%;
            display:flex; justify-content:center; align-items:center;
            background:black; z-index:1000; transition: opacity 1.5s ease;
        }}
        video {{
            width:100%; height:100%; object-fit:cover; object-position:center;
        }}
        .intro-text {{
            position:absolute; bottom:12vh; width:100%;
            text-align:center; font-family:'Special Elite', cursive;
            font-size:clamp(22px,5vw,50px); font-weight:bold; color:white;
            text-shadow:0 0 20px rgba(255,255,255,0.9),0 0 40px rgba(200,220,255,0.6);
            opacity:0;
            animation:fadeInText 3s forwards, fadeOutText 2s 5s forwards;
        }}
        @keyframes fadeInText {{
            0% {{opacity:0; transform:translateY(30px); filter:blur(8px);}}
            100%{{opacity:1; transform:translateY(0); filter:blur(0);}}
        }}
        @keyframes fadeOutText {{
            0%{{opacity:1;}}
            100%{{opacity:0;}}
        }}
        </style>

        <div id="videoDiv">
            <video id="introVideo" autoplay muted playsinline>
                <source src="data:video/mp4;base64,{video_data}" type="video/mp4">
            </video>
            <div class="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        </div>

        <div id="mainContent" style="display:none;">
            <!-- Trang chính sẽ hiện sau video -->
        </div>

        <script>
        const vid = document.getElementById("introVideo");
        vid.onended = () => {{
            const videoDiv = document.getElementById("videoDiv");
            videoDiv.style.opacity = 0;
            setTimeout(()=>{{window.parent.document.getElementById("mainContent").style.display="block";}}, 1500);
        }};
        </script>
        """, unsafe_allow_html=True)
        st.stop()
    else:
        st.error("❌ Không tìm thấy file airplane.mp4")
        st.stop()

# ===== MAIN PAGE =====
if os.path.exists(background_img):
    bg_base64 = process_background(background_img, blur_strength=1.5, brightness=0.85)
else:
    bg_base64 = ""

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Special+Elite&display=swap');
html, body, [data-testid="stAppViewContainer"]{{margin:0;padding:0;height:100vh;}}
.stApp {{
    font-family:'Special Elite', cursive !important;
    background: linear-gradient(rgba(240,230,200,0.45), rgba(240,230,200,0.45)),
                url("data:image/jpeg;base64,{bg_base64}") no-repeat center center fixed;
    background-size:cover;
}}
.stApp::after {{
    content:""; position:fixed; inset:0;
    background: rgba(240,230,200,0.2); backdrop-filter: blur(1.5px);
    pointer-events:none; z-index:-1;
}}
header[data-testid="stHeader"]{{display:none !important;}}
.main-title {{
    font-size:clamp(28px,6vw,54px);
    font-weight:bold; text-align:center; color:#3e2723;
    margin-top:60px; text-shadow:2px 2px 0 #fff,0 0 25px #f0d49b,0 0 50px #bca27a;
}}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📜 TỔ BẢO DƯỠNG SỐ 1</div>', unsafe_allow_html=True)

# ===== BACKGROUND MUSIC =====
try:
    if os.path.exists("background.mp3"):
        with open("background.mp3","rb") as f:
            audio_bytes = f.read()
            audio_base64 = base64.b64encode(audio_bytes).decode()
            st.markdown(f"""
            <div style='position:fixed; top:10px; left:10px; z-index:1000; width:180px;'>
                <audio controls autoplay loop style='width:100%; opacity:0.85;'>
                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                </audio>
            </div>
            """, unsafe_allow_html=True)
except:
    st.warning("⚠️ Không tìm thấy file background.mp3")
