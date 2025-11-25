import streamlit as st
import base64
import os
import re 
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

# === FIX 2 & 3: XỬ LÝ SKIP INTRO VÀ FIRST LOAD/REFRESH ===
# 2/ Khi click nút Về trang chủ trên trang phụ cũng k mở tab mới mà đi trực tiếp về trang chính (k chiếu video intro và reveal)
# 3/ Chỉ khi refresh hoặc truy cập lần đầu từ trang chính mới chiếu video intro và reveal
query_params = st.query_params
skip_intro_param = query_params.get("skip_intro", ["0"])[0] == "1"

# Nếu có skip_intro=1 (từ nút Home trên trang phụ), buộc phải skip video intro
# Logic này đảm bảo khi người dùng quay lại trang chủ từ trang phụ sẽ bỏ qua intro
if skip_intro_param:
    st.session_state.video_ended = True 

# --- CÁC HÀM TIỆN ÍCH ---

def get_base64_encoded_file(file_path):
    """Đọc file và trả về Base64 encoded string."""
    path_to_check = os.path.join(os.path.dirname(__file__), file_path)
    
    if not os.path.exists(path_to_check) or os.path.getsize(path_to_check) == 0:
        return None 
    
    try:
        with open(path_to_check, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    except Exception as e:
        return None


# Mã hóa các file media chính (bắt buộc)
try:
    video_pc_base64 = get_base64_encoded_file("assets/video_pc.mp4")
    video_mobile_base64 = get_base64_encoded_file("assets/video_mobile.mp4")
    # Lấy logo nếu có
    logo_base64 = get_base64_encoded_file("assets/logo.jpg") or get_base64_encoded_file("logo.jpg")

    if not video_pc_base64 or not video_mobile_base64:
        st.error("Không tìm thấy các file video intro: 'assets/video_pc.mp4' hoặc 'assets/video_mobile.mp4'. Vui lòng kiểm tra lại đường dẫn.")
        st.stop()
except Exception as e:
    st.error(f"Lỗi khi mã hóa file: {e}")
    st.stop()


# --- CSS CHÍNH ---

main_css = f"""
<style>
    /* Ẩn Streamlit Header, Footer và Menu */
    #MainMenu, footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stApp {{background-color: #0d1117;}}
    
    /* Thiết lập bố cục chung */
    .stApp > div:first-child {{
        padding: 0;
        margin: 0;
    }}
    .stApp .block-container {{
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }}

    /* Thẻ tiêu đề chính */
    #main-title-container {{
        text-align: center;
        margin-top: 50px;
        margin-bottom: 30px;
        color: #FFFFFF;
        font-family: 'Arial Black', Gadget, sans-serif;
        text-shadow: 2px 2px 4px #000000;
        background: -webkit-linear-gradient(90deg, #00FF00, #FFFF00, #00FF00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: clamp(2.5rem, 5vw, 6rem);
        line-height: 1.1;
    }}
    .number-one {{
        font-size: clamp(3rem, 6vw, 7rem);
        color: #00FF00; 
        text-shadow: 0 0 10px #00FF00, 0 0 20px #00FF00, 0 0 30px #00FF00; 
        margin-left: 10px;
    }}

    /* Logo */
    .logo-img {{
        width: clamp(100px, 15vw, 200px);
        height: auto;
        border-radius: 15px;
        box-shadow: 0 0 15px #00FF00;
        margin-bottom: 20px;
    }}
    
    /* Video Container */
    .video-container {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: 1000;
        background-color: #000;
        display: flex;
        justify-content: center;
        align-items: center;
        transition: opacity 1s ease-out;
        opacity: 1; /* Mặc định hiển thị */
    }}
    .video-container.hidden {{
        opacity: 0;
        pointer-events: none;
    }}
    .intro-video {{
        width: 100%;
        height: 100%;
        object-fit: cover;
    }}

    /* Reveal effect */
    .reveal-overlay {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background-color: #0d1117; /* Màu nền của ứng dụng */
        z-index: 999; /* Dưới video, trên nội dung */
        transition: opacity 1s ease-out;
        opacity: 1; /* Mặc định hiển thị */
        pointer-events: none;
    }}
    .reveal-overlay.hidden {{
        opacity: 0;
    }}

    /* Điều chỉnh video cho PC/Mobile */
    .video-pc-only, .video-mobile-only {{
        display: none;
    }}
    @media (min-width: 768px) {{
        .video-pc-only {{ display: block; }}
    }}
    @media (max-width: 767px) {{
        .video-mobile-only {{ display: block; }}
    }}

    /* Navigation Buttons */
    .nav-buttons-wrapper {{
        display: flex;
        justify-content: center;
        gap: 30px;
        margin-top: 50px;
    }}
    .nav-button {{
        background-color: #008000;
        color: white !important;
        padding: 15px 30px;
        border-radius: 12px;
        text-decoration: none;
        font-weight: bold;
        font-size: 1.2rem;
        box-shadow: 0 6px #006400, 0 0 10px rgba(0, 255, 0, 0.5);
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        gap: 10px;
        border: none;
        cursor: pointer;
    }}
    .nav-button:hover {{
        background-color: #00B000;
        box-shadow: 0 4px #006400, 0 0 15px rgba(0, 255, 0, 0.8);
        transform: translateY(-2px);
    }}
    .nav-button:active {{
        transform: translateY(2px);
        box-shadow: 0 2px #004d00;
    }}
    .nav-button svg {{
        width: 24px;
        height: 24px;
        stroke: white;
    }}
    
    /* Media query cho mobile */
    @media (max-width: 600px) {{
        .nav-buttons-wrapper {{
            flex-direction: column;
            gap: 15px;
        }}
        .nav-button {{
            width: 80%;
            margin: 0 auto;
            justify-content: center;
        }}
    }}
</style>
"""

# --- JAVASCRIPT ĐIỀU KHIỂN VIDEO ---
js_code = """
<script>
    const videoPc = document.getElementById('intro-video-pc');
    const videoMobile = document.getElementById('intro-video-mobile');
    const videoContainer = document.getElementById('video-intro-container');
    const revealOverlay = document.getElementById('reveal-overlay');
    
    // Chọn video tương ứng với thiết bị
    const videoToPlay = window.innerWidth >= 768 ? videoPc : videoMobile;

    if (videoContainer && videoToPlay) {
        // Chỉ chạy video nếu chưa kết thúc (hoặc st.session_state.video_ended = False)
        if (videoContainer.getAttribute('data-ended') === 'false') {
            
            // Xử lý khi video kết thúc
            const handleVideoEnd = () => {
                videoContainer.classList.add('hidden');
                revealOverlay.classList.add('hidden');

                // Gửi sự kiện về Streamlit để cập nhật session state
                const finishedEvent = new CustomEvent('videoFinished');
                window.parent.document.dispatchEvent(finishedEvent);
            };

            // Gán sự kiện cho video đang phát
            videoToPlay.addEventListener('ended', handleVideoEnd);
            videoToPlay.play().catch(error => {
                // Autoplay failed, có thể do trình duyệt
                console.warn("Autoplay failed:", error);
                // Tự động bỏ qua sau 2 giây nếu không thể autoplay
                setTimeout(handleVideoEnd, 2000); 
            });

        } else {
            // Video đã chạy xong, ẩn ngay lập tức
            videoContainer.classList.add('hidden');
            revealOverlay.classList.add('hidden');
        }
    }
</script>
"""

# --- GHI ĐÈ CSS & JS VÀO STREAMLIT ---
st.markdown(main_css, unsafe_allow_html=True)

# Ghi JS và một phần HTML để video chạy được
if not st.session_state.video_ended:
    st.components.v1.html(
        f"""
        <div id="video-intro-container" class="video-container" data-ended="{st.session_state.video_ended}">
            <video id="intro-video-pc" class="intro-video video-pc-only" muted playsinline>
                <source src="data:video/mp4;base64,{video_pc_base64}" type="video/mp4">
            </video>
            <video id="intro-video-mobile" class="intro-video video-mobile-only" muted playsinline>
                <source src="data:video/mp4;base64,{video_mobile_base64}" type="video/mp4">
            </video>
        </div>
        <div id="reveal-overlay" class="reveal-overlay"></div>
        {js_code}
        """, 
        height=0, width=0
    )
    
    # Listen cho sự kiện videoFinished từ JS
    st.components.v1.html(
        """
        <script>
        function sendBackToStreamlit() {
            // Kiểm tra xem đã gửi về Streamlit chưa để tránh loop
            if (!window.finishedSent) {
                window.finishedSent = true;
                // Gửi tín hiệu về Streamlit
                var iframe = window.parent.document.querySelector('iframe[title="Streamlit App"]');
                if (iframe) {
                    // Tạo form và submit để kích hoạt rerun/callback
                    var form = document.createElement('form');
                    form.action = '';
                    form.method = 'POST';
                    var input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = 'video_done';
                    input.value = 'true';
                    form.appendChild(input);
                    document.body.appendChild(form);
                    form.submit();
                }
            }
        }
        
        // Listener cho CustomEvent từ video player
        window.parent.document.addEventListener('videoFinished', sendBackToStreamlit);
        
        // Kiểm tra nếu Streamlit đã nhận được tín hiệu qua form submit
        // Khi Streamlit rerun, video_done sẽ tồn tại trong query params của iframe
        if (window.location.search.includes('video_done=true')) {
            // Dọn dẹp session state trong JS để tránh gửi lại
            window.parent.document.removeEventListener('videoFinished', sendBackToStreamlit);
        }
        </script>
        """, 
        height=0, width=0
    )
    
    # Kiểm tra form submit để cập nhật state trong Python
    if st.query_params.get("video_done") == "true":
        st.session_state.video_ended = True
        # Sau khi cập nhật state, redirect để làm sạch URL (bỏ video_done=true)
        # Sử dụng time.sleep để Streamlit kịp cập nhật state trước khi redirect
        time.sleep(0.1) 
        st.query_params.clear()
        st.experimental_rerun()
    
    # Nếu đang chạy intro, tạm thời không hiển thị nội dung chính
    if not st.session_state.video_ended:
        st.stop()


# --- NỘI DUNG CHÍNH (CHỈ HIỂN THỊ KHI VIDEO_ENDED = TRUE) ---

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if logo_base64:
        st.markdown(f"""
            <div style="text-align: center;">
                <img src="data:image/jpeg;base64,{logo_base64}" class="logo-img" />
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("""
        <div id="main-title-container">
            <h1>TỔ BẢO DƯỠNG SỐ <span class="number-one">1</span></h1>
        </div>
        """, unsafe_allow_html=True)

# --- NAVIGATION BUTTONS (SIMPLE HTML VERSION) ---
# FIX 1: Thêm target="_self" để k mở tab mới
st.markdown("""
<div class="nav-buttons-wrapper">
    <a href="/partnumber" class="nav-button" target="_self">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"></path>
        </svg>
        <span>TRA CỨU PART NUMBER</span>
    </a>
    <a href="/bank" class="nav-button" target="_self">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 7.5h1.5m-1.5 3h1.5m-7.5 3h7.5m-7.5 3h7.5m3-9h1.5m-1.5 3h1.5m-7.5 3h7.5m-7.5 3h7.5M3 10.5a.75.75 0 01.75-.75h14.25a.75.75 0 01.75.75v6.75a.75.75 0 01-.75.75H3.75a.75.75 0 01-.75-.75v-6.75z"></path>
        </svg>
        <span>NGÂN HÀNG CÂU HỎI</span>
    </a>
</div>
""", unsafe_allow_html=True)
