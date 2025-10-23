import streamlit as st
import base64
import time
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

# ========== CẤU HÌNH VÀ TÀI NGUYÊN ==========

# Đảm bảo bạn đã có các file sau. 
VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
SFX = "plane_fly.mp3"

# Thêm 2 file ảnh tĩnh SHUTTER mới
SHUTTER_PC = "airplane_shutter.jpg"  # Ảnh tĩnh chụp cuối video PC
SHUTTER_MOBILE = "mobile_shutter.jpg" # Ảnh tĩnh chụp cuối video Mobile

# File ảnh nền của trang chính (sẽ hiện ra sau khi ghép lại)
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"

st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

# Kích thước lưới và thời gian
GRID_SIZE = 8
SHATTER_DURATION = 1.8  # Thời gian hiệu ứng tan vỡ (giây)
RECONSTRUCT_DURATION = 1.8 # Thời gian hiệu ứng ghép lại (giây)
BLACKOUT_DELAY = 0.5    # Thời gian màn hình đen

# ========== ẨN UI STREAMLIT ==========

def hide_streamlit_ui():
    st.markdown("""
    <style>
    /* ẨN CÁC THÀNH PHẦN UI CỦA STREAMLIT */
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
    }
    
    /* FIX HEIGHT MOBILE: Đảm bảo phần tử bao ngoài full screen */
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


# ========== MÀN HÌNH INTRO - ĐÃ SỬA VỚI HIỆU ỨNG GHÉP LẠI ==========

def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    # SỬ DỤNG FILE SHUTTER MỚI
    shutter_file = SHUTTER_MOBILE if is_mobile else SHUTTER_PC 
    bg_file = BG_MOBILE if is_mobile else BG_PC 

    # Đọc file và mã hóa Base64
    try:
        with open(video_file, "rb") as f:
            video_b64 = base64.b64encode(f.read()).decode()
        with open(SFX, "rb") as a:
            audio_b64 = base64.b64encode(a.read()).decode()
        # MÃ HÓA SHUTTER VÀ BACKGROUND RIÊNG
        with open(shutter_file, "rb") as s:
            shutter_b64 = base64.b64encode(s.read()).decode()
        with open(bg_file, "rb") as b:
            bg_b64 = base64.b64encode(b.read()).decode()
            
    except FileNotFoundError as e:
        st.error(f"Lỗi: Không tìm thấy file tài nguyên. Vui lòng kiểm tra: {e.filename}")
        st.stop()
    
    # Tạo các mảnh vỡ HTML (GRID_SIZE x GRID_SIZE)
    shards_html = "".join([f"<div class='shard' id='shard-{i}'></div>" for i in range(GRID_SIZE * GRID_SIZE)])

    # Chuyển đổi thời gian sang milliseconds cho JS
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
        video {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;
        }}
        audio {{ display: none; }}
        
        /* ĐIỀU CHỈNH: Đưa intro-text lên trên cùng */
        #intro-text {{
            position: absolute; 
            top: 8%; /* Đưa lên top */
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


        /* === STYLE HIỆU ỨNG TAN VỠ VÀ GHÉP LẠI === */
        #shatter-overlay {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            display: grid; grid-template-columns: repeat({GRID_SIZE}, 1fr); grid-template-rows: repeat({GRID_SIZE}, 1fr);
            opacity: 0; pointer-events: none; z-index: 30; 
            transition: opacity 0.5s ease-in; 
        }}
        .shard {{
            position: relative;
            /* DÙNG ẢNH SHUTTER LÀM NỀN BAN ĐẦU */
            background-image: url("data:image/jpeg;base64,{shutter_b64}"); 
            background-size: 100vw 100vh;
            transition: transform {SHATTER_DURATION}s cubic-bezier(0.68, -0.55, 0.27, 1.55), opacity 1.5s ease-in-out; 
            opacity: 1; 
        }}
        
        /* Khi ghép lại: Chuyển sang ảnh nền chính và reset transform */
        .reconstructing .shard {{
            transform: translate(0, 0) rotate(0deg) scale(1) !important; 
            transition: transform {RECONSTRUCT_DURATION}s cubic-bezier(0.19, 1, 0.22, 1), opacity {RECONSTRUCT_DURATION}s ease-in-out; 
            /* SỬ DỤNG ẢNH BG CHÍNH ĐỂ GHÉP LẠI */
            background-image: url("data:image/jpeg;base64,{bg_b64}") !important; 
            opacity: 1 !important;
            /* ĐẢM BẢO BACKGROUND POSITION VỀ 0 0 CHO ẢNH NỀN CHÍNH */
            background-position: 0 0 !important;
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
        const SHATTER_DURATION = {js_shatter_duration};
        const RECONSTRUCT_DURATION = {js_reconstruct_duration};
        const BLACKOUT_DELAY = {js_blackout_delay};


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
            
            // Tính toán Background Position ban đầu (cho ảnh SHUTTER)
            shard.style.backgroundPosition = 'calc(-' + col + ' * 100vw / ' + GRID_SIZE + ') calc(-' + row + ' * 100vh / ' + GRID_SIZE + ')';
            
            // Random Transforms
            const randX = (Math.random() - 0.5) * 200; 
            const randY = (Math.random() - 0.5) * 200; 
            const randR = (Math.random() - 0.5) * 360; 
            const delay = Math.random() * 0.5; 

            initialTransforms.push({{randX, randY, randR, delay}});
        }});


        function finishIntro() {{
            if (ended) return;
            ended = true;
            
            // BƯỚC 1: Bắt đầu Tan Vỡ (Shatter)
            // Đảm bảo blackFade tắt ngay lập tức nếu nó đang che
            blackFade.style.opacity = 0; 
            shatterOverlay.style.opacity = 1; 
            vid.style.opacity = 0; 
            shatterOverlay.classList.remove('reconstructing'); // Loại bỏ class cũ (nếu có)
            shatterOverlay.classList.add('shattering');
            
            shards.forEach((shard, index) => {{
                const t = initialTransforms[index];
                shard.style.transform = 'translate(' + t.randX + 'vw, ' + t.randY + 'vh) rotate(' + t.randR + 'deg) scale(0.1)';
                shard.style.transitionDelay = t.delay + 's';
                shard.style.opacity = 0; // Các mảnh mờ dần khi bay ra
            }});
            
            // BƯỚC 2: Màn Hình Đen (Blackout)
            setTimeout(() => {{
                shatterOverlay.style.opacity = 0; // Tắt mảnh vỡ (đã tan)
                blackFade.style.opacity = 1; // Hiện màn hình đen
            }}, SHATTER_DURATION + 50); 


            // BƯỚC 3: Ghép Lại (Reconstruction)
            setTimeout(() => {{
                // Đảo ngược hiệu ứng: Hiện lại mảnh vỡ, chuẩn bị ghép
                shatterOverlay.style.opacity = 1; 
                blackFade.style.opacity = 0; // Tắt màn hình đen

                shatterOverlay.classList.remove('shattering');
                shatterOverlay.classList.add('reconstructing'); 
                
                shards.forEach((shard, index) => {{
                    // ĐẶT LẠI DELAY NGẪU NHIÊN NHỎ (FIX LỖI GHÉP LẠI KHÔNG XẢY RA)
                    shard.style.transitionDelay = (Math.random() * 0.5) + 's'; 
                    shard.style.opacity = 1; // Mảnh hiện lại
                }});

                // 4. Thông báo hoàn thành sau khi ghép lại
                setTimeout(() => {{
                    window.parent.postMessage({{type: 'intro_done'}}, '*');
                }}, RECONSTRUCT_DURATION + 500); 


            }}, SHATTER_DURATION * 1000 + BLACKOUT_DELAY * 1000 + 50); // Sau khi màn hình đen xong

        }}


        // Logic play video/audio
        vid.addEventListener('canplay', () => {{
            vid.play().catch(() => console.log('Autoplay bị chặn'));
            blackFade.style.opacity = 0; // Mở màn hình đen khi video sẵn sàng
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

        // Ban đầu: Màn hình đen che mọi thứ
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
    /* FIX LỖI ẢNH NỀN KHÔNG HIỂN THỊ TRONG TRANG CHÍNH TRÊN MOBILE */
    html, body, .stApp {{
        height: 100vh !important;
        /* Đảm bảo chiều cao full màn hình */
        min-height: -webkit-fill-available !important; 
        
        background: 
            linear-gradient(to bottom, rgba(255, 235, 200, 0.25) 0%, rgba(160, 130, 90, 0.35) 50%, rgba(90, 70, 50, 0.5) 100%),
            url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed !important;
        background-size: cover !important;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
        position: relative;
        filter: brightness(1.05) contrast(1.1) saturate(1.05);
        animation: fadeInBg 1s ease-in-out forwards; 
    }}
    /* ... (CSS còn lại của main_page) */
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
    </style>

    <div class="welcome">TỔ BẢO DƯỠNG SỐ 1</div>
    """, unsafe_allow_html=True)


# ========== LUỒNG CHÍNH ==========


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


if not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
    
    # Script lắng nghe thông báo hoàn thành từ iframe
    st.markdown("""
    <script>
    window.addEventListener("message", (event) => {
        if (event.data.type === "intro_done") {
            window.parent.location.reload(); 
        }
    });
    </script>
    """, unsafe_allow_html=True)

    # Thời gian chờ fallback (15s)
    time.sleep(15) 
    st.session_state.intro_done = True
    st.rerun()

else:
    main_page(st.session_state.is_mobile)
