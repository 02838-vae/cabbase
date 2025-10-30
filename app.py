import streamlit as st
import os
from pathlib import Path

# --- CẤU HÌNH BAN ĐẦU ---
st.set_page_config(
    page_title="Tổ Bảo Dưỡng Số 1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Khởi tạo session state
if 'video_ended' not in st.session_state:
    st.session_state.video_ended = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

# --- CÁC HÀM TIỆN ÍCH ---

def get_file_url(filename):
    """Tạo URL tương đối cho file trong thư mục static"""
    return filename

def check_files_exist():
    """Kiểm tra các file cần thiết"""
    required_files = [
        "airplane.mp4",
        "mobile.mp4", 
        "plane_fly.mp3",
        "cabbase.jpg",
        "mobile.jpg"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        st.error(f"⚠️ Thiếu các file: {', '.join(missing_files)}")
        st.stop()
    
    # Đếm file nhạc nền
    music_count = len([f for f in os.listdir('.') if f.startswith('background') and f.endswith('.mp3')])
    
    return music_count

music_count = check_files_exist()

# --- PHẦN 1: NHÚNG FONT ---
font_links = """
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
"""
st.markdown(font_links, unsafe_allow_html=True)

# --- PHẦN 2: CSS CHÍNH ---
hide_streamlit_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sacramento&family=Playfair+Display:ital,wght@0,400..900;1,400..900&family=Orbitron:wght@400;700;900&display=swap');

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
}}

.video-finished iframe:first-of-type {{
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
    height: 1px !important;	
    width: 1px !important;
}}

.stApp {{
    --main-bg-url-pc: url('cabbase.jpg');
    --main-bg-url-mobile: url('mobile.jpg');
    --logo-bg-url: url('logo.jpg');
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

@keyframes scrollText {{
    0% {{ transform: translate(100vw, 0); }}
    100% {{ transform: translate(-100%, 0); }}
}}

@keyframes colorShift {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
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
        font-size: 6.5vw;	
        animation-duration: 8s;
    }}
}}

/* === NAVIGATION CARDS === */
.nav-cards-container {{
    position: fixed;
    z-index: 15;
    pointer-events: none;
    opacity: 0;
    transition: opacity 2s 1s;
}}

.video-finished .nav-cards-container {{
    opacity: 1;
    pointer-events: auto;
}}

/* Desktop Layout */
@media (min-width: 769px) {{
    .nav-cards-container {{
        top: 50%;
        left: 0;
        right: 0;
        transform: translateY(-50%);
        display: flex;
        justify-content: space-between;
        padding: 0 5vw;
        gap: 2vw;
    }}
    
    .nav-card {{
        width: 320px;
        height: 200px;
    }}
}}

/* Mobile Layout */
@media (max-width: 768px) {{
    .nav-cards-container {{
        top: 55vh;
        left: 50%;
        transform: translateX(-50%);
        display: flex;
        flex-direction: column;
        gap: 20px;
        align-items: center;
        width: 90%;
        max-width: 400px;
    }}
    
    .nav-card {{
        width: 100%;
        height: 160px;
    }}
}}

@keyframes cardGlow {{
    0%, 100% {{
        box-shadow: 
            0 0 20px rgba(255, 215, 0, 0.4),
            0 0 40px rgba(255, 215, 0, 0.2),
            inset 0 0 20px rgba(255, 215, 0, 0.1);
    }}
    50% {{
        box-shadow: 
            0 0 30px rgba(255, 215, 0, 0.6),
            0 0 60px rgba(255, 215, 0, 0.3),
            inset 0 0 30px rgba(255, 215, 0, 0.2);
    }}
}}

@keyframes pulse {{
    0%, 100% {{ transform: scale(1); }}
    50% {{ transform: scale(1.05); }}
}}

.nav-card {{
    background: linear-gradient(135deg, 
        rgba(139, 115, 85, 0.85) 0%, 
        rgba(101, 84, 63, 0.85) 50%,
        rgba(115, 94, 70, 0.85) 100%);
    backdrop-filter: blur(10px);
    border: 3px solid rgba(255, 215, 0, 0.6);
    border-radius: 20px;
    padding: 30px;
    cursor: pointer;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: 
        0 10px 40px rgba(0, 0, 0, 0.5),
        0 0 20px rgba(255, 215, 0, 0.3),
        inset 0 0 20px rgba(255, 215, 0, 0.1);
}}

