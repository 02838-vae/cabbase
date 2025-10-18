import streamlit as st
import os
import random
import base64
import time

# ------------------ CẤU HÌNH CƠ BẢN ------------------
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

if "intro_complete" not in st.session_state:
    st.session_state["intro_complete"] = False


# ------------------ CSS ẨN GIAO DIỆN STREAMLIT ------------------
def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    header, footer, iframe, svg, [title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ------------------ CSS NỀN TRANG CHÍNH ------------------
def main_page_style():
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("{PC_BACKGROUND}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        transition: background 1s ease-in-out;
    }}
    @media only screen and (max-width: 768px) {{
        .stApp {{
            background-image: url("{MOBILE_BACKGROUND}");
        }}
    }}
    h1 {{
        font-family: 'Times New Roman', serif;
        color: #4E342E;
        text-shadow: 2px 2px 4px #FFF8DC;
    }}
    </style>
    """, unsafe_allow_html=True)


# ------------------ MÀN HÌNH INTRO ------------------
def intro_screen():
    hide_streamlit_ui()

    if not os.path.exists(VIDEO_INTRO):
        st.error("⚠️ Không tìm thấy file airplane.mp4")
        st.session_state["intro_complete"] = True
        st.rerun()
        return

    with open(VIDEO_INTRO, "rb") as f:
        video_bytes = f.read()
    video_b64 = base64.b64encode(video_bytes).decode()

    # HTML video + hiệu ứng chữ + tự chuyển cảnh
    intro_html = f"""
    <style>
    html, body {{
        margin: 0;
        padding: 0;
        overflow: hidden;
        background-color: black;
        width: 100%;
        height: 100%;
    }}

    video {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: contain;
        background-color: black;
    }}

    #intro-text {{
        position: fixed;
        bottom: 18%;
        left: 50%;
        transform: translateX(-50%);
        font-size: clamp(1em, 4vw, 2.5em);
        color: white;
        white-space: nowrap;
        font-family: 'Times New Roman', serif;
        text-shadow: 2px 2px 8px black;
        animation: fadeInOut 6s ease-in-out forwards;
        z-index: 10;
    }}

    @keyframes fadeInOut {{
        0% {{ opacity: 0; }}
        20% {{ opacity: 1; }}
        80% {{ opacity: 1; }}
        100% {{ opacity: 0; }}
    }}

    #fade-overlay {{
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        background: black;
        opacity: 0;
        transition: opacity 1.2s ease-in-out;
        z-index: 15;
    }}
    </style>

    <video id="introVideo" autoplay muted playsinline>
        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
    </video>

    <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    <div id="fade-overlay"></div>

    <script>
    const video = document.getElementById('introVideo');
    const overlay = document.getElementById('fade-overlay');

    // Nếu autoplay bị chặn, phát khi user chạm
    video.play().catch(() => {{
        document.body.addEventListener('click', () => video.play(), {{ once: true }});
    }});

    // Khi video gần kết thúc → fade đen và báo Python
    video.addEventListener('ended', () => {{
        overlay.style.opacity = 1;
        setTimeout(() => {{
            window.parent.postMessage({{ type: 'intro_done' }}, '*');
        }}, 1000);
    }});
    </script>
    """

    st.markdown(intro_html, unsafe_allow_html=True)

    # Cơ chế dự phòng (sau 12s tự chuyển trang nếu JS không gửi tín hiệu)
    time.sleep(12)
    st.session_state["intro_complete"] = True
    st.rerun()


# ------------------ TRANG CHÍNH ------------------
def main_page():
    hide_streamlit_ui()
    main_page_style()

    available = [m for m in MUSIC_FILES if os.path.exists(m)]
    if available:
        random_track = random.choice(available)
        with st.sidebar:
            st.subheader("🎶 Nhạc nền cổ điển")
            st.audio(random_track, format="audio/mp3")
            st.caption(f"Đang phát: **{os.path.basename(random_track)}**")

    st.markdown("""
    <h1 style='text-align:center; font-size:3em; margin-top:60px;'>
        TỔ BẢO DƯỠNG SỐ 1
    </h1>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:70vh'></div>", unsafe_allow_html=True)


# ------------------ LOGIC CHÍNH ------------------
if st.session_state["intro_complete"]:
    main_page()
else:
    intro_screen()
