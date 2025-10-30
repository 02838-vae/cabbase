import streamlit as st
import base64
import os

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
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return None
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    except Exception as e:
        st.error(f"Lỗi khi đọc file {file_path}: {str(e)}")
        return None


# Mã hóa các file media chính (bắt buộc)
try:
    # Đảm bảo các file này nằm cùng thư mục với app.py
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
    
    # MÃ HÓA CHO LOGO
    logo_base64 = get_base64_encoded_file("logo.jpg")

    # Kiểm tra file bắt buộc
    if not all([video_pc_base64, video_mobile_base64, audio_base64, bg_pc_base64, bg_mobile_base64]):
        missing_files = []
        if not video_pc_base64: missing_files.append("airplane.mp4")
        if not video_mobile_base64: missing_files.append("mobile.mp4")
        if not audio_base64: missing_files.append("plane_fly.mp3")
        if not bg_pc_base64: missing_files.append("cabbase.jpg")
        if not bg_mobile_base64: missing_files.append("mobile.jpg")
        
        st.error(f"⚠️ Thiếu các file media cần thiết hoặc file rỗng. Vui lòng kiểm tra lại các file sau trong thư mục:")
        st.write(" - " + "\n - ".join(missing_files))
        st.stop()
        
except Exception as e:
    st.error(f"❌ Lỗi khi đọc file: {str(e)}")
    st.stop()

# Đảm bảo logo_base64 được khởi tạo nếu file không tồn tại
if not 'logo_base64' in locals() or not logo_base64:
    logo_base64 = "" 
    st.info("ℹ️ Không tìm thấy file logo.jpg. Music player sẽ không có hình nền logo.")


# Mã hóa các file nhạc nền (không bắt buộc)
music_files = []
for i in range(1, 7):
    music_base64 = get_base64_encoded_file(f"background{i}.mp3")
    if music_base64:
        music_files.append(music_base64)

if len(music_files) == 0:
    st.info("ℹ️ Không tìm thấy file nhạc nền (background1.mp3 - background6.mp3). Music player sẽ không hoạt động.")


# --- PHẦN 1: NHÚNG FONT BẰNG THẺ LINK TRỰC TIẾP VÀO BODY ---
font_links = """
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Electrolize&display=swap" rel="stylesheet">
"""
st.markdown(font_links, unsafe_allow_html=True)

# --- PHẦN 2: CSS CHÍNH (STREAMLIT APP) ---
hide_streamlit_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sacramento&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Electrolize&display=swap');

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


/* --- KEYFRAMES NEON (Dành cho Music Player) --- */
@keyframes neon-border-pulse {{
    0%, 100% {{
        border-color: #00ffff; /* Cyan */
        box-shadow: 0 0 5px #00ffff, 0 0 10px #00ffff;
    }}
    50% {{
        border-color: #00ccff; /* Blue/Cyan nhẹ hơn */
        box-shadow: 0 0 2px #00ccff, 0 0 5px #00ccff;
    }}
}}

/* --- MUSIC PLAYER STYLES --- */
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
    position: fixed;	
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
    border: 3px solid #00ffff;
    animation: neon-border-pulse 4s infinite alternate;
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

/* --- CSS MỚI CHO 2 TIÊU ĐỀ PHỤ - ĐÃ THÊM VIỀN BAO VÀ CHỈNH VỊ TRÍ PC --- */
.content-links-container {{
    position: fixed; 
    top: 20vh; 
    width: 100%;
    z-index: 10; 
    display: flex;
    justify-content: space-between; 
    align-items: flex-start;
    padding: 0 15vw; /* Đảm bảo PC nằm sâu hai bên */
    pointer-events: none; 
    opacity: 0; 
    transition: opacity 2s ease-out 3s; 
}}

.video-finished .content-links-container {{
    opacity: 1;
    pointer-events: auto; 
}}

