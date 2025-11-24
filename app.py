import streamlit as st
import base64
import os
import re 
import time

# --- CẤU HÌNH BAN ĐẦU ---
st.set_page_config(
    page_title="Tổ Bảo Dưỡng Số 1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Khởi tạo session state
if 'video_ended' not in st.session_state:
    st.session_state.video_ended = False
if 'first_load' not in st.session_state:
    st.session_state.first_load = True

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
        return None


# Mã hóa các file media chính (bắt buộc)
try:
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
    logo_base64 = get_base64_encoded_file("logo.jpg")

    missing_files = []
    if not video_pc_base64: missing_files.append("airplane.mp4")
    if not video_mobile_base64: missing_files.append("mobile.mp4")
    if not audio_base64: missing_files.append("plane_fly.mp3")
    if not bg_pc_base64: missing_files.append("cabbase.jpg")
    if not bg_mobile_base64: missing_files.append("mobile.jpg")

    if missing_files:
        st.error(f"⚠️ Thiếu các file media cần thiết hoặc file rỗng. Vui lòng kiểm tra lại các file sau trong thư mục:")
        st.write(" - " + "\n - ".join(missing_files))
        st.stop()
        
except Exception as e:
    st.error(f"❌ Lỗi khi đọc file: {str(e)}")
    st.stop()

if not 'logo_base64' in locals() or not logo_base64:
    logo_base64 = "" 

# --- CẤU HÌNH NHẠC NỀN ---
BASE_MUSIC_URL = "https://raw.githubusercontent.com/02838-vae/cabbase/main/"
music_files = [f"{BASE_MUSIC_URL}background{i}.mp3" for i in range(1, 7)]


# --- PHẦN 1: NHÚNG FONT VÀ CSS CHÍNH ---
font_links = """
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
"""
st.markdown(font_links, unsafe_allow_html=True)

# --- PHẦN 2: CSS CHÍNH (STREAMLIT APP) ---
hide_streamlit_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sacramento&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');

/* Ẩn các thành phần mặc định của Streamlit */
#MainMenu, footer, header {{visibility: hidden;}}

.main {{
    padding: 0;
    margin: 0;
}}

div.block-container {{
    padding: 0;
    margin: 0;
    max-width: 100% !important;
}}

/* Chặn hành vi dblclick và chọn văn bản trên toàn bộ ứng dụng khi video đang chạy */
.stApp.video-running * {{
    user-select: none;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    cursor: default !important; 
}}

/* Iframe Video Intro */
iframe:first-of-type {{
    transition: opacity 1s ease-out, visibility 1s ease-out;
    opacity: 1;
    visibility: visible;
    width: 100vw !important;
    height: 100vh !important;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1000;
    pointer-events: all;
}}

.video-finished iframe:first-of-type {{
    opacity: 0;
    visibility: hidden;
    pointer-events: none; 
    height: 1px !important;
    width: 1px !important;
}}

.stApp {{
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
    --logo-bg-url: url('data:image/jpeg;base64,{logo_base64}');
}}

.reveal-grid {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    display: grid;
    grid-template-columns: repeat(20, 1fr);
    grid-template-rows: repeat(12, 1fr);
    z-index: 500;
    pointer-events: none;
}}

.grid-cell {{
    background-color: white;
    opacity: 1;
    transition: opacity 0.5s ease-out;
}}

.main-content-revealed {{
    background-image: var(--main-bg-url-pc);
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    filter: sepia(60%) grayscale(20%) brightness(85%) contrast(110%);
    transition: filter 2s ease-out;
}}

@media (max-width: 768px) {{
    .main-content-revealed {{
        background-image: var(--main-bg-url-mobile);
    }}
    .reveal-grid {{
        grid-template-columns: repeat(10, 1fr);
        grid-template-rows: repeat(20, 1fr);
    }}
}}

/* Keyframes cho hiệu ứng chữ chạy đơn */
@keyframes scrollText {{
    0% {{ transform: translate(100vw, 0); }}
    100% {{ transform: translate(-100%, 0); }}
}}

