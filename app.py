import streamlit as st
import base64
import os
import json
import time

# === CÁC FILE NGUỒN ===
video_file = "airplane.mp4"
bg_file = "cabbase.jpg"
bg_mobile_file = "mobile.jpg"
AUDIO_FILES = ["background.mp3"]

# Thời lượng video & thời gian fade
VIDEO_DURATION_SECONDS = 5
FADE_DURATION_SECONDS = 4
TOTAL_ANIMATION_TIME_MS = (VIDEO_DURATION_SECONDS + FADE_DURATION_SECONDS) * 1000

# --- Cấu hình ---
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

# === Hàm tiện ích ===
@st.cache_data
def get_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        return None

# --- Session state ---
if "is_playing" not in st.session_state:
    st.session_state.is_playing = True
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = False
if "intro_rendered" not in st.session_state:
    st.session_state.intro_rendered = False
if "current_track_index" not in st.session_state:
    st.session_state.current_track_index = 0

# === Load file ===
img_base64 = get_base64(bg_file)
if img_base64 is None: st.error(f"❌ Không tìm thấy file {bg_file}."); st.stop()

img_mobile_base64 = get_base64(bg_mobile_file)
if img_mobile_base64 is None: img_mobile_base64 = img_base64

video_data = get_base64(video_file)
if video_data is None: st.error(f"❌ Không tìm thấy file {video_file}."); st.stop()

AUDIO_BASE64 = get_base64(AUDIO_FILES[0])
if AUDIO_BASE64 is None: st.error(f"❌ Không tìm thấy file {AUDIO_FILES[0]}."); st.stop()

current_audio_base64 = AUDIO_BASE64
current_track_name = AUDIO_FILES[0]
is_playing_state = st.session_state.is_playing
is_mobile = st.session_state.is_mobile

# --- Thiết bị ---
if st.query_params.get("mobile_check") == ["true"]:
    st.session_state.is_mobile = True
elif st.query_params.get("mobile_check") == ["false"]:
    st.session_state.is_mobile = False
is_mobile = st.session_state.is_mobile

# --- CSS + JS ---
css_js_placeholder = st.empty()

