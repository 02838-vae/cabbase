import streamlit as st
import base64
import time
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

# ========== CẤU HÌNH ==========
st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
SFX = "plane_fly.mp3"


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


# ========== XÁC ĐỊNH THIẾT BỊ ==========
if "is_mobile" not in st.session_state:
    ua_string = st_javascript("window.navigator.userAgent;")
    if ua_string:
        ua = parse(ua_string)
        st.session_state.is_mobile = not ua.is_pc
        st.rerun()
    else:
        st.info("Đang xác định thiết bị...")
        # st.stop() được thay thế bằng cách hiển thị thông báo chờ
        # và cho phép Streamlit tiếp tục chạy.
        # Nếu đang ở môi trường local, bạn có thể cần chạy lại thủ công.
        pass


# ========== MÀN HÌNH INTRO VỚI HIỆU ỨNG TAN VỠ ==========
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    
    # Đọc file và encode base64
    try:
        with open(video_file, "rb") as f:
            video_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        st.error(f"Không tìm thấy file video: {video_file}. Vui lòng kiểm tra lại đường dẫn.")
        st.stop()

    try:
        with open(SFX, "rb") as a:
            audio_b64 = base64.b64encode(a.read()).decode()
    except FileNotFoundError:
        audio_b64 = "" # Xử lý nếu không có file audio

    intro_html = f"""
    <html>
    <head>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <style>
        html, body {{
            margin: 0; padding: 0;
            overflow: hidden;
            background: black;
            height: 100%;
        }}
        #shattered-container {{
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            z-index: 100;
            display: grid;
            grid-template-columns: repeat(20, 1fr);
            grid-template-rows: repeat(20, 1fr);
            transition: opacity 0.5s ease;
            pointer-events: none;
        }}
        .shattered-piece {{
            /* SỬ DỤNG HÌNH NỀN TỪ VIDEO/ẢNH ĐỂ CÓ MẢNH VỠ */
            background-image: url("data:video/mp4;base64,{video_b64}");
            background-repeat: no-repeat;
            opacity: 0;
            transform: scale(1) translate(0, 0);
        }}
        
        video {{
            position: absolute;
            top: 0; left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: opacity 0.5s;
        }}
        audio {{ display: none; }}
        #intro-text {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
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
            z-index: 2;
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
        #fade {{
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: black;
            opacity: 0;
            transition: opacity 1.5s ease-in-out;
            z-index: 1;
        }}
        </style>
    </head>
    <body>
        <video id='introVid' autoplay muted playsinline>
            <source src='data:video/mp4;base64,{video_b64}' type='video/mp4'>
        </video>
        <audio id='flySfx'>
            <source src='data:audio/mp3;base64,{audio_b64}' type='audio/mp3'>
        </audio>
        <div id='intro-text'>KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id='shattered-container'></div>
        <div id='fade'></div>
        <script>
        const container = document.getElementById('shattered-container');
        const video = document.getElementById('introVid');
        const audio = document.getElementById('flySfx');
        const fade = document.getElementById('fade');
        const COLS = 20;
        const ROWS = 20;
        let ended = false;
        
        // Tạo các mảnh vỡ
        for (let i = 0; i < COLS * ROWS; i++) {{
            const piece = document.createElement('div');
            piece.className = 'shattered-piece';
            
            const col = i % COLS;
            const row = Math.floor(i / COLS);
            const x_pos = (col / COLS) * 100;
            const y_pos = (row / ROWS) * 100;
            const size_x = 100 / COLS;
            const size_y = 100 / ROWS;

            piece.style.cssText = `
                background-position: ${{x_pos}}% ${{y_pos}}%; /* ĐÃ SỬA LỖI ESCAPE */
                background-size: ${{COLS * 100}}% ${{ROWS * 100}}%;
                width: ${{size_x}}%;
                height: ${{size_y}}%;
                position: absolute;
                top: ${{row * size_y}}%; /* ĐÃ SỬA LỖI ESCAPE */
                left: ${{col * size_x}}%; /* ĐÃ SỬA LỖI ESCAPE */
            `;
            container.appendChild(piece);
        }}

        const pieces = document.querySelectorAll('.shattered-piece');
        
        function activateShatter() {{
            if (ended) return; // Tránh kích hoạt nhiều lần

            // Ẩn video/text
            video.style.opacity = 0;
            document.getElementById('intro-text').style.opacity = 0;

            // Kích hoạt hiển thị và hiệu ứng cho các mảnh vỡ
            container.style.opacity = 1;

            pieces.forEach((piece, index) => {{
                // Random vị trí di chuyển và xoay
                const randX = (Math.random() - 0.5) * window.innerWidth * 1.5;
                const randY = (Math.random() - 0.5) * window.innerHeight * 1.5;
                const randRot = (Math.random() - 0.5) * 720;
                const delay = Math.random() * 0.3; // Độ trễ ngẫu nhiên

                piece.style.transition = `transform 1s ease-out ${{delay}}s, opacity 1s ease-out ${{delay}}s`;
                piece.style.opacity = 1;

                // Áp dụng hiệu ứng "tan vỡ"
                setTimeout(() => {{
                    piece.style.transform = `translate(${{randX}}px, ${{randY}}px) rotate(${{randRot}}deg) scale(0.2)`;
                    piece.style.opacity = 0;
                }}, 50); 
            }});

            // Sau khi hiệu ứng tan vỡ kết thúc (ví dụ: 1.5 giây)
            setTimeout(() => {{
                finishIntro();
            }}, 1500);
        }}

        function finishIntro() {{
            if (ended) return;
            ended = true;
            fade.style.opacity = 1;
            setTimeout(() => {{
                // Gửi message và kích hoạt reload Streamlit thông qua query param
                window.parent.location.href = window.parent.location.href.split('?')[0] + '?set_intro_done=true';
            }}, 1000); 
        }}

        video.addEventListener('canplay', () => {{
            video.play().catch(() => console.log('Autoplay bị chặn'));
        }});
        video.addEventListener('play', () => {{
            audio.volume = 1.0;
            audio.currentTime = 0;
            audio.play().catch(() => console.log('Autoplay âm thanh bị chặn'));
        }});
        document.addEventListener('click', () => {{
            video.muted = false;
            video.play();
            audio.volume = 1.0;
            audio.currentTime = 0;
            audio.play().catch(()=>{{}});
        }}, {{once:true}});
        
        // Kích hoạt tan vỡ khi video kết thúc
        video.addEventListener('ended', activateShatter); 
        // Kích hoạt tan vỡ sau 9 giây nếu video không kết thúc (dự phòng)
        setTimeout(activateShatter, 9000); 
        </script>
    </body>
    </html>
    """
    components.html(intro_html, height=800, scrolling=False)


