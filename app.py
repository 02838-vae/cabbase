import streamlit as st
import base64
import time
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

# ==========================
# CẤU HÌNH FILE
# ==========================
VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
SFX = "plane_fly.mp3"

SHUTTER_PC = "airplane_shutter.jpg"
SHUTTER_MOBILE = "mobile_shutter.jpg"

BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"

# ==========================
# CẤU HÌNH HIỆU ỨNG
# ==========================
GRID_SIZE = 8
SHATTER_DURATION = 1.8
RECONSTRUCT_DURATION = 1.8
BLACKOUT_DELAY = 0.2

st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")


def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live], [data-testid="stSidebar"] {
        display: none !important;
    }
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"], .block-container {
        margin: 0 !important;
        padding: 0 !important;
        height: 100vh !important;
        width: 100vw !important;
        overflow: hidden !important;
        background: black !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ==========================
# MÀN HÌNH INTRO
# ==========================
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    shutter_file = SHUTTER_MOBILE if is_mobile else SHUTTER_PC
    bg_file = BG_MOBILE if is_mobile else BG_PC

    try:
        with open(video_file, "rb") as f:
            video_b64 = base64.b64encode(f.read()).decode()
        with open(SFX, "rb") as a:
            audio_b64 = base64.b64encode(a.read()).decode()
        with open(shutter_file, "rb") as s:
            shutter_b64 = base64.b64encode(s.read()).decode()
        with open(bg_file, "rb") as b:
            bg_b64 = base64.b64encode(b.read()).decode()
    except FileNotFoundError as e:
        st.error(f"Lỗi: Không tìm thấy file {e.filename}")
        st.stop()

    shards_html = "".join([f"<div class='shard' id='shard-{i}'></div>" for i in range(GRID_SIZE ** 2)])
    js_shatter_duration = SHATTER_DURATION * 1000
    js_reconstruct_duration = RECONSTRUCT_DURATION * 1000
    js_blackout_delay = BLACKOUT_DELAY * 1000

    intro_html = f"""
    <html>
    <head>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <style>
        html, body {{
            margin: 0; padding: 0;
            width: 100vw; height: 100vh;
            overflow: hidden; background: black;
        }}
        video {{
            position: fixed; top: 0; left: 0;
            width: 100vw; height: 100vh;
            object-fit: cover;
            margin: 0; padding: 0;
        }}
        #intro-text {{
            position: fixed;
            top: 8%;
            left: 50%;
            transform: translateX(-50%);
            white-space: nowrap;
            font-size: clamp(26px, 6vw, 60px);
            color: #f8f4e3;
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
        #static-frame {{
            position: fixed; top: 0; left: 0;
            width: 100vw; height: 100vh;
            background-image: url("data:image/jpeg;base64,{shutter_b64}");
            background-size: cover;
            background-position: center;
            opacity: 0;
            z-index: 20;
            transition: opacity 0.2s linear;
        }}
        #shatter-overlay {{
            position: fixed; top: 0; left: 0;
            width: 100vw; height: 100vh;
            display: grid;
            grid-template-columns: repeat({GRID_SIZE}, 1fr);
            grid-template-rows: repeat({GRID_SIZE}, 1fr);
            opacity: 0; pointer-events: none;
            z-index: 30;
        }}
        .shard {{
            background-image: url("data:image/jpeg;base64,{shutter_b64}");
            background-size: 100vw 100vh;
            transition: transform {SHATTER_DURATION}s ease-in-out, opacity 1.2s ease-in-out;
        }}
        .reconstructing .shard {{
            background-image: url("data:image/jpeg;base64,{bg_b64}") !important;
            transform: none !important;
            opacity: 1 !important;
        }}
        #black-fade {{
            position: fixed; top: 0; left: 0;
            width: 100vw; height: 100vh;
            background: black; opacity: 1;
            transition: opacity 1s ease-in-out;
            z-index: 50;
        }}
        </style>
    </head>
    <body>
        <video id='introVid' autoplay muted playsinline>
            <source src='data:video/mp4;base64,{video_b64}' type='video/mp4'>
        </video>
        <div id='intro-text'>KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <audio id='flySfx'><source src='data:audio/mp3;base64,{audio_b64}' type='audio/mp3'></audio>
        <div id='static-frame'></div>
        <div id='shatter-overlay'>{shards_html}</div>
        <div id='black-fade'></div>

        <script>
        const GRID_SIZE = {GRID_SIZE};
        const SHATTER_DURATION = {js_shatter_duration};
        const RECONSTRUCT_DURATION = {js_reconstruct_duration};
        const BLACKOUT_DELAY = {js_blackout_delay};
        const vid = document.getElementById('introVid');
        const audio = document.getElementById('flySfx');
        const staticFrame = document.getElementById('static-frame');
        const shatterOverlay = document.getElementById('shatter-overlay');
        const shards = document.querySelectorAll('.shard');
        const blackFade = document.getElementById('black-fade');

        let ended = false;
        let initialTransforms = [];
        shards.forEach((shard, index) => {{
            const row = Math.floor(index / GRID_SIZE);
            const col = index % GRID_SIZE;
            shard.style.backgroundPosition = `calc(-${{col}} * 100vw / ${GRID_SIZE}) calc(-${{row}} * 100vh / ${GRID_SIZE})`;
            const randX = (Math.random() - 0.5) * 200;
            const randY = (Math.random() - 0.5) * 200;
            const randR = (Math.random() - 0.5) * 360;
            initialTransforms.push({{randX, randY, randR}});
        }});

        function finishIntro() {{
            if (ended) return;
            ended = true;
            vid.style.opacity = 0;
            staticFrame.style.opacity = 1;
            setTimeout(() => {{
                shatterOverlay.style.opacity = 1;
                staticFrame.style.opacity = 0;
                shards.forEach((shard, i) => {{
                    const t = initialTransforms[i];
                    shard.style.transform = `translate(${{t.randX}}vw, ${{t.randY}}vh) rotate(${{t.randR}}deg) scale(0.1)`;
                    shard.style.opacity = 0;
                }});
            }}, 200);
            setTimeout(() => {{
                shatterOverlay.classList.add('reconstructing');
                shards.forEach(s => s.style.opacity = 1);
            }}, SHATTER_DURATION + BLACKOUT_DELAY);
            setTimeout(() => {{
                window.parent.postMessage({{type: 'intro_done'}}, '*');
            }}, SHATTER_DURATION + RECONSTRUCT_DURATION + 400);
        }}
        vid.addEventListener('canplay', () => {{blackFade.style.opacity = 0;}});
        vid.addEventListener('play', () => {{
            audio.volume = 1.0;
            audio.play().catch(()=>{{}});
        }});
        document.addEventListener('click', () => {{
            vid.muted = false;
            vid.play(); audio.play().catch(()=>{{}});
            blackFade.style.opacity = 0;
        }}, {{once:true}});
        vid.addEventListener('ended', finishIntro);
        setTimeout(finishIntro, 10000);
        </script>
    </body>
    </html>
    """
    components.html(intro_html, height=800, scrolling=False)


