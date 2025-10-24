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
SHUTTER_PC = "airplane_shutter.jpg"
SHUTTER_MOBILE = "mobile_shutter.jpg"

st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

GRID_SIZE = 8
SHATTER_DURATION = 1.8
FADE_TO_BLACK_DELAY = 800  # ms sau khi tan vỡ
MAIN_FADE_IN_DURATION = 3000  # ms


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
    shutter_file = SHUTTER_MOBILE if is_mobile else SHUTTER_PC

    # Encode base64
    def to_b64(file):
        with open(file, "rb") as f:
            return base64.b64encode(f.read()).decode()

    video_b64 = to_b64(video_file)
    audio_b64 = to_b64(SFX)
    bg_b64 = to_b64(bg_file)
    shutter_b64 = to_b64(shutter_file)

    shards_html = "".join([f"<div class='shard' id='s{i}'></div>" for i in range(GRID_SIZE * GRID_SIZE)])

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
            from {{ opacity: 0; transform: scale(0.96); }}
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
            background-image: url("data:image/jpeg;base64,{shutter_b64}");
            background-size: 100vw 100vh;
            transition: transform {SHATTER_DURATION}s cubic-bezier(0.68,-0.55,0.27,1.55), opacity 1.3s ease-in-out;
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
        <video id='vid' autoplay muted playsinline>
            <source src='data:video/mp4;base64,{video_b64}' type='video/mp4'>
        </video>
        <div id='introText'>KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <audio id='sfx'>
            <source src='data:audio/mp3;base64,{audio_b64}' type='audio/mp3'>
        </audio>
        <div id='shatter-overlay'>{shards_html}</div>
        <div id='black-fade'></div>

        <script>
        const GRID_SIZE = {GRID_SIZE};
        const SHATTER_DURATION = {int(SHATTER_DURATION * 1000)};
        const FADE_TO_BLACK_DELAY = {FADE_TO_BLACK_DELAY};
        const MAIN_FADE_IN_DURATION = {MAIN_FADE_IN_DURATION};

        const vid = document.getElementById('vid');
        const sfx = document.getElementById('sfx');
        const shards = document.querySelectorAll('.shard');
        const overlay = document.getElementById('shatter-overlay');
        const blackFade = document.getElementById('black-fade');
        let ended = false;

        // Chuẩn bị các mảnh vỡ
        shards.forEach((s, i) => {{
            const row = Math.floor(i / GRID_SIZE);
            const col = i % GRID_SIZE;
            s.style.backgroundPosition = `calc(-${{col}} * 100vw / ${{GRID_SIZE}}) calc(-${{row}} * 100vh / ${{GRID_SIZE}})`;
        }});

        function startAudio() {{
            sfx.volume = 1;
            sfx.play().catch(()=>{});
        }}

        function finishIntro() {{
            if (ended) return;
            ended = true;

            overlay.style.opacity = 1;
            shards.forEach(s => {{
                const tx = (Math.random() - 0.5) * 200;
                const ty = (Math.random() - 0.5) * 200;
                const tr = (Math.random() - 0.5) * 360;
                const d = Math.random() * 0.4;
                s.style.transitionDelay = d + 's';
                s.style.transform = `translate(${{tx}}vw, ${{ty}}vh) rotate(${{tr}}deg) scale(0.1)`;
                s.style.opacity = 0;
            }});

            // Sau khi tan xong, màn hình đen hoàn toàn
            setTimeout(() => {{
                blackFade.style.opacity = 1;
            }}, SHATTER_DURATION);

            // Sau màn đen, hiện background chính và tiêu đề
            setTimeout(() => {{
                const bg = document.createElement('div');
                bg.style.position = 'absolute';
                bg.style.top = '0';
                bg.style.left = '0';
                bg.style.width = '100%';
                bg.style.height = '100%';
                bg.style.backgroundImage = 'url("data:image/jpeg;base64,{bg_b64}")';
                bg.style.backgroundSize = 'cover';
                bg.style.backgroundPosition = 'center';
                bg.style.opacity = '0';
                bg.style.transition = `opacity ${{MAIN_FADE_IN_DURATION}}ms ease-in-out`;
                bg.style.zIndex = '50';
                document.body.appendChild(bg);

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
                title.style.transition = `opacity ${{MAIN_FADE_IN_DURATION}}ms ease-in-out 0.5s`;
                title.style.zIndex = '55';
                document.body.appendChild(title);

                setTimeout(() => {{
                    bg.style.opacity = 1;
                    title.style.opacity = 1;
                    blackFade.style.opacity = 0;
                }}, 100);
            }}, SHATTER_DURATION + FADE_TO_BLACK_DELAY + 200);
        }}

        // Khi video sẵn sàng → bắt đầu video và âm thanh
        vid.addEventListener('canplay', () => {{
            vid.play().catch(()=>{{}});
            startAudio();
            blackFade.style.opacity = 0;
        }});

        // Khi video kết thúc
        vid.addEventListener('ended', finishIntro);

        // Trường hợp video lỗi hoặc timeout
        setTimeout(finishIntro, 12000);
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