.nav-card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, 
        transparent, 
        rgba(255, 215, 0, 0.3), 
        transparent);
    transition: left 0.6s;
}}

.nav-card:hover::before {{
    left: 100%;
}}

.nav-card:hover {{
    transform: translateY(-10px) scale(1.05);
    border-color: rgba(255, 215, 0, 1);
    box-shadow: 
        0 20px 60px rgba(0, 0, 0, 0.7),
        0 0 40px rgba(255, 215, 0, 0.6),
        inset 0 0 30px rgba(255, 215, 0, 0.2);
    animation: cardGlow 2s ease-in-out infinite;
}}

.nav-card:active {{
    transform: translateY(-5px) scale(1.02);
}}

.nav-card-icon {{
    font-size: 48px;
    margin-bottom: 15px;
    filter: drop-shadow(0 0 10px rgba(255, 215, 0, 0.5));
    transition: all 0.3s ease;
}}

.nav-card:hover .nav-card-icon {{
    transform: scale(1.2) rotate(5deg);
    filter: drop-shadow(0 0 20px rgba(255, 215, 0, 0.8));
}}

.nav-card-title {{
    font-family: 'Orbitron', sans-serif;
    font-size: 24px;
    font-weight: 900;
    color: #FFD700;
    text-shadow: 
        2px 2px 4px rgba(0, 0, 0, 0.8),
        0 0 10px rgba(255, 215, 0, 0.5);
    margin: 0;
    letter-spacing: 2px;
    transition: all 0.3s ease;
}}

.nav-card:hover .nav-card-title {{
    color: #FFF;
    text-shadow: 
        2px 2px 4px rgba(0, 0, 0, 0.8),
        0 0 20px rgba(255, 215, 0, 0.8),
        0 0 30px rgba(255, 215, 0, 0.6);
    letter-spacing: 3px;
}}

.nav-card-subtitle {{
    font-family: 'Playfair Display', serif;
    font-size: 14px;
    color: rgba(255, 255, 255, 0.8);
    margin-top: 10px;
    font-style: italic;
    transition: all 0.3s ease;
}}

.nav-card:hover .nav-card-subtitle {{
    color: rgba(255, 255, 255, 1);
}}

@media (max-width: 768px) {{
    .nav-card {{
        padding: 25px;
    }}
    
    .nav-card-icon {{
        font-size: 40px;
        margin-bottom: 12px;
    }}
    
    .nav-card-title {{
        font-size: 20px;
        letter-spacing: 1.5px;
    }}
    
    .nav-card-subtitle {{
        font-size: 12px;
    }}
}}

@keyframes glow-random-color {{
    0%, 57.14%, 100% {{
        box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.3);
    }}
    
    0% {{
        box-shadow: 
            0 0 10px 4px rgba(255, 0, 0, 0.9), 
            0 0 20px 8px rgba(255, 0, 0, 0.6), 
            inset 0 0 5px 2px rgba(255, 0, 0, 0.9); 
    }}
    
    14.28% {{ 
        box-shadow: 
            0 0 10px 4px rgba(0, 255, 0, 0.9), 
            0 0 20px 8px rgba(0, 255, 0, 0.6), 
            inset 0 0 5px 2px rgba(0, 255, 0, 0.9);
    }}
    
    28.56% {{ 
        box-shadow: 
            0 0 10px 4px rgba(0, 0, 255, 0.9), 
            0 0 20px 8px rgba(0, 0, 255, 0.6), 
            inset 0 0 5px 2px rgba(0, 0, 255, 0.9);
    }}

    42.84% {{ 
        box-shadow: 
            0 0 10px 4px rgba(255, 255, 0, 0.9), 
            0 0 20px 8px rgba(255, 255, 0, 0.6), 
            inset 0 0 5px 2px rgba(255, 255, 0, 0.9);
    }}
    
    57.14% {{ 
        box-shadow: 
            0 0 10px 4px rgba(255, 0, 255, 0.9), 
            0 0 20px 8px rgba(255, 0, 255, 0.6), 
            inset 0 0 5px 2px rgba(255, 0, 255, 0.9);
    }}
}}

