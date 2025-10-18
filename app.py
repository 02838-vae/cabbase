import streamlit as st
import os
import random
import base64
import time

# ================== CẤU HÌNH ==================
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

VIDEO_FILE = "airplane.mp4"
PC_BACKGROUND = "cabbase.jpg"
MOBILE_BACKGROUND = "mobile.jpg"
MUSIC_FILES = ["background.mp3", "background2.mp3", "background3.mp3", "background4.mp3", "background5.mp3"]

if "intro_complete" not in st.session_state:
    st.session_state.intro_complete = False


# ================== ẨN GIAO DIỆN STREAMLIT ==================
def hide_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"],
    header, footer, iframe, [title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ================== CSS CHUNG ==================
def main_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&display=swap');

    .stApp {{
        background-image: url("{PC_BACKGROUND}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        animation: fadeIn 1.5s ease-in;
    }}

    @media only screen and (max-width: 768px) {{
        .stApp {{
            background-image: url("{MOBILE_BACKGROUND}");
        }}
    }}

    h1 {{
        font-family: 'Playfair Display', serif;
        color: #3E2723;
        text-shadow: 2px 2px 5px #FFF8DC;
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    </style>
    """, unsafe_allow_html=True)


# ================== MÀN HÌNH INTRO ==================
def intro_screen():
    hide_ui()

    if not os.path.exists(VIDEO_FILE):
        st.error("⚠️ Không tìm thấy file airplane.mp4")
        st.session_state.intro_complete = True
        st.rerun()
        return

    # Đọc video base64
    with open(VIDEO_FILE, "rb") as f:
        video_bytes = f.read()
    video_b64 = base64.b64encode(video_bytes).decode()

    # CSS + HTML
    intro_html = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&display=swap');
    html, body {{
        margin: 0;
        padding: 0;
        overflow: hidden;
        height: 100%;
        background: black;
    }}
    video {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        object-fit: cover;
        z-index: 1;
    }}
    #intro-text {{
        position: fixed;
        bottom: 22%;
        left: 50%;
        transform: translateX(-50%);
        font-size: clamp(1em, 4vw, 2.5em);
        color: white;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.9);
        font-family: 'Playfair Display', serif;
        white-space: nowrap;
        animation: fadeInOut 6s ease-in-out forwards;
        z-index: 2;
    }}
    @keyframes fadeInOut {{
        0% {{ opacity: 0; transform: translate(-50%, 20px); }}
        20% {{ opacity: 1; transform: translate(-50%, 0); }}
        80% {{ opacity: 1; transform: translate(-50%, 0); }}
        100% {{ opacity: 0; transform: translate(-50%, -10px); }}
    }}
    #fade {{
        position: fixed;
        top: 0; left: 0;
        width: 100%;
        height: 100%;
        background-color: black;
        opacity: 0;
        z-index: 3;
        transition: opacity 1.5s ease-in-out;
    }}
    </style>

    <video autoplay muted playsinline id="introVid">
        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
    </video>

    <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    <div id="fade"></div>

    <script>
    const vid = document.getElementById('introVid');
    const fade = document.getElementById('fade');

    vid.onended = () => {{
        fade.style.opacity = 1;
        setTimeout(() => {{
            window.parent.postMessage({{event: 'video_done'}}, '*');
        }}, 1500);
    }};
    </script>
    """

    st.markdown(intro_html, unsafe_allow_html=True)

    # Tự động chuyển sau 10 giây
    time.sleep(10)
    st.session_state.intro_complete = True
    st.rerun()


# ================== TRANG CHÍNH ==================
def main_page():
    hide_ui()
    main_css()

    st.markdown("<h1 style='text-align:center; margin-top:60px;'>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)

    # Thanh phát nhạc
    available_music = [m for m in MUSIC_FILES if os.path.exists(m)]
    if available_music:
        chosen = random.choice(available_music)
        with st.sidebar:
            st.subheader("🎵 Nhạc nền")
            st.audio(chosen, format="audio/mp3")
            st.caption(f"Đang phát: **{os.path.basename(chosen)}**")


# ================== LUỒNG CHÍNH ==================
if not st.session_state.intro_complete:
    intro_screen()
else:
    main_page()
