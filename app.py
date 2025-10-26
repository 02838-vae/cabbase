import streamlit as st
import base64
import os
import streamlit.components.v1 as components

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

def get_static_song_urls(directory="songs", prefix="background", count=6):
    """Tạo danh sách URL tương đối cho các bài hát tĩnh từ thư mục 'songs'."""
    song_urls = []
    song_names = []
    
    # URL mà Trình duyệt sẽ tìm kiếm (đường dẫn tương đối)
    base_url = "songs/" 
    
    if not os.path.exists(directory):
        st.error(f"LỖI: Không tìm thấy thư mục nhạc '{directory}'. Vui lòng kiểm tra lại cấu trúc file.")
        return [], []
    
    for i in range(1, count + 1):
        filename = f"{prefix}{i}.mp3"
        file_path = os.path.join(directory, filename)
        if os.path.exists(file_path):
            url = base_url + filename
            song_urls.append(url)
            song_names.append(filename)
        else:
            st.warning(f"Cảnh báo: Không tìm thấy file {file_path}. Bỏ qua file này.")
            continue
    return song_urls, song_names

# Mã hóa các file media
try:
    # Media files for intro và background images (vẫn dùng Base64)
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")

    # Music Player songs (Dùng URL tĩnh từ thư mục "songs")
    songs_url_list, song_names_list = get_static_song_urls()

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

/* === MUSIC PLAYER CSS (ĐÃ FIX) === */
#music-player-container {{
    position: fixed;
    bottom: 20px; 
    left: 20px; 
    z-index: 100; 
    padding: 10px;
    background: rgba(0, 0, 0, 0.7); 
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    color: #FFD700; 
    width: 250px; 
    display: flex;
    flex-direction: column;
    opacity: 0; 
    transition: opacity 2s ease-in-out;
}}

.main-content-revealed #music-player-container {{
    opacity: 1;
}}

#player-controls {{
    display: flex;
    justify-content: space-around;
    align-items: center;
    margin-bottom: 8px;
}}

#player-controls button {{
    background: none;
    border: none;
    color: #FFD700;
    font-size: 20px;
    cursor: pointer;
    transition: color 0.2s;
    padding: 5px 8px;
}}

#player-controls button:hover {{
    color: #FFF;
}}

#play-pause-btn {{
    font-size: 28px;
}}

#progress-container {{
    width: 100%;
    height: 6px;
    background: #555;
    border-radius: 3px;
    cursor: pointer;
}}

#progress-bar {{
    height: 100%;
    width: 0%;
    background: #FFD700;
    border-radius: 3px;
}}

/* GIỮ LẠI ĐỂ DUY TRÌ BỐ CỤC */
#song-title {{
    font-family: 'Playfair Display', serif;
    font-size: 14px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-top: 5px;
    text-align: center;
}}

@media (max-width: 768px) {{
    #music-player-container {{
        bottom: 10px;
        left: 10px;
        width: 180px; 
        padding: 8px;
    }}
    #player-controls button {{
        font-size: 16px;
        padding: 3px 6px;
    }}
    #play-pause-btn {{
        font-size: 24px;
    }}
    #song-title {{
        font-size: 12px;
    }}
}}

</style>
"""

# Thêm CSS vào trang chính
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- PHẦN 3: MÃ HTML/CSS/JavaScript IFRAME CHO VIDEO INTRO (GIỮ NGUYÊN) ---

# JavaScript Callback
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
components.html(html_content_modified, height=10, scrolling=False)


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

# Tiêu đề đơn
main_title_text = "TỔ BẢO DƯỠNG SỐ 1" 

# Nhúng tiêu đề
st.markdown(f"""
<div id="main-title-container">
    <h1>{main_title_text}</h1>
