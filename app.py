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
    """Đọc file và trả về Base64 encoded string. Dùng cho các file nhỏ/cần tải ngay."""
    # Kiểm tra tồn tại của file
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Lỗi: Không tìm thấy file media. Vui lòng kiểm tra lại đường dẫn: {file_path}")
        
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    except Exception as e:
        raise Exception(f"Lỗi khi mã hóa Base64 cho file {file_path}: {e}")


# Mã hóa các file media cần thiết (Video, Audio Intro, Ảnh nền)
try:
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3") # Âm thanh Intro
    
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")

    # === SỬ DỤNG ĐƯỜNG DẪN TƯƠNG ĐỐI CHO BÀI HÁT ===
    SONG_PATHS = [f"songs/background{i}.mp3" for i in range(1, 7)]
    song_paths_js_array = str(SONG_PATHS).replace("'", '"')
    
except FileNotFoundError as e:
    st.error(e)
    st.stop()
except Exception as e:
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

.main {{
    padding: 0;
    margin: 0;
}}

div.block-container {{
    padding: 0;
    margin: 0;
    max-width: 100% !important;
}}

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
}}

.stApp {{
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
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

/* Keyframes cho hiệu ứng chữ chạy đơn (từ phải sang trái, lặp lại) */
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


/* === TIÊU ĐỀ TRANG CHÍNH (ĐƠN, CHẠY VÀ ĐỔI MÀU) === */
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

#main-title-container h1 {{
    font-family: 'Playfair Display', serif; 
    font-size: 3.5vw; 
    margin: 0;
    font-weight: 900; 
    font-feature-settings: "lnum" 1; 
    letter-spacing: 5px; 
    white-space: nowrap; 
    
    display: inline-block; 

    /* 1. Hiệu ứng chữ chạy - Tăng tốc độ */
    animation: scrollText 15s linear infinite; 
    
    /* 2. Hiệu ứng đổi màu */
    background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3); /* Cầu vồng */
    background-size: 400% 400%; /* Cần kích thước lớn để tạo hiệu ứng chuyển màu mượt */
    -webkit-background-clip: text; 
    -webkit-text-fill-color: transparent; 
    color: transparent; 
    animation: colorShift 10s ease infinite, scrollText 15s linear infinite; 
    
    /* Thiết lập bóng đổ cổ điển */
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

/* === KHUNG CHUNG CỦA PLAYER === */
#music-player-container {{
    position: fixed;
    top: 50%; 
    left: 20px; 
    transform: translateY(-50%);
    z-index: 150; 
    width: 200px; 
    transition: opacity 1s ease-in-out;
    opacity: 0; /* Ban đầu ẩn */
}}

.video-finished #music-player-container {{
    opacity: 1; /* Hiện ra sau khi video kết thúc */
}}

@media (max-width: 768px) {{
    #music-player-container {{
        top: 20px; 
        left: 10px;
        transform: none;
        width: 150px;
    }}
}}

</style>
"""

# Thêm CSS vào trang chính
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- PHẦN 3: MÃ HTML/CSS/JavaScript IFRAME CHO VIDEO INTRO ---

# JavaScript (ĐÃ SỬA LỖI CÚ PHÁP NGOẶC NHỌN PYTHON)
js_callback_video = f"""
<script>
    function sendBackToStreamlit() {{
        // Gửi tín hiệu lên Streamlit parent để kích hoạt CSS cho trang chính và Player
        window.parent.document.querySelector('.stApp').classList.add('video-finished', 'main-content-revealed');
        initRevealEffect();
    }}
    
    function initRevealEffect() {{
        const revealGrid = window.parent.document.querySelector('.reveal-grid');
        const mainTitle = window.parent.document.getElementById('main-title-container');

        if (mainTitle) {{
             mainTitle.style.opacity = 1; 
        }}

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
                document.body.addEventListener('click', () => {{
                    audio.play().catch(err => console.error("Audio playback error on click:", err));
                }}, {{ once: true }});
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
        }}
        
        #intro-video {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            z-index: -100;
            transition: opacity 1s; 
        }}

        /* === TIÊU ĐỀ INTRO (FONT SACRAMENTO - Chữ Ký) === */
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

# Hiển thị thành phần HTML (video)
st.components.v1.html(html_content_modified, height=10, scrolling=False)


# --- HIỆU ỨNG REVEAL VÀ NỘI DUNG CHÍNH ---

# Tạo Lưới Reveal (Giữ nguyên)
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

# Tiêu đề đơn
main_title_text = "TỔ BẢO DƯỠNG SỐ 1" 

