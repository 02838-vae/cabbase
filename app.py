import streamlit as st
import base64
import os
import re 

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
        # Trong môi trường Streamlit, st.error có thể không hiển thị nếu lỗi xảy ra quá sớm
        # print(f"Lỗi khi đọc file {file_path}: {str(e)}") 
        return None


# Mã hóa các file media chính (bắt buộc)
try:
    # Đảm bảo các file này nằm cùng thư mục với app.py
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
    
    # MÃ HÓA CHO LOGO
    logo_base64 = get_base64_encoded_file("logo.jpg")

    # Kiểm tra file bắt buộc
    missing_files = []
    if not video_pc_base64: missing_files.append("airplane.mp4")
    if not video_mobile_base64: missing_files.append("mobile.mp4")
    if not audio_base64: missing_files.append("plane_fly.mp3")
    if not bg_pc_base64: missing_files.append("cabbase.jpg")
    if not bg_mobile_base64: missing_files.append("mobile.jpg")

    if missing_files:
        st.error(f"⚠️ Thiếu các file media cần thiết hoặc file rỗng. Vui lòng kiểm tra lại các file sau trong thư mục:")
        st.write(" - " + "\n - ".join(missing_files))
        st.stop()
        
except Exception as e:
    st.error(f"❌ Lỗi khi đọc file: {str(e)}")
    st.stop()

# Đảm bảo logo_base64 được khởi tạo nếu file không tồn tại
if not 'logo_base64' in locals() or not logo_base64:
    logo_base64 = "" 
    st.info("ℹ️ Không tìm thấy file logo.jpg. Music player sẽ không có hình nền logo.")


# --- SỬ DỤNG URL TRỰC TIẾP TỪ GITHUB RAW CONTENT (TỐC ĐỘ CAO HƠN) ---
BASE_MUSIC_URL = "https://raw.githubusercontent.com/02838-vae/cabbase/main/"
music_urls = []

# Thêm 6 file nhạc nền vào danh sách URL
for i in range(1, 7):
    url = f"{BASE_MUSIC_URL}background{i}.mp3"
    music_urls.append(url)
    
music_files = music_urls 

if len(music_files) == 0:
    st.info("ℹ️ Không tìm thấy URL nhạc nền. Music player sẽ không hoạt động.")


# --- PHẦN 1: NHÚNG FONT BẰNG THẺ LINK TRỰC TIẾP VÀO BODY ---
font_links = """
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
"""
st.markdown(font_links, unsafe_allow_html=True)

# --- PHẦN 2: CSS CHÍNH (STREAMLIT APP) ---
# Đảm bảo tất cả ngoặc nhọn CSS đều được thoát: {{ và }}
hide_streamlit_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sacramento&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');
/* Ẩn các thành phần mặc định của Streamlit */
#MainMenu, footer, header {{visibility: hidden;}}

.main {{
    padding: 0;
    margin: 0;
}}

div.block-container {{
    padding: 0;
    margin: 0;
    max-width: 100% !important;
}}

/* BỔ SUNG: Chặn hành vi dblclick và chọn văn bản trên toàn bộ ứng dụng khi video đang chạy */
.stApp.video-running * {{
    user-select: none;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    cursor: default !important; /* Đảm bảo con trỏ không thay đổi */
}}

/* Iframe Video Intro */
iframe:first-of-type {{
    transition: opacity 1s ease-out, visibility 1s ease-out;
    opacity: 1;
    visibility: visible;
    width: 100vw !important;
    height: 100vh !important;
    position: fixed;
    top: 0;
    left: 0;
    /* Tăng Z-index để đảm bảo video ở trên cùng */
    z-index: 1000;
    /* FIX: Cho phép tương tác click/touch trên iframe để bắt sự kiện */
    pointer-events: all;
}}

.video-finished iframe:first-of-type {{
    opacity: 0;
    visibility: hidden;
    /* Đảm bảo iframe không chặn tương tác sau khi kết thúc */
    pointer-events: none; 
    height: 1px !important;
    width: 1px !important;
}}

.stApp {{
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
    --logo-bg-url: url('data:image/jpeg;base64,{logo_base64}');
}}

.reveal-grid {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    display: grid;
    grid-template-columns: repeat(20, 1fr);
    grid-template-rows: repeat(12, 1fr);
    z-index: 500;
    pointer-events: none;
}}

.grid-cell {{
    background-color: white;
    opacity: 1;
    transition: opacity 0.5s ease-out;
}}

