import streamlit as st
import base64
import os
import random
import time

# --- Cấu hình trang ---
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

# --- File tài nguyên ---
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


# --- CSS ẩn header và toolbar ---
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


# --- Màn hình intro ---
def intro_screen():
    hide_streamlit_ui()

    if not os.path.exists(VIDEO_INTRO):
        st.warning("⚠️ Không tìm thấy file airplane.mp4")
        st.session_state["intro_complete"] = True
        st.rerun()
        return

    video_b64 = base64.b64encode(open(VIDEO_INTRO, "rb").read()).decode()

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
        font-size: clamp(1em, 4vw, 1.4em);
        color: white;
        font-family: 'Times New Roman', serif;
        text-shadow: 2px 2px 8px black;
        animation: fadeInOut 6s forwards;
        white-space: nowrap;
        z-index: 10;
    }}
    @keyframes fadeInOut {{
        0% {{ opacity: 0; }}
        20% {{ opacity: 1; }}
        80% {{ opacity: 1; }}
        100% {{ opacity: 0; }}
    }}
    #fadeout {{
        position: fixed;
        top: 0; left: 0;
        width: 100%;
        height: 100%;
        background-color: black;
        opacity: 0;
        transition: opacity 1s ease-in-out;
        z-index: 20;
    }}
    </style>

    <video id="introVideo" muted playsinline preload="auto">
        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
    </video>
    <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    <div id="fadeout"></div>

    <script>
    const v = document.getElementById('introVideo');
    v.play().catch(() => {{
        // nếu bị chặn autoplay -> phát khi user chạm
        document.body.addEventListener('click', () => v.play(), {{once:true}});
    }});

    setTimeout(() => {{
        document.getElementById('fadeout').style.opacity = 1;
    }}, 6200);
    </script>
    """

    st.markdown(intro_html, unsafe_allow_html=True)

    time.sleep(7)
    st.session_state["intro_complete"] = True
    st.rerun()


# --- CSS nền trang chính ---
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

    # Tiêu đề chính
    st.markdown("""
    <h1 style='text-align:center; font-size:3.2em; margin-top:50px;'>
        TỔ BẢO DƯỠNG SỐ 1
    </h1>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:75vh'></div>", unsafe_allow_html=True)


# --- Logic chính ---
if st.session_state["intro_complete"]:
    main_page()
else:
    intro_screen()
