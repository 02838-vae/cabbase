import streamlit as st
import base64
import os

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


# Mã hóa các file media chính (bắt buộc)
try:
    # Đảm bảo các file này nằm cùng thư mục với app.py
    # Ghi chú: Các file này phải có sẵn trong thư mục
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
    
    # MÃ HÓA CHO LOGO
    logo_base64 = get_base64_encoded_file("logo.jpg")

    # Kiểm tra file bắt buộc
    if not all([video_pc_base64, video_mobile_base64, audio_base64, bg_pc_base64, bg_mobile_base64]):
        missing_files = []
        if not video_pc_base64: missing_files.append("airplane.mp4")
        if not video_mobile_base64: missing_files.append("mobile.mp4")
        if not audio_base64: missing_files.append("plane_fly.mp3")
        if not bg_pc_base64: missing_files.append("cabbase.jpg")
        if not bg_mobile_base64: missing_files.append("mobile.jpg")
        
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
# Đảm bảo repository của bạn là PUBLIC để các URL này hoạt động
BASE_MUSIC_URL = "https://raw.githubusercontent.com/02838-vae/cabbase/main/"
music_urls = []

# Thêm 6 file nhạc nền vào danh sách URL
for i in range(1, 7):
    url = f"{BASE_MUSIC_URL}background{i}.mp3"
    music_urls.append(url)
    
# Biến được sử dụng trong JS:
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
}}

.video-finished iframe:first-of-type {{
    opacity: 0;
    visibility: hidden;
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

.nav-container {{
    position: fixed;
    /* Lệch trái 15% */
    left: 15%; 
    top: 50%;
    transform: translate(-50%, -50%);
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 40px;
    opacity: 0;
    transition: opacity 2s ease-out 3s;
    /* ✅ QUAN TRỌNG: Đảm bảo button ở trên cùng */
    z-index: 10000;
}}

.video-finished .nav-container {{
    opacity: 1;
}}

/* KHỞI TẠO CÁC BIẾN CSS */
.button {{
    --black-700: hsla(0, 0%, 12%, 1);
    --border_radius: 9999px; 
    --transtion: 0.3s ease-in-out;
    --active: 0; 
    /* ✅ ĐIỀU CHỈNH: Màu ánh sáng hover SIÊU DỊU (Vàng Pastel) */
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
    
    /* ✅ ĐIỀU CHỈNH: Tăng hiệu ứng phóng to (scale 0.2) */
    transform: scale(calc(1 + (var(--active, 0) * 0.2)));
    transition: transform var(--transtion);
    
    text-decoration: none; 
}}

/* NỀN ĐEN CỦA BUTTON */
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

/* HIỆU ỨNG TIA SÁNG BÊN TRONG KHI HOVER (Background Gradient) */
.button::after {{
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 90%;
    height: 90%;
    
    /* ✅ ĐIỀU CHỈNH: Gradient bên trong button chuyển sang tông vàng/cam siêu dịu */
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

/* KÍCH HOẠT TRẠNG THÁI HOVER */
.button:is(:hover, :focus-visible) {{
    --active: 1;
}}

/* HIỆU ỨNG ÁNH SÁNG CHẠY VIỀN LIÊN TỤC (dots_border) */
.button .dots_border {{
    --size_border: calc(100% + 2px);
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
    
    width: 300%; 
    height: 300%; 
    
    transform: translate(-50%, -50%) rotate(0deg); 
    transform-origin: center;
    
    background: white;
    /* ✅ ĐIỀU CHỈNH: Masking mới để ĐẢM BẢO chỉ 1 vệt sáng duy nhất */
    mask: conic-gradient(
        from 0deg at 50% 50%, 
        transparent 0%, 
        transparent 30%, 
        white 31%, 
        white 35%, /* Giữ độ dày vệt sáng đủ để thấy */
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

@media (max-width: 768px) {{
    .nav-container {{
        left: 50%;
        transform: translate(-50%, -50%);
        width: 100%;
        padding: 20px;
    }}
    
    .button {{
        padding: 0.8rem 1.5rem;
        gap: 0.4rem;
        width: 100%;
        max-width: 400px;
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

@keyframes fadeInUp {{
    from {{
        opacity: 0;
        transform: translateY(50px) scale(0.9);
    }}
    to {{
        opacity: 1;
        transform: translateY(0) scale(1);
    }}
}}

.video-finished .button {{
    animation: fadeInUp 1s ease-out forwards;
    animation-delay: 3.2s;
    opacity: 0;
}}

/* === CSS ĐÃ SỬA: ĐỒNG HỒ CƠ (TRÁI) === */
#analog-clock-container {{
    position: fixed;
    top: 25vh; /* Đặt dưới tiêu đề */
    left: 20px; 
    /* Bỏ transform: translateY(-50%) */
    width: 120px; /* Thu gọn */
    height: 120px; /* Thu gọn */
    z-index: 999;
    opacity: 0;
    transition: opacity 1s ease-out 3.5s;
}}

.video-finished #analog-clock-container {{
    opacity: 1;
}}

.analog-clock {{
    width: 100%;
    height: 100%;
    border: 5px solid #FFD700; 
    border-radius: 50%;
    background-color: rgba(0, 0, 0, 0.7);
    box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
    position: relative;
}}

.hand {{
    position: absolute;
    width: 50%;
    height: 3px;
    background: white;
    top: 50%;
    left: 50%;
    transform-origin: 0% 50%;
    transform: rotate(90deg); 
    border-radius: 5px;
}}

.hour-hand {{
    background: #FFD700; 
    width: 30%;
    height: 5px;
    margin-top: -2.5px;
}}

.minute-hand {{
    background: white;
    width: 40%;
    height: 3px;
    margin-top: -1.5px;
}}

.second-hand {{
    background: #FF0000; 
    width: 45%;
    height: 1px;
    margin-top: -0.5px;
}}

.center-dot {{
    width: 10px;
    height: 10px;
    background: #111;
    border: 2px solid white;
    border-radius: 50%;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 10;
}}


/* === CSS ĐÃ SỬA: LỊCH (PHẢI) - Thiết kế cuốn lịch tối giản === */
#calendar-container {{
    position: fixed;
    top: 25vh; /* Đặt dưới tiêu đề */
    right: 20px; 
    /* Bỏ transform: translateY(-50%) */
    width: 100px; 
    height: 140px; 
    padding: 0;
    background: rgba(0, 0, 0, 0.7);
    color: white;
    border-radius: 5px 5px 12px 12px;
    box-shadow: 0 0 15px rgba(255, 255, 255, 0.3);
    border: 3px solid #FFD700; /* Viền màu vàng */
    z-index: 999;
    opacity: 0;
    transition: opacity 1s ease-out 3.5s;
    font-family: Arial, sans-serif;
    text-align: center;
    overflow: hidden; 
}}

.video-finished #calendar-container {{
    opacity: 1;
}}

/* Thêm hiệu ứng ghim/khoen trên đầu cuốn lịch */
#calendar-container::before,
#calendar-container::after {{
    content: '';
    position: absolute;
    top: -5px; /* Đặt cao hơn viền */
    width: 10px;
    height: 10px;
    background: #00FF00; /* Màu ghim */
    border: 2px solid #111;
    border-radius: 50%;
    z-index: 10;
}}

#calendar-container::before {{
    left: 10px;
}}