.main-content-revealed {{
    background-image: var(--main-bg-url-pc);
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    filter: sepia(60%) grayscale(20%) brightness(85%) contrast(110%);
    transition: filter 2s ease-out;
}}

@media (max-width: 768px) {{
    .main-content-revealed {{
        background-image: var(--main-bg-url-mobile);
    }}
    .reveal-grid {{
        grid-template-columns: repeat(10, 1fr);
        grid-template-rows: repeat(20, 1fr);
    }}
}}

/* Keyframes cho hiệu ứng chữ chạy đơn */
@keyframes scrollText {{
    0% {{ transform: translate(100vw, 0); }}
    100% {{ transform: translate(-100%, 0); }}
}}

/* Keyframes cho hiệu ứng Đổi Màu Gradient */
@keyframes colorShift {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

/* === TIÊU ĐỀ TRANG CHÍNH === */
#main-title-container {{
    position: fixed;
    top: 5vh;
    left: 0;
    width: 100%;
    height: 10vh;
    overflow: hidden;
    z-index: 20;
    pointer-events: none;
    opacity: 0;
    transition: opacity 2s;
}}

.video-finished #main-title-container {{
    opacity: 1;
}}

#main-title-container h1 {{
    font-family: 'Playfair Display', serif;
    font-size: 3.5vw;
    margin: 0;
    font-weight: 900;
    font-feature-settings: "lnum" 1;
    letter-spacing: 5px;
    white-space: nowrap;
    display: inline-block;
    animation: scrollText 15s linear infinite;
    background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
    background-size: 400% 400%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    color: transparent;
    animation: colorShift 10s ease infinite, scrollText 15s linear infinite;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}}

@media (max-width: 768px) {{
    #main-title-container {{
        height: 8vh;
        width: 100%;
        left: 0;
    }}
    
    #main-title-container h1 {{
        font-size: 6.5vw;
        animation-duration: 8s;
    }}
}}


/* 🌟 KEYFRAMES: HIỆU ỨNG TỎA SÁNG MÀU NGẪU NHIÊN (Giữ nguyên cho Music Player) */
@keyframes glow-random-color {{
    0%, 57.14%, 100% {{
        box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.3);
    }}
    
    0% {{
        box-shadow: 0 0 10px 4px rgba(255, 0, 0, 0.9), 0 0 20px 8px rgba(255, 0, 0, 0.6), inset 0 0 5px 2px rgba(255, 0, 0, 0.9);
    }}
    
    14.28% {{ 
        box-shadow: 0 0 10px 4px rgba(0, 255, 0, 0.9), 0 0 20px 8px rgba(0, 255, 0, 0.6), inset 0 0 5px 2px rgba(0, 255, 0, 0.9);
    }}
    
    28.56% {{ 
        box-shadow: 0 0 10px 4px rgba(0, 0, 255, 0.9), 0 0 20px 8px rgba(0, 0, 255, 0.6), inset 0 0 5px 2px rgba(0, 0, 255, 0.9);
    }}

    42.84% {{ 
        box-shadow: 0 0 10px 4px rgba(255, 255, 0, 0.9), 0 0 20px 8px rgba(255, 255, 0, 0.6), inset 0 0 5px 2px rgba(255, 255, 0, 0.9);
    }}
    
    57.14% {{ 
        box-shadow: 0 0 10px 4px rgba(255, 0, 255, 0.9), 0 0 20px 8px rgba(255, 0, 255, 0.6), inset 0 0 5px 2px rgba(255, 0, 255, 0.9);
    }}
}}


/* === MUSIC PLAYER STYLES (Giữ nguyên) === */
#music-player-container {{
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 350px; 
    padding: 8px 16px; 
    background: rgba(0, 0, 0, 0.7); 
    border-radius: 12px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7);
    z-index: 999;
    opacity: 0;
    transform: translateY(100px);
    transition: opacity 1s ease-out 2s, transform 1s ease-out 2s;
    position: fixed;
}}

#music-player-container::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    margin: -3px;
    width: calc(100% + 6px);
    height: calc(100% + 6px);
    
    background-image: var(--logo-bg-url);
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    filter: contrast(110%) brightness(90%);
    opacity: 0.4; 
    z-index: -1; 
    
    border-radius: 12px;
    
    box-sizing: border-box; 
    animation: glow-random-color 7s linear infinite;
}}

/* Đảm bảo các thành phần con ở trên lớp giả */
#music-player-container * {{
    position: relative;
    z-index: 5; 
}}

.video-finished #music-player-container {{
    opacity: 1;
    transform: translateY(0);
}}

