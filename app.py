import streamlit as st
import os
import base64
import random
import time
import streamlit.components.v1 as components
from streamlit_js_eval import streamlit_js_eval # Cần cài đặt: pip install streamlit-js-eval

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
    st.session_state.is_mobile = None # Khởi tạo là None, chờ JS xác định

# --- XÁC ĐỊNH THIẾT BỊ NGAY LẬP TỨC (Dùng streamlit_js_eval) ---
if st.session_state.is_mobile is None:
    # Lần chạy đầu tiên: Gọi JS để xác định thiết bị
    # Sử dụng time.time() để đảm bảo key là duy nhất và JS được thực thi
    js_result = streamlit_js_eval(js_expressions='(/Mobi|Android|iPhone|iPad/i.test(navigator.userAgent))', 
                                 key=f'mobile_detector_{time.time()}')
    
    if js_result is not None:
        # Nhận kết quả từ JS (True/False)
        st.session_state.is_mobile = js_result
        st.rerun()
    else:
        # Nếu chưa có kết quả (đang chờ), mặc định là PC
        st.session_state.is_mobile = False
        # Không cần rerun ở đây vì nó sẽ rerun sau khi nhận kết quả hoặc khi tiếp tục luồng.

# ================== ẨN HEADER STREAMLIT ==================
def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"],
    header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ================== MÀN HÌNH INTRO VỚI AUTOPLAY (Dùng components.html + muted) ==================
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    
    video_path = VIDEO_MOBILE if is_mobile else VIDEO_PC
    
    if not os.path.exists(video_path):
        st.error(f"⚠️ Không tìm thấy video: {video_path}")
        st.session_state.intro_done = True
        st.rerun()
        return

    # Mã hóa video thành base64 (Chỉ cho video được chọn)
    with open(video_path, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()

    intro_html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        html, body {{ margin: 0; padding: 0; height: 100%; overflow: hidden; background-color: black; }}
        video {{ width: 100vw; height: 100vh; object-fit: cover; object-position: center; }}
        #intro-text {{
            position: fixed; bottom: 18%; left: 50%; transform: translateX(-50%);
            font-size: clamp(1em, 4vw, 2em); color: white;
            font-family: 'Playfair Display', serif;
            text-shadow: 2px 2px 6px rgba(0,0,0,0.8);
            animation: fadeInOut 6s ease-in-out forwards;
        }}
        @keyframes fadeInOut {{
            0% {{ opacity: 0; transform: translate(-50%, 20px); }}
            20% {{ opacity: 1; transform: translate(-50%, 0); }}
            80% {{ opacity: 1; transform: translate(-50%, 0); }}
            100% {{ opacity: 0; transform: translate(-50%, -10px); }}
        }}
        #fade {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: black; opacity: 0; z-index: 10;
            transition: opacity 1s ease-in-out;
        }}
    </style>
    </head>
    <body>
        <video id="introVid" autoplay muted playsinline> <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="fade"></div>
        <script>
            const vid = document.getElementById("introVid");
            const fade = document.getElementById("fade");
            vid.onended = () => {{
                fade.style.opacity = 1;
                setTimeout(() => {{
                    // Gửi tín hiệu hoàn thành intro
                    window.parent.postMessage({{type: "intro_done"}}, "*");
                }}, 1200);
            }};
        </script>
    </body>
    </html>
    """
    components.html(intro_html, height=800, scrolling=False)

    # Đợi cho video kết thúc
    time.sleep(9)
    st.session_state.intro_done = True
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
        bg_b64 = "" # Fallback

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
    @keyframes fadeInBg {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
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

    # Nhạc nền
    available_music = [m for m in MUSIC_FILES if os.path.exists(m)]
    if available_music:
        chosen = random.choice(available_music)
        with st.sidebar:
            st.subheader("🎵 Nhạc nền")
            # st.audio() sẽ tạo thanh phát nhạc, có thể bị ẩn trên mobile
            st.audio(chosen, start_time=0) 
            st.caption(f"Đang phát: **{os.path.basename(chosen)}**")

    st.markdown("<h1>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)


# ================== LUỒNG CHÍNH ==================
hide_streamlit_ui()

# Kiểm tra nếu is_mobile vẫn đang chờ kết quả, hiển thị thông báo
if st.session_state.is_mobile is None:
    st.info("Đang xác định thiết bị và tải...")
elif not st.session_state.intro_done:
    # is_mobile đã có giá trị (True/False)
    intro_screen(st.session_state.is_mobile)
else:
    # Intro đã xong
    main_page(st.session_state.is_mobile)
