import streamlit as st
import base64

# --- CẤU HÌNH BAN ĐẦU ---
st.set_page_config(
    page_title="Khám phá cùng chúng tôi",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Khởi tạo session state để kiểm soát trạng thái video
if 'video_ended' not in st.session_state:
    st.session_state.video_ended = False

# --- CÁC HÀM TIỆN ÍCH ---

def get_base64_encoded_file(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode("utf-8")

# Mã hóa các file media
try:
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg")  # Tên file nền PC
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg") # Tên file nền Mobile
except FileNotFoundError as e:
    st.error(f"Lỗi: Không tìm thấy file media. Vui lòng kiểm tra lại đường dẫn: {e.filename}")
    st.stop()


# --- CSS ĐỂ ÉP STREAMLIT MAIN CONTAINER & IFRAME FULLSCREEN/ẨN IFRAME ---
# CSS cho trang Streamlit chính
hide_streamlit_style = """
<style>
/* Ẩn các thành phần mặc định của Streamlit */
#MainMenu, footer, header {visibility: hidden;}

/* Đảm bảo Main Content Container chiếm toàn bộ không gian và không có padding */
.main {
    padding: 0;
    margin: 0;
}

/* Đảm bảo khu vực nội dung được căn chỉnh sát lề */
div.block-container {
    padding: 0;
    margin: 0;
    max-width: 100% !important;
}

/* Ẩn iframe khi st.session_state.video_ended là True */
/* Giả sử component được đặt đầu tiên, ta tìm iframe đầu tiên */
iframe:first-of-type {
    transition: opacity 1s ease-out, visibility 1s ease-out;
    opacity: 1;
    visibility: visible;
    width: 100vw !important;
    height: 100vh !important;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1000;
}

/* Class để ẩn iframe */
.video-finished iframe:first-of-type {
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
    height: 1px !important; /* Thay đổi kích thước để giải phóng không gian */
}

/* Định nghĩa nền full-screen cho main content */
.stApp {
    /* Sử dụng biến CSS để lưu trữ URL nền */
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
}

/* CSS cho hiệu ứng Reveal */
.reveal-grid {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    display: grid;
    /* Tùy chỉnh số lượng ô vuông */
    grid-template-columns: repeat(20, 1fr); 
    grid-template-rows: repeat(12, 1fr);
    z-index: 500; /* Dưới iframe (1000), trên nội dung chính */
    pointer-events: none; /* Cho phép tương tác với nội dung bên dưới */
}

.grid-cell {
    background-size: cover;
    background-position: center;
    opacity: 1;
    transition: opacity 0.5s ease-out;
}

/* Class để kích hoạt ẩn/reveal */
.main-content-revealed {
    /* Đặt nền cho toàn bộ ứng dụng */
    background-image: var(--main-bg-url-pc);
    background-size: cover;
    background-position: center;
    transition: background-image 0s; /* Không chuyển đổi nền */
}

/* Điều chỉnh cho Mobile */
@media (max-width: 768px) {
    .main-content-revealed {
        background-image: var(--main-bg-url-mobile);
    }
    .reveal-grid {
        grid-template-columns: repeat(10, 1fr);
        grid-template-rows: repeat(20, 1fr);
    }
}
</style>
"""

# Thêm class để ẩn iframe nếu video đã kết thúc
if st.session_state.video_ended:
    st.markdown(f'<div class="video-finished">{hide_streamlit_style}</div>', unsafe_allow_html=True)
else:
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- MÃ HTML/CSS/JavaScript IFRAME CHO VIDEO INTRO ---

# JavaScript để thông báo cho Streamlit khi video kết thúc
js_callback = f"""
<script>
    function sendBackToStreamlit() {{
        // Gửi tín hiệu trở lại Streamlit
        var xhr = new XMLHttpRequest();
        // Giả sử Streamlit đang chạy trên cùng domain và cổng
        // Phương pháp này không trực tiếp, nhưng thường dùng trong môi trường tùy chỉnh
        // Cách tốt nhất là dùng component riêng, nhưng ta dùng cách 'refresh' bằng session_state
        // Để đơn giản, ta sẽ chỉ dùng logic của video_ended trong JS để áp dụng CSS
        console.log("Video Ended. Signaling Streamlit.");
        // Gửi post message, Streamlit không lắng nghe mặc định
        // Chúng ta sẽ dựa vào việc áp dụng class 'video-finished' trên element Streamlit chính
        // và reload trang (hoặc dùng Custom Streamlit Component)
        
        // Vì Streamlit không có API callback đơn giản cho JS trong st.html,
        // ta sẽ reload trang để kích hoạt st.session_state.video_ended = True 
        // Đây là cách "cồng kềnh" nhất, nhưng hoạt động.
        // Cần một nút ấn hoặc sử dụng window.location.reload() sau một độ trễ
        // TỐT HƠN: Thay đổi nội dung của một div và sau đó thay đổi session_state bằng form
        
        // GIẢI PHÁP TỐT NHẤT CHO TRƯỜNG HỢP NÀY:
        // Cập nhật lại HTML với một form, kích hoạt submit để thay đổi session_state
        // HOẶC: Chấp nhận rằng chỉ có CSS thay đổi sau khi video kết thúc.
        
        // **ÁP DỤNG CSS:** Thêm class vào body chính của Streamlit
        window.parent.document.querySelector('.stApp').classList.add('video-finished', 'main-content-revealed');
        
        // Kích hoạt Hiệu ứng Reveal
        initRevealEffect();
    }
    
    function initRevealEffect() {{
        const revealGrid = window.parent.document.querySelector('.reveal-grid');
        if (!revealGrid) return;

        const cells = revealGrid.querySelectorAll('.grid-cell');
        
        // Hiệu ứng lật mở ngẫu nhiên
        const shuffledCells = Array.from(cells).sort(() => Math.random() - 0.5);

        shuffledCells.forEach((cell, index) => {{
            setTimeout(() => {{
                cell.style.opacity = 0; // Ẩn ô vuông
            }}, index * 20); // Khoảng thời gian giữa các ô, vd: 20ms
        }});
        
        // Sau khi hiệu ứng kết thúc, loại bỏ lưới
        setTimeout(() => {{
             revealGrid.remove();
        }}, shuffledCells.length * 20 + 1000); // 1 giây sau khi ô cuối cùng ẩn
    }

    document.addEventListener("DOMContentLoaded", function() {{
        const video = document.getElementById('intro-video');
        const audio = document.getElementById('background-audio');
        // ... (phần code video playback giữ nguyên) ...

        video.onended = () => {{
            video.style.opacity = 0;
            audio.pause();
            audio.currentTime = 0;
            document.getElementById('intro-text').style.opacity = 0;
            
            // **THAY ĐỔI LỚN:** GỌI HÀM GỬI TÍN HIỆU/ÁP DỤNG CSS TỪ PARENT FRAME
            sendBackToStreamlit(); 
        }};
        
        // (Phần setup video/audio/playMedia giữ nguyên)
        // ...
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
        
        // Cần đảm bảo video luôn sẵn sàng nếu trình duyệt chặn autoplay
        document.body.addEventListener('click', () => {{
             video.play().catch(e => {{}});
             audio.play().catch(e => {{}});
        }}, {{ once: true }});
    }});
</script>
"""
# Thay thế phần <script> trong html_content
html_content_modified = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        /* SỬA LỖI 2: CSS TRONG IFRAME */
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
            transition: opacity 1s; /* Thêm transition để video mờ dần */
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

    {js_callback}
</body>
</html>
"""

# Hiển thị thành phần HTML (video)
st.components.v1.html(html_content_modified, height=10, scrolling=False)


# --- HIỆU ỨNG REVEAL VÀ NỘI DUNG CHÍNH ---

# Hiệu ứng Reveal Grid: Tạo các ô vuông che phủ
# Chúng ta sẽ sử dụng Streamlit markdown để inject HTML/CSS cho lưới
if not st.session_state.video_ended:
    # Lấy thông tin nền thích hợp cho từng ô (Data URI là quá dài, ta dùng CSS background-image
    # đã khai báo trong hide_streamlit_style)
    
    # Tạo số lượng ô phù hợp (20x12 = 240 ô)
    grid_cells_html = ""
    for i in range(240): 
        # Cần tính toán background-position cho từng ô để tạo thành hình ảnh lớn
        # Cần JavaScript phức tạp để tính toán chính xác trong từng ô
        # Đơn giản hóa: Dùng cùng 1 ô, và JS sẽ thay đổi opacity
        grid_cells_html += f'<div class="grid-cell"></div>'

    # Tạo Lưới
    reveal_grid_html = f"""
    <div class="reveal-grid">
        {grid_cells_html}
    </div>
    """
    st.markdown(reveal_grid_html, unsafe_allow_html=True)
    
    # Do st.session_state không thay đổi khi video kết thúc (vì nó nằm trong iframe JS),
    # ta cần một cơ chế khác. Việc dùng JS để thêm class 'main-content-revealed' 
    # và 'video-finished' vào body chính là cách giải quyết tốt nhất.

# Nội dung chính của trang
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
