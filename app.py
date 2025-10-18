import streamlit as st
import os
import base64
import random
import time
import streamlit.components.v1 as components
from streamlit_js_eval import streamlit_js_eval # <-- Thư viện mới

# ================== CẤU HÌNH ==================
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
MUSIC_FILES = ["background.mp3", "background2.mp3", "background3.mp3", "background4.mp3", "background5.mp3"]

# ================== TRẠNG THÁI ==================
# Khởi tạo trạng thái intro_done
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

# Khởi tạo trạng thái is_mobile và kích hoạt xác định thiết bị
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = None
    # Lần chạy đầu tiên: Yêu cầu JS xác định thiết bị
    is_mobile_js = streamlit_js_eval(js_expressions='(/Mobi|Android|iPhone|iPad/i.test(navigator.userAgent))', key='mobile_detector')
    
    # Nếu có kết quả trả về từ JS, cập nhật trạng thái và rerun
    if is_mobile_js is not None:
        st.session_state.is_mobile = is_mobile_js
        st.rerun()
    else:
        # Chờ JS chạy lần đầu (Mặc định PC nếu không có phản hồi)
        st.session_state.is_mobile = False
        st.rerun() # Rerun để vào luồng chính sau khi gán mặc định


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


# ================== MÀN HÌNH INTRO SỬ DỤNG st.video ==================
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    
    # Sử dụng logic chọn video đơn giản, KHÔNG DÙNG BASE64
    video_path = VIDEO_MOBILE if is_mobile else VIDEO_PC
    
    if not os.path.exists(video_path):
        st.error(f"⚠️ Không tìm thấy video: {video_path}")
        st.session_state.intro_done = True
        st.rerun()
        return

    # Ẩn tất cả nội dung trừ video
    st.markdown("""
    <style>
    .stApp { overflow: hidden; background-color: black; }
    </style>
    """, unsafe_allow_html=True)

    # Hiển thị video bằng st.video
    st.video(video_path, format='video/mp4', start_time=0)
    
    # Sử dụng HTML/CSS để hiển thị text và căn video full màn hình
    # LƯU Ý: st.video khó căn full màn hình như components.html
    # Chúng ta phải dùng cách CSS bao bọc thủ công hơn.
    intro_css = f"""
    <style>
        /* CSS căn giữa/full màn hình cho video (phức tạp trong Streamlit) */
        /* Đây chỉ là ví dụ để đảm bảo video được hiển thị */
        #intro-text {{
            position: fixed;
            bottom: 18%;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
            font-size: clamp(1em, 4vw, 2em);
            color: white;
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
    </style>
    <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    """
    st.markdown(intro_css, unsafe_allow_html=True)

    # Đợi cho video kết thúc (Giả định video dài 9 giây)
    time.sleep(9)
    st.session_state.intro_done = True
    st.rerun()


# ================== TRANG CHÍNH (Giữ nguyên) ==================
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
    /* ... (CSS còn lại) ... */
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
            st.audio(chosen)
            st.caption(f"Đang phát: **{os.path.basename(chosen)}**")

    st.markdown("<h1>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)


# ================== LUỒNG CHÍNH ==================
hide_streamlit_ui()

# Kiểm tra nếu is_mobile vẫn là None, nó sẽ tự động chạy lại nhờ logic ở trên
if st.session_state.is_mobile is None:
    # Nếu đến đây, có nghĩa là đang ở lần chạy đầu tiên và đang chờ JS trả lời
    st.info("Đang xác định thiết bị...")
elif not st.session_state.intro_done:
    # is_mobile đã có giá trị (True/False)
    intro_screen(st.session_state.is_mobile)
else:
    # Intro đã xong
    main_page(st.session_state.is_mobile)