/* Các style khác của player (giữ nguyên) */
#music-player-container .controls,
#music-player-container .time-info {{
    color: #fff;
    text-shadow: 0 0 7px #000;
}}

#music-player-container .controls {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin-bottom: 6px; 
}}

#music-player-container .control-btn {{
    background: rgba(255, 255, 255, 0.2);
    border: 2px solid #FFFFFF; 
    color: #FFD700;
    width: 32px; 
    height: 32px;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    font-size: 14px;
}}

#music-player-container .control-btn:hover {{
    background: rgba(255, 215, 0, 0.5);
    transform: scale(1.15);
}}

#music-player-container .control-btn.play-pause {{
    width: 40px; 
    height: 40px;
    font-size: 18px;
}}

#music-player-container .progress-container {{
    width: 100%;
    height: 5px; 
    background: rgba(0, 0, 0, 0.5);
    border-radius: 3px;
    cursor: pointer;
    margin-bottom: 4px; 
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.4); 
}}

#music-player-container .progress-bar {{
    height: 100%;
    background: linear-gradient(90deg, #FFD700, #FFA500);
    border-radius: 3px;
    width: 0%;
    transition: width 0.1s linear;
}}

#music-player-container .time-info {{
    display: flex;
    justify-content: space-between;
    color: rgba(255, 255, 255, 1);
    font-size: 10px; 
    font-family: monospace;
}}

@media (max-width: 768px) {{
    #music-player-container {{
        width: calc(100% - 40px);
        right: 20px;
        left: 20px;
        bottom: 15px;
        padding: 8px 12px;
    }}
    #music-player-container .control-btn,
    #music-player-container .control-btn.play-pause {{
        width: 36px;
        height: 36px;
        font-size: 16px;
    }}
    #music-player-container .control-btn.play-pause {{
        width: 44px;
        height: 44px;
        font-size: 20px;
    }}
}}

/* === CSS MỚI CHO NAVIGATION BUTTON (UIverse Dark Mode) === */

/* SỬ DỤNG FLEXBOX CHO WRAPPER ĐỂ ĐỊNH VỊ 2 NÚT */
#nav-buttons-wrapper {{
    position: fixed;
    top: 50%;
    left: 0;
    width: 100%; 
    transform: translateY(-50%);
    
    display: flex;
    justify-content: space-between; 
    align-items: center;
    padding: 0 80px; 
    
    opacity: 0;
    /* CHỈNH SỬA QUAN TRỌNG: Tăng độ trễ lên 5s để chắc chắn intro và reveal kết thúc */
    transition: opacity 2s ease-out 5s; 
    z-index: 10000;
    /* CHỈNH SỬA QUAN TRỌNG: Chặn tương tác click cho đến khi hiển thị hoàn toàn */
    pointer-events: none;
}}

.nav-container,
.nav-container-right {{
    position: static; 
    left: unset;
    right: unset;
    top: unset;
    transform: none; 
    padding: 0;
    opacity: 1 !important; 
    transition: none !important;
    display: flex; 
    justify-content: center;
    align-items: center;
}}

/* CHỈNH SỬA QUAN TRỌNG: Khi video kết thúc, hiện opacity và cho phép click */
.video-finished #nav-buttons-wrapper {{
    opacity: 1;
    pointer-events: all;
}}

/* KHỞI TẠO CÁC BIẾN CSS (Giữ nguyên) */
.button {{
    --black-700: hsla(0, 0%, 12%, 1);
    --border_radius: 9999px; 
    --transtion: 0.3s ease-in-out;
    --active: 0; 
    --hover-color: hsl(40, 60%, 85%);
    --text-color: hsl(0, 0%, 100%); 
    
    cursor: pointer;
    position: relative;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transform-origin: center;
    padding: 1rem 2rem;
    background-color: transparent;
    border: none;
    border-radius: var(--border_radius);
    
    transform: scale(calc(1 + (var(--active, 0) * 0.2)));
    transition: transform var(--transtion);
    
    text-decoration: none; 
}}

/* NỀN ĐEN CỦA BUTTON (Giữ nguyên) */
.button::before {{
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 100%;
    height: 100%;
    background-color: var(--black-700);
    border-radius: var(--border_radius);
    box-shadow: 
        inset 0 0.5px hsl(0, 0%, 100%), 
        inset 0 -1px 2px 0 hsl(0, 0%, 0%), 
        0px 4px 10px -4px hsla(0, 0%, 0%, calc(1 - var(--active, 0))), 
        0 0 0 calc(var(--active, 0) * 0.375rem) var(--hover-color);
    transition: all var(--transtion);
    z-index: 0;
}}

