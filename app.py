import streamlit as st
import base64
import json

# --- CẤU HÌNH ---
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide", initial_sidebar_state="collapsed")

# Reset lại trạng thái mỗi khi refresh
st.session_state.video_ended = False

# --- HÀM MÃ HÓA BASE64 ---
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# --- MEDIA ---
video_pc = get_base64("airplane.mp4")
video_mobile = get_base64("mobile.mp4")
audio_bg = get_base64("plane_fly.mp3")
bg_pc = get_base64("cabbase.jpg")
bg_mobile = get_base64("mobile.jpg")

# --- DANH SÁCH NHẠC ---
GITHUB_RAW = "https://raw.githubusercontent.com/02838-vae/cabbase/main/static"
music_files = {
    "background1": f"{GITHUB_RAW}/background1.mp3",
    "background2": f"{GITHUB_RAW}/background2.mp3",
    "background3": f"{GITHUB_RAW}/background3.mp3",
    "background4": f"{GITHUB_RAW}/background4.mp3",
    "background5": f"{GITHUB_RAW}/background5.mp3",
    "background6": f"{GITHUB_RAW}/background6.mp3",
}
music_playlist_json = json.dumps(music_files)

# --- CSS ---
css = f"""
<style>
#MainMenu, header, footer {{display: none;}}

.stApp {{
  background: black;
  transition: background 1s ease-out;
}}
.stApp.video-finished {{
  background-image: url('data:image/jpeg;base64,{bg_pc}');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
}}
@media (max-width:768px) {{
  .stApp.video-finished {{
    background-image: url('data:image/jpeg;base64,{bg_mobile}');
  }}
}}

/* Ẩn player ban đầu */
#music-player-wrapper {{
  position: fixed;
  top: 15vh;
  left: 4vw;
  width: 160px;
  height: 70px;
  z-index: -1000;
  opacity: 0;
  pointer-events: none;
  transition: all 1.2s ease-out;
}}
.video-finished #music-player-wrapper {{
  opacity: 1;
  z-index: 100;
  pointer-events: auto;
}}

/* Tiêu đề chính */
#main-title-container {{
  position: fixed;
  top: 5vh;
  width: 100%;
  text-align: center;
  opacity: 0;
  pointer-events: none;
  transition: opacity 2s ease-out;
  border: none !important;
}}
.video-finished #main-title-container {{
  opacity: 1;
}}
#main-title-container h1 {{
  font-family: 'Playfair Display', serif;
  font-size: 3.8vw;
  margin: 0;
  font-weight: 900;
  color: transparent;
  background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
  -webkit-background-clip: text;
  animation: rainbow 6s linear infinite;
  border: none !important;
}}
@keyframes rainbow {{
  0% {{ background-position: 0% 50%; }}
  100% {{ background-position: 100% 50%; }}
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# --- VIDEO INTRO ---
intro_html = f"""
<div id="intro-wrapper" style="position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:9999;overflow:hidden;background:black;">
  <video id="intro-video" autoplay muted playsinline style="width:100%;height:100%;object-fit:cover;"></video>
  <audio id="intro-audio"></audio>
  <div id="intro-text" style="position:absolute;top:5vh;width:100%;text-align:center;font-family:'Sacramento',cursive;font-size:3vw;color:#FFD700;text-shadow:2px 2px 6px rgba(0,0,0,0.8);">
    KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI
  </div>
</div>

<script>
  const video = document.getElementById('intro-video');
  const audio = document.getElementById('intro-audio');
  const intro = document.getElementById('intro-wrapper');
  const stApp = window.parent.document.querySelector('.stApp');
  const isMobile = window.innerWidth <= 768;
  video.src = isMobile ? 'data:video/mp4;base64,{video_mobile}' : 'data:video/mp4;base64,{video_pc}';
  audio.src = 'data:audio/mp3;base64,{audio_bg}';

  video.addEventListener('ended', () => {{
    intro.style.transition = "opacity 1s";
    intro.style.opacity = 0;
    setTimeout(() => {{
      intro.remove();
      stApp.classList.add('video-finished');
    }}, 1000);
  }});

  window.addEventListener('click', () => {{
    video.play().catch(()=>{{}});
    audio.play().catch(()=>{{}});
  }}, {{once:true}});
</script>
"""
st.components.v1.html(intro_html, height=1, scrolling=False)

# --- TIÊU ĐỀ ---
st.markdown("""
<div id="main-title-container">
  <h1>TỔ BẢO DƯỠNG SỐ 1</h1>
</div>
""", unsafe_allow_html=True)

# --- PLAYER ---
player_html = f"""
<div class="player" style="display:flex;align-items:center;justify-content:center;height:100%;background:rgba(0,0,0,0.5);border-radius:10px;border:2px solid gold;">
  <audio id="music" controls style="width:140px;height:40px;">
    <source src="{music_files['background1']}" type="audio/mp3">
  </audio>
</div>
"""
st.markdown('<div id="music-player-wrapper">', unsafe_allow_html=True)
st.components.v1.html(player_html, height=70)
st.markdown('</div>', unsafe_allow_html=True)
