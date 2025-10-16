import streamlit as st
import base64
import os
import json
import time

# === ĐỊNH NGHĨA HẰNG SỐ VÀ FILE ===
video_file = "airplane.mp4"
bg_file = "cabbase.jpg"
bg_mobile_file = "mobile.jpg" 
video_fallback_image = "airplane_fallback.jpg" 

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
if "is_mobile" not in st.session_state:
    # Mặc định là False, sẽ được JS cập nhật
    st.session_state.is_mobile = False 
if "intro_rendered" not in st.session_state:
    st.session_state.intro_rendered = False


# === TẢI VÀ CHUYỂN ĐỔI TẤT CẢ FILE CẦN THIẾT ===
img_base64 = get_base64(bg_file)
if img_base64 is None: st.error(f"❌ Không tìm thấy file {bg_file}."); st.stop()
    
img_mobile_base64 = get_base64(bg_mobile_file)
if img_mobile_base64 is None: img_mobile_base64 = img_base64 

video_data = get_base64(video_file)
video_fallback_data = get_base64(video_fallback_image)

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
is_mobile = st.session_state.is_mobile
# ===================================================

# --- CSS CHUNG VÀ JS FIX MOBILE VH ---
css_js_placeholder = st.empty() 

# 💥 FIX: Đã loại bỏ logic st.experimental_get_query_params()
# Thay vào đó, chúng ta sẽ dựa vào JS để set tham số 'mobile_check'
if st.query_params.get("mobile_check") == ["true"]:
    st.session_state.is_mobile = True
elif st.query_params.get("mobile_check") == ["false"]:
    st.session_state.is_mobile = False
is_mobile = st.session_state.is_mobile


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

/* 2. CSS CHO VIDEO/IMAGE CONTAINER */
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

