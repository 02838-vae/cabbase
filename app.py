import streamlit as st
import base64

# Cấu hình trang như trước
st.set_page_config(
    page_title="Khám phá cùng chúng tôi",
    layout="wide",
    initial_sidebar_state="collapsed"
)

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
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
except FileNotFoundError as e:
    st.error(f"Lỗi: Không tìm thấy file media. Vui lòng kiểm tra lại đường dẫn: {e.filename}")
    st.stop()


# --- MÃ HTML/CSS/JavaScript ĐÃ SỬA LỖI FULLSCREEN VÀ AUDIO LOOP ---

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        /* SỬA LỖI 1: Đảm bảo iframe và body chiếm toàn bộ không gian */
        /* Đây là phần CSS trong iframe của Streamlit */
        html, body {{
            margin: 0; 
            padding: 0; 
            overflow: hidden; /* Quan trọng để tránh thanh cuộn */
            height: 100%; /* Đảm bảo body chiếm 100% chiều cao */
            width: 100%;  /* Đảm bảo body chiếm 100% chiều rộng */
        }}
        
        /* CSS cho video fullscreen */
        #intro-video {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;   /* Chiếm 100% chiều rộng viewport */
            height: 100vh;  /* Chiếm 100% chiều cao viewport */
            object-fit: cover; /* Quan trọng: Đảm bảo video che phủ toàn bộ, cắt bớt nếu cần */
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
        
        @media (max-width: 768px) {{
            #intro-text {{
                font-size: 8vw;
            }}
        }}
        
    </style>
</head>
<body>

    <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    
    <video id="intro-video" muted playsinline></video>
    
    <audio id="background-audio"></audio>

    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            const video = document.getElementById('intro-video');
            const audio = document.getElementById('background-audio');
            const introText = document.getElementById('intro-text');
            const isMobile = window.innerWidth <= 768;

            // Cấu hình nguồn Video
            if (isMobile) {{
                video.src = 'data:video/mp4;base64,{video_mobile_base64}';
            }} else {{
                video.src = 'data:video/mp4;base64,{video_pc_base64}';
            }}
            
            // Cấu hình nguồn Audio
            audio.src = 'data:audio/mp3;base64,{audio_base64}';

            const playMedia = () => {{
                video.load();
                video.play().catch(e => console.log("Video playback failed:", e));
                
                setTimeout(() => {{ introText.style.opacity = 1; }}, 500);

                // Thử bật âm thanh (sẽ thất bại nếu không có tương tác)
                audio.volume = 0.5; 
                audio.play().catch(e => {{
                    console.log("Audio auto-play blocked. Waiting for user interaction.");
                    
                    // Thử phát lại audio khi người dùng tương tác với trang
                    document.body.addEventListener('click', () => {{
                        audio.play().catch(err => console.error("Audio playback error on click:", err));
                    }}, {{ once: true }});
                }});
            }};
            
            playMedia();

            // SỬA LỖI 3: Dừng âm thanh khi video kết thúc
            video.onended = () => {{
                video.style.opacity = 0; // Tùy chọn: Làm mờ hoặc ẩn video
                audio.pause(); // Dừng âm thanh
                audio.currentTime = 0; // Tua về đầu (tùy chọn)
                introText.style.opacity = 0; // Ẩn chữ
                
                // Tùy chọn: Gửi tin nhắn đến Streamlit để hiển thị nội dung chính
                // Streamlit.setComponentValue('video_ended', true); 
                
                console.log("Video intro đã kết thúc. Âm thanh đã dừng.");
            }};
        }});
    </script>
</body>
</html>
"""

# Hiển thị thành phần HTML
# Đặt height=1000 là đủ vì logic fullscreen được xử lý trong CSS (100vh)
st.components.v1.html(html_content, height=1000, scrolling=False)


# Nội dung chính của trang (giữ nguyên, nằm phía dưới lớp video)
st.markdown("""
<div style="padding: 20px; margin-top: 100vh; background-color: white;">
    <h2>Chào mừng đến với Nội dung Chính của Trang!</h2>
    <p>Đây là phần còn lại của trang web.</p>
</div>
""", unsafe_allow_html=True)
