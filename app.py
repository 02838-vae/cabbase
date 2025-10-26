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


# --- PHẦN 2: CSS CHÍNH (FIX PLAYER BẰNG ID) ---

# ID của div chứa Player Iframe (sẽ được nhúng bằng st.markdown)
PLAYER_WRAPPER_ID = "music-player-fixed-wrapper" 
# ID của Player Iframe (được tạo bởi st.components.v1.html đầu tiên)
VIDEO_INTRO_IFRAME_SELECTOR = "iframe:first-of-type"


hide_streamlit_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sacramento&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');

/* Ẩn các thành phần mặc định của Streamlit */
#MainMenu, footer, header {{visibility: hidden;}}

.main {{ padding: 0; margin: 0; }}
div.block-container {{ padding: 0; margin: 0; max-width: 100% !important; }}

/* CSS cho iframe video intro */
{VIDEO_INTRO_IFRAME_SELECTOR} {{
    transition: opacity 1s ease-out, visibility 1s ease-out;
    opacity: 1; visibility: visible;
    width: 100vw !important; height: 100vh !important;
    position: fixed; top: 0; left: 0; z-index: 1000;
}}


.video-finished {VIDEO_INTRO_IFRAME_SELECTOR} {{
    opacity: 0; visibility: hidden; pointer-events: none;
    height: 1px !important;    
}}

/* CSS NỀN DÙNG BASE64 (Giữ nguyên) */
.stApp {{
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
}}

/* ... (Các CSS khác giữ nguyên) ... */

/* ======================================================= */
/* === FIX DỨT ĐIỂM CHO PLAYER WRAPPER (Sử dụng ID duy nhất) === */
/* ======================================================= */

#{PLAYER_WRAPPER_ID} {{
    position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
    z-index: 10; 
    
    /* Ẩn Player Iframe Wrapper (Được nhúng bằng st.markdown) */
    opacity: 0 !important; 
    visibility: hidden !important;
    pointer-events: none !important;
    
    /* Dùng transition để hiệu ứng fade-in mượt hơn */
    transition: opacity 1s ease-out, visibility 0s 1s; 
    
    /* Đảm bảo nội dung Player Iframe hiển thị đúng kích thước */
    height: 80px; width: 170px; 
}}

/* Hiển thị khi video kết thúc (class .video-finished được thêm vào .stApp) */
.video-finished #{PLAYER_WRAPPER_ID} {{
    opacity: 1 !important; 
    visibility: visible !important;
    pointer-events: auto !important;
    transition-delay: 0s;
}}

/* Đảm bảo Iframe bên trong cũng không bị Streamlit ghi đè CSS */
#{PLAYER_WRAPPER_ID} iframe {{
    width: 100%; height: 100%;
}}


@media (max-width: 768px) {{
    .stApp.video-finished {{ background-image: var(--main-bg-url-mobile) !important; }}
    #main-title-container {{ height: 8vh; width: 100%; left: 0; }}
    #main-title-container h1 {{ font-size: 6.5vw; animation-duration: 8s; }}
    .reveal-grid {{ grid-template-columns: repeat(10, 1fr); grid-template-rows: repeat(20, 1fr); }}
}}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- PHẦN 3: IFRAME CHO VIDEO INTRO ---

# Giữ nguyên code cho Video Intro

js_callback_video = f"""
<script>
    function sendBackToStreamlit() {{
        const stApp = window.parent.document.querySelector('.stApp');
        
        // CHỈ THÊM MỘT CLASS DUY NHẤT
        stApp.classList.add('video-finished');
        
        // 2. Kích hoạt hiệu ứng reveal
        initRevealEffect();
        
        // 3. KÍCH HOẠT PLAYER: Gửi lệnh chơi
        try {{
            // Sử dụng ID của div wrapper player để tìm iframe bên trong
            const playerIframe = window.parent.document.querySelector('#{PLAYER_WRAPPER_ID} iframe');
            if (playerIframe && playerIframe.contentWindow) {{
                playerIframe.contentWindow.togglePlayPause(true);
            }}
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

        // XỬ LÝ CLICK ĐẦU TIÊN (Quan trọng để kích hoạt media)
        document.body.addEventListener('click', () => {{
            video.play().catch(e => {{}});
            audio.play().catch(e => {{}});
        }}, {{ once: true }});
    }});
</script>
"""

