import streamlit as st
import base64
import os
import time

# --- CẤU HÌNH BAN ĐẦU ---
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

# Tên các file cần thiết
video_file = "airplane.mp4"
bg_file = "cabbase.jpg"
audio_file = "background.mp3"

# Ước tính thời gian chuyển cảnh (Cần điều chỉnh)
VIDEO_DURATION_SECONDS = 5  
FADE_DURATION_SECONDS = 4   
TOTAL_DELAY_SECONDS = VIDEO_DURATION_SECONDS + FADE_DURATION_SECONDS

# Hàm đọc file và chuyển thành Base64
def get_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        return None

# Khởi tạo Session State
if "show_main" not in st.session_state:
    st.session_state.show_main = False
if "intro_ran" not in st.session_state:
    st.session_state.intro_ran = False

# CSS động để kiểm soát hiển thị video (Chống Flicker)
is_main_page = st.session_state.show_main
video_display_style = "display: none;" if is_main_page else "display: flex;" 

# === CSS NỀN TẢNG VÀ FULLSCREEN/RESPONSIVE ===
st.markdown(f"""
<style>
/* 1. KHẮC PHỤC VIEWPORT CHO MOBILE (Sử dụng đơn vị 'vh' thường gặp lỗi trên mobile) */
/* Cố gắng sửa lỗi 100vh không chính xác trên các trình duyệt mobile */
html, body {{ margin:0; padding:0; height:100%; overflow:hidden; background:black; }}

/* 2. FULLSCREEN TRIỆT ĐỂ */
header[data-testid="stHeader"], footer {{ display: none !important; }}
section.main > div {{ padding-top: 0 !important; padding-left: 0 !important; padding-right: 0 !important; }}
.block-container, .stApp {{
    margin: 0 !important;
    padding: 0 !important;
    max-width: 100% !important;
    width: 100% !important; /* Dùng 100% thay vì 100vw */
    min-height: 100vh !important;
    /* Dùng min-height 100vh để đảm bảo chiều cao tối thiểu */
}}

/* 3. CSS CHO VIDEO CONTAINER (RESPONSIVE VIDEO VÀ CHỐNG FLICKER) */
.video-container {{
    position: fixed; inset:0; width:100%; height:100%;
    justify-content:center; align-items:center;
    background:black; z-index:9999;
    {video_display_style} 
}}
.video-bg {{ 
    width:100%; 
    height:100%; 
    object-fit:cover; /* Đảm bảo video lấp đầy khung hình mà không bị méo */
}}

/* Hiệu ứng mờ dần */
@keyframes fadeOut {{ /* Giữ nguyên hiệu ứng */
    0% {{opacity:1; visibility:visible;}}
    99% {{opacity:0.01; visibility:visible;}}
    100%{{opacity:0; visibility:hidden;}}
}}
.intro-animation {{
    animation: fadeOut {FADE_DURATION_SECONDS}s ease-out {VIDEO_DURATION_SECONDS}s forwards; 
}}

/* Các animation text giữ nguyên */
.video-text {{
    position:absolute; bottom:12vh; width:100%; text-align:center;
    font-family:'Special Elite', cursive; font-size:clamp(24px,5vw,44px);
    font-weight:bold; color:#fff;
    text-shadow: 0 0 20px rgba(255,255,255,0.8), 0 0 40px rgba(180,220,255,0.6), 0 0 60px rgba(255,255,255,0.4);
    opacity:0;
    animation: appear 3s ease-in forwards, floatFade 3s ease-in 5s forwards;
}}
@keyframes appear {{ 0% {{opacity:0; filter:blur(8px); transform:translateY(40px);}} 100%{{opacity:1; filter:blur(0); transform:translateY(0);}} }}
@keyframes floatFade {{ 0% {{opacity:1; filter:blur(0); transform:translateY(0);}} 100%{{opacity:0; filter:blur(12px); transform:translateY(-30px) scale(1.05);}} }}
</style>
""", unsafe_allow_html=True)


# --- GIAO DIỆN CHUYỂN CẢNH (VIDEO INTRO) ---
if not st.session_state.show_main and not st.session_state.intro_ran:
    
    video_data = get_base64(video_file)
    if video_data is None:
        st.error(f"❌ Không tìm thấy file {video_file}.")
        st.stop()
    
    # HTML/Video và Kích hoạt Rerun Bằng Python
    st.markdown(f"""
    <div class="video-container intro-animation" id="videoContainer">
        <video id="introVideo" class="video-bg" autoplay muted playsinline>
            <source src="data:video/mp4;base64,{video_data}" type="video/mp4">
        </video>
        <div class="video-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tạm dừng luồng Streamlit và kích hoạt RERUN
    time.sleep(TOTAL_DELAY_SECONDS) 
    
    st.session_state.show_main = True
    st.session_state.intro_ran = True 
    st.rerun() 
    
    st.stop() 

# --- TRANG CHÍNH ---

img_base64 = get_base64(bg_file)
if img_base64 is None:
    st.error(f"❌ Không tìm thấy file {bg_file}.")
    st.stop()

st.markdown(f"""
<style>
/* 4. CSS cho Trang Chính (RESPONSIVE BACKGROUND) */
.stApp {{
    /* Đảm bảo background fill toàn bộ màn hình */
    background: linear-gradient(rgba(245,242,200,0.4), rgba(245,242,200,0.4)),
                url("data:image/jpeg;base64,{img_base64}") no-repeat center center fixed;
    background-size: cover; /* <--- Đảm bảo background fit và lấp đầy khung hình */
}}
/* Khôi phục padding nhẹ cho nội dung trang chính */
.block-container {{ padding-top:2rem !important; padding-left:1rem !important; padding-right:1rem !important;}}

/* Đảm bảo header/footer ẩn khi ở trang chính */
header[data-testid="stHeader"] {{ display:none; }}
footer {{ display:none; }}

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
audio_base64 = get_base64(audio_file)
if audio_base64:
    st.markdown(f"""
    <audio autoplay loop controls style="position:fixed; top:10px; left:10px; width:200px; z-index:9999;">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
    </audio>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">📜 TỔ BẢO DƯỠNG SỐ 1</div>', unsafe_allow_html=True)
st.write("Chào mừng bạn đến với website ✈️")
