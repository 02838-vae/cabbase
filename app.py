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
    if not os.path.exists(file_path):
        print(f"❌ File không tồn tại: {file_path}")
        return None
    if os.path.getsize(file_path) == 0:
        print(f"❌ File rỗng: {file_path}")
        return None
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        encoded = base64.b64encode(data).decode("utf-8")
        print(f"✅ Đã mã hóa file: {file_path} ({len(encoded)} ký tự)")
        return encoded
    except Exception as e:
        print(f"❌ Lỗi khi đọc file {file_path}: {str(e)}")
        return None


# Mã hóa các file media chính (bắt buộc)
try:
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
    logo_base64 = get_base64_encoded_file("logo.jpg")

    if not all([video_pc_base64, video_mobile_base64, audio_base64, bg_pc_base64, bg_mobile_base64]):
        missing_files = []
        if not video_pc_base64: missing_files.append("airplane.mp4")
        if not video_mobile_base64: missing_files.append("mobile.mp4")
        if not audio_base64: missing_files.append("plane_fly.mp3")
        if not bg_pc_base64: missing_files.append("cabbase.jpg")
        if not bg_mobile_base64: missing_files.append("mobile.jpg")
        
        st.error(f"⚠️ Thiếu các file media cần thiết hoặc file rỗng:")
        for f in missing_files:
            st.write(f"- {f}")
        st.stop()
        
except Exception as e:
    st.error(f"❌ Lỗi khi đọc file: {str(e)}")
    st.stop()

if not logo_base64:
    logo_base64 = "" 


# ===== PHẦN QUAN TRỌNG: MÃ HÓA CÁC FILE NHẠC NỀN =====
print("\n🎵 Đang tìm kiếm file nhạc nền...")
music_files = []

# Thử nhiều pattern tên file khác nhau
patterns_to_try = [
    "background{}.mp3",  # background1.mp3, background2.mp3, ...
    "Background{}.mp3",  # Background1.mp3 (chữ B hoa)
    "music{}.mp3",       # music1.mp3, music2.mp3, ...
    "song{}.mp3",        # song1.mp3, song2.mp3, ...
]

for pattern in patterns_to_try:
    for i in range(1, 10):  # Thử từ 1-9
        filename = pattern.format(i)
        music_base64 = get_base64_encoded_file(filename)
        if music_base64:
            music_files.append(music_base64)
            print(f"✅ Đã tải: {filename}")

# Hiển thị thông tin debug
if len(music_files) == 0:
    print("\n❌ KHÔNG TÌM THẤY FILE NHẠC NÀO!")
    print("📁 Các file trong thư mục hiện tại:")
    for item in os.listdir("."):
        if item.endswith((".mp3", ".MP3")):
            print(f"   - {item}")
    
    st.warning(f"""
    ⚠️ **Không tìm thấy file nhạc nền!**
    
    Vui lòng đặt file MP3 vào cùng thư mục với script này và đặt tên theo format:
    - `background1.mp3`, `background2.mp3`, ... hoặc
    - `music1.mp3`, `music2.mp3`, ... hoặc  
    - `song1.mp3`, `song2.mp3`, ...
    
    Các file MP3 hiện có trong thư mục: {[f for f in os.listdir('.') if f.endswith(('.mp3', '.MP3'))]}
    """)
else:
    print(f"\n✅ ĐÃ TẢI THÀNH CÔNG {len(music_files)} FILE NHẠC!")
    st.success(f"✅ Đã tải {len(music_files)} bài nhạc nền")


# --- PHẦN 1: NHÚNG FONT VÀ CSS CHUNG ---
font_links = """
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Electrolize&display=swap" rel="stylesheet">
"""
st.markdown(font_links, unsafe_allow_html=True)

# CSS (Giữ nguyên - không thay đổi)
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
        border-color: #00ffff;
        box-shadow: 0 0 5px #00ffff, 0 0 10px #00ffff;
    }}
    50% {{
        border-color: #00ccff;
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

.content-links-container {{
    position: fixed; 
    top: 30vh; 
    width: 100%;
    z-index: 10; 
    display: flex;
    justify-content: space-between; 
    align-items: flex-start;
    padding: 0 0; 
    box-sizing: border-box; 
    pointer-events: none; 
    opacity: 0; 
    transition: opacity 2s ease-out 3s; 
}}

.video-finished .content-links-container {{
    opacity: 1;
    pointer-events: auto; 
}}

#link-part-number {{
    margin-right: auto; 
    margin-left: 8vw;    
}}

