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

# ========== HÀM ẨN UI STREAMLIT ==========

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


# ========== MÀN HÌNH INTRO ==========
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    shutter_file = SHUTTER_MOBILE if is_mobile else SHUTTER_PC
    bg_file = BG_MOBILE if is_mobile else BG_PC
    
    # ... (Đọc file và mã hóa Base64 giữ nguyên) ...
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

    # Chuyển đổi hằng số Python sang JS
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
        }}
        #static-frame {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;
            background-image: url("data:image/jpeg;base64,{shutter_b64}");
            background-size: cover; opacity: 0; z-index: 20; transition: opacity 0.1s linear;
        }}
        audio {{ display: none; }}
        #intro-text {{
            position: absolute; 
            top: 8%; /* <--- ĐIỀU CHỈNH: Đặt 8% từ trên xuống */
            left: 50%; 
            transform: translate(-50%, 0); /* <--- ĐIỀU CHỈNH: Chỉ dịch 50% theo chiều ngang */
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

        /* === STYLE HIỆU ỨNG TAN VỠ VÀ GHÉP LẠI (Giữ nguyên) === */
        #shatter-overlay {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            display: grid; grid-template-columns: repeat({GRID_SIZE}, 1fr); grid-template-rows: repeat({GRID_SIZE}, 1fr);
            opacity: 0; pointer-events: none; z-index: 30; 
        }}
        .shard {{
            position: relative;
            background-image: url("data:image/jpeg;base64,{shutter_b64}"); 
            background-size: 100vw 100vh;
            transition: transform {SHATTER_DURATION}s cubic-bezier(0.68, -0.55, 0.27, 1.55), opacity 1.5s ease-in-out; 
            opacity: 1; 
        }}
        
        /* Khi ghép lại */
        .reconstructing .shard {{
            transform: translate(0, 0) rotate(0deg) scale(1) !important; 
            transition: transform {RECONSTRUCT_DURATION}s cubic-bezier(0.19, 1, 0.22, 1), opacity {RECONSTRUCT_DURATION}s ease-in-out; 
            background-image: url("data:image/jpeg;base64,{bg_b64}") !important;
            opacity: 1 !important; 
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
        const SHATTER_DURATION = {js_shatter_duration};
        const RECONSTRUCT_DURATION = {js_reconstruct_duration};
        const BLACKOUT_DELAY = {js_blackout_delay};

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
            
            shard.style.backgroundPosition = 'calc(-' + col + ' * 100vw / ' + GRID_SIZE + ') calc(-' + row + ' * 100vh / ' + GRID_SIZE + ')';
            
            const randX = (Math.random() - 0.5) * 200; 
            const randY = (Math.random() - 0.5) * 200; 
            const randR = (Math.random() - 0.5) * 360; 
            const delay = Math.random() * 0.5; 

            initialTransforms.push({{randX, randY, randR, delay}});
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
                    shard.style.transform = 'translate(' + t.randX + 'vw, ' + t.randY + 'vh) rotate(' + t.randR + 'deg) scale(0.1)';
                    shard.style.transitionDelay = t.delay + 's';
                    shard.style.opacity = 0; 
                }});
            }}, 10);
            
            // BƯỚC 2: Màn Hình Đen (Blackout)
            setTimeout(() => {{
                shatterOverlay.style.opacity = 0; 
                blackFade.style.opacity = 1; 
            }}, SHATTER_DURATION); 

            // BƯỚC 3: Ghép Lại (Reconstruction) - Bắt đầu sau khi màn đen kết thúc
            setTimeout(() => {{
                shatterOverlay.style.opacity = 1; 
                blackFade.style.opacity = 0; 
                
                shatterOverlay.classList.remove('shattering');
                shatterOverlay.classList.add('reconstructing'); 
                
                shards.forEach((shard, index) => {{
                    shard.style.transitionDelay = (RECONSTRUCT_DURATION / 1000 - initialTransforms[index].delay) + 's';
                }});

                // BƯỚC 4: Thông báo hoàn thành - Tải lại trang NGAY LẬP TỨC
                setTimeout(() => {{
                    window.parent.postMessage({{type: 'intro_done'}}, '*');
                }}, RECONSTRUCT_DURATION + 10); 

            }}, SHATTER_DURATION + BLACKOUT_DELAY); 

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
        setTimeout(finishIntro, 9000); 

        blackFade.style.opacity = 1;

        </script>
    </body>
    </html>
    """
    components.html(intro_html, height=800, scrolling=False)

# ----------------------------------------------------------------------------------------------------------------------

# ========== TRANG CHÍNH CÓ HIỆU ỨNG STARFALL ==========

def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    try:
        with open(bg, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError as e:
        st.error(f"Lỗi: Không tìm thấy file tài nguyên: {e.filename}")
        st.stop()
    
    # KHỐI CSS STARFALL VÀ STYLE TRANG CHÍNH
    # CHÚ Ý: Đã thay thế background-image bằng placeholder và sau đó dùng .replace()
    # để tránh lỗi cú pháp f-string phức tạp
    starfall_css = """
    /* Điều chỉnh body/stApp để phù hợp với nền Starfall (màu tối) */
    html, body, .stApp {
        height: 100vh !important;
        /* BACKGROUND của bạn, sử dụng placeholder để thay thế bằng base64 */
        background: 
            linear-gradient(to bottom, rgba(255, 235, 200, 0.25) 0%, rgba(160, 130, 90, 0.35) 50%, rgba(90, 70, 50, 0.5) 100%),
            url("data:image/jpeg;base64,__BG_B64__") no-repeat center center fixed !important;
        background-size: cover !important;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
        position: relative;
        filter: brightness(1.05) contrast(1.1) saturate(1.05);
        animation: fadeInBg 0.5s ease-in-out forwards; 
    }

    /* MEDIA QUERY CỦA BẠN */
    @media only screen and (max-width: 600px) {
        .stApp {
            background-size: auto !important;
            background-position: right !important;
        }
    }
    
    /* CSS STARFALL - Vị trí và Z-index */
    .starfall {
        position: absolute;
        height: 100%;
        width: 100%;
        top: 0;
        left: 0;
        transform-style: preserve-3d;
        perspective: 1000px;
        z-index: 1; /* Thấp hơn noise (2) và văn bản (3) */
    }
    .starfall .falling-star {
        width: 8px;
        height: 8px;
        background: #00d1b2;
        position: absolute;
        border-radius: 50%;
        opacity: 0.5;
        box-shadow: 0 0 5px 1px rgba(0, 209, 178, 0.7);
    }
    
    /* === ANIMATIONS VÀ KEYFRAMES STARFALL === */

    .falling-star:nth-child(1) { transform: translateX(68vw) translateY(-8px); animation: anim1 4s infinite; animation-delay: 0.3s; }
    .falling-star:nth-child(2) { transform: translateX(57vw) translateY(-8px); animation: anim2 4s infinite; animation-delay: 0.6s; }
    .falling-star:nth-child(3) { transform: translateX(70vw) translateY(-8px); animation: anim3 4s infinite; animation-delay: 0.9s; }
    .falling-star:nth-child(4) { transform: translateX(54vw) translateY(-8px); animation: anim4 4s infinite; animation-delay: 1.2s; }
    .falling-star:nth-child(5) { transform: translateX(85vw) translateY(-8px); animation: anim5 4s infinite; animation-delay: 1.5s; }
    .falling-star:nth-child(6) { transform: translateX(59vw) translateY(-8px); animation: anim6 4s infinite; animation-delay: 1.8s; }
    .falling-star:nth-child(7) { transform: translateX(33vw) translateY(-8px); animation: anim7 4s infinite; animation-delay: 2.1s; }
    .falling-star:nth-child(8) { transform: translateX(82vw) translateY(-8px); animation: anim8 4s infinite; animation-delay: 2.4s; }
    .falling-star:nth-child(9) { transform: translateX(24vw) translateY(-8px); animation: anim9 4s infinite; animation-delay: 2.7s; }
    .falling-star:nth-child(10) { transform: translateX(54vw) translateY(-8px); animation: anim10 4s infinite; animation-delay: 3s; }
    .falling-star:nth-child(11) { transform: translateX(11vw) translateY(-8px); animation: anim11 4s infinite; animation-delay: 3.3s; }
    .falling-star:nth-child(12) { transform: translateX(14vw) translateY(-8px); animation: anim12 4s infinite; animation-delay: 3.6s; }
    .falling-star:nth-child(13) { transform: translateX(66vw) translateY(-8px); animation: anim13 4s infinite; animation-delay: 3.9s; }
    .falling-star:nth-child(14) { transform: translateX(64vw) translateY(-8px); animation: anim14 4s infinite; animation-delay: 4.2s; }
    .falling-star:nth-child(15) { transform: translateX(3vw) translateY(-8px); animation: anim15 4s infinite; animation-delay: 4.5s; }
    .falling-star:nth-child(16) { transform: translateX(40vw) translateY(-8px); animation: anim16 4s infinite; animation-delay: 4.8s; }
    .falling-star:nth-child(17) { transform: translateX(96vw) translateY(-8px); animation: anim17 4s infinite; animation-delay: 5.1s; }
    .falling-star:nth-child(18) { transform: translateX(47vw) translateY(-8px); animation: anim18 4s infinite; animation-delay: 5.4s; }
    .falling-star:nth-child(19) { transform: translateX(79vw) translateY(-8px); animation: anim19 4s infinite; animation-delay: 5.7s; }
    .falling-star:nth-child(20) { transform: translateX(98vw) translateY(-8px); animation: anim20 4s infinite; animation-delay: 6s; }
    .falling-star:nth-child(21) { transform: translateX(29vw) translateY(-8px); animation: anim21 4s infinite; animation-delay: 6.3s; }
    .falling-star:nth-child(22) { transform: translateX(36vw) translateY(-8px); animation: anim22 4s infinite; animation-delay: 6.6s; }
    .falling-star:nth-child(23) { transform: translateX(21vw) translateY(-8px); animation: anim23 4s infinite; animation-delay: 6.9s; }
    .falling-star:nth-child(24) { transform: translateX(91vw) translateY(-8px); animation: anim24 4s infinite; animation-delay: 7.2s; }
    .falling-star:nth-child(25) { transform: translateX(46vw) translateY(-8px); animation: anim25 4s infinite; animation-delay: 7.5s; }
    .falling-star:nth-child(26) { transform: translateX(39vw) translateY(-8px); animation: anim26 4s infinite; animation-delay: 7.8s; }
    .falling-star:nth-child(27) { transform: translateX(18vw) translateY(-8px); animation: anim27 4s infinite; animation-delay: 8.1s; }
    .falling-star:nth-child(28) { transform: translateX(94vw) translateY(-8px); animation: anim28 4s infinite; animation-delay: 8.4s; }
    .falling-star:nth-child(29) { transform: translateX(17vw) translateY(-8px); animation: anim29 4s infinite; animation-delay: 8.7s; }
    .falling-star:nth-child(30) { transform: translateX(13vw) translateY(-8px); animation: anim30 4s infinite; animation-delay: 9s; }
    .falling-star:nth-child(31) { transform: translateX(87vw) translateY(-8px); animation: anim31 4s infinite; animation-delay: 9.3s; }
    .falling-star:nth-child(32) { transform: translateX(32vw) translateY(-8px); animation: anim32 4s infinite; animation-delay: 9.6s; }
    .falling-star:nth-child(33) { transform: translateX(38vw) translateY(-8px); animation: anim33 4s infinite; animation-delay: 9.9s; }
    .falling-star:nth-child(34) { transform: translateX(95vw) translateY(-8px); animation: anim34 4s infinite; animation-delay: 10.2s; }
    .falling-star:nth-child(35) { transform: translateX(78vw) translateY(-8px); animation: anim35 4s infinite; animation-delay: 10.5s; }
    .falling-star:nth-child(36) { transform: translateX(12vw) translateY(-8px); animation: anim36 4s infinite; animation-delay: 10.8s; }
    .falling-star:nth-child(37) { transform: translateX(93vw) translateY(-8px); animation: anim37 4s infinite; animation-delay: 11.1s; }
    .falling-star:nth-child(38) { transform: translateX(92vw) translateY(-8px); animation: anim38 4s infinite; animation-delay: 11.4s; }
    .falling-star:nth-child(39) { transform: translateX(20vw) translateY(-8px); animation: anim39 4s infinite; animation-delay: 11.7s; }
    .falling-star:nth-child(40) { transform: translateX(41vw) translateY(-8px); animation: anim40 4s infinite; animation-delay: 12s; }

    @keyframes anim1 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(88vw) translateY(100vh); opacity: 0; } }
    @keyframes anim2 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(77vw) translateY(100vh); opacity: 0; } }
    @keyframes anim3 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(90vw) translateY(100vh); opacity: 0; } }
    @keyframes anim4 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(74vw) translateY(100vh); opacity: 0; } }
    @keyframes anim5 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(105vw) translateY(100vh); opacity: 0; } }
    @keyframes anim6 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(79vw) translateY(100vh); opacity: 0; } }
    @keyframes anim7 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(53vw) translateY(100vh); opacity: 0; } }
    @keyframes anim8 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(102vw) translateY(100vh); opacity: 0; } }
    @keyframes anim9 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(44vw) translateY(100vh); opacity: 0; } }
    @keyframes anim10 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(74vw) translateY(100vh); opacity: 0; } }
    @keyframes anim11 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(31vw) translateY(100vh); opacity: 0; } }
    @keyframes anim12 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(34vw) translateY(100vh); opacity: 0; } }
    @keyframes anim13 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(86vw) translateY(100vh); opacity: 0; } }
    @keyframes anim14 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(84vw) translateY(100vh); opacity: 0; } }
    @keyframes anim15 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(23vw) translateY(100vh); opacity: 0; } }
    @keyframes anim16 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(60vw) translateY(100vh); opacity: 0; } }
    @keyframes anim17 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(116vw) translateY(100vh); opacity: 0; } }
    @keyframes anim18 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(67vw) translateY(100vh); opacity: 0; } }
    @keyframes anim19 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(99vw) translateY(100vh); opacity: 0; } }
    @keyframes anim20 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(118vw) translateY(100vh); opacity: 0; } }
    @keyframes anim21 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(49vw) translateY(100vh); opacity: 0; } }
    @keyframes anim22 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(56vw) translateY(100vh); opacity: 0; } }
    @keyframes anim23 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(41vw) translateY(100vh); opacity: 0; } }
    @keyframes anim24 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(111vw) translateY(100vh); opacity: 0; } }
    @keyframes anim25 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(66vw) translateY(100vh); opacity: 0; } }
    @keyframes anim26 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(59vw) translateY(100vh); opacity: 0; } }
    @keyframes anim27 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(38vw) translateY(100vh); opacity: 0; } }
    @keyframes anim28 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(114vw) translateY(100vh); opacity: 0; } }
    @keyframes anim29 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(37vw) translateY(100vh); opacity: 0; } }
    @keyframes anim30 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(33vw) translateY(100vh); opacity: 0; } }
    @keyframes anim31 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(107vw) translateY(100vh); opacity: 0; } }
    @keyframes anim32 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(52vw) translateY(100vh); opacity: 0; } }
    @keyframes anim33 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(58vw) translateY(100vh); opacity: 0; } }
    @keyframes anim34 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(115vw) translateY(100vh); opacity: 0; } }
    @keyframes anim35 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(98vw) translateY(100vh); opacity: 0; } }
    @keyframes anim36 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(32vw) translateY(100vh); opacity: 0; } }
    @keyframes anim37 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(113vw) translateY(100vh); opacity: 0; } }
    @keyframes anim38 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(112vw) translateY(100vh); opacity: 0; } }
    @keyframes anim39 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(40vw) translateY(100vh); opacity: 0; } }
    @keyframes anim40 { 10% { opacity: 0.5; } 12% { opacity: 1; box-shadow: 0 0 3px 0 #fff; } 15% { opacity: 0.5; } 50% { opacity: 0; } 100% { transform: translateX(61vw) translateY(100vh); opacity: 0; } }

    /* Lớp phủ noise và văn bản (Giữ nguyên Z-index cao hơn starfall) */
    .stApp::after {
        content: "";
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-image: url("https://www.transparenttextures.com/patterns/noise-pattern-with-subtle-cross-lines.png");
        opacity: 0.09;
        mix-blend-mode: multiply;
        z-index: 2; /* Phải cao hơn starfall (z-index: 1) */
    }
    @keyframes fadeInBg {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    .welcome {
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
        z-index: 3; /* Phải cao hơn noise (z-index: 2) và starfall (z-index: 1) */
    }
    @keyframes textLight {
        0% { background-position: 200% 0%; }
        100% { background-position: -200% 0%; }
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: scale(0.97); }
        to { opacity: 1; transform: scale(1); }
    }
    """

    # KHỐI HTML STARFALL
    starfall_html = """
    <div class="starfall">
        <div class="falling-star"></div><div class="falling-star"></div><div class="falling-star"></div><div class="falling-star"></div>
        <div class="falling-star"></div><div class="falling-star"></div><div class="falling-star"></div><div class="falling-star"></div>
        <div class="falling-star"></div><div class="falling-star"></div><div class="falling-star"></div><div class="falling-star"></div>
        <div class="falling-star"></div><div class="falling-star"></div><div class="falling-star"></div><div class="falling-star"></div>
        <div class="falling-star"></div><div class="falling-star"></div><div class="falling-star"></div><div class="falling-star"></div>
        <div class="falling-star"></div><div class="falling-star"></div><div class="falling-star"></div><div class="falling-star"></div>
        <div class="falling-star"></div><div class="falling-star"></div><div class="falling-star"></div><div class="falling-star"></div>
        <div class="falling-star"></div><div class="falling-star"></div><div class="falling-star"></div><div class="falling-star"></div>
        <div class="falling-star"></div><div class="falling-star"></div><div class="falling-star"></div><div class="falling-star"></div>
        <div class="falling-star"></div><div class="falling-star"></div><div class="falling-star"></div><div class="falling-star"></div>
    </div>
    """

    # HIỂN THỊ CUỐI CÙNG
    st.markdown(f"""
    <style>
    {starfall_css.replace("__BG_B64__", bg_b64)}
    </style>
    
    {starfall_html}

    <div class="welcome">TỔ BẢO DƯỠNG SỐ 1</div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------------------------------------------------------------------

# ========== LUỒNG CHÍNH ==========

hide_streamlit_ui()

if "is_mobile" not in st.session_state:
    # Lấy User Agent từ JS để xác định thiết bị
    ua_string = st_javascript("window.navigator.userAgent;")
    if ua_string:
        ua = parse(ua_string)
        # Lưu trạng thái thiết bị vào session state
        st.session_state.is_mobile = not ua.is_pc
        st.rerun()  # Tải lại trang để áp dụng session_state.is_mobile
    else:
        # Nếu chưa nhận được UA, hiển thị thông báo chờ
        st.info("Đang xác định thiết bị...")
        time.sleep(1) 
        st.stop()


if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

if not st.session_state.intro_done:
    # HIỂN THỊ MÀN HÌNH INTRO
    intro_screen(st.session_state.is_mobile)
    
    # Listener JavaScript để nhận thông báo từ iframe khi hiệu ứng hoàn tất
    st.markdown("""
    <script>
    window.addEventListener("message", (event) => {
        // Kiểm tra loại thông báo từ iframe
        if (event.data.type === "intro_done") {
            // Tải lại trang chính sau khi hiệu ứng hoàn tất
            window.parent.location.reload(); 
        }
    });
    </script>
    """, unsafe_allow_html=True)
    
    # Thiết lập timeout dự phòng
    time.sleep(15)  
    st.session_state.intro_done = True
    st.rerun() # Buộc chạy lại Streamlit để chuyển sang main_page

else:
    # HIỂN THỊ TRANG CHÍNH
    main_page(st.session_state.is_mobile)
