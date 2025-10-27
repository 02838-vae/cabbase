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
        # Sử dụng st.error cho file quan trọng
        st.error(f"LỖI CỐT LÕI: Không tìm thấy file media. Vui lòng kiểm tra đường dẫn: {e.filename}")
        st.stop()
        
def get_static_song_urls(directory="songs", prefix="background", count=6):
    """
    Tạo danh sách URL tương đối cho các bài hát tĩnh.
    Điều này hoạt động nhờ cấu hình enable_static_file_serving = true.
    """
    song_urls = []
    # Streamlit phục vụ các tệp từ thư mục gốc, nên đường dẫn là thư mục/tên file
    base_url = f"{directory}/" 
    
    if not os.path.exists(directory):
        # Đây là cảnh báo quan trọng nếu thư mục không tồn tại
        st.warning(f"⚠️ CẢNH BÁO: Không tìm thấy thư mục nhạc '{directory}'. Player sẽ không hoạt động.")
        return []
    
    found_count = 0
    for i in range(1, count + 1):
        filename = f"{prefix}{i}.mp3"
        file_path = os.path.join(directory, filename)
        if os.path.exists(file_path):
            url = base_url + filename
            song_urls.append(url)
            found_count += 1
    
    if found_count == 0 and os.path.exists(directory):
        st.warning(f"⚠️ CẢNH BÁO: Tìm thấy thư mục '{directory}' nhưng không có tệp MP3 nào theo định dạng '{prefix}X.mp3'.")

    return song_urls

# Mã hóa các file media
try:
    # Media files for intro và background images
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")

    # Music Player songs (Dùng URL tĩnh từ thư mục "songs")
    songs_url_list = get_static_song_urls()

except FileNotFoundError:
    # Lỗi đã được xử lý trong get_base64_encoded_file
    st.stop()


# --- PHẦN 1: NHÚNG FONT VÀ CSS CHUNG (Không đổi) ---
font_links = """
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
"""
st.markdown(font_links, unsafe_allow_html=True)


hide_streamlit_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sacramento&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');

/* ... (Phần CSS giữ nguyên như phiên bản trước) ... */

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

@keyframes scrollText {{
    0% {{ transform: translate(100vw, 0); }}
    100% {{ transform: translate(-100%, 0); }}
}}

@keyframes colorShift {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}


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

#prev-btn, #next-btn {{
    font-size: 20px; 
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
    #prev-btn, #next-btn {{
        font-size: 16px;
    }}
}}

</style>
"""

# Thêm CSS vào trang chính
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- PHẦN 2 & 3: VIDEO INTRO VÀ CONTENT CHÍNH (Không thay đổi logic) ---

# JavaScript Callback cho Video Intro (Giữ nguyên)
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

# Mã HTML/CSS cho Video (Giữ nguyên)
html_content_modified = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        /* ... (CSS cho video giữ nguyên) ... */
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

# Xử lý nội dung của tiêu đề video intro để thêm hiệu ứng chữ thả (Giữ nguyên)
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


# Nhúng tiêu đề (Giữ nguyên)
main_title_text = "TỔ BẢO DƯỠNG SỐ 1" 
st.markdown(f"""
<div id="main-title-container">
    <h1>{main_title_text}</h1>
