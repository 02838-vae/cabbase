import streamlit as st
import base64
import os
import time

# ==========================
# ⚙️ CẤU HÌNH CHUNG
# ==========================
st.set_page_config(page_title="Airplane Intro", layout="wide", initial_sidebar_state="collapsed")

# ===== HÀM PHỤ TRỢ =====
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# ==========================
# ⚙️ KHỞI TẠO TRẠNG THÁI
# ==========================
if "show_main" not in st.session_state:
    st.session_state.show_main = False
if "video_played" not in st.session_state:
    st.session_state.video_played = False
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

video_file = "airplane.mp4"

# ==========================
# 🧩 CSS ẨN GIAO DIỆN STREAMLIT
# ==========================
st.markdown("""
    <style>
    [data-testid="stSidebar"], [data-testid="stToolbar"], header, footer {display: none !important;}
    html, body, [class*="stAppViewContainer"], [class*="stApp"], [class*="stMainBlockContainer"] {
        margin: 0;
        padding: 0;
        height: 100%;
        overflow: hidden;
        background: black;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================
# 🎥 VIDEO INTRO
# ==========================
if not st.session_state.show_main:
    if os.path.exists(video_file):
        video_data = get_base64(video_file)

        st.markdown(f"""
        <style>
        html, body, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"] {{
            margin: 0 !important;
            padding: 0 !important;
            background: black !important;
            overflow: hidden !important;
            height: 100vh !important;
        }}
        [data-testid="stHeader"] {{
            display: none !important;
        }}
        .video-container {{
            position: fixed;
            inset: 0;
            width: 100vw;
            height: 100vh;
            background: black;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9998;
            overflow: hidden;
        }}
        .video-bg {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: center center;
            z-index: 9997;
        }}
        @media (max-width: 768px) {{
            .video-bg {{
                object-fit: contain !important;
                object-position: center center !important;
                background-color: black;
            }}
        }}
        .intro-text {{
            position: absolute;
            bottom: 12vh;
            width: 100%;
            text-align: center;
            font-family: 'Special Elite', cursive;
            font-size: 42px;
            font-weight: bold;
            color: #ffffff;
            text-shadow:
                0 0 20px rgba(255,255,255,0.8),
                0 0 40px rgba(180,220,255,0.6),
                0 0 60px rgba(255,255,255,0.4);
            opacity: 0;
            animation:
                appear 3s ease-in forwards,
                floatFade 3s ease-in 5s forwards;
            z-index: 9999;
        }}
        @keyframes appear {{
            0% {{ opacity: 0; filter: blur(8px); transform: translateY(40px); }}
            100% {{ opacity: 1; filter: blur(0); transform: translateY(0); }}
        }}
        @keyframes floatFade {{
            0% {{ opacity: 1; filter: blur(0); transform: translateY(0); }}
            100% {{ opacity: 0; filter: blur(12px); transform: translateY(-30px) scale(1.05); }}
        }}
        </style>

        <div class="video-container">
            <video class="video-bg" autoplay muted playsinline>
                <source src="data:video/mp4;base64,{video_data}" type="video/mp4">
            </video>
            <div class="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.video_played:
            st.session_state.video_played = True
            time.sleep(8.5)  # Thời gian video intro
            st.session_state.show_main = True
            st.rerun()
        st.stop()
    else:
        st.error("❌ Không tìm thấy file airplane.mp4")
        st.stop()

# ---------- TRANG CHÍNH ----------
st.session_state.intro_done = True

# Lấy base64 ảnh nền
bg_path = "cabbase.jpg"
bg_base64 = get_base64(bg_path) if os.path.exists(bg_path) else None

# ========== CSS + HTML ==========
if bg_base64:
    st.markdown(f"""
        <style>
        html, body {{
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            overflow: hidden;
            background: none;
        }}
        [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"],
        [data-testid="stSidebar"], header, footer, [data-testid="stToolbar"] {{
            display: none !important;
        }}

        /* Toàn bộ nền và mờ overlay */
        .bg-wrapper {{
            position: fixed;
            inset: 0;
            width: 100vw;
            height: 100vh;
            background: url("data:image/jpeg;base64,{bg_base64}") no-repeat center center;
            background-size: cover;
            filter: brightness(0.9) sepia(0.12) contrast(1.05);
            z-index: -2;
        }}
        .bg-overlay {{
            position: fixed;
            inset: 0;
            width: 100%;
            height: 100%;
            background: rgba(245,230,200,0.22);
            backdrop-filter: blur(2px);
            z-index: -1;
        }}

        /* Hộp nội dung chính */
        .main-box {{
            position: relative;
            z-index: 10;
            background-color: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(2px);
            border-radius: 20px;
            padding: 3rem;
            box-shadow: 0 4px 25px rgba(0,0,0,0.25);
            max-width: 900px;
            margin: 15vh auto 0 auto;
            text-align: center;
            font-family: 'Georgia', serif;
        }}
        .main-box h1 {{
            font-size: 2.2rem;
            color: #2a2a2a;
            text-shadow: 0 0 6px rgba(255,255,255,0.6);
            margin-bottom: 1rem;
        }}
        .main-box p {{
            font-size: 1.2rem;
            color: #2e2e2e;
        }}
        </style>

        <div class="bg-wrapper"></div>
        <div class="bg-overlay"></div>
    """, unsafe_allow_html=True)
else:
    st.error("❌ Không tìm thấy file nền 'cabbase.jpg'")

# ========== Nội dung ==========
st.markdown("<div class='main-box'>", unsafe_allow_html=True)
st.title("✈️ TỔ BẢO DƯỠNG SỐ 1")
st.write("Video intro đã kết thúc — Chào mừng bạn đến với website 🌍")
st.markdown("</div>", unsafe_allow_html=True)






