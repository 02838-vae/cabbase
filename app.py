import streamlit as st
import random
import time

# --- Cấu hình Trang (Luôn đặt ở đầu) ---
st.set_page_config(layout="wide", page_title="Tổ Bảo Dưỡng Số 1")

# --- Khởi tạo Session State ---
# 'intro_complete' là cờ để kiểm tra xem Intro đã chạy chưa
if 'intro_complete' not in st.session_state:
    st.session_state['intro_complete'] = False
if 'start_time' not in st.session_state:
    st.session_state['start_time'] = time.time()

# --- CSS Tùy chỉnh (Định nghĩa Phong cách Vintage và Hiệu ứng) ---
def custom_css():
    """CSS cho hiệu ứng Intro và Trang Chính (kèm Media Query cho nền)"""
    
    # Danh sách các file nhạc nền (để đảm bảo không bị lỗi tên file)
    music_files = [f"background{i}.mp3" for i in range(6)] 
    
    # CSS cho nền và font chữ Vintage
    vintage_css = f"""
    <style>
    /* CSS Chung cho nền Trang Chính */
    .stApp {{
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        transition: background-image 1s ease-in-out; /* Hiệu ứng mượt khi chuyển nền */
        min-height: 100vh; /* Đảm bảo chiều cao tối thiểu */
    }}
    
    /* Thiết lập ảnh nền mặc định (PC) */
    .stApp.main-page-bg {{
        background-image: url("cabbage.jpg");
    }}
    
    /* Media Query cho Mobile */
    @media only screen and (max-width: 768px) {{
        .stApp.main-page-bg {{
            background-image: url("mobile.jpg"); /* Ảnh nền Mobile */
        }}
    }}

    /* Thiết lập font chữ kiểu cổ điển */
    h1, .stText, p, .stMarkdown, label {{
        font-family: 'Times New Roman', serif; 
        color: #5D4037; 
    }}
    
    /* Hiệu ứng chữ Intro */
    @keyframes fade_in_out {{
        0% {{ opacity: 0; }}
        10% {{ opacity: 1; }} 
        90% {{ opacity: 1; }}
        100% {{ opacity: 0; }} 
    }}
    
    #intro-text {{
        position: fixed; 
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 3em;
        color: white;
        text-shadow: 2px 2px 4px #000000;
        animation: fade_in_out 4s forwards; 
        z-index: 10000; 
        pointer-events: none;
    }}
    
    /* Hiệu ứng chuyển cảnh video mờ dần */
    @keyframes video_fade_out {{
        0% {{ opacity: 1; }}
        100% {{ opacity: 0; }}
    }}
    
    #intro-video-container {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 9999;
        opacity: 1;
        animation: video_fade_out 1s forwards; /* Hiệu ứng mờ 1s */
        animation-delay: 4s; /* Bắt đầu mờ sau 4s (tổng video 5s) */
        overflow: hidden; /* Cắt video nếu tràn */
        background-color: black;
    }}
    
    /* Định dạng lại st.audio trong sidebar cho phong cách Vintage */
    [data-testid="stSidebarContent"] {{
        background-color: rgba(255, 255, 240, 0.7); /* Nền sidebar màu ngà */
        padding: 15px;
    }}
    .stAudio {{
        background-color: rgba(245, 245, 220, 0.8);
        border: 1px solid #A1887F;
        border-radius: 10px;
        padding: 5px;
    }}
    
    </style>
    """
    st.markdown(vintage_css, unsafe_allow_html=True)

# --- Định nghĩa các Màn hình ---

def intro_screen():
    """Màn hình Intro với Video và Chữ (Đã chỉnh sửa để video chạy ổn định)"""
    custom_css()
    st.empty() 

    # --- KHẮC PHỤC LỖI VIDEO KHÔNG CHẠY ---
    # Sử dụng st.components.v1.html với thẻ <video> *rõ ràng* có muted và autoplay
    # để tăng khả năng tương thích với trình duyệt.
    video_html = """
    <div id="intro-video-container">
        <video id="intro-video" width="100%" height="100%" autoplay loop muted playsinline 
               style="object-fit: cover; width: 100%; height: 100%;">
            <source src="airplane.mp4" type="video/mp4">
            Your browser does not support the video tag.
        </video>
    </div>
    <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    """
    # Chiều cao lớn để chiếm gần hết màn hình, video sẽ nằm trong container này
    st.components.v1.html(video_html, height=700, scrolling=False) 

    # --- KÍCH HOẠT CHUYỂN TRANG SAU 5 GIÂY ---
    # Vì video đã được nhúng trong HTML component, ta dùng trick timer của Streamlit
    if time.time() - st.session_state['start_time'] > 5:
        st.session_state['intro_complete'] = True
        st.rerun() # Tải lại trang để chuyển sang Trang chính

def main_page():
    """Trang Chính Tối Giản theo phong cách Vintage"""
    custom_css() # Áp dụng CSS
    
    # Gắn class nền cho Trang Chính
    st.markdown('<div class="main-page-bg">', unsafe_allow_html=True)

    # 1. Thanh phát nhạc ngẫu nhiên (Góc trên bên trái)
    music_files = ["background.mp3", "background1.mp3", "background2.mp3", "background3.mp3", "background4.mp3", "background5.mp3"]
    random_track = random.choice(music_files)
    
    # Sử dụng st.sidebar để đặt thanh nhạc góc trên bên trái
    with st.sidebar:
        st.subheader("🎶 Nhạc Nền Cổ Điển")
        # Phát nhạc ngẫu nhiên, lặp lại (loop=True)
        st.audio(random_track, format="audio/mp3", start_time=0, loop=True) 
        st.caption(f"Đang phát ngẫu nhiên: **{random_track}**")

    # 2. Tiêu đề canh giữa
    st.markdown("<h1 style='text-align: center; color: #4E342E; font-size: 3.5em; text-shadow: 1px 1px 2px #FFF8DC;'>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)
    
    # 3. Nội dung rỗng (Chỉ giữ Tiêu đề và Thanh nhạc)
    st.empty()
    
    st.markdown('</div>', unsafe_allow_html=True) # Kết thúc div .main-page-bg

# --- Luồng Ứng Dụng Chính ---
if st.session_state['intro_complete']:
    main_page()
else:
    intro_screen()
