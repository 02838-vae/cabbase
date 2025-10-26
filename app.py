import streamlit as st
import os

# ======================
# ⚙️ Cấu hình cơ bản
# ======================
st.set_page_config(page_title="Cabbase Music Player", layout="wide")

# 🔗 Đường dẫn file tĩnh (CDN Streamlit Cloud)
STATIC_URL_BASE = "https://cabbase123.streamlit.app/static"

# Danh sách nhạc
MUSIC_FILES = [
    f"{STATIC_URL_BASE}/background1.mp3",
    f"{STATIC_URL_BASE}/background2.mp3",
    f"{STATIC_URL_BASE}/background3.mp3",
    f"{STATIC_URL_BASE}/background4.mp3",
    f"{STATIC_URL_BASE}/background5.mp3",
    f"{STATIC_URL_BASE}/background6.mp3",
]

# Video intro
VIDEO_FILE = f"{STATIC_URL_BASE}/airplane.mp4"

# ======================
# 🎬 HTML cho video intro
# ======================
html_intro = f"""
<style>
body {{
  margin: 0;
  overflow: hidden;
  background-color: black;
}}
video {{
  width: 100vw;
  height: 100vh;
  object-fit: cover;
}}
</style>

<video id="intro-video" autoplay muted playsinline>
  <source src="{VIDEO_FILE}" type="video/mp4">
</video>

<script>
const video = document.getElementById('intro-video');
video.onended = () => {{
    window.parent.document.querySelector('.stApp').classList.add('video-finished', 'main-content-revealed');
    window.parent.document.getElementById('music-player-container').style.display = 'block';
}};
</script>
"""

# ======================
# ⏩ Hiển thị video intro
# ======================
st.components.v1.html(html_intro, height=800, scrolling=False)

# ======================
# 🎵 Music Player (ẩn ban đầu)
# ======================
st.markdown('<div id="music-player-container" style="display:none;">', unsafe_allow_html=True)

st.markdown("""
<style>
#music-player {{
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(30, 30, 30, 0.9);
  color: white;
  padding: 10px 20px;
  border-radius: 12px;
  box-shadow: 0 0 10px rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  gap: 15px;
  z-index: 9999;
}}
#music-player button {{
  background: none;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
}}
#music-player button:hover {{
  color: #1DB954;
}}
</style>

<div id="music-player">
  <button id="prev">⏮</button>
  <button id="playpause">▶️</button>
  <button id="next">⏭</button>
  <audio id="audio"></audio>
</div>

<script>
const songs = {MUSIC_FILES};
let current = 0;
const audio = document.getElementById('audio');
const playpause = document.getElementById('playpause');
const prev = document.getElementById('prev');
const next = document.getElementById('next');

function loadSong(index) {{
    if (index < 0) index = songs.length - 1;
    if (index >= songs.length) index = 0;
    current = index;
    audio.src = songs[current];
}}

function togglePlay() {{
    if (audio.paused) {{
        audio.play();
        playpause.textContent = '⏸';
    }} else {{
        audio.pause();
        playpause.textContent = '▶️';
    }}
}}

playpause.onclick = togglePlay;
prev.onclick = () => {{ loadSong(current - 1); audio.play(); playpause.textContent = '⏸'; }};
next.onclick = () => {{ loadSong(current + 1); audio.play(); playpause.textContent = '⏸'; }};

audio.onended = () => {{ loadSong(current + 1); audio.play(); }};
loadSong(current);
</script>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
