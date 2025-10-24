import streamlit as st
import base64
import time
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components


# ========== CẤU HÌNH VÀ TÀI NGUYÊN ==========

VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
SFX = "plane_fly.mp3"

BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"

st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

# ========== ẨN UI STREAMLIT ==========

def hide_streamlit_ui():
    """Ẩn các phần tử UI mặc định của Streamlit."""
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


# ========== MÀN HÌNH INTRO (CÓ FADE OUT) ==========
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    bg_file = BG_MOBILE if is_mobile else BG_PC
    
    try:
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
        html, body {{ margin: 0; padding: 0; overflow: hidden; background: black; height: 100%; }}
        video {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; transition: opacity 0.3s ease-in-out; opacity: 1; }}
        #intro-text {{ position: absolute; top: 8%; left: 50%; transform: translate(-50%, 0); width: 90vw; text-align: center; color: #f8f4e3; font-size: clamp(22px, 6vw, 60px); font-weight: bold; font-family: 'Playfair Display', serif; background: linear-gradient(120deg, #e9dcb5 20%, #fff9e8 40%, #e9dcb5 60%); background-size: 200%; -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 15px rgba(255,255,230,0.4); animation: lightSweep 6s linear infinite, fadeInOut 6s ease-in-out forwards; line-height: 1.2; word-wrap: break-word; z-index: 10; }}
        @keyframes lightSweep {{ 0% {{ background-position: 200% 0%; }} 100% {{ background-position: -200% 0%; }} }}
        @keyframes fadeInOut {{ 0% {{ opacity: 0; }} 20% {{ opacity: 1; }} 80% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}
        
        /* ĐIỀU CHỈNH FADE-OUT: Màu nền chuyển từ trong suốt sang đen */
        #fade-overlay {{ 
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0); /* Khởi đầu trong suốt */
            opacity: 1; z-index: 40;
            transition: background-color 1.0s ease-in-out; /* Thời gian mờ dần */
            pointer-events: none;
        }}
        
        </style>
    </head>
    <body>
        <div id="pre-load-bg"></div>
        <video id='introVid' autoplay muted playsinline>
            <source src='data:video/mp4;base64,{video_b64}' type='video/mp4'>
        </video>
        <audio id='flySfx' style='display:none;'> <source src='data:audio/mp3;base64,{audio_b64}' type='audio/mp3'></audio>
        <div id='intro-text'>KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>

        <div id='fade-overlay'></div>


        <script>
        
        const vid = document.getElementById('introVid');
        const audio = document.getElementById('flySfx');
        const fadeOverlay = document.getElementById('fade-overlay');
        let ended = false;
        
        function finishIntro() {{
            if (ended) return;
            ended = true;
            
            // 1. Tắt video và âm thanh
            vid.style.opacity = 0; 
            audio.volume = 0; 
            
            // 2. Kích hoạt hiệu ứng mờ dần (Fade-out)
            fadeOverlay.style.backgroundColor = 'rgba(0, 0, 0, 1)'; // Chuyển sang màu đen

            // 3. Chuyển hướng sau khi hiệu ứng mờ dần hoàn tất (1000ms + 50ms dự phòng)
            setTimeout(() => {{
                const currentUrl = window.parent.location.href.split('#')[0];
                const separator = currentUrl.includes('?') ? '&' : '?';
                const newUrl = currentUrl.split('?')[0] + separator + 'intro_done_flag=true';
                window.parent.location.href = newUrl;
            }}, 1050); // Đợi 1.05 giây để fade out xong
        }}

        // Logic play video/audio
        vid.addEventListener('canplay', () => {{
            vid.play().catch(() => console.log('Autoplay bị chặn'));
            // fadeOverlay.style.backgroundColor = 'rgba(0, 0, 0, 0)'; // Đã đặt mặc định là 0
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
        }}, {{once:true}});

        // GỌI finishIntro KHI VIDEO KẾT THÚC
        vid.addEventListener('ended', finishIntro);
        // Timeout dự phòng
        setTimeout(finishIntro, 10000); 

        // Ngay khi load, bắt đầu từ màu đen, sau đó CSS transition về trong suốt khi canplay
        fadeOverlay.style.backgroundColor = 'rgba(0, 0, 0, 1)'; 

        // Nếu video đã sẵn sàng, fade in (mở màn hình)
        vid.addEventListener('canplay', () => {{
            fadeOverlay.style.backgroundColor = 'rgba(0, 0, 0, 0)';
        }});


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
    html, body, .stApp {{ height: 100vh !important; background: linear-gradient(to bottom, rgba(255, 235, 200, 0.25) 0%, rgba(160, 130, 90, 0.35) 50%, rgba(90, 70, 50, 0.5) 100%), url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed !important; background-size: cover !important; overflow: hidden !important; margin: 0 !important; padding: 0 !important; position: relative; filter: brightness(1.05) contrast(1.1) saturate(1.05); animation: fadeInBg 0.5s ease-in-out forwards; }}
    @keyframes fadeInBg {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    .welcome {{ position: absolute; top: 8%; width: 100%; text-align: center; font-size: clamp(30px, 5vw, 65px); color: #fff5d7; font-family: 'Playfair Display', serif; text-shadow: 0 0 18px rgba(0,0,0,0.65), 0 0 30px rgba(255,255,180,0.25); background: linear-gradient(120deg, #f3e6b4 20%, #fff7d6 40%, #f3e6b4 60%); background-size: 200%; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: textLight 10s linear infinite, fadeIn 1s ease-in-out forwards; letter-spacing: 2px; z-index: 3; }}
    </style>


    <div class="welcome">TỔ BẢO DƯỠNG SỐ 1</div>
    """, unsafe_allow_html=True)


# ========== LUỒNG CHÍNH ĐIỀU KHIỂN TRẠNG THÁI ==========

hide_streamlit_ui()

# --- Bước 1: Xác định thiết bị ---
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

# --- Bước 2: Thiết lập cờ intro ---
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

# --- Bước 3: Logic chuyển trạng thái dứt điểm ---

if not st.session_state.intro_done:
    query_params = st.query_params
    
    if query_params.get("intro_done_flag") == ["true"]:
        # Tải lại lần 1: Đã phát hiện video kết thúc qua tham số truy vấn
        
        # 1. Đặt cờ vĩnh viễn
        st.session_state.intro_done = True
        
        # 2. Yêu cầu trình duyệt chuyển hướng ngay lập tức đến URL sạch
        st.markdown(
            """
            <script>
            // Lấy URL cơ sở (không tham số truy vấn)
            const url = new URL(window.location.href);
            url.searchParams.delete('intro_done_flag');
            // Sử dụng window.parent.location.replace để chuyển hướng và tránh back
            window.parent.location.replace(url.toString());
            </script>
            """, 
            unsafe_allow_html=True
        )
        # Dừng luồng Streamlit, vì JS sẽ xử lý chuyển hướng (rerun)
        st.stop() 
        
    else:
        # Lần đầu tải trang: Chạy intro
        intro_screen(st.session_state.is_mobile)
        # Dừng luồng để chờ video kết thúc và JS chuyển hướng
        st.stop()

else:
    # Trạng thái intro_done = True, hiển thị trang chính
    main_page(st.session_state.is_mobile)
