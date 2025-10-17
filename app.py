import streamlit as st
import random
import time

# --- Cấu hình Trang (Luôn đặt ở đầu) ---
st.set_page_config(layout="wide", page_title="Tổ Bảo Dưỡng Số 1")

# --- Khởi tạo Session State ---
if 'intro_complete' not in st.session_state:
    st.session_state['intro_complete'] = False

# --- Khắc phục: CSS Tùy chỉnh & JavaScript để Chuyển Trang Mượt mà ---

def custom_css_js():
    """CSS và JS để xử lý hiệu ứng video và chuyển trang"""
    # Chọn ảnh nền dựa trên giả định thiết bị (dùng Media Query trong CSS)
    
    # CSS cho nền và font chữ Vintage
    vintage_css = f"""
    <style>
    /* CSS Chung cho Trang Chính */
    .main-page-bg {{
        background-image: url("cabbage.jpg"); /* Ảnh nền PC/Default */
    }}
    
    /* Media Query cho Mobile */
    @media only screen and (max-width: 768px) {{
        .main-page-bg {{
            background-image: url("mobile.jpg"); /* Ảnh nền Mobile */
        }}
    }}

    .stApp {{
        /* Áp dụng nền cho cả app */
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }}

    /* Thêm class cho Trang Chính để nhận nền */
    .reportview-container .main .block-container {{
        padding-top: 0rem;
        padding-bottom: 0rem;
    }}
    
    /* Thiết lập font chữ kiểu cổ điển */
    h1, .stText, p, .stMarkdown, label {{
        font-family: 'Times New Roman', serif; /* Font cổ điển */
        color: #5D4037; /* Màu nâu đậm, cổ kính */
    }}
    
    /* Hiệu ứng chữ Intro */
    @keyframes fade_in_out {{
        0% {{ opacity: 0; }}
        10% {{ opacity: 1; }} /* Xuất hiện nhanh hơn */
        90% {{ opacity: 1; }}
        100% {{ opacity: 0; }} /* Biến mất ở cuối video */
    }}
    
    #intro-text {{
        position: fixed; /* Dùng fixed để luôn nằm trên cùng */
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 3em;
        color: white;
        text-shadow: 2px 2px 4px #000000;
        animation: fade_in_out 4s forwards; 
        z-index: 10000; /* Đảm bảo nằm trên mọi thứ */
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
        background-color: black;
        opacity: 1;
        transition: opacity 1s ease-out; /* Hiệu ứng mờ 1s */
    }}
    
    #intro-video-container.fade-out {{
        animation: video_fade_out 1s forwards; /* Tên hiệu ứng */
        animation-delay: 4s; /* Bắt đầu mờ sau 4s (tổng video 5s) */
    }}

    </style>
    """
    st.markdown(vintage_css, unsafe_allow_html=True)

    # JavaScript để kích hoạt video và lắng nghe sự kiện kết thúc
    js_script = """
    <script>
    const video = document.getElementById('intro-video');
    const container = document.getElementById('intro-video-container');
    
    // Khởi chạy video và thêm hiệu ứng chuyển cảnh
    if (video) {
        // Thử chạy video
        video.play().catch(error => {
            console.log("Autoplay prevented:", error);
            // Có thể hiện nút "Bắt đầu" nếu cần thiết
        });

        // Thêm class 'fade-out' để kích hoạt hiệu ứng mờ sau 4s
        setTimeout(() => {
            if (container) {
                container.classList.add('fade-out');
            }
        }, 4000); // 4 giây trước khi mờ
        
        // Lắng nghe sự kiện video kết thúc sau 5s
        setTimeout(() => {
            // Gửi một thông điệp (chuyển trạng thái) về Streamlit
            window.parent.document.dispatchEvent(new CustomEvent('streamlit:setSessionState', {
                detail: {key: 'intro_complete', value: true}
            }));
            // Bỏ container video ra khỏi DOM sau khi mờ xong
            if (container) {
                container.remove();
            }
        }, 5000); // 5 giây sau đó
    }
    </script>
    """
    st.components.v1.html(js_script, height=0, width=0) # Nhúng JS vào Streamlit

# --- Định nghĩa các Màn hình ---

def intro_screen():
    """Màn hình Intro với Video và Chữ (Sử dụng components.v1.html)"""
    st.empty() # Xóa hết nội dung cũ
    custom_css_js() # Nhúng CSS/JS cần thiết

    # HTML/Video cho màn hình Intro
    video_html = """
    <div id="intro-video-container">
        <video id="intro-video" width="100%" height="100%" autoplay muted playsinline style="object-fit: cover;">
            <source src="airplane.mp4" type="video/mp4">
            Your browser does not support the video tag.
        </video>
    </div>
    <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    """
    # st.components.v1.html là cách tốt nhất để nhúng HTML/Video/JS tùy chỉnh
    st.components.v1.html(video_html, height=700, scrolling=False)


def main_page():
    """Trang Chính Tối Giản theo phong cách Vintage"""
    
    # Áp dụng CSS Vintage và nền
    st.markdown('<div class="stApp main-page-bg">', unsafe_allow_html=True)
    custom_css_js() 

    # 1. Thanh phát nhạc ngẫu nhiên (Góc trên bên trái)
    music_files = [f"background{i}.mp3" for i in range(6)] # background.mp3 đến background5.mp3
    random_track = random.choice(music_files)
    
    # Sử dụng st.sidebar để đặt thanh nhạc góc trên bên trái
    with st.sidebar:
        st.subheader("🎶 Nhạc Nền Cổ Điển")
        # Dùng st.audio để phát nhạc
        st.audio(random_track, format="audio/mp3", start_time=0, loop=True) # loop=True để phát lại ngẫu nhiên
        st.caption(f"Đang phát ngẫu nhiên: **{random_track}**")
        st.markdown(
            """
            <style>
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
            """, unsafe_allow_html=True
        )

    # 2. Tiêu đề canh giữa
    st.markdown("<h1 style='text-align: center; color: #4E342E; font-size: 3.5em; text-shadow: 1px 1px 2px #FFF8DC;'>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)
    
    # 3. Nội dung rỗng (đã xóa các đoạn text yêu cầu)
    st.empty() 

    st.markdown('</div>', unsafe_allow_html=True) # Kết thúc div .main-page-bg


# --- Luồng Ứng Dụng Chính ---
if st.session_state['intro_complete']:
    main_page()
else:
    intro_screen()

# --- Xử lý sự kiện sau khi JS chuyển trạng thái ---
# Vì JS không thể tự động gọi st.rerun(), ta thêm một button ẩn để buộc Streamlit cập nhật
if st.session_state['intro_complete'] and st.button('Click to start', key='hidden_start_btn'):
    st.rerun()
# Note: Dù có st.rerun() hay không, Streamlit sẽ tự động cập nhật session state khi có tương tác
# hoặc khi JS gửi lệnh. Tùy thuộc vào môi trường, bạn có thể thấy trang chính xuất hiện ngay
# sau 5s hoặc cần một tương tác nhỏ.
