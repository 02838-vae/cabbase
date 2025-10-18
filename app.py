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
if 'intro_complete' not in st.session_state:
    st.session_state['intro_complete'] = False

# --- CSS tùy chỉnh ---
def custom_css():
    css = f"""
    <style>
    /* Toàn trang */
    .stApp {{
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        transition: background-image 1s ease-in-out;
        min-height: 100vh;
    }}

    /* Ẩn header khi đang intro */
    .stApp > header {{
        display: {'none' if not st.session_state.intro_complete else 'block'} !important;
    }}

    /* Ảnh nền PC và Mobile */
    .stApp.main-page-bg {{
        background-image: url("{PC_BACKGROUND}");
    }}
    @media only screen and (max-width: 768px) {{
        .stApp.main-page-bg {{
            background-image: url("{MOBILE_BACKGROUND}");
        }}
    }}

    /* Font và màu sắc */
    h1, p, label {{
        font-family: 'Times New Roman', serif;
        color: #4E342E;
    }}

    /* Hiệu ứng chữ Intro */
    @keyframes fade_in_out {{
        0% {{ opacity: 0; }}
        10% {{ opacity: 1; }}
        90% {{ opacity: 1; }}
        100% {{ opacity: 0; }}
    }}
    #intro-text {{
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 3em;
        color: white;
        text-shadow: 2px 2px 6px #000;
        animation: fade_in_out 6s forwards;
        z-index: 9999;
        pointer-events: none;
    }}

    /* Màn hình Intro đen */
    .intro-screen-container {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: black;
        z-index: 998;
        transition: opacity 1s ease-out;
    }}
    .intro-screen-container.fade-out {{
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
    custom_css()

    if not os.path.exists(VIDEO_INTRO):
        st.error(f"Không tìm thấy video {VIDEO_INTRO}")
        time.sleep(2)
        st.session_state['intro_complete'] = True
        st.rerun()
        return

    # Hiển thị chữ
    st.markdown('<div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>', unsafe_allow_html=True)

    # Video intro
    video_bytes = open(VIDEO_INTRO, 'rb').read()
    st.video(video_bytes)

    # Overlay đen + script fade out
    st.markdown("""
        <div class="intro-screen-container"></div>
        <script>
            setTimeout(() => {{
                const container = document.querySelector('.intro-screen-container');
                if (container) container.classList.add('fade-out');
            }}, 5500);
        </script>
    """, unsafe_allow_html=True)

    # Sau 6 giây chuyển qua main page
    time.sleep(6)
    st.session_state['intro_complete'] = True
    st.rerun()

# --- Trang chính ---
def main_page():
    custom_css()
    st.markdown('<div class="stApp main-page-bg">', unsafe_allow_html=True)

    # Phát nhạc nền ngẫu nhiên
    music_files = ["background.mp3", "background1.mp3", "background2.mp3", "background3.mp3", "background4.mp3", "background5.mp3"]
    available_music = [m for m in music_files if os.path.exists(m)]
    if available_music:
        random_track = random.choice(available_music)
        with st.sidebar:
            st.subheader("🎶 Nhạc nền cổ điển")
            st.audio(random_track, format="audio/mp3")
            st.caption(f"Đang phát: **{random_track}**")

    # Tiêu đề chính
    st.markdown("""
        <h1 style='text-align:center;
                   font-size:3.5em;
                   text-shadow:2px 2px 4px #FFF8DC;'>
        TỔ BẢO DƯỠNG SỐ 1
        </h1>
    """, unsafe_allow_html=True)

    # Placeholder nội dung
    st.markdown('<div style="height: 60vh;"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Chạy ứng dụng ---
if st.session_state['intro_complete']:
    main_page()
else:
    intro_screen()
