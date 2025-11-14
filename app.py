import streamlit as st
import base64
import os
import time

# --- CẤU HÌNH BAN ĐẦU ---
st.set_page_config(
    page_title="Tổ Bảo Dưỡng Số 1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Khởi tạo session state
if 'video_ended' not in st.session_state:
    st.session_state.video_ended = False

# --- CÁC HÀM TIỆN ÍCH ---

def get_base64_encoded_file(file_path):
    """Đọc file và trả về Base64 encoded string."""
    # Sửa đường dẫn nếu cần thiết để phù hợp với môi trường triển khai
    path_to_check = os.path.join(os.path.dirname(__file__), file_path)
    if not os.path.exists(path_to_check) or os.path.getsize(path_to_check) == 0:
        return None
    try:
        with open(path_to_check, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    except Exception as e:
        st.error(f"Lỗi khi đọc file {file_path}: {str(e)}")
        return None

def set_page_style(css):
    """Áp dụng CSS style cho toàn bộ trang."""
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# Mã hóa các file media chính (bắt buộc)
try:
    # Đảm bảo các file này nằm trong thư mục gốc hoặc đường dẫn đúng
    video_base64 = get_base64_encoded_file("intro.mp4")
    bg_img_base64 = get_base64_encoded_file("bg_main.jpg")
    audio_file_base64 = get_base64_encoded_file("music/BGM.mp3")
except Exception as e:
    st.error(f"Lỗi mã hóa file media: {e}")
    video_base64 = None
    bg_img_base64 = None
    audio_file_base64 = None


# --- CSS CHÍNH CHO TOÀN BỘ ỨNG DỤNG ---
css = f"""
/* 1. Reset và Font */
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@100;300;400;700&display=swap');
* {{
    font-family: 'Roboto', sans-serif;
    transition: background-color 0.5s, color 0.5s, opacity 0.5s, transform 0.5s;
}}

/* 2. Ẩn các thành phần mặc định của Streamlit */
#MainMenu, footer {{visibility: hidden;}}

/* 3. Background chính */
.stApp {{
    background: url("data:image/jpeg;base64,{bg_img_base64}") no-repeat center center fixed !important;
    background-size: cover !important;
    min-height: 100vh; /* Đảm bảo chiều cao tối thiểu */
    position: relative;
}}

/* 4. Che nội dung chính cho đến khi video kết thúc (trạng thái mặc định) */
/* Cần class này để Streamlit không hiển thị các thành phần chính trước khi video xong */
.stApp.video-not-finished {{
    overflow: hidden;
}}

/* 5. Ẩn tiêu đề và nội dung chính khi video đang chạy */
.stApp.video-not-finished .main, 
.stApp.video-not-finished #main-title-container,
.stApp.video-not-finished #music-player-container,
.stApp.video-not-finished .nav-container
{{
    opacity: 0 !important;
    visibility: hidden !important;
    pointer-events: none !important;
    transform: translateY(20px);
}}

/* 6. Hiển thị nội dung chính sau khi video kết thúc và hiệu ứng reveal xong */
.stApp.main-content-revealed .main,
.stApp.main-content-revealed #main-title-container,
.stApp.main-content-revealed #music-player-container,
.stApp.main-content-revealed .nav-container
{{
    opacity: 1 !important;
    visibility: visible !important;
    pointer-events: auto !important;
    transform: translateY(0);
}}

/* 7. Hiệu ứng Grid Reveal */
.reveal-grid {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: grid;
    grid-template-columns: repeat(10, 1fr); /* 10 cột */
    grid-template-rows: repeat(10, 1fr); /* 10 hàng */
    z-index: 999; /* Đảm bảo trên mọi thứ */
    pointer-events: none; /* Không chặn tương tác */
}}

.reveal-cell {{
    background-color: #000; /* Màu đen hoặc màu nền bạn muốn */
    opacity: 1;
    transition: opacity 1s ease-out; /* Thời gian fade out */
}}

/* 8. Container Video */
#video-iframe-container {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 998; /* Dưới lưới reveal */
    background: black; /* Màu nền khi video chưa load */
}}

/* 9. Video iframe (tùy chỉnh cho Streamlit component) */
iframe[title="video_callback_intro"] {{
    width: 100% !important;
    height: 100% !important;
    border: none;
    opacity: 1;
    transition: opacity 0.5s, visibility 0s;
}}

/* 10. Tiêu đề Chính (Running Title) */
#main-title-container {{
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 100;
    background: rgba(0, 0, 0, 0.7);
    padding: 10px 25px;
    border-radius: 50px;
    box-shadow: 0 0 15px rgba(0, 255, 0, 0.5);
}}
#main-title-container h1 {{
    font-size: 2.5rem;
    color: #00FF00;
    margin: 0;
    text-shadow: 0 0 5px #00FF00;
}}

/* 11. Music Player */
#music-player-container {{
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 100;
    background: rgba(0, 0, 0, 0.8);
    padding: 10px 20px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    box-shadow: 0 0 15px rgba(0, 255, 0, 0.5);
}}
.controls .control-btn {{
    background: #111;
    border: 1px solid #00FF00;
    color: #00FF00;
    padding: 5px 10px;
    margin: 0 5px;
    cursor: pointer;
    border-radius: 5px;
}}
.progress-container {{
    width: 150px;
    height: 5px;
    background: #333;
    margin: 0 10px;
    border-radius: 2.5px;
    cursor: pointer;
}}
.progress-bar {{
    height: 100%;
    width: 0%;
    background: #00FF00;
    border-radius: 2.5px;
}}
.time-info span {{
    color: #00FF00;
    font-size: 0.8rem;
    margin: 0 2px;
}}

/* 12. Navigation Button (UIverse Style) */
.nav-container {{
    position: fixed;
    top: 100px;
    right: 20px;
    z-index: 100;
}}
.button {{
    --color: #00FF00;
    --hover: #222;
    --hover-text: #00FF00;
    --size: 100px; /* Tăng kích thước nút */
    -webkit-tap-highlight-color: transparent;
    cursor: pointer;
    background: #000;
    border: 3px solid var(--color);
    width: var(--size);
    height: var(--size);
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    position: relative;
    border-radius: 30%;
}}
.button span {{
    font-size: 1.1em;
    font-weight: 700;
    color: var(--color);
    z-index: 1;
    position: relative;
}}
.dots_container {{
    opacity: 0;
    filter: url(#goo);
    position: absolute;
    width: 100%;
    height: 100%;
}}
.dot {{
    position: absolute;
    width: 12px;
    height: 12px;
    background: var(--color);
    border-radius: 50%;
    top: 0;
    left: 0;
    transform: translate(-50%, -50%);
    transition: transform 0.3s ease-in-out, background 0.3s ease-in-out;
}}
.button:hover .dots_container {{
    opacity: 1;
}}
.button:hover span {{
    color: var(--hover-text);
    transform: scale(0.9);
}}
.button:hover {{
    background: var(--hover);
}}
.button:hover .dot:nth-child(1) {{ transform: translate(150%, 150%); }}
.button:hover .dot:nth-child(2) {{ transform: translate(500%, 150%); }}
.button:hover .dot:nth-child(3) {{ transform: translate(500%, 500%); }}
.button:hover .dot:nth-child(4) {{ transform: translate(150%, 500%); }}
"""
set_page_style(css)

# Thêm class để ẩn nội dung chính ban đầu
st.markdown('<div class="reveal-grid"></div>', unsafe_allow_html=True)
st.markdown('<div id="video-iframe-container"></div>', unsafe_allow_html=True)
st.markdown('<div id="music-audio-container" style="display: none;"></div>', unsafe_allow_html=True) # Container cho Audio

# --- LOGIC XỬ LÝ VIDEO VÀ HIỆU ỨNG TRONG IFRAME (JAVASCRIPT) ---
js_callback_video = f"""
<script>
    // --- KHAI BÁO CÁC HÀM CƠ BẢN ---
    const stApp = window.parent.document.querySelector('.stApp');
    const audioContainer = window.parent.document.querySelector('#music-audio-container');
    const musicBase64 = "{audio_file_base64}";
    let audio = null;
    let isPlaying = false;
    let musicPlayerInitialized = false;

    function initMusicPlayer() {{
        if (musicPlayerInitialized) return;
        musicPlayerInitialized = true;
        
        if (musicBase64) {{
            audio = new Audio('data:audio/mp3;base64,' + musicBase64);
            audio.loop = true;
            audioContainer.appendChild(audio);
            
            // Khởi tạo các nút điều khiển (dựa trên các id trong HTML)
            const playPauseBtn = window.parent.document.querySelector('#play-pause-btn');
            
            if(playPauseBtn) {{
                playPauseBtn.onclick = () => {{
                    if (isPlaying) {{
                        audio.pause();
                        playPauseBtn.textContent = '▶';
                    }} else {{
                        audio.play().catch(e => console.error("Error playing audio:", e));
                        playPauseBtn.textContent = '⏸';
                    }}
                    isPlaying = !isPlaying;
                }};
            }}
            
            // Tự động phát sau 100ms
            setTimeout(() => {{
                if (stApp.classList.contains('main-content-revealed')) {{
                    playPauseBtn.click(); // Kích hoạt phát nhạc (sau khi video xong)
                }}
            }}, 100);
        }}
        console.log("Music Player Initialized.");
    }}

    function initRevealEffect() {{
        const revealGrid = window.parent.document.querySelector('.reveal-grid');
        if (!revealGrid) return;

        const cells = Array.from(revealGrid.querySelectorAll('.reveal-cell'));
        
        cells.forEach((cell, index) => {{
            setTimeout(() => {{
                cell.style.opacity = '0';
            }}, index * 10); // Hiệu ứng quét nhanh 
        }});

        // Sau khi hiệu ứng hoàn tất, xóa lưới
        setTimeout(() => {{
            revealGrid.remove();
        }}, 1000); // Đợi 1s để hoàn tất fade
        
        console.log("Reveal Effect Initialized.");
    }}

    function sendBackToStreamlit() {{
        console.log("Video ended or skipped, revealing main content");
        
        // 1. Gửi tín hiệu về Streamlit (Dùng Streamlit.setComponentValue nếu là custom component, nhưng ở đây dùng logic CSS)
        if (stApp) {{
            stApp.classList.add('video-finished', 'main-content-revealed');
            stApp.classList.remove('video-not-finished'); 
        }}
        
        // 2. Kích hoạt hiệu ứng reveal
        initRevealEffect();
        
        // 3. Khởi tạo Music Player sau khi hiệu ứng bắt đầu
        setTimeout(initMusicPlayer, 100); 
    }}
    
    // --- ✅ LOGIC MỚI: KIỂM TRA THAM SỐ SKIP_INTRO ---
    const urlParams = new URLSearchParams(window.parent.location.search);
    const skipIntro = urlParams.get('skip_intro');
    
    if (skipIntro === '1') {{
        console.log("Skip intro detected. Directly revealing main content and skipping reveal effect.");
        
        // 1. Kích hoạt trạng thái video-finished và main-content-revealed trên .stApp
        if (stApp) {{
            stApp.classList.add('video-finished', 'main-content-revealed');
            stApp.classList.remove('video-not-finished');
        }}

        // 2. Loại bỏ lưới reveal grid ngay lập tức (BỎ QUA HIỆU ỨNG REVEAL CHẬM)
        const revealGrid = window.parent.document.querySelector('.reveal-grid');
        if (revealGrid) {{
            revealGrid.remove();
            console.log("Reveal grid removed instantly.");
        }}
        
        // 3. Khởi tạo Music Player ngay lập tức
        initMusicPlayer();

        // 4. Ẩn iframe video ngay lập tức
        const iframe = window.frameElement;
        if (iframe) {{
            iframe.style.opacity = 0;
            iframe.style.visibility = 'hidden';
            iframe.style.pointerEvents = 'none';
            console.log("Video iframe hidden instantly.");
        }}
        
        return; // Dừng mọi hoạt động khởi tạo video/audio/event listeners
    }}

    // --- LOGIC VIDEO BÌNH THƯỜNG ---
    const videoBase64 = "{video_base64}";
    const iframe = window.frameElement;
    
    if (videoBase64) {{
        // Tạo video element
        const video = document.createElement('video');
        video.src = 'data:video/mp4;base64,' + videoBase64;
        video.autoplay = true;
        video.muted = true; // Bắt buộc để autoplay hoạt động
        video.playsInline = true;
        video.style.width = '100%';
        video.style.height = '100%';
        video.style.objectFit = 'cover';
        video.style.opacity = 1;
        video.style.transition = 'opacity 1s';
        
        // Chèn video vào body của iframe
        document.body.appendChild(video);
        document.body.style.margin = '0';
        document.body.style.overflow = 'hidden';

        // Lắng nghe sự kiện kết thúc
        video.onended = () => {{
            console.log("Video Ended.");
            
            // Ẩn iframe video một cách mượt mà
            if (iframe) {{
                iframe.style.opacity = 0;
                setTimeout(() => {{
                    iframe.style.visibility = 'hidden';
                    iframe.style.pointerEvents = 'none';
                }}, 500); // Đợi fade out
            }}

            // Bắt đầu hiệu ứng reveal và hiển thị nội dung chính
            sendBackToStreamlit();
        }};
        
        // Tự động phát
        video.play().catch(e => {{
            console.error("Auto-play failed:", e);
            // Có thể hiển thị nút Play nếu auto-play bị chặn
            // sendBackToStreamlit(); // Hoặc bỏ qua video nếu không thể tự động phát
        }});
        
    }} else {{
        console.log("Video Base64 not found, skipping video and revealing content.");
        // Nếu không có video, chuyển thẳng
        setTimeout(sendBackToStreamlit, 500); 
    }}
    
    // Khởi tạo các ô lưới reveal
    const revealGrid = window.parent.document.querySelector('.reveal-grid');
    if (revealGrid) {{
        for (let i = 0; i < 100; i++) {{ // 10x10 = 100 ô
            const cell = document.createElement('div');
            cell.classList.add('reveal-cell');
            revealGrid.appendChild(cell);
        }}
    }}
</script>
"""

# Thêm logic để kiểm tra nếu đã video đã chạy xong (để reload trang không phải xem lại)
if st.session_state.video_ended:
    st.markdown(f'<script>window.onload = function() {{ if(window.parent.document.querySelector(".stApp")) {{ window.parent.document.querySelector(".stApp").classList.add("video-finished", "main-content-revealed"); }} if(window.parent.document.querySelector(".reveal-grid")) {{ window.parent.document.querySelector(".reveal-grid").remove(); }} }};</script>', unsafe_allow_html=True)
else:
    # Nếu chưa chạy xong, nhúng iframe video và logic
    import streamlit.components.v1 as components
    components.html(
        js_callback_video,
        height=0, # Ẩn component, chỉ dùng để chạy script trong iframe
        width=0,
        scrolling=False,
        key="video_callback_intro"
    )
    # Cần set state sau khi component chạy xong (vì component chạy bất đồng bộ)
    st.session_state.video_ended = True # Đặt là True để lần sau reload không chạy lại video

# --- TIÊU ĐỀ CHÍNH (FIXED TRÊN CÙNG MÀU) ---
main_title_text = "TỔ BẢO DƯỠNG SỐ 1"

# Nhúng tiêu đề
st.markdown(f"""
<div id="main-title-container">
    <h1>{main_title_text}</h1>
</div>
""", unsafe_allow_html=True)

# --- MUSIC PLAYER ---
music_files = ["music/BGM.mp3"] # Dùng để kiểm tra len
if len(music_files) > 0:
    st.markdown("""
<div id="music-player-container">
    <div class="controls">
        <button class="control-btn" id="prev-btn">⏮</button>
        <button class="control-btn play-pause" id="play-pause-btn">▶</button>
        <button class="control-btn" id="next-btn">⏭</button>
    </div>
    <div class="progress-container" id="progress-container">
        <div class="progress-bar" id="progress-bar"></div>
    </div>
    <div class="time-info">
        <span id="current-time">0:00</span>
        <span id="duration">0:00</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- NAVIGATION BUTTON MỚI (UIverse Style) ---
# Tên trang phụ là partnumber.py nên link href là /partnumber
st.markdown("""
<div class="nav-container">
    <a href="/partnumber" target="_self" class="button">
        <div class="dots_container">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
        <span>TRA CỨU PN</span>
    </a>
</div>
""", unsafe_allow_html=True)

# --- NỘI DUNG CHÍNH (Được hiển thị sau khi video xong) ---
# ... (Phần nội dung chính của trang chủ app.txt) ...
st.markdown("""
<div class="main-content-area" style="padding-top: 150px; padding-bottom: 50px;">
    <h2 style="color: white; text-align: center; margin-bottom: 50px;">Chào mừng đến với Hệ Thống Tra Cứu Nội Bộ</h2>
    <div style="max-width: 800px; margin: auto; padding: 20px; background: rgba(0, 0, 0, 0.7); border-radius: 10px; border: 1px solid #00FF00;">
        <p style="color: #00FF00; line-height: 1.8;">
        Hệ thống này được xây dựng để cung cấp thông tin tra cứu Part Number nhanh chóng và chính xác cho đội ngũ kỹ thuật.
        Vui lòng sử dụng các chức năng ở menu bên phải để truy cập các công cụ hỗ trợ.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
# ...
