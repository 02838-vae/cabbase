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
## PHẦN MÃ HÓA CÁC FILE MEDIA (ĐÃ LOẠI BỎ logic sử dụng plane_fly.mp3 cho intro)
# ------------------------------------------------------------------

try:
    # Media Intro (Giữ nguyên)
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    
    # Audio Intro (Chỉ mã hóa, nhưng KHÔNG dùng trong iframe nữa)
    # Giữ nguyên dòng này để tránh lỗi nếu các biến khác cần nó, 
    # nhưng chúng ta sẽ loại bỏ việc phát nó trong JS bên dưới.
    audio_intro_base64 = get_base64_encoded_file("plane_fly.mp3") 
    
    # Backgrounds
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")

    # Audio Trang Chính (Playlist)
    audio_files = {
        "background1": get_base64_encoded_file("background1.mp3"),
        "background2": get_base64_encoded_file("background2.mp3"),
        "background3": get_base64_encoded_file("background3.mp3"),
    }
    
    # Tạo danh sách các data URL cho player chính
    audio_urls = [f'data:audio/mp3;base64,{b64_data}' for b64_data in audio_files.values()]
    audio_urls_js = ",".join([f"'{url}'" for url in audio_urls]) 
    
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

/* BACKGROUND CHÍNH */
.stApp {{
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
}}

.reveal-grid {{
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    display: grid; grid-template-columns: repeat(20, 1fr); grid-template-rows: repeat(12, 1fr);
    z-index: 500; pointer-events: none; 
}}

.grid-cell {{ background-color: white; opacity: 1; transition: opacity 0.5s ease-out; }}

.main-content-revealed {{
    background-image: var(--main-bg-url-pc);
    background-size: cover; background-position: center; background-attachment: fixed;
    filter: sepia(60%) grayscale(20%) brightness(85%) contrast(110%); 
    transition: filter 2s ease-out; 
}}

@media (max-width: 768px) {{
    .main-content-revealed {{ background-image: var(--main-bg-url-mobile); }}
    .reveal-grid {{ grid-template-columns: repeat(10, 1fr); grid-template-rows: repeat(20, 1fr); }}
}}

/* Keyframes và Tiêu đề chính */
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
</style>
"""
# Thêm CSS vào trang chính
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ------------------------------------------------------------------
## PHẦN 3: MÃ HTML/CSS/JavaScript IFRAME CHO VIDEO INTRO (ĐÃ GỠ BỎ NHẠC INTRO)
# ------------------------------------------------------------------

# JavaScript (Đã GỠ BỎ mọi lệnh liên quan đến audio intro)
js_callback_video = f"""
<script>
    function sendBackToStreamlit() {{
        window.parent.document.querySelector('.stApp').classList.add('video-finished', 'main-content-revealed');
        initRevealEffect();
    }}
    
    function initRevealEffect() {{
        const revealGrid = window.parent.document.querySelector('.reveal-grid');
        const mainTitle = window.parent.document.getElementById('main-title-container');
        
        // Cố gắng kích hoạt player nhạc chính sau khi intro kết thúc
        const mainAudioPlayer = window.parent.document.getElementById('main-audio-player'); 
        if (mainAudioPlayer) {{
            // Cố gắng play. Nếu thất bại, người dùng phải click vào controls
            mainAudioPlayer.play().catch(e => console.log("Main Audio Autoplay failed. Click controls to start.", e)); 
        }}


        if (mainTitle) {{
            mainTitle.style.opacity = 1; 
        }}

        if (!revealGrid) {{ return; }}

        const cells = revealGrid.querySelectorAll('.grid-cell');
        const shuffledCells = Array.from(cells).sort(() => Math.random() - 0.5);

        shuffledCells.forEach((cell, index) => {{
            setTimeout(() => {{
                cell.style.opacity = 0; 
            }}, index * 10);
        }});
        
        setTimeout(() => {{
            revealGrid.remove();
        }}, shuffledCells.length * 10 + 1000);
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
        
        // Đã gỡ bỏ: audio.src = 'data:audio/mp3;base64,{audio_intro_base64}'; 

        const playMedia = () => {{
            video.load();
            video.play().catch(e => console.log("Video playback failed:", e));
                
            const chars = introTextContainer.querySelectorAll('.intro-char');
            chars.forEach((char, index) => {{
                char.style.animationDelay = `${{index * 0.1}}s`; 
                char.classList.add('char-shown'); 
            }});
            
            // Đã gỡ bỏ: Logic play audio intro
        }};
            
        playMedia();
        
        video.onended = () => {{
            video.style.opacity = 0;
            // Đã gỡ bỏ: audio.pause(); audio.currentTime = 0;
            introTextContainer.style.opacity = 0; 
            
            sendBackToStreamlit(); 
        }};

        // Kích hoạt video intro khi user click bất kỳ đâu
        document.body.addEventListener('click', () => {{
            video.play().catch(e => {{}});
            // Đã gỡ bỏ: audio.play().catch(e => {{}});
        }}, {{ once: true }});
    }});