.container-link {{
    /* Vị trí và chữ */
    display: inline-block;
    padding: 10px 15px; /* Giảm padding ngang để khung nhỏ lại */
    margin: 0;
    text-align: center;
    text-decoration: none; 
    
    color: #00ffff; 
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem; 
    font-weight: 700;
    cursor: pointer;
    background-color: rgba(0, 0, 0, 0.4); /* Thêm nền nhẹ cho dễ thấy khung */
    
    /* Thiết lập khung viền */
    border: 2px solid #00ffff; /* Viền Neon Cyan */
    border-radius: 8px; /* Bo góc mềm mại */
    box-sizing: border-box; 
    
    /* Neon Glow Tĩnh */
    text-shadow:
      0 0 4px rgba(0, 255, 255, 0.8), 
      0 0 10px rgba(34, 141, 255, 0.6); 
      
    /* Thêm Box Shadow cho khung (Neon effect) */
    box-shadow: 0 0 5px #00ffff, 0 0 15px rgba(0, 255, 255, 0.5); 
    
    transition: transform 0.3s ease, color 0.3s ease, text-shadow 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}}

.container-link:hover {{
    transform: scale(1.05); 
    color: #ffd700; /* Màu vàng kim khi hover */
    border-color: #ffd700; /* Viền đổi màu vàng khi hover */
    
    /* Box Shadow Vàng khi hover */
    box-shadow: 
      0 0 5px #ffd700, 
      0 0 15px #ff8c00, 
      0 0 25px rgba(255, 215, 0, 0.7); 
      
    /* Text Shadow Vàng khi hover (đã fix lỗi lóa) */
    text-shadow: 
      0 0 3px #ffd700, 
      0 0 8px #ff8c00; 
}}

/* --- MEDIA QUERY CHO MOBILE --- */
@media (max-width: 768px) {{
    .content-links-container {{
        position: fixed; 
        top: 45vh; 
        flex-direction: column; 
        align-items: center; 
        padding: 0 5vw; 
        width: 100%;
    }}
    
    .container-link {{
        font-size: 1.2rem; /* Giảm size để mobile dễ chứa */
        width: auto; 
        max-width: 90%; 
        margin: 10px 0; 
        padding: 8px 12px; 
    }}
    
    .container-link:hover {{
        transform: scale(1.03); 
    }}
}}
</style>
"""

# Thêm CSS vào trang chính
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- PHẦN 3: MÃ HTML/CSS/JavaScript IFRAME CHO VIDEO INTRO (GIỮ NGUYÊN) ---

# Tạo danh sách music sources cho JavaScript 
if len(music_files) > 0:
    music_sources_js = ",\n        ".join([f"'data:audio/mp3;base64,{music}'" for music in music_files])
else:
    music_sources_js = ""

# JavaScript (GIỮ NGUYÊN)
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
            console.error("Music player elements not found in parent document");
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
        console.log("Music player initialized successfully");
    }}

    document.addEventListener("DOMContentLoaded", function() {{
        console.log("DOM loaded, waiting for elements...");
        
        const waitForElements = setInterval(() => {{
            const video = document.getElementById('intro-video');
            const audio = document.getElementById('background-audio');
            const introTextContainer = document.getElementById('intro-text-container');
            
            if (video && audio && introTextContainer) {{
                clearInterval(waitForElements);
                console.log("All elements found, initializing...");
                
                const isMobile = window.innerWidth <= 768;
                const videoSource = isMobile ? 'data:video/mp4;base64,{video_mobile_base64}' : 'data:video/mp4;base64,{video_pc_base64}';

                video.src = videoSource;
                audio.src = 'data:audio/mp3;base64,{audio_base64}';

                console.log("Video/Audio source set. Loading metadata...");
                
                // --- LOGIC CHƠI VIDEO/AUDIO ĐƯỢC CẢI TIẾN ---
                
                const tryToPlay = () => {{
                    console.log("Attempting to play video (User interaction or Canplay event)");
                    
                    // 1. Thử phát video (còn muted)
                    video.play().then(() => {{
                        console.log("✅ Video is playing!");
                    }}).catch(err => {{
                        // Thất bại lần 2 (ngay cả sau tương tác). Có thể do lỗi tệp.
                        console.error("❌ Still can't play video, skipping intro (Error/File issue):", err);
                        
                        // Nếu không thể phát, chuyển sang nội dung chính sau 2 giây
                        setTimeout(sendBackToStreamlit, 2000);	
                    }});

                    // 2. Thử phát audio (có thể bị chặn)
                    audio.play().catch(e => {{
                        console.log("Audio autoplay blocked (normal), waiting for video end.");
                    }});
                }};

                // Lắng nghe sự kiện video sẵn sàng (đáng tin cậy hơn)
                video.addEventListener('canplaythrough', tryToPlay, {{ once: true }});
                
                // Event khi video kết thúc
                video.addEventListener('ended', () => {{
                    console.log("Video ended, transitioning...");
                    video.style.opacity = 0;
                    audio.pause();
                    audio.currentTime = 0;
                    introTextContainer.style.opacity = 0;	
                    setTimeout(sendBackToStreamlit, 500);
                }});

                // Xử lý lỗi tệp video (RẤT QUAN TRỌNG VỚI BASE64)
                video.addEventListener('error', (e) => {{
                    console.error("Video error detected (Codec/Base64/File corrupted). Skipping intro:", e);
                    sendBackToStreamlit();
                }});


                // Click/Touch handler để kích hoạt 'tryToPlay' nếu Autoplay bị chặn
                const clickHandler = () => {{
                    console.log("User interaction detected, forcing play attempt.");
                    tryToPlay();
                    // Xóa listener sau lần tương tác đầu tiên
                    document.removeEventListener('click', clickHandler);
                    document.removeEventListener('touchstart', clickHandler);
                }};
                
                document.addEventListener('click', clickHandler, {{ once: true }});
                document.addEventListener('touchstart', clickHandler, {{ once: true }});
                
                // Load video
                video.load();	
                
                // Animate text
                const chars = introTextContainer.querySelectorAll('.intro-char');
                chars.forEach((char, index) => {{
                    char.style.animationDelay = `${{index * 0.1}}s`;	
                    char.classList.add('char-shown');	
                }});
            }}
        }}, 100);
        
        // Timeout sau 5 giây (nếu video không load được)
        setTimeout(() => {{
            clearInterval(waitForElements);
            const video = document.getElementById('intro-video');
            if (video && !video.src) {{
                console.warn("Timeout before video source set. Force transitioning to main content.");
                sendBackToStreamlit();
            }}
        }}, 5000);
    }});
</script>
"""

