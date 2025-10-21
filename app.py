import streamlit as st
import base64
from streamlit.components.v1 import html

st.set_page_config(page_title="Tổ bảo dưỡng số 1", layout="wide", page_icon="✈️")

# Ẩn header, footer, menu của Streamlit
st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        .stApp {margin: 0; padding: 0; overflow: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==== XÁC ĐỊNH THIẾT BỊ ====
# Dựa vào width của màn hình (Streamlit cung cấp qua session state)
# Không dùng query_params hay request headers để tránh lỗi
is_mobile = st.session_state.get("is_mobile", None)
if is_mobile is None:
    html("""
    <script>
    const isMobile = /Mobi|Android/i.test(navigator.userAgent);
    window.parent.postMessage({is_mobile: isMobile}, "*");
    </script>
    """, height=0)
    st.stop()

if not isinstance(is_mobile, bool):
    is_mobile = False

# ==== CHỌN VIDEO VÀ BACKGROUND ====
if is_mobile:
    video_file = "mobile.mp4"
    background_file = "mobile.jpg"
else:
    video_file = "airplane.mp4"
    background_file = "cabbase.jpg"

# ==== NẠP VIDEO & ÂM THANH ====
with open(video_file, "rb") as f:
    video_b64 = base64.b64encode(f.read()).decode()
with open("plane_fly.mp3", "rb") as f:
    audio_b64 = base64.b64encode(f.read()).decode()

# ==== HTML INTRO ====
intro_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
html, body {{
  margin: 0; padding: 0; width: 100%; height: 100%;
  overflow: hidden; background: black;
}}
video {{
  width: 100%; height: 100%; object-fit: cover;
}}
.text-overlay {{
  position: absolute;
  top: 55%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-family: 'Orbitron', sans-serif;
  font-size: 6vw;
  color: white;
  text-shadow: 0 0 30px rgba(255,255,255,0.7);
  white-space: nowrap;
  background: linear-gradient(90deg, #fff, #0ff, #fff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-size: 200%;
  animation: lightSweep 5s linear infinite, fadeInOut 9s ease-in-out forwards;
}}
@keyframes fadeInOut {{
  0% {{opacity: 0;}}
  10% {{opacity: 1;}}
  80% {{opacity: 1;}}
  100% {{opacity: 0;}}
}}
@keyframes lightSweep {{
  0% {{background-position: -200% 0;}}
  100% {{background-position: 200% 0;}}
}}
.fade-out {{
  animation: fadeToBlack 2s forwards;
}}
@keyframes fadeToBlack {{
  from {{opacity: 1;}}
  to {{opacity: 0;}}
}}
</style>
</head>
<body>
  <video id="introVid" autoplay playsinline muted>
    <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
  </video>
  <audio id="planeAudio" preload="auto">
    <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
  </audio>
  <div class="text-overlay">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
  <script>
    const vid = document.getElementById("introVid");
    const audio = document.getElementById("planeAudio");

    vid.addEventListener("play", () => {{
      audio.volume = 1.0;
      audio.play().catch(err => console.log("Autoplay blocked", err));
    }});

    setTimeout(() => {{
      document.body.classList.add("fade-out");
      setTimeout(() => {{
        window.parent.postMessage("show_main", "*");
      }}, 2000);
    }}, 9000);
  </script>
</body>
</html>
"""

# ==== QUẢN LÝ GIAO DIỆN ====
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

if not st.session_state.intro_done:
    html(intro_html, height=800)
    st.session_state.intro_done = True
else:
    # ==== TRANG CHÍNH ====
    with open(background_file, "rb") as f:
        bg_b64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .main-bg {{
        background-image: url("data:image/jpg;base64,{bg_b64}");
        background-size: cover;
        background-position: center;
        height: 100vh;
        width: 100%;
    }}
    h1 {{
        color: white;
        text-align: center;
        padding-top: 40vh;
        text-shadow: 0 0 20px rgba(255,255,255,0.8);
        font-size: 3rem;
    }}
    </style>
    <div class="main-bg">
        <h1>Tổ bảo dưỡng số 1</h1>
        <audio controls autoplay loop>
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>
    </div>
    """, unsafe_allow_html=True)
