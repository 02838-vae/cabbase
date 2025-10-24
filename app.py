import streamlit as st
import base64
import glob
import os
import random

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

def get_base64_audio_playlist(prefix="background", count=6):
    """Tìm và mã hóa một danh sách các file audio (background1.mp3, ...)"""
    audio_files = []
    base64_audios = {}
    
    # Tạo danh sách tên file mong muốn
    for i in range(1, count + 1):
        filename = f"{prefix}{i}.mp3"
        audio_files.append(filename)

    # Lọc những file có tồn tại và mã hóa chúng
    for file_path in audio_files:
        if os.path.exists(file_path):
            try:
                base64_audios[file_path] = get_base64_encoded_file(file_path)
            except Exception as e:
                st.warning(f"Không thể mã hóa file {file_path}: {e}")
        else:
            st.warning(f"File nhạc {file_path} không được tìm thấy.")
            
    if not base64_audios:
        raise FileNotFoundError("Không tìm thấy bất kỳ file nhạc background nào (ví dụ: background1.mp3).")
        
    return base64_audios


# Mã hóa các file media
try:
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3") # Vẫn giữ audio này cho intro
    
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
    
    # === THAY ĐỔI LỚN 1: MÃ HÓA DANH SÁCH MP3 PLAYLIST ===
    playlist_base64_dict = get_base64_audio_playlist(prefix="background", count=6)
    
    # Chuyển dictionary Base64 sang JSON-like string để nhúng vào JS
    # Định dạng: {"background1.mp3": "base64_data", ...}
    playlist_json_str = str(playlist_base64_dict).replace("'", '"')

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

# === THAY ĐỔI LỚN 2: THÊM CSS CHO MUSIC PLAYER VÀ KÍCH HOẠT NÓ SAU KHI INTRO KẾT THÚC ===
hide_streamlit_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sacramento&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');

/* Ẩn các thành phần mặc định của Streamlit */
#MainMenu, footer, header {{visibility: hidden;}}

/* ... (Giữ nguyên các CSS khác) ... */

/* Thêm Class để hiện Music Player sau khi intro kết thúc */
.stApp.music-active #music-player-container {{
    opacity: 1; /* Hiện Music Player */
    pointer-events: auto; /* Cho phép tương tác */
}}

/* === MUSIC PLAYER STYLE === */
#music-player-container {{
    position: fixed;
    top: 17vh; /* Đặt dưới tiêu đề chính (top 5vh + 10vh height + 2vh margin) */
    left: 50%;
    transform: translateX(-50%);
    z-index: 20;
    pointer-events: none; /* Ẩn ban đầu */
    opacity: 0; 
    transition: opacity 1s ease-in-out; 
    background-color: rgba(255, 255, 255, 0.1); /* Nền mờ */
    border-radius: 10px;
    padding: 5px 15px;
    box-shadow: 0 0 15px rgba(0, 0, 0, 0.5);
}}

#music-player {{
    width: 250px; /* Kích thước nhỏ gọn */
}}

@media (max-width: 768px) {{
    #music-player-container {{
        top: 15vh; /* Điều chỉnh vị trí trên mobile */
    }}
    #music-player {{
        width: 150px; /* Nhỏ hơn trên mobile */
    }}
}}

/* ... (Giữ nguyên các CSS khác cho video, title, reveal grid) ... */

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
    0% {{ transform: translate(100vw, 0); }} /* Bắt đầu từ ngoài cùng bên phải */
    100% {{ transform: translate(-100%, 0); }} /* Chạy sang trái (độ rộng của chữ) */
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
    animation: scrollText 15s linear infinite; /* Giảm từ 25s xuống 15s */
    
    /* 2. Hiệu ứng đổi màu */
    background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3); /* Cầu vồng */
    background-size: 400% 400%; /* Cần kích thước lớn để tạo hiệu ứng chuyển màu mượt */
    -webkit-background-clip: text; /* Clip màu nền theo hình dạng chữ */
    -webkit-text-fill-color: transparent; /* Ẩn màu chữ gốc */
    color: transparent; /* Dành cho các trình duyệt khác */
    animation: colorShift 10s ease infinite, scrollText 15s linear infinite; /* Áp dụng đồng thời 2 animation */
    
    /* Thiết lập bóng đổ cổ điển */
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5); /* Giảm độ đậm của bóng để màu sắc nổi bật */
}}


