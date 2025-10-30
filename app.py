import streamlit as st
import base64
import os

# --- CẤU HÌNH BAN ĐẦU ---
st.set_page_config(
    page_title="Tổ Bảo Dưỡng Số 1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Khởi tạo session state với giá trị mặc định an toàn
if 'video_ended' not in st.session_state:
    st.session_state.video_ended = False

# Kiểm tra query params để bỏ qua video
query_params = st.query_params
if 'skip_video' in query_params or st.session_state.video_ended:
    st.session_state.video_ended = True

# --- CÁC HÀM TIỆN ÍCH ---
def get_base64_encoded_file(file_path):
    """Đọc file và trả về Base64 encoded string."""
    if not os.path.exists(file_path):
        return None
    try:
        if os.path.getsize(file_path) == 0:
            return None
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    except Exception as e:
        print(f"Lỗi khi đọc file {file_path}: {str(e)}") 
        return None

def get_intro_html(video_pc_base64, video_mobile_base64, audio_base64, music_files):
    """Tạo chuỗi HTML/JS cho video intro."""
    
    # Tạo danh sách music sources cho JavaScript 
    if len(music_files) > 0:
        music_sources_js = ",\n        ".join([f"'data:audio/mp3;base64,{music}'" for music in music_files])
    else:
        music_sources_js = ""

    # JavaScript được tối ưu hóa
    js_callback_video = f"""
    <script>
        console.log("🎬 Video script loaded");
        
        // Hàm chuyển sang nội dung chính (KHÔNG dùng fetch API)
        function sendBackToStreamlit() {{
            console.log("✅ Transitioning to main content");
            const stApp = window.parent.document.querySelector('.stApp');
            if (stApp) {{
                stApp.classList.add('video-finished', 'main-content-revealed');
            }}
            
            // Đánh dấu video đã kết thúc bằng localStorage
            try {{
                localStorage.setItem('video_ended', 'true');
            }} catch(e) {{
                console.log("localStorage not available");
            }}
            
            initRevealEffect();
            setTimeout(initMusicPlayer, 100);
        }}
        
        function initRevealEffect() {{
            const revealGrid = window.parent.document.querySelector('.reveal-grid');
            if (!revealGrid) {{ 
                console.log("⚠️ Reveal grid not found");
                return; 
            }}
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
            console.log("🎵 Initializing music player");
            
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
                console.error("❌ Music player elements not found");
                return;
            }}
            
            function loadTrack(index) {{
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
            console.log("✅ Music player initialized");
        }}

        // Kiểm tra localStorage khi load
        try {{
            if (localStorage.getItem('video_ended') === 'true') {{
                console.log("Video already played, skipping...");
                sendBackToStreamlit();
                return;
            }}
        }} catch(e) {{
            console.log("localStorage check failed, continuing...");
        }}

        document.addEventListener("DOMContentLoaded", function() {{
            console.log("📄 DOM loaded, waiting for elements...");
            
            let attemptCount = 0;
            const maxAttempts = 50;
            
            const waitForElements = setInterval(() => {{
                attemptCount++;
                const video = document.getElementById('intro-video');
                const audio = document.getElementById('background-audio');
                const introTextContainer = document.getElementById('intro-text-container');
                
                if (video && audio && introTextContainer) {{
                    clearInterval(waitForElements);
                    console.log("✅ All elements found, initializing...");
                    
                    const isMobile = window.innerWidth <= 768;
                    const videoSource = isMobile ? 'data:video/mp4;base64,{video_mobile_base64}' : 'data:video/mp4;base64,{video_pc_base64}';

                    video.src = videoSource;
                    audio.src = 'data:audio/mp3;base64,{audio_base64}';
                    
                    const tryToPlay = () => {{
                        video.play().then(() => {{
                            console.log("✅ Video playing!");
                        }}).catch(err => {{
                            console.error("❌ Video play failed:", err);
                            setTimeout(sendBackToStreamlit, 1000);	
                        }});

                        audio.play().catch(e => {{
                            console.log("Audio autoplay blocked (normal)");
                        }});
                    }};

                    video.addEventListener('canplaythrough', tryToPlay, {{ once: true }});
                    
                    video.addEventListener('ended', () => {{
                        video.style.opacity = 0;
                        audio.pause();
                        audio.currentTime = 0;
                        introTextContainer.style.opacity = 0;	
                        setTimeout(sendBackToStreamlit, 500);
                    }});

                    video.addEventListener('error', (e) => {{
                        console.error("❌ Video error:", e);
                        sendBackToStreamlit();
                    }});

                    const clickHandler = () => {{
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
                }} else if (attemptCount >= maxAttempts) {{
                    clearInterval(waitForElements);
                    console.warn("⚠️ Timeout: Elements not found, skipping video");
                    sendBackToStreamlit();
                }}
            }}, 100);
        }});
    </script>
    """

    # HTML content
    html_content_modified = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
    
    return html_content_modified

# Mã hóa các file media chính
try:
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
    logo_base64 = get_base64_encoded_file("logo.jpg")

    # Kiểm tra file thiếu
    missing_files = []
    if not video_pc_base64: missing_files.append("airplane.mp4")
    if not video_mobile_base64: missing_files.append("mobile.mp4")
    if not audio_base64: missing_files.append("plane_fly.mp3")
    if not bg_pc_base64: missing_files.append("cabbase.jpg")
    if not bg_mobile_base64: missing_files.append("mobile.jpg")
    
    if missing_files:
        st.error(f"❌ Thiếu các file: {', '.join(missing_files)}")
        st.info("💡 Đảm bảo các file media nằm cùng thư mục với app.py")
        st.stop()
        
except Exception as e:
    st.error(f"❌ Lỗi đọc file: {str(e)}")
    st.stop()

if not logo_base64:
    logo_base64 = ""

# Mã hóa các file nhạc nền
music_files = []
for i in range(1, 7):
    music_base64 = get_base64_encoded_file(f"background{i}.mp3")
    if music_base64:
        music_files.append(music_base64)

# --- NHÚNG FONT ---
font_links = """
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
"""
st.markdown(font_links, unsafe_allow_html=True)

# --- CSS CHÍNH ---
hide_streamlit_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sacramento&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');

#st-global-spinner {{ visibility: hidden; }}
.stApp {{ animation: fadein 0.5s forwards; }}
@keyframes fadein {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}

#MainMenu, footer, header {{visibility: hidden;}}
.main {{ padding: 0; margin: 0; }}
div.block-container {{ padding: 0; margin: 0; max-width: 100% !important; }}

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

@keyframes scrollText {{
    0% {{ transform: translate(100vw, 0); }}
    100% {{ transform: translate(-100%, 0); }}
}}

@keyframes colorShift {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

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
    letter-spacing: 5px;	
    white-space: nowrap;	
    display: inline-block;	
    background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
    background-size: 400% 400%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: colorShift 10s ease infinite, scrollText 15s linear infinite;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}}

