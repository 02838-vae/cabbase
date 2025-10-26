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
        # FileNotFoundError được handle ở khối try...except chính
        raise FileNotFoundError(f"Lỗi: Không tìm thấy file media. Vui lòng kiểm tra lại đường dẫn: {e.filename}")


# --- MÃ HÓA CÁC FILE MEDIA (Base64) VÀ TẠO URL GITHUB ---

try:
    # 1. Base64 cho Video, Audio Intro, Ảnh Nền (Ổn định cho các file này)
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg")    
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")

    # 2. GITHUB RAW URL cho Nhạc nền Music Player (Ổn định trên Streamlit Cloud)
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


# --- PHẦN 1: NHÚNG FONT VÀ NÚT BỎ QUA ---

font_links = """
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
"""
st.markdown(font_links, unsafe_allow_html=True)

# Nút Bỏ qua 
st.markdown(
    """
    <button 
        id="skip-intro-btn" 
        onclick="window.parent.document.querySelector('iframe:first-of-type').contentWindow.sendBackToStreamlit(); 
                 this.style.display='none';"
    >
        Bỏ qua Intro >>
    </button>
    """,
    unsafe_allow_html=True
)

# --- PHẦN 2: CSS CHÍNH (STREAMLIT APP) ---

hide_streamlit_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sacramento&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');

/* Ẩn các thành phần mặc định của Streamlit */
#MainMenu, footer, header {{visibility: hidden;}}

/* CSS cho Nút Bỏ qua */
#skip-intro-btn {{
    position: fixed; top: 20px; right: 20px; z-index: 1001;
    background-color: rgba(255, 215, 0, 0.7); color: #000;
    border: none; padding: 10px 20px; border-radius: 5px;
    cursor: pointer; font-weight: bold;
}}

/* Ẩn nút Bỏ qua khi video đã kết thúc */
.video-finished #skip-intro-btn {{
    display: none !important;
}}

.main {{ padding: 0; margin: 0; }}
div.block-container {{ padding: 0; margin: 0; max-width: 100% !important; }}

/* CSS cho iframe video intro */
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


.main-content-revealed {{
    background-image: var(--main-bg-url-pc);
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    filter: sepia(60%) grayscale(20%) brightness(85%) contrast(110%);  
    transition: filter 2s ease-out;  
}}


/* Keyframes cho hiệu ứng chữ chạy đơn (từ phải sang trái, lặp lại) */
@keyframes scrollText {{ 0% {{ transform: translate(100vw, 0); }} 100% {{ transform: translate(-100%, 0); }} }}

/* Keyframes cho hiệu ứng Đổi Màu Gradient */
@keyframes colorShift {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}

/* === TIÊU ĐỀ TRANG CHÍNH === */
#main-title-container {{
    position: fixed; top: 5vh; left: 0; width: 100%; height: 10vh; overflow: hidden;  z-index: 20;  pointer-events: none; opacity: 0; transition: opacity 2s;
}}

#main-title-container h1 {{
    font-family: 'Playfair Display', serif; font-size: 3.5vw; margin: 0; font-weight: 900; letter-spacing: 5px;  white-space: nowrap; display: inline-block;  
    background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3); background-size: 400% 400%; 
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; color: transparent; 
    animation: colorShift 10s ease infinite, scrollText 15s linear infinite; 
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5); 
}}

/* === MUSIC PLAYER (MỚI) === */
#music-player-container {{
    position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
    z-index: 10; 
    opacity: 0; 
    transition: opacity 1s ease-out;
    pointer-events: none; 
    height: 80px; width: 350px; 
}}
.video-finished #music-player-container {{
    opacity: 1; 
    pointer-events: auto;
}}


@media (max-width: 768px) {{
    .main-content-revealed {{ background-image: var(--main-bg-url-mobile); }}
    #main-title-container {{ height: 8vh; width: 100%; left: 0; }}
    #main-title-container h1 {{ font-size: 6.5vw; animation-duration: 8s; }}
    .reveal-grid {{ grid-template-columns: repeat(10, 1fr); grid-template-rows: repeat(20, 1fr); }}
}}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- PHẦN 3: IFRAME CHO VIDEO INTRO (DÙNG BASE64) ---