# Mã HTML/CSS cho Video
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

# Xử lý nội dung của tiêu đề video intro để thêm hiệu ứng chữ thả
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


# --- HIỆU ỨNG REVEAL VÀ NỘI DUNG CHÍNH ---

# Tạo Lưới Reveal
grid_cells_html = ""
for i in range(240):	
    grid_cells_html += f'<div class="grid-cell"></div>'

reveal_grid_html = f"""
<div class="reveal-grid">
    {grid_cells_html}
</div>
"""
st.markdown(reveal_grid_html, unsafe_allow_html=True)


# --- NỘI DUNG CHÍNH (TIÊU ĐỀ ĐƠN, ĐỔI MÀU) ---
main_title_text = "TỔ BẢO DƯỠNG SỐ 1"	

# Nhúng tiêu đề chính
st.markdown(f"""
<div id="main-title-container">
    <h1>{main_title_text}</h1>
</div>
""", unsafe_allow_html=True)


# --- THÊM 2 TIÊU ĐỀ PHỤ VỚI STYLE ĐÃ CHỈNH SỬA ---
st.markdown("""
<div class="content-links-container">
    <a href="#" class="container-link" id="link-part-number">
        Tra cứu part number 🔍
    </a>
    <a href="#" class="container-link" id="link-quiz-bank">
        Ngân hàng trắc nghiệm 📋✅
    </a>
</div>
""", unsafe_allow_html=True)


# --- MUSIC PLAYER (GIỮ NGUYÊN) ---
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

# Thêm nội dung chính của ứng dụng 
st.markdown("<h2 style='text-align: center; color: white; opacity: 0; transition: opacity 2s 3s;'>Nội dung chính của Trang (sẽ xuất hiện bên dưới)</h2>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: white; opacity: 0; transition: opacity 2s 3s;'>Khu vực này sẽ xuất hiện sau 3 giây</h2>", unsafe_allow_html=True)