@media (max-width: 768px) {{
    #main-title-container {{
        height: 8vh;
        width: 100%;  
        left: 0;
    }}
    
    #main-title-container h1 {{
        font-size: 6.5vw;  
        animation-duration: 8s; /* Tăng tốc độ trên mobile */
    }}
}}
</style>
"""


# Thêm CSS vào trang chính
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# === THAY ĐỔI LỚN 3: THÊM JAVASCRIPT CHO MUSIC PLAYER VÀ KÍCH HOẠT NÓ ===
js_music_player = f"""
<script>
    // Playlist data
    const playlistData = {playlist_json_str};
    const audioFiles = Object.keys(playlistData);
    let currentTrackIndex = -1; // -1 để track đầu tiên được chọn ngẫu nhiên

    function getNextTrackIndex() {{
        // Chọn ngẫu nhiên track tiếp theo (không trùng với track hiện tại nếu có thể)
        if (audioFiles.length === 1) return 0;
        let nextIndex;
        do {{
            nextIndex = Math.floor(Math.random() * audioFiles.length);
        }} while (nextIndex === currentTrackIndex);
        return nextIndex;
    }}

    function playNextTrack() {{
        const audioPlayer = window.parent.document.getElementById('music-player');
        if (!audioPlayer || audioFiles.length === 0) return;

        currentTrackIndex = getNextTrackIndex();
        const nextTrackName = audioFiles[currentTrackIndex];
        const base64Data = playlistData[nextTrackName];
        
        // Thiết lập nguồn Base64 mới
        audioPlayer.src = `data:audio/mp3;base64,${{base64Data}}`;
        
        audioPlayer.load();
        
        // Tự động phát với logic phòng trường hợp autoplay bị chặn
        audioPlayer.play().catch(e => {{
            console.log("Music Player Autoplay blocked. Waiting for user interaction.", e);
            // Có thể thêm thông báo hoặc icon Play/Pause tại đây
        }});
        
        console.log(`Playing: ${{nextTrackName}}`);
    }}

    // Thiết lập sự kiện khi track hiện tại kết thúc
    document.addEventListener("DOMContentLoaded", function() {{
        const audioPlayer = document.getElementById('music-player');
        if (audioPlayer) {{
            // Khi người dùng tương tác với trang, thử phát track đầu tiên
            window.parent.document.body.addEventListener('click', () => {{
                if (currentTrackIndex === -1) {{ // Chỉ gọi lần đầu
                    playNextTrack();
                }} else {{
                    audioPlayer.play().catch(e => {{}});
                }}
            }}, {{ once: true }}); 
            
            // Lắng nghe sự kiện kết thúc track để chuyển bài
            audioPlayer.onended = playNextTrack;
        }
    }});
    
    // Hàm này sẽ được gọi sau khi video intro kết thúc
    window.parent.initMusicPlayer = function() {{
        window.parent.document.querySelector('.stApp').classList.add('music-active');
        playNextTrack(); // Bắt đầu chơi nhạc nền
    }}
</script>
"""

# Mã HTML cho Music Player (sẽ được nhúng vào nội dung chính)
music_player_html = f"""
<div id="music-player-container">
    <audio id="music-player" controls preload="auto"></audio>
</div>
"""
# --- PHẦN 3: MÃ HTML/CSS/JavaScript IFRAME CHO VIDEO INTRO (Cập nhật gọi hàm Music Player) ---


# JavaScript (CẬP NHẬT: Thêm gọi hàm initMusicPlayer())
js_callback_video = f"""
<script>
    function sendBackToStreamlit() {{
        window.parent.document.querySelector('.stApp').classList.add('video-finished', 'main-content-revealed');
        initRevealEffect();
        
        // === THAY ĐỔI LỚN 4: GỌI HÀM KHỞI TẠO MUSIC PLAYER TẠI ĐÂY ===
        if (window.parent.initMusicPlayer) {{
            window.parent.initMusicPlayer();
        }}
    }}
    
    // ... (Giữ nguyên initRevealEffect) ...
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


# --- NỘI DUNG CHÍNH (TIÊU ĐỀ ĐƠN, ĐỔI MÀU & MUSIC PLAYER) ---


# Tiêu đề đơn
main_title_text = "TỔ BẢO DƯỠNG SỐ 1"  


# Nhúng tiêu đề và Music Player
st.markdown(f"""
<div id="main-title-container">
    <h1>{main_title_text}</h1>
</div>

{music_player_html}

{js_music_player}

""", unsafe_allow_html=True)
