import streamlit as st
import base64
import os
import streamlit.components.v1 as components

# --- 1. KHỞI TẠO STATE AN TOÀN ---
if 'video_ended' not in st.session_state:
    st.session_state.video_ended = False
if 'ran_once' not in st.session_state:
    st.session_state.ran_once = False
if 'rerun_done' not in st.session_state:
    st.session_state.rerun_done = False 

# --- CẤC HÀM TIỆN ÍCH DÙNG BASE64 ---

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
    # Tải video/ảnh
    video_pc_data, video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_data, video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_intro_data, audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    
    bg_pc_data, bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_data, bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")

    # Tải file nhạc nền background1.mp3 dưới dạng bytes để dùng st.audio
    audio_bg_data, _ = get_base64_encoded_file("background1.mp3")

except:
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
/* ... (GIỮ NGUYÊN TOÀN BỘ CSS, bao gồm các biến Base64) ... */
#MainMenu, footer, header {{visibility: hidden;}}

.main {{ padding: 0; margin: 0; }}
div.block-container {{ padding: 0; margin: 0; max-width: 100% !important; }}

/* Iframe chứa video intro */
iframe:first-of-type {{
    transition: opacity 1s ease-out, visibility 1s ease-out;
    opacity: 1;
    visibility: visible;
    width: 100vw !important;
    height: 100vh !important;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1000;
}}

.video-finished iframe:first-of-type {{
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
    height: 1px !important; 
}}

.stApp {{
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
}}

.main-content-revealed {{
    background-image: var(--main-bg-url-pc);
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    filter: sepia(60%) grayscale(20%) brightness(85%) contrast(110%); 
    transition: filter 2s ease-out; 
    min-height: 100vh;
}}

@media (max-width: 768px) {{
    .main-content-revealed {{
        background-image: var(--main-bg-url-mobile);
    }}
}}

</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- 4. VIDEO INTRO & LOGIC RERUNING ĐÃ SỬA ---

# JavaScript Callback cho Video Intro (Điều chỉnh)
js_callback_video = f"""
<script>
    function sendBackToStreamlit() {{
        // 1. Gửi tín hiệu video kết thúc và kích hoạt rerun Streamlit: 
        // Thay vì window.location, ta dùng Streamlit set_query_params
        window.parent.document.querySelector('.stApp').classList.add('video-finished', 'main-content-revealed');
        
        // Gửi lệnh set_query_params qua postMessage để Streamlit xử lý
        window.parent.postMessage({{
            streamlit: {{
                command: 'SET_QUERY_PARAMS',
                query_params: {{ 'video_ended': ['true'] }}
            }}
        }}, '*');
    }}
    
    function initRevealEffect() {{
        const revealGrid = window.parent.document.querySelector('.reveal-grid');
        const mainTitle = window.parent.document.getElementById('main-title-container');
        if (mainTitle) {{ mainTitle.style.opacity = 1; }}

        if (!revealGrid) {{ return; }}

        const cells = revealGrid.querySelectorAll('.grid-cell');
        const shuffledCells = Array.from(cells).sort(() => Math.random() - 0.5);

        shuffledCells.forEach((cell, index) => {{
            setTimeout(() => {{
                cell.style.opacity = 0; 
            }}, index * 10);
        }});
        
        setTimeout(() => {{ revealGrid.remove(); }}, shuffledCells.length * 10 + 1000);
    }}

    document.addEventListener("DOMContentLoaded", function() {{
        const video = document.getElementById('intro-video');
        const audio = document.getElementById('background-audio');
        const introTextContainer = document.getElementById('intro-text-container'); 
        const isMobile = window.innerWidth <= 768;

        if (isMobile) {{ video.src = 'data:video/mp4;base64,{video_mobile_base64}'; }} 
        else {{ video.src = 'data:video/mp4;base64,{video_pc_base64}'; }}
        
        audio.src = 'data:audio/mp3;base64,{audio_base64}';
        
        // Kiểm tra xem video_ended đã có trong query params chưa
        var urlParams = new URLSearchParams(window.location.search);
        const videoEnded = urlParams.get('video_ended') === 'true';

        if (!videoEnded) {{
             // Logic chạy video intro
            const playMedia = () => {{
                video.load();
                video.play().catch(e => console.log("Video playback failed:", e));
                
                const chars = introTextContainer.querySelectorAll('.intro-char');
                chars.forEach((char, index) => {{
                    char.style.animationDelay = `${{index * 0.1}}s`; 
                    char.classList.add('char-shown'); 
                }});

                audio.volume = 0.5;
                audio.loop = true; 
                audio.play().catch(e => {{
                    document.body.addEventListener('click', () => {{
                        audio.play().catch(err => console.error("Audio playback error on click:", err));
                    }}, {{ once: true }});
                }});
            }};
            
            playMedia();
            
            video.onended = () => {{
                video.style.opacity = 0;
                audio.pause();
                audio.currentTime = 0;
                introTextContainer.style.opacity = 0; 
                sendBackToStreamlit(); 
            }};
            
            // Lắng nghe click lần đầu để bật video/audio
            document.body.addEventListener('click', () => {{
                  video.play().catch(e => {{}});
                  audio.play().catch(e => {{}});
            }}, {{ once: true }});
            
        }} else {{
            // Nếu đã kết thúc (lần chạy thứ 2), ẩn video ngay lập tức và gọi hiệu ứng reveal
            video.style.opacity = 0;
            video.style.display = 'none';
            window.parent.document.querySelector('.stApp').classList.add('video-finished', 'main-content-revealed');
            initRevealEffect();
        }}
        
    }});
</script>
"""

