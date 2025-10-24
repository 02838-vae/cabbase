import streamlit as st
import base64

# Cấu hình trang (tắt menu mặc định, thêm tiêu đề)
st.set_page_config(
    page_title="Khám phá cùng chúng tôi",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ẩn các thành phần mặc định của Streamlit (header/footer)
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# Hàm mã hóa file thành Base64 để nhúng vào HTML/JS
# Đây là cách tốt nhất để đảm bảo các file media (video, audio) được tải
# và phát đúng cách trong thành phần HTML nhúng.
def get_base64_encoded_file(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode("utf-8")

# Mã hóa các file media
video_pc_base64 = get_base64_encoded_file("airplane.mp4")
video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
audio_base64 = get_base64_encoded_file("plane_fly.mp3")


# --- Mã HTML/CSS/JavaScript cho Video Intro ---

# Sử dụng viewport width để phân biệt PC và Mobile
# PC: width > 768px (hoặc tùy bạn đặt)
# Mobile: width <= 768px

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        /* Đảm bảo toàn bộ viewport được sử dụng */
        body {{ margin: 0; padding: 0; overflow: hidden; }}
        
        /* CSS cho video fullscreen */
        #intro-video {{
            position: fixed;
            top: 0;
            left: 0;
            min-width: 100%;
            min-height: 100%;
            width: auto;
            height: auto;
            z-index: -100; /* Đặt video ở lớp dưới cùng */
        }}

        /* CSS cho dòng chữ cố định */
        #intro-text {{
            position: fixed;
            top: 5vh; /* Cách mép trên 5% chiều cao màn hình */
            width: 100%;
            text-align: center;
            color: white; /* Màu chữ */
            font-size: 3vw; /* Kích thước chữ dựa trên viewport width */
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7); /* Thêm bóng để dễ đọc */
            z-index: 100; /* Đặt chữ ở lớp trên cùng */
            pointer-events: none; /* Đảm bảo chữ không chắn các sự kiện click */
            opacity: 0; /* Ẩn chữ lúc đầu */
            transition: opacity 1s; /* Hiệu ứng chuyển đổi */
        }}
        
        /* Điều chỉnh kích thước chữ cho Mobile */
        @media (max-width: 768px) {{
            #intro-text {{
                font-size: 8vw; /* Kích thước lớn hơn cho mobile */
            }}
        }}
        
    </style>
</head>
<body>

    <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>

    <video id="intro-video" muted playsinline></video>
    
    <audio id="background-audio" loop></audio>

    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            const video = document.getElementById('intro-video');
            const audio = document.getElementById('background-audio');
            const introText = document.getElementById('intro-text');
            const isMobile = window.innerWidth <= 768; // Logic kiểm tra mobile/pc

            // 1. Cấu hình nguồn Video
            if (isMobile) {{
                video.src = 'data:video/mp4;base64,{video_mobile_base64}'; // Mobile video
            }} else {{
                video.src = 'data:video/mp4;base64,{video_pc_base64}';      // PC video
            }}
            
            // 2. Cấu hình nguồn Audio
            audio.src = 'data:audio/mp3;base64,{audio_base64}';

            // 3. Logic phát Video và Audio
            
            // Streamlit nhúng nội dung trong iframe, cần xử lý logic tự động phát
            // vì các trình duyệt (Chrome, Safari) yêu cầu tương tác người dùng
            // để phát âm thanh/video có âm thanh.
            
            // Do video không có âm thanh (muted), nó có thể tự động phát.
            // Âm thanh nền cần sự tương tác. Ta sẽ thử phát ngay lập tức, 
            // nhưng nếu thất bại (do chính sách trình duyệt), ta sẽ chờ tương tác.

            const playMedia = () => {{
                // Bật video và chờ nó tải
                video.load();
                video.play().catch(e => console.log("Video playback failed:", e));
                
                // Bật chữ khi video bắt đầu (hoặc sau một chút delay)
                setTimeout(() => {{ introText.style.opacity = 1; }}, 500);

                // Thử bật âm thanh (sẽ thất bại nếu không có tương tác)
                audio.volume = 0.5; // Giảm âm lượng một chút
                audio.play().catch(e => {{
                    console.log("Audio auto-play blocked. Waiting for user interaction.");
                    
                    // Nếu audio bị chặn, thêm thông báo yêu cầu tương tác
                    // (Tùy chọn: Trong Streamlit, bạn có thể xử lý này ở mã Python)
                    // Hoặc bạn có thể thêm một nút "Bắt đầu" trong HTML.
                    
                    // Thử phát lại audio khi người dùng tương tác với trang
                    document.body.addEventListener('click', () => {{
                        audio.play().catch(err => console.error("Audio playback error on click:", err));
                    }}, {{ once: true }});
                }});
            }};
            
            // Bắt đầu quá trình phát
            playMedia();

            // 4. Khi video kết thúc (Tùy chọn: Chuyển sang nội dung chính)
            video.onended = () => {{
                // video.style.display = 'none'; // Ẩn video
                // audio.pause(); // Dừng âm thanh
                // introText.style.opacity = 0; // Ẩn chữ

                // Tại đây, bạn có thể gửi một thông báo về Streamlit 
                // để hiển thị nội dung chính của trang.
                // Ví dụ: Streamlit.setComponentValue('video_ended', true);
            }};
        }});
    </script>
</body>
</html>
"""

# Hiển thị thành phần HTML với chiều cao tối đa (fullscreen)
# Sử dụng height=1000 để đảm bảo video chiếm đủ không gian ban đầu, 
# hoặc bạn có thể dùng CSS trong HTML để nó chiếm 100vh.
st.components.v1.html(html_content, height=1000, scrolling=False)


# --- Nội dung chính của trang (Phần này sẽ bị video che phủ lúc đầu) ---

# Thêm nội dung khác sau video intro. 
# Sau khi video kết thúc, bạn có thể dùng logic JS/HTML
# để ẩn video và cho phép người dùng thấy phần này.
st.markdown("""
<div style="padding: 20px; margin-top: 100vh; background-color: white;">
    <h2>Chào mừng đến với Nội dung Chính của Trang!</h2>
    <p>Đây là phần còn lại của trang web, hiện ra sau khi video intro kết thúc (hoặc sau khi người dùng cuộn xuống).</p>
</div>
""", unsafe_allow_html=True)
