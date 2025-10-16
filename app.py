import streamlit as st
import base64
import os
import json
import time

# === ĐỊNH NGHĨA HẰNG SỐ VÀ FILE ===
video_file = "airplane.mp4"
bg_file = "cabbase.jpg"
bg_mobile_file = "mobile.jpg" 

# Danh sách bài hát 
AUDIO_FILES = ["background.mp3", "background2.mp3", "background3.mp3", "background4.mp3", "background5.mp3"]

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
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        return None

# --- Khởi tạo Session State ---
if "current_track_index" not in st.session_state:
    st.session_state.current_track_index = 0
if "is_playing" not in st.session_state:
    st.session_state.is_playing = True

# === TẢI VÀ CHUYỂN ĐỔI TẤT CẢ FILE CẦN THIẾT ===
img_base64 = get_base64(bg_file)
if img_base64 is None: st.error(f"❌ Không tìm thấy file {bg_file}."); st.stop()
    
img_mobile_base64 = get_base64(bg_mobile_file)
if img_mobile_base64 is None: img_mobile_base64 = img_base64 

# Tải Base64 cho tất cả audio files
AUDIO_BASE64_LIST = [get_base64(f) for f in AUDIO_FILES if get_base64(f)]

if len(AUDIO_BASE64_LIST) != len(AUDIO_FILES):
    st.error("❌ Thiếu một hoặc nhiều file âm thanh. Vui lòng kiểm tra lại tên và vị trí file.")
    st.stop()
        
# Biến Python để truyền vào JavaScript
current_track_index = st.session_state.current_track_index
current_audio_base64 = AUDIO_BASE64_LIST[current_track_index]
current_track_name = AUDIO_FILES[current_track_index]
total_tracks = len(AUDIO_FILES)
is_playing_state = st.session_state.is_playing 
audio_base64_json = json.dumps(AUDIO_BASE64_LIST)
# ===================================================

# --- CSS CHUNG VÀ JS FIX MOBILE VH ---
st.markdown(f"""
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

/* 2. CSS CHO VIDEO CONTAINER (Sẽ được ẩn bằng JS sau animation) */
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

/* FIX MOBILE VIDEO FIT (Quan trọng: Dùng vh và object-fit) */
.video-bg {{ 
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
    animation: appear 3s ease-in forwards, floatFade 3s ease-in 5s forwards;
}}

/* Keyframes */
@keyframes fadeOut {{ 
    0% {{opacity:1;}}
    100%{{opacity:0;}} 
}}

/* 3. CSS CHO TRANG CHÍNH: BACKGROUND FIX */
.stApp {{
    z-index:1; 
    background-color: #333; 
    background-image: linear-gradient(rgba(245,242,200,0.4), rgba(245,242,200,0.4)),
                      url("data:image/jpeg;base64,{img_base64}");
    
    background-attachment: fixed; background-size: cover; background-repeat: no-repeat; background-position: center center; 
}}

/* Ẩn nội dung trang chính lúc khởi động */
.hide-on-start {{
    opacity: 0;
}}

/* Hiển thị nội dung trang chính */
.show-after-animation {{
    opacity: 1 !important;
    transition: opacity 1s ease-in 0.5s; 
}}

/* 4. MEDIA QUERY cho Mobile Background */
@media screen and (max-width: 768px) {{
    .stApp {{
        background-image: linear-gradient(rgba(245,242,200,0.4), rgba(245,242,200,0.4)),
                          url("data:image/jpeg;base64,{img_mobile_base64}");
        background-size: cover; background-color: #333; 
    }}
}}

/* 5. CUSTOM AUDIO PLAYER */
.custom-audio-player {{
    position: fixed; top: 10px; left: 10px; z-index: 9999;
    display: flex; flex-direction: column;
    width: 300px; 
    background: rgba(0, 0, 0, 0.7);
    border-radius: 8px; padding: 10px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
}}
.main-title {{
    font-family:'Special Elite', cursive; font-size: clamp(36px,5vw,48px);
    font-weight:bold; text-align:center; color:#3e2723; margin-top:50px;
    text-shadow:2px 2px 0 #fff,0 0 25px #f0d49b,0 0 50px #bca27a;
}}
.block-container {{ padding-top:2rem !important; padding-left:1rem !important; padding-right:1rem !important;}}
</style>

<script>
    // 💥 FIX MOBILE VH: Tính toán và áp dụng chiều cao Viewport chính xác
    function setVhProperty() {{
        let vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${{vh}}px`);
        
        // Cập nhật chiều cao video/container
        const video = document.getElementById('introVideo');
        const container = document.getElementById('videoContainer');
        if (video) {{ video.style.height = `calc(${{vh}}px * 100)`; }}
        if (container) {{ container.style.height = `calc(${{vh}}px * 100)`; }}
    }}
    
    setVhProperty();
    window.addEventListener('resize', setVhProperty);
    document.addEventListener('DOMContentLoaded', setVhProperty);
    
    // LOGIC CHUYỂN CẢNH HOÀN TOÀN BẰNG JS (FIX TREO MÀN HÌNH)
    const totalDuration = {TOTAL_ANIMATION_TIME_MS};
    
    function handleIntroTransition() {{
        const videoContainer = document.getElementById('videoContainer');
        const mainContent = document.getElementById('mainContentContainer');
        
        if (videoContainer) {{
            // 1. Áp dụng animation fadeOut cho video container
            videoContainer.style.animation = `fadeOut {FADE_DURATION_SECONDS}s ease-out {VIDEO_DURATION_SECONDS}s forwards`;

            // 2. Ẩn video và hiển thị nội dung chính sau khi animation kết thúc
            setTimeout(() => {{
                videoContainer.classList.add('hidden'); // Ẩn video container
                
                // Hiển thị nội dung chính
                if (mainContent) {{
                    mainContent.classList.add('show-after-animation');
                }}
                
            }}, totalDuration + 500); // Thêm 500ms buffer an toàn
        }} else if (mainContent) {{
            // Nếu video không tồn tại (đã refresh trang), đảm bảo nội dung chính hiển thị
            mainContent.classList.add('show-after-animation');
        }}
    }}
    
    document.addEventListener('DOMContentLoaded', handleIntroTransition);
</script>
""", unsafe_allow_html=True)


