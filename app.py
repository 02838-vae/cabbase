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
        raise FileNotFoundError(f"Lỗi: Không tìm thấy file media. Vui lòng kiểm tra lại đường dẫn: {e.filename}")

# Mã hóa các file media
try:
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg")
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
except FileNotFoundError as e:
    st.error(e)
    st.stop()

# --- PHẦN 1: NHÚNG FONT ---
font_links = """
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
"""
st.markdown(font_links, unsafe_allow_html=True)

# --- PHẦN 2: CSS CHÍNH ---
hide_streamlit_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sacramento&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');

#MainMenu, footer, header {{visibility: hidden;}}

.main {{
    padding: 0;
    margin: 0;
}}
div.block-container {{
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
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- PHẦN 3: VIDEO INTRO ---
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
    const shuffled = Array.from(cells).sort(() => Math.random() - 0.5);
    shuffled.forEach((c,i)=>setTimeout(()=>c.style.opacity=0,i*10));
    setTimeout(()=>revealGrid.remove(),shuffled.length*10+1000);
}}
document.addEventListener("DOMContentLoaded", ()=>{
    const video=document.getElementById('intro-video');
    const audio=document.getElementById('background-audio');
    const intro=document.getElementById('intro-text-container');
    const isMobile=window.innerWidth<=768;
    video.src=isMobile?'data:video/mp4;base64,{video_mobile_base64}':'data:video/mp4;base64,{video_pc_base64}';
    audio.src='data:audio/mp3;base64,{audio_base64}';
    const playMedia=()=>{
        video.load(); video.play().catch(()=>{});
        const chars=intro.querySelectorAll('.intro-char');
        chars.forEach((ch,i)=>{ch.style.animationDelay=`${i*0.1}s`;ch.classList.add('char-shown');});
        audio.volume=0.5; audio.loop=true; audio.play().catch(()=>{});
    };
    playMedia();
    video.onended=()=>{video.style.opacity=0;audio.pause();intro.style.opacity=0;sendBackToStreamlit();};
});
</script>
"""
intro_title = "KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI"
intro_chars_html = ''.join(
    [f'<span class="intro-char">{c}</span>' if c != ' ' else '<span class="intro-char">&nbsp;</span>' for c in intro_title]
)
html_content = f"""
<!DOCTYPE html>
<html>
<head>
<style>
html,body{{margin:0;padding:0;overflow:hidden;height:100vh;width:100vw;}}
#intro-video{{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;z-index:-100;transition:opacity 1s;}}
#intro-text-container{{position:fixed;top:5vh;width:100%;text-align:center;color:#FFD700;font-size:3vw;
font-family:'Sacramento',cursive;font-weight:400;text-shadow:3px 3px 6px rgba(0,0,0,0.8);z-index:100;
display:flex;justify-content:center;opacity:1;}}
.intro-char{{display:inline-block;opacity:0;transform:translateY(-50px);animation-fill-mode:forwards;
animation-duration:0.8s;animation-timing-function:ease-out;}}
@keyframes charDropIn{{from{{opacity:0;transform:translateY(-50px);}}to{{opacity:1;transform:translateY(0);}}}}
.intro-char.char-shown{{animation-name:charDropIn;}}
@media(max-width:768px){{#intro-text-container{{font-size:6vw;}}}}
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
st.components.v1.html(html_content, height=10, scrolling=False)

# --- PHẦN 4: HIỆU ỨNG REVEAL ---
grid_cells_html = ''.join('<div class="grid-cell"></div>' for _ in range(240))
reveal_grid_html = f'<div class="reveal-grid">{grid_cells_html}</div>'
st.markdown(reveal_grid_html, unsafe_allow_html=True)

# --- PHẦN 5: TIÊU ĐỀ CHÍNH ---
main_title_text = "TỔ BẢO DƯỠNG SỐ 1"
st.markdown(f"""
<div id="main-title-container">
    <h1>{main_title_text}</h1>
</div>
""", unsafe_allow_html=True)

# --- PHẦN 6: MUSIC PLAYER ---
song_base64_list = []
for i in range(1, 7):
    try:
        song_base64_list.append(get_base64_encoded_file(f"background{i}.mp3"))
    except FileNotFoundError:
        pass

if song_base64_list:
    song_sources_js = "[" + ",".join([f"'data:audio/mp3;base64,{b}'" for b in song_base64_list]) + "]"
    music_player_html = f"""
    <style>
    #music-player {{
        position: fixed;
        bottom: 2vh;
        left: 2vw;
        width: 250px;
        height: 60px;
        background: rgba(0,0,0,0.55);
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
    }}
    .video-finished #music-player {{
        opacity: 1;
    }}
    #music-player button {{
        background: none;
        border: none;
        color: white;
        font-size: 18px;
        cursor: pointer;
        transition: transform 0.2s;
    }}
    #music-player button:hover {{
        transform: scale(1.2);
    }}
    #music-player input[type="range"] {{
        width: 100px;
        accent-color: #FFD700;
        cursor: pointer;
    }}
    </style>
    <div id="music-player">
        <button id="prev-btn">⏮️</button>
        <button id="play-btn">▶️</button>
        <button id="next-btn">⏭️</button>
        <input type="range" id="progress-bar" value="0" min="0" max="100">
    </div>
    <script>
    const playlist = {song_sources_js};
    let current = 0;
    const audio = new Audio(playlist[current]);
    const playBtn = document.getElementById('play-btn');
    const nextBtn = document.getElementById('next-btn');
    const prevBtn = document.getElementById('prev-btn');
    const bar = document.getElementById('progress-bar');
    let playing = false;

    playBtn.addEventListener('click', ()=>{
        if (!playing) {{audio.play();playBtn.textContent='⏸️';}}
        else {{audio.pause();playBtn.textContent='▶️';}}
        playing=!playing;
    });
    nextBtn.addEventListener('click', ()=>{{current=(current+1)%playlist.length;change();}});
    prevBtn.addEventListener('click', ()=>{{current=(current-1+playlist.length)%playlist.length;change();}});
    function change(){{audio.src=playlist[current];audio.play();playing=true;playBtn.textContent='⏸️';}}
    audio.addEventListener('timeupdate', ()=>{{if(audio.duration) bar.value=(audio.currentTime/audio.duration)*100;}});
    bar.addEventListener('input', ()=>{{if(audio.duration) audio.currentTime=(bar.value/100)*audio.duration;}});
    audio.addEventListener('ended', ()=>{{current=(current+1)%playlist.length;change();}});
    </script>
    """
    st.markdown(music_player_html, unsafe_allow_html=True)