/* HIỆU ỨNG TIA SÁNG BÊN TRONG KHI HOVER (Background Gradient) - Giữ nguyên) */
.button::after {{
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 90%;
    height: 90%;
    background-color: hsla(40, 60%, 85%, 0.75);
    background-image: 
        radial-gradient(at 51% 89%, hsla(45, 60%, 90%, 1) 0px, transparent 50%), 
        radial-gradient(at 100% 100%, hsla(35, 60%, 80%, 1) 0px, transparent 50%), 
        radial-gradient(at 22% 91%, hsla(35, 60%, 80%, 1) 0px, transparent 50%);
    background-position: top;
    opacity: var(--active, 0); 
    border-radius: var(--border_radius);
    transition: opacity var(--transtion);
    z-index: 2;
}}

/* KÍCH HOẠT TRẠNG THÁI HOVER (Giữ nguyên) */
.button:is(:hover, :focus-visible) {{
    --active: 1;
}}

/* HIỆU ỨNG ÁNH SÁNG CHẠY VIỀN LIÊN TỤC (dots_border) */
.button .dots_border {{
    /* Tăng kích thước bao phủ ra ngoài thêm 4px (thay vì 2px) để chắc chắn */
    --size_border: calc(100% + 4px); 
    overflow: hidden;

    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);

    width: var(--size_border);
    height: var(--size_border);
    background-color: transparent;

    border-radius: var(--border_radius);
    z-index: -1; 
}}

/* LỚP GIẢ TẠO DÒNG ÁNH SÁNG XOAY */
.button .dots_border::before {{
    content: "";
    position: absolute;
    top: 50%; 
    left: 50%;
    
    /* Tăng kích thước vùng mask lên 400% để đảm bảo ánh sáng đủ lớn */
    width: 400%; 
    height: 400%; 
    
    transform: translate(-50%, -50%) rotate(0deg); 
    transform-origin: center;
    
    /* MODIFICATION 1: Sử dụng gradient màu vàng kim sáng cho hiệu ứng nổi bật hơn */
    background: linear-gradient(
        45deg, 
        #FFEB3B, /* Bright Yellow */
        #FFC107, /* Amber */
        #FFD700  /* Gold */
    );
    
    mask: conic-gradient(
        from 0deg at 50% 50%, 
        transparent 0%, 
        transparent 30%, 
        white 31%, 
        white 35%, 
        transparent 36%, 
        transparent 100%
    );
                          
    animation: rotate 3s linear infinite;
}}

@keyframes rotate {{
    to {{ transform: translate(-50%, -50%) rotate(360deg); }}
}}

/* ICON và TEXT (Giữ nguyên) */
.button .sparkle {{
    position: relative;
    z-index: 10;
    width: 1.75rem;
}}

.button .sparkle .path {{
    fill: currentColor;
    stroke: currentColor;
    transform-origin: center;
    color: var(--text-color); 
    transition: transform var(--transtion);
}}

.button:is(:hover, :focus) .sparkle .path {{
    animation: path 1.5s linear 0.5s infinite;
}}

@keyframes path {{
    0%, 34%, 71%, 100% {{ transform: scale(1); }}
    17% {{ transform: scale(1.2); }}
    49% {{ transform: scale(1.2); }}
    83% {{ transform: scale(1.2); }}
}}

.button .text_button {{
    position: relative;
    z-index: 10;
    background-image: linear-gradient(
        90deg, 
        var(--text-color) 0%, 
        hsla(0, 0%, 100%, var(--active, 0.5)) 120% 
    );
    background-clip: text;
    -webkit-background-clip: text; 
    font-size: 1.1rem;
    color: transparent; 
    font-weight: 600;
    letter-spacing: 1px;
    white-space: nowrap;
    text-shadow: 0 0 5px rgba(0, 0, 0, 0.5); 
}}

/* --- MEDIA QUERY CHO MOBILE (Giữ nguyên logic Flexbox) --- */
@media (max-width: 768px) {{
    /* Vị trí mới cho mobile: dùng flexbox để xếp dọc */
    #nav-buttons-wrapper {{
        position: fixed;
        bottom: 120px; 
        left: 50%;
        transform: translateX(-50%);
        width: calc(100% - 40px);
        max-width: 450px; 
        display: flex;
        flex-direction: column; /* Xếp dọc */
        gap: 15px; 
        padding: 0; /* Bỏ padding 80px trên desktop */
    }}
    
    /* Cả hai container vẫn là static và xếp chồng lên nhau */
    .nav-container,
    .nav-container-right {{
        position: static; 
        width: 100%;
    }}

    .button {{
        padding: 0.8rem 1.5rem;
        gap: 0.4rem;
        width: 100%;
        max-width: 450px;
        justify-content: center;
    }}
    .button .sparkle {{
        width: 1.5rem;
    }}
    .button .text_button {{
        font-size: 1.1rem;
        white-space: nowrap;
    }}
}}

