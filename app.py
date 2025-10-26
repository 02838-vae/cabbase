import streamlit as st
import base64
import json

# --- THÔNG TIN GITHUB ---
GITHUB_USER = "02838-vae" 
GITHUB_REPO = "cabbase"       
GITHUB_BRANCH = "main"        
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/static"

# --- CẤU HÌNH ---
st.set_page_config(
    page_title="Tổ Bảo Dưỡng Số 1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if 'video_ended' not in st.session_state:
    st.session_state.video_ended = False

# --- HÀM ĐỌC FILE BASE64 ---
def get_base64_encoded_file(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    except FileNotFoundError as e:
        st.error(f"Lỗi: Không tìm thấy file media ({e.filename})")
        st.stop()

# --- TẢI MEDIA ---
video_pc_base64 = get_base64_encoded_file("airplane.mp4")
video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
audio_base64 = get_base64_encoded_file("plane_fly.mp3")
bg_pc_base64 = get_base64_encoded_file("cabbase.jpg")    
bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")

# --- DANH SÁCH NHẠC TỪ GITHUB ---
music_files = {
    "background1": f"{GITHUB_RAW_BASE}/background1.mp3",
    "background2": f"{GITHUB_RAW_BASE}/background2.mp3",
    "background3": f"{GITHUB_RAW_BASE}/background3.mp3",
    "background4": f"{GITHUB_RAW_BASE}/background4.mp3",
    "background5": f"{GITHUB_RAW_BASE}/background5.mp3",
    "background6": f"{GITHUB_RAW_BASE}/background6.mp3",
}
music_playlist_json = json.dumps(music_files)

# --- FONT ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# --- CSS ---
hide_streamlit_style = f"""
<style>
#MainMenu, footer, header {{visibility: hidden;}}
.main, div.block-container {{padding: 0; margin: 0; max-width: 100% !important;}}

.stApp {{
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
}}

/* Video intro full màn hình */
iframe:first-of-type {{
    transition: opacity 1s ease-out, visibility 1s ease-out;
    opacity: 1; visibility: visible;
    width: 100vw !important; height: 100vh !important;
    position: fixed; top: 0; left: 0; z-index: 1000;
}}
.video-finished iframe:first-of-type {{
    opacity: 0; visibility: hidden; pointer-events: none;
    height: 1px !important;
}}

/* Nền chính sau intro */
.video-finished .stApp {{
    background-image: var(--main-bg-url-pc);
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

/* Tiêu đề chính */
#main-title-container {{
    position: fixed; top: 5vh; left: 0; width: 100%; text-align: center;
    z-index: 20; opacity: 0; transition: opacity 1.5s;
}}
.video-finished #main-title-container {{
    opacity: 1;
}}
#main-title-container h1 {{
    font-family: 'Playfair Display', serif; font-size: 3.5vw; 
    font-weight: 900; letter-spacing: 5px; 
    background: linear-gradient(90deg,#ff0000,#ff7f00,#ffff00,#00ff00,#0000ff,#4b0082,#9400d3);
    background-size: 400% 400%;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: colorShift 10s ease infinite, scrollText 15s linear infinite;
}}
@keyframes scrollText {{0%{{transform:translateX(100vw)}}100%{{transform:translateX(-100%)}}}}
@keyframes colorShift {{0%{{background-position:0% 50%}}50%{{background-position:100% 50%}}100%{{background-position:0% 50%}}}}

/* MUSIC PLAYER: chỉ hiển thị khi video kết thúc */
#music-player-container {{
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 1002;
    opacity: 0;
    pointer-events: none;
    height: 80px;
    width: 350px;
    transition: opacity 1s;
}}
.video-finished #music-player-container {{
    opacity: 1;
    pointer-events: auto;
}}

@media (max-width:768px){{
    .video-finished .stApp {{background-image: var(--main-bg-url-mobile);}}
    #main-title-container h1 {{font-size:6.5vw;}}
}}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- VIDEO INTRO (ĐÃ FIX ESCAPE) ---
js_callback_video = f"""
<script>
function sendBackToStreamlit() {{
    const stApp = window.parent.document.querySelector('.stApp');
    stApp.classList.add('video-finished');
    try {{
        window.parent.document.querySelector('#music-player-container iframe').contentWindow.togglePlayPause(true);
    }} catch(e) {{
        console.warn("Auto play failed", e);
    }}
}}
document.addEventListener("DOMContentLoaded", () => {{
    const video = document.getElementById('intro-video');
    const audio = document.getElementById('background-audio');
    if (window.innerWidth <= 768)
        video.src = 'data:video/mp4;base64,{video_mobile_base64}';
    else
        video.src = 'data:video/mp4;base64,{video_pc_base64}';
    audio.src = 'data:audio/mp3;base64,{audio_base64}';
    video.play().catch(()=>{{}});
    audio.loop = true; audio.play().catch(()=>{{}});
    video.onended = () => {{ audio.pause(); sendBackToStreamlit(); }};
}});
</script>
"""

intro_html = f"""
<html><body style="margin:0;overflow:hidden">
<video id="intro-video" muted playsinline style="width:100vw;height:100vh;object-fit:cover"></video>
<audio id="background-audio"></audio>
{js_callback_video}
</body></html>
"""
st.components.v1.html(intro_html, height=10, scrolling=False)

# --- TIÊU ĐỀ CHÍNH ---
st.markdown("""
<div id="main-title-container">
    <h1>TỔ BẢO DƯỠNG SỐ 1</h1>
</div>
""", unsafe_allow_html=True)

# --- MUSIC PLAYER (CHỈ Ở TRANG CHÍNH) ---
custom_music_player_html = f"""
<html><body style="margin:0;overflow:hidden;background:transparent">
<div class="player-container" style="display:flex;align-items:center;justify-content:center;padding:10px;
background-color:rgba(0,0,0,0.4);border-radius:8px;width:300px;margin:0 auto;border:1px solid #FFD700;">
    <div class="player-controls">
        <button onclick="prevTrack()" style="background:none;border:1px solid #FFD700;color:#FFD700;padding:8px 10px;margin:0 3px;border-radius:5px;cursor:pointer;">&#9664;&#9664;</button>
        <button id="play-pause-btn" onclick="togglePlayPause()" style="background:none;border:1px solid #FFD700;color:#FFD700;padding:8px 10px;margin:0 3px;border-radius:5px;cursor:pointer;">&#9658;</button>
        <button onclick="nextTrack()" style="background:none;border:1px solid #FFD700;color:#FFD700;padding:8px 10px;margin:0 3px;border-radius:5px;cursor:pointer;">&#9658;&#9658;</button>
    </div>
    <div id="track-name" style="color:white;font-size:12px;margin-left:10px;width:80px;text-align:center;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;">Đang tải...</div>
</div>
<audio id="audio-player"></audio>
<script>
const playlist = {music_playlist_json};
const keys = Object.keys(playlist);
const audio = document.getElementById('audio-player');
const btn = document.getElementById('play-pause-btn');
const nameEl = document.getElementById('track-name');
let idx = 0;
function loadTrack(i) {{
    const key = keys[i]; audio.src = playlist[key];
    nameEl.textContent = key.replace("background","Bài ");
}}
function togglePlayPause(forcePlay=false) {{
    if (audio.src === "") loadTrack(idx);
    if (audio.paused || forcePlay) {{
        audio.play().then(()=>btn.innerHTML='&#10074;&#10074;');
    }} else {{
        audio.pause(); btn.innerHTML='&#9658;';
    }}
}}
window.togglePlayPause = togglePlayPause;
function nextTrack() {{ idx=(idx+1)%keys.length; loadTrack(idx); audio.play(); }}
function prevTrack() {{ idx=(idx-1+keys.length)%keys.length; loadTrack(idx); audio.play(); }}
audio.addEventListener('ended', nextTrack);
document.addEventListener('DOMContentLoaded',()=>loadTrack(idx));
</script>
</body></html>
"""

st.markdown('<div id="music-player-container">', unsafe_allow_html=True)
st.components.v1.html(custom_music_player_html, height=80)
st.markdown('</div>', unsafe_allow_html=True)
