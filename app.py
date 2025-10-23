import streamlit as st
import base64
import time
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

# ========== CẤU HÌNH VÀ TÀI NGUYÊN ==========
VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
SFX = "plane_fly.mp3"

SHUTTER_PC = "airplane_shutter.jpg"
SHUTTER_MOBILE = "mobile_shutter.jpg"

BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"

st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

GRID_SIZE = 8
SHATTER_DURATION = 1.8
BLACKOUT_DELAY = 0.2


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


# ========== MÀN HÌNH INTRO ==========
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
        st.error(f"Lỗi: Không tìm thấy file tài nguyên: {e.filename}")
        st.stop()

    shards_html = "".join([f"<div class='shard' id='shard-{i}'></div>" for i in range(GRID_SIZE * GRID_SIZE)])

    js_shatter_duration = SHATTER_DURATION * 1000
    js_blackout_delay = BLACKOUT_DELAY * 1000

    intro_html = f"""
    <html>
    <head>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <style>
        html, body {{
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
            background: black !important;
            width: 100vw !important;
            height: 100vh !important;
        }}

        video {{
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            object-fit: cover !important;
            background: black !important;
        }}

        #static-frame {{
            position: absolute; top: 0; left: 0;
            width: 100%; height: 100%;
            background-image: url("data:image/jpeg;base64,{shutter_b64}");
            background-size: cover;
            opacity: 0;
            z-index: 20;
            transition: opacity 0.1s linear;
        }}

        audio {{ display: none; }}

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

        #shatter-overlay {{
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            display: grid;
            grid-template-columns: repeat({GRID_SIZE}, 1fr);
            grid-template-rows: repeat({GRID_SIZE}, 1fr);
            opacity: 0;
            pointer-events: none;
            z-index: 30;
        }}

        .shard {{
            position: relative;
            background-image: url("data:image/jpeg;base64,{shutter_b64}");
            background-size: 100vw 100vh;
            transition: transform {SHATTER_DURATION}s cubic-bezier(0.68, -0.55, 0.27, 1.55),
                        opacity 1.5s ease-in-out;
            opacity: 1;
        }}

        #black-fade {{
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: black;
            opacity: 1;
            z-index: 40;
            transition: opacity 1s ease-in-out;
            pointer-events: none;
        }}
        </style>
    </head>
    <body>
        <video id='introVid' autoplay muted playsinline>
            <source src='data:video/mp4;base64,{video_b64}' type='video/mp4'>
        </video>
        <div id='static-frame'></div>
        <audio id='flySfx'><source src='data:audio/mp3;base64,{audio_b64}' type='audio/mp3'></audio>
        <div id='intro-text'>KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id='shatter-overlay'>{shards_html}</div>
        <div id='black-fade'></div>

        <script>
        const GRID_SIZE = {GRID_SIZE};
        const SHATTER_DURATION = {js_shatter_duration};
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
            shard.style.backgroundPosition =
                'calc(-' + col + ' * 100vw / ' + GRID_SIZE + ') calc(-' + row + ' * 100vh / ' + GRID_SIZE + ')';
            const randX = (Math.random() - 0.5) * 200;
            const randY = (Math.random() - 0.5) * 200;
            const randR = (Math.random() - 0.5) * 360;
            const delay = Math.random() * 0.5;
            initialTransforms.push({{randX, randY, randR, delay}});
        }});

        function finishIntro() {{
            if (ended) return;
            ended = true;
            vid.style.opacity = 0;
            staticFrame.style.opacity = 1;

            setTimeout(() => {{
                blackFade.style.opacity = 0;
                shatterOverlay.style.opacity = 1;
                staticFrame.style.opacity = 0;
                shards.forEach((shard, index) => {{
                    const t = initialTransforms[index];
                    shard.style.transform = 'translate(' + t.randX + 'vw, ' + t.randY + 'vh) rotate(' + t.randR + 'deg) scale(0.1)';
                    shard.style.transitionDelay = t.delay + 's';
                    shard.style.opacity = 0;
                }});
            }}, 10);

            setTimeout(() => {{
                blackFade.style.transition = "opacity 2s ease-in-out";
                blackFade.style.opacity = 1;
                setTimeout(() => {{
                    window.parent.postMessage({{type: 'intro_done'}}, '*');
                }}, 2000);
            }}, SHATTER_DURATION + BLACKOUT_DELAY);
        }}

        vid.addEventListener('canplay', () => {{
            vid.play().catch(() => console.log('Autoplay bị chặn'));
            blackFade.style.opacity = 0;
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
            blackFade.style.opacity = 0;
        }}, {{once:true}});

        vid.addEventListener('ended', finishIntro);
        setTimeout(finishIntro, 9000);
        blackFade.style.opacity = 1;
        </script>
    </body>
    </html>
    """
    components.html(intro_html, height=900, scrolling=False)


# ========== TRANG CHÍNH ==========
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    try:
        with open(bg, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError as e:
        st.error(f"Lỗi: Không tìm thấy file tài nguyên: {e.filename}")
        st.stop()

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
        animation: cinematicReveal 2.5s ease-out forwards;
        transform-origin: center;
    }}
    @keyframes cinematicReveal {{
        0% {{ opacity: 0; transform: scale(1.05); filter: blur(8px); }}
        50% {{ opacity: 1; transform: scale(1.02); filter: blur(2px); }}
        100% {{ opacity: 1; transform: scale(1.0); filter: blur(0px); }}
    }}
    </style>

    <div class="welcome">TỔ BẢO DƯỠNG SỐ 1</div>
    """, unsafe_allow_html=True)


# ========== LUỒNG CHÍNH ==========
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
