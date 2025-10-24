import streamlit as st
import base64

# Cấu hình trang (Tắt menu mặc định)
st.set_page_config(
    page_title="Khám phá cùng chúng tôi",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- SỬA LỖI 1: CSS ĐỂ ÉP STREAMLIT MAIN CONTAINER VÀ IFRAME FULLSCREEN ---
# Áp dụng CSS cho trang Streamlit chính
hide_streamlit_style = """
<style>
/* Ẩn các thành phần mặc định của Streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Đảm bảo Main Content Container chiếm toàn bộ không gian */
.main {
    padding: 0; /* Xóa padding mặc định */
    margin: 0;
}

/* Đảm bảo khu vực nội dung được căn chỉnh sát lề */
div.block-container {
    padding: 0;
    margin: 0;
    max-width: 100% !important;
}

/* Ép iframe của component chiếm toàn bộ chiều cao/rộng */
iframe {
    width: 100vw !important;
    height: 100vh !important;
    position: fixed; /* Đặt cố định để chiếm toàn bộ viewport */
    top: 0;
    left: 0;
    z-index: 1000; /* Đảm bảo nó che phủ mọi thứ */
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def get_base64_encoded_file(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode("utf-8")

# Mã hóa các file media (Giữ nguyên)
try:
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
except FileNotFoundError as e:
    st.error(f"Lỗi: Không tìm thấy file media. Vui lòng kiểm tra lại đường dẫn: {e.filename}")
    st.stop()


# --- MÃ HTML/CSS/JavaScript ĐÃ TỐI ƯU HÓA FULLSCREEN TRONG IFRAME ---

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        /* SỬA LỖI 2: CSS TRONG IFRAME */
        /* Đảm bảo html và body trong iframe chiếm 100% viewport */
        html, body {{
            margin: 0; 
            padding: 0; 
            overflow: hidden; 
            height: 100vh; 
            width: 100vw;
        }}
        
        /* CSS cho video fullscreen */
        #intro-video {{
            position: absolute; /* Dùng absolute vì body đã là 100vh/100vw */
            top: 0;
            left: 0;
            width: 100%;   /* Chiếm 100% chiều rộng của body (100vw) */
            height: 100%;  /* Chiếm 100% chiều cao của body (100vh) */
            object-fit: cover; /* Đảm bảo video che phủ toàn bộ, không bị giãn méo */
            z-index: -100;
        }}

        /* CSS cho dòng chữ cố định (Giữ nguyên) */
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
            }};
        }});
    </script>
</body>
</html>
"""

# Hiển thị thành phần HTML (Dùng chiều cao tối thiểu để component tồn tại)
# Quan trọng: Logic fullscreen được xử lý hoàn toàn bằng CSS và JS.
st.components.v1.html(html_content, height=10, scrolling=False)


# Nội dung chính của trang (Sử dụng CSS để đảm bảo nó nằm dưới lớp video/iframe)
st.markdown("""
<div style="padding: 20px; margin-top: 100vh; background-color: white; position: relative; z-index: 1;">
    <h2>Chào mừng đến với Nội dung Chính của Trang!</h2>
    <p>Đây là phần còn lại của trang web.</p>
</div>
""", unsafe_allow_html=True)
