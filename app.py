import streamlit as st
import os
import base64
import random
import time
from streamlit_javascript import st_javascript
import streamlit.components.v1 as components

# ================== CẤU HÌNH & TRẠNG THÁI ==================
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

VIDEO_PC = "media/airplane.mp4"
VIDEO_MOBILE = "media/mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
PLANE_AUDIO = "media/plane_fly.mp3"
MUSIC_FILES = [
    "background.mp3", "background2.mp3", "background3.mp3",
    "background4.mp3", "background5.mp3"
]

if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = None
if "start_time" not in st.session_state:
    st.session_state.start_time = None

# ================== XÁC ĐỊNH THIẾT BỊ ==================
if st.session_state.is_mobile is None:
    st.session_state.intro_done = False
    ua_string = st_javascript("window.navigator.userAgent;")
    if ua_string:
        st.session_state.is_mobile = "Mobi" in ua_string
        st.rerun()
    else:
        st.info("Đang xác định thiết bị...")
        st.stop()

# ================== ẨN GIAO DIỆN STREAMLIT ==================
def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer,
    iframe[title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
        visibility: hidden !important;
    }
    .stApp, .main, .block-container, [data-testid="stVerticalBlock"] {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100vw !important;
        width: 100vw !important;
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

# ================== INTRO SCREEN ==================
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    video_path = VIDEO_MOBILE if is_mobile else VIDEO_PC
    audio_path = PLANE_AUDIO
    if not os.path.exists(video_path):
        st.error(f"⚠️ Không tìm thấy video: {video_path}")
        st.session_state.intro_done = True
        st.rerun()
        return
    if not os.path.exists(audio_path):
        audio_b64 = ""
    else:
        with open(audio_path, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode()

    with open(video_path, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()

    # CSS vị trí chữ
    text_bottom = "20%" if is_mobile else "18%"

    html_code = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <style>
        html, body {{
            margin:0; padding:0;
            width:100%; height:100%;
            overflow:hidden; background:black;
            font-family: 'Playfair Display', serif;
        }}
        video {{
            position:absolute; top:0; left:0;
            width:100%; height:100%;
            object-fit: cover;
            object-position: center;
            z-index:1;
        }}
        #intro-text {{
            position:absolute; top:50%; left:50%;
            transform: translate(-50%, -50%);
            font-size: clamp(20px,5vw,50px);
            color: #fff;
            z-index:2;
            text-align:center;
            white-space: nowrap;
            animation: fadeInOut 5s ease-in-out forwards;
        }}
        @keyframes fadeInOut {{
            0% {{opacity:0;}} 20%{{opacity:1;}} 80%{{opacity:1;}} 100%{{opacity:0;}}
        }}
        #fade {{
            position:absolute; top:0; left:0; width:100%; height:100%;
            background:black; opacity:0; z-index:3;
            transition: opacity 1s ease-in-out;
        }}
        </style>
    </head>
    <body>
        <video id="introVid" autoplay playsinline>
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <audio id="planeAudio" autoplay>
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>
        <div id="fade"></div>
        <script>
        const vid = document.getElementById("introVid");
        const fade = document.getElementById("fade");
        const audio = document.getElementById("planeAudio");

        function finishIntro(){{
            fade.style.opacity=1;
            setTimeout(()=>{{window.parent.postMessage({{"type":"intro_done"}},"*");}},1000);
        }}

        vid.onended = finishIntro;
        vid.play().catch(()=>{{setTimeout(finishIntro,5000);}});
        audio.play().catch(()=>{});
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=1000, scrolling=False)

    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()
    if time.time() - st.session_state.start_time < 9:
        time.sleep(1)
        st.rerun()
    else:
        st.session_state.intro_done = True
        st.session_state.start_time = None
        st.rerun()

# ================== MAIN PAGE ==================
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg_path = BG_MOBILE if is_mobile else BG_PC
    try:
        with open(bg_path,"rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        bg_b64 = ""
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{bg_b64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        animation: fadeInBg 1s ease-in-out forwards;
    }}
    @keyframes fadeInBg {{from{{opacity:0;}} to{{opacity:1;}}}}
    h1 {{
        text-align:center; margin-top:60px; color:#2E1C14;
        text-shadow:2px 2px 6px #FFF8DC;
        font-family:'Playfair Display', serif;
    }}
    </style>
    """, unsafe_allow_html=True)
    available_music = [m for m in MUSIC_FILES if os.path.exists(m)]
    if available_music:
        chosen = random.choice(available_music)
        with st.sidebar:
            st.subheader("🎵 Nhạc nền")
            st.audio(chosen, start_time=0)
            st.caption(f"Đang phát: **{os.path.basename(chosen)}**")
    st.markdown("<h1>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)

# ================== LUỒNG CHÍNH ==================
hide_streamlit_ui()

if st.session_state.is_mobile is None:
    pass
elif not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
else:
    main_page(st.session_state.is_mobile)
