import streamlit as st
import base64
import json

# --- THÔNG TIN GITHUB CỦA BẠN ---
GITHUB_USER = "02838-vae"
GITHUB_REPO = "cabbase"
GITHUB_BRANCH = "main"
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/static"

st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide", initial_sidebar_state="collapsed")

if "video_ended" not in st.session_state:
    st.session_state.video_ended = False


def get_base64_encoded_file(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# --- MÃ HÓA FILE MEDIA ---
video_pc_base64 = get_base64_encoded_file("airplane.mp4")
video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
audio_base64 = get_base64_encoded_file("plane_fly.mp3")
bg_pc_base64 = get_base64_encoded_file("cabbase.jpg")
bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")

music_files = {
    f"background{i}": f"{GITHUB_RAW_BASE}/background{i}.mp3" for i in range(1, 7)
}
music_playlist_json = json.dumps(music_files)

# --- FONT ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;900&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# --- CSS ---
hide_streamlit_style = f"""
<style>
#MainMenu, footer, header {{visibility: hidden;}}
.main {{padding: 0; margin: 0;}}
div.block-container {{padding: 0; margin: 0; max-width: 100% !important;}}

/* Video intro */
iframe:first-of-type {{
    transition: opacity 1s ease-out, visibility 1s ease-out;
    opacity: 1; visibility: visible;
    width: 100vw !important; height: 100vh !important;
    position: fixed; top: 0; left: 0; z-index: 1000;
}}
.video-finished iframe:first-of-type {{
    opacity: 0; visibility: hidden; pointer-events: none; height: 1px !important;
}}

/* Background */
.stApp {{
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
}}

.reveal-grid {{
    position: fixed; top: 0; left: 0;
    width: 100vw; height: 100vh;
    display: grid; grid-template-columns: repeat(20, 1fr);
    grid-template-rows: repeat(12, 1fr);
    z-index: 500;  pointer-events: none;
}}
.grid-cell {{ background-color: white; opacity: 1; transition: opacity 0.5s ease-out; }}

.main-content-revealed {{
    background-image: var(--main-bg-url-pc);
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    filter: sepia(60%) grayscale(20%) brightness(85%) contrast(110%);
    transition: filter 2s ease-out;
}}

/* Title */
#main-title-container {{
    position: fixed; top: 5vh; left: 0; width: 100%; height: 10vh;
    overflow: hidden; z-index: 20; pointer-events: none;
    opacity: 0; transition: opacity 2s;
}}
.video-finished #main-title-container {{ opacity: 1 !important; }}
#main-title-container h1 {{
    font-family: 'Playfair Display', serif;
    font-size: 3.5vw; margin: 0; font-weight: 900; letter-spacing: 5px;
    white-space: nowrap; display: inline-block;
    background: linear-gradient(90deg,#ff0000,#ff7f00,#ffff00,#00ff00,#0000ff,#4b0082,#9400d3);
    background-size: 400% 400%;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; color: transparent;
    animation: colorShift 10s ease infinite, scrollText 15s linear infinite;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}}

/* Player */
#music-player-container {{
    position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
    z-index: 10;
    display: none;
    pointer-events: none;
    opacity: 0;
    height: 80px; width: 170px;
    transition: opacity 1s ease-in-out;
}}
.video-finished #music-player-container {{
    display: block !important;
    opacity: 1 !important;
    pointer-events: auto;
}}

#music-player-container > div {{ display: none; }}
.video-finished #music-player-container > div {{ display: block; }}

@keyframes scrollText {{0% {{transform: translate(100vw,0);}}100%{{transform: translate(-100%,0);}}}}
@keyframes colorShift {{0%{{background-position:0% 50%;}}50%{{background-position:100% 50%;}}100%{{background-position:0% 50%;}}}}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- JAVASCRIPT CHO VIDEO ---
js_callback_video = f"""
<script>
function sendBackToStreamlit() {{
    const stApp = window.parent.document.querySelector('.stApp');
    stApp.classList.add('video-finished','main-content-revealed');
    initRevealEffect();
    try {{
        window.parent.document.querySelector('#music-player-container iframe').contentWindow.togglePlayPause(true);
    }} catch(e) {{
        console.warn("Could not auto-play:", e);
    }}
}}

function initRevealEffect() {{
    const revealGrid = window.parent.document.querySelector('.reveal-grid');
    if (!revealGrid) return;
    const cells = revealGrid.querySelectorAll('.grid-cell');
    const shuffled = Array.from(cells).sort(() => Math.random() - 0.5);
    shuffled.forEach((cell, i) => {{
        setTimeout(() => {{ cell.style.opacity = 0; }}, i * 10);
    }});
    setTimeout(() => {{ revealGrid.remove(); }}, shuffled.length * 10 + 1000);
}}

document.addEventListener("DOMContentLoaded", function() {{
    const video = document.getElementById('intro-video');
    const audio = document.getElementById('background-audio');
    const isMobile = window.innerWidth <= 768;
    video.src = isMobile ? 'data:video/mp4;base64,{video_mobile_base64}' : 'data:video/mp4;base64,{video_pc_base64}';
    audio.src = 'data:audio/mp3;base64,{audio_base64}';
    const playMedia = () => {{
        video.load(); 
        video.play().catch(() => {{ }});
        audio.volume = 0.5; 
        audio.loop = true; 
        audio.play().catch(() => {{ }});
    }};
    playMedia();
    video.onended = () => {{
        video.style.opacity = 0;
        audio.pause();
        sendBackToStreamlit();
    }};
    document.body.addEventListener('click', () => {{
        video.play().catch(() => {{ }});
        audio.play().catch(() => {{ }});
    }}, {{ once: true }});
}});
</script>
"""

intro_title = "KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI"
intro_chars_html = ''.join([f'<span class="intro-char">{c}</span>' if c != ' ' else '<span class="intro-char">&nbsp;</span>' for c in intro_title])

html_content_modified = f"""
<!DOCTYPE html>
<html>
<head>
<style>
html,body{{margin:0;padding:0;overflow:hidden;height:100vh;width:100vw;}}
#intro-video{{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;z-index:-100;transition:opacity 1s;}}
#intro-text-container{{position:fixed;top:5vh;width:100%;text-align:center;color:#FFD700;font-size:3vw;
font-family:'Sacramento',cursive;text-shadow:3px 3px 6px rgba(0,0,0,0.8);z-index:100;}}
.intro-char{{display:inline-block;opacity:0;transform:translateY(-50px);animation:dropIn 0.8s ease-out forwards;}}
@keyframes dropIn{{from{{opacity:0;transform:translateY(-50px);}}to{{opacity:1;transform:translateY(0);}}}}
</style>
</head>
<body>
<div id="intro-text-container">{intro_chars_html}</div>
<video id="intro-video" muted playsinline></video>
<audio id="background-audio"></audio>
{js_callback_video}
</body>
</html>
"""

st.components.v1.html(html_content_modified, height=10, scrolling=False)

# --- LỚP REVEAL ---
grid_cells_html = "".join(["<div class='grid-cell'></div>" for _ in range(240)])
st.markdown(f"<div class='reveal-grid'>{grid_cells_html}</div>", unsafe_allow_html=True)

# --- MAIN TITLE ---
st.markdown('<div id="main-title-container"><h1>TỔ BẢO DƯỠNG SỐ 1</h1></div>', unsafe_allow_html=True)

# --- MUSIC PLAYER ---
custom_music_player_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
body{{margin:0;padding:0;overflow:hidden;background:transparent;}}
.player-container{{display:flex;align-items:center;justify-content:center;padding:10px;
background-color:rgba(0,0,0,0.4);border-radius:8px;width:150px;margin:0 auto;
border:1px solid #FFD700;}}
.player-controls button{{background:none;border:1px solid #FFD700;color:#FFD700;padding:8px 10px;
margin:0 3px;border-radius:5px;cursor:pointer;font-size:14px;transition:0.3s;}}
.player-controls button:hover{{background-color:#FFD700;color:#000;}}
#audio-player{{display:none;}}
</style>
</head>
<body>
<div class="player-container">
<div class="player-controls">
    <button onclick="prevTrack()">&#9664;&#9664;</button>
    <button id="play-pause-btn" onclick="togglePlayPause()">&#9658;</button>
    <button onclick="nextTrack()">&#9658;&#9658;</button>
</div></div>
<audio id="audio-player"></audio>
<script>
const playlistData = {music_playlist_json};
const keys = Object.keys(playlistData);
const audio = document.getElementById('audio-player');
const btn = document.getElementById('play-pause-btn');
let i = 0;
function loadTrack(x) {{ audio.src = playlistData[keys[x]]; audio.load(); }}
function togglePlayPause(force=false) {{
 if(audio.paused || force) {{
   if(!audio.src) loadTrack(i);
   audio.play().then(()=>btn.innerHTML='&#10074;&#10074;').catch(()=>{{}});
 }} else {{
   audio.pause(); btn.innerHTML='&#9658;';
 }}
}}
window.togglePlayPause = togglePlayPause;
function nextTrack() {{ i=(i+1)%keys.length; loadTrack(i); if(!audio.paused) audio.play(); }}
function prevTrack() {{ i=(i-1+keys.length)%keys.length; loadTrack(i); if(!audio.paused) audio.play(); }}
audio.addEventListener('ended', nextTrack);
document.addEventListener('DOMContentLoaded', ()=>loadTrack(i));
</script>
</body>
</html>
"""

st.markdown('<div id="music-player-container">', unsafe_allow_html=True)
st.components.v1.html(custom_music_player_html, height=80)
st.markdown('</div>', unsafe_allow_html=True)
