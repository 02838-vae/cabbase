import streamlit as st
import random
import base64
import os
import time

# --- Cấu hình trang ---
st.set_page_config(layout="wide", page_title="Tổ Bảo Dưỡng Số 1")

# --- Các file tài nguyên ---
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

# --- State ---
if "intro_complete" not in st.session_state:
    st.session_state["intro_complete"] = False


# --- CSS chung (ẩn header + toolbar + keyboard_...) ---
def base_css():
    st.markdown("""
    <style>
    [data-testid="stDecoration"],
    header, footer, [data-testid="stToolbar"],
    svg, iframe, [title*="keyboard"],
    [tabindex="0"][aria-live] {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)


# --- Trang intro ---
def intro_screen():
    base_css()

    if not os.path.exists(VIDEO_INTRO):
        st.error("Không tìm thấy file airplane.mp4")
        st.session_state["intro_complete"] = True
        st.rerun()
        return

    video_b64 = base64.b64encode(open(VIDEO_INTRO, "rb").read()).decode()

    # HTML full height video
    st.markdown(f"""
    <style>
    html, body {{
        margin: 0;
        padding: 0;
        height: 100%;
        width: 100%;
        background-color: black;
        overflow: hidden;
    }}
    video {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        object-fit: cover;
        z-index: -1;
    }}
    #intro-text {{
        position: fixed;
        bottom: 12%;
        left: 50%;
        transform: translateX(-50%);
        font-size: clamp(1.2em, 4vw, 1.8em);
        color: white;
        font-family: 'Times New Roman', serif;
        text-shadow: 2px 2px 8px black;
        animation: fadeInOut 6s forwards;
        white-space: nowrap;
        z-index: 1000;
    }}
    @keyframes fadeInOut {{
        0% {{ opacity: 0; }}
        20% {{ opacity: 1; }}
        80% {{ opacity: 1; }}
        100% {{ opacity: 0; }}
    }}
    #fadeout {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: black;
        opacity: 0;
        transition: opacity 1s ease-in-out;
        z-index: 2000;
    }}
    </style>

    <video autoplay muted playsinline preload="auto">
        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
    </video>
    <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    <div id="fadeout"></div>

    <script>
    setTimeout(() => {{
        document.getElementById("fadeout").style.opacity = 1;
    }}, 6000);
    </script>
    """, unsafe_allow_html=True)

    # Đợi 7 giây rồi qua trang chính
    time.sleep(7)
    st.session_state["intro_complete"] = True
    st.rerun()


# --- CSS nền trang chính ---
def main_css():
    st.markdown(f"""
    <style>
    .stApp {{
        background-size: cover !important;
        background-position: center;
        background-attachment: fixed;
        min-height: 100vh;
        transition: background-image 1s ease-in-out;
    }}
    .main-bg {{
        background-image: url("{PC_BACKGROUND}");
    }}
    @media only screen and (max-width: 768px) {{
        .main-bg {{
            background-image: url("{MOBILE_BACKGROUND}");
        }}
    }}
    h1 {{
        font-family: 'Times New Roman', serif;
        color: #4E342E;
    }}
    </style>
    """, unsafe_allow_html=True)


# --- Trang chính ---
def main_page():
    base_css()
    main_css()

    st.markdown('<div class="stApp main-bg">', unsafe_allow_html=True)

    # Nhạc nền
    valid_tracks = [m for m in MUSIC_FILES if os.path.exists(m)]
    if valid_tracks:
        track = random.choice(valid_tracks)
        with st.sidebar:
            st.subheader("🎶 Nhạc nền")
            st.audio(track, format="audio/mp3", start_time=0)
            st.caption(f"Đang phát: **{track}**")

    # Tiêu đề
    st.markdown("""
    <h1 style='text-align:center; font-size:3.5em;
               text-shadow:2px 2px 4px #FFF8DC;
               margin-top:40px;'>
        TỔ BẢO DƯỠNG SỐ 1
    </h1>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:70vh;'></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# --- Logic chính ---
if st.session_state["intro_complete"]:
    main_page()
else:
    intro_screen()
