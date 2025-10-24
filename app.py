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
    /* Đảm bảo iframe của component chiếm toàn bộ chiều cao/rộng */
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
    
    # Mã hóa các file hình nền MỚI
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
    
except FileNotFoundError as e:
    st.error(f"Lỗi: Không tìm thấy file media. Vui lòng kiểm tra lại đường dẫn: {e.filename}")
    st.stop()


# --- MÃ HTML/CSS/JavaScript ĐÃ THÊM HIỆU ỨNG REVEAL ---

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        /* CSS CHUNG (Đã sửa lỗi Fullscreen) */
        html, body {{
            margin: 0; 
            padding: 0; 
            overflow: hidden; 
            height: 100vh; 
            width: 100vw;
        }}
        
        /* Lớp chứa Intro (Video + Chữ) - Lớp trên cùng */
        #intro-screen {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 2000; /* Lớp cao hơn cả iframe */
            background-color: black;
            transition: transform 1s cubic-bezier(.8,0,.2,1); /* Hiệu ứng Reveal */
        }}

        /* CSS cho video fullscreen */
        #intro-video {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            z-index: -100;
        }}

        /* CSS cho dòng chữ cố định */
        #intro-text {{
            position: fixed;
            top: 5vh; 
            width: 100%;
            text-align: center;
            color: white; 
            font-size: 3vw; 
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7); 
            z-index: 100; 
            pointer-events: none;
            opacity: 0; 
            transition: opacity 1s; 
        }}
        
        /* CSS TRANG CHÍNH (Lớp dưới) */
        #main-content {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1000; /* Lớp dưới intro-screen */
            background-size: cover;
            background-position: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
            padding: 20px;
            box-sizing: border-box;
            overflow-y: auto; /* Cho phép cuộn nếu nội dung chính dài */
        }}
        
        /* Hiệu ứng Reveal đã kích hoạt */
        .reveal-active #intro-screen {{
            /* Áp dụng transform để ẩn lớp intro, lộ lớp content bên dưới */
            transform: translateY(-100%); 
        }}
        
        @media (max-width: 768px) {{
            #intro-text {{
                font-size: 8vw;
            }}
            /* Hình nền Mobile */
            #main-content {{
                background-image: url('data:image/jpeg;base64,{bg_mobile_base64}');
            }}
        }}

        @media (min-width: 769px) {{
            /* Hình nền PC */
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

    <div id="intro-screen">
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <video id="intro-video" muted playsinline></video>
    </div>
    
    <audio id="background-audio"></audio>

    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            const appBody = document.getElementById('app-body');
            const introScreen = document.getElementById('intro-screen');
            const video = document.getElementById('intro-video');
            const audio = document.getElementById('background-audio');
            const introText = document.getElementById('intro-text');
            const isMobile = window.innerWidth <= 768;

            // 1. Cấu hình nguồn Video
            if (isMobile) {{
                video.src = 'data:video/mp4;base64,{video_mobile_base64}';
            }} else {{
                video.src = 'data:video/mp4;base64,{video_pc_base64}';
            }}
            
            // 2. Cấu hình nguồn Audio
            audio.src = 'data:audio/mp3;base64,{audio_base64}';

            const playMedia = () => {{
                video.load();
                video.play().catch(e => console.log("Video playback failed:", e));
                
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

            // 3. Logic HIỆU ỨNG REVEAL khi video kết thúc
            video.onended = () => {{
                audio.pause(); 
                audio.currentTime = 0; 
                introText.style.opacity = 0;
                
                // Kích hoạt hiệu ứng Reveal: Thêm class 'reveal-active' vào body
                appBody.classList.add('reveal-active');
                
                // Tùy chọn: Xóa intro-screen sau khi chuyển cảnh hoàn tất (1s transition + 0.1s)
                setTimeout(() => {{
                    introScreen.style.display = 'none';
                }}, 1100); 
                
                console.log("Video intro đã kết thúc. Đang chuyển trang.");
            }};
        }});
    </script>
</body>
</html>
"""

# Hiển thị thành phần HTML (Dùng chiều cao tối thiểu)
st.components.v1.html(html_content, height=10, scrolling=False)
