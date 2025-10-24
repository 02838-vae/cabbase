import streamlit as st
import base64

# Cấu hình trang (Tắt menu mặc định)
st.set_page_config(
    page_title="Tổ Bảo Dưỡng Số 1",
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

# Tạo HTML cho 100 ô vuông lật (mặt trước là video, mặt sau là màu đen)
tiles_html = ""
for i in range(NUM_TILES):
    # Mỗi tile cần hai mặt (front và back) cho hiệu ứng lật 3D
    tiles_html += f"""
        <div class="tile">
            <div class="tile-face front">
                <video id="video-tile-{i}" muted playsinline></video>
            </div>
            <div class="tile-face back"></div>
        </div>
    """


# --- MÃ HTML/CSS/JavaScript ĐÃ SỬA LỖI VIDEO PLAYBACK VÀ NỘI DUNG CHÍNH ---

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
        /* 1. LỚP INTRO (Mảnh lật) */
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
        }}

        /* Mỗi mảnh (tile) là một phần của hiệu ứng lật */
        .tile {{
            width: {TILE_SIZE_PERCENT}vw; 
            height: {TILE_SIZE_PERCENT}vh; 
            position: relative;
            transform-style: preserve-3d; /* Rất quan trọng cho 3D */
            transition: transform 0.8s ease-in-out; 
            pointer-events: all; 
        }}
        
        /* Các mặt của ô lật */
        .tile-face {{
            position: absolute;
            width: 100%;
            height: 100%;
            backface-visibility: hidden; /* Ẩn mặt bị quay lưng lại */
        }}

        /* Mặt sau (Back) của ô lật */
        .tile-face.back {{
            background-color: black; /* Màu đen hoặc màu nền trang chính */
            transform: rotateY(180deg); /* Mặt sau quay 180 độ */
        }}

        /* Video trong mỗi ô (đảm bảo nó lấp đầy ô và chỉ hiển thị 1/100) */
        .tile-face.front video {{
            position: absolute;
            top: 0;
            left: 0;
            width: {BACKGROUND_SIZE_PERCENT}vw; /* 1000vw */
            height: {BACKGROUND_SIZE_PERCENT}vh; /* 1000vh */
            object-fit: cover;
            /* Mỗi video sẽ được định vị bằng JS để hiển thị 1/100 màn hình */
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
            justify-content: flex-start; /* Căn tiêu đề lên trên */
            align-items: center;
            color: white;
            padding-top: 15vh; /* Khoảng cách từ trên xuống */
            box-sizing: border-box;
            overflow-y: auto; 
            opacity: 0;
            transition: opacity 1s ease-in 1s; 
        }}
        .page-flipped #main-content {{
            opacity: 1;
        }}
        
        /* Tiêu đề trang chính */
        #main-content h1 {{
            font-size: 5vw; 
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7); 
            margin: 0;
        }}


        /* ---------------------------------------------------- */
        /* 3. ĐIỀU CHỈNH CHUNG & MEDIA QUERIES */
        /* ---------------------------------------------------- */

        /* DÒNG CHỮ INTRO */
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
             #main-content h1 {{
                font-size: 10vw; 
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
        <h1>TỔ BẢO DƯỠNG SỐ 1</h1>
    </div>

    <audio id="background-audio"></audio>

    <div id="intro-tiles-container">
        {tiles_html}
    </div>
    
    <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>


    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            const appBody = document.getElementById('app-body');
            const audio = document.getElementById('background-audio');
            const introText = document.getElementById('intro-text');
            const tiles = document.querySelectorAll('.tile');
            const tileVideos = document.querySelectorAll('.tile-face.front video');
            
            const numTilesPerRow = {TILES_PER_ROW}; 
            const videoSource = isMobile()
                ? 'data:video/mp4;base64,{video_mobile_base64}' 
                : 'data:video/mp4;base64,{video_pc_base64}';

            function isMobile() {{
                return window.innerWidth <= 768;
            }}

            // 1. Cấu hình nguồn Video và Audio
            audio.src = 'data:audio/mp3;base64,{audio_base64}';

            // 2. Thiết lập đồng bộ và vị trí cho từng thẻ <video>
            tileVideos.forEach((videoElement, index) => {{
                // Đặt nguồn video cho từng thẻ
                videoElement.src = videoSource;

                const col = index % numTilesPerRow;
                const row = Math.floor(index / numTilesPerRow);
                
                // Tính toán vị trí dịch chuyển để chỉ hiển thị 1/100 màn hình
                const transformX = -col * 100 + 'vw'; 
                const transformY = -row * 100 + 'vh'; 

                // Áp dụng dịch chuyển cho mỗi video (giữ video Fullscreen, nhưng cắt nó)
                videoElement.style.transform = `translate(-${{col * 10}}%, -${{row * 10}}%)`; 
            }});
            
            const playMedia = () => {{
                // Chạy tất cả các video cùng lúc
                tileVideos.forEach(videoElement => {{
                    videoElement.load();
                    videoElement.play().catch(e => console.log("Video playback failed:", e));
                }});
                
                setTimeout(() => {{ introText.style.opacity = 1; }}, 500);

                // Autoplay Audio (Cần tương tác người dùng nếu bị chặn)
                audio.volume = 0.5; 
                audio.play().catch(e => {{
                    document.body.addEventListener('click', () => {{
                        audio.play().catch(err => console.error("Audio playback error on click:", err));
                    }}, {{ once: true }});
                }});
            }};
            
            playMedia();

            // 3. Logic HIỆU ỨNG LẬT khi một video (tileVideos[0]) kết thúc
            tileVideos[0].onended = () => {{
                // Dừng tất cả các video và âm thanh
                tileVideos.forEach(videoElement => videoElement.pause());
                audio.pause(); 
                audio.currentTime = 0; 
                introText.style.opacity = 0;
                
                // Kích hoạt hiệu ứng Lật
                appBody.classList.add('page-flipped');
                
                setTimeout(() => {{
                    document.getElementById('intro-tiles-container').style.display = 'none';
                    document.body.style.overflow = 'auto'; 
                    document.getElementById('main-content').style.position = 'static';
                }}, 1500); 
            }};

            // 4. Thiết lập độ trễ ngẫu nhiên cho hiệu ứng lật
            tiles.forEach(tile => {{
                const delay = Math.random() * 0.5; 
                tile.style.transitionDelay = delay + 's';
            }});
        }});
    </script>
</body>
</html>
"""

# Hiển thị thành phần HTML
st.components.v1.html(html_content, height=10, scrolling=False)