#link-quiz-bank {{
    margin-left: auto; 
    margin-right: 8vw;   
}}

.container-link {{
    display: inline-block;
    padding: 10px 15px; 
    text-align: center;
    text-decoration: none; 
    color: #00ffff; 
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem; 
    font-weight: 700;
    cursor: pointer;
    background-color: rgba(0, 0, 0, 0.4); 
    border: 2px solid #00ffff; 
    border-radius: 8px; 
    box-sizing: border-box; 
    text-shadow:
      0 0 4px rgba(0, 255, 255, 0.8), 
      0 0 10px rgba(34, 141, 255, 0.6); 
    box-shadow: 0 0 5px #00ffff, 0 0 15px rgba(0, 255, 255, 0.5); 
    transition: transform 0.3s ease, color 0.3s ease, text-shadow 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}}

.container-link:hover {{
    transform: scale(1.05); 
    color: #ffd700; 
    border-color: #ffd700; 
    box-shadow: 
      0 0 5px #ffd700, 
      0 0 15px #ff8c00, 
      0 0 25px rgba(255, 215, 0, 0.7); 
    text-shadow: 
      0 0 3px #ffd700, 
      0 0 8px #ff8c00; 
}}

@media (max-width: 768px) {{
    .content-links-container {{
        position: fixed; 
        top: 45vh; 
        flex-direction: column; 
        align-items: center; 
        padding: 0 5vw; 
        width: 100%;
    }}

    #link-part-number, #link-quiz-bank {{
        margin: 10px 0;
    }}
    
    .container-link {{
        font-size: 1.2rem; 
        width: auto; 
        max-width: 90%; 
        padding: 8px 12px; 
    }}
    
    .container-link:hover {{
        transform: scale(1.03); 
    }}
}}
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- PHẦN 3: MÃ HTML/CSS/JavaScript IFRAME CHO VIDEO INTRO ---

# Tạo danh sách music sources cho JavaScript - FIX QUAN TRỌNG
if len(music_files) > 0:
    music_sources_js = ",\n        ".join([f"'data:audio/mp3;base64,{music}'" for music in music_files])
else:
    music_sources_js = "''"  # Cung cấp giá trị mặc định để tránh lỗi syntax