/* === MUSIC PLAYER === */
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
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- PHẦN 3: JavaScript cho Video Intro ---

music_sources_js = ",\n        ".join([f"'background{i}.mp3'" for i in range(1, music_count + 1)])

js_callback_video = f"""
<script>
    console.log("Script loaded");
    
    function sendBackToStreamlit() {{
        console.log("Video ended or skipped, revealing main content");
        const stApp = window.parent.document.querySelector('.stApp');
        if (stApp) {{
            stApp.classList.add('video-finished', 'main-content-revealed');
        }}
        initRevealEffect();
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
            console.error("Music player elements not found");
            return;
        }}
        
        function loadTrack(index) {{
            console.log("Loading track", index + 1);
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
        
        playPauseBtn.addEventListener('click', togglePlayPause);
        nextBtn.addEventListener('click', nextTrack);
        prevBtn.addEventListener('click', prevTrack);
        
        progressContainer.addEventListener('click', (e) => {{
            const rect = progressContainer.getBoundingClientRect();
            const percent = (e.clientX - rect.left) / rect.width;
            audio.currentTime = percent * audio.duration;
        }});
        
        loadTrack(0);
        console.log("Music player initialized");
    }}

    document.addEventListener("DOMContentLoaded", function() {{
        console.log("DOM loaded");
        
        const waitForElements = setInterval(() => {{
            const video = document.getElementById('intro-video');
            const audio = document.getElementById('background-audio');
            const introTextContainer = document.getElementById('intro-text-container');
            
            if (video && audio && introTextContainer) {{
                clearInterval(waitForElements);
                console.log("Elements found, initializing...");
                
                const isMobile = window.innerWidth <= 768;
                const videoSource = isMobile ? 'mobile.mp4' : 'airplane.mp4';

                video.src = videoSource;
                audio.src = 'plane_fly.mp3';
                
                const tryToPlay = () => {{
                    console.log("Attempting to play video");
                    
                    video.play().then(() => {{
                        console.log("✅ Video playing!");
                    }}).catch(err => {{
                        console.error("❌ Video play error:", err);
                        setTimeout(sendBackToStreamlit, 2000);	
                    }});

                    audio.play().catch(e => {{
                        console.log("Audio autoplay blocked (normal)");
                    }});
                }};

                video.addEventListener('canplaythrough', tryToPlay, {{ once: true }});
                
                video.addEventListener('ended', () => {{
                    console.log("Video ended");
                    video.style.opacity = 0;
                    audio.pause();
                    audio.currentTime = 0;
                    introTextContainer.style.opacity = 0;	
                    setTimeout(sendBackToStreamlit, 500);
                }});

                video.addEventListener('error', (e) => {{
                    console.error("Video error:", e);
                    sendBackToStreamlit();
                }});

                const clickHandler = () => {{
                    console.log("User interaction detected");
                    tryToPlay();
                }};
                
                document.addEventListener('click', clickHandler, {{ once: true }});
                document.addEventListener('touchstart', clickHandler, {{ once: true }});
                
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
                console.warn("Timeout, force transition");
                sendBackToStreamlit();
            }}
        }}, 5000);
    }});
</script>
"""

# HTML cho Video
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

        @media (max-width: 768px) {{
            #intro-text-container {{
                font-size: 6vw;	
            }}
        }}
    </style>
</head>
<body>
    <div id="intro-text-container">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    <video id="intro-video" muted playsinline></video>
    <audio id="background-audio"></audio>
    {js_callback_video}
