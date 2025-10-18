import streamlit as st
import base64
import random
import os
import time

# --- Cấu hình trang ---
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

# --- Tên file ---
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

# --- Session state ---
if "intro_complete" not in st.session_state:
    st.session_state["intro_complete"] = False

# --- Ẩn header, toolbar, icon Streamlit ---
def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stDecoration"],
    header, footer, [data-testid="stToolbar"],
    iframe, svg, [title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CSS nền trang chính ---
def apply_main_css():
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("{PC_BACKGROUND}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
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

# --- Màn hình Intro (HTML inline, autoplay bảo đảm hoạt động) ---
def intro_screen():
    hide_streamlit_ui()

    if not os.path.exists(VIDEO_INTRO):
        st.error("⚠️ Không tìm thấy file airplane.mp4 trong thư mục.")
        st.session_state["intro_complete"] = True
        st.rerun()
        return

    # Encode video base64 để nhúng trực tiếp
    with open(VIDEO_INTRO, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()

    intro_html = f"""
    <style>
    html, body {{
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100%;
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
        bottom: 10%;
        left: 50%;
        transform: translateX(-50%);
        font-size: clamp(1.2em, 4vw, 1.8em);
        color: white;
        font-family: 'Times New Roman', serif;
        text-shadow: 2px 2px 8px black;
        animation: fadeInOut 6s forwards;
        z-index: 10;
        white-space: nowrap;
    }}
    @keyframes fadeInOut {{
        0% {{ opacity: 0; }}
        15% {{ opacity: 1; }}
        85% {{ opacity: 1; }}
        100% {{ opacity: 0; }}
    }}
    #blackout {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: black;
        opacity: 0;
        transition: opacity 1s ease-in-out;
        z-index: 20;
    }}
    </style>

    <video id="introVideo" muted autoplay playsinline preload="auto">
        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
    </video>
    <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    <div id="blackout"></div>

    <script>
    const video = document.getElementById('introVideo');
    // Nếu autoplay bị chặn (mobile), play lại khi user chạm
    video.play().catch(() => {{
        document.body.addEventListener('click', () => video.play(), {{once:true}});
    }});

    // Sau 6.5s fade sang màu đen và gửi tín hiệu về Streamlit
    setTimeout(() => {{
        document.getElementById('blackout').style.opacity = 1;
        setTimeout(() => {{
            window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'done'}}, '*');
        }}, 1000);
    }}, 6500);
    </script>
    """

    # Hiển thị HTML inline trong Streamlit DOM (không bị sandbox)
    st.components.v1.html(intro_html, height=720, scrolling=False)

    # Chờ thời gian video chạy, sau đó chuyển trang
    time.sleep(7.5)
    st.session_state["intro_complete"] = True
    st.rerun()

# --- Trang chính ---
def main_page():
    hide_streamlit_ui()
    apply_main_css()

    # Thanh nhạc nền
    available_music = [m for m in MUSIC_FILES if os.path.exists(m)]
    if available_music:
        track = random.choice(available_music)
        with st.sidebar:
            st.subheader("🎶 Nhạc nền")
            st.audio(track, format="audio/mp3")
            st.caption(f"Đang phát: **{os.path.basename(track)}**")

    # Tiêu đề
    st.markdown("""
    <h1 style='text-align:center; font-size:3.2em; margin-top:50px;'>
        TỔ BẢO DƯỠNG SỐ 1
    </h1>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:70vh'></div>", unsafe_allow_html=True)

# --- Chạy ứng dụng ---
if st.session_state["intro_complete"]:
    main_page()
else:
    intro_screen()
