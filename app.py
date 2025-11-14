import streamlit as st
import base64
import os

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
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return None
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    except Exception as e:
        st.error(f"Lỗi khi đọc file {file_path}: {str(e)}")
        return None


# Mã hóa các file media chính (bắt buộc)
try:
    # Đảm bảo các file này nằm cùng thư mục với app.py
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
    
    # MÃ HÓA CHO LOGO
    logo_base64 = get_base64_encoded_file("logo.jpg")

    # Kiểm tra file bắt buộc
    if not all([video_pc_base64, video_mobile_base64, audio_base64, bg_pc_base64, bg_mobile_base64]):
        missing_files = []
        if not video_pc_base64: missing_files.append("airplane.mp4")
        if not video_mobile_base64: missing_files.append("mobile.mp4")
        if not audio_base64: missing_files.append("plane_fly.mp3")
        if not bg_pc_base64: missing_files.append("cabbase.jpg")
        if not bg_mobile_base64: missing_files.append("mobile.jpg")
        
        st.error(f"⚠️ Thiếu các file media cần thiết hoặc file rỗng. Vui lòng kiểm tra lại các file sau trong thư mục:")
        st.write(" - " + "\n - ".join(missing_files))
        st.stop()
        
except Exception as e:
    st.error(f"❌ Lỗi khi đọc file: {str(e)}")
    st.stop()

# Đảm bảo logo_base64 được khởi tạo nếu file không tồn tại
if not 'logo_base64' in locals() or not logo_base64:
    logo_base64 = "" 
    st.info("ℹ️ Không tìm thấy file logo.jpg.")


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

/* Iframe Video Intro */
iframe:first-of-type {{
    transition: opacity 1s ease-out, visibility 1s ease-out;
    opacity: 1;
    visibility: visible;
    width: 100vw !important;
    height: 100vh !important;
    position: fixed;
    top: 0;
    left: 0;
    /* Tăng Z-index để đảm bảo video ở trên cùng */
    z-index: 1000;
}}

.video-finished iframe:first-of-type {{
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
    height: 1px !important;
    width: 1px !important;
}}

.stApp {{
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
    --logo-bg-url: url('data:image/jpeg;base64,{logo_base64}');
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

/* Keyframes cho hiệu ứng chữ chạy đơn */
@keyframes scrollText {{
    0% {{ transform: translate(100vw, 0); }}
    100% {{ transform: translate(-100%, 0); }}
}}

/* Keyframes cho hiệu ứng Đổi Màu Gradient */
@keyframes colorShift {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

/* === TIÊU ĐỀ TRANG CHÍNH === */
#main-title-container {{
    position: fixed;
    top: 5vh;
    left: 0;
    width: 100%;
    height: 10vh;
    overflow: hidden;
    z-index: 20;
    pointer-events: none;
    opacity: 0;
    transition: opacity 2s;
}}

.video-finished #main-title-container {{
    opacity: 1;
}}

#main-title-container h1 {{
    font-family: 'Playfair Display', serif;
    font-size: 3.5vw;
    margin: 0;
    font-weight: 900;
    font-feature-settings: "lnum" 1;
    letter-spacing: 5px;
    white-space: nowrap;
    display: inline-block;
    animation: scrollText 15s linear infinite;
    background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
    background-size: 400% 400%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    color: transparent;
    animation: colorShift 10s ease infinite, scrollText 15s linear infinite;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}}

@media (max-width: 768px) {{
    #main-title-container {{
        height: 8vh;
        width: 100%;
        left: 0;
    }}
    
    #main-title-container h1 {{
        font-size: 6.5vw;
        animation-duration: 8s;
    }}
}}


/* ✅ ĐÃ XÓA TẤT CẢ CSS LIÊN QUAN ĐẾN MUSIC PLAYER */


/* === CSS MỚI CHO NAVIGATION BUTTON (UIverse Dark Mode) === */

.nav-container {{
    position: fixed;
    /* Lệch trái 15% */
    left: 15%; 
    top: 50%;
    transform: translate(-50%, -50%);
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 40px;
    opacity: 0;
    transition: opacity 2s ease-out 3s;
    /* QUAN TRỌNG: Đảm bảo button ở trên cùng */
    z-index: 10000;
}}

.video-finished .nav-container {{
    opacity: 1;
}}

