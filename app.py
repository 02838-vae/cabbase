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
    st.error("❌ Thiếu một hoặc nhiều file âm thanh. Vui lòng kiểm tra lại.")
    st.stop()
        
# Biến Python để truyền vào JavaScript
current_track_index = st.session_state.current_track_index
current_audio_base64 = AUDIO_BASE64_LIST[current_track_index]
current_track_name = AUDIO_FILES[current_track_index]
total_tracks = len(AUDIO_FILES)
is_playing_state = st.session_state.is_playing 
audio_base64_json = json.dumps(AUDIO_BASE64_LIST) # Dùng json.dumps để đảm bảo định dạng JS chính xác
# ===================================================

# --- LOGIC CHUYỂN CẢNH (Dùng session state để tránh render video liên tục) ---
if not st.session_state.show_main:
    # --- GIAO DIỆN CHUYỂN CẢNH (VIDEO INTRO) ---
    video_data = get_base64(video_file)
    if video_data is None:
        st.error(f"❌ Không tìm thấy file {video_file}.")
        st.stop()
    
    # CSS cho video intro
    st.markdown(f"""
    <style>
    /* 1. KHẮC PHỤC VIEWPORT TRÊN MOBILE và FULL HEIGHT cho PC */
    html, body {{ 
        margin:0; padding:0; height:100%; overflow:hidden; background:black; height: 100%; 
    }}
    header[data-testid="stHeader"], footer {{ display: none !important; }}
    .stApp, section.main {{
        height: calc(var(--vh, 1vh) * 100) !important; min-height: calc(var(--vh, 1vh) * 100) !important;
    }}
    .block-container, section.main > div {{
        margin: 0 !important; padding: 0 !important; max-width: 100% !important;
        width: 100vw !important; height: calc(var(--vh, 1vh) * 100) !important;
    }}

    /* 2. CSS CHO VIDEO CONTAINER (FIX FLICKER VỚI ANIMATION FORWARDS) */
    .video-container {{
        position: fixed; inset:0; 
        width:100vw; height:calc(var(--vh, 1vh) * 100);
        justify-content:center; align-items:center; background:black; 
        z-index: 99999;
        display: flex; /* BẮT BUỘC DISPLAY: FLEX */
        flex-direction: column; 
        animation: fadeOut {FADE_DURATION_SECONDS}s ease-out {VIDEO_DURATION_SECONDS}s forwards;
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
        99% {{opacity:0.01;}} /* Giữ opacity > 0 một chút để browser không hide ngay */
        100%{{opacity:0; visibility:hidden; z-index:-1;}} 
    }}
    @keyframes appear {{ 0% {{opacity:0; filter:blur(8px); transform:translateY(40px);}} 100%{{opacity:1; filter:blur(0); transform:translateY(0);}} }}
    @keyframes floatFade {{ 0% {{opacity:1; filter:blur(0); transform:translateY(0);}} 100%{{opacity:0; filter:blur(12px); transform:translateY(-30px) scale(1.05);}} }}
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
        
        // 💥 QUAN TRỌNG: JS để tự động chuyển trạng thái sau khi hết video + fade
        const totalDuration = {VIDEO_DURATION_SECONDS} + {FADE_DURATION_SECONDS};
        setTimeout(() => {{
            const url = new URL(window.location.href);
            url.searchParams.set('show_main', 'true');
            // Dùng window.location.replace để không bị lưu state cũ vào history
            window.location.replace(url); 
        }}, totalDuration * 1000 + 100); // Thêm 100ms buffer
    </script>
    """, unsafe_allow_html=True)
    
    # 💥 QUAN TRỌNG: Chỉ render video container
    st.markdown(f"""
    <div class="video-container" id="videoContainer">
        <video id="introVideo" class="video-bg" autoplay muted playsinline>
            <source src="data:video/mp4;base64,{video_data}" type="video/mp4">
        </video>
        <div class="video-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Kiểm tra URL parameter để chuyển trạng thái nếu JS hoạt động
    if st.query_params.get("show_main") == "true":
        st.session_state.show_main = True
        del st.query_params["show_main"]
        st.rerun()

    st.stop()


# --- TRANG CHÍNH ---

# Thiết lập lại CSS cho trang chính
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

/* 2. CSS CHO VIDEO CONTAINER - ẨN HOÀN TOÀN KHI VÀO TRANG CHÍNH */
.video-container {{
    display: none !important;
}}

/* 3. CSS CHO TRANG CHÍNH: BACKGROUND FIX */
.stApp {{
    z-index:1; 
    background-color: #333; 
    background-image: linear-gradient(rgba(245,242,200,0.4), rgba(245,242,200,0.4)),
                      url("data:image/jpeg;base64,{img_base64}");
    background-attachment: fixed; background-size: cover; background-repeat: no-repeat; background-position: center center; 
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
    width: 300px; /* 💥 FIX: THU NHỎ CHO MOBILE */
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


# --- NỘI DUNG TRANG CHÍNH ---

st.markdown('<div class="main-title">📜 TỔ BẢO DƯỠNG SỐ 1</div>', unsafe_allow_html=True)
st.write("Chào mừng bạn đến với website ✈️")

# === KHỐI PHÁT NHẠC TÙY CHỈNH (CUSTOM AUDIO PLAYER) ===
if current_audio_base64:

    js_code = f"""
    <script>
        const AUDIO_BASE64_LIST = {audio_base64_json};
        const AUDIO_FILES_NAME = {AUDIO_FILES};
        const TOTAL_TRACKS = {total_tracks};
        let currentTrackIndex = {current_track_index};
        let isPlaying = {'true' if is_playing_state else 'false'};

        function formatTime(seconds) {{
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = Math.floor(seconds % 60);
            return `${{String(minutes).padStart(2, '0')}}:${{String(remainingSeconds).padStart(2, '0')}}`;
        }}
        
        function updateTrackInfo() {{
            document.getElementById('trackInfo').textContent = 
                `Track ${{currentTrackIndex + 1}}/${{TOTAL_TRACKS}}: ${{AUDIO_FILES_NAME[currentTrackIndex]}}`;
        }}

        // Chức năng tải và phát bài hát
        function loadTrack(shouldPlay = true) {{ 
            const player = document.getElementById('customAudioPlayer');
            const newTrackBase64 = AUDIO_BASE64_LIST[currentTrackIndex];
            const newSrc = `data:audio/mp3;base64,${{newTrackBase64}}`;

            player.src = newSrc;
            player.load(); // 💥 FIX LỖI CHUYỂN BÀI: Buộc tải lại nguồn Base64 mới

            updateTrackInfo();
            
            if (shouldPlay) {{
                // Chỉ gọi play() nếu player đã được tải 
                player.play().catch(error => {{
                    // Xử lý lỗi Autoplay bị chặn
                    document.getElementById('playPauseButton').innerHTML = '▶️';
                    isPlaying = false;
                    player.pause();
                }});
                document.getElementById('playPauseButton').innerHTML = '⏸️';
                isPlaying = true;
            }} else {{
                player.pause();
                document.getElementById('playPauseButton').innerHTML = '▶️';
                isPlaying = false;
            }}
        }}

        // Chức năng chuyển bài 
        function switchTrack(direction) {{
            const player = document.getElementById('customAudioPlayer');
            const wasPlaying = !player.paused; // Capture current state
            
            currentTrackIndex = (currentTrackIndex + direction + TOTAL_TRACKS) % TOTAL_TRACKS;
            loadTrack(wasPlaying); 
        }}

        // Chức năng Play/Pause
        function togglePlayPause() {{
            const player = document.getElementById('customAudioPlayer');
            const button = document.getElementById('playPauseButton');

            if (player.paused) {{
                player.play().catch(error => {{
                    document.getElementById('playPauseButton').innerHTML = '▶️';
                    isPlaying = false;
                    player.pause();
                }});
                button.innerHTML = '⏸️';
                isPlaying = true;
            }} else {{
                player.pause();
                button.innerHTML = '▶️';
                isPlaying = false;
            }}
        }}

        // Gắn các hàm JS vào window để có thể gọi từ HTML (Quan trọng cho Streamlit)
        window.switchTrack = switchTrack;
        window.togglePlayPause = togglePlayPause;

        // Đồng bộ thanh tiến trình và thời gian
        document.addEventListener('DOMContentLoaded', () => {{
            const player = document.getElementById('customAudioPlayer');
            const progressBar = document.getElementById('progressBar');
            const progressFilled = document.getElementById('progressFilled');
            const currentTimeDisplay = document.getElementById('currentTime');
            const durationTimeDisplay = document.getElementById('durationTime');

            // 1. Tải bài hát ban đầu
            loadTrack({is_playing_state}); 
            
            // 2. Sự kiện cập nhật thời gian
            player.addEventListener('timeupdate', () => {{
                if (player.duration) {{
                    const percentage = (player.currentTime / player.duration) * 100;
                    progressFilled.style.width = percentage + '%';
                    currentTimeDisplay.textContent = formatTime(player.currentTime);
                }}
            }});
            
            // 3. Sự kiện khi metadata được tải
            player.addEventListener('loadedmetadata', () => {{
                durationTimeDisplay.textContent = formatTime(player.duration);
            }});

            // 4. Sự kiện khi bài hát kết thúc (Tự động chuyển bài)
            player.addEventListener('ended', () => {{
                switchTrack(1);
            }});

            // 5. Xử lý click thanh tiến trình
            progressBar.addEventListener('click', (e) => {{
                const rect = progressBar.getBoundingClientRect();
                const clickPosition = e.clientX - rect.left;
                const totalWidth = progressBar.offsetWidth;
                const clickRatio = clickPosition / totalWidth;
                
                if (player.duration) {{
                    player.currentTime = player.duration * clickRatio;
                }}
            }});
        }});
    </script>
    """
    
    # Ẩn thẻ audio gốc đi, nó chỉ dùng để chạy nhạc. 
    # 💥 FIX LỖI KHÔNG PHÁT NHẠC: Đảm bảo src có Base64 ban đầu
    st.markdown(f"""
    <div style="display: none;">
        <audio id="customAudioPlayer" src="data:audio/mp3;base64,{current_audio_base64}"></audio>
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
# =================================================================================
