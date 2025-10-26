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


# Khởi tạo session state (Không cần thiết cho logic hiện tại nhưng giữ lại)
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


# --- PHẦN 1: NHÚNG FONT BẰNG THẺ LINK TRỰC TIẾP VÀO BODY ---

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

/* BỎ ĐƯỜNG KẺ NGANG PHÍA TRÊN */
.stApp > header,
[data-testid="stHeader"],
header[data-testid="stHeader"] {{
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}}

.main {{ padding: 0; margin: 0; }}
div.block-container {{ padding: 0; margin: 0; max-width: 100% !important; }}

/* CSS cho iframe video intro (iframe:nth-of-type(1)) */
iframe:first-of-type {{
    transition: opacity 1s ease-out, visibility 1s ease-out;
    opacity: 1; visibility: visible;
    width: 100vw !important; height: 100vh !important;
    position: fixed; top: 0; left: 0; z-index: 1000;
}}

.video-finished iframe:first-of-type {{
    opacity: 0; visibility: hidden; pointer-events: none;
    height: 1px !important;    
}}

/* CSS NỀN DÙNG BASE64 - CỐ ĐỊNH */
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

/* KÍCH HOẠT BACKGROUND TRANG CHÍNH */
.stApp.video-finished {{
    background-image: var(--main-bg-url-pc) !important;
    background-size: cover !important;
    background-position: center center !important;
    background-attachment: fixed !important;
    background-repeat: no-repeat !important;
    filter: sepia(60%) grayscale(20%) brightness(85%) contrast(110%) !important;  
    transition: filter 2s ease-out !important;  
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

/* === MUSIC PLAYER (Ẩn hoàn toàn trong Intro, Hiện hoàn toàn trên Trang Chính) === */

/* 🚀 FIX: Thay selector iframe:nth-of-type(3) thành iframe:nth-of-type(2) */
iframe:nth-of-type(2), 
#music-player-container {{
    position: fixed !important; 
    top: 17vh !important;
    left: 2vw !important;
    bottom: auto !important;
    transform: none !important;
    z-index: 10 !important; 
    
    visibility: hidden !important; 
    display: none !important; 
    
    opacity: 0 !important; 
    pointer-events: none !important; 
    
    height: 70px !important; 
    width: 150px !important; 
    transition: opacity 1s ease-out;
}}

/* ẨN DIV wrapper Streamlit */
#music-player-container > div {{
    visibility: hidden !important; 
    display: none !important;
}}

/* KHI VIDEO KẾT THÚC, HIỂN THỊ VÀ BẬT TƯƠNG TÁC */
.video-finished iframe:nth-of-type(2),
.video-finished #music-player-container {{
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important; 
    pointer-events: auto !important; 
}}

.video-finished #music-player-container > div {{
    display: block !important;
    visibility: visible !important;
}}

@media (max-width: 768px) {{
    .stApp.video-finished {{ 
        background-image: var(--main-bg-url-mobile) !important; 
        background-position: center center !important;
    }}
    #main-title-container {{ height: 8vh; width: 100%; left: 0; }}
    #main-title-container h1 {{ font-size: 6.5vw; animation-duration: 8s; }}
    .reveal-grid {{ grid-template-columns: repeat(10, 1fr); grid-template-rows: repeat(20, 1fr); }}
    
    iframe:nth-of-type(2),
    #music-player-container {{
        top: 15vh !important;
        left: 2vw !important;
        width: 130px !important;
        height: 65px !important;
    }}
}}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- PHẦN 3: IFRAME CHO VIDEO INTRO (DÙNG BASE64) ---