@media (max-width: 768px) {{
    #main-title-container {{
        height: 8vh;
    }}
    #main-title-container h1 {{
        font-size: 6.5vw;	
        animation-duration: 8s;
    }}
}}

@keyframes glow-random-color {{
    0%, 57.14%, 100% {{
        box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1);
    }}
    0% {{
        box-shadow: 0 0 15px 5px rgba(255, 0, 0, 0.8), 0 0 30px 10px rgba(255, 0, 0, 0.4);
    }}
    14.28% {{ 
        box-shadow: 0 0 15px 5px rgba(0, 255, 255, 0.8), 0 0 30px 10px rgba(0, 255, 255, 0.4);
    }}
    28.56% {{ 
        box-shadow: 0 0 15px 5px rgba(0, 0, 255, 0.8), 0 0 30px 10px rgba(0, 0, 255, 0.4);
    }}
    42.84% {{ 
        box-shadow: 0 0 15px 5px rgba(255, 0, 255, 0.8), 0 0 30px 10px rgba(255, 0, 255, 0.4);
    }}
    50% {{
        box-shadow: 0 0 20px 8px rgba(255, 255, 0, 1), 0 0 40px 15px rgba(255, 255, 0, 0.6);
    }}
}}

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
    top: -3px;
    left: -3px;
    width: calc(100% + 6px);
    height: calc(100% + 6px);
    background-image: var(--logo-bg-url);
    background-size: cover;
    background-position: center;
    filter: contrast(110%) brightness(90%); 
    opacity: 0.4; 
    z-index: -1; 
    border-radius: 12px;
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
    text-shadow: 0 0 8px #FFD700, 0 0 15px #FFA500; 
}}

