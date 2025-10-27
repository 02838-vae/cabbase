import streamlit as st
import base64
import os
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
    """Đọc file và trả về byte data và Base64 encoded string."""
    try:
        abs_path = os.path.join(os.getcwd(), file_path)
        with open(abs_path, "rb") as f:
            data = f.read()
        return data, base64.b64encode(data).decode("utf-8")
    except FileNotFoundError as e:
        st.error(f"LỖI CỐT LÕI: Không tìm thấy file media. Vui lòng kiểm tra đường dẫn: {e.filename}")
        st.stop()
    except Exception as e:
        st.error(f"Lỗi đọc file {file_path}: {e}")
        st.stop()

# --- 2. BIẾN TOÀN CỤC VÀ TẢI DỮ LIỆU ---

try:
    # Tải video/ảnh
    video_pc_data, video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_data, video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_intro_data, audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    bg_pc_data, bg_pc_base64 = get_base64_encoded_file("cabbase.jpg") 
    bg_mobile_data, bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")

    # Tải file nhạc nền background1.mp3
    audio_bg_data, _ = get_base64_encoded_file("background1.mp3")
    base64_data_url = f"data:audio/mp3;base64,{base64.b64encode(audio_bg_data).decode('utf-8')}"

except Exception:
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

# Khối CSS (Sử dụng các biến Base64 cho background)
hide_streamlit_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sacramento&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');

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

/* Hiệu ứng Reveal */
.reveal-grid {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    display: grid;
    grid-template-columns: repeat(20, 1fr); 
    grid-template-rows: repeat(12, 1fr);
    z-index: 500; 
    pointer-events: none; 
}}

.grid-cell {{
    background-color: white; 
    opacity: 1;
    transition: opacity 0.5s ease-out;
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
    .reveal-grid {{
        grid-template-columns: repeat(10, 1fr);
        grid-template-rows: repeat(20, 1fr);
    }}
}}

