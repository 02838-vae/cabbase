import streamlit as st
import base64

# --- CẤU HÌNH BAN ĐẦU ---
st.set_page_config(
    page_title="Tổ Bảo Dưỡng Số 1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- TIÊU ĐỀ CHÍNH ---
st.markdown("""
    <h1 style='text-align:center; font-size:45px; font-weight:800; 
    font-family: "Playfair Display", serif; color:#003366; 
    text-shadow:2px 2px 6px rgba(0,0,0,0.3);'>
    ✈️ TỔ BẢO DƯỠNG SỐ 1 ✈️
    </h1>
""", unsafe_allow_html=True)

# --- VIDEO INTRO ---
import platform

video_file = "airplane.mp4" if not st.runtime.exists("mobile") else "mobile.mp4"
with open(video_file, "rb") as f:
    video_bytes = f.read()
video_base64 = base64.b64encode(video_bytes).decode()

video_html = f"""
<video autoplay muted loop playsinline style="width:100%; border-radius:15px;">
  <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
</video>
"""
st.markdown(video_html, unsafe_allow_html=True)

# --- MUSIC PLAYER ---
music_player_html = """
<!DOCTYPE html>
<html>
<head>
<style>
body {
    margin: 0;
    padding: 0;
}
#music-player {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 15px;
    background: rgba(255,255,255,0.35);
    backdrop-filter: blur(8px);
    border-radius: 40px;
    padding: 12px 25px;
    z-index: 9999;
    box-shadow: 0 4px 15px rgba(0,0,0,0.25);
    font-family: 'Playfair Display', serif;
}

.music-btn {
    cursor: pointer;
    border: none;
    background: #ffffff;
    padding: 10px 15px;
    border-radius: 50%;
    font-size: 20px;
    box-shadow: 0 3px 6px rgba(0,0,0,0.25);
    transition: all 0.2s ease;
}
.music-btn:hover {
    transform: scale(1.1);
    background: #f2f2f2;
}

#track-title {
    font-size: 18px;
    color: #222;
    min-width: 140px;
    text-align: center;
    font-weight: 600;
}

@media (max-width: 768px) {
    #music-player {
        bottom: 10px;
        padding: 8px 15px;
        gap: 10px;
    }
    #track-title {
        font-size: 14px;
    }
}
</style>
</head>
<body>

<div id="music-player">
  <button class="music-btn" id="prevBtn">⏮️</button>
  <button class="music-btn" id="playPauseBtn">▶️</button>
  <button class="music-btn" id="nextBtn">⏭️</button>
  <div id="track-title">Đang tải...</div>
  <audio id="audio"></audio>
</div>

<script>
const tracks = [
  { title: "Bản nhạc 1", src: "background1.mp3" },
  { title: "Bản nhạc 2", src: "background2.mp3" },
  { title: "Bản nhạc 3", src: "background3.mp3" },
  { title: "Bản nhạc 4", src: "background4.mp3" },
  { title: "Bản nhạc 5", src: "background5.mp3" },
  { title: "Bản nhạc 6", src: "background6.mp3" }
];

let currentIndex = 0;
const audio = document.getElementById('audio');
const titleEl = document.getElementById('track-title');
const playPauseBtn = document.getElementById('playPauseBtn');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');

function loadTrack(index) {
    currentIndex = index;
    audio.src = tracks[index].src;
    titleEl.textContent = tracks[index].title;
}

function playTrack() {
    audio.play();
    playPauseBtn.textContent = "⏸️";
}

function pauseTrack() {
    audio.pause();
    playPauseBtn.textContent = "▶️";
}

playPauseBtn.addEventListener("click", () => {
    if (audio.paused) {
        playTrack();
    } else {
        pauseTrack();
    }
});

prevBtn.addEventListener("click", () => {
    let idx = currentIndex - 1;
    if (idx < 0) idx = tracks.length - 1;
    loadTrack(idx);
    playTrack();
});

nextBtn.addEventListener("click", () => {
    let idx = currentIndex + 1;
    if (idx >= tracks.length) idx = 0;
    loadTrack(idx);
    playTrack();
});

audio.addEventListener("ended", () => {
    nextBtn.click();
});

loadTrack(0);
</script>

</body>
</html>
"""

import streamlit.components.v1 as components
components.html(music_player_html, height=150)