</script>
"""


# Mã HTML/CSS cho Video (Đã gỡ bỏ thẻ <audio> khỏi iframe)
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


# Xử lý nội dung của tiêu đề video intro để thêm hiệu ứng chữ thả
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
## PHẦN BỔ SUNG: MUSIC PLAYER CHO TRANG CHÍNH (ĐÃ TỐI ƯU HÓA)
# ------------------------------------------------------------------

# JavaScript để xử lý danh sách phát và tự động chuyển bài (Đã Tối Ưu Hóa)
player_script_js = f"""
<script>
    // Danh sách các URL Base64 của 3 bài hát
    const audioUrls = [{audio_urls_js}];
    let currentTrackIndex = 0;
    
    const player = document.getElementById('main-audio-player');
    
    if (player) {{
        
        // --- Hàm gán và tải bài hát ---
        function loadTrack(index) {{
            player.src = audioUrls[index];
            player.load();
            console.log("Player Debug: Đã tải bài hát:", index + 1, "từ", audioUrls.length, "bài.");
            
            // Xóa bỏ hàm oncanplay cũ để tránh lỗi gọi đệ quy
            player.oncanplay = null; 
        }}
        
        // --- Xử lý lỗi (Quan trọng) ---
        player.onerror = (e) => {{
            console.error("Player Debug: Lỗi khi tải hoặc phát nhạc.", player.error.code);
            console.error("Player Debug: Chi tiết lỗi:", player.error);
            
            // Thử chuyển bài nếu bài hiện tại bị lỗi (Lỗi 4: MEDIA_ERR_SRC_NOT_SUPPORTED)
            if (player.error.code === 4) {{ 
                setTimeout(() => {{ 
                    console.log("Player Debug: Base64/File bị lỗi. Thử chuyển sang bài tiếp theo...");
                    currentTrackIndex = (currentTrackIndex + 1) % audioUrls.length;
                    loadTrack(currentTrackIndex);
                }}, 1000);
            }}
        }};

        // --- Khởi tạo và Playlist Logic ---
        
        // 1. Chọn ngẫu nhiên một bài hát khi trang load
        currentTrackIndex = Math.floor(Math.random() * audioUrls.length);
        loadTrack(currentTrackIndex);
        
        // 2. Xử lý tự động chuyển bài khi bài hát kết thúc
        player.addEventListener('ended', () => {{
            currentTrackIndex = (currentTrackIndex + 1) % audioUrls.length; 
            loadTrack(currentTrackIndex);
            // Sau khi tải bài mới, cố gắng play ngay (cần tương tác ban đầu của user)
            player.play().catch(e => console.log("Player Debug: Autoplay bài kế tiếp bị chặn.")); 
        }});
        
        // 3. Debug Play/Pause
        player.addEventListener('play', () => {{
            console.log("Player Debug: Bắt đầu phát track:", currentTrackIndex + 1);
        }});
    }}
</script>
"""

# HTML Audio Player (Hiển thị Controls)
audio_player_html = f"""
<div style="position: fixed; bottom: 20px; right: 20px; z-index: 10000; opacity: 0.8; border-radius: 5px; background: rgba(0,0,0,0.5); padding: 5px;">
    <audio id="main-audio-player" controls>
        Trình duyệt của bạn không hỗ trợ phần tử audio.
    </audio>
</div>

{player_script_js}
"""

# Chèn player vào trang chính sau phần nội dung chính
st.markdown(audio_player_html, unsafe_allow_html=True)
