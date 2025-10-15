import streamlit as st
import pandas as pd
import base64
import os
import time
from PIL import Image, ImageFilter
import io

# ====== CẤU HÌNH TRANG ======
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

# ====== HÀM PHỤ TRỢ ======
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def process_background(image_path):
    """Làm mờ nhẹ toàn ảnh, mờ nhiều hơn phía dưới (vintage-style)."""
    if not os.path.exists(image_path):
        return ""
    img = Image.open(image_path).convert("RGB")
    width, height = img.size

    # Mờ nhẹ toàn bộ ảnh
    base_blur = img.filter(ImageFilter.GaussianBlur(3))

    # Làm mờ mạnh hơn vùng dưới (xoá logo)
    bottom_blur = img.crop((0, int(height * 0.7), width, height)).filter(ImageFilter.GaussianBlur(14))
    base_blur.paste(bottom_blur, (0, int(height * 0.7)))

    # Thêm lớp màu vàng nhẹ để tạo cảm giác vintage
    overlay = Image.new("RGB", img.size, (245, 222, 179))  # màu vàng nhạt kiểu giấy cũ
    mask = Image.new("L", img.size, 60)  # toàn ảnh ngả vàng nhẹ
    for y in range(int(height * 0.7), height):
        alpha = int((y - height * 0.7) / (height * 0.3) * 140)  # mạnh dần xuống dưới
        for x in range(width):
            mask.putpixel((x, y), alpha)
    final_img = Image.composite(overlay, base_blur, mask)

    # Xuất base64
    buffered = io.BytesIO()
    final_img.save(buffered, format="JPEG", quality=90)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")




# ====== TRẠNG THÁI ======
if "show_main" not in st.session_state:
    st.session_state.show_main = False
if "video_played" not in st.session_state:
    st.session_state.video_played = False

video_file = "airplane.mp4"

# ====== VIDEO INTRO ======
if not st.session_state.show_main:
    if os.path.exists(video_file):
        video_data = get_base64(video_file)

        st.markdown(rf"""
        <style>
        html, body, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"] {{
            margin: 0 !important;
            padding: 0 !important;
            background: black !important;
            overflow: hidden !important;
            height: 100vh !important;
        }}
        [data-testid="stHeader"] {{ display: none !important; }}
        .video-container {{
            position: fixed;
            inset: 0;
            width: 100vw;
            height: 100vh;
            background: black;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9998;
        }}
        .video-bg {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .intro-text {{
            position: absolute;
            bottom: 12vh;
            width: 100%;
            text-align: center;
            font-family: 'Special Elite', cursive;
            font-size: 44px;
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
        }}
        @keyframes appear {{
            0% {{ opacity: 0; filter: blur(8px); transform: translateY(40px); }}
            100% {{ opacity: 1; filter: blur(0); transform: translateY(0); }}
        }}
        @keyframes floatFade {{
            0% {{ opacity: 1; filter: blur(0); transform: translateY(0); }}
            100% {{ opacity: 0; filter: blur(12px); transform: translateY(-30px) scale(1.05); }}
        }}
        </style>

        <div class="video-container">
            <video class="video-bg" autoplay muted playsinline>
                <source src="data:video/mp4;base64,{video_data}" type="video/mp4">
            </video>
            <div class="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.video_played:
            st.session_state.video_played = True
            time.sleep(8.5)
            st.session_state.show_main = True
            st.rerun()
        st.stop()
    else:
        st.error("❌ Không tìm thấy file airplane.mp4")
        st.stop()

# ====== TRANG CHÍNH ======

# ====== XỬ LÝ ẢNH NỀN ======
img_base64 = process_background("cabbase.jpg")

# ====== CSS PHONG CÁCH ======
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Special+Elite&display=swap');
.stApp {{
    font-family: 'Special Elite', cursive !important;
    background:
        linear-gradient(rgba(245, 222, 179, 0.35), rgba(245, 222, 179, 0.35)),
        url("data:image/jpeg;base64,{img_base64}") no-repeat center center fixed;
    background-size: cover;
    filter: sepia(0.3) brightness(0.9) contrast(1.05);
    backdrop-filter: blur(5px);
}}
.audio-fixed {{
    position: fixed;
    top: 15px;
    left: 15px;
    width: 200px;
    z-index: 10000;
}}
header[data-testid="stHeader"] {{ display: none; }}
.block-container {{ padding-top: 0 !important; }}
.main-title {{
    font-size: 48px;
    font-weight: bold;
    text-align: center;
    color: #3e2723;
    margin-top: 60px;
    text-shadow: 2px 2px 0 #fff, 0 0 25px #f0d49b, 0 0 50px #bca27a;
}}
.sub-title {{
    font-size: 34px;
    text-align: center;
    color: #6d4c41;
    margin-top: 5px;
    margin-bottom: 25px;
    letter-spacing: 1px;
}}
</style>
""", unsafe_allow_html=True)

# ====== TIÊU ĐỀ ======
st.markdown('<div class="main-title">📜 TỔ BẢO DƯỠNG SỐ 1</div>', unsafe_allow_html=True)

# ====== NHẠC NỀN ======
try:
    with open("background.mp3", "rb") as f:
        audio_bytes = f.read()
        st.markdown('<div class="audio-fixed">', unsafe_allow_html=True)
        st.audio(audio_bytes, format="audio/mp3", start_time=0)
        st.markdown('</div>', unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("⚠️ Không tìm thấy file background.mp3")

