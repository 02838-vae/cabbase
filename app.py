import streamlit as st
import base64
import os

# --- CẤU HÌNH BAN ĐẦU ---
st.set_page_config(
    page_title="Tổ Bảo Dưỡng Số 1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Khởi tạo session state (giữ nguyên)
if 'video_ended' not in st.session_state:
    st.session_state.video_ended = False

# --- CÁC HÀM TIỆN ÍCH ---

def get_base64_encoded_file(file_path):
    """Đọc file và trả về Base64 encoded string. Dùng cho các file nhỏ/cần tải ngay."""
    if not os.path.exists(file_path):
        st.error(f"Lỗi: Không tìm thấy file media. Vui lòng kiểm tra lại đường dẫn: {file_path}")
        st.stop() # Dừng ứng dụng nếu file không tồn tại
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    except Exception as e:
        st.error(f"Lỗi khi mã hóa Base64 cho file {file_path}: {e}")
        st.stop()


# Mã hóa các file media cần thiết (Ảnh nền)
try:
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")

    # === SỬ DỤNG ĐƯỜNG DẪN TƯƠNG ĐỐI CHO BÀI HÁT ===
    SONG_PATHS = [f"songs/background{i}.mp3" for i in range(1, 7)]
    song_paths_js_array = str(SONG_PATHS).replace("'", '"')
    
except Exception as e:
    st.error(f"Lỗi khi tải file media: {e}")
    st.stop()


# --- FONT LINKS (giữ nguyên) ---
font_links = """
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
"""
st.markdown(font_links, unsafe_allow_html=True)


# --- PHẦN CSS CHUNG CHO ỨNG DỤNG (ĐÃ CẬP NHẬT CHO GIAO DIỆN MỚI) ---
app_css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sacramento&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');

/* Reset và ẩn các thành phần Streamlit mặc định */
#MainMenu, footer, header {{visibility: hidden;}}
html, body {{margin: 0; padding: 0; scroll-behavior: smooth;}} /* Cuộn mượt */

.main {{padding: 0; margin: 0;}}
div.block-container {{padding: 0; margin: 0; max-width: 100% !important;}}

.stApp {{
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
    background-image: var(--main-bg-url-pc);
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    filter: sepia(60%) grayscale(20%) brightness(85%) contrast(110%); 
    transition: filter 2s ease-out; 
}}

@media (max-width: 768px) {{
    .stApp {{
        background-image: var(--main-bg-url-mobile);
    }}
}}

/* --- HEADER CỐ ĐỊNH & MENU HAMBURGER --- */
.header {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    padding: 15px 30px;
    background: rgba(0, 0, 0, 0.7); /* Nền đen mờ ban đầu */
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 1000;
    transition: background 0.3s ease-in-out, padding 0.3s ease-in-out;
}}

.header.scrolled {{ /* Header khi cuộn */
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
    z-index: 1001; /* Đảm bảo nút hamburger nằm trên menu overlay */
}}

.hamburger-menu .bar {{
    width: 100%;
    height: 3px;
    background-color: white;
    transition: all 0.3s ease-in-out;
}}

/* Hiệu ứng khi menu mở */
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
    right: -100%; /* Ban đầu ẩn sang phải */
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
    right: 0; /* Hiện ra */
}}

.menu-overlay nav ul {{
    list-style: none;
    padding: 0;
    margin: 0;
    text-align: center;
}}

.menu-overlay nav ul li {{
    margin-bottom: 20px;
    opacity: 0; /* Ban đầu ẩn các mục menu */
    transform: translateX(50px);
    transition: opacity 0.4s ease-out, transform 0.4s ease-out;
}}

.menu-overlay.open nav ul li {{
    opacity: 1; /* Hiện ra khi menu mở */
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

/* --- CÁC SECTION NỘI DUNG CHÍNH --- */
.section {{
    min-height: 100vh; /* Mỗi section cao ít nhất 100% viewport */
    display: flex;
    justify-content: center;
    align-items: center;
    color: white;
    text-align: center;
    padding: 50px 20px;
    box-sizing: border-box; /* Bao gồm padding trong chiều cao */
    
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

#hero-section {{
    background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), var(--main-bg-url-pc); /* Lớp phủ đen trên ảnh nền chính */
    background-attachment: fixed; /* Parallax */
}}
@media (max-width: 768px) {{
    #hero-section {{
        background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), var(--main-bg-url-mobile);
    }}
}}


.section h2 {{
    font-family: 'Playfair Display', serif;
    font-size: 50px;
    margin-bottom: 20px;
    color: gold;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
}}

.section p {{
    font-family: 'Playfair Display', serif;
    font-size: 20px;
    line-height: 1.6;
    max-width: 800px;
    margin: 0 auto;
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
    opacity: 1; /* Luôn hiển thị */
}}

@media (max-width: 768px) {{
    #music-player-container {{
        top: auto; /* Bỏ vị trí top cố định */
        bottom: 20px; /* Đặt ở dưới cùng */
        left: 50%;
        transform: translateX(-50%); /* Căn giữa theo chiều ngang */
        width: 80%; /* Rộng hơn trên di động */
    }}
}}