#music-player-container .control-btn:hover {{
    background: rgba(255, 215, 0, 0.5);
    transform: scale(1.15);
    box-shadow: 0 0 10px 3px rgba(255, 215, 0, 0.8),
                0 0 20px 5px rgba(255, 215, 0, 0.4); 
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
    #music-player-container .control-btn {{
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

.nav-links-container {{
    position: fixed;
    top: 25vh; 
    width: 100%;
    z-index: 30; 
    display: flex;
    justify-content: space-between;
    padding: 0 5vw;
    opacity: 0;
    transition: opacity 2s 3s; 
    pointer-events: none; 
}}

.video-finished .nav-links-container {{
    opacity: 1;
    pointer-events: auto; 
}}

.nav-link {{
    font-family: 'Playfair Display', serif;
    font-size: 1.5vw; 
    font-weight: 700;
    text-decoration: none; 
    padding: 10px 15px;
    border-radius: 8px;
    color: #FFFFFF;
    background: rgba(0, 0, 0, 0.4); 
    border: 1px solid rgba(255, 255, 255, 0.3);
    text-shadow: 0 0 5px #00FFFF, 0 0 10px #00FFFF;
    box-shadow: 0 0 10px rgba(0, 255, 255, 0.7); 
    transition: all 0.3s ease-in-out;
}}

.nav-link:hover {{
    color: #FFD700; 
    background: rgba(255, 255, 0, 0.1);
    border-color: #FFD700;
    text-shadow: 0 0 8px #FFD700, 0 0 15px #FFD700;
    box-shadow: 0 0 15px 5px rgba(255, 215, 0, 0.8);
    transform: scale(1.05);
}}

@media (max-width: 768px) {{
    .nav-links-container {{
        position: fixed; 
        top: 25vh;
        flex-direction: column;
        align-items: center;
        gap: 15px;
        padding: 0 5vw;
    }}
    
    .nav-link {{
        font-size: 4.5vw; 
        width: 80vw;
        text-align: center;
    }}
}}
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- VIDEO INTRO ---
video_placeholder = st.empty()

if not st.session_state.video_ended:
    try:
        html_content_modified = get_intro_html(video_pc_base64, video_mobile_base64, audio_base64, music_files)
        video_placeholder.components.v1.html(html_content_modified, height=1080, scrolling=False)
    except Exception as e:
        st.error(f"Lỗi hiển thị video: {str(e)}")
        st.session_state.video_ended = True

# --- REVEAL GRID ---
grid_cells_html = ""
for i in range(240):	
    grid_cells_html += f'<div class="grid-cell"></div>'

reveal_grid_html = f"""
<div class="reveal-grid">
    {grid_cells_html}
</div>
"""
st.markdown(reveal_grid_html, unsafe_allow_html=True)

# --- TIÊU ĐỀ CHÍNH ---
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

# --- NAV LINKS ---
st.markdown("<div id='top-spacer' style='display: none;'></div>", unsafe_allow_html=True)

st.markdown("""
<div class="nav-links-container">
    <a href="https://www.google.com" target="_blank" class="nav-link">
        Tra cứu Part number 🔎
    </a>
    <a href="https://www.google.com" target="_blank" class="nav-link">
        Ngân hàng trắc nghiệm 🧠
    </a>
</div>
""", unsafe_allow_html=True)

# --- NỘI DUNG BỔ SUNG ---
st.markdown("<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)

# --- THÊM NÚT SKIP VIDEO (CHỈ HIỆN KHI VIDEO ĐANG CHẠY) ---
if not st.session_state.video_ended:
    st.markdown("""
    <style>
    #skip-video-btn {{
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1001;
        background: rgba(255, 215, 0, 0.9);
        color: #000;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: bold;
        transition: all 0.3s ease;
    }}
    #skip-video-btn:hover {{
        background: rgba(255, 255, 0, 1);
        transform: scale(1.05);
    }}
    </style>
    <button id="skip-video-btn" onclick="localStorage.setItem('video_ended', 'true'); window.location.href = window.location.href + '?skip_video=1'">
        ⏩ Bỏ qua video
    </button>
    """, unsafe_allow_html=True)
