import streamlit as st
import os
import base64
import random
import time
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

# ================== CONFIG & HẰNG SỐ ==================
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

VIDEO_PC = "media/airplane.mp4"
VIDEO_MOBILE = "media/mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
MUSIC_FILES = [
    "background.mp3", "background2.mp3", "background3.mp3",
    "background4.mp3", "background5.mp3"
]

# Giả định thời lượng video là 9 giây (Hãy điều chỉnh nếu video của bạn khác)
VIDEO_DURATION_SECONDS = 9 

# ================== SESSION STATE ==================
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = None
# Thêm biến lưu thời gian bắt đầu cho cơ chế dự phòng
if "start_time" not in st.session_state: 
    st.session_state.start_time = None


# ================== DETECT DEVICE ==================
if st.session_state.is_mobile is None:
    ua_string = st_javascript("window.navigator.userAgent;")
    if ua_string:
        user_agent = parse(ua_string)
        st.session_state.is_mobile = not user_agent.is_pc
        st.rerun()
    else:
        st.info("Đang phát hiện thiết bị...")
        st.stop()


# ================== HIDE STREAMLIT UI ==================
def hide_streamlit_ui():
    """Ẩn các thành phần mặc định của Streamlit và thiết lập kích thước toàn màn hình."""
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer,
    iframe[title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
    }
    .stApp, .main, .block-container {
        padding: 0 !important;
        margin: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        overflow: hidden !important;
    }
    [data-testid*="stHtmlComponents"] {
        position: fixed !important;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        z-index: 9999;
    }
    </style>
    """, unsafe_allow_html=True)


# ================== INTRO SCREEN ==================
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

    if is_mobile:
        object_position = "center 15%"
        text_bottom = "8%"
        font_size = "clamp(16px, 4.5vw, 24px)"
        text_width = "90vw"
    else:
        object_position = "center center"
        text_bottom = "20%"
        font_size = "clamp(28px, 3vw, 48px)"
        text_width = "70vw"
    
    # Đảm bảo text biến mất trước khi video kết thúc (ví dụ: 8.5s)
    animation_duration = f"{VIDEO_DURATION_SECONDS - 0.5}s"
    
    # --- JAVASCRIPT LOGIC Đã Tối Ưu Hóa ---
    js_handler = f"""
    new Promise(resolve => {{
        const vid = document.getElementById("introVid");
        const fade = document.getElementById("fade");

        // Hàm chuyển cảnh: fade màn hình và giải quyết Promise
        function finishIntro() {{
            // Bước 1: Fade màn hình đen
            fade.style.opacity = "1";
            
            // Bước 2: Chờ fade-out (800ms) xong thì giải quyết Promise (chuyển cảnh)
            setTimeout(() => {{ 
                resolve('done');
            }}, 800);
        }}

        // Cố gắng tự động phát
        vid.addEventListener("canplaythrough", () => {{
             vid.play().catch(() => {{}});
        }});
        
        // Event chính: Callback khi video kết thúc
        vid.addEventListener("ended", finishIntro);
        
        // Cơ chế fadeout sớm
        vid.addEventListener("timeupdate", () => {{
             if (vid.duration > 0 && vid.duration - vid.currentTime <= 1.5) {{
                 fade.style.opacity = "1";
             }}
        }});

        // Cơ chế dự phòng bằng thời gian trong JS (nếu event 'ended' bị lỗi)
        setTimeout(finishIntro, {VIDEO_DURATION_SECONDS * 1000 + 1000}); // Video + 1s để xử lý chuyển cảnh
    }});
    """

    intro_html = f"""
    <html lang="vi">
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&display=swap');
        html, body {{
            margin: 0; padding: 0;
            width: 100vw; height: 100vh;
            overflow: hidden; background: black;
        }}
        video {{
            position: absolute;
            top: 0; left: 0;
            width: 100vw; height: 100vh;
            object-fit: cover;
            object-position: {object_position};
            z-index: 1;
            transition: opacity 1.5s ease-in-out;
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
            text-shadow: 0 0 6px rgba(255,255,255,0.4),
                         0 0 20px rgba(255,240,180,0.8),
                         0 0 40px rgba(255,220,130,0.6);
            z-index: 10;
            opacity: 0;
            /* Đảm bảo text biến mất trước khi kết thúc video */
            animation: textFade {animation_duration} ease-in-out forwards;
            white-space: normal;
        }}
        @keyframes textFade {{
            0% {{ opacity: 0; transform: translate(-50%, 40px); }}
            15% {{ opacity: 1; transform: translate(-50%, 0); }}
            75% {{ opacity: 1; }}
            100% {{ opacity: 0; transform: translate(-50%, -20px); }}
        }}
        #fade {{
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: black;
            opacity: 0;
            z-index: 20;
            transition: opacity 0.8s ease-in-out; /* Giảm thời gian fade cho nhanh hơn */
        }}
        </style>
    </head>
    <body>
        <video id="introVid" autoplay muted playsinline preload="auto">
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="fade"></div>
    </body>
    </html>
    """

    components.html(intro_html, height=950, scrolling=False)
    
    # *********** CƠ CHẾ CHUYỂN CẢNH MỚI ***********
    # st_javascript sẽ block (chờ) cho đến khi Promise trong JS được giải quyết ('done')
    intro_finished_status = st_javascript(js_handler) 

    if intro_finished_status == 'done':
        # Khi JS báo xong, set state và reruns
        st.session_state.intro_done = True
        st.rerun()

    # *********** CƠ CHẾ DỰ PHÒNG PYTHON ***********
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()
    
    # Nếu thời gian đã trôi qua quá lâu (ví dụ: 1s lâu hơn thời lượng video) mà vẫn chưa chuyển cảnh, buộc chuyển
    if time.time() - st.session_state.start_time > (VIDEO_DURATION_SECONDS + 1.0):
        st.session_state.intro_done = True
        st.session_state.start_time = None
        st.rerun()


# ================== MAIN PAGE ==================
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
        animation: fadeInMain 1.5s ease-in-out forwards;
    }}
    @keyframes fadeInMain {{
        from {{ opacity: 0; }} to {{ opacity: 1; }}
    }}
    h1 {{
        text-align: center;
        margin-top: 60px;
        color: #2E1C14;
        text-shadow: 2px 2px 6px #FFF8DC;
        font-family: 'Playfair Display', serif;
    }}
    </style>
    """, unsafe_allow_html=True)

    available_music = [m for m in MUSIC_FILES if os.path.exists(m)]
    if available_music:
        chosen = random.choice(available_music)
        with st.sidebar:
            st.subheader("🎵 Nhạc nền")
            st.audio(chosen, loop=True)
            st.caption(f"Đang phát: **{os.path.basename(chosen)}**")

    st.markdown("<h1>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)


# ================== FLOW ==================
hide_streamlit_ui()

if st.session_state.is_mobile is None:
    pass
elif not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
else:
    main_page(st.session_state.is_mobile)
