import streamlit as st
import base64
import os
import time

# === ĐỊNH NGHĨA HẰNG SỐ VÀ FILE ===
# Tên các file cần thiết
video_file = "airplane.mp4"
bg_file = "cabbase.jpg"
bg_mobile_file = "mobile.jpg" 

# Danh sách bài hát (Dùng cho thẻ <audio> đơn giản)
AUDIO_FILES = ["background.mp3", "background2.mp3", "background3.mp3", "background4.mp3", "background5.mp3"]
# Bài hát mặc định sẽ play
DEFAULT_AUDIO_FILE = AUDIO_FILES[0]

# Ước tính thời gian chuyển cảnh (Cần điều chỉnh)
VIDEO_DURATION_SECONDS = 5  
FADE_DURATION_SECONDS = 4   
TOTAL_DELAY_SECONDS = VIDEO_DURATION_SECONDS + FADE_DURATION_SECONDS
# =========================================================================

# --- CẤU HÌNH BAN ĐẦU ---
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

# Hàm đọc file và chuyển thành Base64
def get_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        return None

# --- Khởi tạo Session State ---
if "show_main" not in st.session_state:
    st.session_state.show_main = False
if "intro_ran" not in st.session_state:
    st.session_state.intro_ran = False

# === TẢI TẤT CẢ FILE CẦN THIẾT ===
img_base64 = get_base64(bg_file)
if img_base64 is None:
    st.error(f"❌ Không tìm thấy file {bg_file}. Vui lòng kiểm tra lại tên và đường dẫn file.")
    st.stop()
    
img_mobile_base64 = get_base64(bg_mobile_file)
if img_mobile_base64 is None:
    img_mobile_base64 = img_base64 

# Tải file âm thanh mặc định
audio_base64 = get_base64(DEFAULT_AUDIO_FILE)
# ===================================================

# CSS động để kiểm soát hiển thị video
is_main_page = st.session_state.show_main
video_display_style = "display: none;" if is_main_page else "display: flex;" 

