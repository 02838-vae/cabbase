import streamlit as st
import base64
import random 
# KHÔNG CẦN IMPORT streamlit_player NỮA

# --- CẤU HÌNH BAN ĐẦU ---

st.set_page_config(
    page_title="Tổ Bảo Dưỡng Số 1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- KHỞI TẠO STATE & CỜ KIỂM TRA (SỬ DỤNG st.query_params) ---

# Đọc cờ từ query params
query_params = st.query_params
video_ended_flag = query_params.get('video_ended_flag') == 'true'

if 'video_ended' not in st.session_state:
    st.session_state.video_ended = video_ended_flag

if video_ended_flag:
    st.session_state.video_ended = True


# --- CÁC HÀM TIỆN ÍCH ---

def get_base64_encoded_file(file_path):
    """Đọc file và trả về Base64 encoded string."""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    except FileNotFoundError as e:
        # Nếu đang chạy trên Streamlit Cloud, các file này phải tồn tại
        raise FileNotFoundError(f"Lỗi: Không tìm thấy file media. Vui lòng kiểm tra lại đường dẫn: {e.filename}")

# ------------------------------------------------------------------
## PHẦN MÃ HÓA CÁC FILE MEDIA 
# ------------------------------------------------------------------

try:
    # Media Intro 
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    
    # Backgrounds
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
    
except FileNotFoundError as e:
    st.error(e)
    st.stop()

# --- PHẦN 1: NHÚNG FONT & CSS CHUNG (ĐÃ SỬA LỖI CÚ PHÁP) ---

font_links = """
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
"""
st.markdown(font_links, unsafe_allow_html=True)

hide_streamlit_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sacramento&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');

/* Ẩn các thành phần mặc định của Streamlit */
#MainMenu, footer, header {{visibility: hidden;}}

.main {{ padding: 0; margin: 0; }}
div.block-container {{ padding: 0; margin: 0; max-width: 100% !important; }}

/* IFRAME VIDEO INTRO */
iframe:first-of-type {{
    transition: opacity 1s ease-out, visibility 1s ease-out;
    opacity: 1; visibility: visible; width: 100vw !important; height: 100vh !important;
    position: fixed; top: 0; left: 0; z-index: 1000;
}}

.video-finished iframe:first-of-type {{
    opacity: 0; visibility: hidden; pointer-events: none; height: 1px !important; 
}}

/* BACKGROUND CHÍNH */
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
    .main-content-revealed {{ background-image: var(--main-bg-url-mobile); }}
}}

/* REVEAL GRID */
.reveal-grid {{
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    display: grid; grid-template-columns: repeat(20, 1fr); grid-template-rows: repeat(12, 1fr);
    z-index: 500; pointer-events: none; 
}}

.grid-cell {{ background-color: white; opacity: 1; transition: opacity 0.5s ease-out; }}


