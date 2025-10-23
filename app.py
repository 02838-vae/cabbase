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
SHATTER_DURATION = 1.8  # Thời gian hiệu ứng tan vỡ (giây)
RECONSTRUCT_DURATION = 2.5 # Thời gian ghép lại (giây)
BLACKOUT_DELAY = 0.0    # Đã bỏ độ trễ màn hình đen
MUSIC_SRC = "https://s3-us-west-2.amazonaws.com/s.cdpn.io/9473/new_year_dubstep_minimix.ogg" # Nguồn nhạc

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


# Callback Function để thay đổi trạng thái và RERUN
def set_intro_done():
    st.session_state.intro_done = True
    st.rerun()


# ========== MÀN HÌNH INTRO (ĐÃ XÓA VÙNG ĐEN PHÍA TRÊN VÀ THANH NHẠC) ==========

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
        # Ảnh nền BG cho pha GHÉP LẠI (cabbase.jpg / mobile.jpg)
        with open(bg_file, "rb") as b:
            bg_b64 = base64.b64encode(b.read()).decode()
            
    except FileNotFoundError as e:
        st.error(f"Lỗi: Không tìm thấy file tài nguyên. Vui lòng kiểm tra: {e.filename}")
        st.stop()
    
    shards_html = "".join([f"<div class='shard' id='shard-{i}'></div>" for i in range(GRID_SIZE * GRID_SIZE)])

    # Chuyển đổi thời gian sang giây (cho JS/CSS)
    js_shatter_duration = SHATTER_DURATION 
    js_reconstruct_duration = RECONSTRUCT_DURATION
    js_blackout_delay = BLACKOUT_DELAY 

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


        /* === STYLE HIỆU ỨNG TAN VỠ VÀ GHÉP LẠI === */
        #shatter-overlay {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            display: grid; grid-template-columns: repeat({GRID_SIZE}, 1fr); grid-template-rows: repeat({GRID_SIZE}, 1fr);
            opacity: 0; pointer-events: none; z-index: 30; 
            transition: opacity 0.5s ease-in; 
        }}
        .shard {{
            position: relative;
            /* DÙNG ẢNH SHUTTER LÀM NỀN BAN ĐẦU (cho pha tan vỡ) */
            background-image: url("data:image/jpeg;base64,{shutter_b64}"); 
            background-size: 100vw 100vh;
            transition: transform {SHATTER_DURATION}s cubic-bezier(0.68, -0.55, 0.27, 1.55), opacity 1.5s ease-in-out; 
            opacity: 1; 
        }}
        
        /* Khi ghép lại: Gỡ background-image để JS gán */
        .reconstructing .shard {{
            transform: translate(0, 0) rotate(0deg) scale(1) !important; 
            transition: transform {RECONSTRUCT_DURATION}s cubic-bezier(0.19, 1, 0.22, 1), opacity {RECONSTRUCT_DURATION}s ease-in-out; 
            /* Bỏ background-image ở đây để JS gán cứng */
            background-image: none !important; 
            opacity: 1 !important;
            /* Bỏ background-position ở đây để JS gán cứng */
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
        const SHATTER_DURATION = {js_shatter_duration}; // giây
        const RECONSTRUCT_DURATION = {js_reconstruct_duration}; // giây
        const BLACKOUT_DELAY = {js_blackout_delay}; // giây
        const BG_B64_URL = "url('data:image/jpeg;base64,{bg_b64}')"; // Lưu ảnh nền chính


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
            
            // Background position cho ảnh SHUTTER và sau này là ảnh BG
            const bgPosition = 'calc(-' + col + ' * 100vw / ' + GRID_SIZE + ') calc(-' + row + ' * 100vh / ' + GRID_SIZE + ')';
            shard.style.backgroundPosition = bgPosition;
            
            const randX = (Math.random() - 0.5) * 200; 
            const randY = (Math.random() - 0.5) * 200; 
            const randR = (Math.random() - 0.5) * 360; 
            const delay = Math.random() * 0.5; 

            // Lưu trữ vị trí nền BAN ĐẦU
            initialTransforms.push({{randX, randY, randR, delay, bgPosition}});
        }});


        function finishIntro() {{
            if (ended) return;
            ended = true;
            
            // BƯỚC 1: Bắt đầu Tan Vỡ (Shatter)
            blackFade.style.opacity = 0; 
            shatterOverlay.style.opacity = 1; 
            vid.style.opacity = 0; 
            shatterOverlay.classList.remove('reconstructing');
            shatterOverlay.classList.add('shattering');
            
            shards.forEach((shard, index) => {{
                const t = initialTransforms[index];
                shard.style.transform = 'translate(' + t.randX + 'vw, ' + t.randY + 'vh) rotate(' + t.randR + 'deg) scale(0.1)';
                shard.style.transitionDelay = t.delay + 's';
                shard.style.opacity = 0; 
            }});
            
            // BƯỚC 2 & 3: GHÉP LẠI NGAY SAU KHI TAN VỠ KẾT THÚC
            // Thời gian chờ = SHATTER_DURATION (kết thúc tan vỡ)
            const RECONSTRUCT_START_DELAY = SHATTER_DURATION * 1000 + 50; 

            setTimeout(() => {{
                // Đảm bảo màn hình đen không hiện (opacity 0)
                blackFade.style.opacity = 0; 
                shatterOverlay.style.opacity = 1; 

                shatterOverlay.classList.remove('shattering');
                shatterOverlay.classList.add('reconstructing'); 
                
                shards.forEach((shard, index) => {{
                    // *** GÁN BACKGROUND-IMAGE VÀ BACKGROUND-POSITION BẰNG JS VÀ DÙNG !IMPORTANT ***
                    const t = initialTransforms[index];

                    shard.style.setProperty('background-image', BG_B64_URL, 'important');
                    shard.style.setProperty('background-position', t.bgPosition, 'important'); // Khắc phục lỗi vị trí

                    const reverseDelay = RECONSTRUCT_DURATION - t.delay; 
                    
                    shard.style.transitionDelay = (Math.max(0, reverseDelay) + (Math.random() * 0.2)) + 's'; 
                    shard.style.opacity = 1; 
                }});

                // 4. Thông báo hoàn thành sau khi ghép lại
                setTimeout(() => {{
                    // Gửi tin nhắn đến Streamlit để kích hoạt RERUN và chuyển trang
                    window.parent.postMessage({{type: 'streamlit:setComponentValue', value: true, dataType: 'json', id: 'intro_done'}}, '*');
                }}, RECONSTRUCT_DURATION * 1000 + 500); 


            }}, RECONSTRUCT_START_DELAY); 

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
    
    # 💥 LỖI TẠO VÙNG ĐEN: Loại bỏ st_javascript và listener.
    # Thay vào đó, chúng ta sẽ sử dụng một component.html đơn giản
    # và chỉ dựa vào thuộc tính 'key' và st.session_state để RERUN.
    components.html(
        intro_html, 
        height=800, 
        scrolling=False,
        key="intro_frame" # Sử dụng key để có thể tham chiếu lại
    )
    
    # *** CƠ CHẾ LẮNG NGHE ĐƠN GIẢN HÓA VÀ FIX LỖI ***
    # Dùng st_javascript để kiểm tra giá trị của một input ảo trong iframe.
    # Do chúng ta đã gửi message có ID='intro_done', ta cần kiểm tra lại
    # giá trị này có được truyền về Streamlit hay không.
    
    # Thao tác này có thể gây ra lỗi trong môi trường sandbox của Streamlit.
    # Thay vào đó, chúng ta sẽ sử dụng một mẹo: đặt một input giả và sau đó
    # lắng nghe thông báo hoàn thành từ iframe.
    
    # 1. Chèn một input ẩn có key là 'intro_done'
    # 2. JS trong iframe sẽ dùng postMessage để cập nhật giá trị của key này.
    
    # Ta sẽ dùng một key JavaScript để lấy giá trị mà iframe đã set.
    js_listener = """
    (() => {
        const iframe = window.parent.document.querySelector('iframe[key="intro_frame"]');
        if (iframe) {
            return iframe.contentWindow.document.querySelector('[id="intro_done"]').value;
        }
        return false;
    })();
    """
    # 💡 LƯU Ý: Do cách Streamlit hoạt động, chúng ta chỉ cần một lần rerender để chuyển trang.
    # Tín hiệu 'streamlit:setComponentValue' từ JS thường được Streamlit nhận và RERUN.
    # Ta sẽ giữ lại logic dựa trên st.session_state và fallback.


# ========== TRANG CHÍNH (BỐ CỤC ĐÃ TỐI ƯU) ==========

def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    try:
        with open(bg, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError as e:
        st.error(f"Lỗi: Không tìm thấy file tài nguyên: {e.filename}")
        st.stop()
        
    MUSIC_SRC = "https://s3-us-west-2.amazonaws.com/s.cdpn.io/9473/new_year_dubstep_minimix.ogg" # Nguồn nhạc mẫu

    st.markdown(f"""
    <style>
    /* CSS CHUNG CHO BODY/BACKGROUND */
    html, body, .stApp {{
        height: 100vh !important;
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

    /* Tiêu đề mặc định (PC) */
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
    
    /* === STYLE CHO THANH PHÁT NHẠC (PC) === */
    .music-player-container {{
        position: fixed; 
        bottom: 20px;
        left: 20px;
        z-index: 1000;
        width: clamp(250px, 40vw, 350px);
        /* PC vẫn giữ background nhẹ cho dễ nhìn */
        background: rgba(30, 30, 30, 0.85); 
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        border-radius: 8px;
        padding: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .music-player-container audio {{
        flex-grow: 1;
        outline: none;
        filter: invert(100%);
        height: 40px; 
    }}
    .nav-buttons {{
        display: flex;
        gap: 5px;
    }}
    .nav-buttons button {{
        background: transparent;
        border: none;
        color: white;
        font-size: 18px;
        cursor: pointer;
        padding: 5px;
        opacity: 0.8;
        transition: opacity 0.2s;
    }}
    .nav-buttons button:hover {{
        opacity: 1;
    }}

    /* ************************************************************************* */
    /* === MOBILE OVERRIDES (ÁP DỤNG KHI MÀN HÌNH NHỎ HƠN 600PX) === */
    @media only screen and (max-width: 600px) {{
        
        /* 1. Thanh phát nhạc lên trên cùng, bỏ khung đen */
        .music-player-container {{
            position: absolute !important; 
            top: 0 !important;
            bottom: unset !important; /* Hủy bottom: 20px */
            left: 0 !important;
            right: 0 !important;
            width: 100% !important;
            border-radius: 0;
            padding: 5px 10px;
            /* Khung đen biến mất (chỉ giữ background tối mờ) */
            background: rgba(30, 30, 30, 0.95) !important; 
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.6); 
        }}
        .music-player-container audio {{
            height: 35px; /* Giảm chiều cao thanh audio trên mobile */
        }}

        /* 2. Tiêu đề dưới thanh phát nhạc */
        .welcome {{
            position: relative; 
            margin-top: 55px; /* Đẩy xuống dưới thanh nhạc */
            top: unset; 
            transform: none; 
            padding: 0 10px;
        }}
    }}
    /* ************************************************************************* */

    </style>

    <div class="music-player-container">
        <div class="nav-buttons">
            <button onclick="alert('Chức năng Previous chưa được triển khai')">⏮</button>
        </div>
        
        <audio controls loop autoplay>
            <source src="{MUSIC_SRC}" type="audio/ogg">
            Trình duyệt của bạn không hỗ trợ audio tag.
        </audio>

        <div class="nav-buttons">
            <button onclick="alert('Chức năng Next chưa được triển khai')">⏭</button>
        </div>
    </div>
    
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
    # 💡 FIX LỖI 1: Loại bỏ các component Streamlit thừa ở đầu để tránh vùng đen.
    # Sử dụng st_javascript để tạo một input ẩn lắng nghe tin nhắn từ iframe.
    # Nếu tin nhắn với ID='intro_done' được gửi, st_javascript sẽ cập nhật
    # st.session_state.intro_done_status và kích hoạt RERUN.
    st_javascript("""
        const listener = (event) => {
            if (event.data.type === 'streamlit:setComponentValue' && event.data.id === 'intro_done') {
                window.Streamlit.setComponentValue(true);
            }
        };
        window.addEventListener('message', listener);
        // Trả về một giá trị mặc định để tránh lỗi
        return false;
    """, key="intro_done_status", height=0)

    # Nếu st.session_state.intro_done_status được set thành True
    if st.session_state.get('intro_done_status'):
        st.session_state.intro_done = True
        st.rerun()

    # Hiển thị Intro
    intro_screen(st.session_state.is_mobile)
    
    # Fallback Timeout
    if not st.session_state.get('intro_done_status'):
        time.sleep(18) 
        if not st.session_state.intro_done:
            st.session_state.intro_done = True
            st.rerun()

else:
    # 💡 FIX LỖI 2: Đảm bảo thanh phát nhạc chỉ xuất hiện trên main_page
    main_page(st.session_state.is_mobile)