# ========== TRANG CHÍNH ==========
def main_page(is_mobile=False):
    hide_streamlit_ui()
    
    # Đọc file và encode base64
    try:
        bg = BG_MOBILE if is_mobile else BG_PC
        with open(bg, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        st.error(f"Không tìm thấy file hình nền: {bg}. Vui lòng kiểm tra lại đường dẫn.")
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
        animation: fadeInBg 1.5s ease-in-out forwards;
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
        animation: textLight 10s linear infinite, fadeIn 2s ease-in-out forwards;
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
    
    /* STYLE CHO NÚT XEM LẠI */
    .stButton>button {{
        background-color: rgba(255, 255, 255, 0.1);
        color: #f3e6b4;
        border: 2px solid #f3e6b4;
        border-radius: 12px;
        padding: 10px 20px;
        font-size: 18px;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.2);
    }}
    .stButton>button:hover {{
        background-color: rgba(255, 255, 255, 0.3);
        box-shadow: 0 0 25px rgba(255, 255, 255, 0.4);
        transform: scale(1.05);
    }}
    </style>


    <div class="welcome">TỔ BẢO DƯỠNG SỐ 1</div>
    """, unsafe_allow_html=True)
    
    # Đặt nút ở giữa màn hình (hoặc vị trí tùy chọn)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown(
            """
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 10;">
            """, 
            unsafe_allow_html=True
        )
        if st.button("▶️ Xem Lại Intro"):
            st.session_state.intro_done = False
            st.rerun()
        st.markdown(
            "</div>", 
            unsafe_allow_html=True
        )


# ========== LUỒNG CHÍNH ==========

if "is_mobile" not in st.session_state:
    st.stop() # Chờ xác định thiết bị

if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

if not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
    
    # Xử lý query param để chuyển trạng thái từ JavaScript
    query_params = st.experimental_get_query_params()
    if 'set_intro_done' in query_params and query_params['set_intro_done'][0] == 'true':
        st.session_state.intro_done = True
        # Xóa query param để tránh lặp lại
        st.experimental_set_query_params()
        st.rerun()
    
    st.stop() # Dừng lại và chờ tín hiệu từ JavaScript

else:
    main_page(st.session_state.is_mobile)

