import streamlit as st
import base64
import time
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

# ===== CẤU HÌNH =====
VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
SFX = "plane_fly.mp3"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"

st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

# ===== ẨN GIAO DIỆN STREAMLIT =====
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
        overflow: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ===== MÀN HÌNH INTRO =====
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    try:
        with open(video_file, "rb") as f:
            video_b64 = base64.b64encode(f.read()).decode()
        with open(SFX, "rb") as a:
            audio_b64 = base64.b64encode(a.read()).decode()
    except FileNotFoundError as e:
        st.error(f"Lỗi: Thiếu file tài nguyên — {e.filename}")
        st.stop()

    intro_html = f"""
    <html>
    <head>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
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
            width: 100%; height: 100%;
            object-fit: cover;
        }}
        #intro-text {{
            position: absolute;
            top: 8%;
            left: 50%;
            transform: translate(-50%, 0);
            width: 90vw;
            text-align: center;
            color: #f8f4e3;
            font-size: clamp(22px, 6vw, 60px);
            font-weight: bold;
            font-family: 'Playfair Display', serif;
            background: linear-gradient(120deg, #e9dcb5 20%, #fff9e8 40%, #e9dcb5 60%);
            background-size: 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 15px rgba(255,255,230,0.4);
            animation: lightSweep 6s linear infinite, fadeInOut 6s ease-in-out forwards;
            z-index: 10;
        }}
        @keyframes lightSweep {{
            0% {{ background-position: 200% 0%; }}
            100% {{ background-position: -200% 0%; }}
        }}
        @keyframes fadeInOut {{
            0% {{ opacity: 0; }}
            20% {{ opacity: 1; }}
            80% {{ opacity: 1; }}
            100% {{ opacity: 0; }}
        }}
        </style>
    </head>
    <body>
        <video id='introVid' autoplay muted playsinline>
            <source src='data:video/mp4;base64,{video_b64}' type='video/mp4'>
        </video>
        <audio id='flySfx'>
            <source src='data:audio/mp3;base64,{audio_b64}' type='audio/mp3'>
        </audio>
        <div id='intro-text'>KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>

        <script>
        const vid = document.getElementById('introVid');
        const audio = document.getElementById('flySfx');
        let ended = false;

        function finishIntro() {{
            if (ended) return;
            ended = true;
            window.parent.postMessage({{ type: 'intro_done' }}, '*');
        }}

        vid.addEventListener('canplay', () => vid.play().catch(()=>{{}}));
        vid.addEventListener('play', () => {{
            audio.volume = 1.0;
            audio.currentTime = 0;
            audio.play().catch(()=>{{}});
        }});

        document.addEventListener('click', () => {{
            vid.muted = false;
            vid.play();
            audio.play().catch(()=>{{}});
        }}, {{ once: true }});

        vid.addEventListener('ended', finishIntro);
        </script>
    </body>
    </html>
    """
    components.html(intro_html, height=800, scrolling=False)

    # 👇 Thêm listener riêng biệt để Streamlit nhận message ngay lập tức
    msg = st_javascript("""
    new Promise((resolve) => {
        window.addEventListener("message", (event) => {
            if (event.data.type === "intro_done") resolve(true);
        });
    });
    """)
    return msg


# ===== TRANG CHÍNH =====
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    with open(bg, "rb") as f:
        bg_b64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    html, body, .stApp {{
        height: 100vh !important;
        background:
            linear-gradient(to bottom, rgba(255, 235, 200, 0.25), rgba(90, 70, 50, 0.5)),
            url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed !important;
        background-size: cover !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        animation: fadeIn 0.3s ease-in-out forwards;
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    .welcome {{
        position: absolute;
        top: 8%;
        width: 100%;
        text-align: center;
        font-size: clamp(30px, 5vw, 65px);
        color: #fff5d7;
        font-family: 'Playfair Display', serif;
        text-shadow: 0 0 18px rgba(0,0,0,0.65);
        background: linear-gradient(120deg, #f3e6b4 20%, #fff7d6 40%, #f3e6b4 60%);
        background-size: 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: textLight 10s linear infinite;
        z-index: 3;
    }}
    @keyframes textLight {{
        0% {{ background-position: 200% 0%; }}
        100% {{ background-position: -200% 0%; }}
    }}
    </style>
    <div class="welcome">TỔ BẢO DƯỠNG SỐ 1</div>
    """, unsafe_allow_html=True)


# ===== LUỒNG CHÍNH =====
hide_streamlit_ui()

if "is_mobile" not in st.session_state:
    ua = parse(st_javascript("window.navigator.userAgent;"))
    st.session_state.is_mobile = not ua.is_pc
    st.rerun()

if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

if not st.session_state.intro_done:
    msg = intro_screen(st.session_state.is_mobile)
    if msg:
        st.session_state.intro_done = True
        st.rerun()
else:
    main_page(st.session_state.is_mobile)
