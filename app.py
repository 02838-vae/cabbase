import streamlit as st
import base64
import time
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

# ========== CẤU HÌNH ==========
st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
SFX = "plane_fly.mp3"

# ========== ẨN UI STREAMLIT ==========
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

# ========== XÁC ĐỊNH THIẾT BỊ ==========
if "is_mobile" not in st.session_state:
    ua_string = st_javascript("window.navigator.userAgent;")
    if ua_string:
        ua = parse(ua_string)
        st.session_state.is_mobile = not ua.is_pc
        st.rerun()
    else:
        st.info("Đang xác định thiết bị...")
        st.stop()

# ========== MÀN HÌNH INTRO ==========
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    with open(video_file, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()
    with open(SFX, "rb") as a:
        audio_b64 = base64.b64encode(a.read()).decode()

    # chữ cao hơn trên PC
    top_pos = "20%" if not is_mobile else "50%"

    intro_html = f"""
    <html>
    <head>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <style>
        html, body {{
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            overflow: hidden;
            background: black;
        }}
        video {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: center center;
            background-color: black;
            z-index: -1;
        }}
        audio {{ display: none; }}
        #intro-text {{
            position: absolute;
            top: {top_pos};
            left: 50%;
            transform: translate(-50%, -50%);
            width: 90vw;
            text-align: center;
            font-family: 'Playfair Display', serif;
            font-weight: bold;
            font-size: clamp(22px, 6vw, 60px);
            color: #f8f4e3;
            background: linear-gradient(120deg, #e9dcb5 20%, #fff9e8 40%, #e9dcb5 60%);
            background-size: 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 12px rgba(255,255,220,0.3);
            animation: lightSweep 6s linear infinite, fadeInOut 6s ease-in-out forwards;
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
        #fade {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: black;
            opacity: 0;
            transition: opacity 1.5s ease-in-out;
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
        <div id='fade'></div>
        <script>
        const vid = document.getElementById('introVid');
        const audio = document.getElementById('flySfx');
        const fade = document.getElementById('fade');
        let ended = false;

        function finishIntro() {{
            if (ended) return;
            ended = true;
            fade.style.opacity = 1;
            setTimeout(() => {{
                window.parent.postMessage({{type: 'intro_done'}}, '*');
            }}, 1000);
        }}

        vid.addEventListener('canplay', () => {{
            vid.play().catch(() => console.log('Autoplay bị chặn'));
        }});
        vid.addEventListener('play', () => {{
            audio.volume = 1.0;
            audio.currentTime = 0;
            audio.play().catch(() => console.log('Autoplay âm thanh bị chặn'));
        }});
        document.addEventListener('click', () => {{
            vid.muted = false;
            vid.play();
            audio.volume = 1.0;
            audio.currentTime = 0;
            audio.play().catch(()=>{{}});
        }}, {{once:true}});
        vid.addEventListener('ended', finishIntro);
        setTimeout(finishIntro, 9000);
        </script>
    </body>
    </html>
    """
    components.html(intro_html, height=900, scrolling=False)

# ========== TRANG CHÍNH ==========
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    with open(bg, "rb") as f:
        bg_b64 = base64.b64encode(f.read()).decode()

    # Vintage dịu nhẹ
    st.markdown(f"""
    <style>
    html, body, .stApp {{
        height: 100vh !important;
        background:
            linear-gradient(to bottom, rgba(230, 210, 180, 0.25), rgba(160, 130, 90, 0.35), rgba(90, 70, 50, 0.45)),
            url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed !important;
        background-size: cover !important;
        filter: brightness(0.98) contrast(1.05) saturate(0.95) sepia(0.1);
        position: relative;
        overflow: hidden !important;
    }}
    .stApp::after {{
        content: "";
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-image: url("https://www.transparenttextures.com/patterns/paper-fibers.png");
        opacity: 0.08;
        mix-blend-mode: multiply;
        pointer-events: none;
    }}
    .welcome {{
        position: absolute;
        top: 8%;
        width: 100%;
        text-align: center;
        font-size: clamp(30px, 5vw, 65px);
        font-family: 'Playfair Display', serif;
        text-shadow: 0 0 20px rgba(0,0,0,0.55);
        background: linear-gradient(270deg, #ffe9b0, #f5c67f, #f1dba3, #fff3c7);
        background-size: 600% 600%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 7s ease infinite, fadeIn 2s ease-in-out forwards;
        letter-spacing: 2.5px;
        z-index: 3;
    }}
    @keyframes gradientShift {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: scale(0.97); }}
        to {{ opacity: 1; transform: scale(1); }}
    }}
    </style>

    <div class="welcome">TỔ BẢO DƯỠNG SỐ 1</div>
    """, unsafe_allow_html=True)

# ========== LUỒNG CHÍNH ==========
hide_streamlit_ui()
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
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
