import streamlit as st
import base64
import os
import json
import time

# === ĐỊNH NGHĨA HẰNG SỐ VÀ FILE ===
video_file = "airplane.mp4"
bg_file = "cabbase.jpg"
bg_mobile_file = "mobile.jpg" 
# CHỈ DÙNG MỘT BÀI NHẠC
AUDIO_FILES = ["background.mp3"] 

# Thời gian chuyển cảnh (Giữ nguyên)
VIDEO_DURATION_SECONDS = 5  
FADE_DURATION_SECONDS = 4   
TOTAL_ANIMATION_TIME_MS = (VIDEO_DURATION_SECONDS + FADE_DURATION_SECONDS) * 1000
# =========================================================================

# --- CẤU HÌNH BAN ĐẦU ---
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

# Hàm đọc file và chuyển thành Base64
@st.cache_data
def get_base64(file_path):
    """Đọc file và chuyển thành chuỗi Base64."""
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        return None

# --- Khởi tạo Session State ---
if "is_playing" not in st.session_state:
    st.session_state.is_playing = True
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = False 
if "intro_rendered" not in st.session_state:
    st.session_state.intro_rendered = False
if "current_track_index" not in st.session_state:
    st.session_state.current_track_index = 0

# === TẢI VÀ CHUYỂN ĐỔI TẤT CẢ FILE CẦN THIẾT ===
img_base64 = get_base64(bg_file)
if img_base64 is None: st.error(f"❌ Không tìm thấy file {bg_file}."); st.stop()
    
img_mobile_base64 = get_base64(bg_mobile_file)
if img_mobile_base64 is None: img_mobile_base64 = img_base64 

video_data = get_base64(video_file)
if video_data is None: st.error(f"❌ Không tìm thấy file {video_file}."); st.stop()

# Tải Base64 cho audio file
AUDIO_BASE64 = get_base64(AUDIO_FILES[0])
if AUDIO_BASE64 is None:
    st.error(f"❌ Không tìm thấy file âm thanh: {AUDIO_FILES[0]}."); st.stop()
        
# Biến Python để truyền vào JavaScript
current_audio_base64 = AUDIO_BASE64
current_track_name = AUDIO_FILES[0]
is_playing_state = st.session_state.is_playing 
is_mobile = st.session_state.is_mobile
# ===================================================

# --- LOGIC PHÁT HIỆN THIẾT BỊ ---
# FIX: Chỉ sử dụng st.query_params và lắng nghe tham số 'mobile_check' từ JS
if st.query_params.get("mobile_check") == ["true"]:
    st.session_state.is_mobile = True
elif st.query_params.get("mobile_check") == ["false"]:
    st.session_state.is_mobile = False
is_mobile = st.session_state.is_mobile


# --- CSS CHUNG VÀ JS FIX MOBILE VH & CHUYỂN CẢNH ---
css_js_placeholder = st.empty() 

