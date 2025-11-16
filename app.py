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
        st.error(f"Lỗi khi đọc file {file_path}: {str(e)}")
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
    transition: opacity 2s ease-out 3s;
    z-index: 10000;
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

.video-finished #nav-buttons-wrapper {{
    opacity: 1;
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
    overflow: hidden; /* Quan trọng để hiệu ứng quét không tràn ra ngoài */
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

/* --- CSS CHUNG CHO CẢ HAI HIỆU ỨNG ÁNH SÁNG CHẠY VIỀN LIÊN TỤC --- */
.button .dots_border,
.button .blue_dots_border {{
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

/* LỚP GIẢ TẠO DÒNG ÁNH SÁNG XOAY (MÀU VÀNG KIM - Dành cho nút Part Number) */
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
    
    /* MÀU VÀNG KIM */
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

/* LỚP GIẢ TẠO DÒNG ÁNH SÁNG XOAY (MÀU XANH LAM ĐẬM - Dành cho nút Trắc Nghiệm) */
.button .blue_dots_border::before {{
    content: "";
    position: absolute;
    top: 50%; 
    left: 50%;
    
    /* Tăng kích thước vùng mask lên 400% để đảm bảo ánh sáng đủ lớn */
    width: 400%; 
    height: 400%; 
    
    transform: translate(-50%, -50%) rotate(0deg); 
    transform-origin: center;
    
    /* MÀU XANH LAM ĐẬM - TƯƠNG PHẢN MẠNH HƠN (Giữ nguyên theo yêu cầu) */
    background: linear-gradient(
        45deg, 
        #00008B, /* Dark Blue */
        #4B0082, /* Indigo */
        #483D8B  /* Dark Slate Blue */
    );
    
    mask: conic-gradient(
        from 0deg at 50% 50%, 
        transparent 0%, 
        transparent 30%, 
        white 31%, 
        white 35%, 
        transparent 36%,