/* KHỞI TẠO CÁC BIẾN CSS */
.button {{
    --black-700: hsla(0, 0%, 12%, 1);
    --border_radius: 9999px; 
    --transtion: 0.3s ease-in-out;
    --active: 0; 
    /* ĐIỀU CHỈNH: Màu ánh sáng hover SIÊU DỊU (Vàng Pastel) */
    --hover-color: hsl(40, 60%, 85%);
    --text-color: hsl(0, 0%, 100%); 
    
    cursor: pointer;
    position: relative;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transform-origin: center;
    padding: 1rem 2rem;
    background-color: transparent;
    border: none;
    border-radius: var(--border_radius);
    
    /* ĐIỀU CHỈNH: Tăng hiệu ứng phóng to (scale 0.2) */
    transform: scale(calc(1 + (var(--active, 0) * 0.2)));
    transition: transform var(--transtion);
    
    text-decoration: none; 
}}

/* NỀN ĐEN CỦA BUTTON */
.button::before {{
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 100%;
    height: 100%;
    background-color: var(--black-700);
    border-radius: var(--border_radius);
    box-shadow: 
        inset 0 0.5px hsl(0, 0%, 100%), 
        inset 0 -1px 2px 0 hsl(0, 0%, 0%), 
        0px 4px 10px -4px hsla(0, 0%, 0%, calc(1 - var(--active, 0))), 
        0 0 0 calc(var(--active, 0) * 0.375rem) var(--hover-color);
    transition: all var(--transtion);
    z-index: 0;
}}

/* HIỆU ỨNG TIA SÁNG BÊN TRONG KHI HOVER (Background Gradient) */
.button::after {{
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 90%;
    height: 90%;
    
    /* ĐIỀU CHỈNH: Gradient bên trong button chuyển sang tông vàng/cam siêu dịu */
    background-color: hsla(40, 60%, 85%, 0.75);
    background-image: 
        radial-gradient(at 51% 89%, hsla(45, 60%, 90%, 1) 0px, transparent 50%), 
        radial-gradient(at 100% 100%, hsla(35, 60%, 80%, 1) 0px, transparent 50%), 
        radial-gradient(at 22% 91%, hsla(35, 60%, 80%, 1) 0px, transparent 50%);
    background-position: top;
    opacity: var(--active, 0); 
    border-radius: var(--border_radius);
    transition: opacity var(--transtion);
    z-index: 2;
}}

/* KÍCH HOẠT TRẠNG THÁI HOVER */
.button:is(:hover, :focus-visible) {{
    --active: 1;
}}

/* HIỆU ỨNG ÁNH SÁNG CHẠY VIỀN LIÊN TỤC (dots_border) */
.button .dots_border {{
    --size_border: calc(100% + 2px);
    overflow: hidden;

    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);

    width: var(--size_border);
    height: var(--size_border);
    background-color: transparent;

    border-radius: var(--border_radius);
    z-index: -1; 
}}

/* LỚP GIẢ TẠO DÒNG ÁNH SÁNG XOAY */
.button .dots_border::before {{
    content: "";
    position: absolute;
    top: 50%; 
    left: 50%;
    
    width: 300%; 
    height: 300%; 
    
    transform: translate(-50%, -50%) rotate(0deg); 
    transform-origin: center;
    
    background: white;
    /* ĐIỀU CHỈNH: Masking mới để ĐẢM BẢO chỉ 1 vệt sáng duy nhất */
    mask: conic-gradient(
        from 0deg at 50% 50%, 
        transparent 0%, 
        transparent 30%, 
        white 31%, 
        white 35%, /* Giữ độ dày vệt sáng đủ để thấy */
        transparent 36%, 
        transparent 100%
    );
                          
    animation: rotate 3s linear infinite;
}}

@keyframes rotate {{
    to {{ transform: translate(-50%, -50%) rotate(360deg); }}
}}

/* ICON và TEXT (Giữ nguyên) */
.button .sparkle {{
    position: relative;
    z-index: 10;
    width: 1.75rem;
}}

.button .sparkle .path {{
    fill: currentColor;
    stroke: currentColor;
    transform-origin: center;
    color: var(--text-color); 
    transition: transform var(--transtion);
}}

.button:is(:hover, :focus) .sparkle .path {{
    animation: path 1.5s linear 0.5s infinite;
}}

