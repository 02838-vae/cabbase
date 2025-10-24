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
    
    # ĐẢM BẢO TÊN FILE LÀ CABBASE.JPG
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
except FileNotFoundError as e:
    st.error(e)
    st.stop()


# --- CSS ĐỂ ÉP STREAMLIT MAIN CONTAINER & IFRAME FULLSCREEN/ẨN IFRAME ---
# SỬA LỖI F-STRING: NHÂN ĐÔI DẤU NGOẶC NHỌN {} TRONG KHỐI CSS
hide_streamlit_style = f"""
<style>
/* Reset Streamlit UI */
#MainMenu, footer, header {{visibility: hidden;}}
.main {{padding: 0; margin: 0;}}
div.block-container {{padding: 0; margin: 0; max-width: 100% !important;}}

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

/* Nền Trang Chính */
.stApp {{
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
}}
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


/* --- HIỆU ỨNG ÁNH SÁNG VÀ TIÊU ĐỀ --- */

/* Keyframes cho hiệu ứng ánh sáng ngang (PC & Intro) */
@keyframes shine-horizontal {{
    0% {{ background-position: -150% 0; }}
    100% {{ background-position: 250% 0; }}
}}

/* Keyframes cho hiệu ứng ánh sáng nghiêng (Mobile) */
@keyframes shine-diagonal {{
    0% {{ background-position: -200% 0; }}
    100% {{ background-position: 300% 0; }}
}}


/* 1. TIÊU ĐỀ TRÊN VIDEO (INTRO TEXT) */
#intro-text {{
    position: fixed; top: 5vh; width: 100%; text-align: center;
    /* Áp dụng hiệu ứng ánh sáng mới */
    color: transparent; 
    background: linear-gradient(45deg, #ffd700, #ffffff, #ffd700); /* Gradient nghiêng màu vàng */
    background-size: 200% 100%; /* Tăng kích thước cho ánh sáng nghiêng */
    background-repeat: no-repeat;
    -webkit-background-clip: text;
    background-clip: text;
    animation: shine-diagonal 4s infinite linear; /* Dùng hiệu ứng nghiêng */
    
    font-size: 4vw; /* Tăng kích thước cho cả PC và Mobile */
    font-weight: bold;
    text-shadow: 
        1px 1px 2px rgba(0,0,0,0.5),
        2px 2px 3px rgba(0,0,0,0.4),
        3px 3px 5px rgba(0,0,0,0.3);
    z-index: 100; pointer-events: none; opacity: 0; transition: opacity 1s;
}}


/* 2. TIÊU ĐỀ TRANG CHÍNH */
#main-title-container {{
    position: fixed; top: 5%; left: 50%;
    transform: translate(-50%, 0); 
    width: 90%; text-align: center;
    z-index: 20; pointer-events: none;
    line-height: 1.2;
}}

/* PC: Tiêu đề H1 (Tổ bảo dưỡng số 1) - Ánh sáng ngang */
#main-title-container h1 {{
    font-size: 5vw; 
    margin: 0; font-weight: 900; letter-spacing: 5px;
    color: transparent; 
    background: linear-gradient(90deg, #f0e68c, #ffffff, #f0e68c); /* Ánh sáng ngang */
    background-size: 150% 100%; /* Kích thước rộng hơn để ánh sáng rõ hơn */
    background-repeat: no-repeat;
    -webkit-background-clip: text;
    background-clip: text;
    animation: shine-horizontal 5s infinite linear; /* Dùng hiệu ứng ngang */
    text-shadow: 
        1px 1px 2px rgba(0,0,0,0.5), 2px 2px 3px rgba(0,0,0,0.4), 3px 3px 5px rgba(0,0,0,0.3);
}}

/* PC: Tiêu đề H2 (Mở ra một chặng đường mới) */
#main-title-container h2 {{
    font-size: 1.8vw; 
    margin: 10px 0 0 0; font-weight: 300;
    color: #e0e0e0;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.6);
}}


/* 3. ĐIỀU CHỈNH CHO MOBILE */
@media (max-width: 768px) {{
    .main-content-revealed {{
        background-image: var(--main-bg-url-mobile);
    }}
    .reveal-grid {{
        grid-template-columns: repeat(10, 1fr); grid-template-rows: repeat(20, 1fr);
    }}
    
    /* Mobile: Tiêu đề H1 (Tổ bảo dưỡng số 1) - Ánh sáng nghiêng */
    #main-title-container h1 {{
        font-size: 10vw; 
        letter-spacing: 3px;
        background: linear-gradient(45deg, #ffd700, #ffffff, #ffd700); /* Ánh sáng nghiêng */
        background-size: 200% 100%; 
        animation: shine-diagonal 5s infinite linear; /* Dùng hiệu ứng nghiêng */
        text-shadow: 1px 1px 1px rgba(0,0,0,0.5), 2px 2px 2px rgba(0,0,0,0.4);
    }}

    /* Mobile: Tiêu đề H2 (Mở ra một chặng đường mới) - Gần hơn */
    #main-title-container h2 {{
        font-size: 4vw; 
        margin: 5px 0 0 0; 
        text-shadow: 1px 1px 1px rgba(0,0,0,0.6);
    }}
    
    #intro-text {{
        font-size: 8vw; /* Kích thước lớn hơn trên mobile */
    }}
}}
</style>
"""

# Thêm CSS vào trang chính
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- MÃ HTML/CSS/JavaScript IFRAME CHO VIDEO INTRO ---

# JavaScript (Không thay đổi logic)
js_callback = f"""
<script>
    function sendBackToStreamlit() {{
        window.parent.document.querySelector('.stApp').classList.add('video-finished', 'main-content-revealed');
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
                
            setTimeout(() => {{ introText.style.opacity = 1; }}, 500);

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

# Mã HTML/CSS cho Video
html_content_modified = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        html, body {{
            margin: 0; padding: 0; overflow: hidden; height: 100vh; width: 100vw;
        }}
        #intro-video {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            object-fit: cover; z-index: -100; transition: opacity 1s; 
        }}
        /* CSS cho #intro-text đã được định nghĩa trong hide_streamlit_style */
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


# --- HIỆU ỨNG REVEAL VÀ NỘI DUNG CHÍNH (CHỈ TIÊU ĐỀ) ---

# Tạo Lưới Reveal (20x12 = 240 ô)
grid_cells_html = ""
for i in range(240): 
    grid_cells_html += f'<div class="grid-cell"></div>'

reveal_grid_html = f"""
<div class="reveal-grid">
    {grid_cells_html}
</div>
"""
st.markdown(reveal_grid_html, unsafe_allow_html=True)
    

# Nội dung chính của trang (CHỈ CÓ TIÊU ĐỀ)
st.markdown("""
<div id="main-title-container" style="color: white; opacity: 0; transition: opacity 2s, transform 1s; transform: translate(-50%, 0) scale(0.9); text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.9);">
    <h1>TỔ BẢO DƯỠNG SỐ 1</h1>
    <h2>MỞ RA MỘT CHẶNG ĐƯỜNG MỚI</h2>
</div>
""", unsafe_allow_html=True)