/* Keyframes cho hiệu ứng Đổi Màu Gradient */
@keyframes colorShift {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

/* Keyframes xoay (bắt buộc phải có) */
@keyframes rotate {{
    to {{ transform: translate(-50%, -50%) rotate(360deg); }}
}}

/* === TIÊU ĐỀ TRANG CHÍNH === */
#main-title-container {{
    position: fixed;
    top: 5vh;
    left: 0;
    width: 100%;
    height: 10vh;
    overflow: hidden;
    z-index: 20;
    pointer-events: none;
    opacity: 0;
    transition: opacity 2s;
}}

.video-finished #main-title-container {{
    opacity: 1;
}}

#main-title-container h1 {{
    font-family: 'Playfair Display', serif;
    font-size: 3.5vw;
    margin: 0;
    font-weight: 900;
    font-feature-settings: "lnum" 1;
    letter-spacing: 5px;
    white-space: nowrap;
    display: inline-block;
    animation: scrollText 15s linear infinite;
    background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
    background-size: 400% 400%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    color: transparent;
    animation: colorShift 10s ease infinite, scrollText 15s linear infinite;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}}

@media (max-width: 768px) {{
    #main-title-container {{
        height: 8vh;
        width: 100%;
        left: 0;
    }}
    
    #main-title-container h1 {{
        /* SỬ DỤNG VMIN cho chế độ dọc mobile */
        font-size: 7.0vmin; 
        animation-duration: 8s;
    }}
}}

/* === ĐIỀU CHỈNH CHO MOBILE LANDSCAPE (MÀN HÌNH NGANG) - ĐÃ CHUYỂN SANG VMIN === */
@media (max-width: 900px) and (orientation: landscape) and (max-height: 500px) {{
    #main-title-container {{
        top: 2vh !important; 
        height: 12vh !important; 
    }}
    
    #main-title-container h1 {{
        /* SỬ DỤNG VMIN THAY CHO VW */
        font-size: 3.5vmin !important; 
        animation-duration: 12s !important; 
    }}
}}
/* ========================================================= */


/* 🌟 KEYFRAMES: HIỆU ỨNG TỎA SÁNG MÀU NGẪU NHIÊN */
@keyframes glow-random-color {{
    0%, 57.14%, 100% {{
        box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.3);
    }}
    
    0% {{
        box-shadow: 0 0 10px 4px rgba(255, 0, 0, 0.9), 0 0 20px 8px rgba(255, 0, 0, 0.6), inset 0 0 5px 2px rgba(255, 0, 0, 0.9);
    }}
    
    14.28% {{ 
        box-shadow: 0 0 10px 4px rgba(0, 255, 0, 0.9), 0 0 20px 8px rgba(0, 255, 0, 0.6), inset 0 0 5px 2px rgba(0, 255, 0, 0.9);
    }}
    
    28.56% {{ 
        box-shadow: 0 0 10px 4px rgba(0, 0, 255, 0.9), 0 0 20px 8px rgba(0, 0, 255, 0.6), inset 0 0 5px 2px rgba(0, 0, 255, 0.9);
    }}

    42.84% {{ 
        box-shadow: 0 0 10px 4px rgba(255, 255, 0, 0.9), 0 0 20px 8px rgba(255, 255, 0, 0.6), inset 0 0 5px 2px rgba(255, 255, 0, 0.9);
    }}
    
    57.14% {{ 
        box-shadow: 0 0 10px 4px rgba(255, 0, 255, 0.9), 0 0 20px 8px rgba(255, 0, 255, 0.6), inset 0 0 5px 2px rgba(255, 0, 255, 0.9);
    }}
}}

/* === MUSIC PLAYER STYLES === */
#music-player-container {{
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 350px; 
    padding: 8px 16px; 
    background: rgba(0, 0, 0, 0.7); 
    border-radius: 12px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7);
    z-index: 999;
    opacity: 0;
    transform: translateY(100px);
    transition: opacity 1s ease-out 2s, transform 1s ease-out 2s;
}}

