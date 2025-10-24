import streamlit as st
import base64

# --- CẤU HÌNH BAN ĐẦU ---
st.set_page_config(
    page_title="Khám phá cùng chúng tôi",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Khởi tạo session state (Không dùng trong logic chính, chỉ để giữ cấu trúc)
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
        # Tái raise lỗi để hàm try/except bên ngoài xử lý
        raise FileNotFoundError(f"Lỗi: Không tìm thấy file media. Vui lòng kiểm tra lại đường dẫn: {e.filename}")


# Mã hóa các file media
try:
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    # Đã đổi tên file ảnh nền PC thành cabbase.jpg theo yêu cầu
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg")
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
except FileNotFoundError as e:
    st.error(e)
    st.stop()


# --- CSS ĐỂ ÉP STREAMLIT MAIN CONTAINER & IFRAME FULLSCREEN/ẨN IFRAME ---
# SỬA LỖI F-STRING: NHÂN ĐÔI DẤU NGOẶC NHỌN {} TRONG KHỐI CSS
hide_streamlit_style = f"""
<style>
/* Ẩn các thành phần mặc định của Streamlit */
#MainMenu, footer, header {{visibility: hidden;}}

/* Đảm bảo Main Content Container chiếm toàn bộ không gian và không có padding */
.main {{
    padding: 0;
    margin: 0;
}}

/* Đảm bảo khu vực nội dung được căn chỉnh sát lề */
div.block-container {{
    padding: 0;
    margin: 0;
    max-width: 100% !important;
}}

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

/* Class để ẩn iframe (được thêm bằng JS) */
.video-finished iframe:first-of-type {{
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
    height: 1px !important; 
}}

/* Định nghĩa nền full-screen cho main content */
.stApp {{
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
}}

/* CSS cho hiệu ứng Reveal */
.reveal-grid {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    display: grid;
    /* Tùy chỉnh số lượng ô vuông */
    grid-template-columns: repeat(20, 1fr); 
    grid-template-rows: repeat(12, 1fr);
    z-index: 500; 
    pointer-events: none; 
}}

.grid-cell {{
    /* Áp dụng nền từ body chính để tính toán vị trí, nhưng ở đây ta chỉ cần màu trắng/nền chung */
    background-color: white; /* Ban đầu là màu trắng/màu che phủ */
    opacity: 1;
    transition: opacity 0.5s ease-out;
}}

/* Class được thêm vào .stApp sau khi video kết thúc */
.main-content-revealed {{
    /* Đặt nền cho toàn bộ ứng dụng */
    background-image: var(--main-bg-url-pc);
    background-size: cover;
    background-position: center;
    background-attachment: fixed; /* Giữ nền cố định khi cuộn */
}}

/* Điều chỉnh cho Mobile */
@media (max-width: 768px) {{
    .main-content-revealed {{
        background-image: var(--main-bg-url-mobile);
    }}
    .reveal-grid {{
        grid-template-columns: repeat(10, 1fr);
        grid-template-rows: repeat(20, 1fr);
    }}
}}
</style>
"""

# Thêm CSS vào trang chính
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- MÃ HTML/CSS/JavaScript IFRAME CHO VIDEO INTRO ---

# JavaScript để thông báo cho Streamlit khi video kết thúc
# SỬA LỖI F-STRING: NHÂN ĐÔI DẤU NGOẶC NHỌN {} TRONG KHỐI JAVASCRIPT
js_callback = f"""
<script>
    function sendBackToStreamlit() {{
        // **BƯỚC 1: Kích hoạt nền và ẩn video**
        window.parent.document.querySelector('.stApp').classList.add('video-finished', 'main-content-revealed');
        
        // **BƯỚC 2: Kích hoạt Hiệu ứng Reveal**
        initRevealEffect();
    }}
    
    function initRevealEffect() {{
        const revealGrid = window.parent.document.querySelector('.reveal-grid');
        if (!revealGrid) return;

        const cells = revealGrid.querySelectorAll('.grid-cell');
        
        // Tạo một mảng ngẫu nhiên các ô
        const shuffledCells = Array.from(cells).sort(() => Math.random() - 0.5);

        shuffledCells.forEach((cell, index) => {{
            setTimeout(() => {{
                // Thay đổi background-color của ô vuông thành màu nền của Streamlit
                // Hoặc đơn giản là ẩn nó đi
                cell.style.opacity = 0; 
            }}, index * 10); // Khoảng thời gian giữa các ô (10ms)
        }});
        
        // Sau khi hiệu ứng kết thúc, loại bỏ lưới
        setTimeout(() => {{
             revealGrid.remove();
        }}, shuffledCells.length * 10 + 1000); // Đợi 1 giây sau khi ô cuối cùng ẩn
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
            audio.loop = true; // Lặp lại âm thanh nếu cần
            audio.play().catch(e => {{
                // Cần tương tác người dùng để Play Audio/Video trên nhiều trình duyệt
                document.body.addEventListener('click', () => {{
                    audio.play().catch(err => console.error("Audio playback error on click:", err));
                }}, {{ once: true }});
            }});
        }};
            
        playMedia();
        
        // Event khi video kết thúc
        video.onended = () => {{
            video.style.opacity = 0;
            audio.pause();
            audio.currentTime = 0;
            introText.style.opacity = 0;
            
            sendBackToStreamlit(); 
        }};

        // Cần đảm bảo video luôn sẵn sàng nếu trình duyệt chặn autoplay
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
        /* SỬA LỖI F-STRING */
        html, body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            height: 100vh;
            width: 100vw;
        }}
        
        #intro-video {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            z-index: -100;
            transition: opacity 1s; 
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

    {js_callback}
</body>
</html>
"""

# Hiển thị thành phần HTML (video)
st.components.v1.html(html_content_modified, height=10, scrolling=False)


# --- HIỆU ỨNG REVEAL VÀ NỘI DUNG CHÍNH ---

# Tạo Lưới Reveal (20x12 = 240 ô)
grid_cells_html = ""
for i in range(240): 
    grid_cells_html += f'<div class="grid-cell"></div>'

reveal_grid_html = f"""
<div class="reveal-grid">
    {grid_cells_html}
</div>
"""
# Lưới này phải được đặt trước nội dung chính và Streamlit sẽ hiển thị nó
# Nó bị ẩn đi bằng CSS/JS sau khi video kết thúc.
st.markdown(reveal_grid_html, unsafe_allow_html=True)
    

# Nội dung chính của trang (Phần này sẽ hiện ra sau khi lưới bị ẩn)
st.markdown("""
<div style="padding: 20px; color: black; position: relative; z-index: 10;">
    <h1>Chào mừng đến với Nội dung Chính của Trang!</h1>
    <p>Nền của trang đã được thay thế bằng hình ảnh **cabbase.jpg** (hoặc **mobile.jpg**).</p>
    <p>Hiệu ứng ô vuông đã lật mở để bạn nhìn thấy nội dung này.</p>
    <p>Bạn có thể cuộn xuống và tương tác với các thành phần Streamlit khác.</p>
</div>
""", unsafe_allow_html=True)

st.slider("Thanh trượt Streamlit", 0, 100)
st.button("Nút ấn")
