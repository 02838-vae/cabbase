import streamlit as st
import base64
import time
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

# ========== CẤU HÌNH VÀ TÀI NGUYÊN ==========

# File video và âm thanh intro
VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
SFX = "plane_fly.mp3"

# File ảnh cho hiệu ứng broken glass (ảnh frame cuối video)
BROKEN_IMAGE_PC = "airplane_shutter.jpg"
BROKEN_IMAGE_MOBILE = "mobile_shutter.jpg"

# File ảnh nền của trang chính
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"

st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

# Cấu hình hiệu ứng
GLASS_ROWS = 10
GLASS_COLS = 10
BREAK_DURATION = 1.5  # Thời gian hiệu ứng vỡ kính (giây)
REVEAL_GRID = 8       # Lưới để reveal trang chính (8x8)
REVEAL_DURATION = 3.5 # Thời gian reveal trang chính (giây)

# ========== ẨN UI STREAMLIT ==========

def hide_streamlit_ui():
    st.markdown("""
    <style>
    /* Ẩn các thành phần mặc định của Streamlit */
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
    }
    /* Đảm bảo ứng dụng chiếm toàn màn hình */
    .stApp, .main, .block-container {
        padding: 0 !important;
        margin: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        overflow: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ========== MÀN HÌNH INTRO VỚI HIỆU ỨNG BROKEN GLASS + REVEAL ==========
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    broken_image = BROKEN_IMAGE_MOBILE if is_mobile else BROKEN_IMAGE_PC
    bg_file = BG_MOBILE if is_mobile else BG_PC
    
    try:
        # Đọc và mã hóa các tệp tài nguyên
        with open(video_file, "rb") as f:
            video_b64 = base64.b64encode(f.read()).decode()
        with open(SFX, "rb") as a:
            audio_b64 = base64.b64encode(a.read()).decode()
        with open(broken_image, "rb") as bi:
            broken_b64 = base64.b64encode(bi.read()).decode()
        with open(bg_file, "rb") as b:
            bg_b64 = base64.b64encode(b.read()).decode()
            
    except FileNotFoundError as e:
        st.error(f"Lỗi: Không tìm thấy file tài nguyên. Vui lòng kiểm tra: {e.filename}")
        st.stop()
    
    # Lấy chiều cao của cửa sổ để component chiếm toàn bộ màn hình
    window_height = st_javascript("window.innerHeight", key="intro_height_js")
    if not isinstance(window_height, (int, float)) or window_height < 100:
        window_height = 800 # Giá trị dự phòng

    intro_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name='viewport' content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
        <style>
        /* ... CSS (Không thay đổi) ... */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html, body {{
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: #000;
        }}
        
        #container {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: #000;
        }}
        
        /* Background trang chính */
        #main-page-bg {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            width: 100%;
            height: 100%;
            background-image: url("data:image/jpeg;base64,{bg_b64}");
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
            z-index: 0;
            opacity: 0;
        }}
        
        #main-page-bg::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(to bottom, rgba(255, 235, 200, 0.25) 0%, rgba(160, 130, 90, 0.35) 50%, rgba(90, 70, 50, 0.5) 100%);
        }}
        
        #main-page-bg::after {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            /* Đổi URL nền thành base64 hoặc URL tĩnh an toàn nếu có thể */
            background-image: url("https://www.transparenttextures.com/patterns/noise-pattern-with-subtle-cross-lines.png");
            opacity: 0.09;
            mix-blend-mode: multiply;
        }}
        
        #main-page-bg.visible {{
            opacity: 1;
        }}
        
        video {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            z-index: 1;
        }}
        
        audio {{ display: none; }}
        
        #intro-text {{
            position: absolute;
            top: 8%;
            left: 50%;
            transform: translate(-50%, 0);
            width: 90%;
            text-align: center;
            color: #f8f4e3;
            font-size: clamp(22px, 6vw, 60px);
            font-weight: bold;
            font-family: 'Playfair Display', serif;
            background: linear-gradient(120deg, #e9dcb5 20%, #fff9e8 40%, #e9dcb5 60%);
            background-size: 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 15px rgba(255,255,230,0.4);
            animation: lightSweep 6s linear infinite, fadeInOut 6s ease-in-out forwards;
            line-height: 1.2;
            z-index: 10;
        }}
        
        @keyframes lightSweep {{ 
            0% {{ background-position: 200% 0%; }} 
            100% {{ background-position: -200% 0%; }} 
        }}
        
        @keyframes fadeInOut {{ 
            0% {{ opacity: 0; }} 
            20% {{ opacity: 1; }} 
            80% {{ opacity: 1; }} 
            100% {{ opacity: 0; }} 
        }}

        #broken-glass-container {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0;
            z-index: 5;
            pointer-events: none;
        }}
        
        #broken-glass-container.active {{
            opacity: 1;
        }}
        
        .broken-piece {{
            position: absolute;
            background-image: url("data:image/jpeg;base64,{broken_b64}");
            background-size: 100% 100%;
            overflow: hidden;
        }}

        #reveal-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: grid;
            grid-template-columns: repeat({REVEAL_GRID}, 1fr);
            grid-template-rows: repeat({REVEAL_GRID}, 1fr);
            z-index: 20;
            pointer-events: none;
        }}
        
        .reveal-tile {{
            background: #000;
            opacity: 1;
        }}
        
        #main-text {{
            position: absolute;
            top: 8%;
            left: 50%;
            transform: translate(-50%, 0);
            width: 90%;
            text-align: center;
            font-size: clamp(30px, 5vw, 65px);
            color: #fff5d7;
            font-family: 'Playfair Display', serif;
            text-shadow: 0 0 18px rgba(0,0,0,0.65), 0 0 30px rgba(255,255,180,0.25);
            background: linear-gradient(120deg, #f3e6b4 20%, #fff7d6 40%, #f3e6b4 60%);
            background-size: 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: textLight 10s linear infinite;
            letter-spacing: 2px;
            z-index: 25;
            opacity: 0;
        }}
        
        @keyframes textLight {{
            0% {{ background-position: 200% 0%; }}
            100% {{ background-position: -200% 0%; }}
        }}
        /* ... Kết thúc CSS ... */
        </style>
    </head>
    <body>
        <div id="container">
            <div id="main-page-bg"></div>
            
            <video id='introVid' autoplay muted playsinline>
                <source src='data:video/mp4;base64,{video_b64}' type='video/mp4'>
            </video>
            
            <audio id='flySfx'> 
                <source src='data:audio/mp3;base64,{audio_b64}' type='audio/mp3'>
            </audio>
            
            <div id='intro-text'>KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>

            <div id='broken-glass-container'></div>
            
            <div id='reveal-overlay'></div>
            
            <div id='main-text'>TỔ BẢO DƯỠNG SỐ 1</div>
        </div>

        <script>
        const GLASS_ROWS = {GLASS_ROWS};
        const GLASS_COLS = {GLASS_COLS};
        const BREAK_DURATION = {BREAK_DURATION};
        const REVEAL_GRID = {REVEAL_GRID};
        const REVEAL_DURATION = {REVEAL_DURATION};
        
        const vid = document.getElementById('introVid');
        const audio = document.getElementById('flySfx');
        const glassContainer = document.getElementById('broken-glass-container');
        const introText = document.getElementById('intro-text');
        // ... (Khai báo các biến khác)
        let ended = false;
        let hasInteracted = false;

        function createBrokenPieces() {{
            // ... (Hàm tạo mảnh vỡ)
            const pieceWidth = 100 / GLASS_COLS;
            const pieceHeight = 100 / GLASS_ROWS;
            
            for (let row = 0; row < GLASS_ROWS; row++) {{
                for (let col = 0; col < GLASS_COLS; col++) {{
                    const piece = document.createElement('div');
                    piece.className = 'broken-piece';
                    
                    piece.style.left = (col * pieceWidth) + '%';
                    piece.style.top = (row * pieceHeight) + '%';
                    piece.style.width = pieceWidth + '%';
                    piece.style.height = pieceHeight + '%';
                    
                    const bgX = -(col * pieceWidth);
                    const bgY = -(row * pieceHeight);
                    piece.style.backgroundPosition = bgX + '% ' + bgY + '%';
                    piece.style.backgroundSize = (GLASS_COLS * 100) + '% ' + (GLASS_ROWS * 100) + '%';
                    
                    glassContainer.appendChild(piece);
                }}
            }}
        }}

        function createRevealGrid() {{
            // ... (Hàm tạo lưới reveal)
            const revealOverlay = document.getElementById('reveal-overlay');
            for (let i = 0; i < REVEAL_GRID * REVEAL_GRID; i++) {{
                const tile = document.createElement('div');
                tile.className = 'reveal-tile';
                revealOverlay.appendChild(tile);
            }}
        }}

        function breakGlass() {{
            // ... (Hàm hiệu ứng vỡ kính)
            const pieces = document.querySelectorAll('.broken-piece');
            
            pieces.forEach((piece) => {{
                const angle = Math.random() * 360;
                const distance = 100 + Math.random() * 500;
                const x = Math.cos(angle * Math.PI / 180) * distance;
                const y = Math.sin(angle * Math.PI / 180) * distance;
                const rotation = Math.random() * 720 - 360;
                const delay = Math.random() * 0.3;
                
                gsap.to(piece, {{
                    x: x,
                    y: y,
                    rotation: rotation,
                    opacity: 0,
                    duration: BREAK_DURATION,
                    delay: delay,
                    ease: "power2.out"
                }});
            }});
        }}

        function revealMainPage() {{
            // ... (Hàm hiệu ứng reveal)
            const tiles = document.querySelectorAll('.reveal-tile');
            const centerRow = Math.floor(REVEAL_GRID / 2);
            const centerCol = Math.floor(REVEAL_GRID / 2);
            const mainBg = document.getElementById('main-page-bg');
            const mainText = document.getElementById('main-text');
            const revealOverlay = document.getElementById('reveal-overlay');
            
            mainBg.classList.add('visible');
            
            gsap.to(mainText, {{
                opacity: 1,
                duration: 1,
                ease: "power2.inOut"
            }});
            
            tiles.forEach((tile, index) => {{
                const row = Math.floor(index / REVEAL_GRID);
                const col = index % REVEAL_GRID;
                const distanceFromCenter = Math.abs(row - centerRow) + Math.abs(col - centerCol);
                const delay = distanceFromCenter * (REVEAL_DURATION / (REVEAL_GRID * 2));
                
                gsap.to(tile, {{
                    opacity: 0,
                    duration: 0.4,
                    delay: delay,
                    ease: "power2.inOut",
                    onComplete: function() {{
                        if (index === tiles.length - 1) {{
                            setTimeout(() => {{
                                revealOverlay.style.display = 'none';
                            }}, 100);
                        }}
                    }}
                }});
            }});
        }}

        function finishIntro() {{
            if (ended) return;
            ended = true;
            
            // Dừng audio và video (nếu chúng vẫn chạy)
            audio.pause(); 
            audio.currentTime = 0;
            vid.pause();
            
            vid.style.opacity = 0;
            introText.style.display = 'none';
            glassContainer.classList.add('active');
            
            setTimeout(() => {{
                breakGlass();
            }}, 100);
            
            setTimeout(() => {{
                glassContainer.style.opacity = 0;
                revealMainPage();
            }}, BREAK_DURATION * 1000 + 200);
            
            // Gửi tin nhắn lên Streamlit sau khi hiệu ứng kết thúc
            const total_duration = BREAK_DURATION * 1000 + REVEAL_DURATION * 1000 + 500;
            setTimeout(() => {{
                // Thay đổi query parameter và reload trang chính (Streamlit)
                // Đây là cơ chế duy nhất để thay đổi state trong Streamlit từ Component
                const currentUrl = new URL(window.parent.location.href);
                currentUrl.searchParams.set('intro_finished', 'true');
                window.parent.location.href = currentUrl.toString();
            }}, total_duration);
        }}

        function handleInteraction() {{
            if (!hasInteracted) {{
                hasInteracted = true;
                // Bỏ mute video (đây là bước quan trọng nhất)
                vid.muted = false; 
                audio.volume = 1.0;
                
                // Thử play video và audio
                const playVidPromise = vid.play();
                if (playVidPromise) {{
                    playVidPromise.catch(e => console.log('Video play failed after interaction:', e));
                }}
                
                const playAudioPromise = audio.play();
                if (playAudioPromise) {{
                    playAudioPromise.catch(e => console.log('Audio play failed after interaction:', e));
                }}
            }}
        }}


        createBrokenPieces();
        createRevealGrid();

        // Xử lý Autoplay ban đầu (muted)
        // Dùng 'loadedmetadata' để đảm bảo video có thể chạy, sau đó play
        vid.addEventListener('loadedmetadata', function() {{
            const playAttempt = vid.play();
            if (playAttempt !== undefined) {{
                playAttempt.then(_ => {{
                    // Autoplay thành công (muted)
                    console.log('Video playing (muted).');
                    // Thử play audio (thường bị chặn)
                    audio.play().catch(e => console.log('Audio blocked (autoplay):', e));
                }}).catch(error => {{
                    // Autoplay bị chặn. Cần tương tác người dùng.
                    console.log('Autoplay blocked, waiting for interaction.');
                }});
            }}
        }}, {{once: true}});
        
        // Gắn sự kiện tương tác để play/unmute (cần thiết cho mobile và desktop có âm thanh)
        document.addEventListener('click', handleInteraction, {{once: true}});
        document.addEventListener('touchstart', handleInteraction, {{once: true}});
        
        // Kết thúc intro khi video kết thúc
        vid.addEventListener('ended', finishIntro);
        
        // Cơ chế dừng dự phòng sau 9 giây
        setTimeout(finishIntro, 9000); 

        </script>
    </body>
    </html>
    """
    components.html(intro_html, height=window_height, scrolling=False)


# ========== TRANG CHÍNH ==========

def main_page(is_mobile=False):
    hide_streamlit_ui()
    st.markdown(f"""
    <style>
    /* ... CSS cho trang chính ... */
    html, body, .stApp {{
        background: black;
        height: 100vh;
    }}
    </style>
    """, unsafe_allow_html=True)

    # Hiển thị nội dung trang chính ở đây
    st.markdown(f"""
    <div style="color: white; text-align: center; padding-top: 20%;">
        <h1>Chào mừng đến với Trang Chính!</h1>
        <p>Phiên bản: {'Mobile' if is_mobile else 'PC'}</p>
        <button onclick="
            // Xóa query parameter và reload trang chính
            const currentUrl = new URL(window.parent.location.href);
            currentUrl.searchParams.delete('intro_finished');
            window.parent.location.href = currentUrl.toString();
        ">Chạy lại Intro</button>
    </div>
    """, unsafe_allow_html=True)
    
# ========== LUỒNG CHÍNH ==========

hide_streamlit_ui()

# 1. Xác định thiết bị
if "is_mobile" not in st.session_state:
    ua_string = st_javascript("window.navigator.userAgent;", key="ua_key")
    if ua_string:
        ua = parse(ua_string)
        st.session_state.is_mobile = not ua.is_pc
        st.rerun() 
    else:
        st.info("Đang xác định thiết bị...")
        time.sleep(1) 
        st.stop()

# 2. Quản lý trạng thái Intro
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

# Kiểm tra query parameter mới bằng st.query_params
if 'intro_finished' in st.query_params and st.query_params['intro_finished'] == 'true':
    st.session_state.intro_done = True
    # Xóa param để tránh lặp vô tận sau khi đã chuyển trạng thái
    del st.query_params['intro_finished'] 
    st.rerun()

# 3. Hiển thị Intro hoặc Trang Chính
if not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
else:
    main_page(st.session_state.is_mobile)