# JavaScript (Đã thêm logic play nhạc nền player khi chuyển cảnh)
js_callback_video = f"""
<script>
    function sendBackToStreamlit() {{
        window.parent.document.querySelector('.stApp').classList.add('video-finished', 'main-content-revealed');
        initRevealEffect();
        
        // Cố gắng tự động play nhạc nền khi chuyển cảnh
        try {{
            // Gọi hàm togglePlayPause trong iframe của Music Player
            window.parent.document.querySelector('#music-player-container iframe').contentWindow.togglePlayPause(true);
        }} catch(e) {{
            console.warn("Could not auto-play background music player:", e);
        }}
    }}
    window.sendBackToStreamlit = sendBackToStreamlit; 

    
    function initRevealEffect() {{
        const revealGrid = window.parent.document.querySelector('.reveal-grid');
        const mainTitle = window.parent.document.getElementById('main-title-container');

        if (mainTitle) {{ mainTitle.style.opacity = 1; }}

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

# Mã HTML/CSS cho Video (Giữ nguyên)
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

# Hiển thị thành phần HTML (video)
st.components.v1.html(html_content_modified, height=10, scrolling=False)


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
st.markdown(f"""
<div id="main-title-container">
    <h1>{main_title_text}</h1>
</div>
""", unsafe_allow_html=True)


# =======================================================
#               MUSIC PLAYER TÙY CHỈNH (DÙNG GITHUB RAW URL)
# =======================================================

custom_music_player_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        /* CSS CHỈ DÀNH CHO IFRAME CỦA PLAYER */
        body {{ margin: 0; padding: 0; overflow: hidden; background: transparent; font-family: Arial, sans-serif; }}
        .player-container {{ display: flex; align-items: center; justify-content: center; padding: 10px; background-color: rgba(0, 0, 0, 0.4); border-radius: 8px; width: 300px; margin: 0 auto; border: 1px solid #FFD700; }}
        
        .player-controls button {{ background: none; border: 1px solid #FFD700; color: #FFD700; padding: 8px 10px; margin: 0 3px; border-radius: 5px; cursor: pointer; font-size: 14px; transition: background-color 0.3s, color 0.3s; }}
        .player-controls button:hover {{ background-color: #FFD700; color: #000; }}
        
        #track-name {{ color: white; font-size: 12px; margin: 0 10px; width: 80px; text-align: center; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }}
        #audio-player {{ display: none; }} 
    </style>
</head>
<body>

    <div class="player-container">
        <div class="player-controls">
            <button onclick="prevTrack()">&#9664;&#9664;</button>
            <button id="play-pause-btn" onclick="togglePlayPause()">&#9658;</button>
            <button onclick="nextTrack()">&#9658;&#9658;</button>
        </div>
        <div id="track-name">Đang tải...</div>
    </div>
    
    <audio id="audio-player"></audio>

    <script>
        // Data chứa GITHUB RAW URL
        const playlistData = {music_playlist_json}; 
        const playlistKeys = Object.keys(playlistData);
        const audio = document.getElementById('audio-player');
        const playPauseBtn = document.getElementById('play-pause-btn');
        const trackNameDisplay = document.getElementById('track-name');
        
        let currentTrackIndex = 0;

        function loadTrack(index) {{
            const key = playlistKeys[index];
            const url = playlistData[key]; 

            // SỬ DỤNG GITHUB RAW URL TRỰC TIẾP
            audio.src = url; 

            trackNameDisplay.textContent = key.toUpperCase().replace("BACKGROUND", "Bài ");
            audio.load();
        }}
        
        function togglePlayPause(forcePlay = false) {{
            if (audio.paused || forcePlay) {{
                // Nếu đang cố gắng play, đảm bảo load track đầu tiên 
                if (audio.src === "") {{ loadTrack(currentTrackIndex); }}
                
                audio.play().then(() => {{
                    playPauseBtn.innerHTML = '&#10074;&#10074;'; 
                }}).catch(e => {{
                    console.error('Lỗi tự động phát (Chặn Autoplay):', e);
                    // Không hiện alert.
                }});
            }} else {{
                audio.pause();
                playPauseBtn.innerHTML = '&#9658;'; 
            }}
        }}
        window.togglePlayPause = togglePlayPause; // Xuất hàm để iframe cha gọi được

        function nextTrack() {{
            currentTrackIndex = (currentTrackIndex + 1) % playlistKeys.length;
            loadTrack(currentTrackIndex);
            if (!audio.paused) {{
                 audio.play(); 
            }}
        }}

        function prevTrack() {{
            currentTrackIndex = (currentTrackIndex - 1 + playlistKeys.length) % playlistKeys.length;
            loadTrack(currentTrackIndex);
            if (!audio.paused) {{
                audio.play();
            }}
        }}

        // Tự động chuyển bài khi kết thúc
        audio.addEventListener('ended', nextTrack);

        // Khởi tạo player với bài đầu tiên
        document.addEventListener("DOMContentLoaded", function() {{
            loadTrack(currentTrackIndex);
        }});

    </script>
</body>
</html>
"""

# Tạo container HTML cho Music Player để áp dụng CSS ID
st.markdown('<div id="music-player-container">', unsafe_allow_html=True)
st.components.v1.html(custom_music_player_html, height=80)
st.markdown('</div>', unsafe_allow_html=True)