# === CSS CHUNG VÀ VIDEO (FIX FLICKER DÙNG LỚP PHỦ ĐEN) ===
st.markdown(f"""
<style>
/* 1. KHẮC PHỤC VIEWPORT TRÊN MOBILE và FULL HEIGHT cho PC */
html, body {{ 
    margin:0; 
    padding:0; 
    height:100%; 
    overflow:hidden; 
    background:black; 
    height: 100%; 
}}

/* 2. FULLSCREEN TRIỆT ĐỂ & FIX Mobile VH */
header[data-testid="stHeader"], footer {{ display: none !important; }}
.block-container, section.main > div {{
    margin: 0 !important;
    padding: 0 !important;
    max-width: 100% !important;
    width: 100vw !important;
    height: calc(var(--vh, 1vh) * 100) !important;
}}
.stApp, section.main {{
    height: calc(var(--vh, 1vh) * 100) !important;
    min-height: calc(var(--vh, 1vh) * 100) !important;
}}

/* 3. CSS CHO LỚP PHỦ ĐEN (FIX FLICKER DỨT ĐIỂM) */
#blackOverlay {{
    position: fixed; inset:0; 
    width:100vw; height:calc(var(--vh, 1vh) * 100);
    background:black; 
    z-index:100000; /* Z-INDEX CAO NHẤT */
    opacity: 1; /* Bắt đầu với màn hình đen */
    transition: opacity {FADE_DURATION_SECONDS}s ease-out;
    animation: fadeOut {FADE_DURATION_SECONDS}s ease-out {VIDEO_DURATION_SECONDS}s forwards;
}}

/* 4. CSS CHO VIDEO CONTAINER (VẪN ĐANG CHẠY BÊN DƯỚI OVERLAY) */
.video-container {{
    position: fixed; inset:0; 
    width:100vw; height:calc(var(--vh, 1vh) * 100);
    justify-content:center; 
    align-items:center;
    background:black; 
    z-index:99999; /* Cao hơn trang chính, thấp hơn Overlay */
    {video_display_style} 
    flex-direction: column; 
    opacity: 1; /* Đảm bảo video hiển thị khi overlay biến mất */
}}

/* FIX VIDEO MOBILE FIT: Bắt video chiếm toàn bộ viewport */
.video-bg {{ 
    width: 100vw; 
    height: calc(var(--vh, 1vh) * 100);
    object-fit:cover; /* Chế độ quan trọng nhất để FIX FIT */
}}

/* CSS CHO DÒNG CHỮ INTRO VÀ HIỆU ỨNG (KHÔI PHỤC) */
.video-text {{
    position:absolute; bottom:12vh; width:100%; text-align:center;
    font-family:'Special Elite', cursive; font-size:clamp(24px,5vw,44px);
    font-weight:bold; color:#fff;
    text-shadow: 0 0 20px rgba(255,255,255,0.8), 0 0 40px rgba(180,220,255,0.6), 0 0 60px rgba(255,255,255,0.4);
    opacity:0;
    animation: appear 3s ease-in forwards, floatFade 3s ease-in 5s forwards;
}}

/* Keyframes */
@keyframes fadeOut {{ 
    0% {{opacity:1;}}
    99% {{opacity:0.01;}}
    100%{{opacity:0; visibility:hidden; z-index:-1;}} 
}}
@keyframes appear {{ 0% {{opacity:0; filter:blur(8px); transform:translateY(40px);}} 100%{{opacity:1; filter:blur(0); transform:translateY(0);}} }}
@keyframes floatFade {{ 0% {{opacity:1; filter:blur(0); transform:translateY(0);}} 100%{{opacity:0; filter:blur(12px); transform:translateY(-30px) scale(1.05);}} }}


/* 5. CSS CHO TRANG CHÍNH: BACKGROUND FIX */
.stApp {{
    z-index:1; 
    background-color: #333; 
    background-image: linear-gradient(rgba(245,242,200,0.4), rgba(245,242,200,0.4)),
                      url("data:image/jpeg;base64,{img_base64}");
    
    background-attachment: fixed; 
    background-size: cover; 
    background-repeat: no-repeat;
    background-position: center center; 
}}

/* Media Query cho Mobile Background */
@media screen and (max-width: 768px) {{
    .stApp {{
        background-image: linear-gradient(rgba(245,242,200,0.4), rgba(245,242,200,0.4)),
                          url("data:image/jpeg;base64,{img_mobile_base64}");
        background-size: cover; 
        background-color: #333; 
    }}
}}

/* Khôi phục padding nhẹ cho nội dung trang chính */
.block-container {{ padding-top:2rem !important; padding-left:1rem !important; padding-right:1rem !important;}}
.main-title {{
    font-family:'Special Elite', cursive;
    font-size: clamp(36px,5vw,48px);
    font-weight:bold; text-align:center;
    color:#3e2723; margin-top:50px;
    text-shadow:2px 2px 0 #fff,0 0 25px #f0d49b,0 0 50px #bca27a;
}}
</style>

<script>
    // CODE JAVASCRIPT ĐỂ FIX LỖI 100vh TRÊN MOBILE (Đã sửa lỗi)
    function setVhProperty() {{
        let vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${{vh}}px`);
        
        const stApp = window.parent.document.querySelector('.stApp');
        if (stApp) {{
            stApp.style.height = `calc(${{vh}}px * 100)`;
        }}
    }}

    window.addEventListener('load', setVhProperty);
    window.addEventListener('resize', setVhProperty);
    
    if (document.readyState === 'complete') {{
        setVhProperty();
    }}
</script>
""", unsafe_allow_html=True)


# --- GIAO DIỆN CHUYỂN CẢNH (VIDEO INTRO) ---
if not st.session_state.show_main and not st.session_state.intro_ran:
    
    video_data = get_base64(video_file)
    if video_data is None:
        st.error(f"❌ Không tìm thấy file {video_file}.")
        st.stop()
    
    # Lớp phủ đen tuyệt đối
    st.markdown('<div id="blackOverlay"></div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="video-container" id="videoContainer">
        <video id="introVideo" class="video-bg" autoplay muted playsinline>
            <source src="data:video/mp4;base64,{video_data}" type="video/mp4">
        </video>
        <div class="video-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    </div>
    """, unsafe_allow_html=True)
    
    time.sleep(TOTAL_DELAY_SECONDS) 
    
    st.session_state.show_main = True
    st.session_state.intro_ran = True 
    st.rerun() 
    
    st.stop() 

# --- TRANG CHÍNH ---

st.markdown('<div class="main-title">📜 TỔ BẢO DƯỠNG SỐ 1</div>', unsafe_allow_html=True)
st.write("Chào mừng bạn đến với website ✈️")

# === KHÔI PHỤC THẺ AUDIO ĐƠN GIẢN ===
if audio_base64:
    # Thẻ audio tiêu chuẩn không có nút next/previous, nhưng sẽ đảm bảo phát nhạc ổn định
    st.markdown(f"""
    <audio autoplay loop controls style="position:fixed; top:10px; left:10px; width:200px; z-index:9999;">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
    </audio>
    """, unsafe_allow_html=True)
# =================================================================================
