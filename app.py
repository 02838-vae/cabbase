import streamlit as st
import base64
import time
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

# ========== FILE TÀI NGUYÊN ==========
VIDEO_PC = "airplane.mp4"
SFX = "plane_fly.mp3"
SHUTTER_PC = "airplane_shutter.jpg"
BG_PC = "cabbase.jpg"

st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

GRID_SIZE = 8
SHATTER_DURATION = 1.4  # giảm thời gian để liền mạch
BLACKOUT_DELAY = 0.15

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
        background: black !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ========== MÀN INTRO ==========
def intro_screen():
    hide_streamlit_ui()

    # --- đọc file ---
    try:
        with open(VIDEO_PC, "rb") as f:
            video_b64 = base64.b64encode(f.read()).decode()
        with open(SFX, "rb") as a:
            audio_b64 = base64.b64encode(a.read()).decode()
        with open(SHUTTER_PC, "rb") as s:
            shutter_b64 = base64.b64encode(s.read()).decode()
        with open(BG_PC, "rb") as b:
            bg_b64 = base64.b64encode(b.read()).decode()
    except FileNotFoundError as e:
        st.error(f"❌ Thiếu file: {e.filename}")
        st.stop()

    shards_html = "".join([f"<div class='shard' id='s{i}'></div>" for i in range(GRID_SIZE * GRID_SIZE)])
    js_shatter_duration = SHATTER_DURATION * 1000
    js_blackout_delay = BLACKOUT_DELAY * 1000

    html = f"""
    <html>
    <head>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <style>
        html, body {{
            margin: 0; padding: 0;
            width: 100%; height: 100%;
            background: black;
            overflow: hidden;
        }}
        video {{
            position: absolute; top: 0; left: 0;
            width: 100%; height: 100%;
            object-fit: cover;
            background: black;
        }}
        #black-fade {{
            position: absolute; top: 0; left: 0;
            width: 100%; height: 100%;
            background: black; opacity: 1;
            z-index: 99;
            transition: opacity 0.8s ease-in-out;
        }}
        #shatter-overlay {{
            position: absolute; top: 0; left: 0;
            width: 100%; height: 100%;
            display: grid;
            grid-template-columns: repeat({GRID_SIZE}, 1fr);
            grid-template-rows: repeat({GRID_SIZE}, 1fr);
            z-index: 50;
            opacity: 0;
        }}
        .shard {{
            background-image: url("data:image/jpeg;base64,{shutter_b64}");
            background-size: 100vw 100vh;
            transition: transform {SHATTER_DURATION}s cubic-bezier(0.68,-0.55,0.27,1.55), opacity 0.8s ease-in-out;
        }}
    </style>
    </head>
    <body>
        <video id='introVid' autoplay muted playsinline>
            <source src='data:video/mp4;base64,{video_b64}' type='video/mp4'>
        </video>
        <audio id='flySfx'><source src='data:audio/mp3;base64,{audio_b64}' type='audio/mp3'></audio>
        <div id='shatter-overlay'>{shards_html}</div>
        <div id='black-fade'></div>

        <script>
        const GRID = {GRID_SIZE};
        const SHATTER_DUR = {js_shatter_duration};
        const BLACKOUT = {js_blackout_delay};
        const vid = document.getElementById("introVid");
        const audio = document.getElementById("flySfx");
        const shatter = document.getElementById("shatter-overlay");
        const shards = document.querySelectorAll(".shard");
        const black = document.getElementById("black-fade");

        function setupShards() {{
            shards.forEach((shard, i) => {{
                const r = Math.floor(i / GRID);
                const c = i % GRID;
                shard.style.backgroundPosition = `-${{c * (100 / GRID)}}vw -${{r * (100 / GRID)}}vh`;
            }});
        }}
        setupShards();

        function playAudio() {{
            audio.volume = 1.0;
            audio.currentTime = 0;
            audio.play().catch(() => {{console.log("Audio blocked");}});
        }}

        vid.addEventListener("canplay", () => {{
            vid.play().catch(()=>{{}});
            black.style.opacity = 0;
        }});

        document.addEventListener("click", playAudio, {{once:true}});

        vid.addEventListener("play", playAudio);

        function shatterEffect() {{
            shatter.style.opacity = 1;
            shards.forEach(s => {{
                const dx = (Math.random() - 0.5) * 200;
                const dy = (Math.random() - 0.5) * 200;
                const rot = (Math.random() - 0.5) * 360;
                s.style.transform = `translate(${{dx}}vw, ${{dy}}vh) rotate(${{rot}}deg) scale(0.2)`;
                s.style.opacity = 0;
            }});
        }}

        function finishIntro() {{
            shatterEffect();
            setTimeout(() => {{
                black.style.opacity = 1; // màn đen
            }}, SHATTER_DUR - 500);

            // sau khoảng 1s -> gửi tín hiệu sang streamlit
            setTimeout(() => {{
                window.parent.postMessage({{type: "intro_done"}}, "*");
            }}, SHATTER_DUR + 1000);
        }}

        vid.addEventListener("ended", finishIntro);
        setTimeout(finishIntro, 9500); // fallback
        </script>
    </body>
    </html>
    """
    components.html(html, height=800, scrolling=False)