css_js_code = f"""
<style>
html, body {{
    margin:0; padding:0; height:100%; overflow:hidden; background:black;
}}
header[data-testid="stHeader"], footer {{ display:none !important; }}
.block-container, section.main > div {{
    margin:0!important; padding:0!important; max-width:100%!important;
    width:100vw!important; height:calc(var(--vh,1vh)*100)!important;
}}
.stApp, section.main {{
    height:calc(var(--vh,1vh)*100)!important; min-height:calc(var(--vh,1vh)*100)!important;
}}

/* VIDEO CONTAINER */
.video-container {{
    position:fixed; inset:0;
    width:100vw; height:calc(var(--vh,1vh)*100);
    justify-content:center; align-items:center; background:black;
    z-index:99999; display:flex; flex-direction:column;
    opacity:1; transition:opacity 0.5s;
}}
.video-container.hidden {{
    opacity:0!important; z-index:-1!important; display:none!important;
}}
.intro-media {{
    width:100vw; height:calc(var(--vh,1vh)*100); object-fit:cover;
}}

/* DÒNG CHỮ TRÊN VIDEO */
.video-text {{
    position:absolute; bottom:12vh; width:100%; text-align:center;
    font-family:'Special Elite', cursive;
    font-size:clamp(24px,5vw,44px); font-weight:bold; color:#fff;
    text-shadow:0 0 20px rgba(255,255,255,0.8),0 0 40px rgba(180,220,255,0.6),0 0 60px rgba(255,255,255,0.4);
    opacity:0; z-index:100000;
    animation:
        appear 1.2s ease-out forwards,
        flicker 0.25s linear infinite 1.2s,
        floatFade {FADE_DURATION_SECONDS}s ease-in {VIDEO_DURATION_SECONDS - 1}s forwards;
}}

@keyframes appear {{
    0% {{opacity:0; filter:blur(8px); transform:translateY(40px);}}
    100% {{opacity:1; filter:blur(0); transform:translateY(0);}}
}}
@keyframes floatFade {{
    0% {{opacity:1; transform:translateY(0); filter:blur(0);}}
    100% {{opacity:0; transform:translateY(-30px) scale(1.05); filter:blur(8px);}}
}}
@keyframes flicker {{
    0%,100% {{text-shadow:0 0 20px rgba(255,255,255,0.8),0 0 40px rgba(180,220,255,0.6);opacity:1;}}
    50% {{text-shadow:0 0 10px rgba(255,255,255,0.5),0 0 30px rgba(180,220,255,0.3);opacity:0.95;}}
    51% {{text-shadow:0 0 30px rgba(255,255,255,0.9),0 0 50px rgba(180,220,255,0.7);opacity:1;}}
}}

/* BACKGROUND CHÍNH */
.stApp {{
    z-index:1;
    background-color:#333;
    background-image:linear-gradient(rgba(245,242,200,0.4), rgba(245,242,200,0.4)),
                      url("data:image/jpeg;base64,{img_base64}");
    background-size:cover; background-repeat:no-repeat; background-position:center;
}}
.hide-on-start {{opacity:0;}}
.show-after-animation {{opacity:1!important;transition:opacity 1s ease-in 0.5s;}}

@media screen and (max-width:768px){{
    .stApp {{
        background-image:linear-gradient(rgba(245,242,200,0.4), rgba(245,242,200,0.4)),
                          url("data:image/jpeg;base64,{img_mobile_base64}");
    }}
}}

/* AUDIO PLAYER */
.custom-audio-player {{
    position:fixed; top:10px; left:10px; z-index:9999;
    display:flex; flex-direction:column; width:300px;
    background:rgba(0,0,0,0.7); border-radius:8px; padding:10px;
    box-shadow:0 4px 15px rgba(0,0,0,0.5);
}}
.player-info {{color:white; font-size:0.9em; margin-bottom:5px;}}
.progress-bar {{width:100%; height:5px; background:#555; cursor:pointer; border-radius:3px; margin:5px 0;}}
.progress-filled {{height:100%; background:#4CAF50; width:0%; border-radius:3px; transition:width 0.1s linear;}}
.time-display {{display:flex; justify-content:space-between; color:white; font-size:0.8em;}}
.player-controls {{display:flex; justify-content:center; margin-top:10px;}}
.control-button {{background:none; border:none; color:white; font-size:1.5em; cursor:pointer; padding:0 10px;}}

/* TITLE */
.main-title {{
    font-family:'Special Elite', cursive;
    font-size:clamp(36px,5vw,48px); font-weight:bold;
    text-align:center; color:#3e2723; margin-top:50px;
    text-shadow:2px 2px 0 #fff,0 0 25px #f0d49b,0 0 50px #bca27a;
}}
</style>

<script>
function setVhProperty(){{
    let vh=window.innerHeight*0.01;
    document.documentElement.style.setProperty('--vh',`${{vh}}px`);
}}
function checkDeviceAndReload(){{
    const isMobile=/Mobi|Android|iPhone|iPad|iPod|Windows Phone/i.test(navigator.userAgent)||window.innerWidth<768;
    const currentParams=new URLSearchParams(window.location.search);
    if(currentParams.get('mobile_check')===null){{
        const newUrl=new URL(window.location.href);
        newUrl.searchParams.set('mobile_check',isMobile?'true':'false');
        window.location.replace(newUrl);
    }}
}}
const totalDuration={TOTAL_ANIMATION_TIME_MS};
function handleIntroTransition(){{
    const videoContainer=document.getElementById('videoContainer');
    const mainContent=document.getElementById('mainContentContainer');
    if(videoContainer){{
        videoContainer.style.animation=`fadeOut {FADE_DURATION_SECONDS}s ease-out {VIDEO_DURATION_SECONDS}s forwards`;
        setTimeout(() => {{
            videoContainer.classList.add('hidden');
            if(mainContent) mainContent.classList.add('show-after-animation');
        }}, totalDuration + 500);
    }} else if(mainContent){{
        mainContent.classList.add('show-after-animation');
    }}
}}
setVhProperty();
window.addEventListener('resize', setVhProperty);
document.addEventListener('DOMContentLoaded', ()=>{
    checkDeviceAndReload();
    handleIntroTransition();
    setVhProperty();
});
</script>
"""
css_js_placeholder.markdown(css_js_code, unsafe_allow_html=True)

