import streamlit as st
import base64
import json

# --- THÔNG TIN GITHUB CỦA BẠN (Dùng cho Music Player) ---
GITHUB_USER = "02838-vae" 
GITHUB_REPO = "cabbase"       
GITHUB_BRANCH = "main"        
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/static"
# -----------------------------------------------------------------


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
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Lỗi: Không tìm thấy file media. Vui lòng kiểm tra lại đường dẫn: {e.filename}")


# --- MÃ HÓA CÁC FILE MEDIA (Base64) VÀ TẠO URL GITHUB ---

try:
    # 1. Base64 cho Video, Audio Intro, Ảnh Nền
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg")    
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")

    # 2. GITHUB RAW URL cho Nhạc nền Music Player
    music_files = {
        "background1": f"{GITHUB_RAW_BASE}/background1.mp3",
        "background2": f"{GITHUB_RAW_BASE}/background2.mp3",
        "background3": f"{GITHUB_RAW_BASE}/background3.mp3",
        "background4": f"{GITHUB_RAW_BASE}/background4.mp3",
        "background5": f"{GITHUB_RAW_BASE}/background5.mp3",
        "background6": f"{GITHUB_RAW_BASE}/background6.mp3",
    }
    music_playlist_json = json.dumps(music_files)

except FileNotFoundError as e:
    st.error(e)
    st.stop()


# --- PHẦN 1: NHÚNG FONT ---

font_links = """
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
"""
st.markdown(font_links, unsafe_allow_html=True)


# --- PHẦN 2: CSS CHÍNH (FIX: CHỈ ẨN PLAYER, KHÔNG ẢNH HƯỞNG VIDEO) ---

hide_streamlit_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sacramento&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');

/* Ẩn các thành phần mặc định của Streamlit */
#MainMenu, footer, header {{visibility: hidden;}}

.main {{ padding: 0; margin: 0; }}
div.block-container {{ padding: 0; margin: 0; max-width: 100% !important; }}

/* ========================================== */
/* CSS CHO VIDEO INTRO - Iframe đầu tiên */
/* ========================================== */
#video-intro-iframe iframe {{
    transition: opacity 1s ease-out, visibility 1s ease-out;
    opacity: 1 !important; 
    visibility: visible !important;
    width: 100vw !important; 
    height: 100vh !important;
    position: fixed !important; 
    top: 0 !important; 
    left: 0 !important; 
    z-index: 1000 !important;
    display: block !important;
}}

.video-finished #video-intro-iframe iframe {{
    opacity: 0 !important; 
    visibility: hidden !important; 
    pointer-events: none !important;
    height: 1px !important;
    z-index: -1 !important;
}}

/* CSS NỀN DÙNG BASE64 */
.stApp {{
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
}}

.reveal-grid {{
    position: fixed; top: 0; left: 0;
    width: 100vw; height: 100vh;
    display: grid; grid-template-columns: repeat(20, 1fr);  
    grid-template-rows: repeat(12, 1fr);
    z-index: 500;  pointer-events: none;  
}}

.grid-cell {{ background-color: white; opacity: 1; transition: opacity 0.5s ease-out; }}

/* FIX NỀN TRANG CHÍNH */
.stApp.video-finished .main, 
.stApp.video-finished .block-container,
.stApp.video-finished [data-testid="stVerticalBlock"],
.stApp.video-finished [data-testid="stHorizontalBlock"]
{{
    background-color: transparent !important;
}}

.stApp.video-finished {{
    background-image: var(--main-bg-url-pc) !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
    filter: sepia(60%) grayscale(20%) brightness(85%) contrast(110%) !important;  
    transition: all 2s ease-out; 
}}

/* Keyframes */
@keyframes scrollText {{ 0% {{ transform: translate(100vw, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
@keyframes colorShift {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}

/* === TIÊU ĐỀ TRANG CHÍNH === */
#main-title-container {{
    position: fixed; top: 5vh; left: 0; width: 100%; height: 10vh; overflow: hidden;  z-index: 20;  pointer-events: none; 
    opacity: 0;
    transition: opacity 2s;
}}

.video-finished #main-title-container {{
    opacity: 1 !important; 
}}

#main-title-container h1 {{
    font-family: 'Playfair Display', serif; font-size: 3.5vw; margin: 0; font-weight: 900; letter-spacing: 5px;  white-space: nowrap; display: inline-block;  
    background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3); background-size: 400% 400%; 
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; color: transparent; 
    animation: colorShift 10s ease infinite, scrollText 15s linear infinite; 
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5); 
}}

/* ========================================== */
/* === MUSIC PLAYER - CHỈ ẨN CONTAINER VÀ IFRAME BÊN TRONG === */
/* ========================================== */