@keyframes path {{
    0%, 34%, 71%, 100% {{ transform: scale(1); }}
    17% {{ transform: scale(1.2); }}
    49% {{ transform: scale(1.2); }}
    83% {{ transform: scale(1.2); }}
}}

.button .text_button {{
    position: relative;
    z-index: 10;
    background-image: linear-gradient(
        90deg, 
        var(--text-color) 0%, 
        hsla(0, 0%, 100%, var(--active, 0.5)) 120% 
    );
    background-clip: text;
    -webkit-background-clip: text; 
    font-size: 1.1rem;
    color: transparent; 
    font-weight: 600;
    letter-spacing: 1px;
    white-space: nowrap;
    text-shadow: 0 0 5px rgba(0, 0, 0, 0.5); 
}}

@media (max-width: 768px) {{
    .nav-container {{
        left: 50%;
        transform: translate(-50%, -50%);
        width: 100%;
        padding: 20px;
    }}
    
    .button {{
        padding: 0.8rem 1.5rem;
        gap: 0.4rem;
        width: 100%;
        max-width: 400px;
        justify-content: center;
    }}
    .button .sparkle {{
        width: 1.5rem;
    }}
    .button .text_button {{
        font-size: 1.1rem;
        white-space: nowrap;
    }}
}}

@keyframes fadeInUp {{
    from {{
        opacity: 0;
        transform: translateY(50px) scale(0.9);
    }}
    to {{
        opacity: 1;
        transform: translateY(0) scale(1);
    }}
}}

.video-finished .button {{
    animation: fadeInUp 1s ease-out forwards;
    animation-delay: 3.2s;
    opacity: 0;
}}
</style>
"""

# Thêm CSS vào trang chính
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- PHẦN 3: MÃ HTML/CSS/JavaScript IFRAME CHO VIDEO INTRO (Đã bỏ Music Player) ---

# JavaScript 
js_callback_video = f"""
<script>
    console.log("Script loaded");
    function sendBackToStreamlit() {{
        console.log("Video ended or skipped, revealing main content");
        const stApp = window.parent.document.querySelector('.stApp');
        if (stApp) {{
            stApp.classList.add('video-finished', 'main-content-revealed');
            // Cập nhật session state của parent để lần sau skip intro (sử dụng kỹ thuật đổi title)
            window.parent.document.title = 'video_ended_true'; 
        }}
        initRevealEffect();
    }}
    
    function initRevealEffect() {{
        const revealGrid = window.parent.document.querySelector('.reveal-grid');
        if (!revealGrid) {{ return; }}

        const cells = revealGrid.querySelectorAll('.grid-cell');
        const shuffledCells = Array.from(cells).sort(() => Math.random() - 0.5);

        shuffledCells.forEach((cell, index) => {{
            setTimeout(() => {{
                cell.style.opacity = 0;
            }}, index * 10);
        }});
        setTimeout(() => {{
             revealGrid.remove();
        }}, shuffledCells.length * 10 + 1000);
    }}
    
    document.addEventListener("DOMContentLoaded", function() {{
        console.log("DOM loaded, waiting for elements...");
        
        const waitForElements = setInterval(() => {{
            const video = document.getElementById('intro-video');
            const audio = document.getElementById('background-audio');
            const introTextContainer = document.getElementById('intro-text-container');
           
            if (video && audio && introTextContainer) {{
                clearInterval(waitForElements);
                console.log("All elements found, initializing...");
                
                const isMobile = window.innerWidth <= 768;
         
                const videoSource = isMobile ? 'data:video/mp4;base64,{video_mobile_base64}' : 'data:video/mp4;base64,{video_pc_base64}';

                video.src = videoSource;
                audio.src = 'data:audio/mp3;base64,{audio_base64}';

                console.log("Video/Audio source set. Loading metadata...");
                const tryToPlay = () => {{
                    console.log("Attempting to play video (User interaction or Canplay event)");
                    video.play().then(() => {{
                        console.log("✅ Video is playing!");
                    }}).catch(err => {{
                        console.error("❌ Still can't play video, skipping intro (Error/File issue):", err);
                
                        setTimeout(sendBackToStreamlit, 2000);
                    }});
                    audio.play().catch(e => {{
                        console.log("Audio autoplay blocked (normal), waiting for video end.");
                    }});
                }};

                video.addEventListener('canplaythrough', tryToPlay, {{ once: true }});
                
                video.addEventListener('ended', () => {{
                    console.log("Video ended, transitioning...");
                    video.style.opacity = 0;
                    audio.pause();
                    audio.currentTime = 0;
    
                    introTextContainer.style.opacity = 0;
                    setTimeout(sendBackToStreamlit, 500);
                }});
                video.addEventListener('error', (e) => {{
                    console.error("Video error detected (Codec/Base64/File corrupted). Skipping intro:", e);
                    sendBackToStreamlit();
                }});
                const clickHandler = () => {{
                    console.log("User interaction detected, forcing play attempt.");
                    tryToPlay();
                    document.removeEventListener('click', clickHandler);
                    document.removeEventListener('touchstart', clickHandler);
                }};
                
                document.addEventListener('click', clickHandler, {{ once: true }});
                document.addEventListener('touchstart', clickHandler, {{ once: true }});
                
                video.load();
                const chars = introTextContainer.querySelectorAll('.intro-char');
                chars.forEach((char, index) => {{
                    char.style.animationDelay = `${{index * 0.1}}s`;
                    char.classList.add('char-shown');
                }});
            }}
        }}, 100);
        setTimeout(() => {{
            clearInterval(waitForElements);
            const video = document.getElementById('intro-video');
            if (video && !video.src) {{
                console.warn("Timeout before video source set. Force transitioning to main content.");
                sendBackToStreamlit();
            }}
  
        }}, 5000);
    }});
