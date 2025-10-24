import streamlit as st
import base64

# --- CẤU HÌNH BAN ĐẦU ---
st.set_page_config(
    page_title="Tổ Bảo Dưỡng Số 1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- SESSION STATE ---
if 'video_ended' not in st.session_state:
    st.session_state.video_ended = False

# --- HÀM TIỆN ÍCH ---
def get_base64_encoded_file(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Lỗi: Không tìm thấy file media. Vui lòng kiểm tra: {e.filename}")

# --- BASE64 MEDIA ---
try:
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg")
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
except FileNotFoundError as e:
    st.error(e)
    st.stop()

# --- CSS CHUNG ---
css_style = f"""
<style>
/* Reset UI */
#MainMenu, footer, header {{visibility: hidden;}}
.main {{padding: 0; margin: 0;}}
div.block-container {{padding: 0; margin: 0; max-width: 100% !important;}}

/* Background */
.stApp {{
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
}}

/* Reveal grid */
.reveal-grid {{
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    display: grid; grid-template-columns: repeat(20, 1fr); 
    grid-template-rows: repeat(12, 1fr); z-index: 500; pointer-events: none; 
}}
.grid-cell {{background-color: white; opacity: 1; transition: opacity 0.5s ease-out;}}
.main-content-revealed {{
    background-image: var(--main-bg-url-pc);
    background-size: cover; background-position: center; background-attachment: fixed;
}}

/* Keyframes ánh sáng */
@keyframes shine-horizontal {{
    0% {{ background-position: -150% 0; }}
    100% {{ background-position: 250% 0; }}
}}
@keyframes shine-diagonal {{
    0% {{ background-position: -200% 0; }}
    100% {{ background-position: 300% 0; }}
}}

/* Intro text */
#intro-text {{
    position: fixed; top: 5vh; width: 100%; text-align: center;
    font-family: 'Poppins', sans-serif;
    font-size: 5vw; font-weight: 800;
    text-transform: uppercase; letter-spacing: 2px;
    padding: 0.5em 1em;
    color: transparent;
    background: linear-gradient(45deg, #ffd700, #ffffff, #ffd700);
    -webkit-background-clip: text; background-clip: text;
    mix-blend-mode: screen;
    animation: shine-diagonal 4s infinite linear;
    text-shadow: 2px 2px 6px rgba(0,0,0,0.4);
    z-index: 100; pointer-events: none; opacity: 0; transition: opacity 1s;
}}

/* Main title */
#main-title-container {{
    position: fixed; top: 5%; left: 50%;
    transform: translate(-50%, 0) scale(0.9);
    width: 90%; text-align: center;
    z-index: 20; pointer-events: none;
    color: white; opacity: 0;
    transition: opacity 2s ease, transform 1s ease;
}}
#main-title-container h1 {{
    font-family: 'Poppins', sans-serif; font-weight: 900;
    font-size: 5vw; letter-spacing: 6px; text-transform: uppercase;
    color: transparent;
    background: linear-gradient(90deg, #f0e68c, #ffffff, #f0e68c);
    -webkit-background-clip: text; background-clip: text;
    animation: shine-horizontal 5s infinite linear;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.6);
    position: relative;
}}
#main-title-container h1::after {{
    content: attr(data-text);
    position: absolute; left:0; top:0;
    width:100%; height:100%; color:#fff;
    opacity:0.15; filter: blur(10px); z-index:-1;
}}
#main-title-container h2 {{
    font-family: 'Poppins', sans-serif; font-weight: 300;
    font-size: 1.8vw; color:#e0e0e0;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.6);
    margin-top: 10px;
}}

/* Mobile */
@media (max-width: 768px) {{
    .main-content-revealed {{ background-image: var(--main-bg-url-mobile); }}
    .reveal-grid {{ grid-template-columns: repeat(10, 1fr); grid-template-rows: repeat(20, 1fr); }}
    #main-title-container h1 {{
        font-size: 10vw; letter-spacing: 3px;
        background: linear-gradient(45deg, #ffd700, #ffffff, #ffd700);
        animation: shine-diagonal 5s infinite linear;
    }}
    #main-title-container h2 {{ font-size: 4vw; margin-top: 0.5em; }}
    #intro-text {{ font-size: 8vw; }}
}}
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# --- JS CALLBACK FIXED { } ---
js_callback = f"""
<script>
function sendBackToStreamlit(){{{{ 
    window.parent.document.querySelector('.stApp').classList.add('video-finished','main-content-revealed');
    initRevealEffect();
}}}}

function initRevealEffect(){{{{ 
    const revealGrid = window.parent.document.querySelector('.reveal-grid');
    if(!revealGrid) return;
    const cells = revealGrid.querySelectorAll('.grid-cell');
    const shuffled = Array.from(cells).sort(()=>Math.random()-0.5);
    shuffled.forEach((c,i)=>setTimeout(()=>{{{{ c.style.opacity=0; }}}}, i*10));
    setTimeout(()=>{{{{ 
        revealGrid.remove();
        const mainTitle = window.parent.document.getElementById('main-title-container');
        if(mainTitle){{
            mainTitle.style.opacity=1;
            mainTitle.style.transform='translate(-50%,0) scale(1)';
        }}
    }}}}, shuffled.length*10 + 1000);
}}}}

document.addEventListener("DOMContentLoaded", function(){{{{ 
    const video = document.getElementById('intro-video');
    const audio = document.getElementById('background-audio');
    const introText = document.getElementById('intro-text');
    const isMobile = window.innerWidth <= 768;

    video.src = isMobile ? 'data:video/mp4;base64,{video_mobile_base64}' : 'data:video/mp4;base64,{video_pc_base64}';
    audio.src = 'data:audio/mp3;base64,{audio_base64}';

    const playMedia = () => {{{{
        video.load(); 
        video.play().catch(e => console.log("Video failed:", e));
        setTimeout(() => {{{{ introText.style.opacity = 1; }}}}, 500);
        audio.volume = 0.5; 
        audio.loop = true;
        audio.play().catch(e => {{{{
            document.body.addEventListener('click', () => {{{{ audio.play().catch(() => {{{}}}); }}}}, {{once:true}});
        }}}});
    }}}};

    playMedia();

    video.onended = () => {{{{
        video.style.opacity = 0; 
        audio.pause(); 
        audio.currentTime = 0; 
        introText.style.opacity = 0;
        sendBackToStreamlit();
    }}}};

    document.body.addEventListener('click', () => {{{{ 
        video.play().catch(() => {{{}}}); 
        audio.play().catch(() => {{{}}}); 
    }}}}, {{once:true}});
}}}});
</script>
"""

# --- HTML VIDEO + INTRO TEXT ---
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        html, body {{margin:0;padding:0;overflow:hidden;height:100vh;width:100vw;}}
        #intro-video {{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;z-index:-100;transition:opacity 1s;}}
    </style>
</head>
<body>
    <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    <video id="intro-video" muted playsinline></video>
    <audio id="background-audio"></audio>
    {js_callback}
</body>
</html>
"""
st.components.v1.html(html_content, height=10, scrolling=False)

# --- LƯỚI REVEAL ---
grid_cells_html = "".join([f'<div class="grid-cell"></div>' for i in range(240)])
st.markdown(f'<div class="reveal-grid">{grid_cells_html}</div>', unsafe_allow_html=True)

# --- TIÊU ĐỀ CHÍNH ---
st.markdown("""
<div id="main-title-container">
    <h1 data-text="TỔ BẢO DƯỠNG SỐ 1">TỔ BẢO DƯỠNG SỐ 1</h1>
    <h2>MỞ RA MỘT CHẶNG ĐƯỜNG MỚI</h2>
</div>
""", unsafe_allow_html=True)
