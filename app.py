import streamlit as st
import base64
import time
import os

# ==============================
# 🔧 Đường dẫn tài nguyên
# ==============================
INTRO_VIDEO = "assets/intro.mp4"
BG_PC = "assets/background_pc.jpg"
BG_MOBILE = "assets/background_mobile.jpg"

# ==============================
# Ẩn giao diện Streamlit mặc định
# ==============================
def hide_streamlit_ui():
    st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding: 0 !important;
        margin: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================
# Hiệu ứng intro video
# ==============================
def intro_screen(is_mobile=False):
    try:
        with open(INTRO_VIDEO, "rb") as f:
            video_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        st.error("❌ Không tìm thấy file intro.mp4 trong thư mục assets/")
        st.stop()

    st.markdown(f"""
    <style>
    html, body {{
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        background: black !important;
        width: 100vw !important;
        height: 100vh !important;
    }}
    video {{
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        object-fit: cover !important;
        background: black !important;
        z-index: 1000 !important;
    }}
    </style>

    <video autoplay muted playsinline id="intro-video">
        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
    </video>

    <script>
    setTimeout(() => {{
        const iframe = window.parent.document.querySelector('iframe');
        if (iframe) iframe.style.display = 'none';
    }}, 2000);
    </script>
    """, unsafe_allow_html=True)

    # Tạm dừng để video chạy xong (khoảng 2.5s)
    time.sleep(2.5)

# ==============================
# Trang chính (main UI)
# ==============================
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    try:
        with open(bg, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError as e:
        st.error(f"Lỗi: Không tìm thấy file tài nguyên: {e.filename}")
        st.stop()

    st.markdown(f"""
    <style>
    html, body, .stApp {{
        height: 100vh !important;
        background:
            linear-gradient(to bottom, rgba(255, 235, 200, 0.25) 0%, rgba(160, 130, 90, 0.35) 50%, rgba(90, 70, 50, 0.5) 100%),
            url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed !important;
        background-size: cover !important;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
        position: relative;
        filter: brightness(1.05) contrast(1.1) saturate(1.05);
        animation: cinematicReveal 2.5s ease-out forwards;
        transform-origin: center;
    }}

    @keyframes cinematicReveal {{
        0% {{ opacity: 0; transform: scale(1.05); filter: blur(8px); }}
        50% {{ opacity: 1; transform: scale(1.02); filter: blur(2px); }}
        100% {{ opacity: 1; transform: scale(1.0); filter: blur(0px); }}
    }}

    /* Tiêu đề chính */
    .welcome {{
        position: absolute;
        top: 8%;
        left: 50%;
        transform: translateX(-50%);
        width: 100%;
        text-align: center;
        font-size: clamp(38px, 5vw, 70px);
        font-weight: 700;
        font-family: 'Playfair Display', serif;
        letter-spacing: 2px;
        color: #fff8dc;
        text-shadow:
            0 0 15px rgba(255, 230, 180, 0.8),
            0 0 30px rgba(255, 200, 100, 0.5),
            0 0 45px rgba(255, 255, 200, 0.3);
        background: linear-gradient(120deg, #ffefb0 20%, #fff7d6 40%, #fceea0 60%);
        background-size: 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        -webkit-text-stroke: 1px rgba(255, 255, 200, 0.6);
        animation: textGlow 6s linear infinite, fadeIn 2.5s ease-out forwards, lightSweep 6s ease-in-out infinite;
        z-index: 10;
        overflow: hidden;
    }}

    /* Hiệu ứng gradient chuyển động */
    @keyframes textGlow {{
        0% {{ background-position: 200% 0%; }}
        100% {{ background-position: -200% 0%; }}
    }}

    /* Hiệu ứng xuất hiện mượt */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translate(-50%, 15px); }}
        to {{ opacity: 1; transform: translate(-50%, 0); }}
    }}

    /* Ánh sáng quét ngang chữ */
    .welcome::before {{
        content: "";
        position: absolute;
        top: 0;
        left: -75%;
        width: 50%;
        height: 100%;
        background: linear-gradient(120deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.8) 50%, rgba(255,255,255,0) 100%);
        transform: skewX(-20deg);
        animation: sweep 4.5s ease-in-out infinite;
        z-index: 11;
    }}

    @keyframes sweep {{
        0% {{ left: -75%; opacity: 0; }}
        20% {{ left: -75%; opacity: 0.5; }}
        50% {{ left: 130%; opacity: 0.7; }}
        100% {{ left: 130%; opacity: 0; }}
    }}
    </style>

    <div class="welcome">✈️ TỔ BẢO DƯỠNG SỐ 1 ✈️</div>
    """, unsafe_allow_html=True)

# ==============================
# App logic
# ==============================
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = st.experimental_get_query_params().get("mobile", ["false"])[0] == "true"

if not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
    st.session_state.intro_done = True
    st.rerun()
else:
    main_page(st.session_state.is_mobile)
