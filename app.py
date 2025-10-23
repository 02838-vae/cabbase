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


# File ảnh tĩnh cho hiệu ứng SHATTER (Ảnh chụp từ frame cuối video)
SHUTTER_PC = "airplane_shutter.jpg"
SHUTTER_MOBILE = "mobile_shutter.jpg"


# File ảnh nền của trang chính (Dùng cho quá trình RECONSTRUCT và Trang Chính)
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"


# LƯU Ý: Đảm bảo các file trên tồn tại trong cùng thư mục với app.py


st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")


# Kích thước lưới và thời gian
GRID_SIZE = 8
SHATTER_DURATION = 1.8   # Thời gian hiệu ứng tan vỡ (giây)
# Đã loại bỏ RECONSTRUCT_DURATION
BLACKOUT_DELAY = 0.0     # Đã bỏ độ trễ màn hình đen


# ========== HÀM ẨN UI STREAMLIT (FIX MOBILE HEIGHT) ==========


def hide_streamlit_ui():
    st.markdown("""
    <style>
    /* ẨN CÁC THÀNH PHẦN UI CỦA STREAMLIT */
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
    }
    
    /* Đảm bảo phần tử bao ngoài full screen */
    html, body {
        height: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .stApp, .main, .block-container {
        padding: 0 !important;
        margin: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        overflow: hidden !important;
    }

    /* FIX HEIGHT iOS/Safari: Sử dụng thuộc tính đặc biệt để khắc phục thanh địa chỉ mobile */
    @media only screen and (max-width: 600px) {
        .stApp, .main, .block-container {
            height: 100% !important;
            min-height: -webkit-fill-available !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)


# ========== MÀN HÌNH INTRO (ĐÃ LOẠI BỎ HIỆU ỨNG NỐI LẠI) ==========


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
        # Ảnh tĩnh SHUTTER cho pha TAN VỠ
        with open(shutter_file, "rb") as s:
            shutter_b64 = base64.b64encode(s.read()).decode()
        # Ảnh nền BG (cần đọc để tránh lỗi FileNotFoundError)
        with open(bg_file, "rb") as b:
            bg_b64 = base64.b64encode(b.read()).decode()
            
    except FileNotFoundError as e:
        st.error(f"Lỗi: Không tìm thấy file tài nguyên. Vui lòng kiểm tra: {e.filename}")
        st.stop()
    
    shards_html = "".join([f"<div class='shard' id='shard-{i}'></div>" for i in range(GRID_SIZE * GRID_SIZE)])

    # Chuyển đổi thời gian sang giây (cho JS/CSS)
    js_shatter_duration = SHATTER_DURATION 

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
        video {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;
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
            0% {{ opacity: 0; }} 20% {{ opacity: 1; }}
            80% {{ opacity: 1; }} 100% {{ opacity: 0; }}
        }}

        /* === STYLE HIỆU ỨNG TAN VỠ === */
        #shatter-overlay {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            display: grid; grid-template-columns: repeat({GRID_SIZE}, 1fr); grid-template-rows: repeat({GRID_SIZE}, 1fr);
            opacity: 0; pointer-events: none; z-index: 30; 
            transition: opacity 0.5s ease-in; 
        }}
        .shard {{
            position: relative;
            background-image: url("data:image/jpeg;base64,{shutter_b64}"); 
            background-size: 100vw 100vh;
            transition: transform {SHATTER_DURATION}s cubic-bezier(0.68, -0.55, 0.27, 1.55), opacity 1.5s ease-in-out; 
            opacity: 1; 
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
        <video id='introVid' autoplay muted playsinline>
            <source src='data:video/mp4;base64,{video_b64}' type='video/mp4'>
        </video>
        <audio id='flySfx'>
            <source src='data:audio/mp3;base64,{audio_b64}' type='audio/mp3'>
        </audio>
        <div id='intro-text'>KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>

        <div id='shatter-overlay'>
            {shards_html}
        </div>
        
        <div id='black-fade'></div>

        <script>
        const GRID_SIZE = {GRID_SIZE};
        const SHATTER_DURATION = {js_shatter_duration}; // giây
        // const RECONSTRUCT_DURATION = {js_reconstruct_duration}; // Đã loại bỏ
        const BG_B64_URL = "url('data:image/jpeg;base64,{bg_b64}')"; 

        const vid = document.getElementById('introVid');
        const audio = document.getElementById('flySfx');
        const shatterOverlay = document.getElementById('shatter-overlay');
        const shards = document.querySelectorAll('.shard');
        const blackFade = document.getElementById('black-fade');
        let ended = false;
        let initialTransforms = []; 

        // 1. Tính toán vị trí nền và transforms ngẫu nhiên
        shards.forEach((shard, index) => {{
            const row = Math.floor(index / GRID_SIZE);
            const col = index % GRID_SIZE;
            
            const bgPosition = 'calc(-' + col + ' * 100vw / ' + GRID_SIZE + ') calc(-' + row + ' * 100vh / ' + GRID_SIZE + ')';
            shard.style.backgroundPosition = bgPosition;
            
            const randX = (Math.random() - 0.5) * 200; 
            const randY = (Math.random() - 0.5) * 200; 
            const randR = (Math.random() - 0.5) * 360; 
            const delay = Math.random() * 0.5; 

            initialTransforms.push({{randX, randY, randR, delay, bgPosition}});
        }});

        function finishIntro() {{
            if (ended) return;
            ended = true;
            
            // BƯỚC 1: Bắt đầu Tan Vỡ (Shatter)
            blackFade.style.opacity = 0; 
            shatterOverlay.style.opacity = 1; 
            vid.style.opacity = 0; 
            shatterOverlay.classList.add('shattering');
            
            shards.forEach((shard, index) => {{
                const t = initialTransforms[index];
                shard.style.transform = 'translate(' + t.randX + 'vw, ' + t.randY + 'vh) rotate(' + t.randR + 'deg) scale(0.1)';
                shard.style.transitionDelay = t.delay + 's';
                shard.style.opacity = 0; 
            }});
            
            // BƯỚC 2: Gửi tín hiệu hoàn thành sau khi tan vỡ kết thúc
            const SHATTER_END_DELAY = SHATTER_DURATION * 1000 + 500; // Đợi tan vỡ xong

            setTimeout(() => {{
                // Gửi thông báo
                window.parent.postMessage({{type: 'intro_done'}}, '*'); 
                
                // Mờ dần lớp phủ (để tránh Streamlit xóa iframe đột ngột)
                setTimeout(() => {{
                    shatterOverlay.style.transition = 'opacity 0.5s ease-out';
                    shatterOverlay.style.opacity = 0; 
                }}, 100); 

            }}, SHATTER_END_DELAY); 
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
        document.addEventListener('click', () => {{
            vid.muted = false;
            vid.play();
            audio.volume = 1.0;
            audio.currentTime = 0;
            audio.play().catch(()=>{{}}); 
            blackFade.style.opacity = 0; 
        }}, {{once:true}});

        vid.addEventListener('ended', finishIntro);
        setTimeout(finishIntro, 10000); // Đặt fallback lâu hơn

        blackFade.style.opacity = 1;
        </script>
    </body>
    </html>
    """
    components.html(intro_html, height=800, scrolling=False)


# ========== TRANG CHÍNH (ĐÃ THÊM HIỆU ỨNG PHÓNG TO NỀN) ==========

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
    /* ẢNH NỀN CỦA TRANG CHÍNH */
    html, body, .stApp {{
        height: 100vh !important;
        min-height: -webkit-fill-available !important; 
        
        background: 
            linear-gradient(to bottom, rgba(255, 235, 200, 0.25) 0%, rgba(160, 130, 90, 0.35) 50%, rgba(90, 70, 50, 0.5) 100%),
            url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed !important;
        
        /* Hiệu ứng phóng to nền */
        background-size: 150vw 150vh !important; /* Bắt đầu từ kích thước lớn */
        background-position: center center !important;
        
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
        position: relative;
        filter: brightness(1.05) contrast(1.1) saturate(1.05);
        
        /* Áp dụng hiệu ứng phóng to */
        animation: 
            zoomInBg 2s cubic-bezier(0.23, 1, 0.32, 1) forwards, /* Phóng to */
            fadeInBg 1s ease-in-out forwards; /* Mờ dần xuất hiện */
    }}
    
    @keyframes zoomInBg {{
        from {{ background-size: 150vw 150vh; }}
        to {{ background-size: cover; }}
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
    .welcome {{ display: none !important; }} 
    </style>
    """, unsafe_allow_html=True)


# ========== HIỂN THỊ TIÊU ĐỀ BAY LÊN ==========

def show_flying_title():
    st.markdown("""
    <style>
    .flying-title {
        position: absolute;
        top: 85%; /* Vị trí bắt đầu: Gần dưới cùng */
        left: 50%;
        transform: translate(-50%, 0);
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
        letter-spacing: 2px;
        z-index: 50; 
        /* Bắt đầu bay lên ngay sau khi trang chính render (0.5s sau rerun) */
        animation: 
            flyUp 2s ease-out 0.5s forwards, /* Độ trễ 0.5s để chờ nền ổn định */
            textLight 10s linear infinite 2.5s; 
        opacity: 0; 
    }

    @keyframes flyUp {
        0% { top: 85%; opacity: 0; transform: translate(-50%, 0) scale(1.05); }
        20% { opacity: 1; }
        100% { top: 8%; opacity: 1; transform: translate(-50%, 0) scale(1); } /* Đích đến là vị trí 8% */
    }

    @keyframes textLight { 
        0% { background-position: 200% 0%; }
        100% { background-position: -200% 0%; }
    }
    </style>
    
    <div class="flying-title">TỔ BẢO DƯỠNG SỐ 1</div>

    """, unsafe_allow_html=True)


# ========== LUỒNG CHÍNH ĐÃ KHẮC PHỤC ==========

hide_streamlit_ui()

# 1. Xác định thiết bị
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

# 2. Xử lý chuyển cảnh
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

if "placeholder_removed" not in st.session_state:
    st.session_state.placeholder_removed = False

intro_placeholder = st.empty()

if not st.session_state.intro_done:
    
    with intro_placeholder.container():
        intro_screen(st.session_state.is_mobile)
    
    # Script lắng nghe thông báo hoàn thành từ iframe
    st.markdown("""
    <script>
    window.addEventListener("message", (event) => {
        if (event.data.type === "intro_done") {
            sessionStorage.setItem('introComplete', 'true');
        }
    });
    </script>
    """, unsafe_allow_html=True)

    # Dùng st_javascript để kiểm tra cờ
    intro_complete_check = st_javascript("sessionStorage.getItem('introComplete');")

    if intro_complete_check == 'true':
        # Dọn dẹp session storage và chuyển trạng thái
        st_javascript("sessionStorage.removeItem('introComplete');")
        st.session_state.intro_done = True
        st.rerun() # Rerun để chuyển sang main_page

    time.sleep(0.1)
    st.stop()

else:
    # Sau khi intro_done=True và RERUN:
    
    # 1. Hiển thị Trang Chính (ảnh nền với hiệu ứng zoom-in)
    main_page(st.session_state.is_mobile)
    
    # 2. Hiển thị tiêu đề bay lên
    show_flying_title()
    
    # 3. Xóa Intro Placeholder để giải phóng iframe
    if not st.session_state.placeholder_removed:
        time.sleep(0.1) # Đợi một chút để DOM kịp cập nhật
        intro_placeholder.empty() 
        st.session_state.placeholder_removed = True
        
    st.stop()