# ========== TRANG CHÍNH ==========
def main_page():
    hide_streamlit_ui()

    # Đọc file ảnh nền
    try:
        with open(BG_PC, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()
        bg_style = f'url("data:image/jpeg;base64,{bg_b64}")'
    except Exception as e:
        st.warning(f"⚠️ Không tìm thấy file nền {BG_PC}, sẽ dùng nền đen.")
        bg_style = "none"

    # CSS nền cinematic + hiệu ứng chữ
    st.markdown(f"""
    <style>
    html, body, .stApp {{
        height: 100vh !important;
        margin: 0; padding: 0;
        overflow: hidden !important;
        background: {bg_style} no-repeat center center fixed;
        background-size: cover;
        background-color: black; /* fallback */
        animation: fadeInBg 1s ease-in-out forwards;
        filter: brightness(1.05) contrast(1.1) saturate(1.08);
    }}
    @keyframes fadeInBg {{
        from {{opacity: 0; transform: scale(1.03);}}
        to {{opacity: 1; transform: scale(1);}}
    }}

    /* lớp overlay nhẹ */
    .stApp::after {{
        content: "";
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: radial-gradient(circle at 50% 60%, rgba(0,0,0,0.25) 0%, rgba(0,0,0,0.6) 80%);
        pointer-events: none;
    }}

    /* tiêu đề chính */
    .welcome {{
        position: absolute;
        top: 8%;
        width: 100%;
        text-align: center;
        font-size: clamp(32px, 5vw, 70px);
        color: #fff5d7;
        font-family: 'Playfair Display', serif;
        text-shadow: 0 0 25px rgba(0,0,0,0.8);
        background: linear-gradient(120deg, #f3e6b4 20%, #fff7d6 40%, #f3e6b4 60%);
        background-size: 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: textLight 10s linear infinite, fadeText 1s ease-in-out forwards;
        letter-spacing: 1.5px;
        z-index: 3;
    }}
    @keyframes textLight {{
        0% {{background-position: 200% 0%;}}
        100% {{background-position: -200% 0%;}}
    }}
    @keyframes fadeText {{
        from {{opacity: 0; transform: scale(0.97);}}
        to {{opacity: 1; transform: scale(1);}}
    }}
    </style>

    <div class="welcome">TỔ BẢO DƯỠNG SỐ 1</div>
    """, unsafe_allow_html=True)


# ========== LUỒNG CHÍNH ==========
hide_streamlit_ui()
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

if not st.session_state.intro_done:
    intro_screen()
    st.markdown("""
    <script>
    window.addEventListener("message", (event) => {
        if (event.data.type === "intro_done") {
            window.parent.location.reload();
        }
    });
    </script>
    """, unsafe_allow_html=True)
    time.sleep(12)
    st.session_state.intro_done = True
    st.rerun()
else:
    main_page()
