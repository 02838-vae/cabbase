import streamlit as st
import base64
import os
import re 
import time

# --- CẤU HÌNH BAN ĐẦU ---
st.set_page_config(
    page_title="Tổ Bảo Dưỡng Số 1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CÁC HÀM TIỆN ÍCH ---


def get_base64_encoded_file(file_path):
    """Đọc file và trả về Base64 encoded string."""
    path_to_check = os.path.join(os.path.dirname(__file__), file_path)
    
    if not os.path.exists(path_to_check) or os.path.getsize(path_to_check) == 0:
        return None 
    
    try:
        with open(path_to_check, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    except Exception as e:
        return None


# Mã hóa các file media chính (bắt buộc)
try:
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
    logo_base64 = get_base64_encoded_file("logo.jpg")

    missing_files = []
    if not audio_base64: missing_files.append("plane_fly.mp3")
    if not bg_pc_base64: missing_files.append("cabbase.jpg")
    if not bg_mobile_base64: missing_files.append("mobile.jpg")

    if missing_files:
        st.error(f"⚠️ Thiếu các file media cần thiết hoặc file rỗng. Vui lòng kiểm tra lại các file sau trong thư mục:")
        st.write(" - " + "\n - ".join(missing_files))
        st.stop()
        
except Exception as e:
    st.error(f"❌ Lỗi khi đọc file: {str(e)}")
    st.stop()

if not 'logo_base64' in locals() or not logo_base64:
    logo_base64 = "" 

# --- CẤU HÌNH NHẠC NỀN ---
BASE_MUSIC_URL = "https://raw.githubusercontent.com/02838-vae/cabbase/main/"
music_files = [f"{BASE_MUSIC_URL}background{i}.mp3" for i in range(1, 7)]


# --- PHẦN 1: NHÚNG FONT VÀ CSS CHÍNH ---
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

/* Chặn hành vi dblclick và chọn văn bản trên toàn bộ ứng dụng khi video đang chạy */
.stApp.video-running * {{
    user-select: none;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    cursor: default !important; 
}}

/* Logo cho music player */
.stApp {{
    --logo-bg-url: url('data:image/jpeg;base64,{logo_base64}');
}}

/* Xóa background mặc định - JS sẽ set background */
body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main,
[data-testid="stAppViewContainer"] > div,
[data-testid="stMain"] > div,
.block-container {{
    background-color: transparent !important;
    background-image: none !important;
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
    background-color: #111;
    opacity: 1;
    transition: opacity 0.5s ease-out;
}}

@media (max-width: 768px) {{
    body,
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    section.main {{
        background-image: url('data:image/jpeg;base64,{bg_mobile_base64}') !important;
    }}
    .reveal-grid {{
        grid-template-columns: repeat(10, 1fr);
        grid-template-rows: repeat(20, 1fr);
    }}
}}

/* Keyframes cho hiệu ứng chữ chạy đơn */
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

/* Keyframes xoay (bắt buộc phải có) */
@keyframes rotate {{
    to {{ transform: translate(-50%, -50%) rotate(360deg); }}
}}

/* === TIÊU ĐỀ TRANG CHÍNH === */
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
    animation: fadeInUI 1.5s ease-out 2.5s forwards;
}}

@keyframes fadeInUI {{
    to {{ opacity: 1; }}
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

/* 🌟 KEYFRAMES: HIỆU ỨNG TỎA SÁNG MÀU NGẪU NHIÊN */
@keyframes glow-random-color {{
    0%, 57.14%, 100% {{
        box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.3);
    }}
    
    0% {{
        box-shadow: 0 0 10px 4px rgba(255, 0, 0, 0.9), 0 0 20px 8px rgba(255, 0, 0, 0.6), inset 0 0 5px 2px rgba(255, 0, 0, 0.9);
    }}
    
    14.28% {{ 
        box-shadow: 0 0 10px 4px rgba(0, 255, 0, 0.9), 0 0 20px 8px rgba(0, 255, 0, 0.6), inset 0 0 5px 2px rgba(0, 255, 0, 0.9);
    }}
    
    28.56% {{ 
        box-shadow: 0 0 10px 4px rgba(0, 0, 255, 0.9), 0 0 20px 8px rgba(0, 0, 255, 0.6), inset 0 0 5px 2px rgba(0, 0, 255, 0.9);
    }}

    42.84% {{ 
        box-shadow: 0 0 10px 4px rgba(255, 255, 0, 0.9), 0 0 20px 8px rgba(255, 255, 0, 0.6), inset 0 0 5px 2px rgba(255, 255, 0, 0.9);
    }}
    
    57.14% {{ 
        box-shadow: 0 0 10px 4px rgba(255, 0, 255, 0.9), 0 0 20px 8px rgba(255, 0, 255, 0.6), inset 0 0 5px 2px rgba(255, 0, 255, 0.9);
    }}
}}

/* === MUSIC PLAYER STYLES === */
#music-player-container {{
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 350px; 
    padding: 8px 16px; 
    background: rgba(0, 0, 0, 0.7); 
    border-radius: 12px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7);
    z-index: 999;
    opacity: 0;
    transform: translateY(100px);
    animation: slideUpMusic 1s ease-out 3s forwards;
}}

