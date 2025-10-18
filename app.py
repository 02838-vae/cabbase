import streamlit as st
import os
import base64
import random
import time
# Import thư viện mới
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components
import html

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
    st.session_state.is_mobile = None # Khởi tạo là None, chờ xác định

# --- XÁC ĐỊNH THIẾT BỊ DÙNG USER AGENT ---
if st.session_state.is_mobile is None:
    # 1. Lấy chuỗi User Agent từ trình duyệt
    ua_string = st_javascript("""window.navigator.userAgent;""")
    
    if ua_string:
        # 2. Phân tích chuỗi User Agent
        user_agent = parse(ua_string)
        
        # 3. Cập nhật trạng thái
        st.session_state.is_mobile = not user_agent.is_pc
        st.session_state.intro_loading_status = None # Reset trạng thái load
        st.rerun()
    else:
        # Hiển thị thông báo khi đang chờ JS phản hồi (chỉ ở lần chạy đầu tiên)
        st.info("Đang xác định thiết bị...")
        st.stop() # Dừng luồng cho đến khi JS trả lời

# ================== ẨN HEADER STREAMLIT ==================
def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ================== MÀN HÌNH INTRO (Đã tối ưu full screen và Autoplay) ==================
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    
    video_path = VIDEO_MOBILE if is_mobile else VIDEO_PC
    
    if not os.path.exists(video_path):
        st.error(f"⚠️ Không tìm thấy video: {video_path}")
        st.session_state.intro_done = True
        st.rerun()
        return

    # Mã hóa video thành base64 (chỉ video được chọn)
    with open(video_path, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()

    # THAY ĐỔI QUAN TRỌNG: Thiết lập chiều cao và rộng 100vh/100vw triệt để
    intro_html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        html, body {{ 
            margin: 0 !important; padding: 0 !important; 
            height: 100vh; width: 100vw; 
            overflow: hidden; background-color: black; 
        }}
        video {{ 
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
            
            // Hàm chuyển trang sau khi hoàn tất
            const finishIntro = () => {{
                fade.style.opacity = 1;
                setTimeout(() => {{
                    window.parent.postMessage({{"type": "intro_done"}}, "*");
                }}, 1200);
            }};

            vid.onended = finishIntro;
            
            // Xử lý chặn Autoplay hoặc lỗi
            vid.play().catch(error => {{
                console.log("Autoplay blocked or failed, waiting 9 seconds.");
                setTimeout(finishIntro, 9000); 
            }});
        </script>
    </body>
    </html>
    """
    
    # Sử dụng height lớn để bao trùm và tránh lỗi chia đôi
    components.html(intro_html, height=1000, scrolling=False) 

    # --- Cơ chế Chuyển Trang dựa trên thời gian (fallback) ---
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()
    
    # Rerun cho đến khi hết 9.5 giây
    if time.time() - st.session_state.start_time < 9.5: 
        time.sleep(1) 
        st.rerun()
    else:
        # Hoàn thành sau khi hết thời gian chờ
        st.session_state.intro_done = True
        del st.session_state.start_time
        st.rerun()


# ================== TRANG CHÍNH ==================
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    
    # Đọc và mã hóa ảnh nền thành Base64
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

    # Nhạc nền
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

# Sau khi is_mobile đã được xác định (không còn None)
if st.session_state.is_mobile is not None:
    if not st.session_state.intro_done:
        # is_mobile đã có giá trị (True/False)
        intro_screen(st.session_state.is_mobile)
    else:
        # Intro đã xong
        main_page(st.session_state.is_mobile)
