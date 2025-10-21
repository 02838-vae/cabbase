import streamlit as st
import base64
import os
import time
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

# ================== CẤU HÌNH CHUNG ==================
st.set_page_config(page_title="Tổ bảo dưỡng số 1", layout="wide")

VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
SOUND = "plane_fly.mp3"

if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = None
if "start_time" not in st.session_state:
    st.session_state.start_time = None


# ================== XÁC ĐỊNH THIẾT BỊ ==================
if st.session_state.is_mobile is None:
    ua_string = st_javascript("""window.navigator.userAgent;""")
    if ua_string:
        user_agent = parse(ua_string)
        st.session_state.is_mobile = not user_agent.is_pc
        st.rerun()
    else:
        st.info("Đang xác định thiết bị...")
        st.stop()


# ================== ẨN GIAO DIỆN STREAMLIT ==================
def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
    }
    .stApp, .main, .block-container {
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ================== MÀN HÌNH INTRO ==================
def intro_screen(is_mobile=False):
    hide_streamlit_ui()

    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    bg_sound = SOUND

    with open(video_file, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()

    with open(bg_sound, "rb") as f:
        sound_b64 = base64.b64encode(f.read()).decode()

    text_bottom = "22%" if is_mobile else "18%"
    text_size = "6vw" if is_mobile else "3vw"

    intro_html = f"""
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
    html, body {{
      margin: 0; padding: 0;
      width: 100vw; height: 100vh;
      background: black; overflow: hidden;
    }}
    video {{
      position: absolute;
      top: 0; left: 0;
      width: 100%; height: 100%;
      object-fit: cover;
    }}
    .text-overlay {{
      position: absolute;
      left: 50%;
      bottom: {text_bottom};
      transform: translateX(-50%);
      font-family: 'Orbitron', sans-serif;
      font-size: {text_size};
      color: white;
      text-shadow: 0 0 30px rgba(255,255,255,0.7);
      background: linear-gradient(90deg, #fff, #0ff, #fff);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-size: 200%;
      animation: lightSweep 5s linear infinite, fadeInOut 9s ease-in-out forwards;
      white-space: nowrap;
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
    .fadeout {{
      animation: fadeToBlack 1.5s forwards;
    }}
    @keyframes fadeToBlack {{
      from {{opacity: 1;}}
      to {{opacity: 0; background-color: black;}}
    }}
    </style>
    </head>
    <body>
      <video id="introVid" autoplay playsinline muted>
        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
      </video>
      <audio id="planeAudio" preload="auto">
        <source src="data:audio/mp3;base64,{sound_b64}" type="audio/mp3">
      </audio>
      <div class="text-overlay">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
      <script>
        const vid = document.getElementById("introVid");
        const audio = document.getElementById("planeAudio");

        vid.addEventListener("play", () => {{
          audio.volume = 1.0;
          audio.play().catch(e => console.log("Autoplay bị chặn:", e));
        }});

        // Khi video kết thúc thì mờ dần và chuyển trang
        vid.onended = () => {{
          document.body.classList.add("fadeout");
          setTimeout(() => {{
            window.parent.postMessage({{"type":"intro_done"}}, "*");
          }}, 1500);
        }};
      </script>
    </body>
    </html>
    """
    components.html(intro_html, height=900, scrolling=False)


# ================== TRANG CHÍNH ==================
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg_file = BG_MOBILE if is_mobile else BG_PC

    if not os.path.exists(bg_file):
        st.error(f"Không tìm thấy background {bg_file}")
        return

    with open(bg_file, "rb") as f:
        bg_b64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .main-bg {{
        background: url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed;
        background-size: cover;
        height: 100vh;
        width: 100%;
    }}
    h1 {{
        text-align: center;
        color: white;
        padding-top: 40vh;
        text-shadow: 0 0 20px rgba(255,255,255,0.8);
        font-family: 'Playfair Display', serif;
    }}
    </style>
    <div class="main-bg">
        <h1>Tổ bảo dưỡng số 1</h1>
    </div>
    """, unsafe_allow_html=True)


# ================== ĐIỀU HƯỚNG ==================
hide_streamlit_ui()

if st.session_state.is_mobile is None:
    st.info("Đang xác định thiết bị...")
elif not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
    st.session_state.intro_done = True
else:
    main_page(st.session_state.is_mobile)
