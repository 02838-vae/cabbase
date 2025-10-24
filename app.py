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

# File ảnh nền của trang chính
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"

st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

# ========== ẨN UI STREAMLIT ==========

def hide_streamlit_ui():
    """Ẩn các thành phần UI mặc định của Streamlit và thiết lập layout toàn màn hình."""
    st.markdown("""
    <style>
    /* Ẩn các thành phần không cần thiết */
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
    }
    /* Thiết lập layout toàn màn hình */
    .stApp, .main, .block-container {
        padding: 0 !important;
        margin: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        overflow: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ========== MÀN HÌNH INTRO ==========
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    bg_file = BG_MOBILE if is_mobile else BG_PC
    
    try:
        # Mã hóa các file thành Base64 để nhúng vào HTML
        with open(video_file, "rb") as f:
            video_b64 = base64.b64encode(f.read()).decode()
        with open(SFX, "rb") as a:
            audio_b64 = base64.b64encode(a.read()).decode()
        with open(bg_file, "rb") as b:
            bg_b64 = base64.b64encode(b.read()).decode()
            
    except FileNotFoundError as e:
        st.error(f"Lỗi: Không tìm thấy file tài nguyên. Vui lòng kiểm tra: {e.filename}")
        st.stop()

    intro_html = f"""
    <html>
    <head>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap');
        html, body {{
            margin: 0; padding: 0;
            overflow: hidden;
            background: black;
            height: 100%;
        }}
        /* Lớp nền chính để lộ ra */
        #main-bg {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed;
            background-size: cover;
            opacity: 0; /* Ẩn ban đầu */
            z-index: 10;
        }}
        video {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;
            z-index: 20;
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
            line-height: 1.2; word-wrap: break-word; z-index: 30;
        }}
        @keyframes lightSweep {{ 0% {{ background-position: 200% 0%; }} 100% {{ background-position: -200% 0%; }} }}
        @keyframes fadeInOut {{ 0% {{ opacity: 0; }} 20% {{ opacity: 1; }} 80% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}

        /* Lớp phủ Reveal */
        #reveal-overlay {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: black; 
            z-index: 50;
            transform: scale(1); /* Bắt đầu với kích thước đầy đủ */
            opacity: 1;
            transition: transform 1.2s cubic-bezier(0.65, 0.05, 0.36, 1), opacity 0.5s ease; 
            pointer-events: none;
        }}
        .reveal-active #reveal-overlay {{
            transform: scale(0); /* Kết thúc với kích thước bằng 0 */
            border-radius: 50%;
            opacity: 0;
        }}
        /* Ẩn video/text khi hiệu ứng reveal bắt đầu */
        .reveal-active video, .reveal-active #intro-text {{
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        
        /* Thông báo bật âm thanh */
        #unmute-prompt {{
            position: absolute; bottom: 10px; right: 10px; 
            padding: 8px 12px;
            background: rgba(255, 255, 255, 0.2); 
            color: white; 
            border-radius: 5px; 
            cursor: pointer;
            z-index: 40;
            font-size: 0.8em;
            display: block; /* Mặc định hiển thị */
            opacity: 0.9;
        }}
        .active-audio #unmute-prompt {{
            display: none; /* Ẩn khi âm thanh đã được bật */
        }}

        </style>
    </head>
    <body>
        <div id='main-bg'></div>
        <video id='introVid' autoplay muted playsinline>
            <source src='data:video/mp4;base64,{video_b64}' type='video/mp4'>
        </video>
        <audio id='flySfx'> <source src='data:audio/mp3;base64,{audio_b64}' type='audio/mp3'></audio>
        <div id='intro-text'>KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>

        <div id='unmute-prompt'>🔊 Click/Chạm để bật âm thanh</div>

        <div id='reveal-overlay'></div>

        <script>
        const vid = document.getElementById('introVid');
        const audio = document.getElementById('flySfx');
        const mainBg = document.getElementById('main-bg');
        const unmutePrompt = document.getElementById('unmute-prompt');
        let ended = false;

        function finishIntro() {{
            if (ended) return;
            ended = true;
            
            // 1. Dừng video/audio
            vid.pause();
            audio.pause();
            
            // 2. Hiện nền trang chính
            mainBg.style.opacity = 1;

            // 3. Kích hoạt hiệu ứng reveal (thu nhỏ lớp phủ đen)
            document.body.classList.add('reveal-active');
            
            // 4. Chuyển trạng thái Streamlit sau khi hiệu ứng kết thúc (1.5s > 1.2s của CSS transition)
            setTimeout(() => {{
                // Thay đổi URL để Streamlit RERUN và chuyển sang trang chính
                window.parent.location.search = '?intro_completed=true';
            }}, 1500); 
        }}

        function handleAudioActivation() {{
            if (document.body.classList.contains('active-audio')) return;

            // Bỏ chế độ muted cho video và phát âm thanh SFX
            vid.muted = false;
            vid.play().catch(()=>{{}}); /* <-- Đã sửa lỗi: Thêm thêm cặp ngoặc nhọn */
            audio.volume = 1.0;
            audio.currentTime = 0;
            audio.play().catch(()=>{{}}); /* <-- Đã sửa lỗi: Thêm thêm cặp ngoặc nhọn */

            document.body.classList.add('active-audio');
        }}

        // Logic Play Video/Audio
        // Khi video đã sẵn sàng, fade out lớp phủ đen ban đầu (nếu có)
        vid.addEventListener('canplay', () => {{
             // Đảm bảo video được play. (Thường sẽ tự play do muted)
             vid.play().catch(() => console.log('Autoplay video bị chặn'));
        }});
        
        // Kích hoạt âm thanh khi người dùng click/tap bất kỳ đâu
        document.addEventListener('click', () => {{
            handleAudioActivation();
        }}, {{once:true}}); /* <-- Đã sửa lỗi: Thêm thêm cặp ngoặc nhọn */

        // Kết thúc khi video kết thúc hoặc sau timeout 9 giây
        vid.addEventListener('ended', finishIntro);
        setTimeout(finishIntro, 9000); 

        </script>
    </body>
    </html>
    """
    components.html(intro_html, height=1000, scrolling=False)


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
    /* ... (CSS trang chính giữ nguyên) ... */
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

# 1. Xác định thiết bị (Giữ nguyên)
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

# 2. Xử lý trạng thái Intro
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
    
# Kiểm tra Query Parameter để chuyển trạng thái từ JS (sau hiệu ứng Reveal)
query_params = st.experimental_get_query_params()
if 'intro_completed' in query_params and query_params['intro_completed'][0] == 'true':
    st.session_state.intro_done = True
    # Xóa query param để URL sạch và lần refresh sau vẫn thấy intro
    st.experimental_set_query_params(intro_completed=None)
    st.rerun() 


if not st.session_state.intro_done:
    # HIỂN THỊ MÀN HÌNH INTRO
    intro_screen(st.session_state.is_mobile)
    
    # Dừng luồng cho đến khi Query Parameter thay đổi bởi JavaScript (Sau hiệu ứng reveal)
    st.stop() 

else:
    # HIỂN THỊ TRANG CHÍNH
    main_page(st.session_state.is_mobile)