#music-player-container::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    margin: -3px;
    width: calc(100% + 6px);
    height: calc(100% + 6px);
    
    background-image: var(--logo-bg-url);
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    filter: contrast(110%) brightness(90%);
    opacity: 0.4; 
    z-index: -1; 
    
    border-radius: 12px;
    
    box-sizing: border-box; 
    animation: glow-random-color 7s linear infinite;
}}

#music-player-container * {{
    position: relative;
    z-index: 5; 
}}

.video-finished #music-player-container {{
    opacity: 1;
    transform: translateY(0);
}}

#music-player-container .controls,
#music-player-container .time-info {{
    color: #fff;
    text-shadow: 0 0 7px #000;
}}

#music-player-container .controls {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin-bottom: 6px; 
}}

#music-player-container .control-btn {{
    background: rgba(255, 255, 255, 0.2);
    border: 2px solid #FFFFFF; 
    color: #FFD700;
    width: 32px; 
    height: 32px;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    font-size: 14px;
}}

#music-player-container .control-btn:hover {{
    background: rgba(255, 215, 0, 0.5);
    transform: scale(1.15);
}}

#music-player-container .control-btn.play-pause {{
    width: 40px; 
    height: 40px;
    font-size: 18px;
}}

#music-player-container .progress-container {{
    width: 100%;
    height: 5px; 
    background: rgba(0, 0, 0, 0.5);
    border-radius: 3px;
    cursor: pointer;
    margin-bottom: 4px; 
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.4); 
}}

#music-player-container .progress-bar {{
    height: 100%;
    background: linear-gradient(90deg, #FFD700, #FFA500);
    border-radius: 3px;
    width: 0%;
    transition: width 0.1s linear;
}}

#music-player-container .time-info {{
    display: flex;
    justify-content: space-between;
    color: rgba(255, 255, 255, 1);
    font-size: 10px; 
    font-family: monospace;
}}

@media (max-width: 768px) {{
    #music-player-container {{
        width: calc(100% - 40px);
        right: 20px;
        left: 20px;
        bottom: 15px;
        padding: 8px 12px;
    }}
    #music-player-container .control-btn,
    #music-player-container .control-btn.play-pause {{
        width: 36px;
        height: 36px;
        font-size: 16px;
    }}
    #music-player-container .control-btn.play-pause {{
        width: 44px;
        height: 44px;
        font-size: 20px;
    }}
}}

/* ================================================ */
/* === CSS CHO NAVIGATION BUTTONS (FIXED) === */
/* ================================================ */

/* Container chứa buttons */
.nav-buttons-wrapper {{
    position: fixed;
    top: 50%;
    left: 0;
    width: 100%;
    transform: translateY(-50%);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 80px;
    z-index: 10000;
    opacity: 0;
    transition: opacity 1s ease-out;
    pointer-events: none;
}}

.video-finished .nav-buttons-wrapper {{
    opacity: 1;
    pointer-events: all;
}}

/* Ẩn columns và elements mặc định của Streamlit */
.nav-buttons-wrapper .stColumn {{
    display: contents !important;
}}

.nav-buttons-wrapper [data-testid="column"] {{
    display: contents !important;
}}

/* Reset CSS cho thẻ a trong page_link */
.nav-buttons-wrapper a {{
    /* Không dùng all: unset; nữa để giữ lại hành vi liên kết */
    text-decoration: none; /* Đảm bảo gạch chân biến mất */
    color: inherit; /* Giữ màu chữ mặc định nếu cần */
    
    display: flex !important;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    cursor: pointer;
    position: relative;
    transform-origin: center;
    padding: 1rem 2rem;
    border-radius: 9999px;
    min-width: 280px;
    
    /* Button variables */
    --black-700: hsla(0, 0%, 12%, 1);
    --border_radius: 9999px;
    --transtion: 0.3s ease-in-out;
    --active: 0;
    --hover-color: hsl(40, 60%, 85%);
    --text-color: hsl(0, 0%, 100%);
    
    transform: scale(calc(1 + (var(--active, 0) * 0.2)));
    transition: transform var(--transtion);
}}

