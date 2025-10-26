import streamlit as st
import base64
import os # Import os for file listing

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
        # Lỗi: Không tìm thấy file
        raise FileNotFoundError(f"Lỗi: Không tìm thấy file media. Vui lòng kiểm tra lại đường dẫn: {e.filename}")

def get_base64_encoded_songs(directory="songs", prefix="background", count=6):
    """Lấy danh sách các bài hát và mã hóa chúng."""
    songs_base64 = []
    song_names = []
    for i in range(1, count + 1):
        filename = f"{prefix}{i}.mp3"
        file_path = os.path.join(directory, filename)
        try:
            songs_base64.append(get_base64_encoded_file(file_path))
            song_names.append(filename)
        except FileNotFoundError:
            # Bỏ qua nếu một số file không tồn tại
            st.warning(f"Cảnh báo: Không tìm thấy file {file_path}. Bỏ qua file này.")
            continue
    return songs_base64, song_names

# Mã hóa các file media
try:
    # Media files for intro
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    
    # Background images
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")

    # Music Player songs
    songs_base64_list, song_names_list = get_base64_encoded_songs()

except FileNotFoundError as e:
    st.error(e)
    st.stop()


# --- PHẦN 1: NHÚNG FONT BẰNG THẺ LINK TRỰC TIẾP VÀO BODY ---
# (GIỮ NGUYÊN)
font_links = """
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
"""
st.markdown(font_links, unsafe_allow_html=True)


# --- PHẦN 2: CSS CHÍNH (STREAMLIT APP) ---
# THÊM CSS MỚI CHO MUSIC PLAYER
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

/* (GIỮ NGUYÊN CSS IFRAME) */
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
/* (KẾT THÚC GIỮ NGUYÊN CSS IFRAME) */


.stApp {{
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
}}

/* (GIỮ NGUYÊN CSS REVEAL GRID VÀ MAIN CONTENT) */
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
/* (KẾT THÚC GIỮ NGUYÊN CSS REVEAL GRID VÀ MAIN CONTENT) */


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
/* (GIỮ NGUYÊN CSS MAIN TITLE) */
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
/* (KẾT THÚC GIỮ NGUYÊN CSS MAIN TITLE) */


/* === MUSIC PLAYER CSS (MỚI) === */
#music-player-container {{
    position: fixed;
    bottom: 20px; /* Cách đáy 20px */
    left: 20px; /* Cách lề trái 20px */
    z-index: 100; /* Nằm trên các nội dung khác */
    padding: 10px;
    background: rgba(0, 0, 0, 0.7); /* Nền đen trong suốt */
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    color: #FFD700; /* Màu chữ vàng */
    width: 250px; /* Chiều rộng cố định */
    display: flex;
    flex-direction: column;
    opacity: 0; /* Ban đầu ẩn, sẽ hiện ra sau khi video intro kết thúc */
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

/* Icon Play/Pause - sử dụng ký tự Unicode hoặc font icon */
#play-pause-btn {{
    font-size: 28px;
}}

/* Thanh trạng thái (Progress Bar) */
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

/* Tên bài hát */
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
        width: 180px; /* Nhỏ hơn trên mobile */
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
/* === KẾT THÚC MUSIC PLAYER CSS === */

</style>
"""

# Thêm CSS vào trang chính
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- PHẦN 3: MÃ HTML/CSS/JavaScript IFRAME CHO VIDEO INTRO (GIỮ NGUYÊN) ---

# (GIỮ NGUYÊN PHẦN JAVASCRIPT INTRO VIDEO VÀ HTML CONTENT)
# ... (Phần code này đã được giữ nguyên như trong yêu cầu của bạn)
# ...
# Hiển thị thành phần HTML (video)
st.components.v1.html(html_content_modified, height=10, scrolling=False)


# --- HIỆU ỨNG REVEAL VÀ NỘI DUNG CHÍNH ---
# (GIỮ NGUYÊN PHẦN TẠO LƯỚI REVEAL)
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

# --- MUSIC PLAYER COMPONENT (MỚI) ---

# Chuẩn bị dữ liệu Base64 cho JS
songs_data_js = [f"'data:audio/mp3;base64,{b64}'" for b64 in songs_base64_list]
song_names_js = [f"'{name}'" for name in song_names_list]

music_player_js = f"""
<script>
    document.addEventListener("DOMContentLoaded", function() {{
        const audioPlayer = new Audio();
        const songs = [{', '.join(songs_data_js)}];
        const songTitles = [{', '.join(song_names_js)}];
        let currentSongIndex = 0;
        let isPlaying = false;

        const playPauseBtn = document.getElementById('play-pause-btn');
        const nextBtn = document.getElementById('next-btn');
        const prevBtn = document.getElementById('prev-btn');
        const progressBar = document.getElementById('progress-bar');
        const progressContainer = document.getElementById('progress-container');
        const songTitleDisplay = document.getElementById('song-title');

        if (songs.length === 0) {{
            // Ẩn player nếu không có bài hát nào được tải
            document.getElementById('music-player-container').style.display = 'none';
            return;
        }}

        function loadSong(index) {{
            audioPlayer.src = songs[index];
            songTitleDisplay.textContent = songTitles[index];
            audioPlayer.load();
        }}

        function playSong() {{
            // Bắt buộc phải được gọi từ một tương tác người dùng
            audioPlayer.play().catch(e => console.log("Audio play failed, waiting for interaction:", e));
            isPlaying = true;
            playPauseBtn.innerHTML = '&#9208;'; // Pause icon
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
            const progressPercent = (currentTime / duration) * 100;
            progressBar.style.width = `${{progressPercent}}%`;
        }});

        // Chuyển bài khi kết thúc
        audioPlayer.addEventListener('ended', nextSong);

        // Xử lý nút Play/Pause
        playPauseBtn.addEventListener('click', () => {{
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
            audioPlayer.currentTime = (clickX / width) * duration;
        }});
        
        // Tải bài đầu tiên khi khởi tạo
        loadSong(currentSongIndex);

        // Thêm sự kiện click toàn bộ body để xử lý autoplay restriction
        window.parent.document.body.addEventListener('click', () => {{
             // Tự động play lần đầu tiên sau khi người dùng tương tác
             if (!isPlaying && audioPlayer.paused) {{
                 playSong();
             }}
        }}, {{ once: true }});
        
    }});
</script>
"""

music_player_html = f"""
<div id="music-player-container">
    <div id="song-title">Đang Tải...</div>
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
