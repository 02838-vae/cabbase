import streamlit as st
import base64

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
        raise FileNotFoundError(f"Lỗi: Không tìm thấy file media. Kiểm tra lại đường dẫn: {e.filename}")


# --- MÃ HÓA FILE MEDIA ---
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
font_links = """
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&display=swap" rel="stylesheet">
"""
st.markdown(font_links, unsafe_allow_html=True)


# --- CSS CHÍNH ---
hide_streamlit_style = f"""
<style>
#MainMenu, footer, header {{visibility: hidden;}}

.main, div.block-container {{
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
    top: 0; left: 0;
    width: 100vw; height: 100vh;
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
    white-space: nowrap;
    animation: colorShift 10s ease infinite, scrollText 15s linear infinite;
    background: linear-gradient(90deg, #ff0000, #ffa500, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
    background-size: 400% 400%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}}

@media (max-width: 768px) {{
    #main-title-container h1 {{
        font-size: 6vw;
        animation-duration: 8s;
    }}
}}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- VIDEO INTRO ---
js_callback_video = f"""
<script>
function sendBackToStreamlit() {{
    window.parent.document.querySelector('.stApp').classList.add('video-finished', 'main-content-revealed');
    initRevealEffect();
}}

function initRevealEffect() {{
    const revealGrid = window.parent.document.querySelector('.reveal-grid');
    const mainTitle = window.parent.document.getElementById('main-title-container');
    if (mainTitle) mainTitle.style.opacity = 1;
    if (!revealGrid) return;

    const cells = revealGrid.querySelectorAll('.grid-cell');
    const shuffledCells = Array.from(cells).sort(() => Math.random() - 0.5);
    shuffledCells.forEach((cell, index) => {{
        setTimeout(() => cell.style.opacity = 0, index * 10);
    }});
    setTimeout(() => revealGrid.remove(), shuffledCells.length * 10 + 1000);
}}

document.addEventListener("DOMContentLoaded", function() {{
    const video = document.getElementById('intro-video');
    const audio = document.getElementById('background-audio');
    const introText = document.getElementById('intro-text-container');
    const isMobile = window.innerWidth <= 768;

    video.src = isMobile ? 'data:video/mp4;base64,{video_mobile_base64}' : 'data:video/mp4;base64,{video_pc_base64}';
    audio.src = 'data:audio/mp3;base64,{audio_base64}';

    video.load();
    video.play().catch(()=>{{}});
    audio.volume = 0.5; audio.loop = true; audio.play().catch(()=>{{}});

    video.onended = () => {{
        video.style.opacity = 0;
        audio.pause();
        audio.currentTime = 0;
        introText.style.opacity = 0;
        sendBackToStreamlit();
    }};
}});
</script>
"""

html_content_modified = f"""
<!DOCTYPE html>
<html>
<head>
<style>
html, body {{
    margin: 0; padding: 0; overflow: hidden; height: 100vh; width: 100vw;
}}
#intro-video {{
    position: absolute; top: 0; left: 0;
    width: 100%; height: 100%;
    object-fit: cover; z-index: -100;
}}
#intro-text-container {{
    position: fixed; top: 5vh; width: 100%;
    text-align: center; color: #FFD700;
    font-size: 3vw; font-family: 'Sacramento', cursive;
    text-shadow: 3px 3px 6px rgba(0,0,0,0.8);
    z-index: 100; pointer-events: none;
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
st.components.v1.html(html_content_modified, height=10, scrolling=False)


# --- REVEAL GRID ---
grid_cells_html = "".join('<div class="grid-cell"></div>' for _ in range(240))
st.markdown(f"<div class='reveal-grid'>{grid_cells_html}</div>", unsafe_allow_html=True)


# --- TIÊU ĐỀ TRANG CHÍNH ---
main_title_text = "TỔ BẢO DƯỠNG SỐ 1"
st.markdown(f"""
<div id="main-title-container">
    <h1>{main_title_text}</h1>
</div>
""", unsafe_allow_html=True)


# --- MUSIC PLAYER DƯỚI TIÊU ĐỀ ---
music_player_html = """
<div id="music-player">
  <button class="music-btn" id="prevBtn">⏮️</button>
  <button class="music-btn" id="playPauseBtn">▶️</button>
  <button class="music-btn" id="nextBtn">⏭️</button>
  <div id="track-title">Đang tải...</div>
  <audio id="audio"></audio>
</div>

<style>
#music-player {
    position: fixed;
    top: 16vh;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 15px;
    background: rgba(255,255,255,0.25);
    backdrop-filter: blur(8px);
    border-radius: 40px;
    padding: 10px 25px;
    z-index: 100;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    font-family: 'Playfair Display', serif;
}
.music-btn {
    cursor: pointer;
    border: none;
    background: #ffffff;
    padding: 10px 15px;
    border-radius: 50%;
    font-size: 20px;
    box-shadow: 0 3px 6px rgba(0,0,0,0.2);
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
        top: 12vh;
        padding: 8px 15px;
        gap: 10px;
    }
    #track-title { font-size: 14px; }
}
</style>

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
function playTrack() { audio.play(); playPauseBtn.textContent = "⏸️"; }
function pauseTrack() { audio.pause(); playPauseBtn.textContent = "▶️"; }

playPauseBtn.addEventListener("click", () => {
  if (audio.paused) playTrack(); else pauseTrack();
});
prevBtn.addEventListener("click", () => {
  let idx = currentIndex - 1; if (idx < 0) idx = tracks.length - 1;
  loadTrack(idx); playTrack();
});
nextBtn.addEventListener("click", () => {
  let idx = currentIndex + 1; if (idx >= tracks.length) idx = 0;
  loadTrack(idx); playTrack();
});
audio.addEventListener("ended", () => nextBtn.click());
loadTrack(0);
</script>
"""
st.markdown(music_player_html, unsafe_allow_html=True)
