import streamlit as st
import base64
import json

# --- THÔNG TIN GITHUB CHO PLAYER ---
GITHUB_USER = "02838-vae"
GITHUB_REPO = "cabbase"
GITHUB_BRANCH = "main"
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/static"

# --- SETUP PAGE ---
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide", initial_sidebar_state="collapsed")

# Reset trạng thái mỗi lần refresh
st.session_state.video_ended = False


# --- HÀM TIỆN ÍCH ---
def b64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# --- LOAD MEDIA ---
video_pc = b64("airplane.mp4")
video_mobile = b64("mobile.mp4")
audio_bg = b64("plane_fly.mp3")
bg_pc = b64("cabbase.jpg")
bg_mobile = b64("mobile.jpg")

music_files = {
    "background1": f"{GITHUB_RAW_BASE}/background1.mp3",
    "background2": f"{GITHUB_RAW_BASE}/background2.mp3",
    "background3": f"{GITHUB_RAW_BASE}/background3.mp3",
    "background4": f"{GITHUB_RAW_BASE}/background4.mp3",
    "background5": f"{GITHUB_RAW_BASE}/background5.mp3",
    "background6": f"{GITHUB_RAW_BASE}/background6.mp3",
}
music_json = json.dumps(music_files)


# --- FONT ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Sacramento&family=Playfair+Display:wght@700;900&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)