# --- RENDER VIDEO VÀ NỘI DUNG CHÍNH (Đồng thời) ---

# 1. RENDER VIDEO INTRO (z-index cao hơn, sẽ tự ẩn bằng JS)
video_data = get_base64(video_file)
if video_data:
    st.markdown(f"""
    <div class="video-container" id="videoContainer">
        <video id="introVideo" class="video-bg" autoplay muted playsinline>
            <source src="data:video/mp4;base64,{video_data}" type="video/mp4">
        </video>
        <div class="video-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    </div>
    """, unsafe_allow_html=True)


# 2. RENDER NỘI DUNG CHÍNH (z-index thấp hơn, sẽ từ từ hiện ra)
st.markdown(f'<div id="mainContentContainer" class="hide-on-start">', unsafe_allow_html=True)

st.markdown('<div class="main-title">📜 TỔ BẢO DƯỠNG SỐ 1</div>', unsafe_allow_html=True)
st.write("Chào mừng bạn đến với website ✈️")


# 3. KHỐI PHÁT NHẠC TÙY CHỈNH (CUSTOM AUDIO PLAYER)
if current_audio_base64:

    js_code = f"""
    <script>
        const AUDIO_BASE64_LIST = {audio_base64_json};
        const AUDIO_FILES_NAME = {json.dumps(AUDIO_FILES)};
        const TOTAL_TRACKS = {total_tracks};
        let currentTrackIndex = {current_track_index};
        let isPlaying = {'true' if is_playing_state else 'false'};
        let audioPlayer; 
        
        function initPlayer() {{
            audioPlayer = document.getElementById('customAudioPlayer');
            
            if (audioPlayer) {{
                if (isPlaying) {{
                    audioPlayer.play().catch(error => {{
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
                audioPlayer.addEventListener('ended', () => window.switchTrack(1));
                
                // Kiểm tra xem các element tồn tại trước khi thêm listener
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
                 infoElement.textContent = 
                    `Track ${{currentTrackIndex + 1}}/${{TOTAL_TRACKS}}: ${{AUDIO_FILES_NAME[currentTrackIndex]}}`;
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

        // Chức năng tải và phát bài hát
        function loadTrack(shouldPlay) {{ 
            const newTrackBase64 = AUDIO_BASE64_LIST[currentTrackIndex];
            const newSrc = `data:audio/mp3;base64,${{newTrackBase64}}`;

            audioPlayer.src = newSrc;
            audioPlayer.load(); // Buộc tải lại nguồn Base64 mới

            updateTrackInfo();
            
            if (shouldPlay) {{
                audioPlayer.play().catch(error => {{
                    document.getElementById('playPauseButton').innerHTML = '▶️';
                    isPlaying = false;
                    audioPlayer.pause();
                }});
                document.getElementById('playPauseButton').innerHTML = '⏸️';
                isPlaying = true;
            }} else {{
                audioPlayer.pause();
                document.getElementById('playPauseButton').innerHTML = '▶️';
                isPlaying = false;
            }}
        }}

        // Chức năng chuyển bài (Gắn vào window)
        window.switchTrack = function(direction) {{
            const wasPlaying = !audioPlayer.paused;
            
            currentTrackIndex = (currentTrackIndex + direction + TOTAL_TRACKS) % TOTAL_TRACKS;
            loadTrack(wasPlaying); 
        }}

        // Chức năng Play/Pause (Gắn vào window)
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
        
        // Chức năng tua nhạc (Gắn vào window)
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
        <div class="player-info" id="trackInfo">Track {current_track_index + 1}/{total_tracks}: {current_track_name}</div>
        <div class="progress-bar" id="progressBar">
            <div class="progress-filled" id="progressFilled"></div>
        </div>
        <div class="time-display">
            <span id="currentTime">00:00</span>
            <span id="durationTime">--:--</span>
        </div>
        <div class="player-controls">
            <button class="control-button" onclick="window.switchTrack(-1)">⏮️</button>
            <button class="control-button" id="playPauseButton" onclick="window.togglePlayPause()">
                {'⏸️' if is_playing_state else '▶️'}
            </button>
            <button class="control-button" onclick="window.switchTrack(1)">⏭️</button>
        </div>
    </div>
    {js_code}
    """, unsafe_allow_html=True)
    
st.markdown('</div>', unsafe_allow_html=True) # Kết thúc div mainContentContainer
