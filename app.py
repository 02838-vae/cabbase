import streamlit as st
import base64

# --- CẤU HÌNH BAN ĐẦU ---
st.set_page_config(
    page_title="Tổ Bảo Dưỡng Số 1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- HÀM TIỆN ÍCH ---
def get_base64_encoded_file(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode("utf-8")

# --- MÃ HÓA MEDIA ---
try:
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg")
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
except FileNotFoundError as e:
    st.error(e)
    st.stop()

# --- FONT ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;900&display=swap" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css" rel="stylesheet">
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
}}

/* === TIÊU ĐỀ === */
#main-title-container {{
    position: fixed;
    top: 5vh;
    left: 0;
    width: 100%;
    text-align: center;
    z-index: 20;
    opacity: 0;
    transition: opacity 2s;
}}
#main-title-container h1 {{
    font-family: 'Playfair Display', serif;
    font-size: 3.5vw;
    font-weight: 900;
    background: linear-gradient(90deg,#ff0000,#ff7f00,#ffff00,#00ff00,#0000ff,#4b0082,#9400d3);
    background-size: 400% 400%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: colorShift 10s ease infinite;
}}
@keyframes colorShift {{
    0% {{background-position: 0% 50%;}}
    50% {{background-position: 100% 50%;}}
    100% {{background-position: 0% 50%;}}
}}
</style>
""", unsafe_allow_html=True)

# --- HTML VIDEO INTRO (GIỮ NGUYÊN) ---
html_intro = f"""
<video id="intro-video" muted playsinline></video>
<audio id="background-audio"></audio>
<script>
document.addEventListener("DOMContentLoaded", () => {{
    const video = document.getElementById('intro-video');
    const audio = document.getElementById('background-audio');
    const isMobile = window.innerWidth <= 768;
    video.src = isMobile ? 'data:video/mp4;base64,{video_mobile_base64}' : 'data:video/mp4;base64,{video_pc_base64}';
    audio.src = 'data:audio/mp3;base64,{audio_base64}';
    video.play();
    audio.loop = true;
    audio.volume = 0.5;
    audio.play();
    video.onended = () => {{
        document.querySelector('.stApp').classList.add('main-content-revealed');
        document.getElementById('main-title-container').style.opacity = 1;
    }};
}});
</script>
"""
st.components.v1.html(html_intro, height=10, scrolling=False)

# --- TIÊU ĐỀ CHÍNH ---
st.markdown("""
<div id="main-title-container">
    <h1>TỔ BẢO DƯỠNG SỐ 1</h1>
</div>
""", unsafe_allow_html=True)

# --- MUSIC PLAYER DƯỚI TIÊU ĐỀ ---
music_files = [f"background{i}.mp3" for i in range(1, 7)]
encoded_musics = []
for file in music_files:
    try:
        encoded_musics.append(get_base64_encoded_file(file))
    except FileNotFoundError:
        st.warning(f"Không tìm thấy {file}")

music_player_html = f"""
<style>
#music-player {{
    position: fixed;
    top: 16vh;
    left: 50%;
    transform: translateX(-50%);
    width: 300px;
    background: rgba(20,20,20,0.7);
    border-radius: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    padding: 15px;
    text-align: center;
    color: white;
    z-index: 50;
    font-family: 'Playfair Display', serif;
}}
.album-art {{
    width: 80px;
    height: 80px;
    border-radius: 50%;
    object-fit: cover;
    margin-bottom: 10px;
    border: 2px solid rgba(255,255,255,0.5);
    animation: spin 10s linear infinite;
}}
@keyframes spin {{
    from {{ transform: rotate(0deg); }}
    to {{ transform: rotate(360deg); }}
}}
.controls {{
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
}}
.controls button {{
    background: none;
    border: none;
    color: white;
    font-size: 1.4rem;
    cursor: pointer;
    transition: transform 0.2s, color 0.2s;
}}
.controls button:hover {{
    transform: scale(1.2);
    color: #ffcc00;
}}
#progress-container {{
    width: 100%;
    height: 5px;
    background: rgba(255,255,255,0.3);
    border-radius: 5px;
    overflow: hidden;
    margin-top: 10px;
}}
#progress {{
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg,#ff4b1f,#ff9068);
}}
</style>

<div id="music-player">
    <img src="https://cdn-icons-png.flaticon.com/512/727/727240.png" class="album-art" id="album-art">
    <div class="controls">
        <button id="prev"><i class="fa-solid fa-backward"></i></button>
        <button id="playpause"><i class="fa-solid fa-play"></i></button>
        <button id="next"><i class="fa-solid fa-forward"></i></button>
    </div>
    <div id="progress-container"><div id="progress"></div></div>
</div>

<script>
const tracks = {encoded_musics};
let current = 0;
let audio = new Audio("data:audio/mp3;base64," + tracks[current]);
let playing = false;
const playBtn = document.getElementById("playpause");
const progressBar = document.getElementById("progress");

function playMusic() {{
    audio.play();
    playing = true;
    playBtn.innerHTML = '<i class="fa-solid fa-pause"></i>';
}}
function pauseMusic() {{
    audio.pause();
    playing = false;
    playBtn.innerHTML = '<i class="fa-solid fa-play"></i>';
}}
function nextTrack() {{
    current = (current + 1) % tracks.length;
    audio.src = "data:audio/mp3;base64," + tracks[current];
    if (playing) playMusic();
}}
function prevTrack() {{
    current = (current - 1 + tracks.length) % tracks.length;
    audio.src = "data:audio/mp3;base64," + tracks[current];
    if (playing) playMusic();
}}
playBtn.addEventListener("click", () => {{ playing ? pauseMusic() : playMusic(); }});
document.getElementById("next").addEventListener("click", nextTrack);
document.getElementById("prev").addEventListener("click", prevTrack);
audio.addEventListener("timeupdate", () => {{
    const progress = (audio.currentTime / audio.duration) * 100;
    progressBar.style.width = progress + "%";
}});
</script>
"""
st.markdown(music_player_html, unsafe_allow_html=True)
