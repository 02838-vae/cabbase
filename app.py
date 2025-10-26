import streamlit as st
import base64
import json

# --- Cấu hình GitHub (giữ nguyên nếu bạn dùng repo đó) ---
GITHUB_USER = "02838-vae"
GITHUB_REPO = "cabbase"
GITHUB_BRANCH = "main"
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/static"

st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide", initial_sidebar_state="collapsed")

# --- Hàm đọc base64 ---
def get_base64_encoded_file(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# --- Nạp video, audio, background ---
video_pc_base64 = get_base64_encoded_file("airplane.mp4")
video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
audio_base64 = get_base64_encoded_file("plane_fly.mp3")
bg_pc_base64 = get_base64_encoded_file("cabbase.jpg")
bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")

music_files = {f"background{i}": f"{GITHUB_RAW_BASE}/background{i}.mp3" for i in range(1, 7)}
music_playlist_json = json.dumps(music_files)

# --- Font ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;900&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# --- CSS ---
css_style = f"""
<style>
#MainMenu, footer, header {{visibility: hidden;}}
.main, div.block-container {{padding: 0; margin: 0; max-width: 100% !important;}}

/* Intro video */
iframe:first-of-type {{
    position: fixed; top: 0; left: 0;
    width: 100vw !important; height: 100vh !important;
    z-index: 1000;
    transition: opacity 1s ease-out, visibility 1s ease-out;
    opacity: 1; visibility: visible;
}}
.video-finished iframe:first-of-type {{
    opacity: 0; visibility: hidden; pointer-events: none; height: 1px !important;
}}

/* Background main */
.stApp {{
    --main-bg-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
    background-color: black;
}}

/* Reveal grid */
.reveal-grid {{
    position: fixed; top: 0; left: 0;
    width: 100vw; height: 100vh;
    display: grid; grid-template-columns: repeat(20, 1fr); grid-template-rows: repeat(12, 1fr);
    z-index: 900; pointer-events: none;
}}
.grid-cell {{
    background: white;
    opacity: 1;
    transition: opacity 0.5s ease-out;
}}

.main-content-revealed {{
    background-image: var(--main-bg-pc);
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    transition: filter 2s ease-out;
    filter: sepia(40%) grayscale(10%) brightness(90%) contrast(105%);
}}

/* Tiêu đề */
#main-title-container {{
    position: fixed; top: 5vh; left: 0; width: 100%;
    text-align: center; opacity: 0; transition: opacity 2s ease-in;
    z-index: 20; pointer-events: none;
}}
.video-finished #main-title-container {{ opacity: 1 !important; }}
#main-title-container h1 {{
    font-family: 'Playfair Display', serif;
    font-size: 3.5vw; letter-spacing: 5px;
    background: linear-gradient(90deg,#ff0000,#ff7f00,#ffff00,#00ff00,#0000ff,#4b0082,#9400d3);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: colorShift 8s infinite linear;
    font-weight: 900;
}}

@keyframes colorShift {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

/* Player */
#music-player-container {{
    position: fixed; bottom: 20px; left: 50%;
    transform: translateX(-50%);
    display: none;
    opacity: 0;
    pointer-events: none;
    z-index: 10;
    transition: opacity 1s ease-in-out;
}}
.video-finished #music-player-container {{
    display: block !important;
    opacity: 1 !important;
    pointer-events: auto;
}}
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# --- JAVASCRIPT ---
js_code = f"""
<script>
function revealMainContent() {{
  const app = window.parent.document.querySelector('.stApp');
  app.classList.add('video-finished','main-content-revealed');
  const grid = window.parent.document.querySelector('.reveal-grid');
  if (grid) {{
    const cells = grid.querySelectorAll('.grid-cell');
    const shuffled = Array.from(cells).sort(() => Math.random() - 0.5);
    shuffled.forEach((cell, i) => {{
      setTimeout(() => cell.style.opacity = 0, i * 10);
    }});
    setTimeout(() => grid.remove(), shuffled.length * 10 + 1200);
  }}
  try {{
    const playerFrame = window.parent.document.querySelector('#music-player-container iframe');
    playerFrame.contentWindow.togglePlayPause(true);
  }} catch(e) {{
    console.warn('Music autoplay blocked:', e);
  }}
}}

document.addEventListener('DOMContentLoaded', () => {{
  const video = document.getElementById('intro-video');
  const audio = document.getElementById('background-audio');
  const isMobile = window.innerWidth <= 768;

  video.src = isMobile ? 'data:video/mp4;base64,{video_mobile_base64}' : 'data:video/mp4;base64,{video_pc_base64}';
  audio.src = 'data:audio/mp3;base64,{audio_base64}';
  audio.loop = true;
  audio.volume = 0.5;

  const startPlayback = () => {{
    video.play().catch(()=>{{}});
    audio.play().catch(()=>{{}});
  }};

  startPlayback();
  document.body.addEventListener('click', startPlayback, {{once:true}});
  video.onended = () => {{
    audio.pause();
    revealMainContent();
  }};
}});
</script>
"""

# --- HTML INTRO ---
intro_html = f"""
<html>
<head>
<style>
html, body {{margin:0;padding:0;overflow:hidden;height:100%;width:100%;background:black;}}
#intro-video {{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;z-index:1;}}
#intro-text-container {{
  position: fixed; top: 10vh; width: 100%; text-align: center;
  font-family: 'Sacramento', cursive; color: #FFD700;
  font-size: 3vw; text-shadow: 3px 3px 6px rgba(0,0,0,0.8);
  z-index: 2;
}}
.intro-char {{
  display:inline-block; opacity:0; transform:translateY(-50px);
  animation: dropIn 0.8s ease-out forwards;
}}
@keyframes dropIn {{
  from {{opacity:0;transform:translateY(-50px);}}
  to {{opacity:1;transform:translateY(0);}}
}}
</style>
</head>
<body>
<div id="intro-text-container">
  {"".join([f"<span class='intro-char'>{c}</span>" if c != ' ' else '<span class=\"intro-char\">&nbsp;</span>' for c in 'KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI'])}
