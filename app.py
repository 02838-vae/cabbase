import streamlit as st
import streamlit.components.v1 as components
import random
import base64
import os
import time

# === Cấu hình cơ bản ===
st.set_page_config(layout="wide", page_title="Tổ Bảo Dưỡng Số 1")

# === File Tài Nguyên ===
VIDEO_INTRO = "airplane.mp4"
PC_BACKGROUND = "cabbase.jpg"
MOBILE_BACKGROUND = "mobile.jpg"
MUSIC_FILES = [
    "background.mp3", "background2.mp3",
    "background3.mp3", "background4.mp3", "background5.mp3"
]

# === Khởi tạo session state ===
if "intro_complete" not in st.session_state:
    st.session_state["intro_complete"] = False


# === Hàm tiện ích ===
def get_base64_file(filepath):
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode()


# === CSS nền chính ===
def apply_main_css():
    css = f"""
    <style>
    /* Ẩn toàn bộ thanh toolbar và icon Streamlit */
    [data-testid="stDecoration"],
    header, footer, [data-testid="stToolbar"], iframe,
    svg, [title*="keyboard"], [tabindex="0"][aria-live] {{
        display: none !important;
        visibility: hidden !important;
    }}

    /* Nền trang */
    .stApp {{
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        transition: background-image 1s ease-in-out;
        min-height: 100vh;
    }}
    .main-bg {{
        background-image: url("{PC_BACKGROUND}");
    }}
    @media only screen and (max-width: 768px) {{
        .main-bg {{
            background-image: url("{MOBILE_BACKGROUND}");
        }}
    }}

    /* Font & màu cổ điển */
    h1, .stText, p, .stMarkdown, label {{
        font-family: 'Times New Roman', serif;
        color: #4E342E;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# === Màn hình intro ===
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
                font-size: clamp(1em, 4vw, 1.6em);
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
                z-index: 2000;
            }}
        </style>
    </head>
    <body>
        <video autoplay muted playsinline preload="auto">
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="fadeout"></div>
        <script>
            // Sau 6s làm tối dần và báo về Streamlit
            setTimeout(() => {{
                document.getElementById("fadeout").style.opacity = 1;
                setTimeout(() => {{
                    window.parent.postMessage({{type: "intro_done"}}, "*");
                }}, 1000);
            }}, 6000);
        </script>
    </body>
    </html>
    """

    components.html(intro_html, height=800, scrolling=False)
    time.sleep(7)
    st.session_state["intro_complete"] = True
    st.rerun()


# === Trang chính ===
def main_page():
    apply_main_css()

    st.markdown('<div class="stApp main-bg">', unsafe_allow_html=True)

    # Thanh nhạc
    with st.sidebar:
        st.subheader("🎶 Nhạc Nền")
        random_track = random.choice(MUSIC_FILES)
        st.audio(random_track, format="audio/mp3", start_time=0)
        st.caption(f"Đang phát: **{random_track}**")

    # Tiêu đề chính
    st.markdown("""
        <h1 style='text-align: center;
                   font-size: 3.5em;
                   text-shadow: 1px 1px 2px #FFF8DC;
                   margin-top: 40px;'>
            TỔ BẢO DƯỠNG SỐ 1
        </h1>
    """, unsafe_allow_html=True)

    # Khoảng trống
    st.markdown('<div style="height: 60vh;"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# === Logic chính ===
if st.session_state["intro_complete"]:
    main_page()
else:
    intro_screen()
