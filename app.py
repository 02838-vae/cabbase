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
FADE_DURATION_MS = 800 # Thời gian fade màn hình đen trong CSS

# ================== SESSION STATE ==================
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = None
if "start_time" not in st.session_state: 
    st.session_state.start_time = None
if "message_received" not in st.session_state:
    st.session_state.message_received = False


# ================== DETECT DEVICE ==================
if st.session_state.is_mobile is None:
    ua_string = st_javascript("window.navigator.userAgent;")
    if ua_string:
        user_agent = parse(ua_string)
        st.session_state.is_mobile = not user_agent.is_pc
        # st.rerun() được gọi để tiếp tục luồng
    else:
        # Nếu JS chưa kịp trả về, dừng lại và chờ
        st.info("Đang phát hiện thiết bị...")
        time.sleep(0.1) # Dừng một chút để JS kịp chạy
        st.stop()
    st.rerun()


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
    
    animation_duration = f"{VIDEO_DURATION_SECONDS - 0.5}s"
    
    # --- JAVASCRIPT LOGIC ---
    js_inside_html = f"""
        <script>
            const vid = document.getElementById("introVid");
            const fade = document.getElementById("fade");
            const FADE_DURATION = {FADE_DURATION_MS};
            const VIDEO_DURATION_MS = {VIDEO_DURATION_SECONDS * 1000};

            function finishIntro() {{
                fade.style.opacity = "1";
                
                setTimeout(() => {{ 
                    vid.style.display = "none";
                    // GỬI TÍN HIỆU ĐẶC BIỆT ĐỂ CHUYỂN CẢNH
                    window.parent.postMessage("INTRO_FINISHED", "*"); 
                }}, FADE_DURATION);
            }}

            vid.addEventListener("canplaythrough", () => {{
                 vid.play().catch(() => {{}});
            }});
            
            vid.addEventListener("ended", finishIntro);
            
            vid.addEventListener("timeupdate", () => {{
                 if (vid.duration > 0 && vid.duration - vid.currentTime <= 1.5) {{
                     fade.style.opacity = "1";
                 }}
            }});
            
            // Cơ chế dự phòng bằng thời gian trong JS (sẽ kích hoạt chuyển cảnh sau 10s)
            setTimeout(finishIntro, VIDEO_DURATION_MS + 1000); 
        </script>
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
            /* FIX LỖI TỈ LỆ: Dùng min-width/height để đảm bảo video che phủ và giữ tỉ lệ */
            min-width: 100%; 
            min-height: 100%;
            width: auto; /* Bổ sung để đảm bảo tỉ lệ */
            height: auto; /* Bổ sung để đảm bảo tỉ lệ */
            object-fit: cover;
            object-position: {object_position};
            z-index: 1;
            transition: opacity 1.5s ease-in-out;
        }}
        #intro-text {{ /* ... (CSS giữ nguyên) ... */
            position: absolute; left: 50%; bottom: {text_bottom};
            transform: translateX(-50%); font-family: 'Cinzel', serif;
            font-size: {font_size}; width: {text_width}; text-align: center;
            color: #fff8dc; font-weight: 700; z-index: 10; opacity: 0;
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
            position: absolute; top: 0; left: 0;
            width: 100%; height: 100%; background: black;
            opacity: 0; z-index: 20;
            transition: opacity 0.8s ease-in-out; 
        }}
        </style>
    </head>
    <body>
        <video id="introVid" autoplay muted playsinline preload="auto">
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="fade"></div>
        {js_inside_html} 
    </body>
    </html>
    """

    components.html(intro_html, height=950, scrolling=False)
    
    # *********** CƠ CHẾ LẮNG NGHE VÀ CHUYỂN CẢNH ***********
    
    # 1. Listener JS bên ngoài iframe (sẽ tự động thay đổi st.session_state.message_received)
    listener_js = """
        window.addEventListener("message", (e) => {
            if (e.data === "INTRO_FINISHED") {
                // Sử dụng cú pháp Streamlit để thay đổi Session State
                window.parent.postMessage({type: "streamlit:setSessionState", key: "message_received", value: true}, "*");
            }
        });
    """
    st_javascript(listener_js)

    # 2. Kiểm tra cờ nhận tin nhắn
    if st.session_state.message_received:
        st.session_state.intro_done = True
        st.session_state.message_received = False
        st.rerun()
        return # Ngăn chặn các cơ chế khác chạy nếu đã chuyển cảnh

    # 3. Cơ chế Dự phòng Bằng Thời gian (Python)
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()
    
    # Chỉ kiểm tra và chạy lại nếu chưa hoàn thành (PC không bị nhấp nháy)
    if not st.session_state.intro_done:
        if time.time() - st.session_state.start_time > (VIDEO_DURATION_SECONDS + 2.0):
            # Nếu đã quá thời gian dự phòng, buộc chuyển cảnh
            st.session_state.intro_done = True
            st.session_state.start_time = None
            st.rerun()
        else:
            # PC/Mobile không cần chạy liên tục, chỉ cần đợi tín hiệu hoặc timeout
            # Không dùng time.sleep và st.rerun() liên tục nữa để tránh nhấp nháy
            pass # Streamlit sẽ tự động rerun khi có state change từ JS, hoặc khi timeout


# ================== MAIN PAGE ==================
# ... (Phần main_page giữ nguyên) ...
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
