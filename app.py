import streamlit as st
import base64
import os
import time
import random

# --- CẤU HÌNH BAN ĐẦU ---
st.set_page_config(
    page_title="Tổ Bảo Dưỡng Số 1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Khởi tạo session state
if 'video_ended' not in st.session_state:
    st.session_state.video_ended = False

# --- CÁC HÀM TIỆN ÍCH ---

def get_base64_encoded_file(file_path):
    """Đọc file và trả về Base64 encoded string."""
    path_to_check = os.path.join(os.path.dirname(__file__), file_path)
    if not os.path.exists(path_to_check) or os.path.getsize(path_to_check) == 0:
        return None
    try:
        with open(path_to_check, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    except Exception as e:
        st.error(f"Lỗi khi đọc file {file_path}: {str(e)}")
        return None


# ✅ Mã hóa các file media chính
pc_video_file = "airplane.mp4"
mobile_video_file = "mobile.mp4"
# ✅ Danh sách nhạc (ở thư mục gốc)
music_files = [f"background{i}.mp3" for i in range(1, 7)] 
music_base64_dict = {} # ✅ Từ điển chứa tất cả nhạc base64

try:
    # Load 2 video cho PC và Mobile
    pc_video_base64 = get_base64_encoded_file(pc_video_file)
    mobile_video_base64 = get_base64_encoded_file(mobile_video_file)
    bg_img_base64 = get_base64_encoded_file("bg_main.jpg")

    # ✅ Load TẤT CẢ các file nhạc
    for file in music_files:
        encoded_data = get_base64_encoded_file(file)
        if encoded_data:
            music_base64_dict[file] = encoded_data
    
    # Chuyển từ điển Python sang chuỗi JSON cho Javascript
    import json
    music_base64_json = json.dumps(music_base64_dict)

except Exception as e:
    st.error(f"Lỗi mã hóa file media: {e}")
    pc_video_base64 = None
    mobile_video_base64 = None
    bg_img_base64 = None
    music_base64_json = "{}" # Set là rỗng nếu lỗi


# ✅ BỔ SUNG LỚP BẢO VỆ NẾU THIẾU MEDIA QUAN TRỌNG
if not bg_img_base64 or (not pc_video_base64 and not mobile_video_base64):
    st.session_state.video_ended = True 
    st.warning("⚠️ **Thiếu file media quan trọng (bg_main.jpg, airplane.mp4, hoặc mobile.mp4)**. Đã bỏ qua Video Intro.")


# --- CSS CHÍNH CHO TOÀN BỘ ỨNG DỤNG ---
def set_page_style(css):
    """Áp dụng CSS style cho toàn bộ trang."""
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

css = f"""
/* 1. Reset và Font */
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@100;300;400;700&display=swap');
* {{
    font-family: 'Roboto', sans-serif;
    transition: background-color 0.5s, color 0.5s, opacity 0.5s, transform 0.5s;
}}

/* 2. Ẩn các thành phần mặc định của Streamlit */
#MainMenu, footer {{visibility: hidden;}}

/* 3. Background chính */
.stApp {{
    background: url("data:image/jpeg;base64,{bg_img_base64}") no-repeat center center fixed !important;
    background-size: cover !important;
    min-height: 100vh; 
    position: relative;
}}

/* 4. Che nội dung chính cho đến khi video kết thúc (trạng thái mặc định) */
.stApp.video-not-finished {{
    overflow: hidden;
}}

/* 5. Ẩn tiêu đề và nội dung chính khi video đang chạy */
.stApp.video-not-finished .main, 
.stApp.video-not-finished #main-title-container,
.stApp.video-not-finished #music-player-container,
.stApp.video-not-finished .nav-container
{{
    opacity: 0 !important;
    visibility: hidden !important;
    pointer-events: none !important;
    transform: translateY(20px);
}}

/* 6. Hiển thị nội dung chính sau khi video kết thúc và hiệu ứng reveal xong */
.stApp.main-content-revealed .main,
.stApp.main-content-revealed #main-title-container,
.stApp.main-content-revealed #music-player-container,
.stApp.main-content-revealed .nav-container
{{
    opacity: 1 !important;
    visibility: visible !important;
    pointer-events: auto !important;
    transform: translateY(0);
}}

/* 7. Hiệu ứng Grid Reveal */
.reveal-grid {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: grid;
    grid-template-columns: repeat(10, 1fr); 
    grid-template-rows: repeat(10, 1fr); 
    z-index: 999; 
    pointer-events: none; 
}}

.reveal-cell {{
    background-color: #000; 
    opacity: 1;
    transition: opacity 1s ease-out; 
}}

/* 8. Container Video */
#video-iframe-container {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 998; 
    background: black; 
}}

/* 9. Video iframe (tùy chỉnh cho Streamlit component) */
iframe[title="video_callback_intro"] {{
    width: 100% !important;
    height: 100% !important;
    border: none;
    opacity: 1;
    transition: opacity 0.5s, visibility 0s;
}}

/* 10. Tiêu đề Chính (Running Title) */
#main-title-container {{
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 100;
    background: rgba(0, 0, 0, 0.7);
    padding: 10px 25px;
    border-radius: 50px;
    box-shadow: 0 0 15px rgba(0, 255, 0, 0.5);
}}
#main-title-container h1 {{
    font-size: 2.5rem;
    color: #00FF00;
    margin: 0;
    text-shadow: 0 0 5px #00FF00;
}}

/* 11. Music Player */
#music-player-container {{
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 100;
    background: rgba(0, 0, 0, 0.8);
    padding: 10px 20px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    box-shadow: 0 0 15px rgba(0, 255, 0, 0.5);
}}
.controls .control-btn {{
    background: #111;
    border: 1px solid #00FF00;
    color: #00FF00;
    padding: 5px 10px;
    margin: 0 5px;
    cursor: pointer;
    border-radius: 5px;
}}
.progress-container {{
    width: 150px;
    height: 5px;
    background: #333;
    margin: 0 10px;
    border-radius: 2.5px;
    cursor: pointer;
}}
.progress-bar {{
    height: 100%;
    width: 0%;
    background: #00FF00;
    border-radius: 2.5px;
}}
.time-info span {{
    color: #00FF00;
    font-size: 0.8rem;
    margin: 0 2px;
}}

/* 12. Navigation Button (UIverse Style) */
.nav-container {{
    position: fixed;
    top: 100px;
    right: 20px;
    z-index: 100;
}}
.button {{
    --color: #00FF00;
    --hover: #222;
    --hover-text: #00FF00;
    --size: 100px; 
    -webkit-tap-highlight-color: transparent;
    cursor: pointer;
    background: #000;
    border: 3px solid var(--color);
    width: var(--size);
    height: var(--size);
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    position: relative;
    border-radius: 30%;
}}
.button span {{
    font-size: 1.1em;
    font-weight: 700;
    color: var(--color);
    z-index: 1;
    position: relative;
}}
.dots_container {{
    opacity: 0;
    filter: url(#goo);
    position: absolute;
    width: 100%;
    height: 100%;
}}
.dot {{
    position: absolute;
    width: 12px;
    height: 12px;
    background: var(--color);
    border-radius: 50%;
    top: 0;
    left: 0;
    transform: translate(-50%, -50%);
    transition: transform 0.3s ease-in-out, background 0.3s ease-in-out;
}}
.button:hover .dots_container {{
    opacity: 1;
}}
.button:hover span {{
    color: var(--hover-text);
    transform: scale(0.9);
}}
.button:hover {{
    background: var(--hover);
}}
.button:hover .dot:nth-child(1) {{ transform: translate(150%, 150%); }}
.button:hover .dot:nth-child(2) {{ transform: translate(500%, 150%); }}
.button:hover .dot:nth-child(3) {{ transform: translate(500%, 500%); }}
.button:hover .dot:nth-child(4) {{ transform: translate(150%, 500%); }}
"""
set_page_style(css)

# Thêm class để ẩn nội dung chính ban đầu
st.markdown('<div class="reveal-grid"></div>', unsafe_allow_html=True)
st.markdown('<div id="video-iframe-container"></div>', unsafe_allow_html=True)
st.markdown('<div id="music-audio-container" style="display: none;"></div>', unsafe_allow_html=True) 

# --- LOGIC XỬ LÝ VIDEO VÀ HIỆU ỨNG TRONG IFRAME (JAVASCRIPT) ---
js_callback_video = f"""
<script>
    // --- KHAI BÁO CÁC HÀM CƠ BẢN ---
    const stApp = window.parent.document.querySelector('.stApp');
    const audioContainer = window.parent.document.querySelector('#music-audio-container');
    
    // ✅ Biến Javascript chứa TẤT CẢ các file nhạc Base64
    const pcVideoBase64 = "{pc_video_base64}";
    const mobileVideoBase64 = "{mobile_video_base64}";
    const musicData = {music_base64_json}; // ✅ Đã sửa: Load toàn bộ JSON
    const musicFiles = Object.keys(musicData);

    let audio = null;
    let isPlaying = false;
    let musicPlayerInitialized = false;
    let currentTrackIndex = 0; // ✅ Theo dõi bài hát hiện tại
    
    function isMobile() {{
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth < 768;
    }}
    
    function formatTime(seconds) {{
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${{minutes}}:${{remainingSeconds < 10 ? '0' : ''}}${{remainingSeconds}}`;
    }}

    function updateMusicDisplay(duration) {{
        const durationSpan = window.parent.document.querySelector('#duration');
        if (durationSpan) {{
            durationSpan.textContent = formatTime(duration);
        }}
    }}

    function loadTrack(index) {{
        if (musicFiles.length === 0) return;

        currentTrackIndex = (index % musicFiles.length + musicFiles.length) % musicFiles.length;
        const fileName = musicFiles[currentTrackIndex];
        const base64Data = musicData[fileName];
        const newSrc = 'data:audio/mp3;base64,' + base64Data;

        // Xóa player cũ nếu có
        if (audio) {{
            audio.pause();
            audio.remove();
        }}
        
        // Tạo player mới
        audio = new Audio(newSrc);
        audio.loop = false; // Tắt loop
        audioContainer.appendChild(audio);
        console.log(`Loaded track: ${{fileName}}`);

        // Cập nhật thông tin bài hát và tự động chuyển bài khi kết thúc
        audio.onloadedmetadata = () => {{
            updateMusicDisplay(audio.duration);
        }};
        
        audio.onended = () => {{
            console.log("Track ended. Playing next track.");
            playNext();
        }};
        
        if (isPlaying) {{
            audio.play().catch(e => console.error("Error playing audio:", e));
        }}
    }}
    
    function playNext() {{
        loadTrack(currentTrackIndex + 1);
        if (isPlaying) {{
            // Đợi 100ms để đảm bảo metadata được load trước khi play
            setTimeout(() => {{
                audio.play().catch(e => console.error("Error playing next track:", e));
            }}, 100);
        }}
    }}
    
    function playPrev() {{
        loadTrack(currentTrackIndex - 1);
        if (isPlaying) {{
             setTimeout(() => {{
                audio.play().catch(e => console.error("Error playing previous track:", e));
            }}, 100);
        }}
    }}

    function initMusicPlayer() {{
        if (musicPlayerInitialized || musicFiles.length === 0) return;
        musicPlayerInitialized = true;
        
        // Bắt đầu từ một bài ngẫu nhiên
        currentTrackIndex = Math.floor(Math.random() * musicFiles.length);
        loadTrack(currentTrackIndex);
        
        const playPauseBtn = window.parent.document.querySelector('#play-pause-btn');
        const prevBtn = window.parent.document.querySelector('#prev-btn');
        const nextBtn = window.parent.document.querySelector('#next-btn');

        if(playPauseBtn) {{
            playPauseBtn.onclick = () => {{
                if (isPlaying) {{
                    audio.pause();
                    playPauseBtn.textContent = '▶';
                }} else {{
                    audio.play().catch(e => console.error("Error playing audio:", e));
                    playPauseBtn.textContent = '⏸';
                }}
                isPlaying = !isPlaying;
            }};
        }}
        
        // ✅ Xử lý nút Previous/Next
        if(nextBtn) {{
            nextBtn.onclick = playNext;
        }}
        if(prevBtn) {{
            prevBtn.onclick = playPrev;
        }}

        // Tự động phát sau 100ms
        setTimeout(() => {{
            if (stApp.classList.contains('main-content-revealed')) {{
                playPauseBtn.click(); // Kích hoạt phát nhạc
            }}
        }}, 100);
        console.log("Music Player Initialized.");
    }}

    function initRevealEffect() {{
        const revealGrid = window.parent.document.querySelector('.reveal-grid');
        if (!revealGrid) return;

        const cells = Array.from(revealGrid.querySelectorAll('.reveal-cell'));
        
        cells.forEach((cell, index) => {{
            setTimeout(() => {{
                cell.style.opacity = '0';
            }}, index * 10); 
        }});

        setTimeout(() => {{
            revealGrid.remove();
        }}, 1000); 
    }}

    function sendBackToStreamlit() {{
        console.log("Video ended or skipped, revealing main content");
        
        if (stApp) {{
            stApp.classList.add('video-finished', 'main-content-revealed');
            stApp.classList.remove('video-not-finished'); 
        }}
        
        initRevealEffect();
        
        setTimeout(initMusicPlayer, 100); 
    }}
    
    // --- LOGIC SKIP INTRO VÀ REVEAL ---
    const urlParams = new URLSearchParams(window.parent.location.search);
    const skipIntro = urlParams.get('skip_intro');
    
    if (skipIntro === '1') {{
        console.log("Skip intro detected. Directly revealing main content and skipping reveal effect.");
        
        if (stApp) {{
            stApp.classList.add('video-finished', 'main-content-revealed');
            stApp.classList.remove('video-not-finished');
        }}

        const revealGrid = window.parent.document.querySelector('.reveal-grid');
        if (revealGrid) {{
            revealGrid.remove();
        }}
        
        initMusicPlayer();

        const iframe = window.frameElement;
        if (iframe) {{
            iframe.style.opacity = 0;
            iframe.style.visibility = 'hidden';
            iframe.style.pointerEvents = 'none';
        }}
        
        return; 
    }}

    // --- LOGIC VIDEO BÌNH THƯỜNG (CHỌN NGUỒN) ---
    const iframe = window.frameElement;
    
    let videoSourceBase64;
    let deviceType = isMobile() ? 'Mobile' : 'PC';

    if (isMobile() && mobileVideoBase64) {{
        videoSourceBase64 = mobileVideoBase64;
    }} else if (!isMobile() && pcVideoBase64) {{
        videoSourceBase64 = pcVideoBase64;
    }}
    
    if (!videoSourceBase64) {{
        console.log(`Fallback: ${{deviceType}} video not found. Trying other video source.`);
        videoSourceBase64 = isMobile() ? pcVideoBase64 : mobileVideoBase64;
    }}
    
    if (videoSourceBase64) {{
        console.log(`Playing video for: ${{deviceType}}`);
        // Tạo video element
        const video = document.createElement('video');
        video.src = 'data:video/mp4;base64,' + videoSourceBase64;
        video.autoplay = true;
        video.muted = true; 
        video.playsInline = true;
        video.style.width = '100%';
        video.style.height = '100%';
        video.style.objectFit = 'cover';
        video.style.opacity = 1;
        video.style.transition = 'opacity 1s';
        
        document.body.appendChild(video);
        document.body.style.margin = '0';
        document.body.style.overflow = 'hidden';

        video.onended = () => {{
            console.log("Video Ended.");
            
            if (iframe) {{
                iframe.style.opacity = 0;
                setTimeout(() => {{
                    iframe.style.visibility = 'hidden';
                    iframe.style.pointerEvents = 'none';
                }}, 500); 
            }}

            sendBackToStreamlit();
        }};
        
        video.play().catch(e => {{
            console.error("Auto-play failed:", e);
            sendBackToStreamlit(); 
        }});
        
    }} else {{
        console.log("No Video Base64 found for any device, skipping video and revealing content.");
        setTimeout(sendBackToStreamlit, 500); 
    }}
    
    // Khởi tạo các ô lưới reveal
    const revealGrid = window.parent.document.querySelector('.reveal-grid');
    if (revealGrid) {{
        for (let i = 0; i < 100; i++) {{ 
            const cell = document.createElement('div');
            cell.classList.add('reveal-cell');
            revealGrid.appendChild(cell);
        }}
    }}
</script>
"""

# Thêm logic để kiểm tra nếu đã video đã chạy xong
if st.session_state.video_ended:
    st.markdown(f'<script>window.onload = function() {{ if(window.parent.document.querySelector(".stApp")) {{ window.parent.document.querySelector(".stApp").classList.add("video-finished", "main-content-revealed"); }} if(window.parent.document.querySelector(".reveal-grid")) {{ window.parent.document.querySelector(".reveal-grid").remove(); }} }};</script>', unsafe_allow_html=True)
else:
    # Nếu chưa chạy xong, nhúng iframe video và logic
    import streamlit.components.v1 as components
    components.html(
        js_callback_video,
        height=0, 
        width=0,
        scrolling=False,
        key="video_callback_intro"
    )
    st.session_state.video_ended = True 

# --- TIÊU ĐỀ CHÍNH ---
main_title_text = "TỔ BẢO DƯỠNG SỐ 1"

# Nhúng tiêu đề
st.markdown(f"""
<div id="main-title-container">
    <h1>{main_title_text}</h1>
</div>
""", unsafe_allow_html=True)

# --- MUSIC PLAYER ---
if len(music_base64_dict) > 0: # Chỉ hiển thị nếu có nhạc
    st.markdown("""
<div id="music-player-container">
    <div class="controls">
        <button class="control-btn" id="prev-btn">⏮</button>
        <button class="control-btn play-pause" id="play-pause-btn">▶</button>
        <button class="control-btn" id="next-btn">⏭</button>
    </div>
    <div class="progress-container" id="progress-container">
        <div class="progress-bar" id="progress-bar"></div>
    </div>
    <div class="time-info">
        <span id="current-time">0:00</span>
        <span id="duration">0:00</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- NAVIGATION BUTTON MỚI (UIverse Style) ---
st.markdown("""
<div class="nav-container">
    <a href="/partnumber" target="_self" class="button">
        <div class="dots_container">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
        <span>TRA CỨU PN</span>
    </a>
</div>
""", unsafe_allow_html=True)

# --- NỘI DUNG CHÍNH ---
st.markdown("""
<div class="main-content-area" style="padding-top: 150px; padding-bottom: 50px;">
    <h2 style="color: white; text-align: center; margin-bottom: 50px;">Chào mừng đến với Hệ Thống Tra Cứu Nội Bộ</h2>
    <div style="max-width: 800px; margin: auto; padding: 20px; background: rgba(0, 0, 0, 0.7); border-radius: 10px; border: 1px solid #00FF00;">
        <p style="color: #00FF00; line-height: 1.8;">
        Hệ thống này được xây dựng để cung cấp thông tin tra cứu Part Number nhanh chóng và chính xác cho đội ngũ kỹ thuật.
        Vui lòng sử dụng các chức năng ở menu bên phải để truy cập các công cụ hỗ trợ.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