</style>
"""
st.markdown(app_css, unsafe_allow_html=True)


# --- JAVASCRIPT CHUNG CHO GIAO DIỆN (HEADER, MENU, SCROLL REVEAL) ---
app_js = """
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const header = document.querySelector('.header');
        const hamburgerMenu = document.querySelector('.hamburger-menu');
        const menuOverlay = document.querySelector('.menu-overlay');
        const menuLinks = document.querySelectorAll('.menu-overlay nav ul li a');
        
        // --- Header Scroll Effect ---
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) { // Khi cuộn quá 50px
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });

        // --- Menu Hamburger Toggle ---
        function toggleMenu() {
            hamburgerMenu.classList.toggle('open');
            menuOverlay.classList.toggle('open');
            document.body.classList.toggle('no-scroll'); // Ngăn cuộn khi menu mở
        }

        hamburgerMenu.addEventListener('click', toggleMenu);

        menuLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault(); // Ngăn hành vi cuộn mặc định
                const targetId = this.getAttribute('href').substring(1); // Lấy ID của section
                const targetSection = document.getElementById(targetId);

                if (targetSection) {
                    toggleMenu(); // Đóng menu sau khi chọn
                    // Cuộn đến section với offset cho header
                    window.scrollTo({
                        top: targetSection.offsetTop - header.offsetHeight, 
                        behavior: 'smooth'
                    });
                }
            });
        });

        // --- Scroll Reveal Effect ---
        const revealElements = document.querySelectorAll('.reveal');

        const observerOptions = {
            root: null, // viewport
            rootMargin: '0px',
            threshold: 0.2 // Hiện ra khi 20% phần tử hiển thị
        };

        const observer = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target); // Ngừng quan sát sau khi hiện
                }
            });
        }, observerOptions);

        revealElements.forEach(el => observer.observe(el));
    });
</script>
"""
st.markdown(app_js, unsafe_allow_html=True)


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

# --- CÁC SECTION NỘI DUNG ---

# Section 1: Hero Section (Trang chủ)
st.markdown(f"""
<section id="hero-section" class="section">
    <div class="reveal">
        <h2>Chào mừng đến với Tổ Bảo Dưỡng Số 1</h2>
        <p>Chúng tôi mang đến những giải pháp bảo dưỡng máy bay hàng đầu với công nghệ tiên tiến và đội ngũ chuyên gia giàu kinh nghiệm.</p>
        <p style="margin-top: 20px;">An toàn, Chất lượng, Hiệu quả là cam kết của chúng tôi.</p>
    </div>
</section>
""", unsafe_allow_html=True)


# Section 2: About Us (Về chúng tôi)
st.markdown("""
<section id="about-section" class="section" style="background-color: rgba(20, 20, 20, 0.8);">
    <div class="reveal">
        <h2>Về Chúng Tôi</h2>
        <p>Với hơn 20 năm kinh nghiệm trong ngành hàng không, Tổ Bảo Dưỡng Số 1 tự hào là đối tác tin cậy của nhiều hãng hàng không lớn.</p>
        <p>Chúng tôi không ngừng nâng cao chất lượng dịch vụ và đầu tư vào công nghệ mới nhất để đảm bảo sự an toàn tuyệt đối cho mọi chuyến bay.</p>
    </div>
</section>
""", unsafe_allow_html=True)

# Section 3: Services (Dịch vụ)
st.markdown("""
<section id="services-section" class="section" style="background-color: rgba(30, 30, 30, 0.8);">
    <div class="reveal">
        <h2>Dịch Vụ Của Chúng Tôi</h2>
        <p>Chúng tôi cung cấp đa dạng các dịch vụ bảo dưỡng, sửa chữa và kiểm tra định kỳ cho nhiều loại máy bay khác nhau.</p>
        <p>Từ kiểm tra động cơ đến hệ thống điện tử, đội ngũ của chúng tôi luôn sẵn sàng phục vụ 24/7.</p>
    </div>
</section>
""", unsafe_allow_html=True)

# Section 4: Team (Đội ngũ)
st.markdown("""
<section id="team-section" class="section" style="background-color: rgba(40, 40, 40, 0.8);">
    <div class="reveal">
        <h2>Đội Ngũ Chuyên Gia</h2>
        <p>Đội ngũ kỹ sư và kỹ thuật viên của chúng tôi đều là những người có chuyên môn cao, được đào tạo bài bản và có nhiều năm kinh nghiệm.</p>
        <p>Chúng tôi luôn đặt sự tận tâm và chuyên nghiệp lên hàng đầu.</p>
    </div>
</section>
""", unsafe_allow_html=True)

# Section 5: Contact (Liên hệ)
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


# --- MUSIC PLAYER CỐ ĐỊNH ---

song_names_js_array = str([f"Background {i}" for i in range(1, 7)]).replace("'", '"')

music_player_full_template = """
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
            
            // Tự động phát nhạc sau khi trang tải xong và có tương tác đầu tiên (nếu cần)
            document.body.addEventListener('click', () => {{
                if (player.paused) {{
                    playSong();
                }}
            }}, {{ once: true }});
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

# Chèn các biến Python vào template
music_player_full_code = music_player_full_template.format(
    song_paths_js_array=song_paths_js_array,
    song_names_js_array=song_names_js_array
)

# Nhúng Music Player vào trang chính bằng st.markdown
st.markdown(music_player_full_code, unsafe_allow_html=True)