@keyframes slideUpMusic {{
    to {{ opacity: 1; transform: translateY(0); }}
}}

#music-player-container::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    margin: -3px;
    width: calc(100% + 6px);
    height: calc(100% + 6px);
    
    background-image: var(--logo-bg-url);
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    filter: contrast(110%) brightness(90%);
    opacity: 0.4; 
    z-index: -1; 
    
    border-radius: 12px;
    
    box-sizing: border-box; 
    animation: glow-random-color 7s linear infinite;
}}

#music-player-container * {{
    position: relative;
    z-index: 5; 
}}

.video-finished #music-player-container {{
    opacity: 1;
    transform: translateY(0);
}}

#music-player-container .controls,
#music-player-container .time-info {{
    color: #fff;
    text-shadow: 0 0 7px #000;
}}

#music-player-container .controls {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin-bottom: 6px; 
}}

#music-player-container .control-btn {{
    background: rgba(255, 255, 255, 0.2);
    border: 2px solid #FFFFFF; 
    color: #FFD700;
    width: 32px; 
    height: 32px;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    font-size: 14px;
}}

#music-player-container .control-btn:hover {{
    background: rgba(255, 215, 0, 0.5);
    transform: scale(1.15);
}}

#music-player-container .control-btn.play-pause {{
    width: 40px; 
    height: 40px;
    font-size: 18px;
}}

#music-player-container .progress-container {{
    width: 100%;
    height: 5px; 
    background: rgba(0, 0, 0, 0.5);
    border-radius: 3px;
    cursor: pointer;
    margin-bottom: 4px; 
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.4); 
}}

#music-player-container .progress-bar {{
    height: 100%;
    background: linear-gradient(90deg, #FFD700, #FFA500);
    border-radius: 3px;
    width: 0%;
    transition: width 0.1s linear;
}}

#music-player-container .time-info {{
    display: flex;
    justify-content: space-between;
    color: rgba(255, 255, 255, 1);
    font-size: 10px; 
    font-family: monospace;
}}

@media (max-width: 768px) {{
    #music-player-container {{
        width: calc(100% - 40px);
        right: 20px;
        left: 20px;
        bottom: 15px;
        padding: 8px 12px;
    }}
    #music-player-container .control-btn,
    #music-player-container .control-btn.play-pause {{
        width: 36px;
        height: 36px;
        font-size: 16px;
    }}
    #music-player-container .control-btn.play-pause {{
        width: 44px;
        height: 44px;
        font-size: 20px;
    }}
}}

/* ================================================ */
/* === CSS CHO NAVIGATION BUTTONS (FIXED) === */
/* ================================================ */

/* Container chứa buttons */
.nav-buttons-wrapper {{
    position: fixed;
    top: 50%;
    left: 0;
    width: 100%;
    transform: translateY(-50%);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 80px;
    z-index: 10000;
    opacity: 0;
    pointer-events: none;
    animation: fadeInNav 1s ease-out 3s forwards;
}}

@keyframes fadeInNav {{
    to {{ opacity: 1; pointer-events: all; }}
}}

/* Ẩn columns và elements mặc định của Streamlit */
.nav-buttons-wrapper .stColumn {{
    display: contents !important;
}}

.nav-buttons-wrapper [data-testid="column"] {{
    display: contents !important;
}}

/* Reset CSS cho thẻ a trong page_link */
.nav-buttons-wrapper a {{
    all: unset;
    display: flex !important;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    cursor: pointer;
    position: relative;
    transform-origin: center;
    padding: 1rem 2rem;
    border-radius: 9999px;
    min-width: 280px;
    text-decoration: none;
    
    /* Button variables */
    --black-700: hsla(0, 0%, 12%, 1);
    --border_radius: 9999px;
    --transtion: 0.3s ease-in-out;
    --active: 0;
    --hover-color: hsl(40, 60%, 85%);
    --text-color: hsl(0, 0%, 100%);
    
    transform: scale(calc(1 + (var(--active, 0) * 0.2)));
    transition: transform var(--transtion);
}}

