import streamlit as st
import base64
import os

# --- CẤU HÌNH BAN ĐẦU ---
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

# Tên các file cần thiết
video_file = "airplane.mp4"
bg_file = "cabbase.jpg"
audio_file = "background.mp3"

# Ước tính thời gian chuyển cảnh (Cần điều chỉnh)
VIDEO_DURATION_SECONDS = 5
FADE_DURATION_SECONDS = 4
TOTAL_DELAY_SECONDS = VIDEO_DURATION_SECONDS + FADE_DURATION_SECONDS

# Hàm đọc file và chuyển thành Base64
def get_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        return None

# Hàm callback khi kích hoạt chuyển cảnh
def switch_to_main():
    # Khi nút vô hình được nhấn, thay đổi cờ
    st.session_state.show_main = True
    # Không cần st.rerun() ở đây, vì việc nhấn nút đã kích hoạt Streamlit rerun

# Khởi tạo Session State
if "show_main" not in st.session_state:
    st.session_state.show_main = False

# --- GIAO DIỆN CHUYỂN CẢNH (VIDEO INTRO) ---
if not st.session_state.show_main:
    
    video_data = get_base64(video_file)
    if video_data is None:
        st.error(f"❌ Không tìm thấy file {video_file}. Vui lòng kiểm tra lại tên và đường dẫn file.")
        st.stop()
    
    # === KHẮC PHỤC 1: ẨN NÚT NGAY LẬP TỨC ===
    # 1. Thêm CSS để ẩn tất cả các nút có key này ngay từ đầu
    st.markdown(f"""
    <style>
    /* Ẩn triệt để nút Vô hình trước khi video chạy */
    [data-testid="stButton"] button[key="switch_trigger_button"] {{
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
        opacity: 0 !important;
        display: none !important; 
    }}

    /* CSS cho trang video */
    html, body {{ margin:0; padding:0; height:100%; overflow:hidden; background:black; }}
    .video-container {{
        position: fixed; inset:0; width:100%; height:100%;
        display:flex; justify-content:center; align-items:center;
        background:black; z-index:9999;
        animation: fadeOut {FADE_DURATION_SECONDS}s ease-out {VIDEO_DURATION_SECONDS}s forwards; 
    }}
    .video-bg {{ width:100%; height:100%; object-fit:cover; }}
    
    /* Hiệu ứng mờ dần */
    @keyframes fadeOut {{
        0% {{opacity:1; visibility:visible;}}
        99% {{opacity:0.01; visibility:visible;}}
        100%{{opacity:0; visibility:hidden;}}
    }}
    
    /* Giữ nguyên các animation khác */
    .video-text {{
        position:absolute; bottom:12vh; width:100%; text-align:center;
        font-family:'Special Elite', cursive; font-size:clamp(24px,5vw,44px);
        font-weight:bold; color:#fff;
        text-shadow: 0 0 20px rgba(255,255,255,0.8), 0 0 40px rgba(180,220,255,0.6), 0 0 60px rgba(255,255,255,0.4);
        opacity:0;
        animation: appear 3s ease-in forwards, floatFade 3s ease-in 5s forwards;
    }}
    @keyframes appear {{ 0% {{opacity:0; filter:blur(8px); transform:translateY(40px);}} 100%{{opacity:1; filter:blur(0); transform:translateY(0);}} }}
    @keyframes floatFade {{ 0% {{opacity:1; filter:blur(0); transform:translateY(0);}} 100%{{opacity:0; filter:blur(12px); transform:translateY(-30px) scale(1.05);}} }}
    </style>
    """, unsafe_allow_html=True)
    
    # 2. Đặt nút Vô hình sau CSS, nhưng nó phải được render.
    # Nút được đặt ở đây và bị ẩn bằng CSS phía trên.
    st.button("Vô hình", key="switch_trigger_button", on_click=switch_to_main)
             
    st.markdown(f"""
    <div class="video-container" id="videoContainer">
        <video id="introVideo" class="video-bg" autoplay muted playsinline>
            <source src="data:video/mp4;base64,{video_data}" type="video/mp4">
        </video>
        <div class="video-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    </div>
    
    <script>
        // === KHẮC PHỤC 2: TỰ ĐỘNG CHUYỂN CẢNH ===
        // Đặt hẹn giờ để kích hoạt nút vô hình sau khi video và fade kết thúc
        setTimeout(() => {{
            // Tìm nút vô hình bằng thuộc tính 'key' trong DOM (Đảm bảo độ chính xác)
            const switchButton = window.parent.document.querySelector('[data-testid="stButton"] button[key="switch_trigger_button"]');
            
            if (switchButton) {{
                // Kích hoạt callback switch_to_main()
                switchButton.click(); 
                
                // Loại bỏ container video (Mặc dù CSS đã làm, nhưng đảm bảo)
                const container = document.getElementById('videoContainer');
                if (container) {{
                    container.style.display='none';
                }}
            }} else {{
                // Fallback: Nếu không tìm thấy nút, in ra console để debug (nếu bạn chạy console)
                console.error("Lỗi: Không tìm thấy nút kích hoạt Streamlit.");
            }}
        }}, {TOTAL_DELAY_SECONDS * 1000});
    </script>
    """, unsafe_allow_html=True)
    
    st.stop() # Dừng luồng cho đến khi nút vô hình được kích hoạt

# --- TRANG CHÍNH ---
# ... (Phần code hiển thị trang chính của bạn giữ nguyên) ...
# Bạn không cần phải thay đổi gì trong phần này.
# Code ở đây sẽ tự động chạy sau khi switch_to_main được gọi và Streamlit rerun.
img_base64 = get_base64(bg_file)
if img_base64 is None:
    st.error(f"❌ Không tìm thấy file {bg_file}.")
    st.stop()

st.markdown(f"""
<style>
.stApp {{
    background: linear-gradient(rgba(245,242,200,0.4), rgba(245,242,200,0.4)),
                url("data:image/jpeg;base64,{img_base64}") no-repeat center center fixed;
    background-size: cover;
}}
header[data-testid="stHeader"] {{ display:none; }}
.block-container {{ padding-top:2rem; }}
.main-title {{
    font-family:'Special Elite', cursive;
    font-size: clamp(36px,5vw,48px);
    font-weight:bold; text-align:center;
    color:#3e2723; margin-top:50px;
    text-shadow:2px 2px 0 #fff,0 0 25px #f0d49b,0 0 50px #bca27a;
}}
</style>
""", unsafe_allow_html=True)

audio_base64 = get_base64(audio_file)
if audio_base64:
    st.markdown(f"""
    <audio autoplay loop controls style="position:fixed; top:10px; left:10px; width:200px; z-index:9999;">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
    </audio>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">📜 TỔ BẢO DƯỠNG SỐ 1</div>', unsafe_allow_html=True)
st.write("Chào mừng bạn đến với website ✈️")
