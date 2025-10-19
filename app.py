import streamlit as st
import os, base64, random
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

# ================== CẤU HÌNH ==================
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

VIDEO_PC = "media/airplane.mp4"
VIDEO_MOBILE = "media/mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
MUSIC_FILES = ["background.mp3", "background2.mp3", "background3.mp3"]

if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = None

# ================== XÁC ĐỊNH THIẾT BỊ ==================
if st.session_state.is_mobile is None:
    ua = st_javascript("window.navigator.userAgent;")
    if ua:
        st.session_state.is_mobile = not parse(ua).is_pc
        st.rerun()
    else:
        st.info("Đang xác định thiết bị...")
        st.stop()

# ================== ẨN UI STREAMLIT ==================
def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
        visibility: hidden !important;
    }
    .stApp, .main, .block-container {
        padding: 0 !important;
        margin: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        max-width: 100vw !important;
        min-height: 100vh !important;
    }
    [data-testid*="stHtmlComponents"] {
        position: fixed !important;
        top: 0; left: 0;
        width: 100vw !important;
        height: 100vh !important;
        z-index: 9999;
    }
    </style>
    """, unsafe_allow_html=True)

# ================== MÀN HÌNH INTRO ==================
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    video_path = VIDEO_MOBILE if is_mobile else VIDEO_PC
    with open(video_path, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()

    object_pos = "center 25%" if is_mobile else "center"
    text_bottom = "10%" if is_mobile else "15%"

    html_code = f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&display=swap" rel="stylesheet">
        <style>
            html, body {{
                margin: 0; padding: 0;
                width: 100%; height: 100%;
                background: black; overflow: hidden;
            }}
            video {{
                position: fixed;
                top: 0; left: 0;
                width: 100%; height: 100%;
                object-fit: cover;
                object-position: {object_pos};
                z-index: 1;
            }}
            #intro-text {{
                position: absolute;
                bottom: {text_bottom};
                left: 50%;
                transform: translateX(-50%);
                font-family: 'Cinzel Decorative', serif;
                font-size: clamp(18px, 4vw, 40px);
                color: white;
                text-shadow: 0 0 20px rgba(255,255,255,0.9), 0 0 40px rgba(255,215,0,0.7);
                opacity: 0;
                white-space: nowrap;
                z-index: 2;
                animation: fadeText 6s ease-in-out forwards;
            }}
            @keyframes fadeText {{
                0% {{opacity: 0; transform: translate(-50%, 20px);}}
                20% {{opacity: 1; transform: translate(-50%, 0);}}
                80% {{opacity: 1; transform: translate(-50%, 0);}}
                100% {{opacity: 0; transform: translate(-50%, -10px);}}
            }}
            #fade {{
                position: fixed;
                top: 0; left: 0;
                width: 100%; height: 100%;
                background: black;
                opacity: 0;
                z-index: 3;
                transition: opacity 1.5s ease-in-out;
            }}
        </style>
    </head>
    <body>
        <video id="introVid" autoplay muted playsinline>
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="fade"></div>

        <script>
            const vid = document.getElementById("introVid");
            const fade = document.getElementById("fade");

            vid.play().catch(() => {{
                vid.muted = true;
                vid.play();
            }});

            // Khi video gần hết -> fade out
            vid.addEventListener("timeupdate", () => {{
                if (vid.duration && vid.currentTime >= vid.duration - 1.5) {{
                    fade.style.opacity = 1;
                }}
            }});

            // Khi kết thúc -> ghi flag sang localStorage
            vid.addEventListener("ended", () => {{
                fade.style.opacity = 1;
                setTimeout(() => {{
                    localStorage.setItem("intro_done_flag", "1");
                }}, 1200);
            }});
        </script>
    </body>
    </html>
    """

    components.html(html_code, height=1000, scrolling=False)

    # Kiểm tra localStorage từ JS mỗi 0.5s
    intro_done = st_javascript("""
        async function checkFlag() {
            return new Promise(resolve => {
                const timer = setInterval(() => {
                    if (localStorage.getItem("intro_done_flag") === "1") {
                        clearInterval(timer);
                        localStorage.removeItem("intro_done_flag");
                        resolve("done");
                    }
                }, 500);
            });
        }
        checkFlag();
    """)

    if intro_done == "done":
        st.session_state.intro_done = True
        st.rerun()

# ================== TRANG CHÍNH ==================
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg_file = BG_MOBILE if is_mobile else BG_PC
    with open(bg_file, "rb") as f:
        bg_b64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&display=swap');
    .stApp {{
        background: url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed;
        background-size: cover;
        animation: fadeInBg 1.5s ease-in-out forwards;
    }}
    @keyframes fadeInBg {{from {{opacity:0;}} to {{opacity:1;}}}}
    h1 {{
        text-align: center;
        margin-top: 60px;
        color: #2E1C14;
        text-shadow: 2px 2px 6px #FFF8DC;
        font-family: 'Playfair Display', serif;
    }}
    </style>
    """, unsafe_allow_html=True)

    music = [m for m in MUSIC_FILES if os.path.exists(m)]
    if music:
        chosen = random.choice(music)
        with st.sidebar:
            st.audio(chosen)
            st.caption(f"🎵 Đang phát: {os.path.basename(chosen)}")

    st.markdown("<h1>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)

# ================== MAIN ==================
hide_streamlit_ui()
if not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
else:
    main_page(st.session_state.is_mobile)
