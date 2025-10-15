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

# === CSS VÀ MOBILE HEIGHT FIX (Không thay đổi) ===
st.markdown(f"""
<style>
/* 1. KHẮC PHỤC VIEWPORT TRÊN MOBILE */
html, body {{ 
    margin:0; 
    padding:0; 
    height:100%; 
    overflow:hidden; 
    background:black; 
    /* Dùng biến CSS --vh được đặt bởi JavaScript */
    height: calc(var(--vh, 1vh) * 100); 
}}

/* 2. FULLSCREEN TRIỆT ĐỂ VÀ DÙNG BIẾN --vh */
header[data-testid="stHeader"], footer {{ display: none !important; }}
section.main > div {{ padding-top: 0 !important; padding-left: 0 !important; padding-right: 0 !important; }}
.block-container, .stApp {{
    margin: 0 !important;
    padding: 0 !important;
    max-width: 100% !important;
    width: 100% !important;
    min-height: calc(var(--vh, 1vh) * 100) !important; 
}}

/* 3. CSS CHO VIDEO CONTAINER (Đã xác nhận hoạt động tốt với CONTAIN) */
.video-container {{
    position: fixed; inset:0; width:100%; height:100%;
    justify-content:center; align-items:center;
    background:black; z-index:9999;
    {video_display_style} 
    height: calc(var(--vh, 1vh) * 100) !important; 
}}
.video-bg {{ 
    max-width: 100%; 
    max-height: 100%;
    object-fit:contain; /* Giữ lại contain cho video để máy bay không bị cắt */
}}

/* Các hiệu ứng khác giữ nguyên */
@keyframes fadeOut {{ /* ... */ }}
.intro-animation {{
    animation: fadeOut {FADE_DURATION_SECONDS}s ease-out {VIDEO_DURATION_SECONDS}s forwards; 
}}

.video-text {{ /* ... */ }}
@keyframes appear {{ /* ... */ }}
@keyframes floatFade {{ /* ... */ }}
</style>

<script>
    // CODE JAVASCRIPT ĐỂ FIX LỖI 100vh TRÊN MOBILE
    function setVhProperty() {{
        let vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${{vh}}px`);
    }}

    setVhProperty();
    window.addEventListener('resize', setVhProperty);
</script>
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
    /* Áp dụng màu nền đen/xám để lấp đầy khoảng trống nếu cần */
    background-color: #333; 
    background-image: linear-gradient(rgba(245,242,200,0.4), rgba(245,242,200,0.4)),
                      url("data:image/jpeg;base64,{img_base64}");
    
    /* !!! QUAN TRỌNG: CHUYỂN VỀ COVER ĐỂ LẤP ĐẦY TOÀN BỘ MÀN HÌNH */
    background-size: cover; 
    background-repeat: no-repeat;
    background-position: center center; 
    min-height: calc(var(--vh, 1vh) * 100) !important;
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
