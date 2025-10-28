import streamlit as st
import base64

# ============ HÀM MÃ HOÁ FILE =============
def get_base64_encoded_file(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# ============ ĐỌC CÁC FILE CẦN THIẾT =============
video_base64 = get_base64_encoded_file("airplane.mp4")
video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
audio_base64 = get_base64_encoded_file("music.mp3")
logo_base64 = get_base64_encoded_file("logo.jpg")

# ============ CSS TÙY CHỈNH =============
hide_streamlit_style = f"""
<style>
html, body {{
    margin: 0;
    padding: 0;
    overflow: hidden;
    height: 100%;
    width: 100%;
}}

#intro-video {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: 0; /* ĐÃ SỬA */
}}

#music-player-container {{
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 280px;
    padding: 12px;
    border-radius: 16px;

    /* nền logo mờ */
    background: rgba(0, 0, 0, 0.7);
    background-image: url("data:image/jpeg;base64,{logo_base64}");
    background-size: cover;
    background-position: center;
    background-blend-mode: overlay;

    backdrop-filter: blur(10px);
    box-shadow: 0 0 20px rgba(255, 255, 255, 0.15);
    color: #fff;
    font-family: sans-serif;
    z-index: 10;
}}

#player-controls {{
    display: flex;
    justify-content: space-around;
    align-items: center;
    margin-top: 10px;
}}

#player-controls button {{
    background: none;
    border: none;
    color: gold;
    font-size: 22px;
    cursor: pointer;
    transition: 0.3s;
    box-shadow: 0 0 6px rgba(255, 215, 0, 0.5);
    border-radius: 50%;
    padding: 6px;
}}

#player-controls button:hover {{
    transform: scale(1.1);
    color: #fff;
}}
</style>
"""

# ============ HTML GIAO DIỆN VIDEO + PLAYER =============
html_content_modified = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
{hide_streamlit_style}
</head>
<body>
    <video id="intro-video" playsinline autoplay muted>
        <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
    </video>

    <div id="music-player-container">
        <div id="player-controls">
            <button id="prev-btn" title="Bài trước">⏮️</button>
            <button id="play-pause-btn" title="Phát/Dừng">▶️</button>
            <button id="next-btn" title="Bài tiếp">⏭️</button>
        </div>
    </div>

<script>
const video = document.getElementById('intro-video');
const audio = new Audio("data:audio/mp3;base64,{audio_base64}");
const playPauseBtn = document.getElementById('play-pause-btn');

let isPlaying = false;

video.muted = true;
video.play().catch(err => console.log("Autoplay blocked:", err));

function tryToPlay() {{
    video.play().catch(() => {{}});
}}

video.addEventListener('loadeddata', tryToPlay, {{ once: true }});
setTimeout(tryToPlay, 500);

playPauseBtn.addEventListener('click', () => {{
    if (!isPlaying) {{
        audio.play();
        video.play();
        playPauseBtn.textContent = "⏸️";
        isPlaying = true;
    }} else {{
        audio.pause();
        video.pause();
        playPauseBtn.textContent = "▶️";
        isPlaying = false;
    }}
}});
</script>
</body>
</html>
"""

# ============ HIỂN THỊ TRÊN STREAMLIT =============
st.set_page_config(page_title="Cabbase", layout="wide", initial_sidebar_state="collapsed")
st.components.v1.html(html_content_modified, height=1080, scrolling=False)
