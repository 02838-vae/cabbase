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
if "show_main" not in st.session_state:
    # Mặc định là FALSE, nhưng nếu là lần render lại sau khi chuyển cảnh (từ JS), nó sẽ là True
    st.session_state.show_main = False 
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
    # Dừng nếu thiếu file âm thanh
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

# --- LOGIC CHUYỂN CẢNH VÀ CSS CHUNG ---

# Kiểm tra query parameter do JS gửi lên để biết khi nào chuyển sang trang chính
if st.query_params.get("show_main") == "true":
    st.session_state.show_main = True
    # Xóa query param để không bị render lại liên tục
    del st.query_params["show_main"] 

is_main_page = st.session_state.show_main

# CSS cho tất cả các trạng thái
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

/* 2. CSS CHO VIDEO CONTAINER */
.video-container {{
    position: fixed; inset:0; 
    width:100vw; height:calc(var(--vh, 1vh) * 100);
    justify-content:center; align-items:center; background:black; 
    z-index: 99999;
    display: flex; 
    flex-direction: column; 
    opacity: 1; /* Bắt đầu luôn hiển thị */
    /* Animation fadeOut chỉ áp dụng khi cần */
}}

/* ẨN video ngay lập tức nếu đã chuyển sang trang chính */
.video-container.hidden {{
    display: none !important;
    z-index: -1 !important;
}}

