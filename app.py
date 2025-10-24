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
        return base64.b64encode(f.read()).decode("utf-8")

# --- MÃ HÓA MEDIA ---
try:
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
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
.main, div.block-container {{padding: 0; margin: 0; max-width: 100% !important;}}
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
    .main-content-revealed {{background-image: var(--main-bg-url-mobile);}}
}}
/* --- TIÊU ĐỀ CHÍNH --- */
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

# --- VIDEO INTRO (SỬA CHIỀU CAO + BỎ AUTOPLAY CHẶN) ---
html_intro = f"""
<video id="intro-video" muted playsinline style="width:100%;height:100vh;object-fit:cover;position:fixed;top:0;left:0;z-index:-1;"></video>
<script>
document.addEventListener("DOMContentLoaded", () => {{
    const video = document.getElementById('intro-video');
    const isMobile = window.innerWidth <= 768;
    video.src = isMobile ? 'data:video/mp4;base64,{video_mobile_base64}' : 'data:video/mp4;base64,{video_pc_base64}';
    video.play().catch(()=>{{
        document.body.addEventListener('click',()=>video.play(),{{once:true}});
    }});
    video.onended = () => {{
        document.querySelector('.stApp').classList.add('main-content-revealed');
        document.getElementById('main-title-container').style.opacity = 1;
    }};
}});
</script>
"""
st.components.v1.html(html_intro, height=600, scrolling=False)

# --- TIÊU ĐỀ CHÍNH ---
st.markdown("""
<div id="main-title-container">
    <h1>TỔ BẢO DƯỠNG SỐ 1</h1>
</div>
""", unsafe_allow_html=True)

# --- MUSIC PLAYER GỌN ---
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
    background: rgba(30,30,30,0.7);
    border-radius: 30px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    padding: 10px 25px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
    color: white;
    font-size: 1.5rem;
    z-index: 100;
}}
.music-btn {{
    background: none;
    border: none;
    color: white;
    cursor: pointer;
    transition: transform 0.2s, color 0.2s;
}}
.music-btn:hover {{
    transform: scale(1.2);
    color: #ffcc00;
}}
</style>

<div id="music-player">
    <button class="music-btn" id="prev"><i class="fa-solid fa-backward"></i></button>
    <button class="music-btn" id="playpause"><i class="fa-solid fa-play"></i></button>
    <button class="music-btn" id="next"><i class="fa-solid fa-forward"></i></button>
</div>

<script>
const tracks = {encoded_musics};
let current = 0;
let audio = new Audio("data:audio/mp3;base64," + tracks[current]);
let playing = false;

function playMusic() {{
    audio.play().catch(()=>{{
        document.body.addEventListener('click',()=>audio.play(),{{once:true}});
    }});
    playing = true;
    document.getElementById("playpause").innerHTML = '<i class="fa-solid fa-pause"></i>';
}}
function pauseMusic() {{
    audio.pause();
    playing = false;
    document.getElementById("playpause").innerHTML = '<i class="fa-solid fa-play"></i>';
}}
function nextTrack() {{
    current = (current + 1) % tracks.length;
    audio.pause();
    audio = new Audio("data:audio/mp3;base64," + tracks[current]);
    if (playing) playMusic();
}}
function prevTrack() {{
    current = (current - 1 + tracks.length) % tracks.length;
    audio.pause();
    audio = new Audio("data:audio/mp3;base64," + tracks[current]);
    if (playing) playMusic();
}}
document.getElementById("playpause").addEventListener("click", ()=>{{ playing ? pauseMusic() : playMusic(); }});
document.getElementById("next").addEventListener("click", nextTrack);
document.getElementById("prev").addEventListener("click", prevTrack);
</script>
"""
st.markdown(music_player_html, unsafe_allow_html=True)
