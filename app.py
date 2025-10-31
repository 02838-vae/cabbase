import streamlit as st
import pandas as pd
import base64
import os
import time

# --- CẤU HÌNH BAN ĐẦU & TRẠNG THÁI ---
st.set_page_config(
    page_title="Tổ Bảo Dưỡng Số 1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Khởi tạo session state
if 'video_ended' not in st.session_state:
    st.session_state.video_ended = False
if 'page' not in st.session_state:
    st.session_state.page = 'home' # <-- TRANG ĐIỀU HƯỚNG CHÍNH
if "video_played_part" not in st.session_state: # Trạng thái video trang Part Number
    st.session_state.video_played_part = False
if "show_main_part" not in st.session_state:
    st.session_state.show_main_part = False


# --- CÁC HÀM TIỆN ÍCH DÙNG CHUNG ---

def get_base64_encoded_file(file_path):
    """Đọc file và trả về Base64 encoded string."""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return None
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    except Exception as e:
        return None

def load_and_clean(excel_file, sheet):
    """Tải và làm sạch DataFrame từ Excel sheet."""
    df = pd.read_excel(excel_file, sheet_name=sheet)
    df.columns = df.columns.str.strip().str.upper()
    df = df.replace(r'^\s*$', pd.NA, regex=True).dropna(how="all")
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].fillna("").astype(str).str.strip()
    return df

# --- PHẦN MUSIC PLAYER (ĐƯỢC GỌI BỞI CẢ 2 TRANG) ---