/* Keyframes và CSS cho Tiêu đề Chính */
@keyframes scrollText {{ 0% {{ transform: translate(100vw, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
@keyframes colorShift {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}

#main-title-container {{ position: fixed; top: 5vh; left: 0; width: 100%; height: 10vh; overflow: hidden; z-index: 20; pointer-events: none; opacity: 0; transition: opacity 2s;}}

#main-title-container h1 {{
    font-family: 'Playfair Display', serif; font-size: 3.5vw; margin: 0; font-weight: 900; letter-spacing: 5px; white-space: nowrap; display: inline-block;
    background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3); background-size: 400% 400%; 
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; color: transparent; 
    animation: colorShift 10s ease infinite, scrollText 15s linear infinite; 
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5); 
}}

@media (max-width: 768px) {{
    #main-title-container {{ height: 8vh; width: 100%; left: 0; }}
    #main-title-container h1 {{ font-size: 6.5vw; animation-duration: 8s; }}
}}

/* CSS cho Player - Đảm bảo nó nổi trên nội dung */
[data-testid="stComponentV1"] {{
    position: fixed !important; 
    bottom: 20px !important; 
    left: 20px !important;
    z-index: 100 !important;
}}

</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- 4. VIDEO INTRO & LOGIC RERUNING ĐÃ SỬA LỖI REVEAL ---

# JavaScript Callback cho Video Intro 
js_callback_video = f"""
<script>
    function sendBackToStreamlit() {{
        // 1. Kích hoạt hiệu ứng Reveal nhanh (immediate=true)
        initRevealEffect(true); 
        
        // 2. Gửi lệnh SET_QUERY_PARAMS để kích hoạt rerun Streamlit
        window.parent.postMessage({{
            streamlit: {{
                command: 'SET_QUERY_PARAMS',
                query_params: {{ 'video_ended': ['true'] }}
            }}
        }}, '*');
    }}
    
    function initRevealEffect(immediate = false) {{
        const revealGrid = window.parent.document.querySelector('.reveal-grid');
        const mainTitle = window.parent.document.getElementById('main-title-container');
        
        if (mainTitle) {{ mainTitle.style.opacity = 1; }}

        if (!revealGrid) {{ return; }}

        if (immediate) {{
            // Nếu gọi ngay lập tức, xóa/ẩn nhanh
            revealGrid.style.opacity = 0;
            setTimeout(() => {{ revealGrid.remove(); }}, 1000);
            return;
        }}
        
        // Logic hiệu ứng Reveal từng ô (chạy khi trang chính hiện lên)
        const cells = revealGrid.querySelectorAll('.grid-cell');
        const shuffledCells = Array.from(cells).sort(() => Math.random() - 0.5);

        shuffledCells.forEach((cell, index) => {{
            setTimeout(() => {{ cell.style.opacity = 0; }}, index * 10);
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
        
        var urlParams = new URLSearchParams(window.location.search);
        const videoEnded = urlParams.get('video_ended') === 'true';
        
        // Đặt các lớp CSS cho nội dung chính ngay lập tức cho lần chạy thứ 2
        window.parent.document.querySelector('.stApp').classList.add('video-finished', 'main-content-revealed');

        if (!videoEnded) {{
            // Lần chạy đầu: Chạy video intro và gửi tín hiệu
            
            // Xóa lớp reveal cho lần đầu chạy (quan trọng)
            window.parent.document.querySelector('.stApp').classList.remove('video-finished', 'main-content-revealed');

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
                audio.play().catch(e => {{}});
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
            // Lần chạy lại (Sau khi RERUN): Ẩn video/audio và gọi hiệu ứng Reveal chậm
            video.style.opacity = 0;
            video.style.display = 'none';
            initRevealEffect(); 
        }}
    }});
</script>
"""

# Mã HTML/CSS cho Video Intro
html_content_modified = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        html, body {{ margin: 0; padding: 0; overflow: hidden; height: 100vh; width: 100vw; }}
        #intro-video {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: -100; transition: opacity 1s; }}
        #intro-text-container {{ position: fixed; top: 5vh; width: 100%; text-align: center; color: #FFD700; font-size: 3vw; font-family: 'Sacramento', cursive; font-weight: 400; text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.8); z-index: 100; pointer-events: none; display: flex; justify-content: center; opacity: 1; }}
        .intro-char {{ display: inline-block; opacity: 0; transform: translateY(-50px); animation-fill-mode: forwards; animation-duration: 0.8s; animation-timing-function: ease-out; }}
        @keyframes charDropIn {{ from {{ opacity: 0; transform: translateY(-50px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .intro-char.char-shown {{ animation-name: charDropIn; }}
        @media (max-width: 768px) {{ #intro-text-container {{ font-size: 6vw; }} }}
    </style>
</head>
<body>
    <div id="intro-text-container">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    <video id="intro-video" muted playsinline></video>
    <audio id="background-audio"></audio>
    {js_callback_video}
</body>
</html>
"""

# Xử lý nội dung của tiêu đề video intro
intro_title = "KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI"
intro_chars_html = ''.join([
    f'<span class="intro-char">{char}</span>' if char != ' ' else '<span class="intro-char">&nbsp;</span>' 
    for char in intro_title
])
html_content_modified = html_content_modified.replace(
    "<div id=\"intro-text-container\">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>",
    f"<div id=\"intro-text-container\">{intro_chars_html}</div>"
)

# Hiển thị thành phần HTML (video)
components.html(html_content_modified, height=10, scrolling=False)

# Tạo Lưới Reveal
grid_cells_html = ""
for i in range(240): grid_cells_html += f'<div class="grid-cell"></div>'
reveal_grid_html = f"""<div class="reveal-grid">{grid_cells_html}</div>"""
st.markdown(reveal_grid_html, unsafe_allow_html=True)

# Nhúng tiêu đề chính
main_title_text = "TỔ BẢO DƯỠNG SỐ 1" 
st.markdown(f"""
<div id="main-title-container">
    <h1>{main_title_text}</h1>
</div>
""", unsafe_allow_html=True) 


# --- 5. NỘI DUNG CHÍNH (Sử dụng st_player) ---

query_params = st.query_params
video_ended_from_js = query_params.get("video_ended", None) == 'true'

if video_ended_from_js:
    
    st.markdown("<h2 style='color: white; text-align: center; margin-top: 15vh;'>NỘI DUNG CHÍNH CỦA ỨNG DỤNG</h2>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='color: #FFD700; text-align: center;'>TRÌNH PHÁT NHẠC NỀN (STREAMLIT PLAYER)</h3>", unsafe_allow_html=True)
    
    # SỬ DỤNG STREAMLIT-PLAYER (st_player)
    try:
        st_player(
            base64_data_url, 
            playing=True,       # Cố gắng Autoplay
            loop=True,          # Phát lặp lại
            volume=0.5,         # Âm lượng
            height=60,
            controls=True,      # Cho phép người dùng điều khiển
            key="streamlit_music_player" 
        )
        st.info("✅ Player đã được nhúng thành công.")
    except Exception as e:
        st.error(f"Lỗi khi tải St Player: {e}")
    
    st.warning("⚠️ Nếu nhạc không tự động phát, vui lòng nhấn nút Play trên player. Đây là giới hạn bảo mật của trình duyệt di động.")

    # Xóa Query Param để ngăn loop
    if not st.session_state.ran_once:
         updated_params = dict(query_params)
         if 'video_ended' in updated_params:
             del updated_params['video_ended']
             
         st.query_params.clear() 
         st.query_params.update(updated_params)
         st.session_state.ran_once = True
