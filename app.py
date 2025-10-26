import streamlit as st
import base64
import os

st.set_page_config(
    page_title="Tổ Bảo Dưỡng Số 1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def get_base64_encoded_file(file_path):
    """Đọc file và trả về Base64 encoded string."""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Lỗi: Không tìm thấy file media. Vui lòng kiểm tra lại đường dẫn: {e.filename}")

# --- Encode các file media ---
try:
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_intro_base64 = get_base64_encoded_file("plane_fly.mp3")
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg")
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
except FileNotFoundError as e:
    st.error(e)
    st.stop()

# Nhạc playlist trong thư mục songs
song_base64_list = []
for i in range(1, 7):
    path = f"songs/background{i}.mp3"
    if os.path.exists(path):
        song_base64_list.append(get_base64_encoded_file(path))
    else:
        st.warning(f"Không tìm thấy {path}")

# --- Nhúng font ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# --- CSS chính ---
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sacramento&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');

/* Ẩn các thành phần mặc định của Streamlit */
#MainMenu, footer, header {{ visibility: hidden; }}

.main {{ padding: 0; margin: 0; }}
div.block-container {{ padding: 0; margin: 0; max-width: 100% !important; }}

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
    letter-spacing: 5px;
    white-space: nowrap;
    display: inline-block;
    animation: colorShift 10s ease infinite, scrollText 15s linear infinite;
    background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
    background-size: 400% 400%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}}
@media (max-width: 768px) {{
    #main-title-container h1 {{
        font-size: 6.5vw;
        animation-duration: 8s;
    }}
}}

/* --- MUSIC PLAYER góc trái --- */
#music-player {{
    position: fixed;
    bottom: 2vh;
    left: 2vw;
    width: 260px;
    height: 70px;
    background: rgba(0, 0, 0, 0.6);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 12px;
    backdrop-filter: blur(8px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    z-index: 50;
    opacity: 0;
    transition: opacity 2s ease;
}}
.video-finished #music-player {{
    opacity: 1;
}}
#music-player button {{
    background: none;
    border: none;
    color: white;
    font-size: 20px;
    cursor: pointer;
    transition: transform 0.2s;
}}
#music-player button:hover {{
    transform: scale(1.3);
}}
#music-player input[type="range"] {{
    width: 140px;
    accent-color: #FFD700;
    cursor: pointer;
}}
</style>
""", unsafe_allow_html=True)

# --- HTML cho intro và video ---
intro_title = "KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI"
intro_chars_html = ''.join([
    f'<span class="intro-char">{char}</span>' if char != ' ' else '<span class="intro-char">&nbsp;</span>'
    for char in intro_title
])
html_content = f"""
<!DOCTYPE html>
<html>
<head></head>
<body>
    <div id="intro-text-container">{intro_chars_html}</div>
    <video id="intro-video" muted playsinline></video>
    <audio id="background-audio"></audio>
    <div id="main-title-container">
        <h1>TỔ BẢO DƯỠNG SỐ 1</h1>
    </div>
    <!-- Player container will be inserted dynamically below -->
</body>
</html>
"""
st.components.v1.html(html_content + "", height=10, scrolling=False)

# --- JavaScript cho video intro và reveal ---
js_intro = f"""
<script>
function sendBackToStreamlit() {{
    window.parent.document.querySelector('.stApp').classList.add('video-finished', 'main-content-revealed');
}}

document.addEventListener("DOMContentLoaded", () => {{
    const video = document.getElementById("intro-video");
    const audioIntro = document.getElementById("background-audio");
    const introText = document.getElementById("intro-text-container");
    const isMobile = window.innerWidth <= 768;
    if (isMobile) {{
        video.src = "data:video/mp4;base64,{video_mobile_base64}";
    }} else {{
        video.src = "data:video/mp4;base64,{video_pc_base64}";
    }}
    audioIntro.src = "data:audio/mp3;base64,{audio_intro_base64}";
    const playMedia = () => {{
        video.load();
        video.play().catch(() => {{}});
        const chars = introText.querySelectorAll(".intro-char");
        chars.forEach((ch, i) => {{
            ch.style.animationDelay = `${{i * 0.1}}s`;
            ch.classList.add("char-shown");
        }});
        audioIntro.volume = 0.5;
        audioIntro.loop = true;
        audioIntro.play().catch(() => {{}});
    }};
    playMedia();
    video.onended = () => {{
        video.style.opacity = 0;
        introText.style.opacity = 0;
        audioIntro.pause();
        sendBackToStreamlit();
    }};
}});
</script>
"""
st.markdown(js_intro, unsafe_allow_html=True)

# --- Reveal grid ---
grid_cells_html = "".join('<div class="grid-cell"></div>' for _ in range(240))
reveal_grid_html = f'<div class="reveal-grid">{grid_cells_html}</div>'
st.markdown(reveal_grid_html, unsafe_allow_html=True)

# --- Music player logic nếu có playlist ---
if song_base64_list:
    song_sources_js = "[" + ",".join([f"'data:audio/mp3;base64,{b}'" for b in song_base64_list]) + "]"
    music_player_html = f"""
<div id="music-player">
    <button id="prev-btn">⏮️</button>
    <button id="play-btn">▶️</button>
    <button id="next-btn">⏭️</button>
    <input type="range" id="seek-slider" value="0" min="0" max="100">
</div>

<script>
const playlist = {song_sources_js};
let currentIndex = 0;
const audio = new Audio(playlist[currentIndex]);
const playBtn = document.getElementById('play-btn');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const seekSlider = document.getElementById('seek-slider');
let isPlaying = false;

playBtn.addEventListener('click', () => {{
    if (!isPlaying) {{
        audio.play();
        playBtn.textContent = '⏸️';
    }} else {{
        audio.pause();
        playBtn.textContent = '▶️';
    }}
    isPlaying = !isPlaying;
}});

prevBtn.addEventListener('click', () => {{
    currentIndex = (currentIndex - 1 + playlist.length) % playlist.length;
    audio.src = playlist[currentIndex];
    audio.play();
    isPlaying = true;
    playBtn.textContent = '⏸️';
}});

nextBtn.addEventListener('click', () => {{
    currentIndex = (currentIndex + 1) % playlist.length;
    audio.src = playlist[currentIndex];
    audio.play();
    isPlaying = true;
    playBtn.textContent = '⏸️';
}});

audio.addEventListener('timeupdate', () => {{
    if (audio.duration) {{
        seekSlider.value = (audio.currentTime / audio.duration) * 100;
    }}
}});

seekSlider.addEventListener('input', () => {{
    if (audio.duration) {{
        audio.currentTime = (seekSlider.value / 100) * audio.duration;
    }}
}});

audio.addEventListener('ended', () => {{
    currentIndex = (currentIndex + 1) % playlist.length;
    audio.src = playlist[currentIndex];
    audio.play();
}});
</script>
"""
    st.markdown(music_player_html, unsafe_allow_html=True)
