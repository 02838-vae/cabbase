import streamlit as st
import base64
import os

st.set_page_config(page_title="Cabbase", page_icon="✈️", layout="wide")

# --- HÀM HỖ TRỢ ---
def get_base64_encoded_file(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# --- LOAD FILE ---
video_pc_base64 = get_base64_encoded_file("airplane.mp4")
video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
audio_base64 = get_base64_encoded_file("background1.mp3")

# --- CSS ---
st.markdown("""
<style>
* {margin: 0; padding: 0; box-sizing: border-box;}
.stApp {
    background: black;
    overflow: hidden;
}

/* --- VIDEO INTRO --- */
#intro-video {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    object-fit: cover;
    z-index: 100;
    transition: opacity 1.5s ease;
}

/* --- CHỮ INTRO --- */
#intro-text-container {
    position: fixed;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    font-size: 4vw;
    font-weight: 700;
    color: white;
    letter-spacing: 3px;
    display: flex;
    gap: 0.2em;
    z-index: 150;
}
.intro-char {
    opacity: 0;
    transform: translateY(20px);
    animation: fadeInUp 0.4s forwards;
}
@keyframes fadeInUp {
    to {opacity: 1; transform: translateY(0);}
}

/* --- BACKGROUND --- */
.video-finished .stApp {
    background: radial-gradient(circle at top left, #001, #003);
}

/* --- TIÊU ĐỀ CHÍNH --- */
#main-title-container {
    position: fixed;
    top: 40%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: white;
    text-align: center;
    opacity: 0;
    transition: opacity 2s ease;
}
.video-finished #main-title-container {
    opacity: 1;
}

/* --- PLAYER NHẠC --- */
#music-player {
    position: fixed;
    bottom: 2vh;
    left: 2vw;
    width: 250px;
    height: 60px;
    background: rgba(0, 0, 0, 0.55);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: space-around;
    padding: 6px 10px;
    backdrop-filter: blur(6px);
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    z-index: 50;
    opacity: 0;
    transition: opacity 2s ease;
}
.video-finished #music-player {
    opacity: 1;
}
#music-player button {
    background: none;
    border: none;
    color: white;
    font-size: 18px;
    cursor: pointer;
    transition: transform 0.2s;
}
#music-player button:hover {
    transform: scale(1.2);
}
#music-player input[type="range"] {
    width: 100px;
    accent-color: #FFD700;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# --- VIDEO INTRO HTML ---
st.markdown(f"""
<video id="intro-video" autoplay muted playsinline></video>
<audio id="background-audio"></audio>
<div id="intro-text-container">
    <span class="intro-char">C</span>
    <span class="intro-char">A</span>
    <span class="intro-char">B</span>
    <span class="intro-char">B</span>
    <span class="intro-char">A</span>
    <span class="intro-char">S</span>
    <span class="intro-char">E</span>
</div>

<div id="main-title-container">
    <h1 style="font-size: 4vw;">CABBASE</h1>
    <h3 style="color: #ccc;">Travel Beyond Horizons</h3>
</div>
""", unsafe_allow_html=True)

# --- JAVASCRIPT CHẠY INTRO ---
js_intro = f"""
<script>
function sendBackToStreamlit() {{
    window.parent.document.querySelector('.stApp').classList.add('video-finished');
}}

document.addEventListener("DOMContentLoaded", () => {{
    const video = document.getElementById("intro-video");
    const audio = document.getElementById("background-audio");
    const intro = document.getElementById("intro-text-container");
    const isMobile = window.innerWidth <= 768;

    if (isMobile) {{
        video.src = "data:video/mp4;base64,{video_mobile_base64}";
    }} else {{
        video.src = "data:video/mp4;base64,{video_pc_base64}";
    }}
    audio.src = "data:audio/mp3;base64,{audio_base64}";

    const playMedia = () => {{
        video.load();
        video.play().catch(() => {{}});
        const chars = intro.querySelectorAll(".intro-char");
        chars.forEach((ch, i) => {{
            ch.style.animationDelay = `${{i * 0.1}}s`;
            ch.classList.add("char-shown");
        }});
        audio.volume = 0.5;
        audio.loop = true;
        audio.play().catch(() => {{}});
    }};
    playMedia();

    video.onended = () => {{
        video.style.opacity = 0;
        intro.style.opacity = 0;
        audio.pause();
        sendBackToStreamlit();
    }};
}});
</script>
"""
st.markdown(js_intro, unsafe_allow_html=True)

# --- MUSIC PLAYER ---
song_base64_list = []
for i in range(1, 7):
    path = f"background{i}.mp3"
    if os.path.exists(path):
        song_base64_list.append(get_base64_encoded_file(path))

if song_base64_list:
    song_sources_js = "[" + ",".join([f"'data:audio/mp3;base64,{b}'" for b in song_base64_list]) + "]"
    music_player_html = f"""
<div id="music-player">
    <button id='prev-btn'>⏮️</button>
    <button id='play-btn'>▶️</button>
    <button id='next-btn'>⏭️</button>
    <input type='range' id='progress-bar' value='0' min='0' max='100'>
</div>

<script>
const playlist = {song_sources_js};
let currentSongIndex = 0;
const audioPlayer = new Audio(playlist[currentSongIndex]);
const playBtn = document.getElementById('play-btn');
const nextBtn = document.getElementById('next-btn');
const prevBtn = document.getElementById('prev-btn');
const progressBar = document.getElementById('progress-bar');
let isPlaying = false;

playBtn.addEventListener('click', () => {{
    if (!isPlaying) {{
        audioPlayer.play();
        playBtn.textContent = '⏸️';
    }} else {{
        audioPlayer.pause();
        playBtn.textContent = '▶️';
    }}
    isPlaying = !isPlaying;
}});

nextBtn.addEventListener('click', () => {{
    currentSongIndex = (currentSongIndex + 1) % playlist.length;
    changeSong();
}});
prevBtn.addEventListener('click', () => {{
    currentSongIndex = (currentSongIndex - 1 + playlist.length) % playlist.length;
    changeSong();
}});
function changeSong() {{
    audioPlayer.src = playlist[currentSongIndex];
    audioPlayer.play();
    isPlaying = true;
    playBtn.textContent = '⏸️';
}}
audioPlayer.addEventListener('timeupdate', () => {{
    if (audioPlayer.duration) {{
        progressBar.value = (audioPlayer.currentTime / audioPlayer.duration) * 100;
    }}
}});
progressBar.addEventListener('input', () => {{
    if (audioPlayer.duration) {{
        audioPlayer.currentTime = (progressBar.value / 100) * audioPlayer.duration;
    }}
}});
audioPlayer.addEventListener('ended', () => {{
    currentSongIndex = (currentSongIndex + 1) % playlist.length;
    changeSong();
}});
</script>
"""
    st.markdown(music_player_html, unsafe_allow_html=True)
