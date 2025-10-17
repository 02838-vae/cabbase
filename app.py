import streamlit as st
import random
import time
import os

# Tên file chính xác
PC_BACKGROUND = "cabbase.jpg" 
MOBILE_BACKGROUND = "mobile.jpg"
VIDEO_INTRO = "airplane.mp4" 

# --- Cấu hình Trang (Luôn đặt ở đầu) ---
st.set_page_config(layout="wide", page_title="Tổ Bảo Dưỡng Số 1")

# --- Khởi tạo Session State ---
if 'intro_complete' not in st.session_state:
    st.session_state['intro_complete'] = False
if 'video_loaded' not in st.session_state:
    st.session_state['video_loaded'] = False

# --- CSS Tùy chỉnh (Định nghĩa Phong cách Vintage và Hiệu ứng) ---
def custom_css():
    """CSS cho Trang Chính và hiệu ứng Intro"""
    
    vintage_css = f"""
    <style>
    /* Ẩn sidebar trong màn hình Intro */
    .stApp > header {{ display: {'none' if not st.session_state.intro_complete else 'block'} !important; }}
    .stApp {{
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        transition: background-image 1s ease-in-out;
        min-height: 100vh;
    }}
    
    /* Thiết lập ảnh nền mặc định (PC) */
    .stApp.main-page-bg {{
        background-image: url("{PC_BACKGROUND}");
    }}
    
    /* Media Query cho Mobile */
    @media only screen and (max-width: 768px) {{
        .stApp.main-page-bg {{
            background-image: url("{MOBILE_BACKGROUND}");
        }}
    }}
    
    /* Thiết lập font chữ và màu cổ điển */
    h1, .stText, p, .stMarkdown, label {{
        font-family: 'Times New Roman', serif; 
        color: #4E342E;
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
        animation: fade_in_out 4.5s forwards; /* Tăng thời gian animation */
        z-index: 10000; 
        pointer-events: none;
    }}
    
    /* Container video (dùng cho màn hình đen) */
    .intro-screen-container {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: black;
        z-index: 999;
        transition: opacity 1s ease-out;
    }}
    
    /* Hiệu ứng mờ dần (chuyển qua trang chính) */
    .intro-screen-container.fade-out {{
        opacity: 0;
        pointer-events: none;
    }}
    
    /* Định dạng sidebar */
    [data-testid="stSidebarContent"] {{
        background-color: rgba(255, 255, 240, 0.9);
        padding: 15px;
        border-right: 2px solid #A1887F;
    }}
    </style>
    """
    st.markdown(vintage_css, unsafe_allow_html=True)

# --- Định nghĩa các Màn hình ---

def intro_screen():
    """Màn hình Intro (Sử dụng st.video và HTML cho hiệu ứng)"""
    custom_css()
    
    if not os.path.exists(VIDEO_INTRO):
        st.error(f"Lỗi: Không tìm thấy file video **{VIDEO_INTRO}**. Vui lòng kiểm tra lại đường dẫn.")
        time.sleep(2)
        st.session_state['intro_complete'] = True
        st.rerun()
        return

    # 1. Hiển thị chữ Intro
    st.markdown('<div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>', unsafe_allow_html=True)
    
    # 2. Sử dụng st.video để tải video
    # Dùng st.empty() để đặt video và đảm bảo nó luôn hiển thị ở trên cùng
    
    video_placeholder = st.empty()
    
    # Đọc file video dưới dạng bytes để Streamlit phục vụ
    video_bytes = open(VIDEO_INTRO, 'rb').read()
    
    # Hiển thị video. Streamlit không có thuộc tính autoplay/muted trực tiếp cho st.video
    # Nó chỉ hoạt động nếu người dùng tương tác.
    # Tuy nhiên, nếu nó từng chạy, chúng ta vẫn dùng nó.
    video_placeholder.video(video_bytes, format="video/mp4", start_time=0)
    
    # 3. Kích hoạt hiệu ứng mờ dần và chuyển trang
    # Chúng ta phải dùng time.sleep và st.rerun để mô phỏng thời gian 5s
    
    # Thêm một container đen ở trên cùng để mô phỏng hiệu ứng mờ dần
    st.markdown("""
        <div class="intro-screen-container"></div>
        <script>
            // JavaScript để kích hoạt hiệu ứng mờ dần sau 4s
            setTimeout(() => {
                const container = document.querySelector('.intro-screen-container');
                if (container) {
                    container.classList.add('fade-out');
                }
            }, 4000); 
        </script>
        """, unsafe_allow_html=True)

    # Dùng logic Python để chuyển trạng thái sau 5.5s
    time.sleep(5.5) 
    st.session_state['intro_complete'] = True
    st.rerun()


def main_page():
    """Trang Chính Tối Giản theo phong cách Vintage"""
    custom_css()
    
    # Gắn class nền cho Trang Chính
    st.markdown('<div class="stApp main-page-bg">', unsafe_allow_html=True)
    
    # 1. Thanh phát nhạc ngẫu nhiên (Góc trên bên trái)
    music_files = ["background.mp3", "background1.mp3", "background2.mp3", "background3.mp3", "background4.mp3", "background5.mp3"]
    random_track = random.choice(music_files)
    
    # Sử dụng st.sidebar để đặt thanh nhạc góc trên bên trái
    with st.sidebar:
        st.subheader("🎶 Nhạc Nền Cổ Điển")
        st.audio(random_track, format="audio/mp3", start_time=0, loop=True) 
        st.caption(f"Đang phát ngẫu nhiên: **{random_track}**")

    # 2. Tiêu đề canh giữa
    st.markdown("<h1 style='text-align: center; font-size: 3.5em; text-shadow: 1px 1px 2px #FFF8DC;'>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)
    
    # 3. Nội dung rỗng
    st.markdown('<div style="height: 50vh;"></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# --- Luồng Ứng Dụng Chính ---
if st.session_state['intro_complete']:
    main_page()
else:
    intro_screen()
