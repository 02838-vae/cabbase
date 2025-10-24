import streamlit as st
import base64

# --- HÀM HỖ TRỢ ---
def get_base64_encoded_file(file_path):
    """Mã hóa file thành chuỗi base64."""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    except FileNotFoundError:
        return "" 

# --- CẤU HÌNH VÀ MÃ HÓA MEDIA ---

# Cấu hình trang (Tắt menu mặc định)
st.set_page_config(
    page_title="Khám phá cùng chúng tôi",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Mã hóa các file media và hình nền
try:
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    
    # Mã hóa hình nền
    cabbage_base64 = get_base64_encoded_file("cabbase.jpg")
    mobile_bg_base64 = get_base64_encoded_file("mobile.jpg")
    
    # Kiểm tra xem có đủ file cần thiết không
    if not (video_pc_base64 and video_mobile_base64 and audio_base64 and cabbage_base64 and mobile_bg_base64):
        missing_files = []
        if not video_pc_base64: missing_files.append("airplane.mp4")
        if not video_mobile_base64: missing_files.append("mobile.mp4")
        if not audio_base64: missing_files.append("plane_fly.mp3")
        if not cabbage_base64: missing_files.append("cabbase.jpg")
        if not mobile_bg_base64: missing_files.append("mobile.jpg")
        st.error(f"Lỗi: Không tìm thấy (hoặc file rỗng) các file sau: {', '.join(missing_files)}. Vui lòng kiểm tra lại đường dẫn.")
        st.stop()
        
except Exception as e:
    st.error(f"Lỗi hệ thống khi đọc file: {e}")
    st.stop()


# --- CSS CHUNG CHO STREAMLIT (NHÚNG ẢNH NỀN VÀ HIỆU ỨNG CHUYỂN TRANG) ---

# SỬ DỤNG F-STRING ĐỂ NHÚNG BASE64 CỦA ẢNH NỀN VÀO CSS
hide_streamlit_style = f"""
<style>
/* Ẩn các thành phần mặc định của Streamlit */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}

/* Đảm bảo Main Content Container chiếm toàn bộ không gian */
.main {{
    padding: 0;
    margin: 0;
    background-color: transparent;
    transition: opacity 1s ease-in; /* Transition cho nội dung chính */
}}

/* Đảm bảo khu vực nội dung được căn chỉnh sát lề */
div.block-container {{
    padding: 0;
    margin: 0;
    max-width: 100% !important;
}}

/* Ép iframe của component chiếm toàn bộ chiều cao/rộng */
iframe {{
    width: 100vw !important;
    height: 100vh !important;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1000; /* Đảm bảo nó che phủ mọi thứ */
}}

/* Class để ẩn lớp phủ video sau khi chuyển tiếp */
.stApp.fade-out-overlay > iframe {{
    visibility: hidden; 
    opacity: 0;
    transition: visibility 0s 1.5s, opacity 1.5s ease-in-out; 
}}

/* Class để làm hiện nội dung chính của trang */
.stApp.fade-out-overlay .main {{
    opacity: 1; /* Hiển thị nội dung chính */
}}

/* Ẩn nội dung chính ban đầu */
.stApp .main {{
    opacity: 0;
}}


/* --- CSS CHO NỘI DUNG CHÍNH (NỀN CỐ ĐỊNH) --- */
.stApp {{
    /* Đặt nền mặc định cho PC */
    background-image: url('data:image/jpeg;base64,{cabbage_base64}') !important; 
    background-size: cover !important;
    background-position: center center !important;
    background-attachment: fixed !important; /* Quan trọng */
}}

@media (max-width: 768px) {{
    .stApp {{
        /* Thay thế nền cho Mobile */
        background-image: url('data:image/jpeg;base64,{mobile_bg_base64}') !important;
    }}
}}

</style>
"""
# Áp dụng CSS cho trang Streamlit chính
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- MÃ HTML/CSS/JavaScript CHO VIDEO INTRO (TRONG IFRAME) ---

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        /* CSS TRONG IFRAME */
        html, body {{
            margin: 0; 
            padding: 0; 
            overflow: hidden; 
            height: 100vh; 
            width: 100vw;
            background: black;
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
            transition: transform 1.5s cubic-bezier(0.5, 0.0, 0.5, 1.0), opacity 1.5s ease-out;
        }}
        
        /* Hiệu ứng phóng to và làm mờ */
        #intro-video.fadeout {{
            transform: scale(1.1);
            opacity: 0;
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

        /* --- CSS MỚI: NÚT BẮT ĐẦU --- */
        #start-button {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            z-index: 1000; 
            opacity: 1;
            transition: opacity 0.5s ease-out;
        }}
        #start-button.hidden {{
            opacity: 0;
            pointer-events: none;
        }}
        #start-button h1 {{
            font-size: 5vw;
            margin-bottom: 20px;
        }}
        #start-button button {{
            padding: 15px 30px;
            font-size: 1.5vw;
            background-color: #33aaff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        #start-button button:hover {{
            background-color: #0077cc;
        }}
        @media (max-width: 768px) {{
            #start-button h1 {{ font-size: 10vw; }}
            #start-button button {{ font-size: 4vw; }}
        }}
        
    </style>