# --- VIDEO INTRO ---
if not st.session_state.intro_rendered:
    st.session_state.intro_rendered = True
    if video_data:
        media_source = f"data:video/mp4;base64,{video_data}"
        st.markdown(f"""
        <div class="video-container" id="videoContainer">
            <video id="introMedia" class="intro-media" autoplay muted playsinline>
                <source src="{media_source}" type="video/mp4">
            </video>
            <div class="video-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        </div>
        """, unsafe_allow_html=True)

# --- MAIN CONTENT ---
initial_main_class = 'hide-on-start' if st.session_state.intro_rendered else 'show-after-animation'
st.markdown(f'<div id="mainContentContainer" class="{initial_main_class}">', unsafe_allow_html=True)

st.markdown('<div class="main-title">📜 TỔ BẢO DƯỠNG SỐ 1</div>', unsafe_allow_html=True)
st.write("Chào mừng bạn đến với website ✈️")

# --- AUDIO PLAYER ---
if current_audio_base64:
    js_code_player = f"""
    <script>
        const AUDIO_BASE64="{current_audio_base64}";
        const TRACK_NAME="{current_track_name}";
        let isPlaying={'true' if is_playing_state else 'false'};
        let audioPlayer;

        function initPlayer(){{
            audioPlayer=document.getElementById('customAudioPlayer');
            if(audioPlayer){{
                if(isPlaying) audioPlayer.play().catch(()=>{{isPlaying=false;}});
                else audioPlayer.pause();
                audioPlayer.addEventListener('timeupdate',window.updateProgress);
                audioPlayer.addEventListener('loadedmetadata',window.updateDuration);
                audioPlayer.addEventListener('ended',()=>{{audioPlayer.currentTime=0;audioPlayer.play();}});
                const pb=document.getElementById('progressBar');
                if(pb) pb.addEventListener('click',window.seekAudio);
            }}
            updateTrackInfo(); updateDuration();
        }}
        function formatTime(s){{const m=Math.floor(s/60),r=Math.floor(s%60);return `${{String(m).padStart(2,'0')}}:${{String(r).padStart(2,'0')}}`;}}
        function updateTrackInfo(){{const i=document.getElementById('trackInfo'); if(i) i.textContent=`Bài hát: ${{TRACK_NAME}}`;}}
        window.updateDuration=function(){{const d=document.getElementById('durationTime');if(audioPlayer&&d){{d.textContent=isFinite(audioPlayer.duration)?formatTime(audioPlayer.duration):'--:--';}}}}
        window.updateProgress=function(){{const p=document.getElementById('progressFilled');const c=document.getElementById('currentTime');if(audioPlayer&&p&&c&&audioPlayer.duration){{const perc=(audioPlayer.currentTime/audioPlayer.duration)*100;p.style.width=perc+'%';c.textContent=formatTime(audioPlayer.currentTime);}}}}
        window.togglePlayPause=function(){{const b=document.getElementById('playPauseButton');if(audioPlayer.paused){{audioPlayer.play();b.innerHTML='⏸️';isPlaying=true;}}else{{audioPlayer.pause();b.innerHTML='▶️';isPlaying=false;}}}}
        window.seekAudio=function(e){{const pb=document.getElementById('progressBar');const r=pb.getBoundingClientRect();const pos=e.clientX-r.left;const ratio=pos/pb.offsetWidth;if(audioPlayer.duration)audioPlayer.currentTime=audioPlayer.duration*ratio;}}
        document.addEventListener('DOMContentLoaded',initPlayer);
    </script>
    """

    st.markdown(f"""
    <div style="display:none;">
        <audio id="customAudioPlayer" src="data:audio/mp3;base64,{current_audio_base64}" autoplay></audio>
    </div>
    <div class="custom-audio-player">
        <div class="player-info" id="trackInfo">Bài hát: {current_track_name}</div>
        <div class="progress-bar" id="progressBar">
            <div class="progress-filled" id="progressFilled"></div>
        </div>
        <div class="time-display">
            <span id="currentTime">00:00</span>
            <span id="durationTime">--:--</span>
        </div>
        <div class="player-controls">
            <button class="control-button" style="visibility:hidden;">&nbsp;</button>
            <button class="control-button" id="playPauseButton" onclick="window.togglePlayPause()">
                {'⏸️' if is_playing_state else '▶️'}
            </button>
            <button class="control-button" style="visibility:hidden;">&nbsp;</button>
        </div>
    </div>
    {js_code_player}
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
