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
REVEAL_GRID = 8  # Lưới để reveal trang chính (8x8)
REVEAL_DURATION = 3.5  # Thời gian reveal trang chính (giây)

# ========== ẨN UI STREAMLIT ==========

def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
    }
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

    # Thêm timestamp để bypass cache
    cache_buster = int(time.time())

    intro_html = f"""
    <html>
    <head>
        <meta name='viewport' content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'>
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <meta http-equiv="Pragma" content="no-cache">
        <meta http-equiv="Expires" content="0">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
        <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html, body {{
            width: 100vw;
            height: 100vh;
            overflow: hidden;
            background: black;
            position: fixed;
            top: 0;
            left: 0;
        }}
        
        /* Background trang chính - FULL SCREEN */
        #main-page-bg {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: 
                linear-gradient(to bottom, rgba(255, 235, 200, 0.25) 0%, rgba(160, 130, 90, 0.35) 50%, rgba(90, 70, 50, 0.5) 100%),
                url("data:image/jpeg;base64,{bg_b64}") no-repeat center center;
            background-size: cover;
            background-position: center center;
            filter: brightness(1.05) contrast(1.1) saturate(1.05);
            z-index: 0;
            opacity: 0;
        }}
        
        #main-page-bg.visible {{
            opacity: 1;
        }}
        
        #main-page-bg::after {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: url("https://www.transparenttextures.com/patterns/noise-pattern-with-subtle-cross-lines.png");
            opacity: 0.09;
            mix-blend-mode: multiply;
        }}
        
        video {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            object-fit: cover;
            z-index: 1;
        }}
        
        audio {{ display: none; }}
        
        #intro-text {{
            position: fixed;
            top: 8%;
            left: 50%;
            transform: translate(-50%, 0);
            width: 90vw;
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
            word-wrap: break-word;
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

        /* Broken Glass Container */
        #broken-glass-container {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
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
            background-size: 100vw 100vh;
            background-position: center;
            overflow: hidden;
        }}

        /* Reveal Grid Overlay */
        #reveal-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            display: grid;
            grid-template-columns: repeat({REVEAL_GRID}, 1fr);
            grid-template-rows: repeat({REVEAL_GRID}, 1fr);
            z-index: 20;
            pointer-events: none;
        }}
        
        .reveal-tile {{
            background: black;
            opacity: 1;
            width: 100%;
            height: 100%;
        }}
        
        /* Text trang chính */
        #main-text {{
            position: fixed;
            top: 8%;
            left: 50%;
            transform: translate(-50%, 0);
            width: 90vw;
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

        </style>
    </head>
    <body>
        <!-- Background trang chính -->
        <div id="main-page-bg"></div>
        
        <video id='introVid' muted playsinline webkit-playsinline preload="auto">
            <source src='data:video/mp4;base64,{video_b64}?v={cache_buster}' type='video/mp4'>
        </video>
        
        <audio id='flySfx' preload="auto"> 
            <source src='data:audio/mp3;base64,{audio_b64}?v={cache_buster}' type='audio/mp3'>
        </audio>
        
        <div id='intro-text'>KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>

        <div id='broken-glass-container'></div>
        
        <!-- Reveal overlay -->
        <div id='reveal-overlay'></div>
        
        <!-- Text trang chính -->
        <div id='main-text'>TỔ BẢO DƯỠNG SỐ 1</div>

        <script>
        const GLASS_ROWS = {GLASS_ROWS};
        const GLASS_COLS = {GLASS_COLS};
        const BREAK_DURATION = {BREAK_DURATION};
        const REVEAL_GRID = {REVEAL_GRID};
        const REVEAL_DURATION = {REVEAL_DURATION};
        
        const vid = document.getElementById('introVid');
        const audio = document.getElementById('flySfx');
        const glassContainer = document.getElementById('broken-glass-container');
        const revealOverlay = document.getElementById('reveal-overlay');
        const introText = document.getElementById('intro-text');
        const mainText = document.getElementById('main-text');
        const mainBg = document.getElementById('main-page-bg');
        let ended = false;
        let videoStarted = false;

        // Xóa cache khi load
        if ('caches' in window) {{
            caches.keys().then(names => {{
                names.forEach(name => {{
                    caches.delete(name);
                }});
            }});
        }}

        // Tạo các mảnh vỡ
        function createBrokenPieces() {{
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
                    
                    piece.style.backgroundPosition = 
                        (-col * (100 / GLASS_COLS)) + '% ' + 
                        (-row * (100 / GLASS_ROWS)) + '%';
                    
                    glassContainer.appendChild(piece);
                }}
            }}
        }}

        // Tạo lưới reveal
        function createRevealGrid() {{
            for (let i = 0; i < REVEAL_GRID * REVEAL_GRID; i++) {{
                const tile = document.createElement('div');
                tile.className = 'reveal-tile';
                tile.dataset.index = i;
                revealOverlay.appendChild(tile);
            }}
        }}

        function breakGlass() {{
            const pieces = document.querySelectorAll('.broken-piece');
            
            pieces.forEach((piece, i) => {{
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
            const tiles = document.querySelectorAll('.reveal-tile');
            const centerRow = Math.floor(REVEAL_GRID / 2);
            const centerCol = Math.floor(REVEAL_GRID / 2);
            
            // Hiện background trang chính
            mainBg.classList.add('visible');
            
            // Fade in text trang chính
            gsap.to(mainText, {{
                opacity: 1,
                duration: 1,
                ease: "power2.inOut"
            }});
            
            // Tính khoảng cách từ mỗi ô đến trung tâm
            tiles.forEach((tile, index) => {{
                const row = Math.floor(index / REVEAL_GRID);
                const col = index % REVEAL_GRID;
                
                // Khoảng cách Manhattan từ trung tâm
                const distanceFromCenter = Math.abs(row - centerRow) + Math.abs(col - centerCol);
                
                // Delay tăng dần từ trung tâm ra ngoài
                const delay = distanceFromCenter * (REVEAL_DURATION / (REVEAL_GRID * 2));
                
                gsap.to(tile, {{
                    opacity: 0,
                    duration: 0.4,
                    delay: delay,
                    ease: "power2.inOut",
                    onComplete: function() {{
                        if (index === tiles.length - 1) {{
                            // Ô cuối cùng biến mất - xóa overlay
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
            
            console.log('Finishing intro...');
            
            // Ẩn video và intro text, hiện ảnh tĩnh với broken glass effect
            vid.style.opacity = 0;
            introText.style.display = 'none';
            glassContainer.classList.add('active');
            
            // Bắt đầu hiệu ứng vỡ kính
            setTimeout(() => {{
                breakGlass();
            }}, 100);
            
            // Sau khi vỡ xong, bắt đầu reveal trang chính
            setTimeout(() => {{
                glassContainer.style.opacity = 0;
                revealMainPage();
            }}, BREAK_DURATION * 1000 + 200);
            
            // Sau khi reveal hoàn tất, thông báo cho Streamlit
            setTimeout(() => {{
                window.parent.postMessage({{type: 'intro_done'}}, '*');
            }}, BREAK_DURATION * 1000 + REVEAL_DURATION * 1000 + 500);
        }}

        // Khởi tạo
        createBrokenPieces();
        createRevealGrid();

        // Force play video - CÁCH MỚI
        function tryPlayVideo() {{
            if (videoStarted) return;
            
            console.log('Attempting to play video...');
            const playPromise = vid.play();
            
            if (playPromise !== undefined) {{
                playPromise.then(() => {{
                    console.log('Video playing successfully');
                    videoStarted = true;
                    
                    // Play audio cùng lúc
                    audio.currentTime = 0;
                    audio.volume = 1.0;
                    audio.play().catch(err => console.log('Audio play failed:', err));
                }}).catch(err => {{
                    console.log('Video play failed:', err);
                    // Retry sau 100ms
                    setTimeout(tryPlayVideo, 100);
                }});
            }}
        }}

        // Multiple triggers để đảm bảo video chạy
        vid.addEventListener('loadedmetadata', () => {{
            console.log('Video metadata loaded');
            tryPlayVideo();
        }});

        vid.addEventListener('canplay', () => {{
            console.log('Video can play');
            tryPlayVideo();
        }});

        vid.addEventListener('loadeddata', () => {{
            console.log('Video data loaded');
            tryPlayVideo();
        }});

        // Force load
        vid.load();
        
        // Backup: Try play after 500ms
        setTimeout(tryPlayVideo, 500);
        
        // Click/Touch để unmute và force play
        const userInteract = () => {{
            console.log('User interaction detected');
            vid.muted = false;
            tryPlayVideo();
            audio.volume = 1.0;
            audio.currentTime = 0;
            audio.play().catch(() => {{}});
        }};
        
        document.addEventListener('click', userInteract, {{once: true}});
        document.addEventListener('touchstart', userInteract, {{once: true}});

        vid.addEventListener('ended', finishIntro);
        
        // Backup timeout
        setTimeout(() => {{
            if (!ended) {{
                console.log('Timeout trigger');
                finishIntro();
            }}
        }}, 9000);

        </script>
    </body>
    </html>
    """
    components.html(intro_html, height=800, scrolling=False)


# ========== TRANG CHÍNH - ĐƠN GIẢN HÓA ==========

def main_page(is_mobile=False):
    hide_streamlit_ui()
    st.markdown("""
    <style>
    html, body, .stApp {
        background: black;
        height: 100vh;
    }
    </style>
    """, unsafe_allow_html=True)


# ========== LUỒNG CHÍNH ==========

hide_streamlit_ui()

if "is_mobile" not in st.session_state:
    ua_string = st_javascript("window.navigator.userAgent;")
    if ua_string:
        ua = parse(ua_string)
        st.session_state.is_mobile = not ua.is_pc
        st.rerun() 
    else:
        st.info("Đang xác định thiết bị...")
        time.sleep(1) 
        st.stop()

if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

# Luôn hiển thị intro screen
intro_screen(st.session_state.is_mobile)

# Lắng nghe message từ intro
st.markdown("""
<script>
window.addEventListener("message", (event) => {
    if (event.data.type === "intro_done") {
        console.log('Intro completed!');
    }
});
</script>
""", unsafe_allow_html=True)
