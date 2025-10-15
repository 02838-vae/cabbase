import streamlit as st
import base64
import os
import time # <<< Cần import thư viện time

st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

video_file = "airplane.mp4"
bg_file = "cabbase.jpg"
audio_file = "background.mp3"

def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

if "show_main" not in st.session_state:
    st.session_state.show_main = False

# --- CƠ CHẾ CHUYỂN CẢNH MỚI ---
# Chỉ chạy video lần đầu tiên (show_main = False)
if not st.session_state.show_main:
    
    # 1. Hiển thị video và hiệu ứng CSS/JS
    if os.path.exists(video_file):
        video_data = get_base64(video_file)
        
        # Đặt tổng thời gian video và mờ dần (ví dụ: Video 5s + Fade 4s = 9s)
        TOTAL_DELAY_SECONDS = 9 
        
        st.markdown(f"""
        <style>
        html, body {{ margin:0; padding:0; height:100%; overflow:hidden; background:black; }}
        .video-container {{
            position: fixed; inset:0; width:100%; height:100%;
            display:flex; justify-content:center; align-items:center;
            background:black; z-index:9999;
            /* Thêm hiệu ứng mờ dần trong 4s */
            animation: fadeOut 4s ease-out {TOTAL_DELAY_SECONDS - 4}s forwards; 
        }}
        .video-bg {{ width:100%; height:100%; object-fit:cover; }}
        /* Giữ nguyên các style khác (video-text, @keyframes appear, floatFade) */
        
        @keyframes fadeOut {{
            0% {{opacity:1; visibility:visible;}}
            100%{{opacity:0; visibility:hidden;}}
        }}
        </style>
        <div class="video-container" id="videoContainer">
            <video id="introVideo" class="video-bg" autoplay muted playsinline>
                <source src="data:video/mp4;base64,{video_data}" type="video/mp4">
            </video>
            <div class="video-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. Tạm dừng luồng Python trong thời gian T = 9s
        # (Điều này chỉ xảy ra một lần duy nhất khi ứng dụng tải)
        time.sleep(TOTAL_DELAY_SECONDS) 
        
        # 3. Sau khi chờ xong, thay đổi trạng thái và Streamlit tự động chạy lại
        st.session_state.show_main = True
        st.rerun() # Bắt buộc chạy lại để hiển thị trang chính
        
    else:
        st.error("❌ Không tìm thấy file airplane.mp4")

# ===== TRANG CHÍNH =====
# background vintage
if not os.path.exists(bg_file):
    st.error("Không tìm thấy cabbase.jpg")
    st.stop()

img_base64 = get_base64(bg_file)
st.markdown(f"""
<style>
.stApp {{
    background: linear-gradient(rgba(245,242,200,0.4), rgba(245,242,200,0.4)),
                url("data:image/jpeg;base64,{img_base64}") no-repeat center center fixed;
    background-size: cover;
}}
header[data-testid="stHeader"] {{ display:none; }}
.block-container {{ padding-top:2rem; }}
.main-title {{
    font-family:'Special Elite', cursive;
    font-size: clamp(36px,5vw,48px);
    font-weight:bold; text-align:center;
    color:#3e2723; margin-top:50px;
    text-shadow:2px 2px 0 #fff,0 0 25px #f0d49b,0 0 50px #bca27a;
}}
</style>
""", unsafe_allow_html=True)

# Nhạc góc trên trái
if os.path.exists(audio_file):
    audio_base64 = get_base64(audio_file)
    st.markdown(f"""
    <audio autoplay loop controls style="position:fixed; top:10px; left:10px; width:200px; z-index:9999;">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
    </audio>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">📜 TỔ BẢO DƯỠNG SỐ 1</div>', unsafe_allow_html=True)
st.write("Chào mừng bạn đến với website ✈️")
