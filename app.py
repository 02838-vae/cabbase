import streamlit as st
import base64
import json

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

# Danh sách các file nhạc nền
background_music_files = [f"background{i}.mp3" for i in range(1, 7)]

# Mã hóa các file media
try:
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    
    # Mã hóa 6 file nhạc nền cho Music Player
    bg_music_base64 = {
        file_name: get_base64_encoded_file(file_name) 
        for file_name in background_music_files
    }
    
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
except FileNotFoundError as e:
    st.error(e)
    st.stop()

# Tạo danh sách các URI dữ liệu cho JavaScript
bg_music_data_uris = [
    f"data:audio/mp3;base64,{base64_data}" 
    for base64_data in bg_music_base64.values()
]
# Chuyển đổi list Python sang chuỗi JSON hợp lệ để nhúng vào JS
bg_music_js_array = json.dumps(bg_music_data_uris)


# --- PHẦN 1: NHÚNG FONT BẰNG THẺ LINK TRỰC TIẾP VÀO BODY ---
font_links = """
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
"""
st.markdown(font_links, unsafe_allow_html=True)


# --- PHẦN 2: CSS CHÍNH (STREAMLIT APP) ---
# ĐÃ CẬP NHẬT CSS MUSIC PLAYER ĐỂ HIỆN NGAY LẬP TỨC
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

/* Điều chỉnh IFRAME của video intro */
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
    background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3); 
    background-size: 400% 400%; 
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

/* === MUSIC PLAYER TÙY CHỈNH (HIỆN NGAY) === */
#music-player-container {{
    position: fixed;
    top: 17vh; 
    left: 50%;
    transform: translateX(-50%);
    z-index: 30;
    padding: 8px 15px;
    background-color: rgba(0, 0, 0, 0.4); 
    backdrop-filter: blur(8px);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    opacity: 1; /* HIỆN NGAY LẬP TỨC */
    width: 250px; 
}}

/* KHÔNG CẦN .video-finished #music-player-container */

#track-info {{
    font-family: 'Playfair Display', serif;
    font-size: 1.1vw;
    color: #FFD700; 
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.9);
    white-space: nowrap;
    overflow: hidden;
    max-width: 100%;
}}

#player-controls {{
    display: flex;
    gap: 20px;
}}

.player-button {{
    background: none;
    border: none;
    cursor: pointer;
    color: #fff;
    font-size: 28px; 
    transition: color 0.3s, transform 0.1s;
    padding: 5px;
}}

.player-button:hover {{
    color: #ff0000; 
    transform: scale(1.2);
}}

.player-button:active {{
    transform: scale(0.9);
    color: #ff7f00; 
}}

.player-button.play-pause::after {{
    content: "▶"; 
}}

.player-button.play-pause.playing::after {{
    content: "⏸"; 
}}

