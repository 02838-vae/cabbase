import streamlit as st
import os
import random
import time
import base64 
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

# ================== CẤU HÌNH & TRẠNG THÁI (Giữ Nguyên) ==================
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

# GIẢ ĐỊNH: VIDEO ĐƯỢC ĐẶT TRONG THƯ MỤC media/
VIDEO_PC = "media/airplane.mp4"
VIDEO_MOBILE = "media/mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
MUSIC_FILES = ["background.mp3", "background2.mp3", "background3.mp3", "background4.mp3", "background5.mp3"]

if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = None 

# --- XÁC ĐỊNH THIẾT BỊ DÙNG USER AGENT (Giữ Nguyên) ---
if st.session_state.is_mobile is None:
    ua_string = st_javascript("""window.navigator.userAgent;""")
    
    if ua_string:
        user_agent = parse(ua_string)
        st.session_state.is_mobile = not user_agent.is_pc
        st.rerun()
    else:
        st.info("Đang xác định thiết bị và tải...")
        st.stop()

# ================== ẨN HEADER STREAMLIT & BẬT FULL SCREEN CSS TỐI ƯU ==================
def hide_streamlit_ui():
    st.markdown("""
    <style>
    /* 1. Ẩn các thành phần Streamlit mặc định */
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* 2. GHI ĐÈ CSS CỦA STREAMLIT TỐI ƯU (Bao gồm cả container chính và block-container) */
    .stApp, .stApp > header, .main, .block-container, 
    [data-testid="stVerticalBlock"] {
        padding: 0 !important;
        margin: 0 !important;
        /* QUAN TRỌNG: Đảm bảo chiều rộng là 100vw trên mọi container cha */
        max-width: 100vw !important; 
        width: 100vw !important;
        min-height: 100vh !important;
    }
    
    .stApp > div {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* 3. TĂNG ĐỘ ƯU TIÊN CHO THẺ VIDEO WRAPPER */
    .stVideo {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        z-index: 9999;
    }
    
    /* 4. Đảm bảo thẻ <video> bên trong full-screen */
    .stVideo > video {
        width: 100% !important;
        height: 100% !important;
        object-fit: cover !important;
    }

    /* 5. Quy tắc bổ sung để khắc phục lỗi padding/margin trên mobile */
    .st-emotion-cache-1jicfl2, .st-emotion-cache-z5in9b, .st-emotion-cache-1cypn32 { 
        padding: 0 !important;
        margin: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ================== MÀN HÌNH INTRO TỐI GIẢN (Dùng st.video) ==================
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    
    video_path = VIDEO_MOBILE if is_mobile else VIDEO_PC
    
    if not os.path.exists(video_path):
        st.error(f"⚠️ Không tìm thấy video: {video_path}")
        st.session_state.intro_done = True
        st.rerun()
        return

    # SỬ DỤNG st.video THAY VÌ components.html/Base64
    # Không cần dùng columns [0.01, 0.98, 0.01] nữa vì CSS đã làm việc đó
    st.video(video_path, format="video/mp4", start_time=0) 

    # --- Dòng chữ trên video ---
    st.markdown(f"""
    <style>
    #intro-text-final {{
        position: fixed; 
        bottom: 20vh; 
        left: 50%; 
        transform: translateX(-50%);
        font-size: clamp(18px, 3vw, 40px); 
        color: white; 
        z-index: 10000;
        text-shadow: 2px 2px 6px rgba(0,0,0,0.8);
        font-family: 'Arial', sans-serif;
    }}
    </style>
    <div id="intro-text-final">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    """, unsafe_allow_html=True)

    # --- Cơ chế Chuyển Trang dựa trên thời gian ---
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()
    
    if time.time() - st.session_state.start_time < 9.5: 
        time.sleep(1) 
        st.rerun()
    else:
        st.session_state.intro_done = True
        del st.session_state.start_time
        st.rerun()


# ================== TRANG CHÍNH (Giữ Nguyên) ==================
def main_page(is_mobile=False):
    hide_streamlit_ui() 
    bg = BG_MOBILE if is_mobile else BG_PC
    
    try:
        with open(bg, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        st.error(f"⚠️ Không tìm thấy ảnh nền: {bg}")
        bg_b64 = ""

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&display=swap');
    .stApp {{
        background-image: url("data:image/jpeg;base64,{bg_b64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        animation: fadeInBg 1s ease-in-out forwards;
    }}
    @keyframes fadeInBg {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    h1 {{
        text-align: center; margin-top: 60px; color: #2E1C14;
        text-shadow: 2px 2px 6px #FFF8DC; font-family: 'Playfair Display', serif;
    }}
    </style>
    """, unsafe_allow_html=True)

    available_music = [m for m in MUSIC_FILES if os.path.exists(m)]
    if available_music:
        chosen = random.choice(available_music)
        with st.sidebar:
            st.subheader("🎵 Nhạc nền")
            st.audio(chosen, start_time=0) 
            st.caption(f"Đang phát: **{os.path.basename(chosen)}**")

    st.markdown("<h1>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)


# ================== LUỒNG CHÍNH (Giữ Nguyên) ==================
hide_streamlit_ui()

if st.session_state.is_mobile is None:
    pass 
elif not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
else:
    main_page(st.session_state.is_mobile)