# Nhúng tiêu đề
st.markdown(f"""
<div id="main-title-container">
    <h1>{main_title_text}</h1>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# --- PHẦN 4: MUSIC PLAYER CỐ ĐỊNH (FIXED MUSIC PLAYER) ---
# -----------------------------------------------------------

song_names_js_array = str([f"Background {i}" for i in range(1, 7)]).replace("'", '"')

# === SỬ DỤNG PHƯƠNG THỨC .format() VÀ KHÔNG DÙNG r""" ĐỂ TRÁNH LỖI THỤT LỀ ===
music_player_full_template = """
<style>
/* CSS NỘI BỘ CHO PLAYER */
#music-player-container {
    padding: 10px;
    background: rgba(0, 0, 0, 0.7); 
    border-radius: 15px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
    display: flex;
    flex-direction: column;
    gap: 10px;
}

#player-controls {
    display: flex;
    justify-content: space-around;
    align-items: center;
}

#player-controls button {
    background: none;
    border: none;
    color: gold;
    font-size: 24px;
    cursor: pointer;
    transition: color 0.3s;
    line-height: 1; 
}

#player-controls button:hover {
    color: white;
}

#song-info {
    color: white;
    font-size: 14px;
    text-align: center;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

#progress-container {
    height: 5px;
    background: #444;
    border-radius: 5px;
    cursor: pointer;
}

#progress-bar {
    height: 100%;
    width: 0%;
    background: gold;
    border-radius: 5px;
    transition: width 0.1s linear;
}
</style>

<div id="music-player-container">
    <div id="song-info">Đang tải...</div>
    
    <div id="player-controls">
        <button id="prev-btn" title="Bài trước">⏮️</button>
        <button id="play-pause-btn" title="Phát/Dừng">▶️</button>
        <button id="next-btn" title="Bài tiếp theo">⏭️</button>
    </div>
    
    <div id="progress-container">
        <div id="progress-bar"></div>
    </div>
    
    <audio id="main-music-player"></audio>
</div>

<script>
    // CHÈN BIẾN PYTHON BẰNG .format()
    const SONG_PATHS = {song_paths_js_array}; 
    const SONG_NAMES = {song_names_js_array};

    let currentSongIndex = 0;
    const player = document.getElementById('main-music-player');
    const playPauseBtn = document.getElementById('play-pause-btn');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const songInfo = document.getElementById('song-info');
    const progressBar = document.getElementById('progress-bar');
    const progressContainer = document.getElementById('progress-container');

    function loadSong(index) {{
        // Cập nhật index vòng lặp
        currentSongIndex = (index + SONG_PATHS.length) % SONG_PATHS.length;
        
        const path = SONG_PATHS[currentSongIndex];
        const songName = SONG_NAMES[currentSongIndex];
        
        // Gán đường dẫn tương đối
        player.src = path;
        songInfo.textContent = songName;
        player.load();
    }}

    function playSong() {{
        player.play().catch(e => {{
            console.log("Audio play failed, waiting for user interaction:", e);
        }});
        playPauseBtn.textContent = '⏸️'; // Dấu tạm dừng
        playPauseBtn.title = 'Pause';
    }}

    function pauseSong() {{
        player.pause();
        playPauseBtn.textContent = '▶️'; // Dấu phát
        playPauseBtn.title = 'Play';
    }}

    function nextSong() {{
        loadSong(currentSongIndex + 1);
        playSong();
    }}

    function prevSong() {{
        loadSong(currentSongIndex - 1);
        playSong();
    }}

    // === XỬ LÝ SỰ KIỆN ===

    playPauseBtn.addEventListener('click', (e) => {{
        e.stopPropagation(); 
        if (player.paused) {{
            playSong();
        }} else {{
            pauseSong();
        }}
    }});

    nextBtn.addEventListener('click', (e) => {{ e.stopPropagation(); nextSong(); }});
    prevBtn.addEventListener('click', (e) => {{ e.stopPropagation(); prevSong(); }});

    // Cập nhật thanh trạng thái
    player.addEventListener('timeupdate', () => {{
        if (!isNaN(player.duration)) {{
            const progressPercent = (player.currentTime / player.duration) * 100;
            progressBar.style.width = progressPercent + '%';
        }}
    }});
    
    // Bấm vào thanh trạng thái để tua
    progressContainer.addEventListener('click', (e) => {{
        const rect = progressContainer.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const width = rect.width;
        const duration = player.duration;
        if (!isNaN(duration)) {{
            player.currentTime = (clickX / width) * duration;
            playSong();
        }}
    }});
    

    // Tự động chuyển bài khi kết thúc
    player.addEventListener('ended', nextSong);

    // Tải bài hát đầu tiên và xử lý tự động phát
    document.addEventListener("DOMContentLoaded", () => {{
        if (SONG_PATHS.length > 0) {{
            loadSong(currentSongIndex);
            
            const stApp = window.parent.document.querySelector('.stApp');
            if(stApp) {{
                const observer = new MutationObserver((mutationsList, observer) => {{
                    if (stApp.classList.contains('video-finished')) {{
                        setTimeout(playSong, 1000); 
                        observer.disconnect(); 
                    }}
                }});
                observer.observe(stApp, {{ attributes: true, attributeFilter: ['class'] }});
            }}
        }}
    }});
    
    const playerContainer = document.getElementById('music-player-container');
    playerContainer.addEventListener('click', () => {{
         if (player.src && player.paused) {{
             playSong();
         }}
    }}, {{ once: true }});

</script>
"""

# Chèn các biến Python vào template
music_player_full_code = music_player_full_template.format(
    song_paths_js_array=song_paths_js_array,
    song_names_js_array=song_names_js_array
)

# Nhúng Music Player vào trang chính bằng st.markdown
st.markdown(music_player_full_code, unsafe_allow_html=True)