</style>
"""

# Thêm CSS vào trang chính
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- PHẦN 3: MÃ HTML/CSS/JavaScript IFRAME CHO VIDEO INTRO ---

# Tạo danh sách music sources cho JavaScript 
if len(music_files) > 0:
    music_sources_js = ",\n\t\t\t".join([f"'{url}'" for url in music_files])
else:
    music_sources_js = ""

# PHẦN JS
js_callback_video = f"""
<script>
    console.log("Script loaded");
    
    // Hàm thực hiện chuyển đổi sang nội dung chính
    function sendBackToStreamlit(isSkipped = false) {{
        console.log("Transitioning to main content. Is Skipped:", isSkipped);
        const stApp = window.parent.document.querySelector('.stApp');
        if (stApp) {{
            stApp.classList.add('video-finished', 'main-content-revealed');
            // 🌟 FIX: Xóa class chặn tương tác khi video kết thúc
            stApp.classList.remove('video-running'); 
        }}
        
        const revealGrid = window.parent.document.querySelector('.reveal-grid');

        if (!isSkipped) {{
            // Chạy hiệu ứng reveal khi video phát xong
            initRevealEffect();
        }} else {{
            // Xóa lưới reveal ngay lập tức khi skip (quay về trang chủ)
            if (revealGrid) {{
                revealGrid.remove();
            }}
        }}
        
        // --- CHỈNH SỬA QUAN TRỌNG: KÍCH HOẠT SỰ KIỆN CLICK SAU KHI REVEAL HOÀN TẤT ---
        const partNumberBtn = window.parent.document.getElementById('partnumber-btn');
        const bankBtn = window.parent.document.getElementById('bank-btn');

        // Định nghĩa hàm điều hướng
        const navigateToPartNumber = (e) => {{
            e.preventDefault(); // Chặn hành vi mặc định của href="#"
            window.parent.location.href = '/partnumber'; 
        }};
        const navigateToBank = (e) => {{
            e.preventDefault(); // Chặn hành vi mặc định của href="#"
            window.parent.location.href = '/bank';
        }};

        // Thêm listener (chỉ 1 lần)
        if (partNumberBtn && !partNumberBtn._listenerAttached) {{
            partNumberBtn.addEventListener('click', navigateToPartNumber);
            partNumberBtn._listenerAttached = true; // Dùng cờ để tránh gắn lại
        }}

        if (bankBtn && !bankBtn._listenerAttached) {{
            bankBtn.addEventListener('click', navigateToBank);
            bankBtn._listenerAttached = true;
        }}
        // --- KẾT THÚC KHỐI CHỈNH SỬA ---

        // Music player có độ trễ riêng (2s sau khi add class video-finished)
        setTimeout(initMusicPlayer, 100); 
    }}
    
    function initRevealEffect() {{
        const revealGrid = window.parent.document.querySelector('.reveal-grid');
        if (!revealGrid) {{ return; }}

        const cells = revealGrid.querySelectorAll('.grid-cell');
        const shuffledCells = Array.from(cells).sort(() => Math.random() - 0.5);

        shuffledCells.forEach((cell, index) => {{
            setTimeout(() => {{
                cell.style.opacity = 0;
            }}, index * 10);
        }});
        // 🌟 FIX: Tăng thời gian chờ sau khi hiệu ứng reveal kết thúc để đồng bộ với delay của nút (5s)
        setTimeout(() => {{
             revealGrid.remove();
        }}, shuffledCells.length * 10 + 1000); 
    }}

    function initMusicPlayer() {{
        console.log("Initializing music player");
        const musicSources = [{music_sources_js}];
        
        if (musicSources.length === 0) {{
            console.log("No music files available");
            return;
        }}
        
        let currentTrack = 0;
        let isPlaying = false;
        
        const audio = new Audio();
        audio.volume = 0.3;
        
        const playPauseBtn = window.parent.document.getElementById('play-pause-btn');
        const prevBtn = window.parent.document.getElementById('prev-btn');
        const nextBtn = window.parent.document.getElementById('next-btn');
        const progressBar = window.parent.document.getElementById('progress-bar');
        const progressContainer = window.parent.document.getElementById('progress-container');
        const currentTimeEl = window.parent.document.getElementById('current-time');
        const durationEl = window.parent.document.getElementById('duration');
        if (!playPauseBtn || !prevBtn || !nextBtn) {{
            console.error("Music player elements not found in parent document");
            return;
        }}
        
        function loadTrack(index) {{
            console.log("Loading track", index + 1, "from URL:", musicSources[index]);
            audio.src = musicSources[index]; 
            audio.load();
        }}
        
        function togglePlayPause() {{
            if (isPlaying) {{
                audio.pause();
                playPauseBtn.textContent = '▶';
            }} else {{
                audio.play().catch(e => console.error("Play error:", e));
                playPauseBtn.textContent = '⏸';
            }}
            isPlaying = !isPlaying;
        }}
        
        function nextTrack() {{
            currentTrack = (currentTrack + 1) % musicSources.length;
            loadTrack(currentTrack);
            if (isPlaying) {{
                audio.play().catch(e => console.error("Play error:", e));
            }}
        }}
        
        function prevTrack() {{
            currentTrack = (currentTrack - 1 + musicSources.length) % musicSources.length;
            loadTrack(currentTrack);
            if (isPlaying) {{
                audio.play().catch(e => console.error("Play error:", e));
            }}
        }}
        
        function formatTime(seconds) {{
            if (isNaN(seconds)) return '0:00';
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return `${{mins}}:${{secs.toString().padStart(2, '0')}}`;
        }}
        
        audio.addEventListener('timeupdate', () => {{
            const progress = (audio.currentTime / audio.duration) * 100;
            progressBar.style.width = progress + '%';
            currentTimeEl.textContent = formatTime(audio.currentTime);
        }});
        audio.addEventListener('loadedmetadata', () => {{
            durationEl.textContent = formatTime(audio.duration);
        }});
        audio.addEventListener('ended', () => {{
            nextTrack();
        }});
        audio.addEventListener('error', (e) => {{ 
            console.error("Error loading music track:", e);
            nextTrack();
        }});
        playPauseBtn.addEventListener('click', togglePlayPause);
        nextBtn.addEventListener('click', nextTrack);
        prevBtn.addEventListener('click', prevTrack);
        
        progressContainer.addEventListener('click', (e) => {{
            const rect = progressContainer.getBoundingClientRect();
            const percent = (e.clientX - rect.left) / rect.width;
            audio.currentTime = percent * audio.duration;
        }});
        loadTrack(0);
        console.log("Music player initialized successfully");
    }}

    document.addEventListener("DOMContentLoaded", function() {{
        console.log("DOM loaded, waiting for elements...");
        
        const stApp = window.parent.document.querySelector('.stApp');
        if (stApp) {{
            // 🌟 FIX: Thêm class chặn tương tác ngay khi tải trang (cửa sổ cha)
            stApp.classList.add('video-running'); 
        }}

        // LOGIC MỚI: KIỂM TRA THAM SỐ SKIP_INTRO
        const urlParams = new URLSearchParams(window.parent.location.search);
        const skipIntro = urlParams.get('skip_intro');
        
        if (skipIntro === '1') {{
            console.log("Skip intro detected. Directly revealing main content.");
            // Giả lập sự kiện video kết thúc và bỏ hiệu ứng reveal
            sendBackToStreamlit(true); // Pass true to skip reveal
            // Ẩn ngay lập tức video iframe
            const iframe = window.frameElement;
            if (iframe) {{
                 iframe.style.opacity = 0;
                 iframe.style.visibility = 'hidden';
                 // Đảm bảo iframe không chặn tương tác
                 iframe.style.pointerEvents = 'none'; 
            }}
            return; // Dừng khởi tạo video/audio
        }}


        const waitForElements = setInterval(() => {{
            const video = document.getElementById('intro-video');
            const audio = document.getElementById('background-audio');
            const introTextContainer = document.getElementById('intro-text-container');
            // FIX: Lấy lớp phủ
            const overlay = document.getElementById('click-to-play-overlay');
           
            if (video && audio && introTextContainer && overlay) {{
                clearInterval(waitForElements);
                console.log("All elements found, initializing...");
                
                const isMobile = window.innerWidth <= 768;
         
                const videoSource = isMobile ? 'data:video/mp4;base64,{video_mobile_base64}' : 'data:video/mp4;base64,{video_pc_base64}';
                video.src = videoSource;
                audio.src = 'data:audio/mp3;base64,{audio_base64}';

                console.log("Video/Audio source set. Loading metadata...");

                let interactionHandled = false; // Biến cờ mới để ngăn chặn đa kích hoạt
                
                // 🌟 FIX: Hàm phát video và ẩn lớp phủ
                const tryToPlayAndHideOverlay = (e) => {{
                    // 🌟 QUAN TRỌNG: Ngăn chặn hành động mặc định của trình duyệt (ví dụ: double-click)
                    e.preventDefault(); 
                    
                    if (interactionHandled) {{
                        console.log("Interaction already handled, ignoring.");
                        return;
                    }}
                    interactionHandled = true;

                    console.log("Attempting to play video (User interaction)");
                    
                    // 🌟 FIX: Loại bỏ ngay lập tức các listener trên overlay 
                    overlay.removeEventListener('click', tryToPlayAndHideOverlay);
                    overlay.removeEventListener('touchstart', tryToPlayAndHideOverlay);
                    overlay.removeEventListener('dblclick', tryToPlayAndHideOverlay); // Chặn double-click

                    video.play().then(() => {{
                        console.log("✅ Video is playing, hiding overlay!");
                        overlay.classList.add('hidden'); // Ẩn lớp phủ sau khi play thành công
                    }}).catch(err => {{
                        console.error("❌ Still can't play video, skipping intro (Error/File issue):", err);
                        overlay.textContent = "LỖI PHÁT. ĐANG CHUYỂN TRANG...";
                        // GỌI sendBackToStreamlit() sau 2s, không phải 200ms
                        setTimeout(() => sendBackToStreamlit(false), 2000); 
                    }});
                    audio.play().catch(e => {{
                        console.log("Audio autoplay blocked (normal), waiting for video end.");
                    }});
                }};


                video.addEventListener('canplaythrough', () => {{
                    // Tự động phát nếu không cần tương tác (PC/Môi trường không chặn)
                    // Vẫn gọi hàm tryToPlayAndHideOverlay, nhưng truyền vào một đối tượng event rỗng để e.preventDefault() không gây lỗi
                    tryToPlayAndHideOverlay({{ preventDefault: () => {{}} }}); 
                }}, {{ once: true }});
                
                video.addEventListener('ended', () => {{
                    console.log("Video ended, transitioning...");
                    video.style.opacity = 0;
                    audio.pause();
                    audio.currentTime = 0;
                    
                    introTextContainer.style.opacity = 0;
                    setTimeout(() => sendBackToStreamlit(false), 500); // Pass false: video ended normally
                }});
                video.addEventListener('error', (e) => {{
                    console.error("Video error detected (Codec/Base64/File corrupted). Skipping intro:", e);
                    sendBackToStreamlit(false); // Pass false: video failed
                }});
                
                // 🌟 FIX: Dùng lớp phủ để bắt tương tác
                overlay.addEventListener('click', tryToPlayAndHideOverlay, {{ once: true }});
                overlay.addEventListener('touchstart', tryToPlayAndHideOverlay, {{ once: true }});
                overlay.addEventListener('dblclick', tryToPlayAndHideOverlay, {{ once: true }}); // Chặn double-click
                
                video.load();
                const chars = introTextContainer.querySelectorAll('.intro-char');
                chars.forEach((char, index) => {{
                    char.style.animationDelay = `${{index * 0.1}}s`;
                    char.classList.add('char-shown');
                }});
            }}
        }}, 100);
        setTimeout(() => {{
            clearInterval(waitForElements);
            const video = document.getElementById('intro-video');
            if (video && !video.src) {{
                console.warn("Timeout before video source set. Force transitioning to main content.");
                sendBackToStreamlit(false); // Pass false: timed out
            }}
        }}, 5000);
    }});