# ==========================
# TRANG CHÍNH
# ==========================
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    with open(bg, "rb") as f:
        bg_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
    <style>
    html, body, .stApp {{
        height: 100vh !important;
        background: url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed;
        background-size: cover !important;
        margin: 0; padding: 0; overflow: hidden;
    }}
    .welcome {{
        position: fixed; top: 8%; width: 100%;
        text-align: center;
        font-size: clamp(30px, 5vw, 65px);
        font-family: 'Playfair Display', serif;
        background: linear-gradient(120deg, #f3e6b4 20%, #fff7d6 40%, #f3e6b4 60%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 18px rgba(0,0,0,0.65);
    }}
    </style>
    <div class="welcome">TỔ BẢO DƯỠNG SỐ 1</div>
    """, unsafe_allow_html=True)


# ==========================
# LUỒNG CHÍNH
# ==========================
hide_streamlit_ui()
if "is_mobile" not in st.session_state:
    ua_string = st_javascript("window.navigator.userAgent;")
    if ua_string:
        ua = parse(ua_string)
        st.session_state.is_mobile = not ua.is_pc
        st.rerun()
    else:
        st.info("Đang xác định thiết bị...")
        time.sleep(1)
        st.stop()

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
    time.sleep(15)
    st.session_state.intro_done = True
    st.rerun()
else:
    main_page(st.session_state.is_mobile)
