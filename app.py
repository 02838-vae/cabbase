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
    """Đọc file và trả về Base64 encoded string. Dùng cho các file nhỏ/cần tải ngay."""
    if not os.path.exists(file_path):
        st.error(f"Lỗi: Không tìm thấy file media. Vui lòng kiểm tra lại đường dẫn: {file_path}")
        st.stop()
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    except Exception as e:
        st.error(f"Lỗi khi mã hóa Base64 cho file {file_path}: {e}")
        st.stop()


# Mã hóa các file media cần thiết
try:
    # Không cần mã hóa video nếu chỉ dùng để preload/src trong iframe
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3") # Âm thanh Intro
    
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")

    # === SỬ DỤNG ĐƯỜNG DẪN TƯƠNG ĐỐI CHO BÀI HÁT ===
    SONG_PATHS = [f"songs/background{i}.mp3" for i in range(1, 7)]
    song_paths_js_array = str(SONG_PATHS).replace("'", '"')
    
except Exception:
    st.stop()


# --- FONT LINKS ---
font_links = """
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
"""
st.markdown(font_links, unsafe_allow_html=True)


# --- PHẦN CSS CHUNG CHO ỨNG DỤNG (ĐÃ FIX LỖI MÀU FILTER) ---
hide_streamlit_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sacramento&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');

/* Reset và ẩn các thành phần Streamlit mặc định */
#MainMenu, footer, header {{visibility: hidden;}}
html, body {{margin: 0; padding: 0; scroll-behavior: smooth;}}

.main {{padding: 0; margin: 0;}}
div.block-container {{padding: 0; margin: 0; max-width: 100% !important;}}

/* --- MÀU NỀN VÀ FILTER CỦA TRANG STREAMLIT CHÍNH --- */
.stApp {{
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
    background-image: var(--main-bg-url-pc);
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    
    /* TRẠNG THÁI GỐC: ÁP DỤNG HIỆU ỨNG CỔ ĐIỂN */
    filter: sepia(60%) grayscale(20%) brightness(85%) contrast(110%); 
    transition: filter 2s ease-out; 
}}

/* TRẠNG THÁI SAU KHI VIDEO KẾT THÚC: KHÔI PHỤC MÀU GỐC */
.stApp.video-finished {{
    filter: none; /* Reset filter về màu gốc */
}}
@media (max-width: 768px) {{
    .stApp {{
        background-image: var(--main-bg-url-mobile);
    }}
}}

/* --- ẨN IFRAME VIDEO INTRO --- */
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
    filter: none; /* ĐẢM BẢO KHÔNG BỊ FILTER TỪ .stApp ẢNH HƯỞNG */
}}

.video-finished iframe:first-of-type {{
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
    height: 1px !important; 
}}


/* --- REVEAL GRID VÀ HIỆU ỨNG --- */
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

@media (max-width: 768px) {{
    .reveal-grid {{
        grid-template-columns: repeat(10, 1fr);
        grid-template-rows: repeat(20, 1fr);
    }}
}}

/* --- HEADER CỐ ĐỊNH & MENU HAMBURGER --- */
.header {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    padding: 15px 30px;
    background: rgba(0, 0, 0, 0.7); 
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 1000;
    transition: background 0.3s ease-in-out, padding 0.3s ease-in-out;
    opacity: 0; 
    pointer-events: none;
}}

.video-finished .header {{
    opacity: 1; 
    pointer-events: all;
}}

.header.scrolled {{ 
    background: rgba(0, 0, 0, 0.9);
    padding: 10px 30px;
}}

.logo {{
    font-family: 'Playfair Display', serif;
    font-size: 28px;
    font-weight: bold;
    color: gold;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
}}

.hamburger-menu {{
    width: 30px;
    height: 20px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    cursor: pointer;
    z-index: 1001;
}}

.hamburger-menu .bar {{
    width: 100%;
    height: 3px;
    background-color: white;
    transition: all 0.3s ease-in-out;
}}

.hamburger-menu.open .bar:nth-child(1) {{
    transform: translateY(8.5px) rotate(45deg);
}}
.hamburger-menu.open .bar:nth-child(2) {{
    opacity: 0;
}}
.hamburger-menu.open .bar:nth-child(3) {{
    transform: translateY(-8.5px) rotate(-45deg);
}}

.menu-overlay {{
    position: fixed;
    top: 0;
    right: -100%; 
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.95);
    z-index: 999;
    display: flex;
    justify-content: center;
    align-items: center;
    transition: right 0.5s ease-in-out;
}}

.menu-overlay.open {{
    right: 0; 
}}

.menu-overlay nav ul {{
    list-style: none;
    padding: 0;
    margin: 0;
    text-align: center;
}}

