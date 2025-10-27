import streamlit as st
import base64
import os
# THAY THẾ: import react_player thành st_player
from streamlit_player import st_player 
import streamlit.components.v1 as components

# --- 1. KHỞI TẠO STATE AN TOÀN ---
if 'video_ended' not in st.session_state:
    st.session_state.video_ended = False
if 'ran_once' not in st.session_state:
    st.session_state.ran_once = False
if 'rerun_done' not in st.session_state:
    st.session_state.rerun_done = False 

# --- CÁC HÀM TIỆN ÍCH DÙNG BASE64 ---

def get_base64_encoded_file(file_path):
    """Đọc file và trả về Base64 encoded string hoặc byte data."""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return data, base64.b64encode(data).decode("utf-8")
    except FileNotFoundError as e:
        st.error(f"LỖI CỐT LÕI: Không tìm thấy file media. Vui lòng kiểm tra đường dẫn: {e.filename}")
        st.stop()

# --- 2. BIẾN TOÀN CỤC VÀ TẢI DỮ LIỆU ---

try:
    video_pc_data, video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_data, video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_intro_data, audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    
    bg_pc_data, bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_data, bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")

    # Tải file nhạc nền background1.mp3 dưới dạng bytes
    audio_bg_data, _ = get_base64_encoded_file("background1.mp3")

    # Tạo Base64 Data URL cho st_player
    base64_data_url = f"data:audio/mp3;base64,{base64.b64encode(audio_bg_data).decode('utf-8')}"

except Exception as e:
    pass 

# --- 3. CẤU HÌNH BAN ĐẦU & CSS ---

st.set_page_config(
    page_title="Tổ Bảo Dưỡng Số 1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

font_links = """
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
"""
st.markdown(font_links, unsafe_allow_html=True)


hide_streamlit_style = f"""
<style>
#MainMenu, footer, header {{visibility: hidden;}}

/* ... (Các CSS khác giữ nguyên) ... */

/* CSS cho Player - Tùy chỉnh vị trí và kiểu dáng */
/* st-player thường là một div wrapper, tên class có thể khác */
/* Bạn có thể cần điều chỉnh selector này sau khi chạy thử */
[data-testid="stComponentV1"] {{
    position: fixed !important; 
    bottom: 20px !important; 
    left: 20px !important;
    z-index: 100 !important;
}}

</style>
"""
# *Lưu ý: Để code ngắn gọn, tôi không dán toàn bộ CSS, nhưng bạn cần giữ lại nó.*
# Bạn cần đảm bảo các biến base64 (ví dụ: {bg_pc_base64}) được dùng trong CSS.
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- 4. VIDEO INTRO & LOGIC RERUNING ---

# JavaScript Callback cho Video Intro (Giữ nguyên)
js_callback_video = f"""
<script>
    function sendBackToStreamlit() {{
        // Gửi lệnh SET_QUERY_PARAMS để kích hoạt rerun Streamlit
        window.parent.postMessage({{
            streamlit: {{
                command: 'SET_QUERY_PARAMS',
                query_params: {{ 'video_ended': ['true'] }}
            }}
        }}, '*');
    }}
    
    // ... (initRevealEffect và toàn bộ logic intro giữ nguyên) ...
</script>
"""

# ... (Phần HTML và Logic Intro không đổi) ...

# Hiển thị thành phần HTML (video)
# Dán lại HTML và logic intro của bạn ở đây.
# Hiện tại tôi sẽ bỏ qua để tập trung vào phần Music Player
# Tuy nhiên bạn PHẢI đảm bảo phần này đầy đủ.
components.html(
    # Phần HTML code của bạn, đã thay thế logic js_callback_video ở trên
    f"""<script>
        function sendBackToStreamlit() {{
            window.parent.postMessage({{
                streamlit: {{
                    command: 'SET_QUERY_PARAMS',
                    query_params: {{ 'video_ended': ['true'] }}
                }}
            }}, '*');
        }}
        // ... (Logic JS còn lại)
    </script>""",
    height=10, scrolling=False
)

# Tạo Lưới Reveal & Tiêu đề chính (Giữ nguyên)
# ...

# --- 5. NỘI DUNG CHÍNH (Sử dụng st_player) ---

query_params = st.query_params
video_ended_from_js = query_params.get("video_ended", None) == 'true'

if video_ended_from_js:
    
    st.markdown("<h2 style='color: white; text-align: center; margin-top: 15vh;'>NỘI DUNG CHÍNH CỦA ỨNG DỤNG</h2>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='color: #FFD700; text-align: center;'>TRÌNH PHÁT NHẠC NỀN (STREAMLIT PLAYER)</h3>", unsafe_allow_html=True)
    
    # ----------------------------------------------------
    # SỬ DỤNG STREAMLIT-PLAYER (st_player)
    # ----------------------------------------------------
    try:
        st_player(
            base64_data_url, # Đường dẫn/Base64 của file MP3
            playing=True,       # Cố gắng Autoplay
            loop=True,          # Phát lặp lại
            volume=0.5,         # Âm lượng (0.0 đến 1.0)
            height=60,
            key="streamlit_music_player" 
        )
        st.info("✅ Player đã được nhúng thành công. Vui lòng kiểm tra trên trình duyệt di động.")
    except Exception as e:
        st.error(f"Lỗi khi tải St Player: {e}")
    
    st.warning("⚠️ Nếu nhạc không tự động phát, vui lòng nhấn nút Play trên player màu đen.")

    # Xóa Query Param để ngăn loop
    if not st.session_state.ran_once:
         updated_params = dict(query_params)
         if 'video_ended' in updated_params:
             del updated_params['video_ended']
             
         st.query_params.clear() 
         st.query_params.update(updated_params)
         st.session_state.ran_once = True
