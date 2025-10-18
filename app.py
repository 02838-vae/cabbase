import streamlit as st
import streamlit.components.v1 as components
import random
import time
import os
import base64

# --- Cấu hình cơ bản ---
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide", initial_sidebar_state="collapsed")

VIDEO_INTRO = "airplane.mp4"
PC_BACKGROUND = "cabbase.jpg"
MOBILE_BACKGROUND = "mobile.jpg"

if "intro_complete" not in st.session_state:
    st.session_state["intro_complete"] = False


# --- Hàm hỗ trợ ---
def get_base64_image(path):
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# --- Màn hình intro (HTML thuần, ẩn toàn bộ Streamlit) ---
def intro_screen():
    if not os.path.exists(VIDEO_INTRO):
        st.error("Không tìm thấy video airplane.mp4")
        time.sleep(1)
        st.session_state["intro_complete"] = True
        st.rerun()
        return

    with open(VIDEO_INTRO, "rb") as f:
        video_bytes = f.read()
    video_b64 = base64.b64encode(video_bytes).decode()

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
                top: 0; left: 0;
                width: 100vw; height: 100vh;
                object-fit: cover;
            }}
            #intro-text {{
                position: fixed;
                bottom: 12%;
                left: 50%;
                transform: translateX(-50%);
                font-size: clamp(1em, 4vw, 1.6em);
                color: white;
                font-family: 'Times New Roman', serif;
                text-shadow: 2px 2px 8px black;
                animation: fadeInOut 6s forwards;
                white-space: nowrap;
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

    # Render HTML toàn màn hình, ẩn toàn bộ Streamlit
    components.html(intro_html, height=800, width=None)
    time.sleep(7)
    st.session_state["intro_complete"] = True
    st.rerun()


# --- CSS cho trang chính ---
def apply_main_css(pc_img, mobile_img):
    st.markdown(f"""
    <style>
    [data-testid="stDecoration"], header, footer, 
    [data-testid="stToolbar"], svg, [title*="keyboard"],
    [tabindex="0"][aria-live] {{
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
    pc_img = get_base64_image(PC_BACKGROUND)
    mobile_img = get_base64_image(MOBILE_BACKGROUND)
    apply_main_css(pc_img, mobile_img)

    # Sidebar nhạc nền
    music_files = [
        "background.mp3", "background1.mp3", "background2.mp3",
        "background3.mp3", "background4.mp3", "background5.mp3"
    ]
    available = [m for m in music_files if os.path.exists(m)]
    if available:
        with st.sidebar:
            st.subheader("🎵 Nhạc nền")
            track = random.choice(available)
            st.audio(track, format="audio/mp3")
            st.caption(f"Đang phát: {track}")

    # Tiêu đề chính
    st.markdown("<h1>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)


# --- Logic ---
if st.session_state["intro_complete"]:
    main_page()
else:
    intro_screen()