.menu-overlay nav ul li {{
    margin-bottom: 20px;
    opacity: 0; 
    transform: translateX(50px);
    transition: opacity 0.4s ease-out, transform 0.4s ease-out;
}}

.menu-overlay.open nav ul li {{
    opacity: 1; 
    transform: translateX(0);
}}

.menu-overlay.open nav ul li:nth-child(1) {{ transition-delay: 0.1s; }}
.menu-overlay.open nav ul li:nth-child(2) {{ transition-delay: 0.2s; }}
.menu-overlay.open nav ul li:nth-child(3) {{ transition-delay: 0.3s; }}
.menu-overlay.open nav ul li:nth-child(4) {{ transition-delay: 0.4s; }}
.menu-overlay.open nav ul li:nth-child(5) {{ transition-delay: 0.5s; }}

.menu-overlay nav ul li a {{
    color: white;
    text-decoration: none;
    font-family: 'Playfair Display', serif;
    font-size: 30px;
    font-weight: 600;
    transition: color 0.3s;
}}

.menu-overlay nav ul li a:hover {{
    color: gold;
}}

/* --- TIÊU ĐỀ CHẠY (TỪ CODE CŨ) --- */
@keyframes scrollText {{
    0% {{ transform: translate(100vw, 0); }} 
    100% {{ transform: translate(-100%, 0); }} 
}}
@keyframes colorShift {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

#main-title-container {{
    position: fixed;
    top: 15vh; 
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

/* --- CÁC SECTION NỘI DUNG CHÍNH --- */
.section {{
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    color: white;
    text-align: center;
    padding: 50px 20px;
    box-sizing: border-box;
    
    padding-top: 100px; 
}}

#hero-section {{
    padding-top: 250px; 
    background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)); 
    background-attachment: fixed;
}}


/* Hiệu ứng Reveal cho các phần tử */
.reveal {{
    opacity: 0;
    transform: translateY(50px);
    transition: opacity 1s ease-out, transform 1s ease-out;
}}

.reveal.visible {{
    opacity: 1;
    transform: translateY(0);
}}

/* --- MUSIC PLAYER --- */
#music-player-container {{
    position: fixed;
    top: 50%; 
    left: 20px; 
    transform: translateY(-50%);
    z-index: 150; 
    width: 200px; 
    transition: opacity 1s ease-in-out;
    opacity: 0; 
}}

.video-finished #music-player-container {{
    opacity: 1; 
}}

@media (max-width: 768px) {{
    #music-player-container {{
        top: auto; 
        bottom: 20px; 
        left: 50%;
        transform: translateX(-50%); 
        width: 80%; 
    }}
}}

</style>
"""

# Thêm CSS vào trang chính
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- JAVASCRIPT CHUNG CHO GIAO DIỆN (HEADER, MENU, SCROLL REVEAL) ---
app_js = """
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const header = window.parent.document.querySelector('.header');
        const hamburgerMenu = window.parent.document.querySelector('.hamburger-menu');
        const menuOverlay = window.parent.document.querySelector('.menu-overlay');
        const menuLinks = window.parent.document.querySelectorAll('.menu-overlay nav ul li a');
        
        // --- Header Scroll Effect ---
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) { 
                if (header) header.classList.add('scrolled');
            } else {
                if (header) header.classList.remove('scrolled');
            }
        });

        // --- Menu Hamburger Toggle ---
        function toggleMenu() {
            if (hamburgerMenu) hamburgerMenu.classList.toggle('open');
            if (menuOverlay) menuOverlay.classList.toggle('open');
        }

        if (hamburgerMenu) hamburgerMenu.addEventListener('click', toggleMenu);

        menuLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault(); 
                const targetId = this.getAttribute('href').substring(1); 
                const targetSection = window.parent.document.getElementById(targetId);

                if (targetSection) {
                    toggleMenu(); 
                    // Cuộn đến section với offset cho header
                    window.parent.window.scrollTo({
                        top: targetSection.offsetTop - (header ? header.offsetHeight : 0), 
                        behavior: 'smooth'
                    });
                }
            });
        });

        // --- Scroll Reveal Effect ---
        const revealElements = window.parent.document.querySelectorAll('.reveal');

        const observerOptions = {
            root: null, 
            rootMargin: '0px',
            threshold: 0.2 
        };

        const observer = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target); 
                }
            });
        }, observerOptions);

        revealElements.forEach(el => observer.observe(el));
    });