# --- CSS CHÍNH (đầy đủ, fix hoàn toàn) ---
css = f"""
<style>
#MainMenu, header, footer {{display: none;}}
.main, div.block-container {{padding:0; margin:0; max-width:100% !important;}}

/* ===== VIDEO INTRO ===== */
.stApp > div > div > div > div > iframe:first-of-type {{
  position:fixed !important;
  top:0; left:0;
  width:100vw !important;
  height:100vh !important;
  z-index:9999 !important;
  border:none !important;
  transition:opacity 1s ease-out;
}}
.video-finished .stApp > div > div > div > div > iframe:first-of-type {{
  opacity:0 !important;
  visibility:hidden !important;
  pointer-events:none !important;
  z-index:-1 !important;
}}

/* ===== BACKGROUND ===== */
.stApp {{
  background:black;
  --bg-pc:url('data:image/jpeg;base64,{bg_pc}');
  --bg-m:url('data:image/jpeg;base64,{bg_mobile}');
}}
.stApp.video-finished {{
  background-image:var(--bg-pc);
  background-size:cover;
  background-position:center;
  background-attachment:fixed;
  transition:filter 2s ease;
  filter:sepia(60%) grayscale(20%) brightness(85%) contrast(110%);
}}
@media(max-width:768px){{
  .stApp.video-finished {{background-image:var(--bg-m);}}
}}

/* ===== LƯỚI REVEAL ===== */
.reveal-grid {{
  position:fixed; top:0; left:0; width:100vw; height:100vh;
  display:grid; grid-template-columns:repeat(20,1fr); grid-template-rows:repeat(12,1fr);
  z-index:500; pointer-events:none;
}}
.grid-cell {{
  background:#fff;
  opacity:1;
  transition:opacity .5s ease-out;
}}

/* ===== TIÊU ĐỀ CHÍNH ===== */
#main-title-container {{
  position:fixed;
  top:5vh;
  width:100%;
  text-align:center;
  opacity:0;
  pointer-events:none;
  transition:opacity 2s;
}}
.video-finished #main-title-container {{opacity:1;}}
#main-title-container h1 {{
  font-family:'Playfair Display',serif;
  font-size:3.8vw;
  margin:0;
  font-weight:900;
  border:none !important;
  letter-spacing:5px;
  background:linear-gradient(90deg,#ff0000,#ff7f00,#ffff00,#00ff00,#0000ff,#4b0082,#9400d3);
  background-size:400% 400%;
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
  animation:colorShift 10s ease infinite;
  text-shadow:2px 2px 4px rgba(0,0,0,0.5);
}}
@keyframes colorShift {{
  0%{{background-position:0% 50%;}}
  100%{{background-position:100% 50%;}}
}}

/* ===== PLAYER ===== */
#music-player-wrapper {{
  position:fixed;
  top:15vh;
  left:4vw;
  width:160px;
  height:70px;
  opacity:0;
  z-index:-10;
  pointer-events:none;
  transition:opacity 1.5s ease-out;
}}
.video-finished #music-player-wrapper {{
  opacity:1;
  z-index:20;
  pointer-events:auto;
}}
#music-player-wrapper iframe {{
  width:100%; height:100%; border:none;
}}
@media(max-width:768px){{
  #main-title-container h1 {{font-size:6.5vw;}}
  #music-player-wrapper {{top:14vh; left:3vw; width:140px; height:60px;}}
  .reveal-grid {{grid-template-columns:repeat(10,1fr); grid-template-rows:repeat(20,1fr);}}
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)


# --- VIDEO INTRO (chữ rơi + audio) ---
intro_html = f"""
<html>
<head>
<style>
  html,body{{margin:0;padding:0;overflow:hidden;background:black;height:100%;}}
  #intro-video{{position:absolute;width:100%;height:100%;object-fit:cover;z-index:1;}}
  #intro-text{{position:fixed;top:5vh;width:100%;text-align:center;font-family:'Sacramento',cursive;
  font-size:3vw;color:#FFD700;z-index:10;text-shadow:3px 3px 6px rgba(0,0,0,0.8);}}
  .intro-char{{display:inline-block;opacity:0;transform:translateY(-50px);
  animation:drop 0.8s ease-out forwards;}}
  @keyframes drop{{from{{opacity:0;transform:translateY(-50px);}}to{{opacity:1;transform:translateY(0);}}}}
  @media(max-width:768px){{#intro-text{{font-size:6vw;}}}}
</style>
</head>
<body>
<video id="intro-video" muted playsinline></video>
<audio id="intro-audio"></audio>
<div id="intro-text"></div>

<script>
const text="KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI";
const container=document.getElementById('intro-text');
text.split('').forEach((ch,i)=>{{
  const span=document.createElement('span');
  span.className='intro-char';
  span.textContent=ch===' ' ? '\\u00A0':ch;
  span.style.animationDelay=`${{i*0.1}}s`;
  container.appendChild(span);
}});
const v=document.getElementById('intro-video');
const a=document.getElementById('intro-audio');
const isM=window.innerWidth<=768;
v.src=isM?'data:video/mp4;base64,{video_mobile}':'data:video/mp4;base64,{video_pc}';
a.src='data:audio/mp3;base64,{audio_bg}';
v.onended=()=>{{
  const app=window.parent.document.querySelector('.stApp');
  app.classList.add('video-finished');
  setTimeout(()=>window.parent.document.querySelector('.reveal-grid')?.remove(),800);
}};
document.body.addEventListener('click',()=>{{
  v.play().catch(()=>{{}});
  a.play().catch(()=>{{}});
}},{{once:true}});
v.play().catch(()=>{{}});
a.play().catch(()=>{{}});
</script>
</body></html>
"""
st.components.v1.html(intro_html, height=1, scrolling=False)


# --- HIỆU ỨNG LƯỚI REVEAL ---
grid = "".join('<div class="grid-cell"></div>' for _ in range(240))
st.markdown(f"<div class='reveal-grid'>{grid}</div>", unsafe_allow_html=True)


# --- TIÊU ĐỀ ---
st.markdown("""
<div id="main-title-container">
  <h1>TỔ BẢO DƯỠNG SỐ 1</h1>
</div>
""", unsafe_allow_html=True)


# --- PLAYER ---
player_html = f"""
<html><body style="margin:0;padding:0;">
<div style="display:flex;align-items:center;justify-content:center;
background:linear-gradient(135deg,rgba(0,0,0,0.75),rgba(30,30,30,0.85));
border-radius:10px;border:2px solid #FFD700;box-shadow:0 3px 12px rgba(255,215,0,0.5);
padding:6px 8px;">
  <div style="display:flex;gap:5px;">
    <button onclick="prev()" style="background:linear-gradient(135deg,#FFD700,#FFA500);border:none;
    border-radius:6px;padding:6px;font-weight:bold;cursor:pointer;">&#9664;&#9664;</button>
    <button id="pp" onclick="toggle()" style="background:linear-gradient(135deg,#FFD700,#FFA500);
    border:none;border-radius:6px;padding:6px 10px;font-weight:bold;">&#9658;</button>
    <button onclick="next()" style="background:linear-gradient(135deg,#FFD700,#FFA500);border:none;
    border-radius:6px;padding:6px;font-weight:bold;cursor:pointer;">&#9658;&#9658;</button>
  </div>
</div>
<audio id="au"></audio>
<script>
const list={music_json};
const keys=Object.keys(list);
let i=0; const a=document.getElementById('au'); const b=document.getElementById('pp');
function load(){a.src=list[keys[i]];}
function toggle(){{if(a.paused){{a.play();b.innerHTML='&#10074;&#10074;';}}else{{a.pause();b.innerHTML='&#9658;';}}}}
function next(){{i=(i+1)%keys.length;load();if(!a.paused)a.play();}}
function prev(){{i=(i-1+keys.length)%keys.length;load();if(!a.paused)a.play();}}
a.addEventListener('ended',next); load();
window.togglePlayPause=toggle;
</script>
</body></html>
"""
st.markdown('<div id="music-player-wrapper">', unsafe_allow_html=True)
st.components.v1.html(player_html, height=70)
st.markdown('</div>', unsafe_allow_html=True)
