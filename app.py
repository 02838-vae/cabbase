import streamlit as st
import streamlit.components.v1 as components
import random
import time
import os
import base64

# --- Cấu hình ---
st.set_page_config(layout="wide", page_title="Tổ Bảo Dưỡng Số 1")

PC_BACKGROUND = "cabbase.jpg"
MOBILE_BACKGROUND = "mobile.jpg"
VIDEO_INTRO = "airplane.mp4"

# --- Session ---
if "intro_complete" not in st.session_state:
    st.session_state["intro_complete"] = False

# --- CSS ---
def apply_css():
    css = f"""
    <style>
    .stApp > header {{
        display: {'none' if not st.session_state.intro_complete else 'block'} !important;
    }}
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
    h1, p, label, div, span {{
        font-family: 'Times New Roman', serif !important;
    }}
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
    if not os.path.exists(VIDEO_INTRO):
        st.error(f"Không tìm thấy file {VIDEO_INTRO}")
        time.sleep(2)
        st.session_state["intro_complete"] = True
        st.rerun()
        return

    # Chuyển video thành base64
    with open(VIDEO_INTRO, "rb") as f:
        video_bytes = f.read()
    video_b64 = base64.b64encode(video_bytes).decode()

    # HTML intro hoàn chỉnh
    intro_html = f"""
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                overflow: hidden;
                background-color: black;
            }}
            video {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                object-fit: cover;
            }}
            #intro-text {{
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-size: 3em;
                color: white;
                font-family: 'Times New Roman', serif;
                text-shadow: 2px 2px 6px black;
                animation: fade_in_out 6s forwards;
            }}
            @keyframes fade_in_out {{
                0% {{ opacity: 0; }}
                15% {{ opacity: 1; }}
                85% {{ opacity: 1; }}
                100% {{ opacity: 0; }}
            }}
            .fade-black {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: black;
                opacity: 0;
                transition: opacity 1s ease-out;
            }}
        </style>
    </head>
    <body>
        <video autoplay muted playsinline>
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div class="fade-black" id="fade"></div>
        <script>
            setTimeout(() => {{
                document.getElementById('fade').style.opacity = 1;
                setTimeout(() => {{
                    window.parent.postMessage({{type: 'intro_done'}}, '*');
                }}, 1000);
            }}, 6000);
        </script>
    </body>
    </html>
    """

    # Render iframe độc lập (sẽ autoplay được)
    components.html(intro_html, height=720, width=None)

    # Bắt tín hiệu JS → Python
    # Streamlit chưa có event bridge, ta dùng session_state để mô phỏng
    # nên chỉ cần delay đủ thời gian video
    time.sleep(7)
    st.session_state["intro_complete"] = True
    st.rerun()

# --- Trang chính ---
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

# --- Chạy ---
if st.session_state["intro_complete"]:
    main_page()
else:
    intro_screen()