# HTML và Components (Giữ nguyên)
html_content_modified = f"""
<!DOCTYPE html>
<html>
<body>
    <div id="intro-text-container">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    <video id="intro-video" muted playsinline></video>
    <audio id="background-audio"></audio>
    {js_callback_video}
</body>
</html>
"""

intro_title = "KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI"
intro_chars_html = ''.join([
    f'<span class="intro-char">{char}</span>' if char != ' ' else '<span class="intro-char">&nbsp;</span>' 
    for char in intro_title
])
html_content_modified = html_content_modified.replace(
    "<div id=\"intro-text-container\">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>",
    f"<div id=\"intro-text-container\">{intro_chars_html}</div>"
)

components.html(html_content_modified, height=10, scrolling=False)

grid_cells_html = ""
for i in range(240): grid_cells_html += f'<div class="grid-cell"></div>'
reveal_grid_html = f"""<div class="reveal-grid">{grid_cells_html}</div>"""
st.markdown(reveal_grid_html, unsafe_allow_html=True)

main_title_text = "TỔ BẢO DƯỠNG SỐ 1" 
st.markdown(f"""
<div id="main-title-container">
    <h1>{main_title_text}</h1>
</div>
""", unsafe_allow_html=True) 


# --- 5. NỘI DUNG CHÍNH (Sử dụng st.audio) ---

# Thay thế st.experimental_get_query_params bằng st.query_params
query_params = st.query_params
video_ended_from_js = query_params.get("video_ended", None) == 'true'

if video_ended_from_js:
    
    st.markdown("<h2 style='color: white; text-align: center; margin-top: 15vh;'>NỘI DUNG CHÍNH CỦA ỨNG DỤNG</h2>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='color: #FFD700; text-align: center;'>TRÌNH PHÁT NHẠC NỀN (st.audio)</h3>", unsafe_allow_html=True)
    
    st.audio(
        audio_bg_data,
        format="audio/mp3",
        autoplay=True, # Vẫn cố gắng autoplay
        loop=True
    )
    
    st.warning("⚠️ Nếu nhạc không tự động phát, điều đó xác nhận TRÌNH DUYỆT ĐANG CHẶN AUTOPLAY. Vui lòng nhấn nút Play trên player màu đen.")

    # Xóa Query Param để ngăn loop
    if not st.session_state.ran_once:
         # Chuyển đổi st.query_params sang dictionary để xóa khóa
         updated_params = dict(query_params)
         if 'video_ended' in updated_params:
             del updated_params['video_ended']
             
         # Sử dụng st.query_params để set lại params
         st.query_params.clear() 
         st.query_params.update(updated_params)
         
         st.session_state.ran_once = True
