import streamlit as st
import base64
from streamlit_player import st_player # Thư viện cho Music Player

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
        # Trả về None nếu file nhạc nền không có
        if file_path.startswith("background"):
            return None 
        # Báo lỗi nếu các file quan trọng khác bị thiếu
        raise FileNotFoundError(f"Lỗi: Không tìm thấy file media quan trọng. Vui lòng kiểm tra lại đường dẫn: {e.filename}")

# Mã hóa các file media
try:
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")

    # MÃ HÓA CÁC FILE NHẠC NỀN
    background_music_files = [f"background{i}.mp3" for i in range(1, 7)]
    bg_music_urls = []
    for f in background_music_files:
        b64_data = get_base64_encoded_file(f)
        if b64_data:
            # Dùng định dạng URL Data cho file Base64
            bg_music_urls.append(f'data:audio/mp3;base64,{b64_data}')

except FileNotFoundError as e:
    st.error(e)
    st.stop()
    
# --- PHẦN 1: NHÚNG FONT BẰNG THẺ LINK TRỰC TIẾP VÀO BODY ---
font_links = """
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
"""
st.markdown(font_links, unsafe_allow_html=True)

# --- PHẦN 2: CSS CHÍNH (STREAMLIT APP) ---
hide_streamlit_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sacramento&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');

/* Ẩn các thành phần mặc định của Streamlit */
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

/* Điều khiển Video Intro */
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

/* Keyframes cho hiệu ứng chữ chạy đơn (từ phải sang trái, lặp lại) */
@keyframes scrollText {{
    0% {{ transform: translate(100vw, 0); }} 
    100% {{ transform: translate(-100%, 0); }} 
}}

/* Keyframes cho hiệu ứng Đổi Màu Gradient */
@keyframes colorShift {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}


/* === TIÊU ĐỀ TRANG CHÍNH (ĐƠN, CHẠY VÀ ĐỔI MÀU) === */
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
    font-feature-settings: "lnum" 1; 
    letter-spacing: 5px; 
    white-space: nowrap; 
    
    display: inline-block; 

    animation: colorShift 10s ease infinite, scrollText 15s linear infinite; 
    
    background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3); 
    background-size: 400% 400%; 
    -webkit-background-clip: text; 
    -webkit-text-fill-color: transparent; 
    color: transparent; 
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5); 
}}

@media (max-width: 768px) {{
    #main-title-container {{
        height: 8vh;
        width: 100%; 
        left: 0;
    }}
    
    #main-title-container h1 {{
        font-size: 6.5vw; 
        animation-duration: 8s; 
    }}
}}

/* === STYLES CHO MUSIC PLAYER === */
.music-player-container {{
    position: fixed;
    bottom: 20px; 
    right: 20px;
    z-index: 50; 
    opacity: 0;
    transition: opacity 1s ease-in;
}}

.video-finished .music-player-container {{
    opacity: 1;
}}

/* === KHẮC PHỤC: ẨN NÚT TRIGGER MỘT CÁCH TRIỆT ĐỂ BẰNG CONTAINER CSS === */
.hidden-trigger-container {{
    position: fixed;
    top: 0;
    left: 0;
    width: 0;
    height: 0;
    overflow: hidden;
    opacity: 0;
    pointer-events: none; /* Rất quan trọng để không cản trở click */
    z-index: 9999;
}}
/* Dù đã ẩn container, vẫn đảm bảo nút bên trong bị disable tương tác */
.hidden-trigger-container button {{
    visibility: hidden !important;
    pointer-events: none !important;
}}
</style>
"""

# Thêm CSS vào trang chính
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- PHẦN 3: MÃ HTML/CSS/JavaScript IFRAME CHO VIDEO INTRO ---

# JavaScript (Đã CHỈNH SỬA để KÍCH HOẠT RERUN và CẬP NHẬT Session State)
js_callback_video = f"""
<script>
    function sendBackToStreamlit() {{
        // 1. Gửi lệnh CSS để ẩn video và reveal nội dung chính
        window.parent.document.querySelector('.stApp').classList.add('video-finished', 'main-content-revealed');
        initRevealEffect();

        // 2. Gửi lệnh cập nhật Streamlit Session State 
        // Tìm button ẩn do Streamlit tạo và click nó để kích hoạt Rerun
        const hiddenButton = window.parent.document.getElementById('video-ended-trigger');
        if (hiddenButton) {{
            hiddenButton.click(); 
        }}
    }}
    
    function initRevealEffect() {{
        const revealGrid = window.parent.document.querySelector('.reveal-grid');
        const mainTitle = window.parent.document.getElementById('main-title-container');

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
        const audio = document.getElementById('background-audio');
        const introTextContainer = document.getElementById('intro-text-container'); 
        const isMobile = window.innerWidth <= 768;

        if (isMobile) {{
            video.src = 'data:video/mp4;base64,{video_mobile_base64}';
        }} else {{
            video.src = 'data:video/mp4;base64,{video_pc_base64}';
        }}
        
        audio.src = 'data:audio/mp3;base64,{audio_base64}';

        const playMedia = () => {{
            video.load();
            video.play().catch(e => console.log("Video playback failed:", e));
                
            const chars = introTextContainer.querySelectorAll('.intro-char');
            chars.forEach((char, index) => {{
                char.style.animationDelay = `${{index * 0.1}}s`; 
                char.classList.add('char-shown'); 
            }});

            audio.volume = 0.5;
            audio.loop = true; 
            audio.play().catch(e => {{
                document.body.addEventListener('click', () => {{
                    audio.play().catch(err => console.error("Audio playback error on click:", err));
                }}, {{ once: true }});
            }});
        }};
            
        playMedia();
        
        video.onended = () => {{
            video.style.opacity = 0;
            audio.pause();
            audio.currentTime = 0;
            introTextContainer.style.opacity = 0; 
            
            sendBackToStreamlit(); 
        }};

        document.body.addEventListener('click', () => {{
             video.play().catch(e => {{}});
             audio.play().catch(e => {{}});
        }}, {{ once: true }});
    }});