</div>
<video id="intro-video" muted playsinline></video>
<audio id="background-audio"></audio>
{js_code}
</body>
</html>
"""
st.components.v1.html(intro_html, height=10, scrolling=False)

# --- REVEAL GRID ---
grid_html = "".join(["<div class='grid-cell'></div>" for _ in range(240)])
st.markdown(f"<div class='reveal-grid'>{grid_html}</div>", unsafe_allow_html=True)

# --- TITLE ---
st.markdown('<div id="main-title-container"><h1>TỔ BẢO DƯỠNG SỐ 1</h1></div>', unsafe_allow_html=True)

# --- MUSIC PLAYER ---
music_player_html = f"""
<html>
<head>
<style>
body{{margin:0;background:transparent;overflow:hidden;}}
.player-container{{display:flex;align-items:center;justify-content:center;
background-color:rgba(0,0,0,0.4);border:1px solid #FFD700;border-radius:8px;
padding:8px;width:150px;margin:0 auto;}}
button{{background:none;border:1px solid #FFD700;color:#FFD700;padding:6px 8px;
margin:0 4px;border-radius:5px;cursor:pointer;transition:0.3s;}}
button:hover{{background-color:#FFD700;color:#000;}}
#audio-player{{display:none;}}
</style>
</head>
<body>
<div class="player-container">
  <button onclick="prev()">&#9664;&#9664;</button>
  <button id="pp" onclick="toggle()">&#9658;</button>
  <button onclick="next()">&#9658;&#9658;</button>
</div>
<audio id="audio-player"></audio>
<script>
const tracks = {music_playlist_json};
const keys = Object.keys(tracks);
let i = 0;
const audio = document.getElementById('audio-player');
const btn = document.getElementById('pp');
function load(x){{audio.src = tracks[keys[x]];audio.load();}}
function toggle(force=false){{if(audio.paused||force){{if(!audio.src)load(i);audio.play();btn.innerHTML='&#10074;&#10074;';}}else{{audio.pause();btn.innerHTML='&#9658;';}}}}
function next(){{i=(i+1)%keys.length;load(i);if(!audio.paused)audio.play();}}
function prev(){{i=(i-1+keys.length)%keys.length;load(i);if(!audio.paused)audio.play();}}
audio.addEventListener('ended',next);
document.addEventListener('DOMContentLoaded',()=>load(i));
window.togglePlayPause=toggle;
</script>
</body>
</html>
"""
st.markdown('<div id="music-player-container">', unsafe_allow_html=True)
st.components.v1.html(music_player_html, height=80)
st.markdown('</div>', unsafe_allow_html=True)
