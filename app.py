import streamlit as st
import base64

# --- CẤU HÌNH BAN ĐẦU ---
st.set_page_config(
    page_title="Tổ Bảo Dưỡng Số 1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Khởi tạo session state
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
        raise FileNotFoundError(f"Lỗi: Không tìm thấy file media. Vui lòng kiểm tra lại đường dẫn: {e.filename}")


# Mã hóa các file media
try:
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
except FileNotFoundError as e:
    st.error(e)
    st.stop()


# --- PHẦN 1: NHÚNG FONT BẰNG THẺ LINK TRỰC TIẾP VÀO BODY ---
font_links = """
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
"""
st.markdown(font_links, unsafe_allow_html=True)


# --- PHẦN 2: CSS CHÍNH (STREAMLIT APP) ---
hide_streamlit_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sacramento&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');

/* Ẩn các thành phần mặc định của Streamlit */
#MainMenu, footer, header {{visibility: hidden;}}

.main {{
    padding: 0;
    margin: 0;
}}

div.block-container {{
    padding: 0;
    margin: 0;
    max-width: 100% !important;
}}

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

.video-finished iframe:first-of-type {{
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
    height: 1px !important; 
}}

.stApp {{
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
}}

.reveal-grid {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    display: grid;
    grid-template-columns: repeat(20, 1fr); 
    grid-template-rows: repeat(12, 1fr);
    z-index: 500; 
    pointer-events: none; 
}}

.grid-cell {{
    background-color: white; 
    opacity: 1;
    transition: opacity 0.5s ease-out;
}}

.main-content-revealed {{
    background-image: var(--main-bg-url-pc);
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    filter: sepia(60%) grayscale(20%) brightness(85%) contrast(110%); 
    transition: filter 2s ease-out; 
}}

@media (max-width: 768px) {{
    .main-content-revealed {{
        background-image: var(--main-bg-url-mobile);
    }}
    .reveal-grid {{
        grid-template-columns: repeat(10, 1fr);
        grid-template-rows: repeat(20, 1fr);
    }}
}}

/* === TIÊU ĐỀ TRANG CHÍNH (FONT PLAYFAIR DISPLAY & HIỆU ỨNG PHÁT SÁNG TỪNG CHỮ) === */
#main-title-container {{
    position: fixed;
    top: 5vh; 
    left: 50%;
    transform: translate(-50%, 0); 
    width: 90%; 
    text-align: center;
    z-index: 20; 
    pointer-events: none; 
    
    display: flex;
    justify-content: center;
    overflow: hidden; 
}}

#main-title-container h1 {{
    display: flex; 
    font-family: 'Playfair Display', serif; 
    font-size: 3.5vw; 
    margin: 0;
    font-weight: 900; 
    font-feature-settings: "lnum" 1; 
    letter-spacing: 5px; 
    color: #F0F0F0; 
    white-space: nowrap; 
}}

.main-title-char {{
    display: inline-block; 
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7); 
    transition: text-shadow 0.3s ease-in-out; 
}}

@keyframes glow {{
    0% {{ 
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7), 
                     0 0 0px rgba(255, 255, 200, 0); 
    }}
    50% {{ 
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7), 
                     0 0 15px rgba(255, 255, 200, 0.8), 
                     0 0 25px rgba(255, 255, 150, 0.6);
    }}
    100% {{ 
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7), 
                     0 0 0px rgba(255, 255, 200, 0); 
    }}
}}

.main-title-char.glowing {{
    animation: glow 1.5s forwards; 
}}