</script>
"""

# Mã HTML/CSS cho Video (Giữ nguyên cấu trúc HTML)
html_content_modified = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            height: 100vh;
            width: 100vw;
        }}
        
        #intro-video {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            z-index: -100;
            transition: opacity 1s; 
        }}

        /* === TIÊU ĐỀ INTRO === */
        #intro-text-container {{ 
            position: fixed;
            top: 5vh;
            width: 100%;
            text-align: center;
            color: #FFD700; 
            font-size: 3vw; 
            
            font-family: 'Sacramento', cursive; 
            font-weight: 400; 
            
            text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.8); 
            z-index: 100;
            pointer-events: none;
            display: flex; 
            justify-content: center;
            opacity: 1; 
        }}
        
        .intro-char {{
            display: inline-block; 
            opacity: 0;
            transform: translateY(-50px); 
            animation-fill-mode: forwards; 
            animation-duration: 0.8s; 
            animation-timing-function: ease-out; 
        }}

        @keyframes charDropIn {{
            from {{
                opacity: 0;
                transform: translateY(-50px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .intro-char.char-shown {{
            animation-name: charDropIn;
        }}

        @media (max-width: 768px) {{
            #intro-text-container {{
                font-size: 6vw; 
            }}
        }}
        
    </style>
</head>
<body>

    <div id="intro-text-container">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    
    <video id="intro-video" muted playsinline></video>
    
    <audio id="background-audio"></audio>

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


# ----------------------------------------------------------------------------------
# --- LOGIC CẬP NHẬT STATE VÀ NỘI DUNG CHÍNH ---
# ----------------------------------------------------------------------------------

# Hàm callback để cập nhật state sau khi video kết thúc
def set_video_ended():
    st.session_state.video_ended = True

# --- KHẮC PHỤC: Ẩn nút Trigger bằng cách bọc trong container CSS ---
st.markdown('<div class="hidden-trigger-container">', unsafe_allow_html=True)
st.button(
    "Video Ended Trigger", 
    key="video-ended-trigger", 
    on_click=set_video_ended, 
)
st.markdown('</div>', unsafe_allow_html=True)


# --- HIỆU ỨNG REVEAL VÀ NỘI DUNG CHÍNH ---

# Tạo Lưới Reveal (Chỉ chạy khi chưa kết thúc video)
if not st.session_state.video_ended:
    grid_cells_html = ""
    for i in range(240): 
        grid_cells_html += f'<div class="grid-cell"></div>'

    reveal_grid_html = f"""
    <div class="reveal-grid">
        {grid_cells_html}
    </div>
    """
    st.markdown(reveal_grid_html, unsafe_allow_html=True)


# --- NỘI DUNG CHÍNH (TIÊU ĐỀ ĐƠN, ĐỔI MÀU & MUSIC PLAYER) ---

# Tiêu đề đơn
main_title_text = "TỔ BẢO DƯỠNG SỐ 1" 

# Nhúng tiêu đề (Đã được CSS fixed)
st.markdown(f"""
<div id="main-title-container">
    <h1>{main_title_text}</h1>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------------
# THÊM MUSIC PLAYER DÙNG streamlit-player 
# ----------------------------------------------------------------------------------

if st.session_state.video_ended and bg_music_urls:
    # 1. Tạo container cố định vị trí bằng CSS
    st.markdown('<div class="music-player-container">', unsafe_allow_html=True)
    
    # 2. Gọi st_player
    st_player(
        url=bg_music_urls,
        playing=True,
        loop=True,
        controls=True,
        config={ # Config cần thiết cho Base64 URLs
            "file": {
                "forceAudio": True
            }
        },
        height=60, # Chiều cao tối thiểu cho audio player
        width=280, # Chiều rộng hợp lý
        key="bg_music_player"
    )

    # 3. Đóng container
    st.markdown('</div>', unsafe_allow_html=True)

# --- NỘI DUNG TRANG CHÍNH KHÁC ---
if st.session_state.video_ended:
    # Dùng markdown để tạo khoảng trống phía dưới tiêu đề cố định
    st.markdown('<br>' * 8, unsafe_allow_html=True) 

    st.header("Chào mừng đến với Trang Chủ! 👋")
    st.write("Đây là nội dung chính của ứng dụng. Trang đã được reveal và nhạc nền đã được tự động phát.")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Về Tổ Bảo Dưỡng")
        st.info("Chúng tôi là đội ngũ chuyên gia hàng đầu trong lĩnh vực bảo trì và sửa chữa máy bay.")
    with col2:
        st.subheader("Dịch Vụ")
        st.success("Kiểm tra định kỳ, bảo dưỡng khẩn cấp, nâng cấp hệ thống.")