</head>
<body>

    <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    
    <video id="intro-video" muted playsinline></video>
    
    <audio id="background-audio"></audio>

    <div id="start-button">
        <h1>Sẵn sàng Khám phá?</h1>
        <button id="start-media">BẮT ĐẦU</button>
    </div>

    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            const video = document.getElementById('intro-video');
            const audio = document.getElementById('background-audio');
            const introText = document.getElementById('intro-text');
            const startButton = document.getElementById('start-button');
            const startMediaButton = document.getElementById('start-media');
            const isMobile = window.innerWidth <= 768;

            // Thiết lập nguồn video/audio
            if (isMobile) {{
                video.src = 'data:video/mp4;base64,{video_mobile_base64}';
            }} else {{
                video.src = 'data:video/mp4;base64,{video_pc_base64}';
            }}
            audio.src = 'data:audio/mp3;base64,{audio_base64}';
            
            // --- LOGIC MỚI: CHỜ CLICK TỪ NGƯỜI DÙNG ---
            startMediaButton.addEventListener('click', () => {{
                // Tương tác người dùng đã xảy ra, giờ có thể play
                video.load();
                video.play().then(() => {{
                    // Video đang chạy
                    startButton.classList.add('hidden');
                    setTimeout(() => {{ introText.style.opacity = 1; }}, 500);
                    
                    audio.volume = 0.5;
                    audio.play().catch(e => console.error("Audio playback failed after user interaction:", e));

                }}).catch(e => {{
                    console.error("Video playback failed after user click:", e);
                    startButton.classList.add('hidden');
                    setTimeout(() => {{ introText.style.opacity = 1; }}, 500);
                }});
            }}, {{ once: true }});

            // --- LOGIC CHUYỂN TRANG KHI VIDEO KẾT THÚC ---
            video.onended = () => {{
                // 1. Áp dụng hiệu ứng phóng to/mờ cho video
                video.classList.add('fadeout');
                
                // 2. Tắt nhạc
                audio.pause(); 
                audio.currentTime = 0; 
                introText.style.opacity = 0;
                
                // 3. Kích hoạt chuyển trang chính trong Streamlit parent window
                parent.document.querySelector('.stApp').classList.add('fade-out-overlay');
            }};
        }});
    </script>
</body>
</html>
"""

# Hiển thị thành phần HTML
st.components.v1.html(html_content, height=10, scrolling=False)


# --- NỘI DUNG CHÍNH CỦA TRANG (HIỆN RA SAU HIỆU ỨNG) ---
st.markdown("""
<div style="
    padding: 20px; 
    margin-top: 100vh; /* Đẩy nội dung xuống dưới lớp video overlay */
    background-color: rgba(255, 255, 255, 0.8); /* Nền hơi trong suốt để nhìn thấy ảnh nền cố định */
    position: relative; 
    z-index: 10;
    min-height: 100vh; /* Đảm bảo trang chính có chiều cao tối thiểu */
">
    <h1 style="color: black;">👋 Chào mừng đến với Trang Chính!</h1>
    <p style="color: black;">Hiệu ứng chuyển trang mượt mà đã hoàn tất.</p>
    <p style="color: black;">Đây là nội dung chính của trang web. Ảnh nền là **cabbase.jpg** (hoặc mobile.jpg) cố định.</p>
    
    <div style="
        margin: 50px 0;
        padding: 20px;
        background-color: rgba(0, 0, 0, 0.1);
        border-radius: 10px;
        height: 800px; 
        display: flex;
        align-items: center;
        justify-content: center;
    ">
        <h3 style="color: black;">Cuộn xuống để xem thêm</h3>
    </div>
    
    <p style="color: black; text-align: center;">--- HẾT NỘI DUNG ---</p>
</div>
""", unsafe_allow_html=True)