js_callback_video = f"""
<script>
    function sendBackToStreamlit() {{
        const stApp = window.parent.document.querySelector('.stApp');
        
        // CHỈ THÊM MỘT CLASS DUY NHẤT để kích hoạt tất cả CSS
        stApp.classList.add('video-finished');
        
        // Kích hoạt hiệu ứng reveal
        initRevealEffect();
        
        // KÍCH HOẠT PLAYER: Gọi hàm play trong iframe của Music Player 
        try {{
            window.parent.document.querySelector('#music-player-container iframe').contentWindow.togglePlayPause(true);
        }} catch(e) {{
            console.warn("Could not auto-play background music player:", e);
        }}
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

        // GÁN DATA URL (BASE64)
        if (isMobile) {{
            video.src = 'data:video/mp4;base64,{video_mobile_base64}';
        }} else {{
            video.src = 'data:video/mp4;base64,{video_pc_base64}';
        }}
        
        audio.src = 'data:audio/mp3;base64,{audio_base64}';

        const playMedia = () => {{
            video.load();
            video.play().catch(e => console.log("Video playback failed on first attempt:", e));
                
            const chars = introTextContainer.querySelectorAll('.intro-char');
            chars.forEach((char, index) => {{
                char.style.animationDelay = `${{index * 0.1}}s`;  
                char.classList.add('char-shown');  
            }});

            audio.volume = 0.5;
            audio.loop = true;  
            // FIX ÂM THANH: Thêm setTimeout để cố gắng phát sau 1 giây
            setTimeout(() => {{
                audio.play().catch(e => {{
                    console.log("Audio playback blocked, setting click listener.");
                }});
            }}, 1000);
        }};
            
        playMedia();
        
        video.onended = () => {{
            video.style.opacity = 0;
            audio.pause();
            audio.currentTime = 0;
            introTextContainer.style.opacity = 0;  
            
            sendBackToStreamlit(); 
        }};

        // XỬ LÝ CLICK ĐẦU TIÊN (Quan trọng để kích hoạt media)
        document.body.addEventListener('click', () => {{
            video.play().catch(e => {{}});
            audio.play().catch(e => {{}}); 
        }}, {{ once: true }});
    }});
</script>
"""

# Mã HTML/CSS cho Video 
html_content_modified = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        html, body {{ margin: 0; padding: 0; overflow: hidden; height: 100vh; width: 100vw; }}
        #intro-video {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: -100; transition: opacity 1s; }}
        #intro-text-container {{ position: fixed; top: 5vh; width: 100%; text-align: center; color: #FFD700; font-size: 3vw; font-family: 'Sacramento', cursive; font-weight: 400; text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.8); z-index: 100; pointer-events: none; display: flex; justify-content: center; opacity: 1; }}
        .intro-char {{ display: inline-block; opacity: 0; transform: translateY(-50px); animation-fill-mode: forwards; animation-duration: 0.8s; animation-timing-function: ease-out; }}
        @keyframes charDropIn {{ from {{ opacity: 0; transform: translateY(-50px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .intro-char.char-shown {{ animation-name: charDropIn; }}
        @media (max-width: 768px) {{ #intro-text-container {{ font-size: 6vw; }} }}
    </style>
</head>
<body>
    <div id="intro-text-container">TỔ BẢO DƯỠNG SỐ 1</div>
    <video id="intro-video" muted playsinline></video>
    <audio id="background-audio"></audio>
    {js_callback_video}
</body>
</html>
"""

# Xử lý nội dung của tiêu đề video intro để thêm hiệu ứng chữ thả
intro_title = "TỔ BẢO DƯỠNG SỐ 1"
intro_chars_html = ''.join([
    f'<span class="intro-char">{char}</span>' if char != ' ' else '<span class="intro-char">&nbsp;</span>'  
    for char in intro_title
])
html_content_modified = html_content_modified.replace(
    "<div id=\"intro-text-container\">TỔ BẢO DƯỠNG SỐ 1</div>",
    f"<div id=\"intro-text-container\">{intro_chars_html}</div>"
)

# IFRAME THỨ 1
st.components.v1.html(html_content_modified, height=800, scrolling=False) 


# --- HIỆU ỨNG REVEAL VÀ NỘI DUNG CHÍNH ---

# Tạo Lưới Reveal (DIV)
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
st.markdown(f"""
<div id="main-title-container">
    <h1>{main_title_text}</h1>
</div>
""", unsafe_allow_html=True)


# =======================================================
#               MUSIC PLAYER TÙY CHỈNH (IFRAME THỨ 2)
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
            padding: 8px 10px; 
            background: linear-gradient(135deg, rgba(0,0,0,0.7) 0%, rgba(30,30,30,0.8) 100%);
            border-radius: 10px; 
            width: 130px;
            margin: 0 auto; 
            border: 2px solid #FFD700;
            box-shadow: 0 3px 12px rgba(255, 215, 0, 0.5);
        }}
        
        .player-controls {{ display: flex; gap: 5px; }}
        
        .player-controls button {{ 
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            border: none;
            color: #000;
            padding: 6px 8px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 0 2px 6px rgba(255, 215, 0, 0.4);
        }}
        
        .player-controls button:hover {{ 
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(255, 215, 0, 0.6);
        }}
        
        .player-controls button:active {{
            transform: translateY(0);
        }}
        
        #play-pause-btn {{
            padding: 6px 10px;
            font-size: 14px;
        }}
        
        #audio-player {{ display: none; }} 
    </style>
</head>
<body>

    <div class="player-container">
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
                    console.error('Lỗi tự động phát:', e);
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
st.components.v1.html(custom_music_player_html, height=70)
st.markdown('</div>', unsafe_allow_html=True)
