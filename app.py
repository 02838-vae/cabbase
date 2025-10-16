import streamlit as st
import base64
import os
import time

# --- CẤU HÌNH BAN ĐẦU ---
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

# Tên các file cần thiết
video_file = "airplane.mp4"
bg_file = "cabbase.jpg"
bg_mobile_file = "mobile.jpg" 

# === DANH SÁCH BÀI HÁT (Thêm background2.mp3 đến background5.mp3) ===
AUDIO_FILES = ["background.mp3", "background2.mp3", "background3.mp3", "background4.mp3", "background5.mp3"]

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

# --- Khởi tạo Session State ---
if "show_main" not in st.session_state:
    st.session_state.show_main = False
if "intro_ran" not in st.session_state:
    st.session_state.intro_ran = False
# Session State MỚI cho Playlist
if "current_track_index" not in st.session_state:
    st.session_state.current_track_index = 0

# === TẢI FILE NỀN SỚM ===
img_base64 = get_base64(bg_file)
if img_base64 is None:
    st.error(f"❌ Không tìm thấy file {bg_file}. Vui lòng kiểm tra lại tên và đường dẫn file.")
    st.stop()
    
# TẢI FILE NỀN MOBILE
img_mobile_base64 = get_base64(bg_mobile_file)
if img_mobile_base64 is None:
    img_mobile_base64 = img_base64 
# ===================================================

# Lấy bài hát hiện tại
current_audio_file = AUDIO_FILES[st.session_state.current_track_index]
audio_base64 = get_base64(current_audio_file)

# CSS động để kiểm soát hiển thị video
is_main_page = st.session_state.show_main
video_display_style = "display: none;" if is_main_page else "display: flex;" 

# === Xử lý logic chuyển bài khi nhận được lệnh từ JavaScript ===
if "next_track" in st.session_state:
    if st.session_state.next_track:
        new_index = (st.session_state.current_track_index + 1) % len(AUDIO_FILES)
        st.session_state.current_track_index = new_index
        st.session_state.next_track = False
        st.rerun() # Bắt buộc Rerun để phát bài mới
elif "prev_track" in st.session_state:
    if st.session_state.prev_track:
        new_index = (st.session_state.current_track_index - 1 + len(AUDIO_FILES)) % len(AUDIO_FILES)
        st.session_state.current_track_index = new_index
        st.session_state.prev_track = False
        st.rerun() # Bắt buộc Rerun để phát bài mới
# =============================================================


# === CSS CHUNG VÀ VIDEO (Đã Fix Lỗi) ===
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

/* 2. FULLSCREEN TRIỆT ĐỂ */
header[data-testid="stHeader"], footer {{ display: none !important; }}
.block-container, section.main > div {{
    margin: 0 !important;
    padding: 0 !important;
    max-width: 100% !important;
    width: 100vw !important;
    height: 100vh !important;
}}

/* 3. CSS CHO VIDEO CONTAINER */
.video-container {{
    position: fixed; inset:0; width:100vw; height:100vh;
    justify-content:center; 
    align-items:center;
    background:black; 
    z-index:99999; 
    {video_display_style} 
    flex-direction: column; 
}}

/* Video settings giữ nguyên */
.video-bg {{ 
    max-width: 100%; 
    max-height: 100%;
    object-fit:contain; 
}}

/* Keyframes và animations giữ nguyên */
@keyframes fadeOut {{ 
    0% {{opacity:1;}}
    99% {{opacity:0.01;}}
    100%{{opacity:0; visibility:hidden; z-index:-1;}} 
}}
.intro-animation {{
    animation: fadeOut {FADE_DURATION_SECONDS}s ease-out {VIDEO_DURATION_SECONDS}s forwards; 
}}

/* 4. CSS CHO TRANG CHÍNH: BACKGROUND FIX */
.stApp {{
    background-color: #333; 
    background-image: linear-gradient(rgba(245,242,200,0.4), rgba(245,242,200,0.4)),
                      url("data:image/jpeg;base64,{img_base64}");
    
    background-attachment: fixed; 
    background-size: cover; 
    background-repeat: no-repeat;
    background-position: center center; 
    
    width: 100vw !important;
    height: 100vh !important;
    z-index:1;
}}

/* 5. MEDIA QUERY (FIX DỨT ĐIỂM BACKGROUND TRÊN MOBILE) */
@media screen and (max-width: 768px) {{
    .stApp {{
        background-image: linear-gradient(rgba(245,242,200,0.4), rgba(245,242,200,0.4)),
                          url("data:image/jpeg;base64,{img_mobile_base64}");
        background-size: cover; 
        background-color: #333; 
    }}
}}

/* 6. CSS CHO AUDIO PLAYER MỚI */
.audio-controls-container {{
    position: fixed; 
    top: 10px; 
    left: 10px; 
    z-index: 9999;
    display: flex;
    align-items: center;
    background: rgba(0, 0, 0, 0.4);
    border-radius: 8px;
    padding: 5px;
}}
.audio-button {{
    background: #4A90E2; 
    color: white;
    border: none;
    padding: 8px 12px;
    margin: 0 5px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    transition: background 0.3s;
}}
.audio-button:hover {{
    background: #3A7BB6;
}}
.track-info {{
    color: #FFF;
    font-size: 14px;
    margin-left: 10px;
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
    // CODE JAVASCRIPT ĐỂ FIX LỖI 100vh TRÊN MOBILE (Giữ nguyên)
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
    
    st.markdown(f"""
    <div class="video-container intro-animation" id="videoContainer">
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

# === KHỐI PHÁT NHẠC VÀ NÚT ĐIỀU KHIỂN MỚI ===
if audio_base64:
    current_track_name = AUDIO_FILES[st.session_state.current_track_index]
    track_number = st.session_state.current_track_index + 1
    total_tracks = len(AUDIO_FILES)

    # Sử dụng st.empty() để tạo ra một container cho JavaScript
    js_placeholder = st.empty()

    js_code = f"""
    <script>
        function setStreamlitValue(key, value) {{
            // Sử dụng Streamlit API để cập nhật Session State
            const iframe = window.parent.document.querySelector('iframe');
            if (iframe) {{
                iframe.contentWindow.postMessage({{ key: key, value: value }}, '*');
            }}
        }}

        // Hàm được gọi khi nhấn nút 'Next'
        function nextTrack() {{
            Streamlit.setComponentValue('next_track', true);
        }}

        // Hàm được gọi khi nhấn nút 'Previous'
        function prevTrack() {{
            Streamlit.setComponentValue('prev_track', true);
        }}
    </script>
    """
    
    # Đặt nội dung HTML/JS vào placeholder
    js_placeholder.markdown(f"""
    {js_code}
    <div class="audio-controls-container">
        <button class="audio-button" onclick="prevTrack()">⏮️ Prev</button>
        <audio id="backgroundAudio" autoplay loop controls>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        <button class="audio-button" onclick="nextTrack()">Next ⏭️</button>
        <div class="track-info">Track {track_number}/{total_tracks}: {current_track_name}</div>
    </div>
    """, unsafe_allow_html=True)

    # st.runtime.legacy_caching.clear_cache() # Thêm dòng này nếu gặp vấn đề về cache âm thanh
# =================================================================================
