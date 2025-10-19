import streamlit as st
import os
import base64
import random
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

# ========== CẤU HÌNH ==========
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

VIDEO_PC = "media/airplane.mp4"
VIDEO_MOBILE = "media/mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
MUSIC_FILES = [
    "background.mp3", "background2.mp3", "background3.mp3",
    "background4.mp3", "background5.mp3"
]

if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = None

# ========== PHÁT HIỆN THIẾT BỊ ==========
if st.session_state.is_mobile is None:
    ua_string = st_javascript("window.navigator.userAgent;")
    if ua_string:
        ua = parse(ua_string)
        st.session_state.is_mobile = not ua.is_pc
        st.rerun()
    else:
        st.info("Đang phát hiện thiết bị...")
        st.stop()

# ========== ẨN GIAO DIỆN STREAMLIT ==========
def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer,
    iframe[title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
        visibility: hidden !important;
    }
    .stApp, .main, .block-container {
        padding: 0 !important;
        margin: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        overflow: hidden !important;
    }
    [data-testid*="stHtmlComponents"] {
        position: fixed !important;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        z-index: 9999;
    }
    </style>
    """, unsafe_allow_html=True)

# ========== MÀN HÌNH INTRO ==========
def intro_screen(is_mobile=False):
    hide_streamlit_ui()

    video_path = VIDEO_MOBILE if is_mobile else VIDEO_PC
    if not os.path.exists(video_path):
        st.error(f"Không tìm thấy video: {video_path}")
        st.session_state.intro_done = True
        st.rerun()
        return

    with open(video_path, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()

    if is_mobile:
        object_position = "center 10%"
        text_bottom = "8%"
        font_size = "clamp(16px, 4.5vw, 26px)"
        text_width = "90vw"
    else:
        object_position = "center center"
        text_bottom = "20%"
        font_size = "clamp(26px, 3vw, 46px)"
        text_width = "70vw"

    intro_html = f"""
    <html lang="vi">
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&display=swap');
        html, body {{
            margin: 0; padding: 0;
            width: 100vw; height: 100vh;
            overflow: hidden; background: black;
        }}
        video {{
            position: absolute; top: 0; left: 0;
            width: 100vw; height: 100vh;
            object-fit: cover;
            object-position: {object_position};
            z-index: 1;
            opacity: 1;
            transition: opacity 1.5s ease-in-out;
        }}
        #intro-text {{
            position: absolute;
            left: 50%; bottom: {text_bottom};
            transform: translateX(-50%);
            font-family: 'Cinzel', serif;
            font-size: {font_size};
            width: {text_width};
            text-align: center;
            color: #fff8dc;
            font-weight: 700;
            text-shadow: 0 0 6px rgba(255,255,255,0.3),
                         0 0 20px rgba(255,240,180,0.6),
                         0 0 40px rgba(255,220,130,0.4);
            z-index: 10;
            opacity: 0;
            animation: textFade 7s ease-in-out forwards;
            white-space: normal;
            overflow-wrap: break-word;
        }}
        @keyframes textFade {{
            0% {{ opacity: 0; transform: translate(-50%, 40px); }}
            15% {{ opacity: 1; transform: translate(-50%, 0); }}
            75% {{ opacity: 1; }}
            100% {{ opacity: 0; transform: translate(-50%, -20px); }}
        }}
        #fade {{
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: black;
            opacity: 0;
            transition: opacity 1.5s ease-in-out;
            z-index: 20;
        }}
        </style>
    </head>
    <body>
        <video id="introVid" autoplay muted playsinline preload="auto">
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="fade"></div>
        <script>
        const vid = document.getElementById("introVid");
        const fade = document.getElementById("fade");

        vid.addEventListener('canplaythrough', () => {{
            vid.play().catch(()=>{});
        }});

        vid.addEventListener('timeupdate', () => {{
            if (vid.duration - vid.currentTime <= 1.5) {{
                vid.style.opacity = '0';
                fade.style.opacity = '1';
            }}
        }});

        vid.addEventListener('ended', () => {{
            setTimeout(() => {{
                window.parent.postMessage({{"type": "intro_done"}}, "*");
            }}, 800);
        }});

        // fallback nếu autoplay bị chặn
        setTimeout(() => {{
            if (vid.paused) {{
                vid.play().catch(() => {{
                    window.parent.postMessage({{"type": "intro_done"}}, "*");
                }});
            }}
        }}, 2000);
        </script>
    </body>
    </html>
    """
    components.html(intro_html, height=950, scrolling=False)

# ========== TRANG CHÍNH ==========
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    try:
        with open(bg, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        st.error(f"Không tìm thấy ảnh nền: {bg}")
        bg_b64 = ""

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&display=swap');
    .stApp {{
        background-image: url("data:image/jpeg;base64,{bg_b64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        animation: fadeInMain 1.2s ease-in-out forwards;
    }}
    @keyframes fadeInMain {{
        from {{ opacity: 0; }} to {{ opacity: 1; }}
    }}
    h1 {{
        text-align: center;
        margin-top: 60px;
        color: #2E1C14;
        text-shadow: 2px 2px 6px #FFF8DC;
        font-family: 'Playfair Display', serif;
    }}
    </style>
    """, unsafe_allow_html=True)

    available_music = [m for m in MUSIC_FILES if os.path.exists(m)]
    if available_music:
        chosen = random.choice(available_music)
        with st.sidebar:
            st.subheader("🎵 Nhạc nền")
            st.audio(chosen)
            st.caption(f"Đang phát: **{os.path.basename(chosen)}**")

    st.markdown("<h1>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)

# ========== MAIN FLOW ==========
hide_streamlit_ui()

if st.session_state.is_mobile is None:
    pass
elif not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
else:
    main_page(st.session_state.is_mobile)
