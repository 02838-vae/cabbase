import streamlit as st
import random
import time

# --- Cấu hình Trang (Luôn đặt ở đầu) ---
st.set_page_config(layout="wide", page_title="Tổ Bảo Dưỡng Số 1")

# --- Khởi tạo Session State ---
# 'intro_complete' là cờ để kiểm tra xem Intro đã chạy chưa
if 'intro_complete' not in st.session_state:
    st.session_state['intro_complete'] = False

# --- CSS Tùy chỉnh (Định nghĩa Phong cách Vintage và Hiệu ứng) ---
def local_css(file_name):
    """Hàm nhúng CSS từ file hoặc chuỗi"""
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def custom_css():
    """CSS nhúng trực tiếp"""
    # Lấy tên file ảnh nền dựa vào thiết bị (Streamlit không có hàm kiểm tra trực tiếp)
    # Tạm thời ta chỉ dùng 1 ảnh nền hoặc cần JS để check. Dùng 'cabbage.jpg' làm mặc định.
    # Trong thực tế, bạn cần JS để check viewport width và nhúng CSS tương ứng.
    # Dưới đây là phong cách vintage cơ bản:
    
    # CSS cho nền và font chữ Vintage
    vintage_css = f"""
    <style>
    /* Ẩn thanh cuộn mặc định của Streamlit và làm cho nền ảnh bao phủ */
    .stApp {{
        background-image: url("cabbage.jpg"); /* Ảnh nền PC/Default */
        background-size: cover;
        background-attachment: fixed; /* Giữ ảnh nền cố định khi cuộn */
        background-position: center;
    }}
    
    /* Thiết lập font chữ kiểu cổ điển (Cần cài đặt font nếu muốn chính xác) */
    h1, h2, h3, h4, .stText, p, .stMarkdown, label {{
        font-family: 'Times New Roman', serif; /* Font cổ điển */
        color: #5D4037; /* Màu nâu đậm, cổ kính */
    }}
    
    /* Màu nền cho các khung/widget để tăng tính cổ điển */
    .stMarkdown, .stText, .stButton > button, .stAudio {{
        background-color: rgba(255, 255, 240, 0.7); /* Màu trắng ngà mờ */
        border-radius: 5px;
        padding: 10px;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3); /* Tạo bóng nhẹ */
    }}
    
    /* Hiệu ứng chữ Intro */
    @keyframes fade_in_out {{
        0% {{ opacity: 0; }}
        25% {{ opacity: 1; }}
        75% {{ opacity: 1; }}
        100% {{ opacity: 0; }}
    }}
    
    .intro_text {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 3em;
        color: white;
        text-shadow: 2px 2px 4px #000000;
        animation: fade_in_out 4s forwards; /* 4s để khớp với video 5s (1s cuối mờ) */
        z-index: 1000;
        pointer-events: none;
    }}
    
    /* CSS cho hiệu ứng mờ dần */
    @keyframes fade_out {{
        0% {{ opacity: 1; }}
        100% {{ opacity: 0; }}
    }}
    
    .video_fade_out {{
        animation: fade_out 1s forwards; /* 1s để mờ dần */
        animation-delay: 4s; /* Chờ 4s trước khi bắt đầu mờ (Video 5s) */
    }}
    </style>
    """
    st.markdown(vintage_css, unsafe_allow_html=True)

# --- Định nghĩa các Màn hình ---

