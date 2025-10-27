import streamlit as st
import base64
import random 

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

# ------------------------------------------------------------------
## PHẦN MÃ HÓA CÁC FILE MEDIA (CHỈ CẦN VIDEO VÀ HÌNH NỀN)
# ------------------------------------------------------------------

try:
    # Media Intro 
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    
    # Backgrounds
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
    
    # KHÔNG CẦN mã hóa plane_fly.mp3 hay backgroundX.mp3 nữa
    
except FileNotFoundError as e:
    st.error(e)
    st.stop()

# --- PHẦN 1: NHÚNG FONT ---
font_links = """
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
"""
st.markdown(font_links, unsafe_allow_html=True)

# ------------------------------------------------------------------
## PHẦN 2: CSS CHÍNH (STREAMLIT APP)
# ------------------------------------------------------------------

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

/* BACKGROUND CHÍNH và TIÊU ĐỀ */

.stApp {{
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
}}
/* ... (Giữ nguyên CSS còn lại cho Reveal Grid, main-content-revealed và Tiêu đề chạy) ... */

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
/* CSS cho player cố định (quan trọng) */
.soundcloud-player-fixed {{
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 10000;
    width: 300px; /* Chiều rộng cố định cho Player */
    height: 150px; /* Chiều cao cố định cho Player */
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    transition: opacity 1s;
    opacity: 0; /* Ẩn player lúc đầu */
}}
.video-finished .soundcloud-player-fixed {{
    opacity: 1; /* Hiển thị player sau khi video intro kết thúc */
}}
.reveal-grid {{
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    display: grid; grid-template-columns: repeat(20, 1fr); grid-template-rows: repeat(12, 1fr);
    z-index: 500; pointer-events: none; 
}}

.grid-cell {{ background-color: white; opacity: 1; transition: opacity 0.5s ease-out; }}
</style>
"""
# Thêm CSS vào trang chính
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ------------------------------------------------------------------
## PHẦN 3: MÃ HTML/CSS/JavaScript IFRAME CHO VIDEO INTRO (ĐÃ BỎ NHẠC)
# ------------------------------------------------------------------

# JavaScript (Đã BỎ hoàn toàn logic nhạc intro)
js_callback_video = f"""
<script>
    function sendBackToStreamlit() {{
        // Thêm class 'video-finished' để kích hoạt hiệu ứng CSS (ví dụ: hiển thị SoundCloud player)
        window.parent.document.querySelector('.stApp').classList.add('video-finished', 'main-content-revealed');
        initRevealEffect();
    }}
    
    function initRevealEffect() {{
        const revealGrid = window.parent.document.querySelector('.reveal-grid');
        const mainTitle = window.parent.document.getElementById('main-title-container');
        
        if (mainTitle) {{
            mainTitle.style.opacity = 1; 
        }}

        if (!revealGrid) {{ return; }}
        
        // Logic Reveal Grid (Giữ nguyên)
        const cells = revealGrid.querySelectorAll('.grid-cell');
        const shuffledCells = Array.from(cells).sort(() => Math.random() - 0.5);
        shuffledCells.forEach((cell, index) => {{
            setTimeout(() => {{ cell.style.opacity = 0; }}, index * 10);
        }});
        
        setTimeout(() => {{ revealGrid.remove(); }}, shuffledCells.length * 10 + 1000);
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
            
        playMedia();
        
        video.onended = () => {{
            video.style.opacity = 0;
            introTextContainer.style.opacity = 0; 
            sendBackToStreamlit(); 
        }};

        // Kích hoạt video intro khi user click bất kỳ đâu
        document.body.addEventListener('click', () => {{
            video.play().catch(e => {{}});
        }}, {{ once: true }});
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


# Xử lý nội dung của tiêu đề video intro
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
st.components.v1.html(html_content_modified, height=10, scrolling=False)


# --- HIỆU ỨNG REVEAL VÀ NỘI DUNG CHÍNH ---

# Tạo Lưới Reveal 
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
## PHẦN BỔ SUNG: SOUNDCLOUD EMBED PLAYER (ĐẢM BẢO HOẠT ĐỘNG)
# ------------------------------------------------------------------

# Mã nhúng của Playlist SoundCloud bạn cung cấp
# Đã điều chỉnh autoplay=false để tuân thủ quy tắc trình duyệt, nhưng nó sẽ hiện controls
SOUNDCLOUD_EMBED_CODE = """
<iframe width="100%" height="150" scrolling="no" frameborder="no" allow="autoplay" 
src="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/playlists/1879007623&color=%23ff5500&auto_play=false&hide_related=false&show_comments=true&show_user=true&show_reposts=false&show_teaser=true&visual=true">
</iframe>
"""

# HTML để cố định Player và ẩn/hiện bằng CSS (dùng class 'soundcloud-player-fixed' đã định nghĩa ở trên)
soundcloud_player_html = f"""
<div class="soundcloud-player-fixed">
    {SOUNDCLOUD_EMBED_CODE}
</div>
"""

# Chèn player vào trang chính
st.markdown(soundcloud_player_html, unsafe_allow_html=True)