#calendar-container::after {{
    right: 10px;
}}

/* Style cho Ngày (số) */
#calendar-container .date-display {{
    font-size: 3rem;
    font-weight: 900;
    color: #111; /* Màu chữ tối */
    background-color: #f0f0f0; /* Nền giấy/cuốn lịch */
    line-height: 1.2;
    margin: 25px 0 0 0; /* Đẩy xuống để chừa chỗ cho ghim */
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-sizing: border-box;
    font-family: 'Playfair Display', serif;
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

# ✅ PHẦN JS ĐÃ CHỈNH SỬA (Giữ nguyên logic chính xác)
js_callback_video = f"""
<script>
    console.log("Script loaded");

    // === CHỈNH SỬA 1: THÊM THAM SỐ skipReveal ===
    function sendBackToStreamlit(skipReveal = false) {{
        console.log("Video ended or skipped, revealing main content. Skip Reveal:", skipReveal);
        const stApp = window.parent.document.querySelector('.stApp');
        if (stApp) {{
            stApp.classList.add('video-finished', 'main-content-revealed');
        }}
        
        // CHỈ CHẠY REVEAL NẾU KHÔNG SKIP
        if (!skipReveal) {{ 
            initRevealEffect();
        }} else {{
            // Nếu skip reveal, ẩn ngay lập tức lớp grid
            const revealGrid = window.parent.document.querySelector('.reveal-grid');
            if (revealGrid) {{
                // Tăng tốc độ ẩn grid nếu skip reveal
                revealGrid.style.opacity = 0;
                setTimeout(() => {{ revealGrid.remove(); }}, 100); 
            }}
        }}

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

        // ✅ CHỈNH SỬA 2: SỬ DỤNG skipReveal=true KHI skipIntro='1'
        const urlParams = new URLSearchParams(window.parent.location.search);
        const skipIntro = urlParams.get('skip_intro');
        
        if (skipIntro === '1') {{
            console.log("Skip intro detected. Directly revealing main content, skipping reveal effect.");
            // Truyền true để bỏ qua hiệu ứng reveal
            sendBackToStreamlit(true);
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
           
            if (video && audio && introTextContainer) {{
                clearInterval(waitForElements);
                console.log("All elements found, initializing...");
                
                const isMobile = window.innerWidth <= 768;
         
                const videoSource = isMobile ? 'data:video/mp4;base64,{video_mobile_base64}' : 'data:video/mp4;base64,{video_pc_base64}';

                video.src = videoSource;
                audio.src = 'data:audio/mp3;base64,{audio_base64}';

                console.log("Video/Audio source set. Loading metadata...");
                const tryToPlay = () => {{
                    console.log("Attempting to play video (User interaction or Canplay event)");
                    video.play().then(() => {{
                        console.log("✅ Video is playing!");
                    }}).catch(err => {{
                        console.error("❌ Still can't play video, skipping intro (Error/File issue):", err);
                        // Khi lỗi/không thể tự động phát, chuyển tiếp và vẫn chạy reveal (mặc định)
                        setTimeout(() => sendBackToStreamlit(false), 2000); 
                    }});
                    audio.play().catch(e => {{
                        console.log("Audio autoplay blocked (normal), waiting for video end.");
                    }});
                }};

                video.addEventListener('canplaythrough', tryToPlay, {{ once: true }});
                
                video.addEventListener('ended', () => {{
                    console.log("Video ended, transitioning...");
                    video.style.opacity = 0;
                    audio.pause();
                    audio.currentTime = 0;
    
                    introTextContainer.style.opacity = 0;
                    // Gọi hàm mặc định (skipReveal=false), vẫn chạy reveal
                    setTimeout(() => sendBackToStreamlit(false), 500);
                }});
                video.addEventListener('error', (e) => {{
                    console.error("Video error detected (Codec/Base64/File corrupted). Skipping intro:", e);
                    // Gọi hàm mặc định (skipReveal=false), vẫn chạy reveal
                    sendBackToStreamlit(false);
                }});
                const clickHandler = () => {{
                    console.log("User interaction detected, forcing play attempt.");
                    tryToPlay();
                    document.removeEventListener('click', clickHandler);
                    document.removeEventListener('touchstart', clickHandler);
                }};
                
                document.addEventListener('click', clickHandler, {{ once: true }});
                document.addEventListener('touchstart', clickHandler, {{ once: true }});
                
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
                // Gọi hàm mặc định (skipReveal=false), vẫn chạy reveal
                sendBackToStreamlit(false);
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

        @media (max-width: 768px) {{
            #intro-text-container {{
                font-size: 6vw;
            }}
        }}
    </style>
</head>
<body>
    <div id="intro-text-container">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    <video id="intro-video" muted playsinline></video>
    <audio id="background-audio"></audio>
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
# Tên trang phụ là partnumber.py nên link href là /partnumber
st.markdown("""
<div class="nav-container">
    <a href="/partnumber" target="_self" class="button">
        <div class="dots_border"></div>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="sparkle" > 
            <path class="path" stroke-linejoin="round" stroke-linecap="round" stroke="currentColor" fill="currentColor" d="M10 17a7 7 0 100-14 7 7 0 000 14zM21 21l-4-4" ></path> 
        </svg> 
        <span class="text_button">TRA CỨU PART NUMBER</span> 
    </a>