/* Background đen của button */
.nav-buttons-wrapper a::before {{
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 100%;
    height: 100%;
    background-color: var(--black-700);
    border-radius: var(--border_radius);
    box-shadow: 
        inset 0 0.5px hsl(0, 0%, 100%), 
        inset 0 -1px 2px 0 hsl(0, 0%, 0%), 
        0px 4px 10px -4px hsla(0, 0%, 0%, calc(1 - var(--active, 0))), 
        0 0 0 calc(var(--active, 0) * 0.375rem) var(--hover-color);
    transition: all var(--transtion);
    z-index: 0;
}}

/* Hiệu ứng sáng bên trong khi hover */
.nav-buttons-wrapper a::after {{
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 90%;
    height: 90%;
    background-color: hsla(40, 60%, 85%, 0.75);
    background-image: 
        radial-gradient(at 51% 89%, hsla(45, 60%, 90%, 1) 0px, transparent 50%), 
        radial-gradient(at 100% 100%, hsla(35, 60%, 80%, 1) 0px, transparent 50%), 
        radial-gradient(at 22% 91%, hsla(35, 60%, 80%, 1) 0px, transparent 50%);
    background-position: top;
    opacity: var(--active, 0);
    border-radius: var(--border_radius);
    transition: opacity var(--transtion);
    z-index: 2;
}}

/* Hover state */
.nav-buttons-wrapper a:hover,
.nav-buttons-wrapper a:focus-visible {{
    --active: 1;
    box-shadow: 0 0 15px 5px var(--hover-color), 0 0 0 0.375rem var(--hover-color);
}}

/* Text styling */
.nav-buttons-wrapper a span {{
    position: relative;
    z-index: 10;
    background-image: linear-gradient(
        90deg, 
        var(--text-color) 0%, 
        hsla(0, 0%, 100%, var(--active, 0.5)) 120%
    );
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    color: transparent;
    font-weight: 600;
    letter-spacing: 1px;
    white-space: nowrap;
    text-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
    font-size: 1.1rem;
    line-height: 1.1rem;
}}

/* SVG icon styling */
.nav-buttons-wrapper a svg {{
    position: relative;
    z-index: 10;
    width: 1.75rem;
    height: 1.75rem;
    color: var(--text-color);
    flex-shrink: 0;
}}

/* Mobile responsive */
@media (max-width: 768px) {{
    .nav-buttons-wrapper {{
        bottom: 120px;
        top: auto;
        left: 50%;
        width: calc(100% - 40px);
        max-width: 450px;
        transform: translateX(-50%);
        flex-direction: column;
        gap: 15px;
        padding: 0;
    }}
    
    .nav-buttons-wrapper a {{
        width: 100%;
        min-width: unset;
        padding: 0.8rem 1.5rem;
    }}
    
    .nav-buttons-wrapper a svg {{
        width: 1.5rem;
        height: 1.5rem;
    }}
}}
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- HIỆU ỨNG REVEAL VÀ NỘI DUNG CHÍNH ---

grid_cells_html = ""
for i in range(240):
    grid_cells_html += f'<div class="grid-cell"></div>'

reveal_grid_html = f"""
<div class="reveal-grid" id="reveal-grid-main">
    {grid_cells_html}
</div>
<script>
(function() {{
    function startReveal() {{
        // Script chạy trong cùng document Streamlit, không cần window.parent
        const revealGrid = document.getElementById('reveal-grid-main');
        if (!revealGrid) {{ return; }}
        const cells = revealGrid.querySelectorAll('.grid-cell');
        const shuffledCells = Array.from(cells).sort(() => Math.random() - 0.5);
        shuffledCells.forEach((cell, index) => {{
            setTimeout(() => {{ cell.style.opacity = 0; }}, index * 10);
        }});
        setTimeout(() => {{
            revealGrid.style.display = 'none';
        }}, shuffledCells.length * 10 + 600);
    }}

    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', startReveal);
    }} else {{
        startReveal();
    }}
}})();
</script>
"""
st.markdown(reveal_grid_html, unsafe_allow_html=True)

# --- INJECT BACKGROUND: div fixed + style tag vào head ---
st.components.v1.html(f"""
<script>
(function() {{
    function injectBackground() {{
        const doc = window.parent.document;
        const isMobile = window.parent.innerWidth <= 768;
        const b64 = isMobile ? '{bg_mobile_base64}' : '{bg_pc_base64}';
        const imgUrl = 'data:image/jpeg;base64,' + b64;

        // 1. Inject div background cố định vào body (không bị override bởi Streamlit)
        let bgDiv = doc.getElementById('__st_bg__');
        if (!bgDiv) {{
            bgDiv = doc.createElement('div');
            bgDiv.id = '__st_bg__';
            doc.body.insertBefore(bgDiv, doc.body.firstChild);
        }}
        bgDiv.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;' +
            'background:url(' + imgUrl + ') center/cover no-repeat;' +
            'filter:sepia(60%) grayscale(20%) brightness(85%) contrast(110%);' +
            'z-index:0;pointer-events:none;';

        // 2. Làm trong suốt tất cả Streamlit containers
        const styleId = '__st_bg_style__';
        let s = doc.getElementById(styleId);
        if (!s) {{ s = doc.createElement('style'); s.id = styleId; doc.head.appendChild(s); }}
        s.textContent =
            'body,.stApp,[data-testid="stAppViewContainer"],' +
            '[data-testid="stMain"],[data-testid="stBottom"],' +
            'section.main,.block-container,' +
            '[data-testid="stHeader"],[data-testid="stDecoration"]' +
            '{{background:transparent!important;background-color:transparent!important;background-image:none!important;}}';
    }}

    injectBackground();
    setTimeout(injectBackground, 100);
    setTimeout(injectBackground, 500);
    setTimeout(injectBackground, 1500);
}})();
</script>
""", height=0)