</script>
"""

html_content_modified = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            height: 100vh;
            width: 100vw;
            background-color: #000;
        }}
        
        #intro-video {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            z-index: 0;
            transition: opacity 1s;
        }}

        #intro-text-container {{
            position: fixed;
            top: 5vh;
            width: 100%;
            text-align: center;
            color: #FFD700;
            font-size: 3vw;
            font-family: 'Sacramento', cursive;
            font-weight: 400;
            text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.8);
            z-index: 100;
            pointer-events: none;
            display: flex;
            justify-content: center;
            opacity: 1;
            transition: opacity 0.5s;
        }}
        
        .intro-char {{
            display: inline-block;
            opacity: 0;
            transform: translateY(-50px);
            animation-fill-mode: forwards;
            animation-duration: 0.8s;
            animation-timing-function: ease-out;
        }}

        @keyframes charDropIn {{
            from {{
                opacity: 0;
                transform: translateY(-50px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .intro-char.char-shown {{
            animation-name: charDropIn;
        }}
        
        /* FIX: CSS cho lớp phủ chặn click */
        #click-to-play-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 200; 
            cursor: pointer;
            background: rgba(0, 0, 0, 0.5); 
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Playfair Display', serif;
            color: #fff;
            font-size: 2vw;
            text-shadow: 1px 1px 3px #000;
            transition: opacity 0.5s;
        }}

        #click-to-play-overlay.hidden {{
            opacity: 0;
            pointer-events: none; /* Rất quan trọng: không còn chặn tương tác sau khi phát */
        }}

        @media (max-width: 768px) {{
            #intro-text-container {{
                font-size: 6vw;
            }}
            /* FIX: Cỡ chữ overlay trên mobile */
             #click-to-play-overlay {{
                font-size: 4vw;
            }}
        }}
    </style>
</head>
<body>
    <div id="intro-text-container">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    <video id="intro-video" muted playsinline></video>
    <audio id="background-audio"></audio>
    <div id="click-to-play-overlay">CLICK/TOUCH VÀO ĐÂY ĐỂ BẮT ĐẦU</div>
    {js_callback_video}
</body>
</html>
"""

