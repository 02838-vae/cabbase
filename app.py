import streamlit as st
import base64
import os

# --- CẤU HÌNH TRANG ---
# Tiêu đề chính xác mà ứng dụng sẽ reset về sau khi video kết thúc
APP_TITLE_RESET = "Ứng dụng Tra Cứu Part Number - Tổ Bảo Dưỡng Số 1"

st.set_page_config(
    page_title=APP_TITLE_RESET, 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- HÀM HỖ TRỢ ---
def get_base64_encoded_file(file_path):
    """Mã hóa file ảnh sang base64 để dùng trong CSS."""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        # Placeholder 1x1 pixel base64 nếu file không tìm thấy
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return "iVBORw0KGgoAAAANHHEAAAABJRU5ErkJggg=="

# --- TẢI TÀI NGUYÊN ---
PC_VIDEO_PATH = "airplane.mp4"    # Video cho PC/màn hình lớn
MOBILE_VIDEO_PATH = "mobile.mp4"  # Video cho Mobile/màn hình nhỏ
LOGO_PATH = "logo.jpg" 

logo_base64 = get_base64_encoded_file(LOGO_PATH)

# Kiểm tra tham số truy vấn để quyết định có bỏ qua video hay không
try:
    query_params = st.query_params
except AttributeError:
    query_params = st.experimental_get_query_params()

# Logic để bỏ qua video intro
# Kiểm tra nếu 'skip_intro' tồn tại và có giá trị là '1'
skip_intro = 'skip_intro' in query_params and (query_params.get('skip_intro') == ['1'] or query_params.get('skip_intro') == '1')
show_video_placeholder = st.empty()

# --- CSS VÀ CẤU HÌNH GIAO DIỆN ---
hide_streamlit_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;700&display=swap');
#MainMenu, footer, header {{visibility: hidden;}}

.stApp {{
    /* Dùng logo làm nền mờ cho music player trong partnumber.py */
    --logo-bg-url: url('data:image/jpeg;base64,{logo_base64}'); 
    background-color: #000000 !important; /* Nền đen cho trang chủ */
    font-family: 'Oswald', sans-serif !important;
}}

/* Giấu nội dung chính khi video đang chạy */
.main-content-hidden {{
    display: none;
}}

.css-1d3w5rq, .stApp > header {{
    display: none;
}}

/* Fix: Đảm bảo sidebar không hiển thị */
.css-1eewqq2 {{
    display: none !important;
}}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- XỬ LÝ VIDEO INTRO VÀ REVEAL ---
if not skip_intro:
    video_placeholder = st.empty()
    
    # 2. KIỂM TRA FILE VIDEO TỒN TẠI (Kiểm tra ít nhất một file)
    if (os.path.exists(PC_VIDEO_PATH) and os.path.getsize(PC_VIDEO_PATH) > 0) or \
       (os.path.exists(MOBILE_VIDEO_PATH) and os.path.getsize(MOBILE_VIDEO_PATH) > 0):
        
        # 3. HIỂN THỊ VIDEO CONTAINER
        with video_placeholder.container():
            st.markdown(f"""
                <div id="video-intro-container" style="position: fixed; top: 0; left: 0; width: 100%; height: 100vh; background: black; z-index: 9999;">
                    <video id="intro-video" width="100%" height="100%" autoplay muted playsinline style="object-fit: cover;">
                        <!-- Source sẽ được set bằng JavaScript ở dưới -->
                        Trình duyệt của bạn không hỗ trợ thẻ video.
                    </video>
                </div>
            """, unsafe_allow_html=True)
            
            # 4. JAVASCRIPT XỬ LÝ KẾT THÚC VIDEO VÀ CHUYỂN NGUỒN
            st.components.v1.html(f"""
            <script>
                const video = window.parent.document.getElementById('intro-video');
                const videoContainer = window.parent.document.getElementById('video-intro-container');
                const pcVideoSrc = '{PC_VIDEO_PATH}';
                const mobileVideoSrc = '{MOBILE_VIDEO_PATH}';
                
                if (video) {{
                    // HÀM CHỌN NGUỒN VIDEO DỰA TRÊN KÍCH THƯỚC MÀN HÌNH
                    function setVideoSource() {{
                        // Dùng 768px làm breakpoint cho mobile
                        const isMobile = window.innerWidth <= 768;
                        const newSrc = isMobile ? mobileVideoSrc : pcVideoSrc;
                        
                        // Chỉ cập nhật nguồn nếu nó khác nguồn hiện tại
                        if (video.src.indexOf(newSrc) === -1) {{
                            video.src = newSrc;
                            console.log('Video source set to: ' + newSrc);
                            video.load();
                            // Cố gắng phát lại (cần thiết sau khi set source mới)
                            video.play().catch(e => {{
                                console.log("Autoplay blocked, user interaction required.");
                            }});
                        }}
                    }}

                    // Set nguồn ban đầu và lắng nghe sự kiện resize
                    setVideoSource();
                    window.addEventListener('resize', setVideoSource);

                    // Set tiêu đề trình duyệt để sau này JS ở dòng cuối cùng biết video đã phát xong
                    window.parent.document.title = "video_running";
                    
                    video.addEventListener('ended', () => {{
                        console.log('Video intro ended. Revealing content.');
                        
                        if (videoContainer) {{
                            videoContainer.style.transition = 'opacity 1.5s ease-out';
                            videoContainer.style.opacity = '0';
                            
                            setTimeout(() => {{
                                // Ẩn hẳn container video sau hiệu ứng mờ dần
                                videoContainer.style.display = 'none';
                                
                                // Set cờ "video_ended_true" trên tiêu đề trình duyệt
                                window.parent.document.title = "video_ended_true";
                            }}, 1500); // 1.5 giây transition
                        }}
                    }});
                    
                    video.addEventListener('error', () => {{
                        console.error('Video load error. Skipping intro.');
                        if (videoContainer) {{
                            videoContainer.style.display = 'none';
                            window.parent.document.title = "video_ended_true";
                        }}
                    }});
                    
                }} else {{
                    console.log("Video element not found.");
                }}
            </script>
            """, height=0)
    else:
        # Nếu lỗi, set skip_intro để hiển thị nội dung chính ngay
        st.error(f"❌ Không tìm thấy file video. Cần có ít nhất một trong hai file: {PC_VIDEO_PATH} hoặc {MOBILE_VIDEO_PATH}.")
        skip_intro = True
        
else:
    # Nếu skip_intro là True, xóa placeholder video ngay lập tức
    show_video_placeholder.empty()

# --- NỘI DUNG CHÍNH (MAIN CONTENT) ---
if skip_intro or (not os.path.exists(PC_VIDEO_PATH) and not os.path.exists(MOBILE_VIDEO_PATH)):
    
    st.title("🛡️ Ứng dụng Tra Cứu Part Number")
    
    # 1. Hướng dẫn người dùng
    st.info("""
    **Chào mừng bạn đến với Ứng dụng Tra Cứu Part Number của Tổ Bảo Dưỡng Số 1.**
    
    Để bắt đầu, vui lòng chọn mục tra cứu từ thanh điều hướng bên trái (hiện đang ẩn do cấu hình, hãy truy cập trực tiếp vào `/partnumber`):
    * **Part Number (PN):** Tra cứu theo Zone, Loại máy bay và Mô tả.
    """)
    
    # 2. Thêm liên kết trực tiếp
    st.markdown("---")
    st.subheader("Bắt đầu Tra Cứu")
    # Đảm bảo đường dẫn này khớp với tên file trang trong thư mục pages/
    st.markdown("""
    ### [👉 Tra Cứu Part Number](partnumber) 
    
    *Lưu ý: Nếu bạn đang ở trang này sau khi nhấn "Về Trang Chủ", video intro sẽ được bỏ qua.*
    """)
    st.markdown("---")
    
    # Thêm một chút nội dung khác cho trang chủ
    try:
        st.columns(3)[1].image(LOGO_PATH, caption="Logo Tổ Bảo Dưỡng Số 1", use_column_width="auto")
    except Exception:
        # Bỏ qua nếu không tìm thấy file logo
        pass 
    
    st.markdown(f"""
    <div style='text-align:center; padding: 20px; font-size: 1.1rem; color: #aaaaaa;'>
        © 2025 {APP_TITLE_RESET}. Phát triển bởi Tổ Bảo Dưỡng Số 1.
    </div>
    """, unsafe_allow_html=True)
    
else:
    # Nếu đang trong quá trình chờ video, chỉ hiển thị một màn hình đen hoặc thông báo ngắn
    st.empty() 

# --- JAVASCRIPT FIX: RESET TIÊU ĐỀ SAU KHI VIDEO KẾT THÚC ---
st.empty().markdown(
    f"""
    <script>
        // Kiểm tra nếu tiêu đề đã được JS của video set thành cờ "video_ended_true"
        if(window.parent.document.title === "video_ended_true") {{
            // 1. Reset tiêu đề trình duyệt (Khắc phục RuntimeError)
            window.parent.document.title = "{APP_TITLE_RESET}";
            
            // 2. Kích hoạt Streamlit re-run để loại bỏ container video bằng Python
            // Đặt tham số 'skip_intro=1' để lần chạy tiếp theo hiển thị nội dung chính
            window.parent.history.pushState(null, null, '/?skip_intro=1');
        }}
    </script>
    """, 
    unsafe_allow_html=True
)