# 💥 ĐÃ FIX: Thêm z-index cao cho text và điều chỉnh thời gian animation floatFade
css_js_code = f"""
<style>
/* 1. KHẮC PHỤC VIEWPORT TRÊN MOBILE và FULL HEIGHT cho PC */
html, body {{ 
    margin:0; padding:0; height:100%; overflow:hidden; background:black; height: 100%; 
}}
header[data-testid="stHeader"], footer {{ display: none !important; }}
.block-container, section.main > div {{
    margin: 0 !important; padding: 0 !important; max-width: 100% !important;
    width: 100vw !important; height: calc(var(--vh, 1vh) * 100) !important;
}}
.stApp, section.main {{
    height: calc(var(--vh, 1vh) * 100) !important; min-height: calc(var(--vh, 1vh) * 100) !important;
}}

/* 2. CSS CHO VIDEO CONTAINER */
.video-container {{
    position: fixed; inset:0; 
    width:100vw; height:calc(var(--vh, 1vh) * 100);
    justify-content:center; align-items:center; background:black; 
    z-index: 99999;
    display: flex; 
    flex-direction: column; 
    opacity: 1; 
    transition: opacity 0.5s; 
}}

/* Lớp ẩn hoàn toàn */
.video-container.hidden {{
    opacity: 0 !important;
    z-index: -1 !important;
    display: none !important;
}}

/* 💥 FIX MOBILE VIDEO FIT (Quan trọng) */
.intro-media {{ 
    width: 100vw; 
    height: calc(var(--vh, 1vh) * 100); 
    object-fit:cover; 
}}

/* CSS CHO DÒNG CHỮ INTRO VÀ HIỆU ỨNG */
.video-text {{
    position:absolute; bottom:12vh; width:100%; text-align:center;
    font-family:'Special Elite', cursive; font-size:clamp(24px,5vw,44px);
    font-weight:bold; color:#fff;
    text-shadow: 0 0 20px rgba(255,255,255,0.8), 0 0 40px rgba(180,220,255,0.6), 0 0 60px rgba(255,255,255,0.4);
    opacity:0;
    /* 🔑 FIX: Z-INDEX cao để text không bị video che */
    z-index: 100000; 
    /* 🔑 FIX: floatFade 4s delay 5s để kết thúc đồng bộ với video container fade (9s) */
    animation: appear 3s ease-in forwards, floatFade {FADE_DURATION_SECONDS}s ease-in {VIDEO_DURATION_SECONDS}s forwards;
}}

/* Keyframes */
@keyframes fadeOut {{ 
    0% {{opacity:1;}}
    100%{{opacity:0;}} 
}}
@keyframes appear {{ 0% {{opacity:0; filter:blur(8px); transform:translateY(40px);}} 100%{{opacity:1; filter:blur(0); transform:translateY(0);}} }}
@keyframes floatFade {{ 0% {{opacity:1; filter:blur(0); transform:translateY(0);}} 100%{{opacity:0; filter:blur(12px); transform:translateY(-30px) scale(1.05);}} }}

/* 3. CSS CHO TRANG CHÍNH: BACKGROUND FIX */
.stApp {{
    z-index:1; 
    background-color: #333; 
    background-image: linear-gradient(rgba(245,242,200,0.4), rgba(245,242,200,0.4)),
                      url("data:image/jpeg;base64,{img_base64}");
    background-attachment: fixed; background-size: cover; background-repeat: no-repeat; background-position: center center; 
}}

/* Ẩn/Hiện nội dung chính */
.hide-on-start {{ opacity: 0; }}
.show-after-animation {{ opacity: 1 !important; transition: opacity 1s ease-in 0.5s; }}

/* 4. MEDIA QUERY cho Mobile Background */
@media screen and (max-width: 768px) {{
    .stApp {{
        background-image: linear-gradient(rgba(245,242,200,0.4), rgba(245,242,200,0.4)),
                          url("data:image/jpeg;base64,{img_mobile_base64}");
        background-size: cover; background-color: #333; 
    }}
}}

/* Các CSS Player và Title khác giữ nguyên */
.custom-audio-player {{ position: fixed; top: 10px; left: 10px; z-index: 9999; display: flex; flex-direction: column; width: 300px; background: rgba(0, 0, 0, 0.7); border-radius: 8px; padding: 10px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5); }}
.player-info {{ color: white; font-size: 0.9em; margin-bottom: 5px; }}
.progress-bar {{ width: 100%; height: 5px; background: #555; cursor: pointer; border-radius: 3px; margin: 5px 0; }}
.progress-filled {{ height: 100%; background: #4CAF50; width: 0%; border-radius: 3px; transition: width 0.1s linear; }}
.time-display {{ display: flex; justify-content: space-between; color: white; font-size: 0.8em; }}
.player-controls {{ display: flex; justify-content: center; margin-top: 10px; }}
.control-button {{ background: none; border: none; color: white; font-size: 1.5em; cursor: pointer; padding: 0 10px; }}

.main-title {{ font-family:'Special Elite', cursive; font-size: clamp(36px,5vw,48px); font-weight:bold; text-align:center; color:#3e2723; margin-top:50px; text-shadow:2px 2px 0 #fff,0 0 25px #f0d49b,0 0 50px #bca27a; }}
.block-container {{ padding-top:2rem !important; padding-left:1rem !important; padding-right:1rem !important;}}
</style>

<script>
    // 💥 FIX MOBILE VH: Tính toán và áp dụng chiều cao Viewport chính xác
    function setVhProperty() {{
        let vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${{vh}}px`);
        
        const media = document.getElementById('introMedia');
        const container = document.getElementById('videoContainer');
        if (media) {{ media.style.height = `calc(${{vh}}px * 100)`; }}
        if (container) {{ container.style.height = `calc(${{vh}}px * 100)`; }}
    }}
    
    // 💥 PHÁT HIỆN THIẾT BỊ VÀ RELOAD STREAMLIT CHỈ MỘT LẦN
    function checkDeviceAndReload() {{
        const isMobileDevice = /Mobi|Android|iPhone|iPad|iPod|Windows Phone/i.test(navigator.userAgent) || window.innerWidth < 768;
        const currentParams = new URLSearchParams(window.location.search);
        
        // Reload chỉ khi tham số mobile_check chưa được set
        if (currentParams.get('mobile_check') === null) {{
            const newUrl = new URL(window.location.href);
            newUrl.searchParams.set('mobile_check', isMobileDevice ? 'true' : 'false');
            window.location.replace(newUrl);
        }}
    }}
    
    // LOGIC CHUYỂN CẢNH HOÀN TOÀN BẰNG JS 
    const totalDuration = {TOTAL_ANIMATION_TIME_MS};
    
    function handleIntroTransition() {{
        const videoContainer = document.getElementById('videoContainer');
        const mainContent = document.getElementById('mainContentContainer');
        
        if (videoContainer) {{
            // Áp dụng animation fadeOut
            videoContainer.style.animation = `fadeOut {FADE_DURATION_SECONDS}s ease-out {VIDEO_DURATION_SECONDS}s forwards`;

            // Ẩn video và hiển thị nội dung chính sau khi animation kết thúc
            setTimeout(() => {{
                videoContainer.classList.add('hidden'); 
                
                if (mainContent) {{
                    mainContent.classList.add('show-after-animation');
                }}
            }}, totalDuration + 500); // Thêm 500ms để đảm bảo mượt mà
        }} else if (mainContent) {{
            mainContent.classList.add('show-after-animation');
        }}
    }}
    
    // Chạy các hàm khi script được tải
    setVhProperty();
    window.addEventListener('resize', setVhProperty);
    document.addEventListener('DOMContentLoaded', () => {{
        checkDeviceAndReload(); 
        handleIntroTransition();
        setVhProperty();
    }});
</script>
"""
css_js_placeholder.markdown(css_js_code, unsafe_allow_html=True)