@media (max-width: 768px) {{
    #main-title-container {{
        width: 95%; 
        left: 50%;
        /* Đảm bảo căn giữa tuyệt đối trên Mobile */
        justify-content: center; 
    }}
    
    #main-title-container h1 {{
        font-size: 6.5vw; 
        font-weight: 900; 
        font-feature-settings: "lnum" 1; 
        white-space: nowrap; 
    }}
    .main-title-char {{
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.7); 
    }}
    @keyframes glow {{ 
        0% {{ 
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.7), 
                         0 0 0px rgba(255, 255, 200, 0); 
        }}
        50% {{ 
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.7), 
                         0 0 10px rgba(255, 255, 200, 0.7), 
                         0 0 20px rgba(255, 255, 150, 0.5);
        }}
        100% {{ 
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.7), 
                         0 0 0px rgba(255, 255, 200, 0); 
        }}
    }}
}}
</style>
"""

# Thêm CSS vào trang chính
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- PHẦN 3: MÃ HTML/CSS/JavaScript IFRAME CHO VIDEO INTRO (FONT SACRAMENTO & HIỆU ỨNG CHỮ THẢ) ---

# JavaScript ĐÃ CHỈNH SỬA: Thêm code hiển thị tiêu đề chính vào initRevealEffect
js_callback_video = f"""
<script>
    function sendBackToStreamlit() {{
        window.parent.document.querySelector('.stApp').classList.add('video-finished', 'main-content-revealed');
        initRevealEffect();
        window.parent.postMessage({{ type: 'video_ended' }}, '*'); 
    }}
    
    function initRevealEffect() {{
        const revealGrid = window.parent.document.querySelector('.reveal-grid');
        const mainTitle = window.parent.document.getElementById('main-title-container');

        if (!revealGrid) {{
            if (mainTitle) {{
                 mainTitle.style.opacity = 1;
                 mainTitle.style.transform = 'translate(-50%, 0) scale(1)';
            }}
            return;
        }}

        const cells = revealGrid.querySelectorAll('.grid-cell');
        const shuffledCells = Array.from(cells).sort(() => Math.random() - 0.5);

        shuffledCells.forEach((cell, index) => {{
            setTimeout(() => {{
                cell.style.opacity = 0; 
            }}, index * 10);
        }});
        
        setTimeout(() => {{
             revealGrid.remove();
             if (mainTitle) {{
                 mainTitle.style.opacity = 1;
                 mainTitle.style.transform = 'translate(-50%, 0) scale(1)';
             }}
        }}, shuffledCells.length * 10 + 1000);
    }}

    document.addEventListener("DOMContentLoaded", function() {{
        const video = document.getElementById('intro-video');
        const audio = document.getElementById('background-audio');
        const introTextContainer = document.getElementById('intro-text-container'); 
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
                
            const chars = introTextContainer.querySelectorAll('.intro-char');
            chars.forEach((char, index) => {{
                char.style.animationDelay = `${{index * 0.1}}s`; 
                char.classList.add('char-shown'); 
            }});

            audio.volume = 0.5;
            audio.loop = true; 
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
            introTextContainer.style.opacity = 0; 
            
            sendBackToStreamlit(); 
        }};

        document.body.addEventListener('click', () => {{
             video.play().catch(e => {{}});
             audio.play().catch(e => {{}});
        }}, {{ once: true }});
    }});
</script>
"""

# Mã HTML/CSS cho Video (Font Sacramento)
html_content_modified = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
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

        /* === TIÊU ĐỀ INTRO (FONT SACRAMENTO - Chữ Ký) === */
        #intro-text-container {{ 
            position: fixed;
            top: 5vh;
            width: 100%;
            text-align: center;
            color: #FFD700; 
            font-size: 3vw; 
            
            font-family: 'Sacramento', cursive; 
            font-weight: 400; 
            
            text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.8); 
            z-index: 100;
            pointer-events: none;
            display: flex; 
            justify-content: center;
            opacity: 1; 
        }}
        
        .intro-char {{
            display: inline-block; 
            opacity: 0;
            transform: translateY(-50px); 
            animation-fill-mode: forwards; 
            animation-duration: 0.8s; 
            animation-timing-function: ease-out; 
        }}

        @keyframes charDropIn {{
            from {{
                opacity: 0;
                transform: translateY(-50px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .intro-char.char-shown {{
            animation-name: charDropIn;
        }}

        @media (max-width: 768px) {{
            #intro-text-container {{
                font-size: 6vw; 
            }}
        }}
        
    </style>
</head>
<body>

    <div id="intro-text-container">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    
    <video id="intro-video" muted playsinline></video>
    
    <audio id="background-audio"></audio>

    {js_callback_video}
</body>
</html>
"""

