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

    intro_html = f"""
    <html>
    <head>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <style>
        html, body {{
            margin: 0; padding: 0; border: 0;
            overflow: hidden;
            width: 100vw; height: 100vh;
            background: black;
        }}
        video {{
            position: fixed;
            top: 0; left: 0;
            width: 100vw;
            height: 100vh;
            object-fit: cover;
            z-index: 1;
        }}
        audio {{ display: none; }}
        #intro-text {{
            position: absolute;
            top: 12%;
            left: 50%;
            transform: translateX(-50%);
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
            z-index: 2;
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

        /* --- SHUTTER EFFECT --- */
        #left-shutter, #right-shutter {{
            position: fixed;
            top: 0;
            width: 50vw;
            height: 100vh;
            background: black;
            z-index: 3;
            transition: all 1s ease-in-out;
        }}
        #left-shutter {{ left: -50vw; }}
        #right-shutter {{ right: -50vw; }}
        .shutter-close #left-shutter {{ left: 0; }}
        .shutter-close #right-shutter {{ right: 0; }}
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

        <div id='left-shutter'></div>
        <div id='right-shutter'></div>

        <script>
        const vid = document.getElementById('introVid');
        const audio = document.getElementById('flySfx');
        let ended = false;

        function finishIntro() {{
            if (ended) return;
            ended = true;
            document.body.classList.add('shutter-close');
            setTimeout(() => {{
                window.parent.postMessage({{type: 'intro_done_internal'}}, '*');
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

    components.html(intro_html, height=1080, scrolling=False)


# ========== TRANG CHÍNH ==========
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
            linear-gradient(to bottom, rgba(255, 235, 200, 0.25) 0%, rgba(160, 130, 90, 0.35) 50%, rgba(90, 70, 50, 0.5) 100%),
            url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed !important;
        background-size: cover !important;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
        position: relative;
        filter: brightness(1.05) contrast(1.1) saturate(1.05);
    }}
    .welcome {{
        position: absolute;
        top: 8%;
        width: 100%;
        text-align: center;
        font-size: clamp(30px, 5vw, 65px);
        color: #fff5d7;
        font-family: 'Playfair Display', serif;
        text-shadow: 0 0 18px rgba(0,0,0,0.65), 0 0 30px rgba(255,255,180,0.25);
        background: linear-gradient(120deg, #f3e6b4 20%, #fff7d6 40%, #f3e6b4 60%);
        background-size: 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: textLight 10s linear infinite, fadeIn 2s ease-in-out forwards;
    }}
    @keyframes textLight {{
        0% {{ background-position: 200% 0%; }}
        100% {{ background-position: -200% 0%; }}
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: scale(0.97); }}
        to {{ opacity: 1; transform: scale(1); }}
    }}

    /* Shutter open animation */
    #left-shutter, #right-shutter {{
        position: fixed;
        top: 0;
        width: 50vw;
        height: 100vh;
        background: black;
        z-index: 10;
        transition: all 1.2s ease-in-out;
    }}
    #left-shutter {{ left: 0; }}
    #right-shutter {{ right: 0; }}
    body.open-shutter #left-shutter {{ left: -50vw; }}
    body.open-shutter #right-shutter {{ right: -50vw; }}
    </style>

    <div id="left-shutter"></div>
    <div id="right-shutter"></div>
    <div class="welcome">TỔ BẢO DƯỠNG SỐ 1</div>

    <script>
    setTimeout(() => {{
        document.body.classList.add('open-shutter');
    }}, 100);
    </script>
    """, unsafe_allow_html=True)


# ========== LUỒNG CHÍNH ==========
hide_streamlit_ui()
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

# Lắng nghe tín hiệu từ intro mà KHÔNG reload toàn trang
st.markdown("""
<script>
window.addEventListener("message", (event) => {
    if (event.data.type === "intro_done_internal") {
        const iframe = window.frameElement;
        if (iframe) {
            iframe.contentWindow.postMessage({ type: "streamlit_rerun" }, "*");
        }
        window.parent.postMessage({ type: "streamlit_rerun" }, "*");
    }
});
</script>
""", unsafe_allow_html=True)

if not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
    # Giữ lại DOM, không reload
    time.sleep(9)
    st.session_state.intro_done = True
    st.rerun()
else:
    main_page(st.session_state.is_mobile)