def intro_screen():
    """Màn hình Intro với Video và Chữ"""
    st.empty() # Xóa hết nội dung trước
    
    # Áp dụng CSS mờ dần cho Video
    video_html = """
    <div class="video_fade_out" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 999; background-color: black;">
        <video width="100%" height="100%" autoplay muted playsinline style="object-fit: cover;">
            <source src="airplane.mp4" type="video/mp4">
            Your browser does not support the video tag.
        </video>
    </div>
    <div class="intro_text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    """
    st.markdown(video_html, unsafe_allow_html=True)

    # Đặt hẹn giờ để chuyển trạng thái sau 5 giây (Thời lượng video)
    # Streamlit không chạy background thread, nên ta dùng JS/HTML để check time thực tế.
    # Trong môi trường Streamlit, ta dùng `time.sleep` hoặc một trick nhỏ:
    
    # --- TRICK Streamlit để chuyển trạng thái sau time.sleep ---
    # Ta dùng một placeholder và đợi, sau đó cập nhật session state.
    # Lưu ý: Điều này sẽ làm ứng dụng "đứng" 5s. Nếu bạn muốn trải nghiệm mượt hơn, 
    # cần dùng JavaScript để thông báo khi video kết thúc.
    
    if not st.session_state.get('intro_ran'):
        with st.empty():
            time.sleep(5) # Đợi 5 giây
            st.session_state['intro_complete'] = True
            st.session_state['intro_ran'] = True
            st.rerun() # Tải lại trang để chuyển sang Trang chính

def main_page():
    """Trang Chính theo phong cách Vintage"""
    custom_css() # Áp dụng CSS Vintage cho Trang Chính

    # 1. Thanh phát nhạc ngẫu nhiên (Góc trên bên trái)
    music_files = ["background.mp3", "background1.mp3", "background2.mp3", "background3.mp3", "background4.mp3", "background5.mp3"]
    # Chọn ngẫu nhiên một bài để bắt đầu phát
    random_track = random.choice(music_files)
    
    # Sử dụng st.sidebar để đặt thanh nhạc góc trên bên trái
    with st.sidebar:
        st.subheader("🎶 Nhạc Nền Cổ Điển")
        # Dùng st.audio để phát nhạc
        st.audio(random_track, format="audio/mp3", start_time=0)
        st.caption(f"Đang phát: **{random_track}**")
        st.markdown(
            """
            <style>
            /* Định dạng lại st.audio trong sidebar cho phong cách Vintage */
            .stAudio {{
                background-color: rgba(245, 245, 220, 0.8); /* Màu be nhạt */
                border: 1px solid #A1887F; /* Viền nâu cổ */
                border-radius: 10px;
                padding: 5px;
            }}
            </style>
            """, unsafe_allow_html=True
        )

    # 2. Tiêu đề canh giữa
    st.markdown("<h1 style='text-align: center; color: #4E342E; font-size: 3.5em; text-shadow: 1px 1px 2px #FFF8DC;'>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)
    
    st.write("---")

    # 3. Nội dung trang chính (Vintage Content)
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(
            """
            <div style="border: 2px solid #A1887F; padding: 15px; border-radius: 5px; background-color: rgba(255, 255, 240, 0.8);">
                <h2 style='color: #6D4C41;'>📜 Châm Ngôn Phục Hưng</h2>
                <p>
                *Mỗi cỗ máy là một câu chuyện cần được gìn giữ. Chúng tôi không chỉ sửa chữa, chúng tôi hồi sinh Ký ức.*
                </p>
                <p>
                Thời đại không thể xóa nhòa đi giá trị của sự Tinh Xảo. Hãy để những cổ vật của bạn lại Tỏa Sáng!
                </p>
            </div>
            """, unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div style="border: 2px solid #A1887F; padding: 15px; border-radius: 5px; background-color: rgba(255, 255, 240, 0.8);">
                <h2 style='color: #6D4C41;'>⚙️ Dịch Vụ Của Chúng Tôi</h2>
                <ul>
                    <li>Phục hồi đồng hồ cổ và máy đánh chữ.</li>
                    <li>Bảo dưỡng xe đạp, xe máy cổ.</li>
                    <li>Sửa chữa các thiết bị cơ khí thủ công.</li>
                </ul>
                <p style="text-align: right; font-style: italic;">Liên hệ: 1800-VINTAGE</p>
            </div>
            """, unsafe_allow_html=True
        )
    
    # Giả lập thêm một số nội dung nữa
    st.write("\n")
    st.subheader("Bộ Sưu Tập Tiêu Biểu")
    st.image("cabbage.jpg", caption="Hình ảnh chỉ mang tính minh họa cho phong cách cổ điển", width=400)


# --- Luồng Ứng Dụng Chính ---
if st.session_state['intro_complete']:
    main_page()
else:
    intro_screen()