</script>
"""
st.markdown(app_js, unsafe_allow_html=True)


# --- PHẦN 3: MÃ HTML/CSS/JavaScript IFRAME CHO VIDEO INTRO ---

js_callback_video = f"""
<script>
    function sendBackToStreamlit() {{
        // Lớp 'video-finished' sẽ loại bỏ filter màu trên .stApp
        window.parent.document.querySelector('.stApp').classList.add('video-finished');
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

# --- CẤU TRÚC HEADER VÀ MENU ---
st.markdown("""
<header class="header">
    <div class="logo">Tổ Bảo Dưỡng Số 1</div>
    <div class="hamburger-menu">
        <div class="bar"></div>
        <div class="bar"></div>
        <div class="bar"></div>
    </div>
</header>

<div class="menu-overlay">
    <nav>
        <ul>
            <li><a href="#hero-section">TRANG CHỦ</a></li>
            <li><a href="#about-section">VỀ CHÚNG TÔI</a></li>
            <li><a href="#services-section">DỊCH VỤ</a></li>
            <li><a href="#team-section">ĐỘI NGŨ</a></li>
            <li><a href="#contact-section">LIÊN HỆ</a></li>
        </ul>
    </nav>
</div>
""", unsafe_allow_html=True)

# --- TIÊU ĐỀ CHẠY (TỪ CODE CŨ) ---
main_title_text = "TỔ BẢO DƯỠNG SỐ 1" 
st.markdown(f"""
<div id="main-title-container">
    <h1>{main_title_text}</h1>
</div>
""", unsafe_allow_html=True)


# --- CÁC SECTION NỘI DUNG ---

st.markdown(f"""
<section id="hero-section" class="section">
    <div class="reveal">
        <h2 style="margin-top: 100px;">Chào mừng đến với Tổ Bảo Dưỡng Số 1</h2>
        <p>Chúng tôi mang đến những giải pháp bảo dưỡng máy bay hàng đầu với công nghệ tiên tiến và đội ngũ chuyên gia giàu kinh nghiệm.</p>
        <p style="margin-top: 20px;">An toàn, Chất lượng, Hiệu quả là cam kết của chúng tôi.</p>
    </div>
</section>
""", unsafe_allow_html=True)


st.markdown("""
<section id="about-section" class="section" style="background-color: rgba(20, 20, 20, 0.8);">
    <div class="reveal">
        <h2>Về Chúng Tôi</h2>
        <p>Với hơn 20 năm kinh nghiệm trong ngành hàng không, Tổ Bảo Dưỡng Số 1 tự hào là đối tác tin cậy của nhiều hãng hàng không lớn.</p>
        <p>Chúng tôi không ngừng nâng cao chất lượng dịch vụ và đầu tư vào công nghệ mới nhất để đảm bảo sự an toàn tuyệt đối cho mọi chuyến bay.</p>
    </div>
</section>
""", unsafe_allow_html=True)

st.markdown("""
<section id="services-section" class="section" style="background-color: rgba(30, 30, 30, 0.8);">
    <div class="reveal">
        <h2>Dịch Vụ Của Chúng Tôi</h2>
        <p>Chúng tôi cung cấp đa dạng các dịch vụ bảo dưỡng, sửa chữa và kiểm tra định kỳ cho nhiều loại máy bay khác nhau.</p>
        <p>Từ kiểm tra động cơ đến hệ thống điện tử, đội ngũ của chúng tôi luôn sẵn sàng phục vụ 24/7.</p>
    </div>
</section>
""", unsafe_allow_html=True)

st.markdown("""
<section id="team-section" class="section" style="background-color: rgba(40, 40, 40, 0.8);">
    <div class="reveal">
        <h2>Đội Ngũ Chuyên Gia</h2>
        <p>Đội ngũ kỹ sư và kỹ thuật viên của chúng tôi đều là những người có chuyên môn cao, được đào tạo bài bản và có nhiều năm kinh nghiệm.</p>
        <p>Chúng tôi luôn đặt sự tận tâm và chuyên nghiệp lên hàng đầu.</p>
    </div>
</section>
""", unsafe_allow_html=True)

st.markdown("""
<section id="contact-section" class="section" style="background-color: rgba(50, 50, 50, 0.8);">
    <div class="reveal">
        <h2>Liên Hệ Với Chúng Tôi</h2>
        <p>Nếu bạn có bất kỳ câu hỏi nào về dịch vụ của chúng tôi, đừng ngần ngại liên hệ.</p>
        <p>Chúng tôi luôn sẵn lòng lắng nghe và hỗ trợ.</p>
        <p>Email: info@tobaoduongso1.com | Điện thoại: (84) 123 456 789</p>
    </div>
</section>
""", unsafe_allow_html=True)


# -----------------------------------------------------------
# --- PHẦN 4: MUSIC PLAYER CỐ ĐỊNH (FIXED MUSIC PLAYER) ---
# -----------------------------------------------------------

song_names_js_array = str([f"Background {i}" for i in range(1, 7)]).replace("'", '"')

music_player_full_code = f"""
<style>
/* CSS NỘI BỘ CHO PLAYER */
#music-player-container {{
    padding: 10px;
    background: rgba(0, 0, 0, 0.7); 
    border-radius: 15px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
    display: flex;
    flex-direction: column;
    gap: 10px;
}}

#player-controls {{
    display: flex;
    justify-content: space-around;
    align-items: center;
}}

#player-controls button {{
    background: none;
    border: none;
    color: gold;
    font-size: 24px;
    cursor: pointer;
    transition: color 0.3s;
    line-height: 1; 
}}

#player-controls button:hover {{
    color: white;
}}

#song-info {{
    color: white;
    font-size: 14px;
    text-align: center;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

#progress-container {{
    height: 5px;
    background: #444;
    border-radius: 5px;
    cursor: pointer;
}}

#progress-bar {{
    height: 100%;
    width: 0%;
    background: gold;
    border-radius: 5px;
    transition: width 0.1s linear;
}}
</style>

<div id="music-player-container">
    <div id="song-info">Đang tải...</div>
    
    <div id="player-controls">
        <button id="prev-btn" title="Bài trước">⏮️</button>
        <button id="play-pause-btn" title="Phát/Dừng">▶️</button>
        <button id="next-btn" title="Bài tiếp theo">⏭️</button>
    </div>
    
    <div id="progress-container">
        <div id="progress-bar"></div>
    </div>
    
    <audio id="main-music-player"></audio>
</div>

<script>
    const SONG_PATHS = {song_paths_js_array}; 
    const SONG_NAMES = {song_names_js_array};

    let currentSongIndex = 0;
    const player = document.getElementById('main-music-player');
    const playPauseBtn = document.getElementById('play-pause-btn');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const songInfo = document.getElementById('song-info');
    const progressBar = document.getElementById('progress-bar');
    const progressContainer = document.getElementById('progress-container');

    function loadSong(index) {{
        currentSongIndex = (index + SONG_PATHS.length) % SONG_PATHS.length;
        
        const path = SONG_PATHS[currentSongIndex];
        const songName = SONG_NAMES[currentSongIndex];
        
        player.src = path;
        songInfo.textContent = songName;
        player.load();
    }}

    function playSong() {{
        player.play().catch(e => {{
            console.log("Audio play failed, waiting for user interaction:", e);
        }});
        playPauseBtn.textContent = '⏸️'; 
        playPauseBtn.title = 'Pause';
    }}

    function pauseSong() {{
        player.pause();
        playPauseBtn.textContent = '▶️'; 
        playPauseBtn.title = 'Play';
    }}

    function nextSong() {{
        loadSong(currentSongIndex + 1);
        playSong();
    }}

    function prevSong() {{
        loadSong(currentSongIndex - 1);
        playSong();
    }}

    playPauseBtn.addEventListener('click', (e) => {{
        e.stopPropagation(); 
        if (player.paused) {{
            playSong();
        }} else {{
            pauseSong();
        }}
    }});

    nextBtn.addEventListener('click', (e) => {{ e.stopPropagation(); nextSong(); }});
    prevBtn.addEventListener('click', (e) => {{ e.stopPropagation(); prevSong(); }});

    player.addEventListener('timeupdate', () => {{
        if (!isNaN(player.duration)) {{
            const progressPercent = (player.currentTime / player.duration) * 100;
            progressBar.style.width = progressPercent + '%';
        }}
    }});
    
    progressContainer.addEventListener('click', (e) => {{
        const rect = progressContainer.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const width = rect.width;
        const duration = player.duration;
        if (!isNaN(duration)) {{
            player.currentTime = (clickX / width) * duration;
            playSong();
        }}
    }});
    
    player.addEventListener('ended', nextSong);

    document.addEventListener("DOMContentLoaded", () => {{
        if (SONG_PATHS.length > 0) {{
            loadSong(currentSongIndex);
            
            const stApp = window.parent.document.querySelector('.stApp');
            if(stApp) {{
                // Chờ cho lớp 'video-finished' được thêm vào (Video Intro kết thúc)
                const observer = new MutationObserver((mutationsList, observer) => {{
                    if (stApp.classList.contains('video-finished')) {{
                        setTimeout(playSong, 1000); 
                        observer.disconnect(); 
                    }}
                }});
                observer.observe(stApp, {{ attributes: true, attributeFilter: ['class'] }});
            }}
        }}
    }});
    
    const playerContainer = document.getElementById('music-player-container');
    playerContainer.addEventListener('click', () => {{
         if (player.src && player.paused) {{
             playSong();
         }}
    }}, {{ once: true }});

</script>
"""

# Nhúng Music Player vào trang chính bằng st.markdown
st.markdown(music_player_full_code, unsafe_allow_html=True)