# --- RENDER VIDEO VÀ NỘI DUNG CHÍNH (Đồng thời) ---

# 1. RENDER VIDEO INTRO 
intro_rendered = st.session_state.intro_rendered

if not intro_rendered:
    
    st.session_state.intro_rendered = True
    
    # Chỉ render video tag nếu có data
    if video_data:
        media_source = f"data:video/mp4;base64,{video_data}"
        media_tag = f"""
        <video id="introMedia" class="intro-media" autoplay muted playsinline>
            <source src="{media_source}" type="video/mp4">
        </video>
        """
        
        st.markdown(f"""
        <div class="video-container" id="videoContainer">
            {media_tag}
            <div class="video-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        </div>
        """, unsafe_allow_html=True)


# 2. RENDER NỘI DUNG CHÍNH (z-index thấp hơn, sẽ từ từ hiện ra)
initial_main_class = 'hide-on-start'
if intro_rendered:
    initial_main_class = 'show-after-animation'

st.markdown(f'<div id="mainContentContainer" class="{initial_main_class}">', unsafe_allow_html=True)

st.markdown('<div class="main-title">📜 TỔ BẢO DƯỠNG SỐ 1</div>', unsafe_allow_html=True)
st.write("Chào mừng bạn đến với website ✈️")


# 3. KHỐI PHÁT NHẠC TÙY CHỈNH (CHỈ 1 BÀI)
if current_audio_base64:

    js_code_player = f"""
    <script>
        const AUDIO_BASE64 = "{current_audio_base64}";
        const TRACK_NAME = "{current_track_name}";
        let isPlaying = {'true' if is_playing_state else 'false'};
        let audioPlayer; 
        
        function initPlayer() {{
            audioPlayer = document.getElementById('customAudioPlayer');
            
            if (audioPlayer) {{
                // FIX: Play/Pause dựa trên Session State
                if (isPlaying) {{
                    audioPlayer.play().catch(error => {{
                        // Bắt lỗi autoplay fail (thường trên mobile)
                        document.getElementById('playPauseButton').innerHTML = '▶️';
                        isPlaying = false;
                        audioPlayer.pause();
                    }});
                }} else {{
                    audioPlayer.pause();
                }}

                // Gắn event listeners
                audioPlayer.addEventListener('timeupdate', window.updateProgress);
                audioPlayer.addEventListener('loadedmetadata', window.updateDuration);
                // Tự động lặp lại
                audioPlayer.addEventListener('ended', () => {{ 
                    audioPlayer.currentTime = 0;
                    audioPlayer.play();
                }});
                
                const progressBarElement = document.getElementById('progressBar');
                if (progressBarElement) {{
                    progressBarElement.addEventListener('click', window.seekAudio);
                }}
            }}
            
            updateTrackInfo();
            updateDuration(); 
        }}

        function formatTime(seconds) {{ 
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = Math.floor(seconds % 60);
            return `${{String(minutes).padStart(2, '0')}}:${{String(remainingSeconds).padStart(2, '0')}}`;
        }}
        
        function updateTrackInfo() {{ 
            const infoElement = document.getElementById('trackInfo');
            if(infoElement) {{
                 infoElement.textContent = `Bài hát: ${{TRACK_NAME}}`;
            }}
        }}
        
        window.updateDuration = function() {{ 
            const durationTimeDisplay = document.getElementById('durationTime');
            if (audioPlayer && durationTimeDisplay) {{
                if (audioPlayer.duration && isFinite(audioPlayer.duration)) {{
                    durationTimeDisplay.textContent = formatTime(audioPlayer.duration);
                }} else {{
                    durationTimeDisplay.textContent = '--:--';
                }}
            }}
        }}
        
        window.updateProgress = function() {{ 
            const progressFilled = document.getElementById('progressFilled');
            const currentTimeDisplay = document.getElementById('currentTime');
            if (audioPlayer && progressFilled && currentTimeDisplay && audioPlayer.duration) {{
                const percentage = (audioPlayer.currentTime / audioPlayer.duration) * 100;
                progressFilled.style.width = percentage + '%';
                currentTimeDisplay.textContent = formatTime(audioPlayer.currentTime);
            }}
        }}

        window.togglePlayPause = function() {{ 
            const button = document.getElementById('playPauseButton');

            if (audioPlayer.paused) {{
                audioPlayer.play().catch(error => {{
                    button.innerHTML = '▶️';
                    isPlaying = false;
                    audioPlayer.pause();
                }});
                button.innerHTML = '⏸️';
                isPlaying = true;
            }} else {{
                audioPlayer.pause();
                button.innerHTML = '▶️';
                isPlaying = false;
            }}
        }}
        
        window.seekAudio = function(e) {{ 
            const progressBar = document.getElementById('progressBar');
            const rect = progressBar.getBoundingClientRect();
            const clickPosition = e.clientX - rect.left;
            const totalWidth = progressBar.offsetWidth;
            const clickRatio = clickPosition / totalWidth;
            
            if (audioPlayer.duration) {{
                audioPlayer.currentTime = audioPlayer.duration * clickRatio;
            }}
        }}

        document.addEventListener('DOMContentLoaded', initPlayer);
    </script>
    """
    
    st.markdown(f"""
    <div style="display: none;">
        <audio id="customAudioPlayer" src="data:audio/mp3;base64,{current_audio_base64}" autoplay></audio>
    </div>
    <div class="custom-audio-player">
        <div class="player-info" id="trackInfo">Bài hát: {current_track_name}</div>
        <div class="progress-bar" id="progressBar">
            <div class="progress-filled" id="progressFilled"></div>
        </div>
        <div class="time-display">
            <span id="currentTime">00:00</span>
            <span id="durationTime">--:--</span>
        </div>
        <div class="player-controls">
            <button class="control-button" style="visibility:hidden;">&nbsp;</button>
            <button class="control-button" id="playPauseButton" onclick="window.togglePlayPause()">
                {'⏸️' if is_playing_state else '▶️'}
            </button>
            <button class="control-button" style="visibility:hidden;">&nbsp;</button>
        </div>
    </div>
    {js_code_player}
    """, unsafe_allow_html=True)
    
st.markdown('</div>', unsafe_allow_html=True) # Kết thúc div mainContentContainer
