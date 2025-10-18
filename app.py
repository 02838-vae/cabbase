import streamlit as st
import os
import base64
import time
import random
import streamlit.components.v1 as components

# ================== CẤU HÌNH ==================
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

# File assets
VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
MUSIC_FILES = ["background.mp3", "background2.mp3", "background3.mp3", "background4.mp3", "background5.mp3"]

# ================== TRẠNG THÁI ==================
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = None  # chưa xác định


# ================== ẨN HEADER STREAMLIT ==================
def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"],
    header, footer, iframe, [title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ================== XÁC ĐỊNH THIẾT BỊ ==================
def detect_device():
    """Gửi thông tin thiết bị từ JS về Python qua streamlit components"""
    detect_component = """
    <script>
    const isMobile = /Mobi|Android|iPhone|iPad/i.test(navigator.userAgent);
    const streamlitDoc = window.parent.document;
    const streamlitInput = streamlitDoc.querySelector('iframe[srcdoc]') || window.parent;
    streamlitInput.contentWindow.postMessage({type: "streamlit:setComponentValue", value: isMobile}, "*");
    </script>
    """
    components.html(detect_component, height=0, width=0)


# ================== MÀN HÌNH INTRO ==================
def intro_screen(is_mobile=False):
    hide_streamlit_ui()

    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    if not os.path.exists(video_file):
        st.error(f"⚠️ Không tìm thấy file video: {video_file}")
        st.session_state.intro_done = True
        st.rerun()
        return

    with open(video_file, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()

    intro_html = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&display=swap');
    html, body {{
        margin: 0;
        padding: 0;
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
        z-index: 0;
    }}
    #intro-text {{
        position: fixed;
        bottom: 20%;
        left: 50%;
        transform: translateX(-50%);
        font-size: clamp(1em, 4vw, 2.2em);
        color: white;
        font-family: 'Playfair Display', serif;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.7);
        animation: fadeInOut 6s ease-in-out forwards;
        white-space: nowrap;
        z-index: 2;
    }}
    @keyframes fadeInOut {{
        0% {{ opacity: 0; transform: translate(-50%, 10px); }}
        20% {{ opacity: 1; transform: translate(-50%, 0); }}
        80% {{ opacity: 1; transform: translate(-50%, 0); }}
        100% {{ opacity: 0; transform: translate(-50%, -10px); }}
    }}
    #fade {{
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: black;
        opacity: 0;
        z-index: 3;
        transition: opacity 1s ease-in-out;
    }}
    </style>

    <video autoplay muted playsinline id="introVid">
        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
    </video>

    <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    <div id="fade"></div>

    <script>
    const vid = document.getElementById("introVid");
    const fade = document.getElementById("fade");
    vid.onended = () => {{
        fade.style.opacity = 1;
        setTimeout(() => {{
            window.parent.postMessage({{type: "intro_done"}}, "*");
        }}, 1000);
    }};
    </script>
    """
    components.html(intro_html, height=800, scrolling=False)

    time.sleep(9)
    st.session_state.intro_done = True
    st.rerun()


# ================== TRANG CHÍNH ==================
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&display=swap');
    .stApp {{
        background-image: url("{bg}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        animation: fadeInBg 1.5s ease-in forwards;
    }}
    @keyframes fadeInBg {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    h1 {{
        font-family: 'Playfair Display', serif;
        color: #2E1C14;
        text-shadow: 2px 2px 6px #FFF8DC;
    }}
    </style>
    """, unsafe_allow_html=True)

    available_music = [m for m in MUSIC_FILES if os.path.exists(m)]
    if available_music:
        chosen = random.choice(available_music)
        with st.sidebar:
            st.subheader("🎵 Nhạc nền")
            st.audio(chosen)
            st.caption(f"Đang phát: **{os.path.basename(chosen)}**")

    st.markdown("""
    <div style="text-align:center; margin-top:60px;">
        <h1>TỔ BẢO DƯỠNG SỐ 1</h1>
    </div>
    """, unsafe_allow_html=True)


# ================== LUỒNG CHÍNH ==================
hide_streamlit_ui()

if st.session_state.is_mobile is None:
    # Gửi JS để xác định thiết bị
    st.write("🔍 Đang phát hiện thiết bị, vui lòng chờ...")
    is_mobile = components.html(
        """
        <script>
        const isMobile = /Mobi|Android|iPhone|iPad/i.test(navigator.userAgent);
        const streamlitDoc = window.parent.document;
        const streamlitInput = streamlitDoc.querySelector('iframe[srcdoc]') || window.parent;
        streamlitInput.contentWindow.postMessage({type: "streamlit:setComponentValue", value: isMobile}, "*");
        </script>
        """,
        height=0
    )
    # Giả định PC lần đầu (nếu JS chưa kịp phản hồi)
    st.session_state.is_mobile = False
    st.rerun()
else:
    if not st.session_state.intro_done:
        intro_screen(st.session_state.is_mobile)
    else:
        main_page(st.session_state.is_mobile)
