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
if "is_playing" not in st.session_state:
    st.session_state.is_playing = True # Mặc định là đang phát khi trang tải

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
current_track_index = st.session_state.current_track_index
current_audio_file = AUDIO_FILES[current_track_index]
audio_base64 = get_base64(current_audio_file)
current_track_name = current_audio_file
total_tracks = len(AUDIO_FILES)
is_playing_state = st.session_state.is_playing # Lấy trạng thái phát nhạc


# CSS động để kiểm soát hiển thị video
is_main_page = st.session_state.show_main
video_display_style = "display: none;" if is_main_page else "display: flex;" 


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

/* 6. CSS MỚI: CUSTOM AUDIO PLAYER */
.custom-audio-player {{
    position: fixed; 
    top: 10px; 
    left: 10px; 
    z-index: 9999;
    display: flex;
    flex-direction: column;
    width: 280px; /* Điều chỉnh kích thước để trông gọn hơn */
    background: rgba(0, 0, 0, 0.7);
    border-radius: 8px;
    padding: 10px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
}}
.player-info {{
    color: #FFF;
    font-size: 13px;
    text-align: center;
    margin-bottom: 8px;
}}
.player-controls {{
    display: flex;
    justify-content: space-around;
    align-items: center;
}}
.control-button {{
    background: none;
    border: none;
    color: #FFF;
    font-size: 20px;
    cursor: pointer;
    padding: 5px;
    transition: color 0.2s;
}}
.control-button:hover {{
    color: #4A90E2;
}}
.progress-bar {{
    height: 5px;
    background: #555;
    margin: 10px 0;
    border-radius: 2px;
    cursor: pointer;
}}
.progress-filled {{
    height: 100%;
    width: 0%; 
    background: #4A90E2;
    border-radius: 2px;
}}
.time-display {{
    display: flex;
    justify-content: space-between;
    color: #AAA;
    font-size: 11px;
}}

/* Khôi phục padding nhẹ cho nội dung trang chính */
.block-container {{ padding-top:2rem !important; padding-left:1rem !important; padding-right:1rem !important;}}
.main-title {{ /* Giữ nguyên CSS title */ }}
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

# === KHỐI PHÁT NHẠC TÙY CHỈNH (CUSTOM AUDIO PLAYER) ===
if audio_base64:
    track_number = current_track_index + 1

    js_code = f"""
    <script>
        const AUDIO_FILES = {AUDIO_FILES};
        let currentTrackIndex = {current_track_index};
        let isPlaying = {'true' if is_playing_state else 'false'};

        // Chức năng để định dạng thời gian (ví dụ: 00:00)
        function formatTime(seconds) {{
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = Math.floor(seconds % 60);
            return `${{String(minutes).padStart(2, '0')}}:${{String(remainingSeconds).padStart(2, '0')}}`;
        }}

        // Chức năng để cập nhật Session State (cho trạng thái Play/Pause)
        function updateStreamlitState(key, value) {{
            // Giả lập cập nhật Session State để Streamlit biết trạng thái
            // Đây là kỹ thuật hack không chính thức, nhưng hoạt động trong môi trường này
            if (window.parent.document.querySelector('iframe')) {{
                window.parent.document.querySelector('iframe').contentWindow.postMessage({{
                    isStreamlit: true,
                    type: 'setComponentValue',
                    componentName: 'custom_audio_player',
                    value: {{[key]: value}}
                }}, '*');
            }}
        }}

        // Chức năng tải và phát bài hát
        function loadTrack() {{
            const player = document.getElementById('customAudioPlayer');
            const newTrackName = AUDIO_FILES[currentTrackIndex];
            const newTrackBase64 = '{base64.b64encode(open(newTrackName, "rb").read()).decode("utf-8")}'
            const newSrc = `data:audio/mp3;base64,${{newTrackBase64}}`;

            player.src = newSrc;
            
            // Cập nhật thông tin bài hát
            document.getElementById('trackInfo').textContent = `Track ${{currentTrackIndex + 1}}/{total_tracks}: ${{newTrackName}}`;
            
            if (isPlaying) {{
                player.play();
                document.getElementById('playPauseButton').innerHTML = '⏸️';
            }} else {{
                document.getElementById('playPauseButton').innerHTML = '▶️';
            }}
        }}
        
        // Cần tải lại trang khi chuyển bài để Python/Streamlit biết bài hát mới
        function switchTrack(direction) {{
            currentTrackIndex = (currentTrackIndex + direction + {total_tracks}) % {total_tracks};
            
            // Kích hoạt Rerun để tải Base64 bài hát mới từ Python
            const url = new URL(window.location);
            url.searchParams.set('track_index', currentTrackIndex);
            
            // Lưu trạng thái Play/Pause trước khi Rerun
            updateStreamlitState('current_track_index', currentTrackIndex); 
            updateStreamlitState('is_playing', isPlaying);

            window.location.href = url.toString(); // Rerun Streamlit
        }}


        // Chức năng Play/Pause
        function togglePlayPause() {{
            const player = document.getElementById('customAudioPlayer');
            const button = document.getElementById('playPauseButton');

            if (player.paused) {{
                player.play();
                button.innerHTML = '⏸️';
                isPlaying = true;
            }} else {{
                player.pause();
                button.innerHTML = '▶️';
                isPlaying = false;
            }}
            updateStreamlitState('is_playing', isPlaying); // Lưu trạng thái
        }}

        // Đồng bộ thanh tiến trình và thời gian
        document.addEventListener('DOMContentLoaded', () => {{
            const player = document.getElementById('customAudioPlayer');
            const progressBar = document.getElementById('progressBar');
            const progressFilled = document.getElementById('progressFilled');
            const currentTimeDisplay = document.getElementById('currentTime');
            const durationTimeDisplay = document.getElementById('durationTime');

            // Set trạng thái ban đầu
            if (isPlaying) {{ player.play(); }} else {{ player.pause(); }}

            // Sự kiện cập nhật thời gian
            player.addEventListener('timeupdate', () => {{
                if (player.duration) {{
                    const percentage = (player.currentTime / player.duration) * 100;
                    progressFilled.style.width = percentage + '%';
                    currentTimeDisplay.textContent = formatTime(player.currentTime);
                }}
            }});
            
            // Sự kiện khi metadata được tải
            player.addEventListener('loadedmetadata', () => {{
                durationTimeDisplay.textContent = formatTime(player.duration);
            }});

            // Sự kiện khi bài hát kết thúc (Tự động chuyển bài)
            player.addEventListener('ended', () => {{
                switchTrack(1);
            }});

            // Xử lý click thanh tiến trình
            progressBar.addEventListener('click', (e) => {{
                const clickPosition = e.offsetX;
                const totalWidth = progressBar.offsetWidth;
                const clickRatio = clickPosition / totalWidth;
                
                if (player.duration) {{
                    player.currentTime = player.duration * clickRatio;
                }}
            }});
            
            // Fix cho vấn đề Autoplay (Chromium)
            player.play().catch(error => {{
                // Autoplay bị chặn, hiển thị nút Play
                document.getElementById('playPauseButton').innerHTML = '▶️';
                isPlaying = false;
                player.pause();
            }});
        }});
    </script>
    """
    
    # Đặt nội dung HTML/JS vào placeholder
    st.markdown(f"""
    <div style="display: none;">
        <audio id="customAudioPlayer" src="data:audio/mp3;base64,{audio_base64}" loop></audio>
    </div>
    <div class="custom-audio-player">
        <div class="player-info" id="trackInfo">Track {track_number}/{total_tracks}: {current_track_name}</div>
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