/* FIX MOBILE VIDEO FIT (Áp dụng cho cả video và image) */
.intro-media {{ 
    width: 100vw; 
    height: calc(var(--vh, 1vh) * 100); 
    object-fit:cover; 
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

/* Hiển thị nội dung chính */
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

/* Khối CSS cho Player và Title giữ nguyên... */
.player-info {{ color: #FFF; font-size: 13px; text-align: center; margin-bottom: 8px; }}
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
        
        const media = document.getElementById('introMedia');
        const container = document.getElementById('videoContainer');
        if (media) {{ media.style.height = `calc(${{vh}}px * 100)`; }}
        if (container) {{ container.style.height = `calc(${{vh}}px * 100)`; }}
    }}
    
    // 💥 PHÁT HIỆN THIẾT BỊ VÀ RELOAD STREAMLIT CHỈ MỘT LẦN
    function checkDeviceAndReload() {{
        // Logic phát hiện mobile
        const isMobileDevice = /Mobi|Android|iPhone|iPad|iPod|Windows Phone/i.test(navigator.userAgent) || window.innerWidth < 768;
        const currentParams = new URLSearchParams(window.location.search);
        
        // Chỉ reload nếu tham số chưa được set hoặc giá trị bị lệch
        if (currentParams.get('mobile_check') === null) {{
            const newUrl = new URL(window.location.href);
            newUrl.searchParams.set('mobile_check', isMobileDevice ? 'true' : 'false');
            // Dùng replace để tránh tạo lịch sử
            window.location.replace(newUrl);
        }}
    }}
    
    // LOGIC CHUYỂN CẢNH HOÀN TOÀN BẰNG JS (FIX TREO MÀN HÌNH)
    const totalDuration = {TOTAL_ANIMATION_TIME_MS};
    
    function handleIntroTransition() {{
        const videoContainer = document.getElementById('videoContainer');
        const mainContent = document.getElementById('mainContentContainer');
        
        if (videoContainer) {{
            videoContainer.style.animation = `fadeOut {FADE_DURATION_SECONDS}s ease-out {VIDEO_DURATION_SECONDS}s forwards`;

            setTimeout(() => {{
                videoContainer.classList.add('hidden'); 
                
                if (mainContent) {{
                    mainContent.classList.add('show-after-animation');
                }}
            }}, totalDuration + 500); 
        }} else if (mainContent) {{
            // Nếu đã vượt qua intro (do refresh), hiển thị nội dung chính ngay
            mainContent.classList.add('show-after-animation');
        }}
    }}
    
    // Chạy các hàm
    setVhProperty();
    window.addEventListener('resize', setVhProperty);
    document.addEventListener('DOMContentLoaded', () => {{
        checkDeviceAndReload(); // Chạy kiểm tra thiết bị trước
        handleIntroTransition();
        setVhProperty();
    }});
</script>
"""
css_js_placeholder.markdown(css_js_code, unsafe_allow_html=True)


# --- RENDER VIDEO VÀ NỘI DUNG CHÍNH (Đồng thời) ---

# 1. RENDER VIDEO INTRO (z-index cao hơn, sẽ tự ẩn bằng JS)
# Quyết định có nên phát video không
should_play_video = is_mobile and video_data
intro_rendered = st.session_state.intro_rendered

if not intro_rendered:
    
    st.session_state.intro_rendered = True
    
    if should_play_video or video_fallback_data:
        
        media_tag = ""
        
        if should_play_video:
            media_source = f"data:video/mp4;base64,{video_data}"
            media_tag = f"""
            <video id="introMedia" class="intro-media" autoplay muted playsinline>
                <source src="{media_source}" type="video/mp4">
            </video>
            """
        elif video_fallback_data:
            media_source = f"data:image/jpeg;base64,{video_fallback_data}"
            media_tag = f"""
            <img id="introMedia" class="intro-media" src="{media_source}" alt="Background Intro Image">
            """
        
        st.markdown(f"""
        <div class="video-container" id="videoContainer">
            {media_tag}
            <div class="video-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        </div>
        """, unsafe_allow_html=True)


# 2. RENDER NỘI DUNG CHÍNH (z-index thấp hơn, sẽ từ từ hiện ra)
# Thêm một class 'show-after-animation' nếu là lần render lại, hoặc 'hide-on-start'
initial_main_class = 'hide-on-start'
if intro_rendered:
    initial_main_class = 'show-after-animation' # Hiển thị nếu đã render intro (hoặc là lần thứ 2)

st.markdown(f'<div id="mainContentContainer" class="{initial_main_class}">', unsafe_allow_html=True)

st.markdown('<div class="main-title">📜 TỔ BẢO DƯỠNG SỐ 1</div>', unsafe_allow_html=True)
st.write("Chào mừng bạn đến với website ✈️")


# 3. KHỐI PHÁT NHẠC TÙY CHỈNH (CUSTOM AUDIO PLAYER)
if current_audio_base64:

    js_code_player = f"""
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
                    // Bỏ qua lỗi Autoplay và chỉ phát nếu người dùng đã tương tác (hoặc browser cho phép)
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
                
                const progressBarElement = document.getElementById('progressBar');
                if (progressBarElement) {{
                    progressBarElement.addEventListener('click', window.seekAudio);
                }}
            }}
            
            updateTrackInfo();
            updateDuration(); 
        }}

        function formatTime(seconds) {{ /* Logic format time giữ nguyên */
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = Math.floor(seconds % 60);
            return `${{String(minutes).padStart(2, '0')}}:${{String(remainingSeconds).padStart(2, '0')}}`;
        }}
        
        function updateTrackInfo() {{ /* Logic update info giữ nguyên */
            const infoElement = document.getElementById('trackInfo');
            if(infoElement) {{
                 infoElement.textContent = 
                    `Track ${{currentTrackIndex + 1}}/${{TOTAL_TRACKS}}: ${{AUDIO_FILES_NAME[currentTrackIndex]}}`;
            }}
        }}
        
        window.updateDuration = function() {{ /* Logic update duration giữ nguyên */
            const durationTimeDisplay = document.getElementById('durationTime');
            if (audioPlayer && durationTimeDisplay) {{
                if (audioPlayer.duration && isFinite(audioPlayer.duration)) {{
                    durationTimeDisplay.textContent = formatTime(audioPlayer.duration);
                }} else {{
                    durationTimeDisplay.textContent = '--:--';
                }}
            }}
        }}
        
        window.updateProgress = function() {{ /* Logic update progress giữ nguyên */
            const progressFilled = document.getElementById('progressFilled');
            const currentTimeDisplay = document.getElementById('currentTime');
            if (audioPlayer && progressFilled && currentTimeDisplay && audioPlayer.duration) {{
                const percentage = (audioPlayer.currentTime / audioPlayer.duration) * 100;
                progressFilled.style.width = percentage + '%';
                currentTimeDisplay.textContent = formatTime(audioPlayer.currentTime);
            }}
        }}

        function loadTrack(shouldPlay) {{ /* Logic load track giữ nguyên */
            const newTrackBase64 = AUDIO_BASE64_LIST[currentTrackIndex];
            const newSrc = `data:audio/mp3;base64,${{newTrackBase64}}`;

            audioPlayer.src = newSrc;
            audioPlayer.load(); 

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

        window.switchTrack = function(direction) {{ /* Logic switch track giữ nguyên */
            const wasPlaying = !audioPlayer.paused;
            currentTrackIndex = (currentTrackIndex + direction + TOTAL_TRACKS) % TOTAL_TRACKS;
            loadTrack(wasPlaying); 
        }}

        window.togglePlayPause = function() {{ /* Logic toggle play/pause giữ nguyên */
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
        
        window.seekAudio = function(e) {{ /* Logic seek audio giữ nguyên */
            const progressBar = document.getElementById('progressBar');
            const rect = progressBar.getBoundingClientRect();
            const clickPosition = e.clientX - rect.left;
            const totalWidth = progressBar.offsetWidth;
            const clickRatio = clickPosition / totalWidth;
            
            if (audioPlayer.duration) {{
                audioPlayer.currentTime = audioPlayer.duration * clickRatio;
            }}
        }}

        // Khởi tạo player sau khi DOM tải xong
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
    {js_code_player}
    """, unsafe_allow_html=True)
    
st.markdown('</div>', unsafe_allow_html=True) # Kết thúc div mainContentContainer