# --- NỘI DUNG CHÍNH (TIÊU ĐỀ) ---
main_title_text = "TỔ BẢO DƯỠNG SỐ 1"

st.markdown(f"""
<div id="main-title-container">
    <h1>{main_title_text}</h1>
</div>
""", unsafe_allow_html=True)

# --- MUSIC PLAYER ---
if len(music_files) > 0:
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

# Music player JS dùng iframe thật để window.parent hoạt động đúng
if len(music_files) > 0:
    music_sources_js_str = ",".join([f"'{url}'" for url in music_files])
    st.components.v1.html(f"""
<script>
(function() {{
    function initMusicPlayer() {{
        const musicSources = [{music_sources_js_str}];
        if (musicSources.length === 0) return;
        let currentTrack = 0;
        let isPlaying = false;
        const audio = new Audio();
        audio.volume = 0.3;
        const doc = window.parent.document;
        const playPauseBtn = doc.getElementById('play-pause-btn');
        const prevBtn = doc.getElementById('prev-btn');
        const nextBtn = doc.getElementById('next-btn');
        const progressBar = doc.getElementById('progress-bar');
        const progressContainer = doc.getElementById('progress-container');
        const currentTimeEl = doc.getElementById('current-time');
        const durationEl = doc.getElementById('duration');
        if (!playPauseBtn) return;
        function loadTrack(index) {{ audio.src = musicSources[index]; audio.load(); }}
        function togglePlayPause() {{
            if (isPlaying) {{ audio.pause(); playPauseBtn.textContent = '▶'; }}
            else {{ audio.play().catch(e => {{}}); playPauseBtn.textContent = '⏸'; }}
            isPlaying = !isPlaying;
        }}
        function nextTrack() {{ currentTrack = (currentTrack + 1) % musicSources.length; loadTrack(currentTrack); if (isPlaying) audio.play().catch(e => {{}}); }}
        function prevTrack() {{ currentTrack = (currentTrack - 1 + musicSources.length) % musicSources.length; loadTrack(currentTrack); if (isPlaying) audio.play().catch(e => {{}}); }}
        function formatTime(s) {{ if (isNaN(s)) return '0:00'; return Math.floor(s/60)+':'+Math.floor(s%60).toString().padStart(2,'0'); }}
        audio.addEventListener('timeupdate', () => {{ if(progressBar) progressBar.style.width=(audio.currentTime/audio.duration*100)+'%'; if(currentTimeEl) currentTimeEl.textContent=formatTime(audio.currentTime); }});
        audio.addEventListener('loadedmetadata', () => {{ if(durationEl) durationEl.textContent=formatTime(audio.duration); }});
        audio.addEventListener('ended', nextTrack);
        audio.addEventListener('error', nextTrack);
        playPauseBtn.addEventListener('click', togglePlayPause);
        if(nextBtn) nextBtn.addEventListener('click', nextTrack);
        if(prevBtn) prevBtn.addEventListener('click', prevTrack);
        if (progressContainer) progressContainer.addEventListener('click', (e) => {{ const r=progressContainer.getBoundingClientRect(); audio.currentTime=(e.clientX-r.left)/r.width*audio.duration; }});
        loadTrack(0);
    }}
    // Đợi DOM của parent load xong
    setTimeout(initMusicPlayer, 500);
}})();
</script>
""", height=0)

# --- NAVIGATION BUTTONS (SỬA LẠI LOGIC NAVIGATION) ---
st.markdown("""
<div class="nav-buttons-wrapper">
    <a href="/partnumber" class="nav-button" target="_self">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"></path>
        </svg>
        <span>TRA CỨU PART NUMBER</span>
    </a>
    <a href="/bank" class="nav-button" target="_self">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <span>NGÂN HÀNG TRẮC NGHIỆM</span>
    </a>
</div>
""", unsafe_allow_html=True)
