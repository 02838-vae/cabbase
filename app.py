import streamlit as st
import base64
import time
from PIL import Image, ImageEnhance
import io

st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide", initial_sidebar_state="collapsed")

# ===== Hàm phụ =====
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def process_background(image_path, blur_factor=1.8, tint=(245, 242, 200, 120)):
    """Mở ảnh, làm mờ, phủ màu vàng nhạt vintage và trả về base64"""
    img = Image.open(image_path).convert("RGBA")
    # Làm mờ
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(0.9)  # giảm sáng
    img = img.filter(Image.Filter.GaussianBlur(radius=blur_factor))
    # Overlay vàng nhạt
    overlay = Image.new("RGBA", img.size, tint)
    img = Image.alpha_composite(img, overlay)
    buffered = io.BytesIO()
    img.convert("RGB").save(buffered, format="JPEG", quality=90)
    return base64.b64encode(buffered.getvalue()).decode()

# ===== Trạng thái =====
if "show_main" not in st.session_state:
    st.session_state.show_main = False
if "video_start" not in st.session_state:
    st.session_state.video_start = None

video_file = "airplane.mp4"
video_duration = 8.5  # thời lượng video intro

# ===== MÀN HÌNH INTRO =====
if not st.session_state.show_main:
    st.video(video_file, format="video/mp4", start_time=0)

    # Overlay chữ fade
    st.markdown("""
    <style>
    .video-overlay {
        position: fixed;
        bottom: 12vh;
        width: 100%;
        text-align: center;
        font-family: 'Special Elite', cursive;
        font-size: clamp(24px, 5vw, 44px);
        font-weight: bold;
        color: #ffffff;
        text-shadow:
            0 0 20px rgba(255,255,255,0.8),
            0 0 40px rgba(180,220,255,0.6),
            0 0 60px rgba(255,255,255,0.4);
        opacity: 0;
        animation:
            appear 3s ease-in forwards,
            floatFade 3s ease-in 5s forwards;
        z-index: 9999;
    }
    @keyframes appear {
        0% { opacity: 0; filter: blur(8px); transform: translateY(40px);}
        100% { opacity: 1; filter: blur(0); transform: translateY(0);}
    }
    @keyframes floatFade {
        0% { opacity: 1; filter: blur(0); transform: translateY(0);}
        100% { opacity: 0; filter: blur(12px); transform: translateY(-30px) scale(1.05);}
    }
    </style>
    <div class="video-overlay">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    """, unsafe_allow_html=True)

    # Khởi tạo thời gian bắt đầu video
    if st.session_state.video_start is None:
        st.session_state.video_start = time.time()
        st.stop()

    # Khi video kết thúc, chuyển trang chính
    if time.time() - st.session_state.video_start > video_duration:
        st.session_state.show_main = True
        st.experimental_rerun()

# ===== TRANG CHÍNH =====
else:
    # Xử lý background vintage
    bg_file = "cabbase.jpg"
    if not os.path.exists(bg_file):
        st.error("Không tìm thấy cabbase.jpg")
        st.stop()
    img_base64 = process_background(bg_file, blur_factor=2.5, tint=(245, 242, 200, 140))

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Special+Elite&display=swap');

    .stApp {{
        font-family: 'Special Elite', cursive !important;
        background: linear-gradient(rgba(245,242,200,0.4), rgba(245,242,200,0.4)),
                    url("data:image/jpeg;base64,{img_base64}") no-repeat center center fixed;
        background-size: cover;
    }}
    .stApp::after {{
        content: "";
        position: fixed;
        inset: 0;
        background: url("https://www.transparenttextures.com/patterns/aged-paper.png");
        opacity: 0.15;
        pointer-events: none;
        z-index: -1;
    }}
    header[data-testid="stHeader"] {{ display: none; }}
    .block-container {{ padding-top: 2rem; }}

    /* Tiêu đề */
    .main-title {{
        font-size: clamp(36px, 5vw, 48px);
        font-weight: bold;
        text-align: center;
        color: #3e2723;
        margin-top: 50px;
        text-shadow: 2px 2px 0 #fff, 0 0 25px #f0d49b, 0 0 50px #bca27a;
    }}
    </style>
    """, unsafe_allow_html=True)

    # Thanh nhạc góc trên trái
    audio_file = "background.mp3"
    if os.path.exists(audio_file):
        audio_base64 = get_base64(audio_file)
        st.markdown(f"""
        <audio autoplay loop controls style="position:fixed; top:10px; left:10px; width:200px; z-index:9999;">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        """, unsafe_allow_html=True)

    st.markdown('<div class="main-title">📜 TỔ BẢO DƯỠNG SỐ 1</div>', unsafe_allow_html=True)
    st.write("Chào mừng bạn đến với website ✈️")
