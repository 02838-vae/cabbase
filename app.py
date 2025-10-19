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
MUSIC_FILES = [
    "background.mp3", "background2.mp3", "background3.mp3",
    "background4.mp3", "background5.mp3"
]

# Giả định video intro dài 9 giây
VIDEO_DURATION_SECONDS = 9

if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = None
if "start_time" not in st.session_state:
    st.session_state.start_time = None


# ================== XÁC ĐỊNH THIẾT BỊ ==================
if st.session_state.is_mobile is None:
    st.session_state.intro_done = False
    ua_string = st_javascript("""window.navigator.userAgent;""")

    if ua_string:
        user_agent = parse(ua_string)
        st.session_state.is_mobile = not user_agent.is_pc
        st.rerun()
    else:
        st.info("Đang xác định thiết bị và tải...")
        time.sleep(0.5) 
        st.stop()


# ================== ẨN GIAO DIỆN STREAMLIT ==================
def hide_streamlit_ui():
    """Ẩn các thành phần giao diện mặc định của Streamlit."""
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer,
    iframe[title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
        visibility: hidden !important;
    }

    .stApp, .main, .block-container, [data-testid="stVerticalBlock"] {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100vw !important;
        width: 100vw !important;
        min-height: 100vh !important;
    }

    [data-testid*="stHtmlComponents"] {
        position: fixed !important;
        top: 0; left: 0;
        width: 100vw !important;
        height: 100vh !important;
        z-index: 9999;
    }
    </style>
    """, unsafe_allow_html=True)


# ================== MÀN HÌNH INTRO ==================
def intro_screen(is_mobile=False):
    hide_streamlit_ui()

    video_path = VIDEO_MOBILE if is_mobile else VIDEO_PC
    if not os.path.exists(video_path):
        st.error(f"⚠️ Không tìm thấy video: {video_path}")
        st.session_state.intro_done = True
        st.rerun()
        return

    # Mã hóa video sang Base64 để nhúng vào HTML
    try:
        with open(video_path, "rb") as f:
            video_b64 = base64.b64encode(f.read()).decode()
    except Exception as e:
        st.error(f"Lỗi khi đọc file video: {e}")
        st.session_state.intro_done = True
        st.rerun()
        return

    # --- Cấu hình CSS tùy theo thiết bị ---
    if is_mobile:
        object_position = "center 15%"
        text_bottom = "12%"               
        font_size = "clamp(16px, 4.5vw, 26px)"
        text_width = "92vw"
    else:
        object_position = "center center"
        text_bottom = "20%"
        font_size = "clamp(26px, 3vw, 46px)"
        text_width = "70vw"

    # Đảm bảo text biến mất trước khi video kết thúc
    animation_duration = f"{VIDEO_DURATION_SECONDS - 0.5}s" # 8.5s
    video_duration_ms = VIDEO_DURATION_SECONDS * 1000

    intro_html = f"""
    <html lang="vi">
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&display=swap');

            html, body {{
                margin: 0; padding: 0;
                width: 100vw;
                height: 100vh;
                overflow: hidden;
                background: black;
            }}

            video {{
                position: absolute;
                top: 0; left: 0;
                width: 100vw;
                height: 100vh;
                object-fit: cover;
                object-position: {object_position};
                z-index: 1;
            }}

            #intro-text {{
                position: absolute;
                left: 50%;
                bottom: {text_bottom};
                transform: translateX(-50%);
                font-family: 'Cinzel', serif;
                font-size: {font_size};
                width: {text_width};
                text-align: center;
                color: #fff8dc;
                font-weight: 700;
                letter-spacing: 2px;
                text-shadow: 0 0 6px rgba(255, 255, 255, 0.3), 0 0 18px rgba(255, 240, 180, 0.5);
                z-index: 10;
                opacity: 0;
                animation: fadeAppear {animation_duration} ease-in-out forwards; 
                white-space: normal;
                overflow-wrap: break-word;
            }}

            /* --- CSS CHO CLICK TO PLAY OVERLAY --- */
            #click-to-play-overlay {{
                position: absolute;
                top: 0; left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.6);
                z-index: 15; /* Cao hơn video và text */
                display: flex;
                justify-content: center;
                align-items: center;
                cursor: pointer;
                text-align: center;
                opacity: 1;
                transition: opacity 0.5s;
            }}

            #click-to-play-overlay p {{
                color: white;
                font-size: clamp(20px, 5vw, 36px);
                font-family: Arial, sans-serif;
                text-shadow: 0 0 10px black;
                padding: 20px;
                border: 2px solid white;
                border-radius: 10px;
                animation: pulse 1.5s infinite;
            }}

            @keyframes pulse {{
                0% {{ transform: scale(1); opacity: 0.8; }}
                50% {{ transform: scale(1.05); opacity: 1; }}
                100% {{ transform: scale(1); opacity: 0.8; }}
            }}
            /* ------------------------------------- */

            /* cinematic fade xuất hiện – sáng – tan biến */
            @keyframes fadeAppear {{
                0% {{
                    opacity: 0;
                    transform: translate(-50%, 40px);
                    text-shadow: none;
                }}
                25% {{
                    opacity: 1;
                    text-shadow: 0 0 10px rgba(255, 240, 180, 0.8), 0 0 20px rgba(255,255,255,0.4);
                    transform: translate(-50%, 0);
                }}
                70% {{
                    opacity: 1;
                    text-shadow: 0 0 16px rgba(255, 255, 220, 0.8);
                }}
                100% {{
                    opacity: 0; 
                    transform: translate(-50%, -30px);
                    text-shadow: 0 0 2px rgba(255,255,255,0.1);
                }}
            }}

            #fade {{
                position: absolute;
                top: 0; left: 0;
                width: 100%;
                height: 100%;
                background: black;
                opacity: 0;
                z-index: 9;
                transition: opacity 1.2s ease-in-out;
            }}
        </style>
    </head>
    <body>
        <video id="introVid" autoplay muted playsinline>
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="fade"></div>
        
        <div id="click-to-play-overlay">
            <p>CHẠM ĐỂ BẮT ĐẦU</p>
        </div>

        <script>
            const vid = document.getElementById("introVid");
            const fade = document.getElementById("fade");
            const overlay = document.getElementById("click-to-play-overlay");
            const videoDurationMs = {video_duration_ms};

            function finishIntro() {{
                fade.style.opacity = 1;
                setTimeout(() => {{
                    window.parent.postMessage({{"type": "intro_done"}}, "*");
                }}, 1200);
            }}

            // Xử lý sự kiện khi người dùng chạm vào overlay
            overlay.addEventListener('click', function() {{
                vid.play().then(() => {{
                    // Phát thành công, ẩn overlay và bắt đầu animation text
                    overlay.style.opacity = 0;
                    document.getElementById("intro-text").style.animationPlayState = 'running';

                    setTimeout(() => {{
                        overlay.style.display = 'none';
                    }}, 500);

                }}).catch(error => {{
                    console.error("Lỗi khi cố gắng phát video:", error);
                    // Nếu vẫn lỗi, chuyển sang cơ chế dự phòng sau thời gian video
                    finishIntro();
                }});
            }});

            // Nếu video kết thúc tự nhiên (chỉ khi đã phát thành công)
            vid.onended = finishIntro;
            
            // Cố gắng tự động phát
            vid.play().then(() => {{
                console.log("Autoplay thành công.");
                // Nếu thành công, ẩn ngay overlay và cho phép text animation chạy
                overlay.style.display = 'none';
            }}).catch(() => {{
                console.log("Autoplay bị chặn, hiển thị overlay 'Click to Play' và dừng animation text.");
                // Dừng animation text cho đến khi người dùng chạm
                document.getElementById("intro-text").style.animationPlayState = 'paused';
                
                // Thiết lập timeout dự phòng nếu người dùng không tương tác
                setTimeout(finishIntro, videoDurationMs); 
            }});
        </script>
    </body>
    </html>
    """

    components.html(intro_html, height=950, scrolling=False)

    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()
    # Cơ chế dự phòng Python
    if time.time() - st.session_state.start_time < (VIDEO_DURATION_SECONDS + 0.5):
        time.sleep(1)
        st.rerun()
    else:
        st.session_state.intro_done = True
        st.session_state.start_time = None
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
        text-shadow: 2px 2px 6px #FFF8DC;
        font-family: 'Playfair Display', serif;
    }}
    /* Đảm bảo sidebar hiển thị nếu có nhạc nền */
    [data-testid="stSidebar"] {{
        visibility: visible !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    available_music = [m for m in MUSIC_FILES if os.path.exists(m)]
    if available_music:
        chosen = random.choice(available_music)
        # Sử dụng st.sidebar thay vì st.container() cho nhạc nền
        with st.sidebar:
            st.subheader("🎵 Nhạc nền")
            st.audio(chosen, start_time=0, loop=True) # Thêm loop=True để nhạc lặp lại
            st.caption(f"Đang phát: **{os.path.basename(chosen)}**")

    st.markdown("<h1>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)
    
    # Bạn có thể thêm nội dung trang chính ở đây, ví dụ:
    st.markdown("---")
    st.write("Chào mừng đến với trang chính của ứng dụng!")


# ================== LUỒNG CHÍNH ==================
hide_streamlit_ui() 

if st.session_state.is_mobile is None:
    pass
elif not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
else:
    main_page(st.session_state.is_mobile)