</div>
""", unsafe_allow_html=True) 


# --- MUSIC PLAYER COMPONENT (ĐÃ SỬA LỖI TƯƠNG TÁC) ---

# Chuẩn bị dữ liệu URL cho JS
songs_data_js = [f"'{url}'" for url in songs_url_list] 
song_names_js = [f"'{name}'" for name in song_names_list] 

music_player_js = f"""
<script>
    document.addEventListener("DOMContentLoaded", function() {{
        const audioPlayer = new Audio();
        // Sử dụng URL tĩnh từ thư mục 'songs'
        const songs = [{', '.join(songs_data_js)}];
        const songTitles = [{', '.join(song_names_js)}]; // Giữ lại songTitles để đảm bảo loadSong hoạt động
        let currentSongIndex = 0;
        let isPlaying = false;

        const playPauseBtn = document.getElementById('play-pause-btn');
        const nextBtn = document.getElementById('next-btn');
        const prevBtn = document.getElementById('prev-btn');
        const progressBar = document.getElementById('progress-bar');
        const progressContainer = document.getElementById('progress-container');
        const songTitleDisplay = document.getElementById('song-title');

        if (songs.length === 0) {{
            document.getElementById('music-player-container').style.display = 'none';
            return;
        }}
        
        function loadSong(index) {{
            audioPlayer.src = songs[index];
            // BỎ qua việc cập nhật tên bài hát. Giữ lại text tĩnh "Đang tải..." nếu muốn.
            // Nếu muốn ẩn hoàn toàn, có thể dùng: songTitleDisplay.style.display = 'none';
            audioPlayer.load();
        }}

        function playSong() {{
            // Sử dụng Promise để xử lý lỗi Autoplay một cách chính xác
            audioPlayer.play().then(() => {{
                isPlaying = true;
                playPauseBtn.innerHTML = '&#9208;'; // Pause icon
                songTitleDisplay.textContent = songTitles[currentSongIndex]; // Cập nhật tên khi play thành công
            }}).catch(e => {{
                console.log("Audio play failed (Autoplay Blocked). Ensure user interaction occurred:", e);
                // Giữ nguyên icon Play nếu bị chặn
            }});
        }}

        function pauseSong() {{
            audioPlayer.pause();
            isPlaying = false;
            playPauseBtn.innerHTML = '&#9654;'; // Play icon
        }}

        function nextSong() {{
            currentSongIndex = (currentSongIndex + 1) % songs.length;
            loadSong(currentSongIndex);
            playSong();
        }}

        function prevSong() {{
            currentSongIndex = (currentSongIndex - 1 + songs.length) % songs.length;
            loadSong(currentSongIndex);
            playSong();
        }}
        
        // Cập nhật thanh tiến trình
        audioPlayer.addEventListener('timeupdate', (e) => {{
            const {{duration, currentTime}} = e.target;
            if (isFinite(duration) && duration > 0) {{
                const progressPercent = (currentTime / duration) * 100;
                progressBar.style.width = `${{progressPercent}}%`;
            }}
        }});
        
        // Cập nhật trạng thái loading
        audioPlayer.addEventListener('loadeddata', () => {{
            // Khi dữ liệu bài hát đã sẵn sàng, thay đổi text sang tên bài hát
            songTitleDisplay.textContent = songTitles[currentSongIndex]; 
        }});
        audioPlayer.addEventListener('error', (e) => {{
            songTitleDisplay.textContent = "Lỗi tải nhạc!";
            console.error("Lỗi tải file nhạc:", e);
        }});


        // Chuyển bài khi kết thúc
        audioPlayer.addEventListener('ended', nextSong);

        // Xử lý nút Play/Pause - Đảm bảo lệnh play được gọi trực tiếp từ tương tác
        playPauseBtn.addEventListener('click', (e) => {{
            e.stopPropagation(); // Ngăn sự kiện click lan truyền lên body
            if (isPlaying) {{
                pauseSong();
            }} else {{
                playSong();
            }}
        }});
        
        // Xử lý nút Next/Prev
        nextBtn.addEventListener('click', nextSong);
        prevBtn.addEventListener('click', prevSong);
        
        // Xử lý click trên thanh tiến trình
        progressContainer.addEventListener('click', (e) => {{
            const width = progressContainer.clientWidth;
            const clickX = e.offsetX;
            const duration = audioPlayer.duration;
            if (isFinite(duration) && duration > 0) {{
                 audioPlayer.currentTime = (clickX / width) * duration;
            }}
        }});
        
        // Khởi tạo bài hát đầu tiên
        loadSong(currentSongIndex);

        // Tối ưu Autoplay: Đảm bảo player hoạt động ngay sau khi người dùng tương tác lần đầu
        window.parent.document.body.addEventListener('click', () => {{
             if (!isPlaying && audioPlayer.paused && audioPlayer.src) {{
                 // Tải lại bài hát và cố gắng play
                 playSong();
             }}
        }}, {{ once: true }});
        
    }});
</script>
"""

music_player_html = f"""
<div id="music-player-container">
    <div id="song-title">Đang tải...</div>
    <div id="player-controls">
        <button id="prev-btn" title="Previous">&#9664;</button>
        <button id="play-pause-btn" title="Play">&#9654;</button>
        <button id="next-btn" title="Next">&#9655;</button>
    </div>
    <div id="progress-container">
        <div id="progress-bar"></div>
    </div>
    {music_player_js}
</div>
"""

st.markdown(music_player_html, unsafe_allow_html=True)
