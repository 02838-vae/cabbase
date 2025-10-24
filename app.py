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

    intro_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
        <style>
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
        
        /* Debug info */
        #debug {{
            position: fixed;
            top: 10px;
            left: 10px;
            background: rgba(255,255,255,0.8);
            padding: 10px;
            font-family: monospace;
            font-size: 12px;
            z-index: 9999;
            max-width: 300px;
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
            background: #000;
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

        </style>
    </head>
    <body>
        <div id="debug">Đang tải video...</div>
        
        <div id="container">
            <div id="main-page-bg"></div>
            
            <video id='introVid' muted playsinline webkit-playsinline>
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
        const revealOverlay = document.getElementById('reveal-overlay');
        const introText = document.getElementById('intro-text');
        const mainText = document.getElementById('main-text');
        const mainBg = document.getElementById('main-page-bg');
        const debugDiv = document.getElementById('debug');
        let ended = false;
        let debugLog = [];

        function log(msg) {{
            console.log(msg);
            debugLog.push(msg);
            debugDiv.innerHTML = debugLog.slice(-10).join('<br>');
        }}

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
                    
                    const bgX = -(col * pieceWidth);
                    const bgY = -(row * pieceHeight);
                    piece.style.backgroundPosition = bgX + '% ' + bgY + '%';
                    piece.style.backgroundSize = (GLASS_COLS * 100) + '% ' + (GLASS_ROWS * 100) + '%';
                    
                    glassContainer.appendChild(piece);
                }}
            }}
        }}

        function createRevealGrid() {{
            for (let i = 0; i < REVEAL_GRID * REVEAL_GRID; i++) {{
                const tile = document.createElement('div');
                tile.className = 'reveal-tile';
                revealOverlay.appendChild(tile);
            }}
        }}

        function breakGlass() {{
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
            log('Starting reveal...');
            const tiles = document.querySelectorAll('.reveal-tile');
            const centerRow = Math.floor(REVEAL_GRID / 2);
            const centerCol = Math.floor(REVEAL_GRID / 2);
            
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
                                debugDiv.style.display = 'none';
                                log('Reveal complete!');
                            }}, 100);
                        }}
                    }}
                }});
            }});
        }}

        function finishIntro() {{
            if (ended) return;
            ended = true;
            log('Finishing intro...');
            
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
            
            setTimeout(() => {{
                window.parent.postMessage({{type: 'intro_done'}}, '*');
            }}, BREAK_DURATION * 1000 + REVEAL_DURATION * 1000 + 500);
        }}

        createBrokenPieces();
        createRevealGrid();

        log('Video element created');
        log('ReadyState: ' + vid.readyState);

        // Event listeners cho debug
        vid.addEventListener('loadstart', () => log('loadstart'));
        vid.addEventListener('loadedmetadata', () => log('loadedmetadata'));
        vid.addEventListener('loadeddata', () => log('loadeddata'));
        vid.addEventListener('canplay', () => log('canplay'));
        vid.addEventListener('canplaythrough', () => log('canplaythrough'));
        vid.addEventListener('playing', () => log('playing'));
        vid.addEventListener('pause', () => log('pause'));
        vid.addEventListener('error', (e) => log('ERROR: ' + e.message));
        vid.addEventListener('stalled', () => log('stalled'));
        vid.addEventListener('waiting', () => log('waiting'));

        // Thử play ngay
        setTimeout(() => {{
            log('Attempting autoplay...');
            vid.play().then(() => {{
                log('✓ Video playing!');
                audio.currentTime = 0;
                audio.volume = 1.0;
                audio.play().catch(e => log('Audio error: ' + e.message));
            }}).catch(e => {{
                log('✗ Autoplay failed: ' + e.message);
                log('Click màn hình để play!');
            }});
        }}, 100);

        // Click để play
        let clicked = false;
        document.addEventListener('click', function() {{
            if (!clicked) {{
                clicked = true;
                log('User clicked!');
                vid.muted = false;
                vid.play().then(() => {{
                    log('✓ Playing after click');
                    audio.currentTime = 0;
                    audio.volume = 1.0;
                    audio.play();
                }}).catch(e => log('Play error: ' + e.message));
            }}
        }});

        // Touch cho mobile
        document.addEventListener('touchstart', function() {{
            if (!clicked) {{
                clicked = true;
                log('User touched!');
                vid.muted = false;
                vid.play().then(() => {{
                    log('✓ Playing after touch');
                    audio.currentTime = 0;
                    audio.volume = 1.0;
                    audio.play();
                }}).catch(e => log('Play error: ' + e.message));
            }}
        }}, {{once: true}});

        vid.addEventListener('ended', finishIntro);
        setTimeout(finishIntro, 9000);

        </script>
    </body>
    </html>
    """
    components.html(intro_html, height=800, scrolling=False)


# ========== TRANG CHÍNH ==========

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

intro_screen(st.session_state.is_mobile)

st.markdown("""
<script>
window.addEventListener("message", (event) => {
    if (event.data.type === "intro_done") {
        console.log('Intro completed!');
    }
});
</script>
""", unsafe_allow_html=True)
