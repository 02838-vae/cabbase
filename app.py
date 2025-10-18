import streamlit as st
import streamlit.components.v1 as components
import random
import time
import os
import base64

# --- Cấu hình trang ---
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide", initial_sidebar_state="collapsed")

# --- File ---
VIDEO_INTRO = "airplane.mp4"
PC_BACKGROUND = "cabbase.jpg"
MOBILE_BACKGROUND = "mobile.jpg"

# --- Session ---
if "intro_complete" not in st.session_state:
    st.session_state["intro_complete"] = False

# --- CSS cho trang chính ---
def apply_css_main():
    st.markdown(f"""
    <style>
    html, body, [data-testid="stAppViewContainer"] {{
        margin: 0 !important;
        padding: 0 !important;
        height: 100% !important;
        overflow: hidden !important;
        background: url("{PC_BACKGROUND}") center center / cover no-repeat fixed !important;
    }}
    @media (max-width: 768px) {{
        html, body, [data-testid="stAppViewContainer"] {{
            background: url("{MOBILE_BACKGROUND}") center center / cover no-repeat fixed !important;
        }}
    }}
    /* Ẩn hoàn toàn header, toolbar, biểu tượng Streamlit */
    header, footer, [data-testid="stToolbar"], [title*="keyboard"], svg[aria-label*="keyboard"], [tabindex="0"][aria-live], [data-testid="stDecoration"] {{
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }}
    h1 {{
        font-family: 'Times New Roman', serif;
        color: #fff8dc;
        text-align: center;
        text-shadow: 2px 2px 8px black;
        font-size: 3.5em;
        margin-top: 30px;
    }}
    </style>
    """, unsafe_allow_html=True)


# --- Intro (hiển thị video full màn hình) ---
def intro_screen():
    if not os.path.exists(VIDEO_INTRO):
        st.error("Không tìm thấy file airplane.mp4")
        time.sleep(2)
        st.session_state["intro_complete"] = True
        st.rerun()
        return

    with open(VIDEO_INTRO, "rb") as f:
        video_data = f.read()
    video_b64 = base64.b64encode(video_data).decode()

    intro_html = f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            html, body {{
                margin: 0;
                padding: 0;
                height: 100%;
                width: 100%;
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
            }}
            #intro-text {{
                position: fixed;
                bottom: 12%;
                left: 50%;
                transform: translateX(-50%);
                font-size: clamp(1em, 4vw, 1.8em);
                color: white;
                font-family: 'Times New Roman', serif;
                text-shadow: 2px 2px 8px black;
                animation: fadeInOut 6s forwards;
                letter-spacing: 2px;
                white-space: nowrap;
            }}
            @keyframes fadeInOut {{
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

    # Dùng full HTML để hiển thị video intro chiếm toàn màn hình
    components.html(intro_html, height=800, width=None)

    # Sau khi video kết thúc, chuyển sang trang chính
    time.sleep(7)
    st.session_state["intro_complete"] = True
    st.rerun()


# --- Trang chính ---
def main_page():
    apply_css_main()

    # Sidebar: nhạc nền ngẫu nhiên
    music_files = [
        "background.mp3", "background1.mp3", "background2.mp3",
        "background3.mp3", "background4.mp3", "background5.mp3"
    ]
    available = [f for f in music_files if os.path.exists(f)]
    if available:
        with st.sidebar:
            track = random.choice(available)
            st.subheader("🎵 Nhạc nền")
            st.audio(track, format="audio/mp3")
            st.caption(f"Đang phát: {track}")

    # Tiêu đề chính
    st.markdown("<h1>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)


# --- Điều hướng ---
if st.session_state["intro_complete"]:
    main_page()
else:
    intro_screen()
