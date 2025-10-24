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

# --- CSS ĐỂ ÉP STREAMLIT MAIN CONTAINER & IFRAME FULLSCREEN/ẨN IFRAME ---
hide_streamlit_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;900&family=Raleway:wght@600;800&display=swap');

/* Ẩn các thành phần mặc định của Streamlit */
#MainMenu, footer, header {{visibility: hidden;}}

/* Đảm bảo Main Content Container chiếm toàn bộ không gian và không có padding */
.main {{ padding: 0; margin: 0; }}
div.block-container {{ padding: 0; margin: 0; max-width: 100% !important; }}

/* IFRAME VIDEO INTRO */
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

/* Nền full-screen cho main content */
.stApp {{
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
}}

/* CSS Reveal Grid */
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
}}

/* Mobile */
@media (max-width: 768px) {{
    .main-content-revealed {{
        background-image: var(--main-bg-url-mobile);
    }}
    .reveal-grid {{
        grid-template-columns: repeat(10, 1fr);
        grid-template-rows: repeat(20, 1fr);
    }}
}}

/* === TIÊU ĐỀ TRANG CHÍNH === */
#main-title-container {{
    position: fixed;
    top: 5vh;
    left: 50%;
    transform: translate(-50%, 0); 
    width: 90%; 
    text-align: center;
    z-index: 20; 
    pointer-events: none; 
}}
#main-title-container h1 {{
    font-size: 3vw;
    margin: 0;
    font-weight: 800;
    letter-spacing: 5px;
    font-family: 'Raleway', sans-serif;
    color: white;
    text-shadow: 3px 3px 6px rgba(0,0,0,0.9);
}}
@media (max-width: 768px) {{
    #main-title-container h1 {{ font-size: 8vw; }}
}}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- HTML/JS VIDEO INTRO ---
js_callback = f"""
<script>
function sendBackToStreamlit() {{
    window.parent.document.querySelector('.stApp').classList.add('video-finished','main-content-revealed');
    initRevealEffect();
}}

function initRevealEffect() {{
    const revealGrid = window.parent.document.querySelector('.reveal-grid');
    if (!revealGrid) return;
    const cells = revealGrid.querySelectorAll('.grid-cell');
    const shuffledCells = Array.from(cells).sort(() => Math.random()-0.5);
    shuffledCells.forEach((cell,index) => {{
        setTimeout(() => {{ cell.style.opacity = 0; }}, index*10);
    }});
    setTimeout(() => {{ revealGrid.remove();
        const mainTitle = window.parent.document.getElementById('main-title-container');
        if(mainTitle) {{
            mainTitle.style.opacity=1;
            mainTitle.style.transform='translate(-50%,0) scale(1)';
        }}
    }}, shuffledCells.length*10 +1000);
}}

document.addEventListener("DOMContentLoaded", function() {{
    const video = document.getElementById('intro-video');
    const audio = document.getElementById('background-audio');
    const introText = document.getElementById('intro-text');
    const isMobile = window.innerWidth<=768;

    if(isMobile) video.src='data:video/mp4;base64,{video_mobile_base64}';
    else video.src='data:video/mp4;base64,{video_pc_base64}';
    audio.src='data:audio/mp3;base64,{audio_base64}';

    const playMedia = ()=>{{
        video.load(); video.play().catch(e=>console.log(e));
        setTimeout(()=>{{ introText.classList.add('text-shown'); }},500);
        audio.volume=0.5; audio.loop=true; audio.play().catch(e=>{{ document.body.addEventListener('click',()=>{{audio.play().catch(err=>console.error(err));}},{{once:true}}); }});
    }};
    playMedia();
    video.onended=()=>{{
        video.style.opacity=0; audio.pause(); audio.currentTime=0;
        introText.classList.remove('text-shown'); introText.style.opacity=0;
        sendBackToStreamlit();
    }};
}});
</script>
"""

html_content_modified = f"""
<!DOCTYPE html>
<html>
<head>
<style>
html,body {{ margin:0; padding:0; overflow:hidden; height:100vh; width:100vw; }}
#intro-video {{
    position:absolute; top:0; left:0; width:100%; height:100%;
    object-fit:cover; z-index:-100; transition:opacity 1s;
}}
#intro-text {{
    position: fixed; top:5vh; width:100%; text-align:center;
    color:#FFD700; font-size:3.5vw; font-weight:900; z-index:100;
    pointer-events:none; font-family:'Montserrat',sans-serif;
    text-shadow:3px 3px 6px rgba(0,0,0,0.8);
    opacity:0; filter:blur(10px); transition:opacity 1.5s, filter 1.5s;
}}
#intro-text.text-shown {{ opacity:1; filter:blur(0); }}
@media (max-width:768px){{ #intro-text{{ font-size:7vw; }} }}
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
st.components.v1.html(html_content_modified, height=10, scrolling=False)

# --- Reveal Grid ---
grid_cells_html = "".join([f'<div class="grid-cell"></div>' for i in range(240)])
reveal_grid_html = f"<div class='reveal-grid'>{grid_cells_html}</div>"
st.markdown(reveal_grid_html, unsafe_allow_html=True)

# --- Tiêu đề trang chính ---
st.markdown("""
<div id="main-title-container" style="opacity:0; transition:opacity 2s, transform 1s; transform:translate(-50%,0) scale(0.9);">
    <h1>TỔ BẢO DƯỠNG SỐ 1</h1>
</div>
""", unsafe_allow_html=True)
