import streamlit as st
import base64
import os
import random
import time

# ====================== CẤU HÌNH ======================
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

VIDEO_INTRO = "airplane.mp4"
PC_BACKGROUND = "cabbase.jpg"
MOBILE_BACKGROUND = "mobile.jpg"
MUSIC_FILES = [
    "background.mp3",
    "background2.mp3",
    "background3.mp3",
    "background4.mp3",
    "background5.mp3"
]

if "intro_done" not in st.session_state:
    st.session_state.intro_done = False


# ====================== CSS CHUNG ======================
def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    header, footer, iframe, svg, [title*="keyboard"],
    [tabindex="0"][aria-live] {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ====================== MÀN HÌNH INTRO ======================
def show_intro():
    hide_streamlit_ui()

    if not os.path.exists(VIDEO_INTRO):
        st.error("⚠️ Không tìm thấy file airplane.mp4")
        st.session_state.intro_done = True
        st.rerun()
        return

    video_bytes = open(VIDEO_INTRO, "rb").read()
    video_b64 = base64.b64encode(video_bytes).decode()

    intro_html = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&display=swap');

    html, body {{
        margin: 0;
        padding: 0;
        height: 100%;
        overflow: hidden;
        background-color: black;
    }}

    video {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        object-fit: cover;
        z-index: 0;
    }}

    #intro-text {{
        position: fixed;
        bottom: 22%;
        left: 50%;
        transform: translateX(-50%);
        font-size: clamp(1.2em, 4vw, 2.4em);
        color: white;
        font-family: 'Playfair Display', serif;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.8);
        animation: fadeInOut 6s ease-in-out forwards;
        white-space: nowrap;
        z-index: 2;
    }}

    @keyframes fadeInOut {{
        0% {{ opacity: 0; transform: translate(-50%, 20px); }}
        20% {{ opacity: 1; transform: translate(-50%, 0); }}
        80% {{ opacity: 1; transform: translate(-50%, 0); }}
        100% {{ opacity: 0; transform: translate(-50%, -10px); }}
    }}

    #fadeout {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: black;
        opacity: 0;
        z-index: 5;
        transition: opacity 1.5s ease-in-out;
    }}
    </style>

    <video autoplay muted playsinline id="introVid">
        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
    </video>

    <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    <div id="fadeout"></div>

    <script>
    const vid = document.getElementById("introVid");
    const fade = document.getElementById("fadeout");
    vid.onended = () => {{
        fade.style.opacity = 1;
    }};
    </script>
    """
    st.components.v1.html(intro_html, height=720)

    # Đợi video xong rồi chuyển trang (tự động)
    time.sleep(9)
    st.session_state.intro_done = True
    st.rerun()


# ====================== TRANG CHÍNH ======================
def show_main_page():
    hide_streamlit_ui()

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&display=swap');

    .stApp {{
        background-image: url("{PC_BACKGROUND}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        animation: fadeIn 2s ease-in-out;
    }}
    @media only screen and (max-width: 768px) {{
        .stApp {{
            background-image: url("{MOBILE_BACKGROUND}");
        }}
    }}
    h1 {{
        font-family: 'Playfair Display', serif;
        color: #3E2723;
        text-shadow: 2px 2px 6px #FFF8DC;
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
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

    st.markdown("""
    <div style="text-align:center; margin-top:60px;">
        <h1>TỔ BẢO DƯỠNG SỐ 1</h1>
    </div>
    """, unsafe_allow_html=True)


# ====================== LOGIC CHÍNH ======================
if not st.session_state.intro_done:
    show_intro()
else:
    show_main_page()
