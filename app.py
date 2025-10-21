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
        # Nếu chưa xác định được, hiển thị thông báo và dừng
        st.info("Đang xác định thiết bị...")
        # Sử dụng time.sleep thay vì st.stop() để tránh lỗi re-run vô tận trong một số môi trường
        time.sleep(0.1)
        st.session_state.is_mobile = False # Giả định để chạy tiếp nếu không xác định được

# Kiểm tra lại biến session state sau khi xử lý.
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = False


# ========== MÀN HÌNH INTRO - CÓ HIỆU ỨNG SHUTTER ĐÓNG ==========
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    with open(video_file, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()
    with open(SFX, "rb") as a:
        audio_b64 = base64.b64encode(a.read()).decode()

    intro_html = f"""
    <html>
    <head>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <style>
        html, body {{
            margin: 0 !important;
            padding: 0 !important;
            border: 0 !important;
            overflow: hidden !important;
            width: 100vw !important;
            height: 100vh !important;
            background: black !important;
        }}
        :root, iframe, div, section {{
            margin: 0 !important;
            padding: 0 !important;
            border: 0 !important;
        }}
        video {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            object-fit: cover;
            background: black;
            z-index: 1;
        }}
        audio {{ display: none; }}
        #intro-text {{
            position: absolute;
            top: 12%;
            left: 50%;
            transform: translateX(-50%);
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
        
        /* CSS CHO HIỆU ỨNG SHUTTER */
        .shutter {{
            position: fixed;
            left: 0;
            width: 100vw;
            height: 50vh; /* Mỗi thanh chiếm nửa màn hình */
            background: black; /* Màu màn trập: Đen */
            z-index: 3; /* Nằm trên video và text */
            /* Vị trí ban đầu: Đóng (che màn hình) */
            transform: translateY(0);
            transition: transform 1.5s ease-in-out; 
        }}
        #shutter-top {{
            top: 0;
        }}
        #shutter-bottom {{
            bottom: 0;
        }}

        /* Class để kích hoạt hiệu ứng MỞ màn trập (nếu muốn dùng lại) */
        /* Ở đây ta dùng hiệu ứng ĐÓNG ở Intro và MỞ ở Main, nhưng Streamlit buộc phải chuyển trang */
        /* Nên ta dùng hiệu ứng ĐÓNG để che đi và chuyển trang, sau đó Main sẽ hiển thị */
        /* Ở đây ta dùng hiệu ứng MỞ (trượt ra) để lộ ra video (vì video cũng đang chạy) */
        .shutter-close #shutter-top {{
            transform: translateY(-100%); /* Thanh trên trượt lên */
        }}
        .shutter-close #shutter-bottom {{
            transform: translateY(100%); /* Thanh dưới trượt xuống */
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

        <div id='shutter-top' class='shutter'></div>
        <div id='shutter-bottom' class='shutter'></div>
        
        <script>
        const vid = document.getElementById('introVid');
        const audio = document.getElementById('flySfx');
        const body = document.body;

        let ended = false;

        function finishIntro() {{
            if (ended) return;
            ended = true;

            // Kích hoạt hiệu ứng Shutter ĐÓNG (trượt ra để lộ nội dung chính)
            // LƯU Ý: Ở đây ta dùng hiệu ứng MỞ để lộ ra video đang chạy, sau đó chuyển trang.
            // Nếu bạn muốn hiệu ứng màn trập đóng lại bằng màu đen trước khi chuyển trang:
            // Chỉ cần để Shutter ở trạng thái MỞ ban đầu (trans: translateY(0)) 
            // và sau đó áp dụng class làm nó TRƯỢT VÀO.
            // Ở ví dụ này, ta dùng hiệu ứng màn trập MỞ (trượt ra) để làm lộ video đang chạy.

            // Giả sử ta muốn: Màn trập MỞ ra (trượt ra khỏi màn hình) để lộ video intro.
            // Để làm hiệu ứng ĐÓNG (che) lại trước khi chuyển trang, ta sẽ cần thêm một lớp phủ.
            
            // **THAY ĐỔI CƠ CHẾ ĐỂ TẠO HIỆU ỨNG ĐÓNG MÀN TRẬP (SHUTTER CLOSE) THỰC SỰ**
            // 1. CSS phải để Shutter ở trạng thái MỞ (transform: translateY(-100%)/100%)
            // 2. JavaScript sẽ xóa class đó đi để Shutter TRƯỢT VÀO.
            
            // Tuy nhiên, do cấu trúc Streamlit buộc phải reload, ta dùng cách đơn giản nhất:
            // Màn hình chuyển sang màu đen (giống fade), sau đó reload.
            // Tạm thời quay lại hiệu ứng fade để đảm bảo chuyển trang, nhưng dùng Shutter style:

            const topShutter = document.getElementById('shutter-top');
            const bottomShutter = document.getElementById('shutter-bottom');

            // Hiệu ứng "Đóng màn trập" (che màn hình)
            topShutter.style.transform = "translateY(0)"; // Trượt vào
            bottomShutter.style.transform = "translateY(0)"; // Trượt vào
            
            setTimeout(() => {{
                // Gửi thông báo hoàn thành sau khi màn trập đóng (1.5 giây)
                window.parent.postMessage({{type: 'intro_done'}}, '*');
            }}, 1500);
        }}

        // Đảm bảo Shutter MỞ (trượt ra) ngay khi tải trang (ngược lại với CSS đã viết)
        const topShutter = document.getElementById('shutter-top');
        const bottomShutter = document.getElementById('shutter-bottom');
        topShutter.style.transform = "translateY(-100%)";
        bottomShutter.style.transform = "translateY(100%)";


        vid.addEventListener('canplay', () => {{
            vid.play().catch(() => console.log('Autoplay bị chặn'));
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

        vid.addEventListener('ended', finishIntro);
        setTimeout(finishIntro, 9000);
        </script>
    </body>
    </html>
    """

    # ✅ phải nằm TRONG hàm
    components.html(intro_html, height=1080, scrolling=False)


# ========== TRANG CHÍNH ==========
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    with open(bg, "rb") as f:
        bg_b64 = base64.b64encode(f.read()).decode()

    # Thêm hiệu ứng Shutter MỞ khi vào trang chính (tùy chọn)
    st.markdown(f"""
    <style>
    /* CSS CŨ CỦA MAIN PAGE */
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
        z-index: 10; /* Đảm bảo chữ nằm trên Shutter */
    }}
    @keyframes textLight {{
        0% {{ background-position: 200% 0%; }}
        100% {{ background-position: -200% 0%; }}
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: scale(0.97); }}
        to {{ opacity: 1; transform: scale(1); }}
    }}

    /* CSS CHO HIỆU ỨNG SHUTTER MỞ TRÊN TRANG CHÍNH */
    .shutter-main {{
        position: fixed;
        left: 0;
        width: 100vw;
        height: 50vh;
        background: black;
        z-index: 50; /* Rất cao để che mọi thứ */
        transition: transform 1.5s ease-in-out 0.2s; /* Delay nhẹ */
    }}
    #shutter-main-top {{
        top: 0;
        transform: translateY(0); /* Ban đầu ĐÓNG (che) */
    }}
    #shutter-main-bottom {{
        bottom: 0;
        transform: translateY(0); /* Ban đầu ĐÓNG (che) */
    }}
    /* Kích hoạt hiệu ứng MỞ (trượt ra khỏi màn hình) */
    #shutter-main-top.open {{
        transform: translateY(-100%);
    }}
    #shutter-main-bottom.open {{
        transform: translateY(100%);
    }}

    </style>
    
    <div id="shutter-main-top" class="shutter-main"></div>
    <div id="shutter-main-bottom" class="shutter-main"></div>

    <div class="welcome">TỔ BẢO DƯỠNG SỐ 1</div>

    <script>
    // Kích hoạt hiệu ứng MỞ màn trập ngay lập tức
    document.addEventListener('DOMContentLoaded', () => {{
        const topShutter = document.getElementById('shutter-main-top');
        const bottomShutter = document.getElementById('shutter-main-bottom');
        topShutter.classList.add('open');
        bottomShutter.classList.add('open');
    }});
    </script>
    """, unsafe_allow_html=True)


# ========== LUỒNG CHÍNH ==========
hide_streamlit_ui()
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

if not st.session_state.intro_done:
    # --- Hiển thị Intro Screen ---
    intro_screen(st.session_state.is_mobile)
    
    # Script nhận thông báo 'intro_done' từ iframe
    st.markdown("""
    <script>
    window.addEventListener("message", (event) => {
        if (event.data.type === "intro_done") {
            // Sử dụng window.parent.location.reload() để buộc Streamlit reload và chuyển sang main_page
            window.parent.location.reload(); 
        }
    });
    </script>
    """, unsafe_allow_html=True)
    
    # Dùng time.sleep để giữ màn hình intro đủ lâu (nếu reload không kịp)
    time.sleep(9.5) 
    st.session_state.intro_done = True
    st.rerun() # Kích hoạt reload nếu script postMessage bị chặn hoặc lỗi
else:
    # --- Hiển thị Main Page ---
    main_page(st.session_state.is_mobile)