/* FIX VIDEO MOBILE FIT */
.video-bg {{ 
    width: 100vw; height: calc(var(--vh, 1vh) * 100);
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

/* Ẩn nội dung trang chính lúc khởi động để tránh flicker */
.hide-on-start {{
    opacity: 0;
    transition: opacity 1s ease-in;
}}
/* Hiển thị nội dung trang chính khi animation xong */
.show-after-animation {{
    opacity: 1 !important;
}}

/* 4. MEDIA QUERY cho Mobile Background */
@media screen and (max-width: 768px) {{
    .stApp {{
        background-image: linear-gradient(rgba(245,242,200,0.4), rgba(245,242,200,0.4)),
                          url("data:image/jpeg;base64,{img_mobile_base64}");
        background-size: cover; background-color: #333; 
    }}
}}

/* 5. CUSTOM AUDIO PLAYER (FIX DESIGN MOBILE) */
.custom-audio-player {{
    position: fixed; top: 10px; left: 10px; z-index: 9999;
    display: flex; flex-direction: column;
    width: 300px; /* FIX: THU NHỎ CHO MOBILE */
    background: rgba(0, 0, 0, 0.7);
    border-radius: 8px; padding: 10px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
}}
.player-info {{ color: #FFF; font-size: 13px; text-align: center; margin-bottom: 8px; }}
.player-controls {{
    display: flex; justify-content: space-around; align-items: center;
}}
.control-button {{
    background: none; border: none; color: #FFF; font-size: 20px;
    cursor: pointer; padding: 5px; transition: color 0.2s;
}}
.control-button:hover {{ color: #4A90E2; }}
.progress-bar {{
    height: 5px; background: #555; margin: 10px 0;
    border-radius: 2px; cursor: pointer;
}}
.progress-filled {{ height: 100%; width: 0%; background: #4A90E2; border-radius: 2px; }}
.time-display {{
    display: flex; justify-content: space-between; color: #AAA; font-size: 11px;
}}
.main-title {{
    font-family:'Special Elite', cursive; font-size: clamp(36px,5vw,48px);
    font-weight:bold; text-align:center; color:#3e2723; margin-top:50px;
    text-shadow:2px 2px 0 #fff,0 0 25px #f0d49b,0 0 50px #bca27a;
}}
/* Khôi phục padding nhẹ cho nội dung trang chính */
.block-container {{ padding-top:2rem !important; padding-left:1rem !important; padding-right:1rem !important;}}
</style>

<script>
    // JS Fix VH (Giữ nguyên)
    function setVhProperty() {{
        let vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${{vh}}px`);
        const stApp = window.parent.document.querySelector('.stApp');
        if (stApp) {{ stApp.style.height = `calc(${{vh}}px * 100)`; }}
    }}
    window.addEventListener('load', setVhProperty);
    window.addEventListener('resize', setVhProperty);
    if (document.readyState === 'complete') {{ setVhProperty(); }}
</script>
""", unsafe_allow_html=True)


# --- LOGIC RENDER ---

# 1. RENDER VIDEO INTRO VÀ CƠ CHẾ CHUYỂN CẢNH
if not is_main_page:
    video_data = get_base64(video_file)
    if video_data is None:
        st.error(f"❌ Không tìm thấy file {video_file}.")
        st.stop()
        
    # Thêm class intro-animation vào container và lắng nghe sự kiện
    st.markdown(f"""
    <div class="video-container" id="videoContainer">
        <video id="introVideo" class="video-bg intro-animation" autoplay muted playsinline>
            <source src="data:video/mp4;base64,{video_data}" type="video/mp4">
        </video>
        <div class="video-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    </div>
    
    <script>
        // 💥 FIX LỖI TỐI ĐEN: Dùng setTimeout để ẩn container và reload trang chính xác
        const totalDuration = {TOTAL_ANIMATION_TIME_MS};
        
        // 1. Áp dụng animation fadeOut
        const videoContainer = document.getElementById('videoContainer');
        videoContainer.style.animation = `fadeOut {FADE_DURATION_SECONDS}s ease-out {VIDEO_DURATION_SECONDS}s forwards`;
        
        // 2. Tự động chuyển trạng thái và ẩn video container sau khi animation kết thúc
        setTimeout(() => {{
            videoContainer.classList.add('hidden'); // Ẩn video container
            
            // Dùng Streamlit.setComponentValue để giao tiếp với Python (cần thư viện Streamlit Components nếu muốn clean hơn, nhưng ta dùng cách này để đơn giản hóa)
            // Thay thế bằng cách đơn giản nhất: thay đổi URL và reload
            const url = new URL(window.location.href);
            url.searchParams.set('show_main', 'true');
            window.location.replace(url); 
            
        }}, totalDuration + 100); 
    </script>
    """, unsafe_allow_html=True)
    
    # 💥 QUAN TRỌNG: Chỉ dừng nếu không có query param, nếu có thì sẽ để JS xử lý.
    if st.query_params.get("show_main") != "true":
        st.stop() 


# 2. RENDER TRANG CHÍNH VÀ PLAYER (Luôn chạy sau khi có tín hiệu chuyển cảnh)

# Thêm class để ẩn nội dung trang chính khi mới vào
content_class = "hide-on-start"
if is_main_page:
    # Nếu đã chuyển cảnh, nội dung sẽ từ từ hiển thị
    content_class = "show-after-animation"

st.markdown(f'<div class="{content_class}">', unsafe_allow_html=True)
st.markdown('<div class="main-title">📜 TỔ BẢO DƯỠNG SỐ 1</div>', unsafe_allow_html=True)
st.write("Chào mừng bạn đến với website ✈️")


# === KHỐI PHÁT NHẠC TÙY CHỈNH (CUSTOM AUDIO PLAYER) ===
if current_audio_base64:

    js_code = f"""
    <script>
        const AUDIO_BASE64_LIST = {audio_base64_json};
        const AUDIO_FILES_NAME = {json.dumps(AUDIO_FILES)}; // Đảm bảo list tên file cũng là JSON hợp lệ
        const TOTAL_TRACKS = {total_tracks};
        let currentTrackIndex = {current_track_index};
        let isPlaying = {'true' if is_playing_state else 'false'};
        let audioPlayer; 
        
        // Hàm này chạy sau khi DOMContentLoaded
        function initPlayer() {{
            audioPlayer = document.getElementById('customAudioPlayer');
            
            // Gán lại trạng thái ban đầu của player
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
            audioPlayer.addEventListener('timeupdate', updateProgress);
            audioPlayer.addEventListener('loadedmetadata', updateDuration);
            audioPlayer.addEventListener('ended', () => switchTrack(1));
            document.getElementById('progressBar').addEventListener('click', seekAudio);
            
            updateTrackInfo();
            updateDuration(); // Gọi lần đầu để hiển thị --:-- hoặc thời lượng
        }}

        function formatTime(seconds) {{
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = Math.floor(seconds % 60);
            return `${{String(minutes).padStart(2, '0')}}:${{String(remainingSeconds).padStart(2, '0')}}`;
        }}
        
        function updateTrackInfo() {{
            document.getElementById('trackInfo').textContent = 
                `Track ${{currentTrackIndex + 1}}/${{TOTAL_TRACKS}}: ${{AUDIO_FILES_NAME[currentTrackIndex]}}`;
        }}
        
        function updateDuration() {{
            const durationTimeDisplay = document.getElementById('durationTime');
            if (audioPlayer.duration) {{
                durationTimeDisplay.textContent = formatTime(audioPlayer.duration);
            }} else {{
                durationTimeDisplay.textContent = '--:--';
            }}
        }}
        
        function updateProgress() {{
            const progressFilled = document.getElementById('progressFilled');
            const currentTimeDisplay = document.getElementById('currentTime');
            if (audioPlayer.duration) {{
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
            audioPlayer.load(); // 💥 FIX LỖI CHUYỂN BÀI: Buộc tải lại nguồn Base64 mới

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

        // Chức năng chuyển bài 
        window.switchTrack = function(direction) {{
            const wasPlaying = !audioPlayer.paused;
            
            currentTrackIndex = (currentTrackIndex + direction + TOTAL_TRACKS) % TOTAL_TRACKS;
            loadTrack(wasPlaying); 
        }}

        // Chức năng Play/Pause
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
        
        // Chức năng tua nhạc
        function seekAudio(e) {{
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
    
    # Ẩn thẻ audio gốc đi
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
            <button class="control-button" onclick="switchTrack(-1)">⏮️</button>
            <button class="control-button" id="playPauseButton" onclick="togglePlayPause()">
                {'⏸️' if is_playing_state else '▶️'}
            </button>
            <button class="control-button" onclick="switchTrack(1)">⏭️</button>
        </div>
    </div>
    {js_code}
    """, unsafe_allow_html=True)
    
st.markdown('</div>', unsafe_allow_html=True) # Kết thúc div content_class
# =================================================================================
