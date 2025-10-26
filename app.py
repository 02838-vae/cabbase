import streamlit as st
import base64
import os

# --- CẤU HÌNH BAN ĐẦU ---
st.set_page_config(
    page_title="Tổ Bảo Dưỡng Số 1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- HÀM ĐỌC FILE ---
def get_base64_encoded_file(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# --- MÃ HÓA FILE ---
try:
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg")
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")

    # Đọc tất cả nhạc trong thư mục songs/
    song_files = [f for f in os.listdir("songs") if f.endswith(".mp3")]
    song_files.sort()
    songs_base64 = [
        f"data:audio/mp3;base64,{get_base64_encoded_file(os.path.join('songs', s))}"
        for s in song_files
    ]
except FileNotFoundError as e:
    st.error(f"Không tìm thấy file: {e.filename}")
    st.stop()

# --- FONT GOOGLE ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;900&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# --- CSS CHÍNH ---
st.markdown(f"""
<style>
#MainMenu, footer, header {{visibility: hidden;}}
.main, div.block-container {{
    padding: 0; margin: 0; max-width: 100% !important;
}}
.stApp {{
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
}}
.stApp.main-content-revealed {{
    background-image: var(--main-bg-url-pc);
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
@media (max-width: 768px) {{
    .stApp.main-content-revealed {{
        background-image: var(--main-bg-url-mobile);
    }}
}}
/* PLAYER CSS */
#music-player-container {{
    position: fixed;
    bottom: 3vh;
    left: 3vw;
    background: rgba(0, 0, 0, 0.6);
    border: 1px solid gold;
    border-radius: 15px;
    padding: 10px 15px;
    display: flex;
    flex-direction: column;
    align-items: center;
    z-index: 9999;
    backdrop-filter: blur(6px);
}}
#player-controls {{
    display: flex;
    align-items: center;
    gap: 15px;
}}
#player-controls button {{
    background: none;
    border: none;
    color: gold;
    font-size: 22px;
    cursor: pointer;
    line-height: 1;
    font-family: 'Segoe UI Emoji', 'Noto Color Emoji', 'Apple Color Emoji', sans-serif !important;
    transition: transform 0.2s, color 0.3s;
}}
#player-controls button:hover {{
    color: white;
    transform: scale(1.2);
}}
#progress-container {{
    width: 120px;
    height: 4px;
    background: rgba(255,255,255,0.3);
    margin-top: 8px;
    border-radius: 2px;
    overflow: hidden;
}}
#progress-bar {{
    height: 100%;
    width: 0%;
    background: gold;
    transition: width 0.2s linear;
}}
</style>
""", unsafe_allow_html=True)

# --- VIDEO INTRO ---
html_intro = f"""
<html>
<body>
    <video id="intro-video" muted playsinline style="width:100vw;height:100vh;object-fit:cover;position:fixed;top:0;left:0;z-index:-1;"></video>
    <audio id="background-audio"></audio>
    <script>
        const video = document.getElementById('intro-video');
        const audio = document.getElementById('background-audio');
        const isMobile = window.innerWidth <= 768;
        video.src = isMobile ? "data:video/mp4;base64,{video_mobile_base64}" : "data:video/mp4;base64,{video_pc_base64}";
        audio.src = "data:audio/mp3;base64,{audio_base64}";
        video.play().catch(()=>{{}});
        audio.play().catch(()=>{{}});
    </script>
</body>
</html>
"""
st.components.v1.html(html_intro, height=10, scrolling=False)

# --- PLAYER HTML + JS ---
songs_js_array = "[" + ",".join([f"'{s}'" for s in songs_base64]) + "]"

music_player_html = f"""
<div id="music-player-container">
    <div id="player-controls">
        <button id="prev-btn" title="Bài trước">&#9198;</button>
        <button id="play-pause-btn" title="Phát/Dừng">&#9654;</button>
        <button id="next-btn" title="Bài tiếp theo">&#9197;</button>
    </div>
    <div id="progress-container">
        <div id="progress-bar"></div>
    </div>
    <audio id="main-music-player"></audio>
</div>

<script>
const songs = {songs_js_array};
let currentSongIndex = 0;
const player = document.getElementById('main-music-player');
const playPauseBtn = document.getElementById('play-pause-btn');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const progressBar = document.getElementById('progress-bar');
player.src = songs[currentSongIndex];

function playSong() {{
    player.play();
    playPauseBtn.innerHTML = '&#9208;'; // Pause icon
}}
function pauseSong() {{
    player.pause();
    playPauseBtn.innerHTML = '&#9654;'; // Play icon
}}
playPauseBtn.addEventListener('click', () => {{
    if (player.paused) playSong(); else pauseSong();
}});
prevBtn.addEventListener('click', () => {{
    currentSongIndex = (currentSongIndex - 1 + songs.length) % songs.length;
    player.src = songs[currentSongIndex];
    playSong();
}});
nextBtn.addEventListener('click', () => {{
    currentSongIndex = (currentSongIndex + 1) % songs.length;
    player.src = songs[currentSongIndex];
    playSong();
}});
player.addEventListener('timeupdate', () => {{
    const progress = (player.currentTime / player.duration) * 100;
    progressBar.style.width = progress + '%';
}});
player.addEventListener('ended', () => {{
    nextBtn.click();
}});
</script>
"""

# --- HIỂN THỊ PLAYER ---
st.components.v1.html(music_player_html, height=120, scrolling=False)

# --- TIÊU ĐỀ CHÍNH ---
st.markdown("""
<div id="main-title-container" style="
position:fixed;top:5vh;left:0;width:100%;text-align:center;z-index:50;
font-family:'Playfair Display',serif;font-size:3.5vw;color:gold;
text-shadow:2px 2px 4px rgba(0,0,0,0.5);letter-spacing:5px;">
TỔ BẢO DƯỠNG SỐ 1
</div>
""", unsafe_allow_html=True)
