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
# Chỉ chạy một lần, khi chưa xác định được thiết bị
if st.session_state.is_mobile is None:
    # Đặt lại intro_done để đảm bảo quá trình xác định thiết bị không bị bỏ qua
    st.session_state.intro_done = False
    
    # Lấy User Agent từ trình duyệt
    ua_string = st_javascript("""window.navigator.userAgent;""")

    if ua_string:
        # Phân tích chuỗi User Agent
        user_agent = parse(ua_string)
        st.session_state.is_mobile = not user_agent.is_pc
        st.rerun()
    else:
        st.info("Đang xác định thiết bị và tải...")
        # Đợi một chút để JavaScript kịp chạy
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

    /* Đảm bảo HTML components chiếm toàn bộ màn hình cho intro */
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

    # Điều chỉnh thời gian animation để text biến mất trước khi video kết thúc (9s)
    # 8.5s đảm bảo text mờ và biến mất hoàn toàn
    animation_duration = f"{VIDEO_DURATION_SECONDS - 0.5}s" # 8.5s

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
                /* Sử dụng thời gian đã điều chỉnh để text biến mất sớm hơn */
                animation: fadeAppear {animation_duration} ease-in-out forwards; 
                white-space: normal;
                overflow-wrap: break-word;
            }}

            /* ✨ cinematic fade xuất hiện – sáng – tan biến */
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
                    opacity: 0; /* Đảm bảo text biến mất */
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

        <script>
            const vid = document.getElementById("introVid");
            const fade = document.getElementById("fade");

            function finishIntro() {{
                fade.style.opacity = 1; // Bắt đầu chuyển sang màn hình đen
                setTimeout(() => {{
                    // Thông báo cho Streamlit để chuyển trang
                    window.parent.postMessage({{"type": "intro_done"}}, "*"); 
                }}, 1200); // Chờ 1.2s để màn hình đen hoàn toàn
            }}

            vid.onended = finishIntro;
            vid.play().catch(() => {{
                console.log("Autoplay bị chặn, fallback {VIDEO_DURATION_SECONDS}s");
                // Cơ chế dự phòng dựa trên thời gian (ví dụ 9000ms)
                setTimeout(finishIntro, {VIDEO_DURATION_SECONDS * 1000}); 
            }});
        </script>
    </body>
    </html>
    """

    # Nhúng HTML component
    components.html(intro_html, height=950, scrolling=False)

    # Cơ chế dự phòng Python (nếu JS thất bại)
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()
    
    # Chờ lâu hơn thời lượng video một chút (ví dụ 9.5s)
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
    </style>
    """, unsafe_allow_html=True)

    available_music = [m for m in MUSIC_FILES if os.path.exists(m)]
    if available_music:
        chosen = random.choice(available_music)
        # Sử dụng st.container() để tránh lỗi khi st.sidebar bị ẩn
        with st.container():
            st.subheader("🎵 Nhạc nền")
            st.audio(chosen, start_time=0)
            st.caption(f"Đang phát: **{os.path.basename(chosen)}**")

    st.markdown("<h1>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)


# ================== LUỒNG CHÍNH ==================
# Luôn ẩn giao diện mặc định ngay từ đầu
hide_streamlit_ui() 

if st.session_state.is_mobile is None:
    # Đợi xác định thiết bị
    pass 
elif not st.session_state.intro_done:
    # Chạy màn hình intro
    intro_screen(st.session_state.is_mobile)
else:
    # Chạy trang chính
    main_page(st.session_state.is_mobile)