</div>
""", unsafe_allow_html=True) 


# --- MUSIC PLAYER COMPONENT (Tinh chỉnh log) ---

# Chuẩn bị dữ liệu URL cho JS
songs_data_js = [f"'{url}'" for url in songs_url_list] 

music_player_js = f"""
<script>
    document.addEventListener("DOMContentLoaded", function() {{
        const audioPlayer = new Audio();
        audioPlayer.crossOrigin = "anonymous";
        
        const songs = [{', '.join(songs_data_js)}];
        let currentSongIndex = 0;
        let isPlaying = false;

        const playPauseBtn = document.getElementById('play-pause-btn');
        // Icon cảnh báo tải lỗi ban đầu
        playPauseBtn.innerHTML = '&#9654;'; 

        const nextBtn = document.getElementById('next-btn');
        const prevBtn = document.getElementById('prev-btn');
        const progressBar = document.getElementById('progress-bar');
        const progressContainer = document.getElementById('progress-container');

        if (songs.length === 0) {{
            console.error("LỖI: Không tìm thấy file nhạc nào. Player bị ẩn.");
            document.getElementById('music-player-container').style.display = 'none';
            return;
        }}
        
        // Listener báo lỗi khi tải file
        audioPlayer.addEventListener('error', (e) => {{
            console.error('❌ LỖI TẢI AUDIO! VUI LÒNG KIỂM TRA LẠI FILE STATIC VÀ CONFIG.TOML');
            console.error('Mã lỗi:', e.target.error.code, 'Message:', e.target.error.message);
            console.error('Đường dẫn file bị lỗi:', audioPlayer.src);
            playPauseBtn.innerHTML = '&#9940;'; // Icon cấm
            isPlaying = false;
        }});
        
        // Listener khi tệp được tải thành công
        audioPlayer.addEventListener('canplay', () => {{
            console.log('✅ Tệp audio đã được tải và sẵn sàng phát:', audioPlayer.src);
        }});
        
        function loadSong(index) {{
            audioPlayer.src = songs[index];
            audioPlayer.load();
        }}

        function playSong() {{
            // Cố gắng phát nhạc ngay khi được gọi
            audioPlayer.play().then(() => {{
                isPlaying = true;
                playPauseBtn.innerHTML = '&#9208;'; // Icon Pause
                console.log("MUSIC PLAYER: Phát nhạc thành công.");
            }}).catch(e => {{
                // Đây là lúc Autoplay bị chặn
                console.warn("MUSIC PLAYER: ⚠️ Autoplay bị chặn. Vui lòng BẤM LẠI nút Play.");
                playPauseBtn.innerHTML = '&#9654;'; // Icon Play
                isPlaying = false;
            }});
        }}

        function pauseSong() {{
            audioPlayer.pause();
            isPlaying = false;
            playPauseBtn.innerHTML = '&#9654;'; // Icon Play
            console.log("MUSIC PLAYER: Tạm dừng.");
        }}

        function nextSong() {{
            currentSongIndex = (currentSongIndex + 1) % songs.length;
            loadSong(currentSongIndex);
            playSong();
            console.log("MUSIC PLAYER: Chuyển bài tiếp theo.");
        }}

        function prevSong() {{
            currentSongIndex = (currentSongIndex - 1 + songs.length) % songs.length;
            loadSong(currentSongIndex);
            playSong();
            console.log("MUSIC PLAYER: Chuyển bài trước.");
        }}
        
        // Cập nhật thanh tiến trình
        audioPlayer.addEventListener('timeupdate', (e) => {{
            const {{duration, currentTime}} = e.target;
            if (isFinite(duration) && duration > 0) {{
                const progressPercent = (currentTime / duration) * 100;
                progressBar.style.width = `${{progressPercent}}%`;
            }}
        }});
        
        // Chuyển bài khi kết thúc
        audioPlayer.addEventListener('ended', nextSong);

        // Xử lý nút Play/Pause - Logic cốt lõi để phát nhạc
        playPauseBtn.addEventListener('click', (e) => {{
            e.stopPropagation(); 
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
        
        // Tối ưu Autoplay: Dùng sự kiện 'click' trên body để kích hoạt âm thanh sau khi video kết thúc
        window.parent.document.body.addEventListener('click', () => {{
             // Chỉ cố gắng play nếu hiện tại không đang play và audio đã được load
             if (!isPlaying && audioPlayer.paused && audioPlayer.src) {{
                 playSong();
             }}
        }}, {{ once: true }});
        
    }});
</script>
"""

music_player_html = f"""
<div id="music-player-container">
    <div id="player-controls">
        <button id="prev-btn" title="Previous">&#171;</button> 
        <button id="play-pause-btn" title="Play">&#9654;</button>
        <button id="next-btn" title="Next">&#187;</button>
    </div>
    <div id="progress-container">
        <div id="progress-bar"></div>
    </div>
    {music_player_js}
</div>
"""

st.markdown(music_player_html, unsafe_allow_html=True)