/* Background đen của button */
.nav-buttons-wrapper a::before {{
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 100%;
    height: 100%;
    background-color: var(--black-700);
    border-radius: var(--border_radius);
    box-shadow: 
        inset 0 0.5px hsl(0, 0%, 100%), 
        inset 0 -1px 2px 0 hsl(0, 0%, 0%), 
        0px 4px 10px -4px hsla(0, 0%, 0%, calc(1 - var(--active, 0))), 
        0 0 0 calc(var(--active, 0) * 0.375rem) var(--hover-color);
    transition: all var(--transtion);
    z-index: 0;
}}

/* Hiệu ứng sáng bên trong khi hover */
.nav-buttons-wrapper a::after {{
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 90%;
    height: 90%;
    background-color: hsla(40, 60%, 85%, 0.75);
    background-image: 
        radial-gradient(at 51% 89%, hsla(45, 60%, 90%, 1) 0px, transparent 50%), 
        radial-gradient(at 100% 100%, hsla(35, 60%, 80%, 1) 0px, transparent 50%), 
        radial-gradient(at 22% 91%, hsla(35, 60%, 80%, 1) 0px, transparent 50%);
    background-position: top;
    opacity: var(--active, 0);
    border-radius: var(--border_radius);
    transition: opacity var(--transtion);
    z-index: 2;
}}

/* Hover state */
.nav-buttons-wrapper a:hover,
.nav-buttons-wrapper a:focus-visible {{
    --active: 1;
    box-shadow: 0 0 15px 5px var(--hover-color), 0 0 0 0.375rem var(--hover-color);
}}

/* Text styling */
.nav-buttons-wrapper a span {{
    position: relative;
    z-index: 10;
    background-image: linear-gradient(
        90deg, 
        var(--text-color) 0%, 
        hsla(0, 0%, 100%, var(--active, 0.5)) 120%
    );
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    color: transparent;
    font-weight: 600;
    letter-spacing: 1px;
    white-space: nowrap;
    text-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
    font-size: 1.1rem;
    line-height: 1.1rem;
}}

/* SVG icon styling */
.nav-buttons-wrapper a svg {{
    position: relative;
    z-index: 10;
    width: 1.75rem;
    height: 1.75rem;
    color: var(--text-color);
    flex-shrink: 0;
}}

/* Mobile responsive */
@media (max-width: 768px) {{
    .nav-buttons-wrapper {{
        bottom: 120px;
        top: auto;
        left: 50%;
        width: calc(100% - 40px);
        max-width: 450px;
        transform: translateX(-50%);
        flex-direction: column;
        gap: 15px;
        padding: 0;
    }}
    
    .nav-buttons-wrapper a {{
        width: 100%;
        min-width: unset;
        padding: 0.8rem 1.5rem;
    }}
    
    .nav-buttons-wrapper a svg {{
        width: 1.5rem;
        height: 1.5rem;
    }}
}}
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- PHẦN 3: MÃ HTML/CSS/JavaScript IFRAME CHO VIDEO INTRO (KHÔNG THAY ĐỔI) ---

if len(music_files) > 0:
    music_sources_js = ",\n\t\t\t".join([f"'{url}'" for url in music_files])
else:
    music_sources_js = ""

