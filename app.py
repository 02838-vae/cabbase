import streamlit as st
import os
import base64
import random
import time
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

# ================== CẤU HÌNH ==================
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
MUSIC_FILES = ["background.mp3", "background2.mp3", "background3.mp3", "background4.mp3", "background5.mp3"]

# ================== TRẠNG THÁI ==================
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = None 

# --- XÁC ĐỊNH THIẾT BỊ DÙNG USER AGENT ---
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
    
    /* 2. GHI ĐÈ CSS CỦA STREAMLIT (Sử dụng selector mạnh) */
    /* Đây là quy tắc tổng quát để loại bỏ padding/margin khỏi các container chính */
    .stApp, .stApp > header, .main, .block-container {
        padding: 0 !important;
        margin: 0 !important;
        /* Đảm bảo chiếm toàn bộ không gian */
        max-width: 100vw !important; 
        width: 100vw !important;
        min-height: 100vh !important;
    }
    
    /* 3. Đảm bảo iframe của components.html (video intro) full screen */
    [data-testid*="stHtmlComponents"] {
        /* Chuyển từ fixed sang absolute để tránh xung đột z-index/fixed */
        position: absolute !important; 
        top: 0;
        left: 0;
        width: 100vw !important;
        height: 100vh !important;
        z-index: 9999; 
    }
    
    /* 4. Quy tắc bổ sung để khắc phục lỗi padding/margin trên mobile (thường là .main) */
    /* Sử dụng selector tổng quát cho các phiên bản Streamlit mới */
    .st-emotion-cache-1jicfl2, /* Ví dụ từ bạn */
    .st-emotion-cache-z5in9b, 
    .st-emotion-cache-1cypn32 { 
        padding: 0 !important;
        margin: 0 !important;
    }

    
    </style>
    """, unsafe_allow_html=True)


# ================== MÀN HÌNH INTRO (FULL SCREEN & AUTOPLAY) ==================
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    
    video_path = VIDEO_MOBILE if is_mobile else VIDEO_PC
    
    if not os.path.exists(video_path):
        st.error(f"⚠️ Không tìm thấy video: {video_path}")
        st.session_state.intro_done = True
        st.rerun()
        return

    with open(video_path, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()

    intro_html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        /* QUAN TRỌNG: CSS bên trong components.html */
        html, body {{ 
            margin: 0 !important; padding: 0 !important; 
            height: 100vh; width: 100vw; 
            overflow: hidden; background-color: black; 
        }}
        video {{ 
            position: absolute; /* Đảm bảo video nằm trong iframe */
            top: 0; left: 0;
            width: 100vw; height: 100vh; 
            object-fit: cover; object-position: center; 
        }}
        #intro-text {{
            position: fixed; bottom: 18%; left: 50%; transform: translateX(-50%);
            font-size: clamp(1em, 4vw, 2em); color: white; z-index: 10;
            font-family: 'Playfair Display', serif; text-shadow: 2px 2px 6px rgba(0,0,0,0.8);
            animation: fadeInOut 6s ease-in-out forwards;
        }}
        @keyframes fadeInOut {{
            0% {{ opacity: 0; transform: translate(-50%, 20px); }} 20% {{ opacity: 1; transform: translate(-50%, 0); }}
            80% {{ opacity: 1; transform: translate(-50%, 0); }} 100% {{ opacity: 0; transform: translate(-50%, -10px); }}
        }}
        #fade {{
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: black; opacity: 0; z-index: 10;
            transition: opacity 1s ease-in-out;
        }}
    </style>
    </head>
    <body>
        <video id="introVid" autoplay muted playsinline>
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="fade"></div>
        <script>
            const vid = document.getElementById("introVid");
            const fade = document.getElementById("fade");
            
            const finishIntro = () => {{
                fade.style.opacity = 1;
                setTimeout(() => {{
                    window.parent.postMessage({{"type": "intro_done"}}, "*");
                }}, 1200);
            }};

            vid.onended = finishIntro;
            
            // Xử lý chặn Autoplay: Nếu bị chặn, chờ 9 giây rồi chuyển trang
            vid.play().catch(error => {{
                console.log("Autoplay blocked or failed, waiting 9 seconds.");
                setTimeout(finishIntro, 9000); 
            }});
        </script>
    </body>
    </html>
    """
    
    # Bỏ tham số height để CSS fixed quyết định
    components.html(intro_html, scrolling=False) 

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


# ================== TRANG CHÍNH ==================
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


# ================== LUỒNG CHÍNH ==================
hide_streamlit_ui()

if st.session_state.is_mobile is None:
    pass 
elif not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
else:
    main_page(st.session_state.is_mobile)