def render_music_player(logo_base64):
    """Render thanh Music Player và CSS/JS liên quan."""

    # Mã hóa các file nhạc nền (Music Player)
    music_files = []
    for i in range(1, 7):
        music_base64 = get_base64_encoded_file(f"background{{i}}.mp3")
        if music_base64:
            music_files.append(music_base64)
    
    music_sources_js = ",\n        ".join([f"'data:audio/mp3;base64,{music}'" for music in music_files]) if len(music_files) > 0 else ""

    # CSS cho Music Player (phải định nghĩa lại để sử dụng logo_base64)
    music_player_css = f"""
    <style>
    @keyframes neon-border-pulse {{
        0%, 100% {{ border-color: #00ffff; box-shadow: 0 0 5px #00ffff, 0 0 10px #00ffff; }}
        50% {{ border-color: #00ccff; box-shadow: 0 0 2px #00ccff, 0 0 5px #00ccff; }}
    }}

    .stApp {{
        --logo-bg-url: url('data:image/jpeg;base64,{logo_base64}');
    }}
    
    #music-player-container {{
        position: fixed; bottom: 20px; right: 20px; width: 350px; padding: 8px 16px;
        background: rgba(0, 0, 0, 0.7); border-radius: 12px; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7);
        z-index: 999; opacity: 1; transform: translateY(0); transition: none; /* KHÔNG CẦN CHUYỂN ĐỘNG Ở ĐÂY */
    }}
    #music-player-container::before {{
        content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%; margin: -3px;
        width: calc(100% + 6px); height: calc(100% + 6px); background-image: var(--logo-bg-url);
        background-size: cover; background-position: center; filter: contrast(110%) brightness(90%);
        opacity: 0.4; z-index: -1; border-radius: 12px; box-sizing: border-box; border: 3px solid #00ffff;
        animation: neon-border-pulse 4s infinite alternate;
    }}
    #music-player-container * {{ position: relative; z-index: 5; }}
    #music-player-container .controls,
    #music-player-container .time-info {{ color: #fff; text-shadow: 0 0 7px #000; }}
    #music-player-container .controls {{ display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 6px; }}
    #music-player-container .control-btn {{
        background: rgba(255, 255, 255, 0.2); border: 2px solid #FFFFFF; color: #FFD700; width: 32px;
        height: 32px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center;
        transition: all 0.3s ease; font-size: 14px;
    }}
    #music-player-container .control-btn:hover {{ background: rgba(255, 215, 0, 0.5); transform: scale(1.15); }}
    #music-player-container .control-btn.play-pause {{ width: 40px; height: 40px; font-size: 18px; }}
    #music-player-container .progress-container {{ width: 100%; height: 5px; background: rgba(0, 0, 0, 0.5); border-radius: 3px; cursor: pointer; margin-bottom: 4px; position: relative; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.4); }}
    #music-player-container .progress-bar {{ height: 100%; background: linear-gradient(90deg, #FFD700, #FFA500); border-radius: 3px; width: 0%; transition: width 0.1s linear; }}
    #music-player-container .time-info {{ display: flex; justify-content: space-between; color: rgba(255, 255, 255, 1); font-size: 10px; font-family: monospace; }}

    @media (max-width: 768px) {{
        #music-player-container {{ width: calc(100% - 40px); right: 20px; left: 20px; bottom: 15px; padding: 8px 12px; }}
    }}

    </style>
    """
    st.markdown(music_player_css, unsafe_allow_html=True)

    # JavaScript để quản lý Audio (nhúng trực tiếp vào trang)
    music_player_js = f"""
    <script>
        // Chỉ chạy nếu Player chưa được khởi tạo
        if (!window.musicPlayerInitialized) {{
            const musicSources = [{music_sources_js}];
            const playPauseBtn = document.getElementById('play-pause-btn');
            const prevBtn = document.getElementById('prev-btn');
            const nextBtn = document.getElementById('next-btn');
            const progressBar = document.getElementById('progress-bar');
            const progressContainer = document.getElementById('progress-container');
            const currentTimeEl = document.getElementById('current-time');
            const durationEl = document.getElementById('duration');
            
            if (!playPauseBtn || musicSources.length === 0) {{
                if (durationEl) durationEl.textContent = 'N/A';
                return; 
            }}
            
            let currentTrack = 0;
            // Sử dụng global audio object nếu đã tồn tại từ trang Home (iframe)
            let audio = window.parent.document.getElementById('global-music-audio');
            
            if (!audio) {{
                audio = new Audio();
                audio.id = 'global-music-audio'; // Gán ID để các trang khác tái sử dụng
                audio.volume = 0.3;
                document.body.appendChild(audio); // Thêm vào DOM
            }}

            function loadTrack(index) {{
                // Chỉ đổi src nếu audio chưa được tải hoặc là trang chủ mới khởi tạo
                if (audio.src !== musicSources[index]) {{
                    audio.src = musicSources[index];
                    audio.load(); 
                }}
            }}
            
            function togglePlayPause() {{
                if (!audio.paused) {{
                    audio.pause();
                    playPauseBtn.textContent = '▶';
                }} else {{
                    if (!audio.src) {{ loadTrack(currentTrack); }}
                    audio.load(); 
                    audio.play().then(() => {{
                        playPauseBtn.textContent = '⏸';
                    }}).catch(e => {{
                        console.error("Play error:", e);
                        alert("❌ Lỗi phát nhạc: Kiểm tra lại file MP3 hoặc Base64. (Chi tiết lỗi: " + e.message + ")");
                        playPauseBtn.textContent = '▶';
                    }});
                }}
            }}
            
            function updatePlayerUI() {{
                 // Đồng bộ trạng thái UI khi chuyển trang
                 if (!audio.paused) {{
                    playPauseBtn.textContent = '⏸';
                 }} else {{
                    playPauseBtn.textContent = '▶';
                 }}
                 const progress = (audio.currentTime / audio.duration) * 100;
                 if (!isNaN(progress)) progressBar.style.width = progress + '%';
                 currentTimeEl.textContent = formatTime(audio.currentTime);
                 if (!isNaN(audio.duration)) durationEl.textContent = formatTime(audio.duration);
                 else durationEl.textContent = '0:00';
            }}

            function formatTime(seconds) {{
                if (isNaN(seconds)) return '0:00';
                const mins = Math.floor(seconds / 60);
                const secs = Math.floor(seconds % 60);
                return `${{mins}}:${{secs.toString().padStart(2, '0')}}`;
            }}

            // Gắn sự kiện (chỉ 1 lần)
            if (!window.audioListenersAdded) {{
                audio.addEventListener('timeupdate', () => {{
                    const progress = (audio.currentTime / audio.duration) * 100;
                    progressBar.style.width = progress + '%';
                    currentTimeEl.textContent = formatTime(audio.currentTime);
                }});
                audio.addEventListener('loadedmetadata', () => {{ durationEl.textContent = formatTime(audio.duration); }});
                audio.addEventListener('ended', () => {{ nextTrack(); }});
                window.audioListenersAdded = true;
            }}
            
            // Hàm chuyển bài (giữ nguyên logic)
            function nextTrack() {{
                currentTrack = (currentTrack + 1) % musicSources.length;
                loadTrack(currentTrack);
                if (!audio.paused) {{ audio.play().catch(e => console.error("Next track play error:", e)); }}
            }}
            function prevTrack() {{
                currentTrack = (currentTrack - 1 + musicSources.length) % musicSources.length;
                loadTrack(currentTrack);
                if (!audio.paused) {{ audio.play().catch(e => console.error("Prev track play error:", e)); }}
            }}

            playPauseBtn.addEventListener('click', togglePlayPause);
            nextBtn.addEventListener('click', nextTrack);
            prevBtn.addEventListener('click', prevTrack);
            progressContainer.addEventListener('click', (e) => {{
                if (audio.duration) {{
                    const rect = progressContainer.getBoundingClientRect();
                    const percent = (e.clientX - rect.left) / rect.width;
                    audio.currentTime = percent * audio.duration;
                }}
            }});

            // Khởi tạo và đồng bộ UI
            updatePlayerUI();
            
            window.musicPlayerInitialized = true;
        }}
    </script>
    """
    
    # Hiển thị HTML Player
    st.markdown("""
    <div id="music-player-container">
        <div class="controls">
            <button class="control-btn" id="prev-btn">⏮</button>
            <button class="control-btn play-pause" id="play-pause-btn">▶</button>
            <button class="control-btn" id="next-btn">⏭</button>
        </div>
        <div class="progress-container" id="progress-container">
            <div class="progress-bar" id="progress-bar"></div>
        </div>
        <div class="time-info">
            <span id="current-time">0:00</span>
            <span id="duration">0:00</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Nhúng JavaScript
    st.components.v1.html(music_player_js, height=0)

# --- HÀM RENDER TRANG CHỦ (HOME PAGE) ---
def render_home_page():
    # Mã hóa các file media chính (bắt buộc cho Home Page)
    try:
        video_pc_base64 = get_base64_encoded_file("airplane.mp4")
        video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
        audio_base64 = get_base64_encoded_file("plane_fly.mp3")
        bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
        bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
        logo_base64 = get_base64_encoded_file("logo.jpg")

        if not all([video_pc_base64, video_mobile_base64, audio_base64, bg_pc_base64, bg_mobile_base64]):
            st.error("⚠️ Thiếu một số file media bắt buộc cho Trang Chủ.")
            st.stop()
            
    except Exception as e:
        st.error(f"❌ Lỗi khi đọc file media: {{str(e)}}")
        st.stop()

    if not logo_base64: logo_base64 = "" 

    # --- PHẦN 1: NHÚNG FONT VÀ CSS CHUNG ---
    font_links = """
    <link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Electrolize&display=swap" rel="stylesheet">
    """
    st.markdown(font_links, unsafe_allow_html=True)

    # CSS (Chứa logic ảnh nền và hiệu ứng)
    hide_streamlit_style = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sacramento&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Electrolize&display=swap');

    /* Ẩn các thành phần mặc định của Streamlit */
    #MainMenu, footer, header {{visibility: hidden;}}

    .main {{ padding: 0; margin: 0; }}
    div.block-container {{ padding: 0; margin: 0; max-width: 100% !important; }}

    /* Iframe Video Intro */
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
        width: 1px !important;
    }}

    .stApp {{
        --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
        --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
        /* logo_base64 được định nghĩa trong render_music_player */
    }}

    .reveal-grid {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        display: grid; grid-template-columns: repeat(20, 1fr);	grid-template-rows: repeat(12, 1fr);
        z-index: 500; pointer-events: none;	
    }}
    .grid-cell {{ background-color: white; opacity: 1; transition: opacity 0.5s ease-out; }}
    .main-content-revealed {{
        background-image: var(--main-bg-url-pc); background-size: cover; background-position: center;
        background-attachment: fixed; filter: sepia(60%) grayscale(20%) brightness(85%) contrast(110%);	
        transition: filter 2s ease-out;	
    }}

    @media (max-width: 768px) {{
        .main-content-revealed {{ background-image: var(--main-bg-url-mobile); }}
        .reveal-grid {{ grid-template-columns: repeat(10, 1fr); grid-template-rows: repeat(20, 1fr); }}
    }}

    @keyframes scrollText {{ 0% {{ transform: translate(100vw, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
    @keyframes colorShift {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}

    #main-title-container {{
        position: fixed; top: 5vh; left: 0; width: 100%; height: 10vh;
        overflow: hidden; z-index: 20; pointer-events: none; opacity: 0; transition: opacity 2s;
    }}
    .video-finished #main-title-container {{ opacity: 1; }}

    #main-title-container h1 {{
        font-family: 'Playfair Display', serif; font-size: 3.5vw; margin: 0; font-weight: 900;
        letter-spacing: 5px; white-space: nowrap; display: inline-block;
        background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
        background-size: 400% 400%; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: colorShift 10s ease infinite, scrollText 15s linear infinite; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }}
    
    @media (max-width: 768px) {{
        #main-title-container h1 {{ font-size: 6.5vw; animation-duration: 8s; }}
    }}
    
    /* Music player chỉ hiện thị sau khi video kết thúc trên trang home */
    .video-finished #music-player-container {{
        opacity: 1;
        transform: translateY(0);
        transition: opacity 1s ease-out 2s, transform 1s ease-out 2s; 
    }}

    /* CSS cho các link */
    .content-links-container {{
        position: fixed; top: 30vh; width: 100%; z-index: 10; display: flex;
        justify-content: space-between; align-items: flex-start; padding: 0 0;
        box-sizing: border-box; pointer-events: none; opacity: 0; transition: opacity 2s ease-out 3s;
    }}
    .video-finished .content-links-container {{ opacity: 1; pointer-events: auto; }}
    #link-part-number {{ margin-right: auto; margin-left: 8vw; }}
    #link-quiz-bank {{ margin-left: auto; margin-right: 8vw; }}

    .container-link {{
        display: inline-block; padding: 10px 15px; text-align: center; text-decoration: none;
        color: #00ffff; font-family: 'Playfair Display', serif; font-size: 2.2rem;
        font-weight: 700; cursor: pointer; background-color: rgba(0, 0, 0, 0.4);
        border: 2px solid #00ffff; border-radius: 8px; box-sizing: border-box;
        text-shadow: 0 0 4px rgba(0, 255, 255, 0.8), 0 0 10px rgba(34, 141, 255, 0.6);
        box-shadow: 0 0 5px #00ffff, 0 0 15px rgba(0, 255, 255, 0.5);
        transition: transform 0.3s ease, color 0.3s ease, text-shadow 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    }}

    .container-link:hover {{
        transform: scale(1.05); color: #ffd700; border-color: #ffd700;
        box-shadow: 0 0 5px #ffd700, 0 0 15px #ff8c00, 0 0 25px rgba(255, 215, 0, 0.7);
        text-shadow: 0 0 3px #ffd700, 0 0 8px #ff8c00;
    }}
    </style>
    """

    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


    # JavaScript (Có thêm logic chuyển trang)
    js_callback_video = f"""
    <script>
        console.log("Home Script loaded");
        
        // Hàm gửi tín hiệu chuyển trang về Streamlit Python
        function sendPageChange(pageName) {{
            window.parent.document.dispatchEvent(new CustomEvent('streamlit:setPage', {{ detail: pageName }}));
        }}

        function switchToPartNumber() {{
            sendPageChange('part_number');
        }}
        
        function switchToQuizBank() {{
            alert("Trang Ngân hàng trắc nghiệm đang được xây dựng!");
        }}
        
        function sendBackToStreamlit() {{
            console.log("Video ended or skipped, revealing main content");
            const stApp = window.parent.document.querySelector('.stApp');
            if (stApp) {{
                stApp.classList.add('video-finished', 'main-content-revealed');
            }}
            initRevealEffect();
            // Không gọi initMusicPlayer ở đây nữa, mà gọi ở parent DOM
        }}
        
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
            const waitForElements = setInterval(() => {{
                const video = document.getElementById('intro-video');
                const audio = document.getElementById('background-audio');
                const introTextContainer = document.getElementById('intro-text-container');
                
                if (video && audio && introTextContainer) {{
                    clearInterval(waitForElements);
                    
                    const isMobile = window.innerWidth <= 768;
                    const videoSource = isMobile ? 'data:video/mp4;base64,{video_mobile_base64}' : 'data:video/mp4;base64,{video_pc_base64}';

                    video.src = videoSource;
                    audio.src = 'data:audio/mp3;base64,{audio_base64}';

                    const tryToPlay = () => {{
                        video.play().catch(err => {{ setTimeout(sendBackToStreamlit, 2000); }});
                        audio.play().catch(e => {{}});
                    }};

                    video.addEventListener('canplaythrough', tryToPlay, {{ once: true }});
                    video.addEventListener('ended', () => {{
                        video.style.opacity = 0; audio.pause(); audio.currentTime = 0; introTextContainer.style.opacity = 0;	
                        setTimeout(sendBackToStreamlit, 500);
                    }});
                    video.addEventListener('error', (e) => {{ sendBackToStreamlit(); }});

                    const clickHandler = () => {{
                        tryToPlay();
                        document.removeEventListener('click', clickHandler);
                        document.removeEventListener('touchstart', clickHandler);
                    }};
                    
                    document.addEventListener('click', clickHandler, {{ once: true }});
                    document.addEventListener('touchstart', clickHandler, {{ once: true }});
                    
                    video.load();	
                    const chars = introTextContainer.querySelectorAll('.intro-char');
                    chars.forEach((char, index) => {{
                        char.style.animationDelay = `${{index * 0.1}}s`;	
                        char.classList.add('char-shown');	
                    }});
                }}
            }}, 100);
        }});
    </script>
    """
    
    # Mã HTML/CSS cho Video Intro
    html_content_modified = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            html, body {{ margin: 0; padding: 0; overflow: hidden; height: 100vh; width: 100vw; background-color: #000; }}
            #intro-video {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: 0; transition: opacity 1s; }}
            #intro-text-container {{	position: fixed; top: 5vh; width: 100%; text-align: center; color: #FFD700; font-size: 3vw; font-family: 'Sacramento', cursive; text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.8); z-index: 100; pointer-events: none; display: flex; justify-content: center; opacity: 1; transition: opacity 0.5s; }}
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

    # --- HIỂN THỊ IFRAME VIDEO ---
    st.components.v1.html(html_content_modified, height=1080, scrolling=False)


    # --- HIỆU ỨNG REVEAL VÀ NỘI DUNG CHÍNH ---
    grid_cells_html = "".join([f'<div class="grid-cell"></div>' for i in range(240)])
    reveal_grid_html = f'<div class="reveal-grid">{grid_cells_html}</div>'
    st.markdown(reveal_grid_html, unsafe_allow_html=True)


    # --- TIÊU ĐỀ CHÍNH ---
    st.markdown(f"""
    <div id="main-title-container">
        <h1>TỔ BẢO DƯỠNG SỐ 1</h1>
    </div>
    """, unsafe_allow_html=True)


    # --- TIÊU ĐỀ PHỤ (CÓ CLICK CHUYỂN TRANG) ---
    st.markdown("""
    <div class="content-links-container">
        <div class="container-link" id="link-part-number" onclick="switchToPartNumber()">
            Tra cứu part number 🔍
        </div>
        <div class="container-link" id="link-quiz-bank" onclick="switchToQuizBank()">
            Ngân hàng trắc nghiệm 📋✅
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- MUSIC PLAYER ---
    render_music_player(logo_base64)


    # Nội dung placeholder
    st.markdown("<h2 style='text-align: center; color: white; opacity: 0; transition: opacity 2s 3s;'>Nội dung chính của Trang (sẽ xuất hiện bên dưới)</h2>", unsafe_allow_html=True)


# --- HÀM RENDER TRANG TRA CỨU PART NUMBER ---

def render_part_number_page():
    
    excel_file = "A787.xlsx"
    if not os.path.exists(excel_file):
        st.error("❌ Không tìm thấy file A787.xlsx")
        st.stop()

    xls = pd.ExcelFile(excel_file)
    # Đã đổi tên file nền thành partnumber.jpg
    bg_img_base64 = get_base64_encoded_file("partnumber.jpg") if os.path.exists("partnumber.jpg") else ""
    logo_base64 = get_base64_encoded_file("logo.jpg") if os.path.exists("logo.jpg") else ""
    
    # === CSS PHONG CÁCH VINTAGE ===
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Special+Elite&display=swap');
    
    /* Quay lại trang chủ */
    .back-to-home-btn {{
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 100;
        background: #6d4c41;
        color: #fff8e1;
        border: 2px solid #3e2723;
        padding: 10px 15px;
        border-radius: 8px;
        cursor: pointer;
        font-family: 'Special Elite', cursive;
        font-size: 18px;
        box-shadow: 4px 4px 0 #3e2723;
        transition: all 0.2s ease;
    }}
    .back-to-home-btn:hover {{
        background: #5d4037;
        box-shadow: 2px 2px 0 #3e2723;
        transform: translate(2px, 2px);
    }}

    .stApp {{
        font-family: 'Special Elite', cursive !important;
        background:
            linear-gradient(rgba(245, 242, 230, 0.5), rgba(245, 242, 230, 0.5)),
            url("data:image/jpeg;base64,{bg_img_base64}") no-repeat center center fixed; /* ĐÃ DÙNG partnumber.jpg */
        background-size: cover;
    }}
    /* Bỏ qua phần CSS cũ của trang home để tránh ghi đè */
    
    /* ... Các style khác cho trang Part Number giữ nguyên ... */
    
    .stApp::after {{
        content: ""; position: fixed; inset: 0;
        background: url("https://www.transparenttextures.com/patterns/aged-paper.png");
        opacity: 0.2; pointer-events: none; z-index: -1;
    }}

    header[data-testid="stHeader"] {{ display: none; }}
    .block-container {{ padding-top: 0 !important; }}

    .main-title {{ font-size: 48px; font-weight: bold; text-align: center; color: #3e2723; margin-top: 25px; text-shadow: 2px 2px 0 #fff, 0 0 25px #f0d49b, 0 0 50px #bca27a; }}
    .sub-title {{ font-size: 34px; text-align: center; color: #6d4c41; margin-top: 5px; margin-bottom: 25px; letter-spacing: 1px; animation: glowTitle 3s ease-in-out infinite alternate; }}
    @keyframes glowTitle {{
        from {{ text-shadow: 0 0 10px #bfa67a, 0 0 20px #d2b48c, 0 0 30px #e6d5a8; color: #4e342e; }}
        to {{ text-shadow: 0 0 20px #f8e1b4, 0 0 40px #e0b97d, 0 0 60px #f7e7ce; color: #5d4037; }}
    }}

    /* === FORM STYLE === */
    .stSelectbox label {{ font-weight: bold !important; font-size: 22px !important; color: #4e342e !important; }}
    .stSelectbox div[data-baseweb="select"] {{
        font-size: 18px !important; color: #3e2723 !important; background: #fdfbf5 !important;
        border: 2px dashed #5d4037 !important; border-radius: 8px !important; min-height: 50px !important;
        transition: transform 0.2s ease;
    }}
    .stSelectbox div[data-baseweb="select"]:hover {{ transform: scale(1.02); box-shadow: 0 0 12px rgba(100, 80, 60, 0.3); }}

    /* === BẢNG KẾT QUẢ === */
    table.dataframe {{ width: 100%; border-collapse: collapse; background: rgba(255,255,255,0.88); backdrop-filter: blur(2px); font-size: 18px; }}
    table.dataframe thead th {{ background: #6d4c41; color: #fff8e1; padding: 14px; border: 2px solid #3e2723; font-size: 19px; text-align: center; }}
    table.dataframe tbody td {{ border: 1.8px solid #5d4037; padding: 12px; font-size: 18px; color: #3e2723; text-align: center; }}
    table.dataframe tbody tr:nth-child(even) td {{ background: rgba(248, 244, 236, 0.85); }}
    table.dataframe tbody tr:hover td {{ background: rgba(241, 224, 198, 0.9); transition: 0.3s; }}
    .highlight-msg {{ font-size: 20px; font-weight: bold; color: #3e2723; background: rgba(239, 235, 233, 0.9); padding: 12px 18px; border-left: 6px solid #6d4c41; border-radius: 8px; margin: 18px 0; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

    
    # Thêm nút quay lại trang chủ
    if st.button("⬅️ Quay lại Trang Chủ", key="back_home_part", help="Trở về màn hình giới thiệu", disabled=False, type="secondary"):
        st.session_state.page = 'home'
        st.query_params.clear()
        st.rerun()

    # --- MUSIC PLAYER ---
    if logo_base64:
        render_music_player(logo_base64)
    # Lưu ý: Đã bỏ phần nhạc nền và thanh audio riêng của trang Part Number.

    # ===== TIÊU ĐỀ =====
    st.markdown('<div class="main-title">📜 TỔ BẢO DƯỠNG SỐ 1</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">🔎 TRA CỨU PART NUMBER</div>', unsafe_allow_html=True)


    # ===== NỘI DUNG CHÍNH =====
    zone = st.selectbox("📂 Bạn muốn tra cứu zone nào?", xls.sheet_names)
    if zone:
        df = load_and_clean(excel_file, zone)

        if "A/C" in df.columns:
            aircrafts = sorted([ac for ac in df["A/C"].dropna().unique().tolist() if ac])
            aircraft = st.selectbox("✈️ Loại máy bay?", aircrafts)
        else:
            aircraft = None

        if aircraft:
            df_ac = df[df["A/C"] == aircraft]

            if "DESCRIPTION" in df_ac.columns:
                desc_list = sorted([d for d in df_ac["DESCRIPTION"].dropna().unique().tolist() if d])
                description = st.selectbox("📑 Bạn muốn tra cứu phần nào?", desc_list)
            else:
                description = None

            if description:
                df_desc = df_ac[df_ac["DESCRIPTION"] == description]

                if "ITEM" in df_desc.columns:
                    items = sorted([i for i in df_desc["ITEM"].dropna().unique().tolist() if i])
                    item = st.selectbox("🔢 Bạn muốn tra cứu Item nào?", items)
                    df_desc = df_desc[df_desc["ITEM"] == item]

                df_desc = df_desc.drop(columns=["A/C", "ITEM", "DESCRIPTION"], errors="ignore")
                df_desc = df_desc.replace(r'^\s*$', pd.NA, regex=True).dropna(how="all")

                if not df_desc.empty:
                    df_desc.insert(0, "STT", range(1, len(df_desc) + 1))
                    st.markdown(f'<div class="highlight-msg">✅ Tìm thấy {len(df_desc)} dòng dữ liệu</div>', unsafe_allow_html=True)
                    st.write(df_desc.to_html(escape=False, index=False), unsafe_allow_html=True)
                else:
                    st.warning("📌 Không có dữ liệu phù hợp.")


# --- LOGIC ĐIỀU HƯỚNG CHÍNH CỦA ỨNG DỤNG ---

# Lắng nghe sự kiện chuyển trang từ JavaScript
js_redirect_script = """
<script>
    // Gửi tín hiệu và trigger rerun
    window.parent.document.addEventListener('streamlit:setPage', function(e) {
        if (e.detail) {
            window.parent.location.href = window.parent.location.href.split('?')[0] + '?page=' + e.detail;
        }
    });
</script>
"""
st.markdown(js_redirect_script, unsafe_allow_html=True)


# Kiểm tra query param để đặt lại session state
if 'page' in st.query_params:
    st.session_state.page = st.query_params['page'][0]


if st.session_state.page == 'part_number':
    render_part_number_page() 
elif st.session_state.page == 'quiz_bank':
    st.title("Ngân hàng trắc nghiệm 📋✅")
    st.markdown("---")
    st.markdown("### Trang này đang được xây dựng!")
    if st.button("⬅️ Quay lại Trang Chủ", key="back_home_quiz"):
        st.session_state.page = 'home'
        st.query_params.clear()
        st.rerun()
else: # st.session_state.page == 'home'
    render_home_page()
