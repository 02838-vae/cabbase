import streamlit as st
import streamlit.components.v1 as components
import random
import time
import os
import base64

# --- Cấu hình trang ---
st.set_page_config(layout="wide", page_title="Tổ Bảo Dưỡng Số 1")

PC_BACKGROUND = "cabbase.jpg"
MOBILE_BACKGROUND = "mobile.jpg"
VIDEO_INTRO = "airplane.mp4"

# --- Session ---
if "intro_complete" not in st.session_state:
    st.session_state["intro_complete"] = False

# --- CSS chung ---
def apply_css():
    css = f"""
    <style>
    /* Ẩn header khi intro */
    .stApp > header {{
        display: {'none' if not st.session_state.intro_complete else 'block'} !important;
    }}

    /* Ẩn hoàn toàn các phần tử phụ của Streamlit */
    div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"],
    div[tabindex="0"][aria-live="polite"],
    div[tabindex="0"][role="region"],
    div[title*="keyboard_double_arrow"],
    button[kind="header"],
    svg[aria-label*="keyboard"],
    [data-testid="stToolbar"],
    [data-testid="stMainBlockContainer"] > div:first-child {{
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        overflow: hidden !important;
    }}

    /* Nền PC/Mobile */
    .stApp {{
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        transition: background-image 1s ease-in-out;
        overflow: hidden !important;
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
    if not os.path.exists(VIDEO_INTRO):
        st.error(f"Không tìm thấy file {VIDEO_INTRO}")
        time.sleep(2)
        st.session_state["intro_complete"] = True
        st.rerun()
        return

    with open(VIDEO_INTRO, "rb") as f:
        video_bytes = f.read()
    video_b64 = base64.b64encode(video_bytes).decode()

    # HTML video intro (fit mọi màn hình, text nhỏ, dưới máy bay)
    intro_html = f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
        <style>
            html, body {{
                margin: 0;
                padding: 0;
                height: 100%;
                width: 100%;
                overflow: hidden;
                background: black;
            }}
            video {{
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 100vw;
                height: 100vh;
                object-fit: cover;
                object-position: center;
            }}
            #intro-text {{
                position: fixed;
                bottom: 12%;
                left: 50%;
                transform: translateX(-50%);
                font-size: clamp(1em, 4vw, 1.8em);
                color: white;
                font-family: 'Times New Roman', serif;
                text-shadow: 2px 2px 5px black;
                animation: fade_in_out 6s forwards;
                white-space: nowrap;
                text-align: center;
                letter-spacing: 1.5px;
            }}
            @keyframes fade_in_out {{
                0% {{ opacity: 0; transform: translate(-50%, 20%); }}
                15% {{ opacity: 1; transform: translate(-50%, 0); }}
                85% {{ opacity: 1; }}
                100% {{ opacity: 0; transform: translate(-50%, -10%); }}
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

    components.html(intro_html, height=720, width=None)
    time.sleep(7)
    st.session_state["intro_complete"] = True
    st.rerun()

# --- Trang chính ---
def main_page():
    apply_css()

    # Sidebar nhạc nền
    music_files = [
        "background.mp3",
        "background1.mp3",
        "background2.mp3",
        "background3.mp3",
        "background4.mp3",
        "background5.mp3",
    ]
    available = [m for m in music_files if os.path.exists(m)]
    if available:
        track = random.choice(available)
        with st.sidebar:
            st.subheader("🎵 Nhạc nền")
            st.audio(track, format="audio/mp3")
            st.caption(f"Đang phát: {track}")

    # Tiêu đề chính
    st.markdown("""
        <h1 style='text-align:center;
                   font-size:3.5em;
                   text-shadow:2px 2px 6px #FFF8DC;
                   margin-top: 30px;'>
        TỔ BẢO DƯỠNG SỐ 1
        </h1>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:60vh'></div>", unsafe_allow_html=True)

# --- Logic chính ---
if st.session_state["intro_complete"]:
    main_page()
else:
    intro_screen()
