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
    # FIX AUTOPLAY REFRESH
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
## 🎬 MÀN HÌNH INTRO CUỐI CÙNG (Video Base64 + CSS Background + Click Play)
# -------------------------------------------------------------
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    
    video_path = VIDEO_MOBILE if is_mobile else VIDEO_PC
    
    if not os.path.exists(video_path):
        st.error(f"⚠️ Không tìm thấy video: {video_path}.")
        time.sleep(3)
        st.session_state.intro_done = True
        st.rerun()
        return

    # SỬ DỤNG BASE64 LẠI ĐỂ ĐẢM BẢO VIDEO LOAD ĐƯỢC
    with open(video_path, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()
    
    intro_html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        /* CSS CHUNG */
        html, body {{ 
            margin: 0 !important; padding: 0 !important; 
            height: 100vh; width: 100vw; 
            overflow: hidden; background-color: black; 
            font-family: 'Arial', sans-serif; 
            position: relative; 
        }}
        /* KỸ THUẬT VIDEO BACKGROUND FULL-SCREEN MẠNH MẼ */
        #introVid {{ 
            position: absolute; 
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            min-width: 100%; 
            min-height: 100%; 
            width: auto; height: auto;
            object-fit: cover; /* Đảm bảo video che phủ toàn bộ */
            z-index: -1; 
        }}
        /* NÚT PLAY VÀ LỚP PHỦ */
        #overlay {{
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(0, 0, 0, 0.8);
            z-index: 100;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            transition: opacity 0.5s;
        }}
        #playButton {{
            background: #4A90E2; 
            color: white; 
            border: none; 
            padding: 15px 30px; 
            font-size: 24px; 
            cursor: pointer;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            transition: background 0.3s;
        }}
        #playButton:hover {{
            background: #357ABD;
        }}

        #intro-text {{
            position: fixed; bottom: 18%; left: 50%; transform: translateX(-50%);
            font-size: clamp(18px, 2.5vw, 40px); color: white; z-index: 10;
            text-shadow: 2px 2px 6px rgba(0,0,0,0.8);
            /* Loại bỏ animation để chỉ hiển thị khi video chạy */
            opacity: 0; 
            transition: opacity 1s;
        }}
        #fade {{
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: black; opacity: 0; z-index: 10;
            transition: opacity 1.2s ease-in-out;
        }}
    </style>
    </head>
    <body>
        <video id="introVid" muted playsinline loop=false>
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4"> 
        </video>

        <div id="overlay">
            <button id="playButton">▶️ BẮT ĐẦU</button>
            <p style="color: white; margin-top: 20px;">Nhấn để xem giới thiệu</p>
        </div>

        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="fade"></div>
        
        <script>
            const vid = document.getElementById("introVid");
            const fade = document.getElementById("fade");
            const overlay = document.getElementById("overlay");
            const playButton = document.getElementById("playButton");
            const introText = document.getElementById("intro-text");


            const finishIntro = () => {{
                fade.style.opacity = 1;
                setTimeout(() => {{
                    // Gửi tín hiệu hoàn thành intro
                    window.parent.postMessage({{"type": "intro_done"}}, "*");
                }}, 1200);
            }};

            vid.onended = finishIntro;
            
            // Xử lý sự kiện click nút Play
            playButton.addEventListener('click', () => {{
                // Cố gắng chạy video
                const playPromise = vid.play();
                
                if (playPromise !== undefined) {{
                    playPromise.then(() => {{
                        // Chạy thành công: Ẩn overlay và hiển thị chữ
                        overlay.style.opacity = 0;
                        setTimeout(() => {{ overlay.style.display = 'none'; }}, 500);
                        introText.style.opacity = 1; // Hiển thị chữ sau khi video chạy

                    }}).catch(error => {{
                        console.error("Lỗi phát video sau khi tương tác:", error);
                        // Fallback: Ẩn overlay và bắt đầu timer nếu lỗi
                        overlay.style.opacity = 0;
                        setTimeout(() => {{ overlay.style.display = 'none'; }}, 500);
                        introText.style.opacity = 1;
                        setTimeout(finishIntro, 9000); // Bắt đầu timer dự phòng
                    }});
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    components.html(intro_html, scrolling=False) 

    # --- Cơ chế Chuyển Trang dựa trên thời gian (Cơ chế dự phòng Python) ---
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()
    
    # Giữ timer Python dự phòng để đảm bảo chuyển cảnh kể cả khi JS lỗi
    if time.time() - st.session_state.start_time < 12.0: # Tăng thời gian chờ thêm 3s cho người dùng nhấn nút
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
    #... (Giữ nguyên hàm main_page)
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
## ⚙️ LUỒNG CHÍNH (Giữ Nguyên)
# -------------------------------------------------------------
hide_streamlit_ui()

if st.session_state.is_mobile is None:
    pass 
elif not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
else:
    main_page(st.session_state.is_mobile)
