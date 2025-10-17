import streamlit as st
import random
import time
import os

# Tên file ảnh nền chính xác
PC_BACKGROUND = "cabbase.jpg" # Đã sửa lại theo yêu cầu của bạn
MOBILE_BACKGROUND = "mobile.jpg"
VIDEO_INTRO = "airplane.mp4"

# --- Cấu hình Trang (Luôn đặt ở đầu) ---
st.set_page_config(layout="wide", page_title="Tổ Bảo Dưỡng Số 1")

# --- Khởi tạo Session State ---
if 'intro_complete' not in st.session_state:
    st.session_state['intro_complete'] = False
if 'intro_start_time' not in st.session_state:
    st.session_state['intro_start_time'] = time.time()

# --- CSS Tùy chỉnh (Định nghĩa Phong cách Vintage và Hiệu ứng) ---
def custom_css():
    """CSS cho Trang Chính (kèm Media Query cho nền) và hiệu ứng Intro"""
    
    vintage_css = f"""
    <style>
    /* CSS Chung cho nền Trang Chính */
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
            background-image: url("{MOBILE_BACKGROUND}"); /* Ảnh nền Mobile */
        }}
    }}

    /* Thiết lập font chữ kiểu cổ điển */
    h1, .stText, p, .stMarkdown, label {{
        font-family: 'Times New Roman', serif; 
        color: #4E342E; /* Màu nâu đậm */
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
        100% {{ opacity: 0; visibility: hidden; }}
    }}
    
    /* Container video */
    #video-container-fade {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 9999;
        opacity: 1;
        animation: video_fade_out 1s forwards; /* Hiệu ứng mờ 1s */
        animation-delay: 4s; /* Bắt đầu mờ sau 4s (tổng video 5s) */
        overflow: hidden;
        background-color: black;
    }}
    
    /* Căn giữa video trong container */
    #video-container-fade video {{
        position: absolute;
        top: 50%;
        left: 50%;
        min-width: 100%; 
        min-height: 100%;
        width: auto;
        height: auto;
        transform: translate(-50%, -50%);
        object-fit: cover;
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

def embed_intro_video_and_text():
    """Nhúng video và chữ intro sử dụng HTML/CSS trực tiếp"""
    custom_css()
    
    if not os.path.exists(VIDEO_INTRO):
        st.error(f"Lỗi: Không tìm thấy file video **{VIDEO_INTRO}**. Vui lòng kiểm tra lại đường dẫn.")
        time.sleep(2)
        st.session_state['intro_complete'] = True
        st.rerun()
        return

    # Sử dụng st.markdown để nhúng video HTML
    video_html = f"""
    <div id="video-container-fade">
        <video id="intro-video" autoplay muted playsinline loop
               style="object-fit: cover; width: 100%; height: 100%;"
               src="{VIDEO_INTRO}">
            Trình duyệt của bạn không hỗ trợ video.
        </video>
    </div>
    <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    """
    
    st.markdown(video_html, unsafe_allow_html=True)
    
    # --- KÍCH HOẠT CHUYỂN TRANG SAU 5 GIÂY ---
    time_elapsed = time.time() - st.session_state['intro_start_time']
    
    if time_elapsed > 5.5: # 5 giây video + 0.5s buffer
        st.session_state['intro_complete'] = True
        st.rerun() 
    else:
        # Tạm dừng 1 giây và buộc rerender để đếm ngược
        st.empty().write(f"Đang tải Intro... ({int(time_elapsed)}s)")
        time.sleep(1) 
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
    embed_intro_video_and_text()
