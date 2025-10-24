import streamlit as st
import base64
import time
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components


# ========== CẤU HÌNH ==========
VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
SFX = "plane_fly.mp3"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"

st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")
GRID_SIZE = 8
SHATTER_DURATION = 1.8
BLACKOUT_DELAY = 0.2


# ========== ẨN GIAO DIỆN STREAMLIT ==========
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
        background: black;
    }
    </style>
    """, unsafe_allow_html=True)


# ========== MÀN HÌNH INTRO ==========
def intro_screen(is_mobile=False):
    hide_streamlit_ui()

    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    bg_file = BG_MOBILE if is_mobile else BG_PC
    
    with open(video_file, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()
    with open(SFX, "rb") as a:
        audio_b64 = base64.b64encode(a.read()).decode()
    with open(bg_file, "rb") as b:
        bg_b64 = base64.b64encode(b.read()).decode()

    shards_html = "".join([f"<div class='shard' id='shard-{i}'></div>" for i in range(GRID_SIZE * GRID_SIZE)])
    js_shatter_duration = SHATTER_DURATION * 1000
    js_blackout_delay = BLACKOUT_DELAY * 1000

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
            z-index: 1;
        }}
        #introText {{
            position: absolute;
            top: 10%;
            width: 100%;
            text-align: center;
            color: #fff5d7;
            font-family: 'Playfair Display', serif;
            font-size: clamp(24px, 4.5vw, 60px);
            text-shadow: 0 0 18px rgba(0,0,0,0.65);
            z-index: 3;
            opacity: 0;
            animation: fadeInText 2s ease-in-out 1s forwards;
        }}
        @keyframes fadeInText {{
            from {{ opacity: 0; transform: scale(0.97); }}
            to {{ opacity: 1; transform: scale(1); }}
        }}
        #shatter-overlay {{
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            display: grid;
            grid-template-columns: repeat({GRID_SIZE}, 1fr);
            grid-template-rows: repeat({GRID_SIZE}, 1fr);
            z-index: 5;
            opacity: 0;
        }}
        .shard {{
            position: relative;
            background-image: url("data:image/jpeg;base64,{bg_b64}");
            background-size: 100vw 100vh;
            transition: transform {SHATTER_DURATION}s cubic-bezier(0.68, -0.55, 0.27, 1.55),
                        opacity 1.2s ease-in-out;
            opacity: 1;
        }}
        #black-fade {{
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: black;
            opacity: 1;
            z-index: 10;
            transition: opacity 1s ease-in-out;
        }}
    </style>
    </head>
    <body>
        <video id='introVid' autoplay muted playsinline>
            <source src='data:video/mp4;base64,{video_b64}' type='video/mp4'>
        </video>
        <div id='introText'>KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <audio id='flySfx'>
            <source src='data:audio/mp3;base64,{audio_b64}' type='audio/mp3'>
        </audio>
        <div id='shatter-overlay'>{shards_html}</div>
        <div id='black-fade'></div>

        <script>
        const GRID_SIZE = {GRID_SIZE};
        const SHATTER_DURATION = {js_shatter_duration};
        const BLACKOUT_DELAY = {js_blackout_delay};

        const vid = document.getElementById('introVid');
        const audio = document.getElementById('flySfx');
        const shatterOverlay = document.getElementById('shatter-overlay');
        const shards = document.querySelectorAll('.shard');
        const blackFade = document.getElementById('black-fade');

        let ended = false;

        let initialTransforms = [];
        shards.forEach((shard, i) => {{
            const row = Math.floor(i / GRID_SIZE);
            const col = i % GRID_SIZE;
            shard.style.backgroundPosition = `calc(-${{col}} * 100vw / ${{GRID_SIZE}}) calc(-${{row}} * 100vh / ${{GRID_SIZE}})`;
            const randX = (Math.random() - 0.5) * 200;
            const randY = (Math.random() - 0.5) * 200;
            const randR = (Math.random() - 0.5) * 360;
            const delay = Math.random() * 0.5;
            initialTransforms.push({{randX, randY, randR, delay}});
        }});

        function finishIntro() {{
            if (ended) return;
            ended = true;

            // Hiệu ứng tan vỡ
            shatterOverlay.style.opacity = 1;
            shards.forEach((shard, i) => {{
                const t = initialTransforms[i];
                shard.style.transform = `translate(${{t.randX}}vw, ${{t.randY}}vh) rotate(${{t.randR}}deg) scale(0.1)`;
                shard.style.transitionDelay = t.delay + 's';
                shard.style.opacity = 0;
            }});

            // Sau khi tan vỡ: fade-in background chính & tiêu đề
            setTimeout(() => {{
                const fadeBg = document.createElement('div');
                fadeBg.style.position = 'absolute';
                fadeBg.style.top = '0';
                fadeBg.style.left = '0';
                fadeBg.style.width = '100%';
                fadeBg.style.height = '100%';
                fadeBg.style.backgroundImage = 'url("data:image/jpeg;base64,{bg_b64}")';
                fadeBg.style.backgroundSize = 'cover';
                fadeBg.style.backgroundPosition = 'center';
                fadeBg.style.opacity = '0';
                fadeBg.style.transition = 'opacity 2.5s ease-in-out';
                fadeBg.style.zIndex = '50';
                document.body.appendChild(fadeBg);

                const title = document.createElement('div');
                title.innerText = 'TỔ BẢO DƯỠNG SỐ 1';
                title.style.position = 'absolute';
                title.style.top = '8%';
                title.style.width = '100%';
                title.style.textAlign = 'center';
                title.style.color = '#fff5d7';
                title.style.fontFamily = "'Playfair Display', serif";
                title.style.fontSize = 'clamp(30px, 5vw, 65px)';
                title.style.textShadow = '0 0 18px rgba(0,0,0,0.65)';
                title.style.opacity = '0';
                title.style.transition = 'opacity 2.5s ease-in-out 0.5s';
                title.style.zIndex = '55';
                document.body.appendChild(title);

                // Fade-in mượt
                setTimeout(() => {{
                    fadeBg.style.opacity = 1;
                    title.style.opacity = 1;
                    blackFade.style.opacity = 0;
                }}, 300);
            }}, SHATTER_DURATION + BLACKOUT_DELAY);
        }}

        vid.addEventListener('canplay', () => {{
            vid.play().catch(()=>{{}});
            blackFade.style.opacity = 0;
        }});
        vid.addEventListener('ended', finishIntro);
        setTimeout(finishIntro, 9000);
        </script>
    </body>
    </html>
    """

    components.html(intro_html, height=800, scrolling=False)


# ========== CHẠY ==========
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

intro_screen(st.session_state.is_mobile)
