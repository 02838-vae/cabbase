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

# Cấu hình hiệu ứng broken glass
GLASS_ROWS = 10
GLASS_COLS = 10
BREAK_DURATION = 1.5  # Thời gian hiệu ứng vỡ kính (giây)

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


# ========== MÀN HÌNH INTRO VỚI HIỆU ỨNG BROKEN GLASS ==========
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
    <html>
    <head>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
        <style>
        html, body {{
            margin: 0; padding: 0;
            overflow: hidden;
            background: black;
            height: 100%;
        }}
        #pre-load-bg {{ display: none; background-image: url("data:image/jpeg;base64,{bg_b64}"); }}
        
        video {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
            object-fit: cover; z-index: 1;
        }}
        
        audio {{ display: none; }}
        
        #intro-text {{
            position: absolute; 
            top: 8%;
            left: 50%; 
            transform: translate(-50%, 0);
            width: 90vw; text-align: center; color: #f8f4e3;
            font-size: clamp(22px, 6vw, 60px); font-weight: bold; font-family: 'Playfair Display', serif;
            background: linear-gradient(120deg, #e9dcb5 20%, #fff9e8 40%, #e9dcb5 60%);
            background-size: 200%; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            text-shadow: 0 0 15px rgba(255,255,230,0.4);
            animation: lightSweep 6s linear infinite, fadeInOut 6s ease-in-out forwards;
            line-height: 1.2; word-wrap: break-word; z-index: 10;
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
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
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
            overflow: hidden;
        }}

        #black-fade {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: black; opacity: 1; z-index: 40;
            transition: opacity 1s ease-in-out; pointer-events: none;
        }}

        </style>
    </head>
    <body>
        <div id="pre-load-bg"></div>
        
        <video id='introVid' autoplay muted playsinline>
            <source src='data:video/mp4;base64,{video_b64}' type='video/mp4'>
        </video>
        
        <audio id='flySfx'> 
            <source src='data:audio/mp3;base64,{audio_b64}' type='audio/mp3'>
        </audio>
        
        <div id='intro-text'>KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>

        <div id='broken-glass-container'></div>
        
        <div id='black-fade'></div>

        <script>
        const ROWS = {GLASS_ROWS};
        const COLS = {GLASS_COLS};
        const BREAK_DURATION = {BREAK_DURATION};
        
        const vid = document.getElementById('introVid');
        const audio = document.getElementById('flySfx');
        const blackFade = document.getElementById('black-fade');
        const glassContainer = document.getElementById('broken-glass-container');
        let ended = false;

        // Tạo các mảnh vỡ
        function createBrokenPieces() {{
            const pieceWidth = 100 / COLS;
            const pieceHeight = 100 / ROWS;
            
            for (let row = 0; row < ROWS; row++) {{
                for (let col = 0; col < COLS; col++) {{
                    const piece = document.createElement('div');
                    piece.className = 'broken-piece';
                    
                    piece.style.left = (col * pieceWidth) + '%';
                    piece.style.top = (row * pieceHeight) + '%';
                    piece.style.width = pieceWidth + '%';
                    piece.style.height = pieceHeight + '%';
                    
                    piece.style.backgroundPosition = 
                        (-col * (100 / COLS)) + '% ' + 
                        (-row * (100 / ROWS)) + '%';
                    
                    glassContainer.appendChild(piece);
                }}
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

        function finishIntro() {{
            if (ended) return;
            ended = true;
            
            // Ẩn video, hiện ảnh tĩnh với broken glass effect
            vid.style.opacity = 0;
            glassContainer.classList.add('active');
            
            // Bắt đầu hiệu ứng vỡ kính
            setTimeout(() => {{
                breakGlass();
            }}, 100);
            
            // Fade to black sau khi vỡ xong
            setTimeout(() => {{
                blackFade.style.opacity = 1;
            }}, BREAK_DURATION * 1000 + 300);
            
            // Reload trang
            setTimeout(() => {{
                window.parent.postMessage({{type: 'intro_done'}}, '*');
            }}, BREAK_DURATION * 1000 + 1300);
        }}

        // Khởi tạo các mảnh vỡ
        createBrokenPieces();

        // Logic play video/audio
        vid.addEventListener('canplay', () => {{
            vid.play().catch(() => console.log('Autoplay bị chặn'));
            blackFade.style.opacity = 0; 
        }});
        
        vid.addEventListener('play', () => {{
            audio.volume = 1.0;
            audio.currentTime = 0;
            audio.play().catch(() => console.log('Autoplay âm thanh bị chặn'));
        }});
        
        document.addEventListener('click', () => {{
            vid.muted = false;
            vid.play();
            audio.volume = 1.0;
            audio.currentTime = 0;
            audio.play().catch(()=>{{}}); 
            blackFade.style.opacity = 0; 
        }}, {{once:true}});

        vid.addEventListener('ended', finishIntro);
        setTimeout(finishIntro, 9000); 

        blackFade.style.opacity = 1;

        </script>
    </body>
    </html>
    """
    components.html(intro_html, height=800, scrolling=False)


# ========== TRANG CHÍNH ==========

def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    try:
        with open(bg, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError as e:
        st.error(f"Lỗi: Không tìm thấy file tài nguyên: {e.filename}")
        st.stop()

    st.markdown(f"""
    <style>
    html, body, .stApp {{
        height: 100vh !important;
        background: 
            linear-gradient(to bottom, rgba(255, 235, 200, 0.25) 0%, rgba(160, 130, 90, 0.35) 50%, rgba(90, 70, 50, 0.5) 100%),
            url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed !important;
        background-size: cover !important;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
        position: relative;
        filter: brightness(1.05) contrast(1.1) saturate(1.05);
        animation: fadeInBg 0.5s ease-in-out forwards; 
    }}
    .stApp::after {{
        content: "";
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-image: url("https://www.transparenttextures.com/patterns/noise-pattern-with-subtle-cross-lines.png");
        opacity: 0.09;
        mix-blend-mode: multiply;
    }}
    @keyframes fadeInBg {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    .welcome {{
        position: absolute;
        top: 8%;
        width: 100%;
        text-align: center;
        font-size: clamp(30px, 5vw, 65px);
        color: #fff5d7;
        font-family: 'Playfair Display', serif;
        text-shadow: 0 0 18px rgba(0,0,0,0.65), 0 0 30px rgba(255,255,180,0.25);
        background: linear-gradient(120deg, #f3e6b4 20%, #fff7d6 40%, #f3e6b4 60%);
        background-size: 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: textLight 10s linear infinite, fadeIn 1s ease-in-out forwards; 
        letter-spacing: 2px;
        z-index: 3;
    }}
    @keyframes textLight {{
        0% {{ background-position: 200% 0%; }}
        100% {{ background-position: -200% 0%; }}
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: scale(0.97); }}
        to {{ opacity: 1; transform: scale(1); }}
    }}
    </style>

    <div class="welcome">TỔ BẢO DƯỠNG SỐ 1</div>
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

if not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
    
    st.markdown("""
    <script>
    window.addEventListener("message", (event) => {
        if (event.data.type === "intro_done") {
            window.parent.location.reload(); 
        }
    });
    </script>
    """, unsafe_allow_html=True)

    time.sleep(15) 
    st.session_state.intro_done = True
    st.rerun()

else:
    main_page(st.session_state.is_mobile)
