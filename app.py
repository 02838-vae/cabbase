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
    
    # Mã hóa các file hình nền MỚI (Đã xác nhận là cabbage.jpg)
    bg_pc_base64 = get_base64_encoded_file("cabbage.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
    
except FileNotFoundError as e:
    st.error(f"Lỗi: Không tìm thấy file media. Vui lòng kiểm tra lại đường dẫn: {e.filename}")
    st.stop()


# Số lượng ô vuông (tiles) cho hiệu ứng lật (10x10 = 100 ô)
NUM_TILES = 100
TILES_PER_ROW = 10

# Tạo HTML cho 100 ô vuông
tiles_html = ""
for i in range(NUM_TILES):
    # Mỗi ô vuông sẽ chứa video intro (được cắt bằng CSS)
    tiles_html += f'<div class="tile"></div>'


# --- MÃ HTML/CSS/JavaScript ĐÃ THÊM HIỆU ỨNG LẬT TRANG (PAGE FLIP) ---

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
            perspective: 1000px; /* Cần thiết cho hiệu ứng 3D flip */
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
            pointer-events: none; /* Không chặn click */
        }}

        /* Mỗi mảnh (tile) là một phần của hiệu ứng lật */
        .tile {{
            width: {100 / TILES_PER_ROW}vw; /* 100/10 = 10vw */
            height: {100 / TILES_PER_ROW}vh; /* 100/10 = 10vh */
            position: relative;
            transform-style: preserve-3d; /* Rất quan trọng cho 3D */
            transition: transform 0.8s ease-in-out; /* Thời gian lật của mỗi ô */
            cursor: pointer;
            pointer-events: all; /* Cho phép JS điều khiển */
        }}

        /* Nội dung mặt trước của mỗi ô (Video Intro) */
        .tile::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: black;
            backface-visibility: hidden; /* Ẩn mặt trước khi lật */
            
            /* Dùng background-image thay vì video, JS sẽ fill bằng video */
            background-size: cover;
            background-position: center;
        }}

        /* Hiệu ứng lật đã kích hoạt */
        .page-flipped .tile {{
            transform: rotateY(180deg); /* Lật 180 độ */
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
            z-index: 1000; /* Dưới lớp tiles */
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
            /* Thêm hiệu ứng mờ dần khi hiện ra */
            opacity: 0;
            transition: opacity 1s ease-in 1s; /* Bắt đầu mờ sau 1s lật */
        }}
        .page-flipped #main-content {{
            opacity: 1;
        }}


        /* ---------------------------------------------------- */
        /* 3. ĐIỀU CHỈNH CHUNG */
        /* ---------------------------------------------------- */

        /* CSS cho dòng chữ cố định (Di chuyển lên trên lớp tiles) */
        #intro-text {{
            position: fixed;
            top: 5vh; 
            width: 100%;
            text-align: center;
            color: white; 
            font-size: 3vw; 
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9); 
            z-index: 3000; /* Cao hơn cả tiles */
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
            const tilesContainer = document.getElementById('intro-tiles-container');
            const hiddenVideo = document.getElementById('intro-video-hidden');
            const audio = document.getElementById('background-audio');
            const introText = document.getElementById('intro-text');
            const isMobile = window.innerWidth <= 768;
            const tiles = document.querySelectorAll('.tile');
            
            const numTilesPerRow = {TILES_PER_ROW}; 
            const videoSource = isMobile 
                ? 'data:video/mp4;base64,{video_mobile_base64}' 
                : 'data:video/mp4;base64,{video_pc_base64}';

            // 1. Cấu hình nguồn Video (Chỉ cần set cho video ẩn)
            hiddenVideo.src = videoSource;
            audio.src = 'data:audio/mp3;base64,{audio_base64}';

            // 2. Thiết lập background cho từng mảnh (tile)
            tiles.forEach((tile, index) => {{
                // Tính toán vị trí background cho mỗi tile để cắt video thành 100 mảnh
                const col = index % numTilesPerRow;
                const row = Math.floor(index / numTilesPerRow);
                
                const backgroundPosX = -col * 100 + '%'; // 0%, -100%, -200%...
                const backgroundPosY = -row * 100 + '%'; // 0%, -100%, -200%...

                tile.style.setProperty('--tile-bg-x', backgroundPosX);
                tile.style.setProperty('--tile-bg-y', backgroundPosY);
                
                // Set background là video intro
                tile.style.setProperty('background-image', 'url(' + videoSource + ')'); 

                // Thiết lập độ trễ ngẫu nhiên cho hiệu ứng lật
                const delay = Math.random() * 0.5; // Độ trễ tối đa 0.5s
                tile.style.transitionDelay = delay + 's';
            }});
            
            // Cần cập nhật lại CSS để áp dụng background-image cho :before
            // Do phức tạp của việc sử dụng ::before, ta sẽ dùng background-image trực tiếp trên .tile
            const styleElement = document.createElement('style');
            styleElement.innerHTML = `
                .tile {{
                    background-size: {numTilesPerRow * 100}%; /* Kích thước tổng thể 1000% (10x) */
                    background-position: var(--tile-bg-x) var(--tile-bg-y);
                    background-repeat: no-repeat;
                }}
            `;
            document.head.appendChild(styleElement);


            const playMedia = () => {{
                // Chạy video ẩn (chỉ để đồng bộ âm thanh và lấy sự kiện onended)
                hiddenVideo.load();
                hiddenVideo.play().catch(e => console.log("Video playback failed:", e));
                
                setTimeout(() => {{ introText.style.opacity = 1; }}, 500);

                audio.volume = 0.5; 
                audio.play().catch(e => {{
                    // Yêu cầu tương tác người dùng nếu autoplay bị chặn
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
                
                // Kích hoạt hiệu ứng Lật: Thêm class 'page-flipped' vào body
                appBody.classList.add('page-flipped');
                
                // Tùy chọn: Xóa intro-tiles-container sau khi chuyển cảnh hoàn tất (~1.5s)
                setTimeout(() => {{
                    tilesContainer.style.display = 'none';
                    // Đảm bảo main content có thể cuộn (vì body đang là overflow: hidden)
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
