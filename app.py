import streamlit as st
import base64
import time
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

# ========== CẤU HÌNH ==========
st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

# Vui lòng đảm bảo các file này tồn tại trong cùng thư mục với file python
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

# ========== KIỂM TRA SỰ TỒN TẠI CỦA FILE ==========
def check_files():
    files_to_check = [VIDEO_PC, VIDEO_MOBILE, BG_PC, BG_MOBILE, SFX]
    missing_files = [f for f in files_to_check if not __import__('os').path.exists(f)]
    if missing_files:
        st.error(f"Lỗi: Không tìm thấy các file sau, vui lòng đảm bảo chúng ở cùng thư mục: {', '.join(missing_files)}")
        st.stop()
    return True

# ========== MÀN HÌNH INTRO ==========
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    with open(video_file, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()
    with open(SFX, "rb") as a:
        audio_b64 = base64.b64encode(a.read()).decode()

    top_pos = "50%" if is_mobile else "35%" # Điều chỉnh vị trí chữ trên PC

    intro_html = f"""
    <html>
    <head>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
        <style>
        html, body {{
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            background: black;
            overflow: hidden;
            font-family: 'Playfair Display', serif;
        }}
        #video-container {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }}
        video {{
            width: 100%;
            height: 100%;
            object-fit: cover; /* Đây là thuộc tính giúp video luôn full màn hình */
            object-position: center center;
        }}
        audio {{ display: none; }}
        #intro-text {{
            position: absolute;
            top: {top_pos};
            left: 50%;
            transform: translate(-50%, -50%);
            width: 90vw;
            text-align: center;
            color: #f8f4e3;
            font-size: clamp(24px, 6vw, 60px);
            font-weight: bold;
            background: linear-gradient(120deg, #f5e9c8 20%, #fff9e8 40%, #f5e9c8 60%);
            background-size: 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 15px rgba(255,255,230,0.4);
            animation: lightSweep 6s linear infinite, fadeInOut 6s ease-in-out forwards;
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
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: black;
            opacity: 0;
            transition: opacity 1.5s ease-in-out;
            pointer-events: none; /* Cho phép click xuyên qua */
        }}
        </style>
    </head>
    <body>
        <div id="video-container">
            <video id='introVid' autoplay muted playsinline>
                <source src='data:video/mp4;base64,{video_b64}' type='video/mp4'>
            </video>
        </div>
        <audio id='flySfx'>
            <source src='data:audio/mp3;base64,{audio_b64}' type='audio/mp3'>
        </audio>
        <div id='intro-text'>KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id='fade'></div>
        <script>
        const vid = document.getElementById('introVid');
        const audio = document.getElementById('flySfx');
        const fade = document.getElementById('fade');
        let ended = false;
        function finishIntro() {{
            if (ended) return;
            ended = true;
            fade.style.opacity = 1;
            setTimeout(() => {{
                // Gửi thông điệp tới Streamlit để biết intro đã xong
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: true}}, '*');
            }}, 1000);
        }}

        // Cố gắng phát video khi sẵn sàng
        vid.addEventListener('canplay', () => {{
            vid.play().catch(() => console.log('Autoplay bị trình duyệt chặn. Cần người dùng tương tác.'));
        }});

        // Khi video bắt đầu chạy, phát âm thanh
        vid.addEventListener('play', () => {{
            audio.volume = 1.0;
            audio.currentTime = 0;
            audio.play().catch(() => console.log('Autoplay âm thanh bị chặn.'));
        }});

        // Bật âm thanh khi người dùng click lần đầu
        document.body.addEventListener('click', () => {{
            if(vid.muted) {{
               vid.muted = false;
            }}
            vid.play(); // Đảm bảo video chạy khi click
            audio.play();
        }}, {{once:true}});

        vid.addEventListener('ended', finishIntro);
        setTimeout(finishIntro, 9000); // Timeout dự phòng
        </script>
    </body>
    </html>
    """
    intro_finished = components.html(intro_html, height=None)
    if intro_finished:
        st.session_state.intro_done = True
        st.rerun()

# ========== TRANG CHÍNH ==========
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    with open(bg, "rb") as f:
        bg_b64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <head>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
    </head>
    <style>
    .stApp {{
        background:
            linear-gradient(to bottom, rgba(245, 235, 220, 0.15), rgba(180, 160, 135, 0.35)),
            url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed !important;
        background-size: cover !important;
        position: relative;
        filter: sepia(0.3) brightness(1.05) contrast(1.05) saturate(0.95);
    }}
    .stApp::after {{
        content: "";
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-image: url("https://www.transparenttextures.com/patterns/paper-fibers.png");
        opacity: 0.15;
        mix-blend-mode: overlay;
        pointer-events: none;
    }}
    .welcome {{
        position: absolute;
        top: 10%;
        left: 50%;
        transform: translateX(-50%);
        width: 100%;
        text-align: center;
        font-size: clamp(32px, 5.5vw, 65px);
        font-family: 'Playfair Display', serif;
        text-shadow: 0 2px 20px rgba(0,0,0,0.5);
        background: linear-gradient(270deg, #ffe8a3, #ffca7f, #f9d58e, #fff5c7);
        background-size: 600% 600%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 8s ease infinite, fadeIn 2s ease-in-out forwards;
        letter-spacing: 2.5px;
        z-index: 3;
    }}
    @keyframes gradientShift {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateX(-50%) scale(0.97); }}
        to {{ opacity: 1; transform: translateX(-50%) scale(1); }}
    }}
    </style>
    <div class="welcome">TỔ BẢO DƯỠNG SỐ 1</div>
    """, unsafe_allow_html=True)

# ========== LUỒNG CHÍNH ==========
if __name__ == "__main__":
    # 1. Kiểm tra sự tồn tại của tất cả các file cần thiết ngay từ đầu
    check_files()
    hide_streamlit_ui()

    # 2. Luồng khởi tạo để xác định thiết bị một lần duy nhất
    if "initialized" not in st.session_state:
        # Lấy thông tin user agent từ client bằng javascript
        ua_string = st_javascript("window.navigator.userAgent;")

        if ua_string:
            # Khi JS đã trả về user agent, tiến hành phân tích
            ua = parse(ua_string)
            st.session_state.is_mobile = not ua.is_pc
            st.session_state.intro_done = False
            st.session_state.initialized = True
            # Chạy lại script để vào luồng chính
            st.rerun()
        else:
            # Lần đầu tiên chạy, JS chưa kịp trả về giá trị.
            # Hiển thị thông báo và dừng thực thi script.
            # Streamlit sẽ tự động chạy lại khi giá trị JS được trả về.
            st.info("Đang khởi tạo, vui lòng chờ...")
            st.stop()

    # 3. Luồng chính của ứng dụng sau khi đã khởi tạo
    if not st.session_state.get('intro_done', False):
        intro_screen(st.session_state.is_mobile)
    else:
        main_page(st.session_state.is_mobile)

