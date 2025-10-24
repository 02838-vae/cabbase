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
/* 1. THÊM GOOGLE FONT IMPORT CHO FONT RETRO (PRESS START 2P) */
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Montserrat:wght@900&display=swap');

/* Ẩn các thành phần mặc định của Streamlit */
#MainMenu, footer, header {{visibility: hidden;}}

/* Đảm bảo Main Content Container chiếm toàn bộ không gian và không có padding */
.main {{
    padding: 0;
    margin: 0;
}}

/* Đảm bảo khu vực nội dung được căn chỉnh sát lề */
div.block-container {{
    padding: 0;
    margin: 0;
    max-width: 100% !important;
}}

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

/* Class để ẩn iframe (được thêm bằng JS) */
.video-finished iframe:first-of-type {{
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
    height: 1px !important; 
}}

/* Định nghĩa nền full-screen cho main content */
.stApp {{
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
}}

/* CSS cho hiệu ứng Reveal */
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

/* Class được thêm vào .stApp sau khi video kết thúc */
.main-content-revealed {{
    /* Đặt nền cho toàn bộ ứng dụng */
    background-image: var(--main-bg-url-pc);
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    
    /* 2. HIỆU ỨNG FILTER HOÀI CỔ: giảm bão hòa và thêm độ mờ */
    filter: grayscale(30%) brightness(80%) blur(1px); 
    transition: filter 2s ease-out; 
}}

/* Điều chỉnh cho Mobile */
@media (max-width: 768px) {{
    .main-content-revealed {{
        background-image: var(--main-bg-url-mobile);
    }}
    .reveal-grid {{
        grid-template-columns: repeat(10, 1fr);
        grid-template-rows: repeat(20, 1fr);
    }}
}}

/* === CHỈNH SỬA CHO TIÊU ĐỀ TRANG CHÍNH === */
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

/* Đặt kích thước và FONT RETRO cho tiêu đề chính (H1) */
#main-title-container h1 {{
    font-size: 5vw; 
    margin: 0;
    font-weight: 400; /* Font Retro thường không quá đậm */
    letter-spacing: 5px;
    /* ÁP DỤNG FONT RETRO */
    font-family: 'Press Start 2P', cursive; 
    /* MÀU SẮC RETRO */
    color: #F8B400; /* Vàng đậm (Gợi nhớ ánh sáng màn hình cũ) */
    /* BÓNG CHỮ ĐỂ NỔI BẬT HƠN TRÊN NỀN MỜ */
    text-shadow: 
        1px 1px 0px #FF00FF, /* Màu Magenta */
        -1px -1px 0px #00FFFF, /* Màu Cyan */
        0 0 10px rgba(248, 180, 0, 0.8); /* Bóng sáng */
}}

/* Giữ nguyên kích thước trên Mobile */
@media (max-width: 768px) {{
    #main-title-container h1 {{
        font-size: 8vw; 
    }}
}}

/* 3. HIỆU ỨNG GRAIN/NOISE (HẠT NHIỄU) */
.grain-overlay {{
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 999; /* Dưới video intro, trên nội dung */
    pointer-events: none;
    opacity: 0.15; /* Độ trong suốt của hạt nhiễu */
    
    /* Tạo hiệu ứng hạt nhiễu bằng background gradient nhỏ lặp lại */
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2 2"><filter id="a"><feTurbulence baseFrequency="0.6" type="fractalNoise" result="c" numOctaves="3" /><feColorMatrix type="saturate" values="0" /></filter><rect width="100%" height="100%" filter="url(%23a)" opacity="0.1" /></svg>');
    background-size: 200px 200px;
}}

/* Ẩn lớp phủ nhiễu khi video đang chạy */
.stApp:not(.main-content-revealed) .grain-overlay {{
    display: none;
}}
</style>
"""

# Thêm CSS vào trang chính
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- MÃ HTML/CSS/JavaScript IFRAME CHO VIDEO INTRO (Cập nhật Font-family) ---

# JavaScript (Giữ nguyên logic Blur-in)
js_callback = f"""
<script>
    function sendBackToStreamlit() {{
        // **BƯỚC 1: Kích hoạt nền và ẩn video**
        window.parent.document.querySelector('.stApp').classList.add('video-finished', 'main-content-revealed');
        
        // **BƯỚC 2: Kích hoạt Hiệu ứng Reveal**
        initRevealEffect();
    }}
    
    function initRevealEffect() {{
        const revealGrid = window.parent.document.querySelector('.reveal-grid');
        if (!revealGrid) return;

        const cells = revealGrid.querySelectorAll('.grid-cell');
        const shuffledCells = Array.from(cells).sort(() => Math.random() - 0.5);

        shuffledCells.forEach((cell, index) => {{
            setTimeout(() => {{
                cell.style.opacity = 0; 
            }}, index * 10);
        }});
        
        setTimeout(() => {{
             revealGrid.remove();
             const mainTitle = window.parent.document.getElementById('main-title-container');
             if (mainTitle) {{
                 mainTitle.style.opacity = 1;
                 mainTitle.style.transform = 'translate(-50%, 0) scale(1)';
             }}
        }}, shuffledCells.length * 10 + 1000);
    }}

    document.addEventListener("DOMContentLoaded", function() {{
        const video = document.getElementById('intro-video');
        const audio = document.getElementById('background-audio');
        const introText = document.getElementById('intro-text');
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
                
            setTimeout(() => {{ 
                introText.classList.add('text-shown'); 
            }}, 500);

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
            introText.classList.remove('text-shown');
            introText.style.opacity = 0;
            
            sendBackToStreamlit(); 
        }};

        document.body.addEventListener('click', () => {{
             video.play().catch(e => {{}});
             audio.play().catch(e => {{}});
        }}, {{ once: true }});
    }});
</script>
"""

# Mã HTML/CSS cho Video (Cập nhật Font-family)
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

        /* Tiêu đề Intro (Sử dụng Font 'Montserrat' cho rõ ràng hơn trong intro) */
        #intro-text {{
            position: fixed;
            top: 5vh;
            width: 100%;
            text-align: center;
            color: #FFD700; 
            font-size: 3.5vw; 
            font-weight: 900; 
            text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.8); 
            z-index: 100;
            pointer-events: none;
            /* FONT HIỆN ĐẠI HƠN CHO INTRO VIDEO */
            font-family: 'Montserrat', sans-serif; 

            /* HIỆU ỨNG BLUR-IN */
            opacity: 0; 
            filter: blur(10px);
            transition: opacity 1.5s ease-out, filter 1.5s ease-out; 
        }}
        
        #intro-text.text-shown {{
            opacity: 1;
            filter: blur(0); 
        }}

        @media (max-width: 768px) {{
            #intro-text {{
                font-size: 7vw; 
            }}
        }}
        
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

# Hiển thị thành phần HTML (video)
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

# Lớp phủ Grain/Noise (Hạt nhiễu)
st.markdown("""
<div class="grain-overlay"></div>
""", unsafe_allow_html=True)


# Nội dung chính của trang 
st.markdown("""
<div id="main-title-container" style="color: white; opacity: 0; transition: opacity 2s, transform 1s; transform: translate(-50%, 0) scale(0.9); text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.9);">
    <h1>TỔ BẢO DƯỠNG SỐ 1</h1>
</div>
""", unsafe_allow_html=True)