</body>
</html>
"""

# Xử lý hiệu ứng chữ thả
intro_title = "KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI"
intro_chars_html = ''.join([
    f'<span class="intro-char">{char}</span>' if char != ' ' else '<span class="intro-char">&nbsp;</span>'	
    for char in intro_title
])
html_content_modified = html_content_modified.replace(
    "<div id=\"intro-text-container\">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>",
    f"<div id=\"intro-text-container\">{intro_chars_html}</div>"
)

# --- HIỂN THỊ IFRAME VIDEO ---
st.components.v1.html(html_content_modified, height=1080, scrolling=False)

# --- HIỆU ỨNG REVEAL ---
grid_cells_html = "".join(['<div class="grid-cell"></div>' for _ in range(240)])
st.markdown(f'<div class="reveal-grid">{grid_cells_html}</div>', unsafe_allow_html=True)

# --- NỘI DUNG CHÍNH ---
main_title_text = "TỔ BẢO DƯỠNG SỐ 1"	
st.markdown(f'<div id="main-title-container"><h1>{main_title_text}</h1></div>', unsafe_allow_html=True)

# --- NAVIGATION CARDS ---
st.markdown("""
<div class="nav-cards-container">
    <div class="nav-card" onclick="window.parent.postMessage({type: 'navigate', page: 'partnumber'}, '*')">
        <div class="nav-card-icon">🔧</div>
        <h2 class="nav-card-title">TRA CỨU PART NUMBER</h2>
        <p class="nav-card-subtitle">Tìm kiếm thông tin linh kiện nhanh chóng</p>
    </div>
    
    <div class="nav-card" onclick="window.parent.postMessage({type: 'navigate', page: 'quiz'}, '*')">
        <div class="nav-card-icon">📚</div>
        <h2 class="nav-card-title">NGÂN HÀNG TRẮC NGHIỆM</h2>
        <p class="nav-card-subtitle">Kiểm tra kiến thức chuyên môn</p>
    </div>
</div>

<script>
    window.addEventListener('message', function(event) {
        if (event.data.type === 'navigate') {
            console.log('Navigation requested to:', event.data.page);
            // Streamlit sẽ xử lý navigation thông qua session state
            const buttons = window.parent.document.querySelectorAll('button');
            buttons.forEach(btn => {
                if (btn.innerText.includes(event.data.page)) {
                    btn.click();
                }
            });
        }
    });
</script>
""", unsafe_allow_html=True)

# --- MUSIC PLAYER ---
if music_count > 0:
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

# --- XỬ LÝ NAVIGATION ---
# Tạo các nút ẩn để xử lý navigation
col1, col2 = st.columns(2)
with col1:
    if st.button("partnumber", key="nav_partnumber", help="Tra cứu Part Number"):
        st.session_state.current_page = 'partnumber'
        st.rerun()

with col2:
    if st.button("quiz", key="nav_quiz", help="Ngân hàng trắc nghiệm"):
        st.session_state.current_page = 'quiz'
        st.rerun()

# Ẩn các nút navigation bằng CSS
st.markdown("""
<style>
    button[kind="secondary"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# --- HIỂN THỊ TRANG THEO SESSION STATE ---
if st.session_state.current_page == 'partnumber':
    st.markdown("""
    <div style='position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; 
                background: rgba(0,0,0,0.95); z-index: 2000; 
                display: flex; flex-direction: column; justify-content: center; align-items: center;'>
        <h1 style='color: #FFD700; font-family: Orbitron; font-size: 48px; margin-bottom: 30px;'>
            🔧 TRA CỨU PART NUMBER
        </h1>
        <p style='color: white; font-size: 20px; margin-bottom: 50px;'>
            Trang đang được xây dựng...
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🏠 Quay lại trang chủ", key="back_from_partnumber"):
        st.session_state.current_page = 'home'
        st.rerun()

elif st.session_state.current_page == 'quiz':
    st.markdown("""
    <div style='position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; 
                background: rgba(0,0,0,0.95); z-index: 2000; 
                display: flex; flex-direction: column; justify-content: center; align-items: center;'>
        <h1 style='color: #FFD700; font-family: Orbitron; font-size: 48px; margin-bottom: 30px;'>
            📚 NGÂN HÀNG TRẮC NGHIỆM
        </h1>
        <p style='color: white; font-size: 20px; margin-bottom: 50px;'>
            Trang đang được xây dựng...
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🏠 Quay lại trang chủ", key="back_from_quiz"):
        st.session_state.current_page = 'home'
        st.rerun()
