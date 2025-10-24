import streamlit as st
import base64

# Cấu hình trang (Tắt menu mặc định)
st.set_page_config(
    page_title="Khám phá cùng chúng tôi",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Áp dụng CSS để ép Streamlit main container và iframe Fullscreen
hide_streamlit_style = """
<style>
/* ... (Giữ nguyên CSS fullscreen cho Streamlit và iframe) ... */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.main {padding: 0; margin: 0;}

div.block-container {
    padding: 0;
    margin: 0;
    max-width: 100% !important;
}

iframe {
    width: 100vw !important;
    height: 100vh !important;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1000;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def get_base64_encoded_file(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode("utf-8")

# Mã hóa các file media
try:
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    
    # SỬA LỖI TÊN FILE: Đã sử dụng "cabbase.jpg"
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
    
except FileNotFoundError as e:
    st.error(f"Lỗi: Không tìm thấy file media. Vui lòng kiểm tra lại đường dẫn: {e.filename}")
    st.stop()


# Số lượng ô vuông (tiles) cho hiệu ứng lật (10x10 = 100 ô)
NUM_TILES = 100
TILES_PER_ROW = 10
TILE_SIZE_PERCENT = 100 / TILES_PER_ROW # 10.0%
BACKGROUND_SIZE_PERCENT = TILES_PER_ROW * 100 # 1000%

# Tạo HTML cho 100 ô vuông
tiles_html = "".join([f'<div class="tile"></div>' for _ in range(NUM_TILES)])


# --- MÃ HTML/CSS/JavaScript ĐÃ SỬA LỖI TÊN FILE BACKGROUND ---

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        /* CSS CHUNG */
        html, body {{
            margin: 0; 
            padding: 0; 
            overflow: hidden; 
            height: 100vh; 
            width: 100vw;
            perspective: 1000px; 
        }}
        
        /* ---------------------------------------------------- */
        /* 1. LỚP INTRO (Được thay bằng các mảnh lật) */
        /* ---------------------------------------------------- */
        #intro-tiles-container {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 2000;
            display: flex;
            flex-wrap: wrap;
            pointer-events: none;
        }}

        /* Mỗi mảnh (tile) là một phần của hiệu ứng lật */
        .tile {{
            width: {TILE_SIZE_PERCENT}vw; 
            height: {TILE_SIZE_PERCENT}vh; 
            position: relative;
            transform-style: preserve-3d; 
            transition: transform 0.8s ease-in-out; 
            cursor: pointer;
            pointer-events: all; 
            
            background-size: {BACKGROUND_SIZE_PERCENT}%; /* Kích thước tổng thể 1000% */
            background-position: var(--tile-bg-x) var(--tile-bg-y);
            background-repeat: no-repeat;
        }}

        /* Sử dụng pseudo-element cho mặt trước 3D */
        .tile::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: black;
            backface-visibility: hidden; 
        }}
        
        /* Hiệu ứng lật đã kích hoạt */
        .page-flipped .tile {{
            transform: rotateY(180deg); 
        }}
        
        /* ---------------------------------------------------- */
        /* 2. LỚP TRANG CHÍNH (Nội dung chính) */
        /* ---------------------------------------------------- */
        #main-content {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1000; 
            background-size: cover;
            background-position: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
            padding: 20px;
            box-sizing: border-box;
            overflow-y: auto; 
            opacity: 0;
            transition: opacity 1s ease-in 1s; 
        }}
        .page-flipped #main-content {{
            opacity: 1;
        }}


        /* ---------------------------------------------------- */
        /* 3. ĐIỀU CHỈNH CHUNG */
        /* ---------------------------------------------------- */

        #intro-text {{
            position: fixed;
            top: 5vh; 
            width: 100%;
            text-align: center;
            color: white; 
            font-size: 3vw; 
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9); 
            z-index: 3000; 
            pointer-events: none;
            opacity: 0; 
            transition: opacity 1s; 
        }}
        
        @media (max-width: 768px) {{
            #intro-text {{
                font-size: 8vw;
            }}
            #main-content {{
                background-image: url('data:image/jpeg;base64,{bg_mobile_base64}');
            }}
        }}

        @media (min-width: 769px) {{
            #main-content {{
                /* ĐÃ SỬA LỖI: Dùng cabbase.jpg */
                background-image: url('data:image/jpeg;base64,{bg_pc_base64}');
            }}
        }}

    </style>
</head>
<body id="app-body">
    
    <div id="main-content">
        <h1>TRANG CHỦ ĐÃ SẴN SÀNG!</h1>
        <p>Chào mừng bạn đến với thế giới đầy cảm hứng của chúng tôi.</p>
        <button style="padding: 10px 20px; margin-top: 20px; font-size: 1.2em; cursor: pointer; background-color: #007bff; color: white; border: none; border-radius: 5px;">Bắt đầu khám phá</button>
        <div style="height: 1000px; padding: 20px; background: rgba(0,0,0,0.5); margin-top: 50px;">
            <p>Phần cuộn (Scrollable content) của trang chính.</p>
        </div>
    </div>

    <video id="intro-video-hidden" muted playsinline style="display: none;"></video>
    <audio id="background-audio"></audio>

    <div id="intro-tiles-container">
        {tiles_html}
    </div>
    
    <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>


    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            const appBody = document.getElementById('app-body');
            const hiddenVideo = document.getElementById('intro-video-hidden');
            const audio = document.getElementById('background-audio');
            const introText = document.getElementById('intro-text');
            const tiles = document.querySelectorAll('.tile');
            
            const numTilesPerRow = {TILES_PER_ROW}; 
            
            function isMobile() {{
                return window.innerWidth <= 768;
            }}
            
            const videoSource = isMobile()
                ? 'data:video/mp4;base64,{video_mobile_base64}' 
                : 'data:video/mp4;base64,{video_pc_base64}';

            // 1. Cấu hình nguồn Video và Audio
            hiddenVideo.src = videoSource;
            audio.src = 'data:audio/mp3;base64,{audio_base64}';

            // 2. Thiết lập background cho từng mảnh (tile)
            tiles.forEach((tile, index) => {{
                const col = index % numTilesPerRow;
                const row = Math.floor(index / numTilesPerRow);
                
                const backgroundPosX = -col * 100 + '%'; 
                const backgroundPosY = -row * 100 + '%';

                tile.style.setProperty('--tile-bg-x', backgroundPosX);
                tile.style.setProperty('--tile-bg-y', backgroundPosY);
                
                // Set background là video intro
                tile.style.backgroundImage = 'url(' + videoSource + ')'; 

                // Thiết lập độ trễ ngẫu nhiên cho hiệu ứng lật
                const delay = Math.random() * 0.5; 
                tile.style.transitionDelay = delay + 's';
            }});
            
            const playMedia = () => {{
                hiddenVideo.load();
                hiddenVideo.play().catch(e => console.log("Hidden Video playback failed:", e));
                
                setTimeout(() => {{ introText.style.opacity = 1; }}, 500);

                audio.volume = 0.5; 
                audio.play().catch(e => {{
                    document.body.addEventListener('click', () => {{
                        audio.play().catch(err => console.error("Audio playback error on click:", err));
                    }}, {{ once: true }});
                }});
            }};
            
            playMedia();

            // 3. Logic HIỆU ỨNG LẬT khi video kết thúc
            hiddenVideo.onended = () => {{
                audio.pause(); 
                audio.currentTime = 0; 
                introText.style.opacity = 0;
                
                appBody.classList.add('page-flipped');
                
                setTimeout(() => {{
                    document.getElementById('intro-tiles-container').style.display = 'none';
                    // Cho phép cuộn trang chính
                    document.body.style.overflow = 'auto'; 
                    document.getElementById('main-content').style.position = 'static';
                }}, 1500); 
                
                console.log("Video intro đã kết thúc. Đang kích hoạt hiệu ứng Lật trang.");
            }};
        }});
    </script>
</body>
</html>
"""

# Hiển thị thành phần HTML
st.components.v1.html(html_content, height=10, scrolling=False)