# Mã HTML/CSS cho Video 
intro_title = "KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI"
intro_chars_html = ''.join([
    f'<span class="intro-char">{char}</span>' if char != ' ' else '<span class="intro-char">&nbsp;</span>'  
    for char in intro_title
])
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
    <div id="intro-text-container">{intro_chars_html}</div>
    <video id="intro-video" muted playsinline></video>
    <audio id="background-audio"></audio>
    {js_callback_video}
</body>
</html>
"""

# Hiển thị thành phần HTML (video)
st.components.v1.html(html_content_modified, height=10, scrolling=False)


# --- HIỆU ỨNG REVEAL VÀ NỘI DUNG CHÍNH (Giữ nguyên) ---

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
st.markdown(f"""
<div id="main-title-container">
    <h1>{main_title_text}</h1>
</div>
""", unsafe_allow_html=True)


# =======================================================
#               MUSIC PLAYER TÙY CHỈNH (CHỈ DÙNG MARKDOWN)
# =======================================================

# 1. Tạo Iframe HTML cho Player
custom_music_player_iframe_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        /* CSS CHỈ DÀNH CHO IFRAME CỦA PLAYER */
        body {{ margin: 0; padding: 0; overflow: hidden; background: transparent; font-family: Arial, sans-serif; }}
        .player-container {{ 
            display: none; 
            align-items: center; justify-content: center; padding: 10px; background-color: rgba(0, 0, 0, 0.4); border-radius: 8px; 
            width: 150px; 
            margin: 0 auto; border: 1px solid #FFD700; 
            opacity: 1; 
            transition: all 0.5s ease-in-out;
        }}
        
        /* Dùng class để kích hoạt hiển thị Player bên trong Iframe */
        .player-container.player-visible {{
            display: flex;
        }}
        
        .player-controls button {{ background: none; border: 1px solid #FFD700; color: #FFD700; padding: 8px 10px; margin: 0 3px; border-radius: 5px; cursor: pointer; font-size: 14px; transition: background-color 0.3s, color 0.3s; }}
        .player-controls button:hover {{ background-color: #FFD700; color: #000; }}
        
        #audio-player {{ display: none; }} 
    </style>
</head>
<body>

    <div class="player-container" id="player-main-container">
        <div class="player-controls">
            <button onclick="prevTrack()">&#9664;&#9664;</button>
            <button id="play-pause-btn" onclick="togglePlayPause()">&#9658;</button>
            <button onclick="nextTrack()">&#9658;&#9658;</button>
        </div>
    </div>
    
    <audio id="audio-player"></audio>

    <script>
        const playlistData = {music_playlist_json}; 
        const playlistKeys = Object.keys(playlistData);
        const audio = document.getElementById('audio-player');
        const playPauseBtn = document.getElementById('play-pause-btn');
        const playerMainContainer = document.getElementById('player-main-container'); 
        
        let currentTrackIndex = 0;
        
        function showPlayer() {{ playerMainContainer.classList.add('player-visible'); }}

        function loadTrack(index) {{
            const key = playlistKeys[index];
            const url = playlistData[key]; 
            audio.src = url; 
            audio.load();
        }}
        
        function togglePlayPause(forcePlay = false) {{
            if (audio.paused || forcePlay) {{
                if (audio.src === "") {{ loadTrack(currentTrackIndex); }}
                showPlayer(); 
                audio.play().then(() => {{ playPauseBtn.innerHTML = '&#10074;&#10074;'; }});
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

# 2. Base64 Encode nội dung Iframe để nhúng vào thẻ <iframe>
base64_iframe_content = base64.b64encode(custom_music_player_iframe_content.encode("utf-8")).decode("utf-8")

# 3. Gom thành khối HTML duy nhất, dùng st.markdown
music_player_final_html = f"""
<div id="{PLAYER_WRAPPER_ID}" style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); z-index: 10;">
    <iframe 
        src="data:text/html;base64,{base64_iframe_content}" 
        width="170" 
        height="80" 
        frameborder="0" 
        scrolling="no"
    ></iframe>
</div>
"""

# Nhúng toàn bộ khối Player bằng st.markdown (Không dùng st.components.v1.html nữa)
st.markdown(music_player_final_html, unsafe_allow_html=True)
