import streamlit as st
import random
import time
import os
import base64
import streamlit.components.v1 as components

# --- File cấu hình ---
PC_BACKGROUND = "cabbase.jpg"
MOBILE_BACKGROUND = "mobile.jpg"
VIDEO_INTRO = "airplane.mp4"
MUSIC_FILES = ["background.mp3", "background2.mp3", "background3.mp3", "background4.mp3", "background5.mp3"]

# --- Cấu hình Trang ---
st.set_page_config(layout="wide", page_title="Tổ Bảo Dưỡng Số 1")

# --- Session state ---
if 'intro_complete' not in st.session_state:
    st.session_state['intro_complete'] = False

# --- CSS Ẩn header, toolbar ---
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


# --- CSS trang chính ---
def apply_main_css():
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


# --- Màn hình intro ---
def intro_screen():
    hide_streamlit_ui()

    if not os.path.exists(VIDEO_INTRO):
        st.error(f"Không tìm thấy file video: {VIDEO_INTRO}")
        time.sleep(1)
        st.session_state['intro_complete'] = True
        st.rerun()
        return

    # Đọc video và encode base64 để nhúng
    video_b64 = base64.b64encode(open(VIDEO_INTRO, "rb").read()).decode()

    # HTML hiển thị video full màn hình + text
    intro_html = f"""
    <style>
    html, body {{
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100%;
        overflow: hidden;
        background-color: black;
    }}
    video {{
        position: fixed;
        top: 50%;
        left: 50%;
        min-width: 100%;
        min-height: 100%;
        width: auto;
        height: auto;
        transform: translate(-50%, -50%);
        object-fit: cover;
        object-position: center;
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
        white-space: nowrap;
        z-index: 10;
    }}
    @keyframes fadeInOut {{
        0% {{ opacity: 0; }}
        15% {{ opacity: 1; }}
        85% {{ opacity: 1; }}
        100% {{ opacity: 0; }}
    }}
    #fadeout {{
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-color: black;
        opacity: 0;
        transition: opacity 1s ease-in-out;
        z-index: 20;
    }}
    </style>

    <video id="introVideo" autoplay muted playsinline preload="auto">
        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
    </video>
    <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    <div id="fadeout"></div>

    <script>
    const v = document.getElementById('introVideo');
    v.play().catch(() => {{
        document.body.addEventListener('click', () => v.play(), {{once:true}});
    }});
    setTimeout(() => {{
        document.getElementById('fadeout').style.opacity = 1;
    }}, 6200);
    </script>
    """

    components.html(intro_html, height=800, scrolling=False)

    time.sleep(7)
    st.session_state['intro_complete'] = True
    st.rerun()


# --- Trang chính ---
def main_page():
    hide_streamlit_ui()
    apply_main_css()

    # Thanh nhạc nền
    valid_tracks = [m for m in MUSIC_FILES if os.path.exists(m)]
    if valid_tracks:
        track = random.choice(valid_tracks)
        with st.sidebar:
            st.subheader("🎶 Nhạc nền")
            st.audio(track, format="audio/mp3")
            st.caption(f"Đang phát: **{os.path.basename(track)}**")
    else:
        st.sidebar.warning("⚠️ Không tìm thấy file nhạc nền nào")

    # Tiêu đề chính
    st.markdown("""
    <h1 style='text-align:center; font-size:3.2em; margin-top:50px;'>
        TỔ BẢO DƯỠNG SỐ 1
    </h1>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:75vh'></div>", unsafe_allow_html=True)


# --- Điều hướng chính ---
if st.session_state['intro_complete']:
    main_page()
else:
    intro_screen()
