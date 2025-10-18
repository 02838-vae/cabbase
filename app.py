import streamlit as st
import streamlit.components.v1 as components
import random
import time
import os
import base64

# --- Cấu hình ---
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide", initial_sidebar_state="collapsed")

VIDEO_INTRO = "airplane.mp4"
PC_BACKGROUND = "cabbase.jpg"
MOBILE_BACKGROUND = "mobile.jpg"

if "intro_complete" not in st.session_state:
    st.session_state["intro_complete"] = False


# --- Hàm phụ ---
def get_base64_file(path):
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# --- Màn hình intro (HTML thuần, không hiển thị phần Streamlit nào) ---
def intro_screen():
    if not os.path.exists(VIDEO_INTRO):
        st.error("Không tìm thấy video airplane.mp4")
        time.sleep(1)
        st.session_state["intro_complete"] = True
        st.rerun()
        return

    video_b64 = get_base64_file(VIDEO_INTRO)

    intro_html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            html, body {{
                margin: 0; padding: 0;
                width: 100%; height: 100%;
                overflow: hidden;
                background-color: black;
            }}
            video {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                min-width: 100%;
                min-height: 100%;
                object-fit: cover;
                object-position: center;
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
                z-index: 1000;
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
                transition: opacity 1s ease-out;
            }}
        </style>
    </head>
    <body>
        <video autoplay muted playsinline>
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="fadeout"></div>
        <script>
            setTimeout(() => {{
                document.getElementById("fadeout").style.opacity = 1;
                setTimeout(() => {{
                    window.parent.postMessage({{type: "intro_done"}}, "*");
                }}, 1000);
            }}, 6200);
        </script>
    </body>
    </html>
    """

    # Render fullscreen, không hiển thị header Streamlit
    components.html(intro_html, height=800, width=None, scrolling=False)
    time.sleep(7)
    st.session_state["intro_complete"] = True
    st.rerun()


# --- CSS cho trang chính ---
def apply_main_css(pc_img, mobile_img):
    st.markdown(f"""
    <style>
    [data-testid="stDecoration"], header, footer, [data-testid="stToolbar"], svg,
    [title*="keyboard"], [tabindex="0"][aria-live], iframe {{
        display: none !important;
    }}
    html, body, [data-testid="stAppViewContainer"] {{
        background: url("data:image/jpeg;base64,{pc_img}") center center / cover no-repeat fixed;
    }}
    @media (max-width: 768px) {{
        html, body, [data-testid="stAppViewContainer"] {{
            background: url("data:image/jpeg;base64,{mobile_img}") center center / cover no-repeat fixed;
        }}
    }}
    h1 {{
        font-family: 'Times New Roman', serif;
        color: #fff8dc;
        text-align: center;
        text-shadow: 2px 2px 8px black;
        font-size: 3.2em;
        margin-top: 40px;
    }}
    </style>
    """, unsafe_allow_html=True)


# --- Trang chính ---
def main_page():
    pc_img = get_base64_file(PC_BACKGROUND)
    mobile_img = get_base64_file(MOBILE_BACKGROUND)
    apply_main_css(pc_img, mobile_img)

    # --- Phát nhạc nền ---
    music_files = [
        "background.mp3", "background1.mp3", "background2.mp3",
        "background3.mp3", "background4.mp3", "background5.mp3"
    ]
    available = [m for m in music_files if os.path.exists(m)]
    if available:
        track = random.choice(available)
        audio_b64 = get_base64_file(track)
        st.markdown(f"""
        <audio autoplay loop controls style="position:fixed; top:15px; left:15px; z-index:1000; opacity:0.8;">
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>
        """, unsafe_allow_html=True)

    # --- Tiêu đề chính ---
    st.markdown("<h1>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)


# --- Logic ---
if st.session_state["intro_complete"]:
    main_page()
else:
    intro_screen()
