import streamlit as st
import base64
import time
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

# ===== CẤU HÌNH =====
st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
SFX = "plane_fly.mp3"

# ===== ẨN UI STREAMLIT =====
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

# ===== XÁC ĐỊNH THIẾT BỊ =====
if "is_mobile" not in st.session_state:
    ua_string = st_javascript("window.navigator.userAgent;")
    if ua_string:
        ua = parse(ua_string)
        st.session_state.is_mobile = not ua.is_pc
        st.rerun()
    else:
        st.info("Đang xác định thiết bị...")
        st.stop()

# ===== MÀN HÌNH INTRO =====
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    with open(video_file, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()
    with open(SFX, "rb") as a:
        audio_b64 = base64.b64encode(a.read()).decode()

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
        audio {{ display: none; }}
        #intro-text {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 100vw;
            max-width: 100%;
            padding: 0 5vw;
            text-align: center;
            color: white;
            font-size: clamp(22px, 6vw, 60px);
            font-weight: 700;
            font-family: 'Playfair Display', serif;
            line-height: 1.3;
            text-shadow: 0 0 25px rgba(0,0,0,0.6);
            background: linear-gradient(110deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,1) 50%, rgba(255,255,255,0.1) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-size: 200%;
            animation: fadeInOut 9s ease-in-out forwards, lightSweep 9s linear forwards;
        }}
        @keyframes fadeInOut {{
            0% {{ opacity: 0; }}
            10% {{ opacity: 1; }}
            90% {{ opacity: 1; }}
            100% {{ opacity: 0; }}
        }}
        @keyframes lightSweep {{
            0% {{ background-position: -200% center; }}
            100% {{ background-position: 200% center; }}
        }}
        #fade {{
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: black;
            opacity: 0;
            transition: opacity 1.5s ease-in-out;
        }}
        </style>
    </head>
    <body>
        <video id="introVid" autoplay playsinline muted>
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        <audio id="flySfx">
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="fade"></div>

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
                window.parent.postMessage({{type: "intro_done"}}, "*");
            }}, 1000);
        }}

        // Đảm bảo video tự chạy
        vid.play().catch(err => console.log("Autoplay bị chặn:", err));

        // Phát âm thanh sau khi video bắt đầu 0.5s
        vid.addEventListener('play', () => {{
            setTimeout(() => {{
                audio.volume = 1.0;
                audio.play().catch(()=>{{ console.log("Audio play blocked"); }});
            }}, 500);
        }});

        vid.addEventListener('ended', finishIntro);
        setTimeout(finishIntro, 9500);
        </script>
    </body>
    </html>
    """
    components.html(intro_html, height=800, scrolling=False)

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
        background: url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed !important;
        background-size: cover !important;
        animation: fadeInBg 1.2s ease-in-out forwards;
    }}
    @keyframes fadeInBg {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    .welcome {{
        height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: clamp(28px, 5vw, 60px);
        color: white;
        font-family: 'Playfair Display', serif;
        text-shadow: 0 0 20px rgba(0,0,0,0.7);
        animation: fadeIn 1.5s ease-in-out;
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    </style>

    <div class="welcome">✈️ TỔ BẢO DƯỠNG SỐ 1 ✈️</div>
    """, unsafe_allow_html=True)

# ===== LUỒNG CHÍNH =====
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
    time.sleep(9.5)
    st.session_state.intro_done = True
    st.rerun()
else:
    main_page(st.session_state.is_mobile)