@media (max-width: 768px) {{
    #music-player-container {{
        top: 15vh;
        width: 180px;
        padding: 6px 10px;
    }}
    #track-info {{
        font-size: 3vw;
    }}
    .player-button {{
        font-size: 24px;
    }}
}}
</style>
"""

# Thêm CSS vào trang chính
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- PHẦN 3: MÃ HTML/CSS/JavaScript IFRAME CHO VIDEO INTRO (GIỮ NGUYÊN) ---

# JavaScript (GIỮ NGUYÊN)
js_callback_video = f"""
<script>
    function sendBackToStreamlit() {{
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

# Mã HTML/CSS cho Video (GIỮ NGUYÊN)
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


# --------------------------------------------------------------------------------
# --- PHẦN 4: MUSIC PLAYER (ĐÃ TỐI ƯU HÓA TỐC ĐỘ LOAD VÀ TƯƠNG TÁC) ---
# --------------------------------------------------------------------------------

music_player_html_js = f"""
<div id="music-player-container">
    <div id="track-info">Đang tải...</div>
    <div id="player-controls">
        <button id="prev-button" class="player-button" title="Previous" onclick="window.parent.prevTrack()">⏮</button>
        <button id="play-pause-button" class="player-button play-pause" title="Play/Pause" onclick="window.parent.togglePlayPause()">▶</button>
        <button id="next-button" class="player-button" title="Next" onclick="window.parent.nextTrack()">⏭</button>
    </div>
    <audio id="background-playlist-audio" preload="auto"></audio>
</div>

<script>
    // Kiểm tra xem đã tồn tại chưa để tránh tạo lại khi Streamlit re-run
    if (typeof window.parent.playlist === 'undefined') {{
        // Gán các phần tử và biến vào window.parent để truy cập global
        window.parent.audio = window.parent.document.getElementById('background-playlist-audio');
        window.parent.playPauseButton = window.parent.document.getElementById('play-pause-button');
        window.parent.trackInfo = window.parent.document.getElementById('track-info');
        
        window.parent.playlist = {bg_music_js_array}; 
        window.parent.trackNames = ['BACKGROUND 1', 'BACKGROUND 2', 'BACKGROUND 3', 'BACKGROUND 4', 'BACKGROUND 5', 'BACKGROUND 6'];
        
        window.parent.currentTrackIndex = 0;
        window.parent.isPlaying = false;
        window.parent.playerInitialized = false;

        window.parent.updatePlayerState = function() {{
            window.parent.trackInfo.textContent = '🎵 ' + window.parent.trackNames[window.parent.currentTrackIndex];
            
            if (window.parent.isPlaying) {{
                window.parent.playPauseButton.classList.add('playing');
            }} else {{
                window.parent.playPauseButton.classList.remove('playing');
            }}
        }};

        window.parent.loadTrack = function(index) {{
            window.parent.currentTrackIndex = index;
            window.parent.audio.src = window.parent.playlist[window.parent.currentTrackIndex];
            // Tải (load) ngay lập tức
            window.parent.audio.load(); 
            window.parent.updatePlayerState();
        }};

        window.parent.playTrack = function() {{
            // Sử dụng Promise để xử lý lỗi Autoplay
            window.parent.audio.play().then(() => {{
                window.parent.isPlaying = true;
                window.parent.updatePlayerState();
            }}).catch(e => {{
                console.log("Autoplay failed. Waiting for user interaction.");
                window.parent.isPlaying = false; 
                window.parent.updatePlayerState();
            }});
        }};

        window.parent.togglePlayPause = function() {{
            if (window.parent.isPlaying) {{
                window.parent.audio.pause();
                window.parent.isPlaying = false;
            }} else {{
                // Đảm bảo track được load trước khi play
                if (!window.parent.playerInitialized) {{
                    window.parent.loadTrack(window.parent.currentTrackIndex);
                    window.parent.playerInitialized = true;
                }}
                window.parent.playTrack();
            }}
            window.parent.updatePlayerState();
        }};

        window.parent.nextTrack = function() {{
            window.parent.currentTrackIndex = (window.parent.currentTrackIndex + 1) % window.parent.playlist.length;
            window.parent.loadTrack(window.parent.currentTrackIndex);
            if (window.parent.isPlaying) {{
                window.parent.playTrack();
            }}
        }};

        window.parent.prevTrack = function() {{
            window.parent.currentTrackIndex = (window.parent.currentTrackIndex - 1 + window.parent.playlist.length) % window.parent.playlist.length;
            window.parent.loadTrack(window.parent.currentTrackIndex);
            if (window.parent.isPlaying) {{
                window.parent.playTrack();
            }}
        }};
        
        // Tự động chuyển bài khi kết thúc
        window.parent.audio.addEventListener('ended', window.parent.nextTrack);
        
        // *** TẢI TRACK ĐẦU TIÊN NGAY LẬP TỨC KHI SCRIPT ĐƯỢC CHẠY ***
        window.parent.loadTrack(window.parent.currentTrackIndex);
        window.parent.playerInitialized = true; // Coi như đã init
    }}
    
    // Khuyến nghị: Bắt sự kiện click bất kỳ trên trang để xử lý lỗi Autoplay
    // Lần click đầu tiên của người dùng sẽ kích hoạt media
    window.parent.document.body.addEventListener('click', () => {{
        if (!window.parent.autoPlayAttempted) {{
            window.parent.autoPlayAttempted = true;
            // Nếu người dùng đã click, thử phát nhạc ngay cả khi chưa bấm nút play
            // Đây là mẹo giúp âm thanh có thể bắt đầu sau lần tương tác đầu tiên
            window.parent.playTrack(); 
        }}
    }}, {{ once: true }}); 

</script>
"""

st.markdown(music_player_html_js, unsafe_allow_html=True)