</div>
""", unsafe_allow_html=True)

# --- PHẦN 4: ĐỒNG HỒ CƠ VÀ LỊCH XEM NGÀY/THÁNG (ĐÃ SỬA) ---

clock_calendar_html = """
<div id="analog-clock-container">
    <div class="analog-clock">
        <div class="hand hour-hand" id="hour-hand"></div>
        <div class="hand minute-hand" id="minute-hand"></div>
        <div class="hand second-hand" id="second-hand"></div>
        <div class="center-dot"></div>
    </div>
</div>

<div id="calendar-container">
    <div class="date-display" id="current-date">01</div>
</div>

<script>
    function updateClockAndCalendar() {
        const now = new Date();
        
        // --- CẬP NHẬT ĐỒNG HỒ CƠ ---
        const seconds = now.getSeconds();
        const minutes = now.getMinutes();
        const hours = now.getHours();

        // Tính góc xoay (cộng 90deg để bù trừ cho vị trí ban đầu của kim tại 3 giờ)
        const secondDeg = (seconds / 60) * 360 + 90;
        const minuteDeg = (minutes / 60) * 360 + (seconds / 60) * 6 + 90;
        const hourDeg = (hours / 12) * 360 + (minutes / 60) * 30 + 90;

        const hourHand = window.parent.document.getElementById('hour-hand');
        const minuteHand = window.parent.document.getElementById('minute-hand');
        const secondHand = window.parent.document.getElementById('second-hand');

        if (hourHand && minuteHand && secondHand) {
            hourHand.style.transform = `rotate(${hourDeg}deg)`;
            minuteHand.style.transform = `rotate(${minuteDeg}deg)`;
            secondHand.style.transform = `rotate(${secondDeg}deg)`;
        }

        // --- CẬP NHẬT LỊCH (Chỉ cập nhật Ngày) ---
        const currentDateEl = window.parent.document.getElementById('current-date');

        if (currentDateEl) {
            // Hiển thị ngày (số), thêm số 0 ở đầu nếu cần
            currentDateEl.textContent = now.getDate().toString().padStart(2, '0');
        }
    }

    // Chạy lần đầu và thiết lập Interval để cập nhật mỗi giây (đảm bảo độ chính xác)
    setTimeout(() => {
        updateClockAndCalendar();
        setInterval(updateClockAndCalendar, 1000); // Cập nhật mỗi 1 giây
    }, 4000); 
</script>
"""

st.markdown(clock_calendar_html, unsafe_allow_html=True)