js_callback_video = f"""
<script>
    console.log("Script loaded");
    
    function sendBackToStreamlit(isSkipped = false) {{
        console.log("Transitioning to main content. Is Skipped:", isSkipped);
        const stApp = window.parent.document.querySelector('.stApp');
        if (stApp) {{
            stApp.classList.add('video-finished', 'main-content-revealed');
            stApp.classList.remove('video-running'); 
        }}
        
        const revealGrid = window.parent.document.querySelector('.reveal-grid');

        if (!isSkipped) {{
            initRevealEffect();
        }} else {{
            if (revealGrid) {{
                revealGrid.remove();
            }}
        }}
        
        setTimeout(initMusicPlayer, 100); 
    }}
    
    function initRevealEffect() {{
        const revealGrid = window.parent.document.querySelector('.reveal-grid');
        if (!revealGrid) {{ return; }}

        const cells = revealGrid.querySelectorAll('.grid-cell');
        const shuffledCells = Array.from(cells).sort(() => Math.random() - 0.5);

        shuffledCells.forEach((cell, index) => {{
            setTimeout(() => {{
                cell.style.opacity = 0;
            }}, index * 10);
        }});
        setTimeout(() => {{
             revealGrid.remove();
        }}, shuffledCells.length * 10 + 1000); 
    }}

    function initMusicPlayer() {{
        console.log("Initializing music player");
        const musicSources = [{music_sources_js}];
        
        if (musicSources.length === 0) {{
            console.log("No music files available");
            return;
        }}
        
        let currentTrack = 0;
        let isPlaying = false;
        
        const audio = new Audio();
        audio.volume = 0.3;
        
        const playPauseBtn = window.parent.document.getElementById('play-pause-btn');
        const prevBtn = window.parent.document.getElementById('prev-btn');
        const nextBtn = window.parent.document.getElementById('next-btn');
        const progressBar = window.parent.document.getElementById('progress-bar');
        const progressContainer = window.parent.document.getElementById('progress-container');
        const currentTimeEl = window.parent.document.getElementById('current-time');
        const durationEl = window.parent.document.getElementById('duration');
        if (!playPauseBtn || !prevBtn || !nextBtn) {{
            console.error("Music player elements not found in parent document");
            return;
        }}
        
        function loadTrack(index) {{
            console.log("Loading track", index + 1, "from URL:", musicSources[index]);
            audio.src = musicSources[index]; 
            audio.load();
        }}
        
        function togglePlayPause() {{
            if (isPlaying) {{
                audio.pause();
                playPauseBtn.textContent = '▶';
            }} else {{
                audio.play().catch(e => console.error("Play error:", e));
                playPauseBtn.textContent = '⏸';
            }}
            isPlaying = !isPlaying;
        }}
        
        function nextTrack() {{
            currentTrack = (currentTrack + 1) % musicSources.length;
            loadTrack(currentTrack);
            if (isPlaying) {{
                audio.play().catch(e => console.error("Play error:", e));
            }}
        }}
        
        function prevTrack() {{
            currentTrack = (currentTrack - 1 + musicSources.length) % musicSources.length;
            loadTrack(currentTrack);
            if (isPlaying) {{
                audio.play().catch(e => console.error("Play error:", e));
            }}
        }}
        
        function formatTime(seconds) {{
            if (isNaN(seconds)) return '0:00';
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return `${{mins}}:${{secs.toString().padStart(2, '0')}}`;
        }}
        
        audio.addEventListener('timeupdate', () => {{
            const progress = (audio.currentTime / audio.duration) * 100;
            progressBar.style.width = progress + '%';
            currentTimeEl.textContent = formatTime(audio.currentTime);
        }});
        audio.addEventListener('loadedmetadata', () => {{
            durationEl.textContent = formatTime(audio.duration);
        }});
        audio.addEventListener('ended', () => {{
            nextTrack();
        }});
        audio.addEventListener('error', (e) => {{ 
            console.error("Error loading music track:", e);
            nextTrack();
        }});
        playPauseBtn.addEventListener('click', togglePlayPause);
        nextBtn.addEventListener('click', nextTrack);
        prevBtn.addEventListener('click', prevTrack);
        
        progressContainer.addEventListener('click', (e) => {{
            const rect = progressContainer.getBoundingClientRect();
            const percent = (e.clientX - rect.left) / rect.width;
            audio.currentTime = percent * audio.duration;
        }});
        loadTrack(0);
        console.log("Music player initialized successfully");
    }}

    document.addEventListener("DOMContentLoaded", function() {{
        console.log("DOM loaded, waiting for elements...");
        
        const stApp = window.parent.document.querySelector('.stApp');
        if (stApp) {{
            stApp.classList.add('video-running'); 
        }}

        const urlParams = new URLSearchParams(window.parent.location.search);
        const skipIntro = urlParams.get('skip_intro');
        
        if (skipIntro === '1') {{
            console.log("Skip intro detected. Directly revealing main content.");
            sendBackToStreamlit(true); 
            const iframe = window.frameElement;
            if (iframe) {{
                 iframe.style.opacity = 0;
                 iframe.style.visibility = 'hidden';
                 iframe.style.pointerEvents = 'none'; 
            }}
            return; 
        }}

        const waitForElements = setInterval(() => {{
            const video = document.getElementById('intro-video');
            const audio = document.getElementById('background-audio');
            const introTextContainer = document.getElementById('intro-text-container');
            const overlay = document.getElementById('click-to-play-overlay');
           
            if (video && audio && introTextContainer && overlay) {{
                clearInterval(waitForElements);
                console.log("All elements found, initializing...");
                
                const isMobile = window.innerWidth <= 768;
         
                const videoSource = isMobile ? 'data:video/mp4;base64,{video_mobile_base64}' : 'data:video/mp4;base64,{video_pc_base64}';
                video.src = videoSource;
                audio.src = 'data:audio/mp3;base64,{audio_base64}';

                console.log("Video/Audio source set. Loading metadata...");

                let interactionHandled = false; 
                
                const tryToPlayAndHideOverlay = (e) => {{
                    e.preventDefault(); 
                    
                    if (interactionHandled) {{
                        console.log("Interaction already handled, ignoring.");
                        return;
                    }}
                    interactionHandled = true;

                    console.log("Attempting to play video (User interaction)");
                    
                    overlay.removeEventListener('click', tryToPlayAndHideOverlay);
                    overlay.removeEventListener('touchstart', tryToPlayAndHideOverlay);
                    overlay.removeEventListener('dblclick', tryToPlayAndHideOverlay); 

                    video.play().then(() => {{
                        console.log("✅ Video is playing, hiding overlay!");
                        overlay.classList.add('hidden'); 
                    }}).catch(err => {{
                        console.error("❌ Still can't play video, skipping intro (Error/File issue):", err);
                        overlay.textContent = "LỖI PHÁT. ĐANG CHUYỂN TRANG...";
                        setTimeout(() => sendBackToStreamlit(false), 2000); 
                    }});
                    audio.play().catch(e => {{
                        console.log("Audio autoplay blocked (normal), waiting for video end.");
                    }});
                }};

                video.addEventListener('canplaythrough', () => {{
                    tryToPlayAndHideOverlay({{ preventDefault: () => {{}} }}); 
                }}, {{ once: true }});

                video.addEventListener('ended', () => {{
                    console.log("Video ended, transitioning...");
                    video.
                    style.opacity = 0;
audio.pause();
audio.currentTime = 0;
                introTextContainer.style.opacity = 0;
                setTimeout(() => sendBackToStreamlit(false), 500); 
            }});
            video.addEventListener('error', (e) => {{
                console.error("Video error detected (Codec/Base64/File corrupted). Skipping intro:", e);
                sendBackToStreamlit(false); 
            }});
            
            overlay.addEventListener('click', tryToPlayAndHideOverlay, {{ once: true }});
            overlay.addEventListener('touchstart', tryToPlayAndHideOverlay, {{ once: true }});
            overlay.addEventListener('dblclick', tryToPlayAndHideOverlay, {{ once: true }}); 
            
            video.load();
            const chars = introTextContainer.querySelectorAll('.intro-char');
            chars.forEach((char, index) => {{
                char.style.animationDelay = `${{index * 0.1}}s`;
                char.classList.add('char-shown');
            }});
        }}
    }}, 100);
    setTimeout(() => {{
        clearInterval(waitForElements);
        const video = document.getElementById('intro-video');
        if (video && !video.src) {{
            console.warn("Timeout before video source set. Force transitioning to main content.");
            sendBackToStreamlit(false); 
        }}
    }}, 5000);
}});
</script>
"""
html_content_modified = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            height: 100vh;
            width: 100vw;
            background-color: #000;
        }}
    #intro-video {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        z-index: 0;
        transition: opacity 1s;
    }}

    #intro-text-container {{
        position: fixed;
        top: 5vh;
        width: 100%;
        text-align: center;
        color: #FFD700;
        font-size: 3vw;
        font-family: 'Sacramento', cursive;
        font-weight: 400;
        text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.8);
        z-index: 100;
        pointer-events: none;
        display: flex;
        justify-content: center;
        opacity: 1;
        transition: opacity 0.5s;
    }}
    
    .intro-char {{
        display: inline-block;
        opacity: 0;
        transform: translateY(-50px);
        animation-fill-mode: forwards;
        animation-duration: 0.8s;
        animation-timing-function: ease-out;
    }}

    @keyframes charDropIn {{
        from {{
            opacity: 0;
            transform: translateY(-50px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}

    .intro-char.char-shown {{
        animation-name: charDropIn;
    }}
    
    #click-to-play-overlay {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 200; 
        cursor: pointer;
        background: rgba(0, 0, 0, 0.5); 
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Playfair Display', serif;
        color: #fff;
        font-size: 2vw;
        text-shadow: 1px 1px 3px #000;
        transition: opacity 0.5s;
    }}

    #click-to-play-overlay.hidden {{
        opacity: 0;
        pointer-events: none; 
    }}

    @media (max-width: 768px) {{
        #intro-text-container {{
            font-size: 6vw;
        }}
         #click-to-play-overlay {{
            font-size: 4vw;
        }}
    }}