/* Trạng thái MẶC ĐỊNH: ẨN HOÀN TOÀN CHỈ PLAYER */
#music-player-container {{
    position: fixed !important; 
    top: 18vh !important;
    left: 50% !important; 
    transform: translateX(-50%) !important;
    z-index: -100 !important;
    
    /* ẨN HOÀN TOÀN */
    opacity: 0 !important;
    visibility: hidden !important;
    display: none !important;
    pointer-events: none !important;
    
    width: 200px;
    height: 80px;
}}

/* Ẩn iframe và các phần tử con của PLAYER */
#music-player-container iframe,
#music-player-container > div {{
    opacity: 0 !important;
    visibility: hidden !important;
    pointer-events: none !important;
}}

/* KHI VIDEO KẾT THÚC: HIỆN PLAYER */
.video-finished #music-player-container {{
    z-index: 20 !important;
    opacity: 1 !important;
    visibility: visible !important;
    display: block !important;
    pointer-events: auto !important;
    transition: opacity 1.5s ease-out 0.5s, visibility 0s 0s;
}}

/* Hiện iframe và các phần tử con của PLAYER */
.video-finished #music-player-container iframe,
.video-finished #music-player-container > div {{
    opacity: 1 !important;
    visibility: visible !important;
    pointer-events: auto !important;
    transition: opacity 1s ease-out 0.5s;
}}

@media (max-width: 768px) {{
    .stApp.video-finished {{ background-image: var(--main-bg-url-mobile) !important; }}
    #main-title-container {{ height: 8vh; width: 100%; left: 0; }}
    #main-title-container h1 {{ font-size: 6.5vw; animation-duration: 8s; }}
    .reveal-grid {{ grid-template-columns: repeat(10, 1fr); grid-template-rows: repeat(20, 1fr); }}
    
    #music-player-container {{
        top: 15vh !important;
        width: 180px;
    }}
}}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- PHẦN 3: IFRAME CHO VIDEO INTRO ---

js_callback_video = f"""
<script>
    function sendBackToStreamlit() {{
        const stApp = window.parent.document.querySelector('.stApp');
        
        // Thêm class để kích hoạt trang chính
        stApp.classList.add('video-finished');
        
        // Kích hoạt hiệu ứng reveal
        initRevealEffect();
        
        // KÍCH HOẠT PLAYER (với delay)
        setTimeout(() => {{
            try {{
                const playerIframe = window.parent.document.querySelector('#music-player-container iframe');
                if (playerIframe && playerIframe.contentWindow && playerIframe.contentWindow.togglePlayPause) {{
                    playerIframe.contentWindow.togglePlayPause(true);
                }}
            }} catch(e) {{
                console.warn("Could not auto-play background music player:", e);
            }}
        }}, 1000);
    }}
    window.sendBackToStreamlit = sendBackToStreamlit; 

    function initRevealEffect() {{
        const revealGrid = window.parent.document.querySelector('.reveal-grid');
        if (!revealGrid) {{ return; }}

        const cells = revealGrid.querySelectorAll('.grid-cell');
        const shuffledCells = Array.from(cells).sort(() => Math.random() - 0.5);

        shuffledCells.forEach((cell, index) => {{
            setTimeout(() => {{ cell.style.opacity = 0; }}, index * 10);
        }});
        
        setTimeout(() => {{ revealGrid.remove(); }}, shuffledCells.length * 10 + 1000);
    }}

    document.addEventListener("DOMContentLoaded", function() {{
        const video = document.getElementById('intro-video');
        const audio = document.getElementById('background-audio');
        const introTextContainer = document.getElementById('intro-text-container');  
        const isMobile = window.innerWidth <= 768;

        if (isMobile) {{
            video.src = 'data:video/mp4;base64,{video_mobile_base64}';
        }} else {{
            video.src = 'data:video/mp4;base64,{video_pc_base64}';
        }}
        
        audio.src = 'data:audio/mp3;base64,{audio_base64}';

        const playMedia = () => {{
            video.load();
            video.play().catch(e => console.log("Video playback failed:", e));
                
            const chars = introTextContainer.querySelectorAll('.intro-char');
            chars.forEach((char, index) => {{
                char.style.animationDelay = `${{index * 0.1}}s`;  
                char.classList.add('char-shown');  
            }});

            audio.volume = 0.5;
            audio.loop = true;  
            audio.play().catch(e => {{
                 console.log("Audio playback blocked, setting click listener.");
            }});
        }};
            
        playMedia();
        
        video.onended = () => {{
            video.style.opacity = 0;
            audio.pause();
            audio.currentTime = 0;
            introTextContainer.style.opacity = 0;  
            
            sendBackToStreamlit(); 
        }};

        document.body.addEventListener('click', () => {{
            video.play().catch(e => {{}});
            audio.play().catch(e => {{}});
        }}, {{ once: true }});
    }});
</script>
"""

