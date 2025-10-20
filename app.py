import streamlit as st
import base64
import time
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

# ====== ĐƯỜNG DẪN FILE ======
VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
PLANE_AUDIO = "plane_fly.mp3"

# ====== TRẠNG THÁI ======
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = None

# ====== ẨN GIAO DIỆN STREAMLIT ======
def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"] {display:none!important;}
    .stApp, .block-container, .main {padding:0!important;margin:0!important;}
    </style>
    """, unsafe_allow_html=True)

# ====== XÁC ĐỊNH THIẾT BỊ ======
if st.session_state.is_mobile is None:
    ua_string = st_javascript("window.navigator.userAgent;")
    if ua_string:
        ua = parse(ua_string)
        st.session_state.is_mobile = not ua.is_pc
        st.rerun()
    else:
        st.info("Đang xác định thiết bị...")
        st.stop()

# ====== MÀN HÌNH INTRO ======
def intro_screen(is_mobile=False):
    hide_streamlit_ui()

    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    bg_audio = PLANE_AUDIO

    # encode video
    with open(video_file, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()
    # encode audio
    with open(bg_audio, "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode()

    html_code = f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
        html, body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            height: 100%;
            background: black;
        }}
        video {{
            position: absolute;
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        #intro-text {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 95%;
            text-align: center;
            font-size: clamp(20px, 6vw, 60px);
            font-family: 'Playfair Display', serif;
            font-weight: bold;
            background: linear-gradient(90deg, #fff, #ffd166, #fca311, #fff);
            background-size: 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shine 5s linear infinite, fadeInOut 6s ease-in-out forwards;
        }}
        @keyframes shine {{
            0% {{ background-position: 300%; }}
            100% {{ background-position: -300%; }}
        }}
        @keyframes fadeInOut {{
            0% {{ opacity: 0; }}
            15% {{ opacity: 1; }}
            85% {{ opacity: 1; }}
            100% {{ opacity: 0; }}
        }}
        #fade {{
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: black;
            opacity: 0;
            transition: opacity 1s ease-in-out;
        }}
        </style>
    </head>
    <body>
        <video id="vid" autoplay playsinline muted>
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>

        <audio id="audio" preload="auto">
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>

        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="fade"></div>

        <script>
        const vid = document.getElementById('vid');
        const fade = document.getElementById('fade');
        const audio = document.getElementById('audio');

        vid.muted = false;

        vid.addEventListener('play', () => {{
            audio.currentTime = 0;
            audio.volume = 0.9;
            audio.play().catch(e => console.log("Audio blocked:", e));
        }});

        vid.addEventListener('ended', () => {{
            fade.style.opacity = 1;
            setTimeout(() => {{
                window.parent.postMessage({{type: 'intro_done'}}, '*');
            }}, 800);
        }});

        vid.play().catch(() => {{
            console.log('Autoplay blocked');
            window.parent.postMessage({{type: 'intro_done'}}, '*');
        }});
        </script>
    </body>
    </html>
    """

    components.html(html_code, height=800, scrolling=False)

# ====== TRANG CHÍNH ======
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg_file = BG_MOBILE if is_mobile else BG_PC
    with open(bg_file, "rb") as f:
        bg_b64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    html, body {{
        height: 100vh;
        margin: 0;
        background: url("data:image/jpg;base64,{bg_b64}") no-repeat center center fixed;
        background-size: cover;
    }}
    .welcome {{
        height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: clamp(28px, 5vw, 60px);
        color: white;
        font-family: 'Playfair Display', serif;
        text-shadow: 0 0 20px rgba(0,0,0,0.8);
    }}
    </style>
    <div class="welcome">✈️ CHÀO MỪNG ĐẾN VỚI CABBASE ✈️</div>
    """, unsafe_allow_html=True)

# ====== LOGIC CHÍNH ======
hide_streamlit_ui()

if not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
    st.markdown("""
    <script>
    window.addEventListener("message", (event) => {
        if (event.data.type === "intro_done") {
            window.parent.location.reload();
        }
    });
    </script>
    """, unsafe_allow_html=True)
    time.sleep(6)
    st.session_state.intro_done = True
    st.rerun()
else:
    main_page(st.session_state.is_mobile)