# Xử lý nội dung của tiêu đề video intro để thêm hiệu ứng chữ thả
intro_title = "KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI"
intro_chars_html = ''.join([
    f'<span class="intro-char">{char}</span>' if char != ' ' else '<span class="intro-char">&nbsp;</span>'
    for char in intro_title
])
html_content_modified = html_content_modified.replace(
    "<div id=\"intro-text-container\">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>",
    f"<div id=\"intro-text-container\">{intro_chars_html}</div>"
)

# --- HIỂN THỊ IFRAME VIDEO ---
st.components.v1.html(html_content_modified, height=1080, scrolling=False)

# --- HIỆU ỨNG REVEAL VÀ NỘI DUNG CHÍNH ---

# Tạo Lưới Reveal
grid_cells_html = ""
for i in range(240):
    grid_cells_html += f'<div class="grid-cell"></div>'

reveal_grid_html = f"""
<div class="reveal-grid">
    {grid_cells_html}
</div>
"""
st.markdown(reveal_grid_html, unsafe_allow_html=True)

# --- NỘI DUNG CHÍNH (TIÊU ĐỀ ĐƠN, ĐỔI MÀU) ---
main_title_text = "TỔ BẢO DƯỠNG SỐ 1"

# Nhúng tiêu đề
st.markdown(f"""
<div id="main-title-container">
    <h1>{main_title_text}</h1>
</div>
""", unsafe_allow_html=True)

