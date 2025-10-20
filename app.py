import streamlit as st
import base64
import time
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

# ====================== CẤU HÌNH ======================
st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
PLANE_AUDIO = "plane_fly.mp3"

# ====================== TRẠNG THÁI ======================
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = None


# ====================== ẨN GIAO DIỆN STREAMLIT ======================
def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
    }
    .stApp, .main, .block-container {
        padding: 0 !important;
        margin: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ====================== XÁC ĐỊNH THIẾT BỊ ======================
if st.session_state.is_mobile is None:
    ua_string = st_javascript("window.navigator.userAgent;")
    if ua_string:
        ua = parse(ua_string)
        st.session_state.is_mobile = not ua.is_pc
        st.rerun()
    else:
        st.info("Đang xác định thiết bị...")
        st.stop()


# ====================== MÀN HÌNH INTRO ======================
def intro_screen(is_mobile=False):
    hide_streamlit_ui()

    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    with open(video_file, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()

    with open(PLANE_AUDIO, "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode()

    intro_html = f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
        html, body {{
            margin: 0; padding: 0;
            overflow: hidden;
            background: black;
            height: 100%;
        }}
        video {{
            position: absolute;
            top: 0; left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        #intro-text {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            font-family: 'Playfair Display', serif;
            font-weight: bold;
            font-size: clamp(22px, 6vw, 60px);
            background: linear-gradient(90deg, #fff, #ffcf40, #fca311, #fff);
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
            transition: opacity 1.2s ease-in-out;
        }}
        </style>
    </head>
    <body>
        <video id="introVid" autoplay playsinline muted>
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        <audio id="planeSound">
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="fade"></div>

        <script>
        const vid = document.getElementById('introVid');
        const fade = document.getElementById('fade');
        const audio = document.getElementById('planeSound');

        let ended = false;

        function startPlayback() {{
            vid.muted = false;
            vid.play().then(() => {{
                audio.volume = 0.8;
                audio.play().catch(e => console.log("Audio blocked", e));
            }}).catch(err => {{
                console.log("Autoplay blocked:", err);
                setTimeout(finishIntro, 6000);
            }});
        }}

        function finishIntro() {{
            if (ended) return;
            ended = true;
            fade.style.opacity = 1;
            setTimeout(() => {{
                window.parent.postMessage({{type: "intro_done"}}, "*");
            }}, 1000);
        }}

        vid.addEventListener('play', () => {{
            setTimeout(() => {{
                fade.style.opacity = 1;
                finishIntro();
            }}, 9000);
        }});

        vid.addEventListener('ended', finishIntro);

        window.onload = startPlayback;
        </script>
    </body>
    </html>
    """

    components.html(intro_html, height=800, scrolling=False)


# ====================== TRANG CHÍNH ======================
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC

    try:
        with open(bg, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        bg_b64 = ""

    st.markdown(f"""
    <style>
    html, body {{
        height: 100vh;
        background: url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed;
        background-size: cover;
        margin: 0;
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
        animation: fadeIn 1.5s ease-in-out;
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    </style>
    <div class="welcome">✈️ CHÀO MỪNG ĐẾN VỚI CABBASE ✈️</div>
    """, unsafe_allow_html=True)


# ====================== LUỒNG CHÍNH ======================
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
    time.sleep(9)
    st.session_state.intro_done = True
    st.rerun()
else:
    main_page(st.session_state.is_mobile)