/* TIÊU ĐỀ CHÍNH */
@keyframes scrollText {{ 0% {{ transform: translate(100vw, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
@keyframes colorShift {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}

#main-title-container {{ position: fixed; top: 5vh; left: 0; width: 100%; height: 10vh; overflow: hidden; z-index: 20; pointer-events: none; opacity: 0; transition: opacity 2s; }}
#main-title-container h1 {{
    font-family: 'Playfair Display', serif; font-size: 3.5vw; margin: 0; font-weight: 900; letter-spacing: 5px; white-space: nowrap; display: inline-block; 
    animation: colorShift 10s ease infinite, scrollText 15s linear infinite;
    background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
    background-size: 400% 400%; -webkit-background-clip: text; -webkit-text-fill-color: transparent; color: transparent;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5); 
}}

@media (max-width: 768px) {{
    #main-title-container {{ height: 8vh; width: 100%; left: 0; }}
    #main-title-container h1 {{ font-size: 6.5vw; animation-duration: 8s; }}
}}

/* CSS DÀNH RIÊNG CHO ST.AUDIO (ĐÃ SỬA LỖI CÚ PHÁP) */
div.stAudio + div {{ /* Chọn div liền kề sau stAudio container */
    position: fixed !important;
    bottom: 20px !important;
    right: 20px !important;
    z-index: 10000 !important;
    width: 300px !important; 
    border-radius: 8px !important;
    overflow: hidden !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
    opacity: 0.9 !important;
    margin: 0 !important;
    padding: 0 !important;
    
    /* Làm cho Player st.audio ẩn đi khi intro chưa kết thúc */
    visibility: hidden;
    transition: visibility 0s, opacity 0.5s linear;
}}

.main-content-revealed div.stAudio + div {{
    visibility: visible;
    opacity: 1;
}}

/* Đảm bảo thẻ audio bên trong lấp đầy container */
div.stAudio + div audio {{
    width: 100%;
}}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ------------------------------------------------------------------
## PHẦN 3: MÃ HTML/CSS/JavaScript IFRAME CHO VIDEO INTRO (FIXED)
# ------------------------------------------------------------------

# JavaScript (Giữ nguyên logic reload)
js_callback_video = f"""
<script>
    function sendBackToStreamlit() {{
        window.parent.document.querySelector('.stApp').classList.add('video-finished', 'main-content-revealed');
        initRevealEffect();
        
        const currentUrl = new URL(window.parent.location);
        currentUrl.searchParams.set('video_ended_flag', 'true');
        
        // Tải lại trang chính Streamlit
        window.parent.location.replace(currentUrl.toString()); 
    }}
    
    function initRevealEffect() {{
        const revealGrid = window.parent.document.querySelector('.reveal-grid');
        const mainTitle = window.parent.document.getElementById('main-title-container');
        
        if (mainTitle) {{ mainTitle.style.opacity = 1; }}

        if (!revealGrid) {{ return; }}
        
        const cells = revealGrid.querySelectorAll('.grid-cell');
        const shuffledCells = Array.from(cells).sort(() => Math.random() - 0.5);
        shuffledCells.forEach((cell, index) => {{
            setTimeout(() => {{ cell.style.opacity = 0; }}, index * 10);
        }});
    }}


    document.addEventListener("DOMContentLoaded", function() {{
        const video = document.getElementById('intro-video');
        const introTextContainer = document.getElementById('intro-text-container'); 
        const isMobile = window.innerWidth <= 768;


        if (isMobile) {{
            video.src = 'data:video/mp4;base64,{video_mobile_base64}';
        }} else {{
            video.src = 'data:video/mp4;base64,{video_pc_base64}';
        }}
        
        const playMedia = () => {{
            video.load();
            video.play().catch(e => console.log("Video playback failed:", e));
                
            const chars = introTextContainer.querySelectorAll('.intro-char');
            chars.forEach((char, index) => {{
                char.style.animationDelay = `${{index * 0.1}}s`; 
                char.classList.add('char-shown'); 
            }});
        }};
        
        const urlParams = new URLSearchParams(window.parent.location.search);
        if (urlParams.get('video_ended_flag') === 'true') {{
            video.style.opacity = 0;
            introTextContainer.style.opacity = 0; 
            window.parent.document.querySelector('.stApp').classList.add('video-finished', 'main-content-revealed');
            initRevealEffect(); 
        }} else {{
            playMedia();
            
            video.onended = () => {{
                video.style.opacity = 0;
                introTextContainer.style.opacity = 0; 
                sendBackToStreamlit(); 
            }};
            
            document.body.addEventListener('click', () => {{
                video.play().catch(e => {{}});
            }}, {{ once: true }});
        }}
    }});
</script>
"""

# Mã HTML/CSS cho Video 
html_content_modified = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        html, body {{ margin: 0; padding: 0; overflow: hidden; height: 100vh; width: 100vw; }}
        #intro-video {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: -100; transition: opacity 1s; }}
        #intro-text-container {{ position: fixed; top: 5vh; width: 100%; text-align: center; color: #FFD700; font-size: 3vw; font-family: 'Sacramento', cursive; font-weight: 400; text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.8); z-index: 100; pointer-events: none; display: flex; justify-content: center; opacity: 1; }}
        .intro-char {{ display: inline-block; opacity: 0; transform: translateY(-50px); animation-fill-mode: forwards; animation-duration: 0.8s; animation-timing-function: ease-out; }}
        @keyframes charDropIn {{ from {{ opacity: 0; transform: translateY(-50px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .intro-char.char-shown {{ animation-name: charDropIn; }}
        @media (max-width: 768px) {{ #intro-text-container {{ font-size: 6vw; }} }}
    </style>
</head>
<body>
    <div id="intro-text-container">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    <video id="intro-video" muted playsinline></video>
    {js_callback_video}
</body>
</html>
"""

intro_title = "KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI"
intro_chars_html = ''.join([
    f'<span class="intro-char">{char}</span>' if char != ' ' else '<span class="intro-char">&nbsp;</span>' 
    for char in intro_title
])
html_content_modified = html_content_modified.replace(
    "<div id=\"intro-text-container\">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>",
    f"<div id=\"intro-text-container\">{intro_chars_html}</div>"
)


# Hiển thị thành phần HTML (video)
if not st.session_state.video_ended:
    st.components.v1.html(html_content_modified, height=10, scrolling=False)


# --- HIỆU ỨNG REVEAL VÀ NỘI DUNG CHÍNH ---

# Tạo Lưới Reveal (Giữ nguyên)
grid_cells_html = ""
for i in range(240): 
    grid_cells_html += f'<div class="grid-cell"></div>'

reveal_grid_html = f"""
<div class="reveal-grid">
    {grid_cells_html}
</div>
"""
st.markdown(reveal_grid_html, unsafe_allow_html=True)


# --- NỘI DUNG CHÍNH (TIÊU ĐỀ ĐƠN, ĐỔI MÀU) ---

main_title_text = "TỔ BẢO DƯỠNG SỐ 1" 

st.markdown(f"""
<div id="main-title-container">
    <h1>{main_title_text}</h1>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
## PHẦN BỔ SUNG: ST.AUDIO (TỆP ĐƠN)
# ------------------------------------------------------------------

# ⚠️ BẠN PHẢI THAY THẾ URL NÀY BẰNG URL MP3 CÔNG KHAI CỦA BẠN
# KHÔNG DÙNG LINK PLAYLIST SOUNDCLOUD.
audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" # URL MP3 mẫu

# st.audio() sẽ tự động render Player
if st.session_state.video_ended:
    # Player sẽ được render ở vị trí này, và CSS sẽ cố định nó
    st.audio(audio_url, format="audio/mp3", loop=True)