# --- MUSIC PLAYER ---
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

# Định nghĩa SVG trong biến Python đơn dòng
svg_part_number = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="sparkle" ><path class="path" stroke-linejoin="round" stroke-linecap="round" stroke="currentColor" fill="currentColor" d="M10 17a7 7 0 100-14 7 7 0 000 14zM21 21l-4-4" ></path></svg>'
svg_bank = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" class="sparkle"><path class="path" stroke-linecap="round" stroke-linejoin="round" stroke="currentColor" fill="currentColor" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>'

# Gộp toàn bộ HTML vào một chuỗi Python đa dòng
nav_buttons_html = f"""
<div id="nav-buttons-wrapper">
    <div class="nav-container">
        <a href="#" id="partnumber-btn" target="_self" class="button">
            <div class="dots_border"></div>
            {svg_part_number} 
            <span class="text_button">TRA CỨU PART NUMBER</span> 
        </a>
    </div>
    
    <div class="nav-container-right">
        <a href="#" id="bank-btn" target="_self" class="button">
            <div class="dots_border"></div> 
            {svg_bank}
            <span class="text_button">NGÂN HÀNG TRẮC NGHIỆM</span> 
        </a>
    </div>
</div>
"""

# BƯỚC KHẮC PHỤC TRIỆT ĐỂ: LÀM SẠCH CHUỖI HTML
nav_buttons_html_cleaned = re.sub(r'>\s+<', '><', nav_buttons_html.strip())
nav_buttons_html_cleaned = nav_buttons_html_cleaned.replace('\n', '')

# Hiển thị chuỗi HTML đã được làm sạch
st.markdown(nav_buttons_html_cleaned, unsafe_allow_html=True)