html_content_modified = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        html, body {{ margin: 0; padding: 0; overflow: hidden; height: 100vh; width: 100vw; }}
        #intro-video {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: 1; transition: opacity 1s; }}
        #intro-text-container {{ position: fixed; top: 5vh; width: 100%; text-align: center; color: #FFD700; font-size: 3vw; font-family: 'Sacramento', cursive; font-weight: 400; text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.8); z-index: 100; pointer-events: none; display: flex; justify-content: center; opacity: 1; }}
        .intro-char {{ display: inline-block; opacity: 0; transform: translateY(-50px); animation-fill-mode: forwards; animation-duration: 0.8s; animation-timing-function: ease-out; }}
        @keyframes charDropIn {{ from {{ opacity: 0; transform: translateY(-50px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .intro-char.char-shown {{ animation-name: charDropIn; }}
        @media (max-width: 768px) {{ #intro-text-container {{ font-size: 6vw; }} }}
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

intro_title = "KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI"
intro_chars_html = ''.join([
    f'<span class="intro-char">{char}</span>' if char != ' ' else '<span class="intro-char">&nbsp;</span>'  
    for char in intro_title
])
html_content_modified = html_content_modified.replace(
    "<div id=\"intro-text-container\">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>",
    f"<div id=\"intro-text-container\">{intro_chars_html}</div>"
)

# Wrap video intro trong div có ID
st.markdown('<div id="video-intro-iframe">', unsafe_allow_html=True)
st.components.v1.html(html_content_modified, height=10, scrolling=False)
st.markdown('</div>', unsafe_allow_html=True)


# --- HIỆU ỨNG REVEAL ---

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


# =======================================================
#               MUSIC PLAYER TÙY CHỈNH
# =======================================================

custom_music_player_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ margin: 0; padding: 0; overflow: hidden; background: transparent; font-family: Arial, sans-serif; }}
        .player-container {{ 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            padding: 12px 15px; 
            background: linear-gradient(135deg, rgba(0,0,0,0.6) 0%, rgba(30,30,30,0.7) 100%);
            border-radius: 12px; 
            width: 180px;
            margin: 0 auto; 
            border: 2px solid #FFD700;
            box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
        }}
        
        .player-controls {{ display: flex; gap: 8px; }}
        
        .player-controls button {{ 
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            border: none;
            color: #000;
            padding: 10px 12px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(255, 215, 0, 0.4);
        }}
        
        .player-controls button:hover {{ 
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 215, 0, 0.6);
        }}
        
        .player-controls button:active {{
            transform: translateY(0);
        }}
        
        #play-pause-btn {{
            padding: 10px 16px;
            font-size: 18px;
        }}
        
        #audio-player {{ display: none; }} 
    </style>
</head>
<body>

    <div class="player-container" id="player-main-container">
        <div class="player-controls">
            <button onclick="prevTrack()" title="Bài trước">&#9664;&#9664;</button>
            <button id="play-pause-btn" onclick="togglePlayPause()" title="Phát/Dừng">&#9658;</button>
            <button onclick="nextTrack()" title="Bài sau">&#9658;&#9658;</button>
        </div>
    </div>
    
    <audio id="audio-player"></audio>

    <script>
        const playlistData = {music_playlist_json}; 
        const playlistKeys = Object.keys(playlistData);
        const audio = document.getElementById('audio-player');
        const playPauseBtn = document.getElementById('play-pause-btn');
        
        let currentTrackIndex = 0;

        function loadTrack(index) {{
            const key = playlistKeys[index];
            const url = playlistData[key]; 
            audio.src = url; 
            audio.load();
        }}
        
        function togglePlayPause(forcePlay = false) {{
            if (audio.paused || forcePlay) {{
                if (audio.src === "") {{ loadTrack(currentTrackIndex); }}
                
                audio.play().then(() => {{
                    playPauseBtn.innerHTML = '&#10074;&#10074;'; 
                }}).catch(e => {{
                    console.error('Lỗi tự động phát (Chặn Autoplay):', e);
                }});
            }} else {{
                audio.pause();
                playPauseBtn.innerHTML = '&#9658;'; 
            }}
        }}
        window.togglePlayPause = togglePlayPause; 

        function nextTrack() {{
            currentTrackIndex = (currentTrackIndex + 1) % playlistKeys.length;
            loadTrack(currentTrackIndex);
            if (!audio.paused) {{ audio.play(); }}
        }}

        function prevTrack() {{
            currentTrackIndex = (currentTrackIndex - 1 + playlistKeys.length) % playlistKeys.length;
            loadTrack(currentTrackIndex);
            if (!audio.paused) {{ audio.play(); }}
        }}

        audio.addEventListener('ended', nextTrack);

        document.addEventListener("DOMContentLoaded", function() {{
            loadTrack(currentTrackIndex);
        }});
    </script>
</body>
</html>
"""

# Tạo container HTML cho Music Player
st.markdown('<div id="music-player-container">', unsafe_allow_html=True)
st.components.v1.html(custom_music_player_html, height=80)
st.markdown('</div>', unsafe_allow_html=True)
