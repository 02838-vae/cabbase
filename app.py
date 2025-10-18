import streamlit as st
import os
import base64
import random
import time
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

# ================== CẤU HÌNH & TRẠNG THÁI ==================
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

# THAY THẾ: Dùng ảnh nền cho màn hình intro (khắc phục lỗi full-screen)
INTRO_BG = "intro_bg.jpg" # <--- Tên file ảnh nền cho intro

VIDEO_PC = "media/airplane.mp4"
VIDEO_MOBILE = "media/mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
MUSIC_FILES = ["background.mp3", "background2.mp3", "background3.mp3", "background4.mp3", "background5.mp3"]

if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = None 
if "start_time" not in st.session_state:
    st.session_state.start_time = None

# --- XÁC ĐỊNH THIẾT BỊ DÙNG USER AGENT ---
if st.session_state.is_mobile is None:
    # FIX AUTOPLAY REFRESH: Reset trạng thái khi F5
    st.session_state.intro_done = False
    
    ua_string = st_javascript("""window.navigator.userAgent;""")
    
    if ua_string:
        user_agent = parse(ua_string)
        st.session_state.is_mobile = not user_agent.is_pc
        st.rerun()
    else:
        st.info("Đang xác định thiết bị và tải...")
        st.stop()

# ================== ẨN HEADER STREAMLIT & CSS CHÍNH ==================
def hide_streamlit_ui():
    st.markdown("""
    <style>
    /* Ẩn các thành phần Streamlit mặc định */
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* GHI ĐÈ CONTAINER CHÍNH */
    .stApp, .stApp > header, .main, .block-container, [data-testid="stVerticalBlock"] {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100vw !important; 
        width: 100vw !important;
        min-height: 100vh !important;
    }
    
    /* Đảm bảo iFrame của components.html vẫn full screen */
    [data-testid*="stHtmlComponents"] {
        position: fixed !important; 
        top: 0;
        left: 0;
        width: 100vw !important;
        height: 100vh !important;
        z-index: 9999; 
    }
    
    /* Các quy tắc bổ sung */
    .stApp > div, .st-emotion-cache-1jicfl2, .st-emotion-cache-z5in9b, .st-emotion-cache-1cypn32 { 
        padding: 0 !important;
        margin: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)


# -------------------------------------------------------------
## 🎬 MÀN HÌNH INTRO CUỐI CÙNG (Sử dụng Ảnh nền và Video ẩn)
# -------------------------------------------------------------
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    
    video_path = VIDEO_MOBILE if is_mobile else VIDEO_PC
    
    if not os.path.exists(video_path) or not os.path.exists(INTRO_BG):
        st.error(f"⚠️ Không tìm thấy file video hoặc ảnh nền intro.")
        st.session_state.intro_done = True
        st.rerun()
        return

    # MÃ HÓA ẢNH NỀN THÀNH BASE64
    with open(INTRO_BG, "rb") as f:
        bg_b64 = base64.b64encode(f.read()).decode()

    # KHÔNG MÃ HÓA VIDEO - CHỈ DÙNG ĐƯỜNG DẪN CỤC BỘ TRONG THẺ VIDEO ẨN
    # Video sẽ chạy ẩn để kích hoạt sự kiện "onended" và Autoplay
    
    intro_html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        /* SỬ DỤNG ẢNH NỀN CSS ĐỂ TẠO HIỆU ỨNG FULL-SCREEN */
        html, body {{ 
            margin: 0 !important; padding: 0 !important; 
            height: 100vh; width: 100vw; 
            overflow: hidden; 
            background-image: url("data:image/jpeg;base64,{bg_b64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-color: black; 
            font-family: 'Arial', sans-serif; 
        }}
        /* ẨN VIDEO - CHỈ DÙNG ĐỂ CHẠY AUTOPLAY/TIMER */
        video {{ 
            display: none; 
            opacity: 0;
        }}
        #intro-text {{
            position: fixed; bottom: 18%; left: 50%; transform: translateX(-50%);
            font-size: clamp(18px, 2.5vw, 40px); color: white; z-index: 10;
            text-shadow: 2px 2px 6px rgba(0,0,0,0.8);
            animation: fadeInOut 6s ease-in-out forwards;
        }}
        @keyframes fadeInOut {{
            0% {{ opacity: 0; transform: translate(-50%, 20px); }} 20% {{ opacity: 1; transform: translate(-50%, 0); }}
            80% {{ opacity: 1; transform: translate(-50%, 0); }} 100% {{ opacity: 0; transform: translate(-50%, -10px); }}
        }}
        #fade {{
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: black; opacity: 0; z-index: 10;
            transition: opacity 1.2s ease-in-out;
        }}
    </style>
    </head>
    <body>
        <video id="introVid" autoplay muted playsinline>
            <source src="{video_path}" type="video/mp4"> 
        </video>
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="fade"></div>
        <script>
            const vid = document.getElementById("introVid");
            const fade = document.getElementById("fade");

            const finishIntro = () => {{
                fade.style.opacity = 1;
                setTimeout(() => {{
                    // Gửi tín hiệu hoàn thành intro
                    window.parent.postMessage({{"type": "intro_done"}}, "*");
                }}, 1200);
            }};

            // Dùng onended nếu trình duyệt cho phép autoplay
            vid.onended = finishIntro;
            
            // Xử lý chặn Autoplay bằng cách cố gắng play và fallback về timer
            vid.play().catch(error => {{
                console.log("Autoplay blocked, falling back to timer.");
                // Tự động chuyển trang sau 9 giây nếu Autoplay bị chặn
                setTimeout(finishIntro, 9000); 
            }});
        </script>
    </body>
    </html>
    """
    
    components.html(intro_html, scrolling=False) 

    # --- Cơ chế Chuyển Trang dựa trên thời gian (Cơ chế dự phòng) ---
    # Luôn giữ cơ chế dự phòng này để đảm bảo chuyển trang nếu JS bị lỗi
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()
    
    if time.time() - st.session_state.start_time < 9.5: 
        time.sleep(1) 
        st.rerun()
    else:
        st.session_state.intro_done = True
        st.session_state.start_time = None 
        st.rerun()


# -------------------------------------------------------------
## 🖼️ TRANG CHÍNH (Giữ Nguyên)
# -------------------------------------------------------------
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


# -------------------------------------------------------------
## ⚙️ LUỒNG CHÍNH
# -------------------------------------------------------------
hide_streamlit_ui()

if st.session_state.is_mobile is None:
    pass 
elif not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
else:
    main_page(st.session_state.is_mobile)
