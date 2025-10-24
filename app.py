import streamlit as st
import base64
import time
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

# ==========================
# FILE CẤU HÌNH
# ==========================
VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
SFX = "plane_fly.mp3"

SHUTTER_PC = "airplane_shutter.jpg"
SHUTTER_MOBILE = "mobile_shutter.jpg"

BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"

# ==========================
# CẤU HÌNH GIAO DIỆN
# ==========================
st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live], [data-testid="stSidebar"] {
        display: none !important;
    }
    html, body, .stApp, [data-testid="stAppViewContainer"], .block-container {
        margin: 0 !important;
        padding: 0 !important;
        height: 100vh !important;
        width: 100vw !important;
        overflow: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================
# MÀN HÌNH INTRO (CÓ HIỆU ỨNG GSAP)
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
            transition: opacity 0.4s ease-in-out;
        }}
        #brokenGlassCanvas {{
            position: fixed;
            top: 0; left: 0;
            width: 100vw; height: 100vh;
            z-index: 30;
            opacity: 0;
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
        <canvas id="brokenGlassCanvas"></canvas>
        <div id='black-fade'></div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>

        <script>
        const vid = document.getElementById('introVid');
        const audio = document.getElementById('flySfx');
        const staticFrame = document.getElementById('static-frame');
        const canvas = document.getElementById("brokenGlassCanvas");
        const ctx = canvas.getContext("2d");
        const blackFade = document.getElementById('black-fade');

        let img = new Image();
        img.src = "data:image/jpeg;base64,{shutter_b64}";
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        function drawInitial() {{
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        }}
        img.onload = drawInitial;

        function shatterEffect() {{
            canvas.style.opacity = 1;
            const numPieces = 25;
            const pieces = [];

            for (let i = 0; i < numPieces; i++) {{
                const x = Math.random() * canvas.width;
                const y = Math.random() * canvas.height;
                const w = 100 + Math.random() * 150;
                const h = 100 + Math.random() * 150;
                const dx = (Math.random() - 0.5) * 900;
                const dy = (Math.random() - 0.5) * 900;
                const rot = (Math.random() - 0.5) * 720;
                pieces.push({{x, y, w, h, dx, dy, rot}});
            }}

            gsap.timeline({{
                onUpdate: render,
                onComplete: () => {{
                    gsap.to(canvas, {{opacity: 0, duration: 1}});
                    gsap.to(staticFrame, {{opacity: 0, duration: 1}});
                    setTimeout(() => {{
                        window.parent.postMessage({{type: 'intro_done'}}, '*');
                    }}, 1200);
                }}
            }})
            .to(pieces, {{
                duration: 1.8,
                x: p => p.x + p.dx,
                y: p => p.y + p.dy,
                rotation: p => p.rot,
                ease: "expo.inOut"
            }});

            function render() {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                pieces.forEach(p => {{
                    ctx.save();
                    ctx.translate(p.x + p.w/2, p.y + p.h/2);
                    ctx.rotate((p.rot || 0) * Math.PI/180);
                    ctx.drawImage(img, p.x, p.y, p.w, p.h, -p.w/2, -p.h/2, p.w, p.h);
                    ctx.restore();
                }});
            }}
        }}

        function finishIntro() {{
            vid.style.opacity = 0;
            staticFrame.style.opacity = 1;
            setTimeout(() => {{
                shatterEffect();
            }}, 200);
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
        background: url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed !important;
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
            window.parent.postMessage({type:"switch_to_main"}, "*");
        }
    });
    </script>
    """, unsafe_allow_html=True)
else:
    main_page(st.session_state.is_mobile)