# Xử lý nội dung của tiêu đề video intro để thêm hiệu ứng chữ thả
intro_title = "KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI"
intro_chars_html = ''.join([
    f'<span class="intro-char">{char}</span>' if char != ' ' else '<span class="intro-char">&nbsp;</span>' 
    for char in intro_title
])
html_content_modified = html_content_modified.replace(
    "<div id=\"intro-text-container\">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>",
    f"<div id=\"intro-text-container\">{intro_chars_html}</div>"
)

# Hiển thị thành phần HTML (video)
st.components.v1.html(html_content_modified, height=10, scrolling=False)


# --- HIỆU ỨNG REVEAL VÀ NỘI DUNG CHÍNH ---

# Tạo Lưới Reveal (Giữ nguyên)
grid_cells_html = ""
for i in range(240): 
    grid_cells_html += f'<div class="grid-cell"></div>'

reveal_grid_html = f"""
<div class="reveal-grid">
    {grid_cells_html}
</div>
"""
st.markdown(reveal_grid_html, unsafe_allow_html=True)


# --- NỘI DUNG CHÍNH VÀ JS CHO HIỆU ỨNG CHỮ PHÁT SÁNG ---

# Tiêu đề trang chính (Được bọc trong các span cho hiệu ứng)
main_title_text = "TỔ BẢO DƯỠNG SỐ 1"
main_title_chars_html = ''.join([
    f'<span class="main-title-char">{char}</span>' if char != ' ' else '<span class="main-title-char">&nbsp;</span>' 
    for char in main_title_text
])

# JavaScript cho hiệu ứng phát sáng lặp lại (ĐÃ SỬA LỖI)
js_glow_effect = f"""
<script>
    function startMainTitleGlow() {{
        const mainTitleContainer = document.getElementById('main-title-container');
        if (!mainTitleContainer) return;
        
        const chars = mainTitleContainer.querySelectorAll('.main-title-char');
        if (chars.length === 0) return;
        
        let currentIndex = 0;
        const delay = 100; // Độ trễ giữa mỗi chữ (ms)
        const animationDuration = 1500; // Tổng thời gian animation của mỗi chữ (ms)

        function animateChar() {{
            const currentChar = chars[currentIndex];
            
            // Xóa animation cũ
            currentChar.classList.remove('glowing'); 
            // Dùng requestAnimationFrame để force reflow và reset animation mượt hơn void offsetWidth
            requestAnimationFrame(() => {{
                currentChar.classList.add('glowing');
            }});

            // Thiết lập timer cho chữ cái tiếp theo
            currentIndex = (currentIndex + 1) % chars.length;
            setTimeout(animateChar, delay);
        }}

        // Bắt đầu animation
        setTimeout(() => {{
            animateChar();
        }}, 500); 
    }}

    // Lắng nghe sự kiện từ iframe con (video) để biết khi nào video kết thúc
    window.addEventListener('message', (event) => {{
        if (event.data && event.data.type === 'video_ended') {{
            // Đợi một chút để tiêu đề chính hiện ra hoàn toàn
            setTimeout(startMainTitleGlow, 1200); 
        }}
    }});

    // Nếu trang được tải lại trực tiếp (ví dụ: F5), bắt đầu glow ngay
    document.addEventListener("DOMContentLoaded", function() {{
        const stApp = document.querySelector('.stApp');
        // Kiểm tra nếu class 'main-content-revealed' đã được thêm vào (tức là đã qua intro)
        if (stApp && stApp.classList.contains('main-content-revealed')) {{
             // Đợi một chút để đảm bảo DOM đã sẵn sàng và tiêu đề đã hiện
             setTimeout(startMainTitleGlow, 1500);
        }}
    }});

</script>
"""

# Nhúng tiêu đề và JavaScript vào Streamlit
st.markdown(f"""
<div id="main-title-container" style="color: white; opacity: 0; transition: opacity 2s, transform 1s; transform: translate(-50%, 0) scale(0.9);">
    <h1>{main_title_chars_html}</h1>
</div>
{js_glow_effect}
""", unsafe_allow_html=True)
