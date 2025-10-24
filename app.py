import streamlit as st
import base64

# Cấu hình trang (Tắt menu mặc định)
st.set_page_config(
    page_title="Khám phá cùng chúng tôi",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS ĐỂ ÉP STREAMLIT MAIN CONTAINER VÀ IFRAME FULLSCREEN ---
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
    /* Streamlit Main Content sẽ là nền cho trang chính */
    background-color: transparent; /* Quan trọng để nhìn xuyên qua content wrapper */
    transition: opacity 1s; /* Thêm transition cho độ mượt khi fade-in */
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

/* Class để ẩn lớp phủ video sau khi chuyển tiếp */
.stApp.fade-out-overlay > iframe {
    /* Quan trọng: Dùng visibility thay vì display: none; để tránh giật */
    visibility: hidden; 
    opacity: 0;
    transition: visibility 0s 1.5s, opacity 1.5s ease-in-out; /* Ẩn sau khi transition kết thúc */
}

/* Class để làm hiện nội dung chính của trang */
.stApp.fade-out-overlay .main {
    opacity: 1; /* Hiển thị nội dung chính */
}

/* Ẩn nội dung chính ban đầu */
.stApp .main {
    opacity: 0;
}


/* --- CSS CHO NỘI DUNG CHÍNH (NỀN CỐ ĐỊNH) --- */
/* Thêm nền cố định cho toàn bộ ứng dụng Streamlit */
.stApp {
    /* Đặt nền mặc định cho PC, sẽ bị video che phủ lúc đầu */
    background-image: url('data:image/jpeg;base64,{get_base64_encoded_file("cabbage.jpg")}') !important;
    background-size: cover !important;
    background-position: center center !important;
    background-attachment: fixed !important; /* Quan trọng: Đảm bảo nền cố định */
}

@media (max-width: 768px) {
    .stApp {
        /* Thay thế nền cho Mobile */
        background-image: url('data:image/jpeg;base64,{get_base64_encoded_file("mobile.jpg")}') !important;
    }
}

</style>
"""

def get_base64_encoded_file(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    except FileNotFoundError:
        return "" # Trả về chuỗi rỗng nếu không tìm thấy, lỗi sẽ được xử lý ở phần st.error

# Mã hóa các file media
try:
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    
    # Mã hóa hình nền để nhúng vào CSS (Quan trọng: Phải gọi ở đây)
    cabbage_base64 = get_base64_encoded_file("cabbage.jpg")
    mobile_bg_base64 = get_base64_encoded_file("mobile.jpg")
    
except FileNotFoundError as e:
    st.error(f"Lỗi: Không tìm thấy file media hoặc hình nền. Vui lòng kiểm tra lại đường dẫn: {e.filename}")
    st.stop()

# Áp dụng CSS cho trang Streamlit chính (Đã bao gồm hình nền)
# Phải dùng f-string vì cần nhúng base64 của ảnh nền vào CSS
st.markdown(hide_streamlit_style.format(
    get_base64_encoded_file=get_base64_encoded_file
), unsafe_allow_html=True)


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
            background: black; /* Đảm bảo nền đen nếu video load chậm */
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
            /* Thêm transition cho hiệu ứng phóng to mượt mà */
            transition: transform 1.5s cubic-bezier(0.5, 0.0, 0.5, 1.0), opacity 1s ease-out;
        }}
        
        /* Class khi video kết thúc (Hiệu ứng Codepen) */
        #intro-video.fadeout {{
            transform: scale(1.1); /* Phóng to 10% */
            opacity: 0; /* Làm mờ */
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

            // --- LOGIC CHUYỂN TRANG MỚI ---
            video.onended = () => {{
                // 1. Áp dụng hiệu ứng phóng to/mờ cho video
                video.classList.add('fadeout');
                
                // 2. Tắt nhạc
                audio.pause(); 
                audio.currentTime = 0; 
                introText.style.opacity = 0;
                
                // 3. Kích hoạt chuyển trang chính (Áp dụng class vào body/root của Streamlit)
                // Phải gửi thông điệp cho Streamlit parent window
                parent.document.querySelector('.stApp').classList.add('fade-out-overlay');
            }};
        }});
    </script>
</body>
</html>
"""

# Hiển thị thành phần HTML (Dùng chiều cao tối thiểu để component tồn tại)
st.components.v1.html(html_content, height=10, scrolling=False)


# Nội dung chính của trang (Phải được đặt ở đây)
# Dùng div có margin-top lớn để nội dung chính nằm dưới lớp video overlay ban đầu
st.markdown("""
<div style="
    padding: 20px; 
    margin-top: 100vh; /* Đẩy nội dung xuống dưới 100% viewport */
    background-color: rgba(255, 255, 255, 0.8); /* Nền hơi trong suốt để nhìn thấy ảnh nền */
    position: relative; 
    z-index: 10; /* Đảm bảo nội dung nằm trên lớp ảnh nền tĩnh */
    min-height: 100vh; /* Đảm bảo trang chính có nội dung cuộn được */
">
    <h1 style="color: black;">Chào mừng đến với Nội dung Chính của Trang!</h1>
    <p style="color: black;">Đây là phần còn lại của trang web, hiện ra sau khi video kết thúc.</p>
    <br>
    <p style="color: black;">Bạn có thể kéo xuống để xem nội dung khác.</p>
    <div style="height: 1000px;"></div> <p style="color: black;">Kết thúc trang.</p>
</div>
""", unsafe_allow_html=True)