</script>
"""

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
            background-color: #000;
        }}
        
        #intro-video {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            z-index: 0;
            transition: opacity 1s;
        }}

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
            transition: opacity 0.5s;
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

# --- HIỂN THỊ IFRAME VIDEO VÀ REVEAL GRID ---

# LOGIC BỎ HIỆU ỨNG REVEAL KHI ĐÃ XEM LẦN ĐẦU (Quay lại trang chủ)
if not st.session_state.video_ended:
    # Lần đầu load trang: Hiển thị iframe và reveal grid
    st.components.v1.html(html_content_modified, height=1080, scrolling=False)

    # --- HIỆU ỨNG REVEAL VÀ NỘI DUNG CHÍNH ---

    # Tạo Lưới Reveal
    grid_cells_html = ""
    for i in range(240):
        grid_cells_html += f'<div class="grid-cell"></div>'

    reveal_grid_html = f"""
    <div class="reveal-grid">
        {grid_cells_html}
    </div>
    """
    st.markdown(reveal_grid_html, unsafe_allow_html=True)
    
    # Cập nhật session state khi JS đã báo hiệu video kết thúc
    # Sử dụng `st.empty()` để kiểm tra title (giả định kỹ thuật này được sử dụng để cập nhật session state)
    st.empty().markdown(f'<script>if(window.parent.document.title === "video_ended_true") window.parent.document.title = "{st.get_option("general.title")}";</script>', unsafe_allow_html=True)
    if st.get_option("general.title") == "video_ended_true":
        st.session_state.video_ended = True
        st.experimental_rerun()
                 
else:
    # Khi đã quay lại trang chủ, bỏ qua iframe và reveal grid, áp dụng CSS classes ngay lập tức
    st.markdown("""
    <script>
        const stApp = window.parent.document.querySelector('.stApp');
        if (stApp) {
            stApp.classList.add('video-finished', 'main-content-revealed');
        }
    </script>
    """, unsafe_allow_html=True)

# --- NỘI DUNG CHÍNH (TIÊU ĐỀ ĐƠN, ĐỔI MÀU) ---
main_title_text = "TỔ BẢO DƯỠNG SỐ 1"

# Nhúng tiêu đề
st.markdown(f"""
<div id="main-title-container">
    <h1>{main_title_text}</h1>
</div>
""", unsafe_allow_html=True)


# --- NAVIGATION BUTTON MỚI (UIverse Style) ---
# Tên trang phụ là partnumber.py nên link href là /partnumber
st.markdown("""
<div class="nav-container">
    <a href="/partnumber" target="_self" class="button">
        <div class="dots_border"></div>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="sparkle" > 
            <path class="path" stroke-linejoin="round" stroke-linecap="round" stroke="currentColor" fill="currentColor" d="M10 17a7 7 0 100-14 7 7 0 000 14zM21 21l-4-4" ></path> 
        </svg> 
        <span class="text_button">TRA CỨU PART NUMBER</span> 
    </a>
</div>
""", unsafe_allow_html=True)
