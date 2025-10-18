import streamlit as st
import os
import random
import base64
import time

# ================== CẤU HÌNH ==================
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

# File
VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
MUSIC_FILES = ["background.mp3", "background2.mp3", "background3.mp3", "background4.mp3", "background5.mp3"]

if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = None  # sẽ xác định bằng JS


# ================== ẨN GIAO DIỆN STREAMLIT ==================
def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer, iframe, [title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ================== PHÁT HIỆN MOBILE ==================
def detect_mobile():
    """Dùng JS gửi thông tin thiết bị về Python"""
    detect_script = """
    <script>
    const isMobile = /Mobi|Android|iPhone/i.test(navigator.userAgent);
    window.parent.postMessage({isMobile}, "*");
    </script>
    """
    st.markdown(detect_script, unsafe_allow_html=True)


# ================== MÀN HÌNH INTRO ==================
def intro_screen(is_mobile=False):
    hide_streamlit_ui()

    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    if not os.path.exists(video_file):
        st.error(f"⚠️ Không tìm thấy file {video_file}")
        st.session_state.intro_done = True
        st.rerun()
        return

    # Đọc video và mã hóa base64
    with open(video_file, "rb") as f:
        video_bytes = f.read()
    video_b64 = base64.b64encode(video_bytes).decode()

    intro_html = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&display=swap');

    html, body {{
        margin: 0;
        padding: 0;
        overflow: hidden;
        background-color: black;
        height: 100%;
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

    #fadeout {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: black;
        opacity: 0;
        z-index: 3;
        transition: opacity 1.2s ease-in-out;
    }}
    </style>

    <video autoplay muted playsinline id="introVid">
        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
    </video>

    <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    <div id="fadeout"></div>

    <script>
    const vid = document.getElementById('introVid');
    const fade = document.getElementById('fadeout');
    vid.onended = () => {{
        fade.style.opacity = 1;
    }};
    </script>
    """
    st.markdown(intro_html, unsafe_allow_html=True)

    # Tự chuyển qua trang chính sau 9s
    time.sleep(9)
    st.session_state.intro_done = True
    st.rerun()


# ================== TRANG CHÍNH ==================
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&display=swap');
    .stApp {{
        background-image: url("{bg}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        animation: fadeIn 1.5s ease-in;
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


# ================== LUỒNG CHÍNH ==================
if st.session_state.is_mobile is None:
    # Dùng JS để phát hiện thiết bị
    hide_streamlit_ui()
    st.markdown("""
    <script>
    const isMobile = /Mobi|Android|iPhone|iPad/i.test(navigator.userAgent);
    window.parent.postMessage({isMobile}, "*");
    </script>
    """, unsafe_allow_html=True)
    st.write("🔍 Đang phát hiện thiết bị... hãy reload nếu chậm.")
    # giả định PC nếu JS chưa kịp trả về
    st.session_state.is_mobile = False
    st.rerun()
else:
    if not st.session_state.intro_done:
        intro_screen(st.session_state.is_mobile)
    else:
        main_page(st.session_state.is_mobile)
