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

# File ảnh tĩnh cho hiệu ứng SHATTER/RECONSTRUCT (Ảnh chụp từ frame cuối video)
SHUTTER_PC = "airplane_shutter.jpg"
SHUTTER_MOBILE = "mobile_shutter.jpg"

# File ảnh nền của trang chính (sẽ hiện ra sau khi ghép lại)
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"

st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

# Kích thước lưới và thời gian
GRID_SIZE = 8
SHATTER_DURATION = 1.8  # Thời gian hiệu ứng tan vỡ (giây)
RECONSTRUCT_DURATION = 1.8 # Thời gian hiệu ứng ghép lại (giây)
BLACKOUT_DELAY = 0.2    # Thời gian màn hình đen

# ========== ẨN UI STREAMLIT ==========

def hide_streamlit_ui():
    st.markdown("""
    <style>
    /* Ẩn các thành phần UI mặc định của Streamlit */
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
    }
    /* Đảm bảo toàn bộ ứng dụng chiếm hết màn hình */
    .stApp, .main, .block-container {
        padding: 0 !important;
        margin: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        overflow: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------

# ========== MÀN HÌNH INTRO CÓ HIỆU ỨNG KÍNH VỠ ==========
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    shutter_file = SHUTTER_MOBILE if is_mobile else SHUTTER_PC
    bg_file = BG_MOBILE if is_mobile else BG_PC
    
    # Đọc file và mã hóa Base64
    try:
        with open(video_file, "rb") as f:
            video_b64 = base64.b64encode(f.read()).decode()
        with open(SFX, "rb") as a:
            audio_b64 = base64.b64encode(a.read()).decode()
        with open(shutter_file, "rb") as s:
            shutter_b64 = base64.b64encode(s.read()).decode()
        with open(bg_file, "rb") as b:
            bg_b64 = base64.b64encode(b.read()).decode()
            
    except FileNotFoundError as e:
        st.error(f"Lỗi: Không tìm thấy file tài nguyên. Vui lòng kiểm tra: {e.filename}")
        st.stop()
    
    shards_html = "".join([f"<div class='shard' id='shard-{i}'></div>" for i in range(GRID_SIZE * GRID_SIZE)])

    # Chuyển đổi hằng số Python sang JS (milliseconds)
    js_shatter_duration = SHATTER_DURATION * 1000
    js_reconstruct_duration = RECONSTRUCT_DURATION * 1000
    js_blackout_delay = BLACKOUT_DELAY * 1000


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
        #pre-load-bg {{ display: none; background-image: url("data:image/jpeg;base64,{bg_b64}"); }}
        video {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;
            transition: opacity 0.1s linear;
        }}
        #static-frame {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;
            background-image: url("data:image/jpeg;base64,{shutter_b64}");
            background-size: cover; opacity: 0; z-index: 20; transition: opacity 0.1s linear;
        }}
        audio {{ display: none; }}
        #intro-text {{
            position: absolute; 
            top: 8%; /* Đặt 8% từ trên xuống */
            left: 50%; 
            transform: translate(-50%, 0); /* Chỉ dịch 50% theo chiều ngang */
            width: 90vw; text-align: center; color: #f8f4e3;
            font-size: clamp(22px, 6vw, 60px); font-weight: bold; font-family: 'Playfair Display', serif;
            background: linear-gradient(120deg, #e9dcb5 20%, #fff9e8 40%, #e9dcb5 60%);
            background-size: 200%; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            text-shadow: 0 0 15px rgba(255,255,230,0.4);
            animation: lightSweep 6s linear infinite, fadeInOut 6s ease-in-out forwards;
            line-height: 1.2; word-wrap: break-word; z-index: 10;
        }}
        @keyframes lightSweep {{ 0% {{ background-position: 200% 0%; }} 100% {{ background-position: -200% 0%; }} }}
        @keyframes fadeInOut {{ 0% {{ opacity: 0; }} 20% {{ opacity: 1; }} 80% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}

        /* === STYLE HIỆU ỨNG TAN VỠ VÀ GHÉP LẠI (GSAP Inspired) === */
        #shatter-overlay {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            display: grid; grid-template-columns: repeat({GRID_SIZE}, 1fr); grid-template-rows: repeat({GRID_SIZE}, 1fr);
            opacity: 0; pointer-events: none; z-index: 30;
            perspective: 1500px; /* Thêm phối cảnh 3D */
        }}
        .shard {{
            position: relative;
            background-image: url("data:image/jpeg;base64,{shutter_b64}"); 
            background-size: 100vw 100vh;
            /* Thay đổi hàm timing cho hiệu ứng kịch tính hơn */
            transition: transform {SHATTER_DURATION}s cubic-bezier(0.86, 0, 0.07, 1), opacity {SHATTER_DURATION}s ease-out, box-shadow {SHATTER_DURATION}s ease-out; 
            opacity: 1;
            box-shadow: 0 0 0px rgba(0,0,0,0.0);
            backface-visibility: hidden; /* Tránh glitch 3D */
        }}
        
        /* Khi tan vỡ */
        .shattering .shard {{
            opacity: 0 !important;
            /* Thêm shadow để mô phỏng 3D/độ dày khi bay ra */
            box-shadow: 
                -20px 20px 50px rgba(0, 0, 0, 0.8), 
                inset 0 0 10px rgba(255, 255, 255, 0.4); 
        }}

        /* Khi ghép lại */
        .reconstructing .shard {{
            transform: translate(0, 0) rotate(0deg) scale(1) !important; 
            /* Transition nhẹ nhàng khi ghép lại */
            transition: transform {RECONSTRUCT_DURATION}s cubic-bezier(0.19, 1, 0.22, 1), opacity {RECONSTRUCT_DURATION}s ease-in-out, background-image 0s; 
            background-image: url("data:image/jpeg;base64,{bg_b64}") !important;
            opacity: 1 !important; 
            box-shadow: 0 0 0px rgba(0,0,0,0.0) !important;
        }}

        /* Lớp phủ màn hình đen */
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
        <div id='static-frame'></div>
        <audio id='flySfx'> <source src='data:audio/mp3;base64,{audio_b64}' type='audio/mp3'></audio>
        <div id='intro-text'>KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>

        <div id='shatter-overlay'>{shards_html}</div>
        <div id='black-fade'></div>


        <script>
        const GRID_SIZE = {GRID_SIZE};
        const SHATTER_DURATION_MS = {js_shatter_duration};
        const RECONSTRUCT_DURATION_MS = {js_reconstruct_duration};
        const BLACKOUT_DELAY_MS = {js_blackout_delay};
        const SHATTER_DURATION_S = {SHATTER_DURATION};
        const RECONSTRUCT_DURATION_S = {RECONSTRUCT_DURATION};

        const vid = document.getElementById('introVid');
        const audio = document.getElementById('flySfx');
        const staticFrame = document.getElementById('static-frame');
        const shatterOverlay = document.getElementById('shatter-overlay');
        const shards = document.querySelectorAll('.shard');
        const blackFade = document.getElementById('black-fade');
        let ended = false;
        let initialTransforms = []; 

        shards.forEach((shard, index) => {{
            const row = Math.floor(index / GRID_SIZE);
            const col = index % GRID_SIZE;
            
            // Đặt vị trí background cho mỗi mảnh vỡ
            shard.style.backgroundPosition = 'calc(-' + col + ' * 100vw / ' + GRID_SIZE + ') calc(-' + row + ' * 100vh / ' + GRID_SIZE + ')';
            
            // TẠO THAM SỐ NGẪU NHIÊN CHO HIỆU ỨNG KÍNH VỠ
            const randX = (Math.random() - 0.5) * 450; // Bay xa hơn (450vw)
            const randY = (Math.random() - 0.5) * 450; // Bay xa hơn (450vh)
            const randZ = (Math.random() * 500) + 100; // Bay sâu vào không gian (100-600px)
            const randR = (Math.random() - 0.5) * 720; // Xoay mạnh hơn (lên đến 720 độ)
            const delay = Math.random() * 0.4; // Delay ngắn hơn
            const scale = Math.random() * 0.2 + 0.05; // Giảm kích thước xuống rất nhỏ (0.05-0.25)

            initialTransforms.push({{randX, randY, randZ, randR, delay, scale}});
        }});

        function finishIntro() {{
            if (ended) return;
            ended = true;
            
            // BƯỚC 0: Chuyển từ Video sang Ảnh tĩnh (shutter)
            vid.style.opacity = 0; 
            staticFrame.style.opacity = 1; 
            
            // BƯỚC 1: Bắt đầu Tan Vỡ (Shatter)
            setTimeout(() => {{ 
                blackFade.style.opacity = 0; 
                shatterOverlay.style.opacity = 1; 
                staticFrame.style.opacity = 0; 
                
                shatterOverlay.classList.remove('reconstructing');
                shatterOverlay.classList.add('shattering');
                shards.forEach((shard, index) => {{
                    const t = initialTransforms[index];
                    // SỬ DỤNG NỐI CHUỖI CỔ ĐIỂN ĐỂ TRÁNH LỖI CÚ PHÁP: 
                    shard.style.transform = 'translate3d(' + t.randX + 'vw, ' + t.randY + 'vh, ' + t.randZ + 'px) rotate(' + t.randR + 'deg) scale(' + t.scale + ')';
                    shard.style.transitionDelay = t.delay + 's';
                    shard.style.opacity = 0; 
                }});
            }}, 10);
            
            // BƯỚC 2: Màn Hình Đen (Blackout)
            setTimeout(() => {{
                shatterOverlay.style.opacity = 0; 
                blackFade.style.opacity = 1; 
            }}, SHATTER_DURATION_MS); 

            // BƯỚC 3: Ghép Lại (Reconstruction) - Bắt đầu sau khi màn đen kết thúc
            setTimeout(() => {{
                shatterOverlay.style.opacity = 1; 
                blackFade.style.opacity = 0; 
                
                shatterOverlay.classList.remove('shattering');
                shatterOverlay.classList.add('reconstructing'); 
                
                shards.forEach((shard, index) => {{
                    // Áp dụng lại transition delay để đồng bộ hóa việc ghép lại
                    shard.style.transitionDelay = (RECONSTRUCT_DURATION_S - initialTransforms[index].delay) + 's';
                }});

                // BƯỚC 4: Thông báo hoàn thành - Tải lại trang NGAY LẬP TỨC
                setTimeout(() => {{
                    window.parent.postMessage({{type: 'intro_done'}}, '*');
                }}, RECONSTRUCT_DURATION_MS + 10); 

            }}, SHATTER_DURATION_MS + BLACKOUT_DELAY_MS); 

        }}

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
        // Cho phép click để kích hoạt audio nếu bị chặn
        document.addEventListener('click', () => {{
            vid.muted = false;
            vid.play();
            audio.volume = 1.0;
            audio.currentTime = 0;
            audio.play().catch(()=>{{}}); 
            blackFade.style.opacity = 0; 
        }}, {{once:true}});

        vid.addEventListener('ended', finishIntro);
        setTimeout(finishIntro, 9000); // Dự phòng nếu video bị lỗi không gọi 'ended'

        blackFade.style.opacity = 1;

        </script>
    </body>
    </html>
    """
    components.html(intro_html, height=800, scrolling=False)

# ------------------------------------------------------------------

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
    /* Style cho trang chính, áp dụng background và tiêu đề */
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

# ------------------------------------------------------------------

# ========== LUỒNG CHÍNH ==========

hide_streamlit_ui()

# BƯỚC 1: Xác định thiết bị
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


# BƯỚC 2: Kiểm tra trạng thái Intro
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

# BƯỚC 3: Hiển thị Intro nếu chưa hoàn thành
if not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
    
    # JavaScript lắng nghe sự kiện hoàn thành từ iframe
    st.markdown("""
    <script>
    window.addEventListener("message", (event) => {
        // Chỉ xử lý thông báo intro_done
        if (event.data.type === "intro_done") {
            // Tải lại trang Streamlit chính để kích hoạt main_page
            window.parent.location.reload(); 
        }
    });
    </script>
    """, unsafe_allow_html=True)

    # Dừng luồng Python để chờ JS hoàn thành
    time.sleep(15) 
    st.session_state.intro_done = True
    st.rerun()

# BƯỚC 4: Hiển thị Trang Chính
else:
    main_page(st.session_state.is_mobile)
