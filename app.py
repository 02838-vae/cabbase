import streamlit as st
import random
import time
import base64 # Cần thiết để nhúng HTML local

# --- Cấu hình Trang (Luôn đặt ở đầu) ---
st.set_page_config(layout="wide", page_title="Tổ Bảo Dưỡng Số 1")

# --- Khởi tạo Session State ---
if 'intro_complete' not in st.session_state:
    st.session_state['intro_complete'] = False

# --- CSS Tùy chỉnh (Định nghĩa Phong cách Vintage và Hiệu ứng) ---
def custom_css():
    """CSS cho Trang Chính (kèm Media Query cho nền)"""
    
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
        color: #4E342E; /* Màu nâu đậm */
    }}

    /* Định dạng lại st.audio trong sidebar cho phong cách Vintage */
    [data-testid="stSidebarContent"] {{
        background-color: rgba(255, 255, 240, 0.9); /* Nền sidebar màu ngà */
        padding: 15px;
        border-right: 2px solid #A1887F; /* Thêm viền cổ */
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

def embed_intro_video():
    """Nhúng file HTML video intro sử dụng base64"""
    try:
        with open("intro_video.html", "r") as f:
            html_code = f.read()
        
        # Mã hóa HTML sang base64 để nhúng vào iframe (giải pháp tốt nhất cho Streamlit)
        b64_html = base64.b64encode(html_code.encode()).decode()
        
        # Nhúng iframe
        st.components.v1.html(
            f'<iframe src="data:text/html;base64,{b64_html}" width="100%" height="100%" frameborder="0" style="position:fixed; top:0; left:0; z-index:9999;"></iframe>',
            height=700, # Chiều cao tạm thời, iframe sẽ chiếm toàn màn hình
            scrolling=False
        )

    except FileNotFoundError:
        st.error("Lỗi: Không tìm thấy file 'intro_video.html' hoặc 'airplane.mp4'. Vui lòng kiểm tra lại đường dẫn.")
        # Tự động chuyển trang nếu video lỗi
        time.sleep(1)
        st.session_state['intro_complete'] = True
        st.rerun()

def main_page():
    """Trang Chính Tối Giản theo phong cách Vintage"""
    custom_css() # Áp dụng CSS
    
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
    st.empty()
    st.markdown('<div style="height: 50vh;"></div>', unsafe_allow_html=True) # Giữ cho trang không bị trống rỗng

    st.markdown('</div>', unsafe_allow_html=True)

# --- Luồng Ứng Dụng Chính ---

if not st.session_state['intro_complete']:
    embed_intro_video()
    
    # --- XỬ LÝ SỰ KIỆN CHUYỂN TRANG TỪ IFRAME ---
    # Nghe thông điệp từ JavaScript trong iframe
    st.components.v1.html("""
        <script>
            window.addEventListener('message', event => {
                if (event.data && event.data.type === 'intro_done') {
                    // Cập nhật session state của Streamlit để kích hoạt chuyển trang
                    // Tự động reload trang sau khi nhận thông điệp
                    window.parent.location.reload(); 
                }
            });
        </script>
    """, height=0, width=0)

else:
    main_page()