# JavaScript với logging chi tiết hơn
js_callback_video = f"""
<script>
    console.log("🎬 Script loaded");
    console.log("🎵 Number of music files available: {len(music_files)}");
    
    function sendBackToStreamlit() {{
        console.log("✅ Video ended, revealing main content");
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
        console.log("🎵 Initializing music player...");
        
        const musicSources = [{music_sources_js}];
        console.log("📋 Music sources array length:", musicSources.length);
        
        const playPauseBtn = window.parent.document.getElementById('play-pause-btn');
        const prevBtn = window.parent.document.getElementById('prev-btn');
        const nextBtn = window.parent.document.getElementById('next-btn');
        const progressBar = window.parent.document.getElementById('progress-bar');
        const progressContainer = window.parent.document.getElementById('progress-container');
        const currentTimeEl = window.parent.document.getElementById('current-time');
        const durationEl = window.parent.document.getElementById('duration');
        
        if (!playPauseBtn || !prevBtn || !nextBtn) {{
            console.error("❌ Music player elements not found!");
            return;
        }}
        
        if (musicSources.length === 0 || musicSources[0] === '') {{
             console.warn("⚠️ No music files available!");
             durationEl.textContent = 'N/A';
             playPauseBtn.textContent = '❌';
             playPauseBtn.style.pointerEvents = 'none';
             prevBtn.style.pointerEvents = 'none';
             nextBtn.style.pointerEvents = 'none';
             playPauseBtn.style.opacity = '0.5';
             prevBtn.style.opacity = '0.5';
             nextBtn.style.opacity = '0.5';
             return; 
        }}
        
        console.log("✅ Music player elements found, creating Audio object...");
        
        let currentTrack = 0;
        const audio = new Audio();
        audio.volume = 0.3;
        
        function loadTrack(index) {{
            console.log("📀 Loading track #" + (index + 1) + "...");
            audio.src = musicSources[index];
            audio.load();
            console.log("✅ Track loaded, src length:", audio.src.length);
        }}
        
        function togglePlayPause() {{
            console.log("🎵 Toggle play/pause clicked. Current paused state:", audio.paused);
            
            if (!audio.paused) {{
                audio.pause();
                playPauseBtn.textContent = '▶';
                console.log("⏸️ Music paused");
            }} else {{
                if (!audio.src || audio.src === '') {{
                    console.log("⚠️ No source, loading track 0...");
                    loadTrack(currentTrack);
                }}

                console.log("▶️ Attempting to play...");
                audio.play().then(() => {{
                    playPauseBtn.textContent = '⏸';
                    console.log("✅ Music playing successfully!");
                }}).catch(e => {{
                    console.error("❌ Play failed:", e);
                    alert("❌ Lỗi phát nhạc: " + e.message + "\\n\\nVui lòng kiểm tra:\\n1. File MP3 có đúng format không?\\n2. File có bị lỗi không?\\n3. Xem console log để biết chi tiết");
                    playPauseBtn.textContent = '▶';
                }});
            }}
        }}
        
        function nextTrack() {{
            currentTrack = (currentTrack + 1) % musicSources.length;
            console.log("⏭️ Next track:", currentTrack + 1);
            loadTrack(currentTrack);
            if (!audio.paused) {{
                audio.play().catch(e => console.error("Next track play error:", e));
            }}
        }}
        
        function prevTrack() {{
            currentTrack = (currentTrack - 1 + musicSources.length) % musicSources.length;
            console.log("⏮️ Previous track:", currentTrack + 1);
            loadTrack(currentTrack);
            if (!audio.paused) {{
                audio.play().catch(e => console.error("Prev track play error:", e));
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
            console.log("📊 Duration loaded:", audio.duration + "s");
        }});
        
        audio.addEventListener('ended', () => {{
            console.log("🔚 Track ended, playing next...");
            nextTrack();
        }});
        
        audio.addEventListener('error', (e) => {{
            console.error("❌ Audio error event:", e);
            console.error("Error code:", audio.error ? audio.error.code : 'unknown');
            console.error("Error message:", audio.error ? audio.error.message : 'unknown');
        }});
        
        playPauseBtn.addEventListener('click', togglePlayPause);
        nextBtn.addEventListener('click', nextTrack);
        prevBtn.addEventListener('click', prevTrack);
        
        progressContainer.addEventListener('click', (e) => {{
            if (audio.duration) {{
                const rect = progressContainer.getBoundingClientRect();
                const percent = (e.clientX - rect.left) / rect.width;
                audio.currentTime = percent * audio.duration;
            }}
        }});
        
        loadTrack(0);
        console.log("✅ Music player fully initialized!");
    }}

    document.addEventListener("DOMContentLoaded", function() {{
        const waitForElements = setInterval(() => {{
            const video = document.getElementById('intro-video');
            const audio = document.getElementById('background-audio');
            const introTextContainer = document.getElementById('intro-text-container');
            
            if (video && audio && introTextContainer) {{
                clearInterval(waitForElements);
                
                const isMobile = window.innerWidth <= 768;
                const videoSource = isMobile ? 'data:video/mp4;base64,{video_mobile_base64}' : 'data:video/mp4;base64,{video_pc_base64}';

                video.src = videoSource;
                audio.src = 'data:audio/mp3;base64,{audio_base64}';

                const tryToPlay = () => {{
                    video.play().catch(err => {{
                        console.error("Video play failed:", err);
                        setTimeout(sendBackToStreamlit, 2000);	
                    }});
                    audio.play().catch(e => {{
                        console.log("Audio autoplay blocked (normal).");
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
                    console.error("Video error detected. Skipping intro.", e);
                    sendBackToStreamlit();
                }});


                const clickHandler = () => {{
                    tryToPlay();
                    document.removeEventListener('click', clickHandler);
                    document.removeEventListener('touchstart', clickHandler);
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


# --- MUSIC PLAYER ---
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