</style>
</head>
<body>
    <div id="intro-text-container">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    <video id="intro-video" muted playsinline></video>
    <audio id="background-audio"></audio>
    <div id="click-to-play-overlay">CLICK/TOUCH VÀO ĐÂY ĐỂ BẮT ĐẦU</div>
    {js_callback_video}
</body>
</html>
"""
intro_title = "KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI"
intro_chars_html = ''.join([
    f'<span class="intro-char">{char}</span>' if char != ' ' else '<span class="intro-char">&nbsp;</span>'
    for char in intro_title
])
html_content_modified = html_content_modified.replace(
    '<div id="intro-text-container">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>',
    f'<div id="intro-text-container">{intro_chars_html}</div>'
)

# --- HIỂN THỊ IFRAME VIDEO ---
st.components.v1.html(html_content_modified, height=1080, scrolling=False)

# --- HIỆU ỨNG REVEAL VÀ NỘI DUNG CHÍNH ---

grid_cells_html = ""
for i in range(240):
    grid_cells_html += f'<div class="grid-cell"></div>'

reveal_grid_html = f"""
<div class="reveal-grid">
    {grid_cells_html}
</div>
"""
st.markdown(reveal_grid_html, unsafe_allow_html=True)

# --- NỘI DUNG CHÍNH (TIÊU ĐỀ) ---
main_title_text = "TỔ BẢO DƯỠNG SỐ 1"

st.markdown(f"""
<div id="main-title-container">
    <h1>{main_title_text}</h1>
</div>
""", unsafe_allow_html=True)

# --- MUSIC PLAYER ---
if len(music_files) > 0:
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

# --- NAVIGATION BUTTONS (SIMPLE HTML VERSION) ---
st.markdown("""
<div class="nav-buttons-wrapper">
    <a href="/partnumber" class="nav-button">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"></path>
        </svg>
        <span>TRA CỨU PART NUMBER</span>
    </a>
    <a href="/bank" class="nav-button">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <span>NGÂN HÀNG TRẮC NGHIỆM</span>
    </a>
</div>
""", unsafe_allow_html=True)

# Mark first load as complete
if st.session_state.first_load:
    st.session_state.first_load = False
