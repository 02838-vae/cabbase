import streamlit as st
import base64

# --- CẤU HÌNH BAN ĐẦU ---
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
        st.error(f"Lỗi: Không tìm thấy file {e.filename}")
        st.stop()

# --- LOAD MEDIA ---
video_pc_base64 = get_base64_encoded_file("airplane.mp4")
video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
audio_base64 = get_base64_encoded_file("plane_fly.mp3")
bg_pc_base64 = get_base64_encoded_file("cabbase.jpg")
bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")

# --- IMPORT FONT ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Stay+Strong&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# --- CSS CHÍNH ---
css = f"""
<style>
#MainMenu, footer, header {{visibility: hidden;}}
div.block-container {{padding:0; margin:0; max-width:100% !important;}}

/* Video iframe */
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
    opacity:0;
    visibility:hidden;
    pointer-events:none;
    height:1px !important;
}}

/* Background */
.stApp {{
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
}}

/* Reveal grid */
.reveal-grid {{
    position: fixed;
    top:0; left:0;
    width:100vw; height:100vh;
    display:grid;
    grid-template-columns:repeat(20,1fr);
    grid-template-rows:repeat(12,1fr);
    z-index:500;
    pointer-events:none;
}}
.grid-cell {{
    background-color:white;
    opacity:1;
    transition: opacity 0.5s ease-out;
}}

.main-content-revealed {{
    background-image: var(--main-bg-url-pc);
    background-size: cover;
    background-position:center;
    background-attachment:fixed;
    filter: sepia(30%) grayscale(10%) brightness(95%);
    transition: filter 2s ease-out;
}}

@media (max-width:768px) {{
    .main-content-revealed {{
        background-image: var(--main-bg-url-mobile);
    }}
    .reveal-grid {{
        grid-template-columns: repeat(10,1fr);
        grid-template-rows: repeat(20,1fr);
    }}
}}

/* Tiêu đề chính */
#main-title-container {{
    position: fixed;
    top:5vh; left:50%;
    transform:translate(-50%,0);
    width:90%;
    text-align:center;
    z-index:20;
    pointer-events:none;
}}
#main-title-container h1 {{
    font-family: 'Stay Strong', cursive !important;
    font-size:3.5vw;
    margin:0;
    font-weight:400;
    letter-spacing:2px;
    color:white;
    text-shadow:3px 3px 6px rgba(0,0,0,0.9);
}}
@media (max-width:768px){{
    #main-title-container h1 {{ font-size:7vw; }}
}}

/* Intro video text */
#intro-text {{
    position: fixed;
    top:5vh;
    width:100%;
    text-align:center;
    color:#FFD700;
    font-size:3vw;
    font-family: 'Sacramento', cursive !important;
    font-weight:400;
    text-shadow:3px 3px 6px rgba(0,0,0,0.8);
    z-index:100;
    pointer-events:none;
    opacity:0;
    filter:blur(10px);
    transition: opacity 1.5s ease-out, filter 1.5s ease-out;
}}
#intro-text.text-shown {{
    opacity:1;
    filter:blur(0);
}}
@media (max-width:768px){{
    #intro-text {{ font-size:6vw; }}
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# --- HTML + JS CHO VIDEO INTRO ---
js_html = f"""
<script>
function sendBackToStreamlit(){{
    window.parent.document.querySelector('.stApp').classList.add('video-finished','main-content-revealed');
    initRevealEffect();
}}
function initRevealEffect(){{
    const revealGrid = window.parent.document.querySelector('.reveal-grid');
    if(!revealGrid) return;
    const cells = revealGrid.querySelectorAll('.grid-cell');
    const shuffled = Array.from(cells).sort(()=>Math.random()-0.5);
    shuffled.forEach((c,i)=>{{ setTimeout(()=>{{c.style.opacity=0;}}, i*10); }});
    setTimeout(()=>{{revealGrid.remove();
        const mainTitle = window.parent.document.getElementById('main-title-container');
        if(mainTitle){{
            mainTitle.style.opacity=1;
            mainTitle.style.transform='translate(-50%,0) scale(1)';
        }}
    }}, shuffled.length*10 + 1000);
}}

document.addEventListener("DOMContentLoaded",function(){{
    const video=document.getElementById('intro-video');
    const audio=document.getElementById('background-audio');
    const introText=document.getElementById('intro-text');
    const isMobile = window.innerWidth<=768;
    video.src = isMobile ? 'data:video/mp4;base64,{video_mobile_base64}' : 'data:video/mp4;base64,{video_pc_base64}';
    audio.src='data:audio/mp3;base64,{audio_base64}';
    
    video.load(); video.play().catch(()=>{});
    audio.volume=0.5; audio.loop=true; audio.play().catch(()=>{{
        document.body.addEventListener('click',()=>{{audio.play();}},{{once:true}});
    }});
    setTimeout(()=>{{ introText.classList.add('text-shown'); }},500);

    video.onended = ()=>{{
        video.style.opacity=0;
        audio.pause(); audio.currentTime=0;
        introText.classList.remove('text-shown'); introText.style.opacity=0;
        sendBackToStreamlit();
    }};
    document.body.addEventListener('click',()=>{{ video.play(); audio.play(); }},{{once:true}});
}});
</script>
"""

html_content = f"""
<div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
<video id="intro-video" muted playsinline></video>
<audio id="background-audio"></audio>
{js_html}
"""

st.components.v1.html(html_content, height=10, scrolling=False)

# --- Reveal grid ---
grid_cells = "".join([f'<div class="grid-cell"></div>' for _ in range(240)])
st.markdown(f'<div class="reveal-grid">{grid_cells}</div>', unsafe_allow_html=True)

# --- Nội dung chính ---
st.markdown("""
<div id="main-title-container" style="opacity:0; transition:opacity 2s, transform 1s; transform:translate(-50%,0) scale(0.9);">
    <h1>TỔ BẢO DƯỠNG SỐ 1</h1>
</div>
""", unsafe_allow_html=True)
