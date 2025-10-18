import streamlit as st
import random
import time
import os

# --- Đường dẫn file ---
PC_BACKGROUND = "cabbase.jpg"
MOBILE_BACKGROUND = "mobile.jpg"
VIDEO_INTRO = "airplane.mp4"

# --- Cấu hình trang ---
st.set_page_config(layout="wide", page_title="Tổ Bảo Dưỡng Số 1")

# --- Session State ---
if "intro_complete" not in st.session_state:
    st.session_state["intro_complete"] = False

# --- CSS ---
def apply_css():
    css = f"""
    <style>
    /* Ẩn header khi đang Intro */
    .stApp > header {{
        display: {'none' if not st.session_state.intro_complete else 'block'} !important;
    }}

    /* Nền PC / Mobile */
    .stApp {{
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        transition: background-image 1s ease-in-out;
    }}
    .stApp {{
        background-image: url("{PC_BACKGROUND}");
    }}
    @media only screen and (max-width: 768px) {{
        .stApp {{
            background-image: url("{MOBILE_BACKGROUND}") !important;
        }}
    }}

    /* Phông chữ */
    h1, p, label, div, span {{
        font-family: 'Times New Roman', serif !important;
    }}

    /* Chữ Intro */
    #intro-text {{
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 3em;
        color: white;
        text-align: center;
        white-space: nowrap;
        text-shadow: 2px 2px 6px black;
        animation: fade_in_out 6s forwards;
        z-index: 9999;
        pointer-events: none;
    }}

    @keyframes fade_in_out {{
        0% {{ opacity: 0; }}
        15% {{ opacity: 1; }}
        85% {{ opacity: 1; }}
        100% {{ opacity: 0; }}
    }}

    /* Lớp phủ đen fade-out */
    .intro-screen {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: black;
        z-index: 9998;
        transition: opacity 1s ease-out;
    }}
    .intro-screen.fade-out {{
        opacity: 0;
        pointer-events: none;
    }}

    /* Sidebar */
    [data-testid="stSidebarContent"] {{
        background-color: rgba(255, 255, 240, 0.9);
        border-right: 2px solid #A1887F;
        padding: 10px;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# --- Intro ---
def intro_screen():
    apply_css()

    if not os.path.exists(VIDEO_INTRO):
        st.error(f"Không tìm thấy file {VIDEO_INTRO}")
        time.sleep(2)
        st.session_state["intro_complete"] = True
        st.rerun()
        return

    # Chữ xuất hiện giữa video
    st.markdown('<div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>', unsafe_allow_html=True)

    # Hiển thị video
    video_bytes = open(VIDEO_INTRO, "rb").read()
    st.video(video_bytes)

    # Lớp phủ fade đen + script
    st.markdown("""
        <div class="intro-screen"></div>
        <script>
            setTimeout(() => {{
                const overlay = document.querySelector('.intro-screen');
                if (overlay) overlay.classList.add('fade-out');
            }}, 5500);
        </script>
    """, unsafe_allow_html=True)

    # Sau 6.5s → qua main page
    time.sleep(6.5)
    st.session_state["intro_complete"] = True
    st.rerun()

# --- Main Page ---
def main_page():
    apply_css()

    # Sidebar nhạc
    music_files = ["background.mp3", "background1.mp3", "background2.mp3", "background3.mp3", "background4.mp3", "background5.mp3"]
    available = [m for m in music_files if os.path.exists(m)]
    if available:
        track = random.choice(available)
        with st.sidebar:
            st.subheader("🎵 Nhạc nền")
            st.audio(track, format="audio/mp3")
            st.caption(f"Đang phát: {track}")

    # Tiêu đề
    st.markdown("""
        <h1 style='text-align:center;
                   font-size:3.5em;
                   text-shadow:2px 2px 6px #FFF8DC;'>
        TỔ BẢO DƯỠNG SỐ 1
        </h1>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:60vh'></div>", unsafe_allow_html=True)

# --- Luồng chính ---
if st.session_state["intro_complete"]:
    main_page()
else:
    intro_screen()
