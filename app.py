import streamlit as st
import os
import base64
import random
import time
import streamlit.components.v1 as components
from streamlit_js_eval import streamlit_js_eval 
# Cần cài đặt: pip install streamlit-js-eval

# ================== CẤU HÌNH & TRẠNG THÁI ==================
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
MUSIC_FILES = ["background.mp3", "background2.mp3", "background3.mp3", "background4.mp3", "background5.mp3"]

if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = None

# --- XÁC ĐỊNH THIẾT BỊ NGAY LẬP TỨC ---
if st.session_state.is_mobile is None:
    js_result = streamlit_js_eval(js_expressions='(/Mobi|Android|iPhone|iPad/i.test(navigator.userAgent))', 
                                 key=f'mobile_detector_{time.time()}')
    
    if js_result is not None:
        st.session_state.is_mobile = js_result
        st.rerun()
    else:
        # Giả định PC trong khi chờ
        st.session_state.is_mobile = False

# ================== ẨN HEADER STREAMLIT ==================
def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"],
    header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ================== MÀN HÌNH INTRO ĐÃ SỬA LỖI CHIA ĐÔI ==================
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    
    video_path = VIDEO_MOBILE if is_mobile else VIDEO_PC
    
    if not os.path.exists(video_path):
        st.error(f"⚠️ Không tìm thấy video: {video_path}")
        st.session_state.intro_done = True
        st.rerun()
        return

    # Mã hóa video thành base64
    with open(video_path, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()

    # THAY ĐỔI QUAN TRỌNG: Sử dụng Vh và Vw triệt để, loại bỏ margin/padding
    intro_html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        html, body {{ 
            margin: 0 !important; 
            padding: 0 !important; 
            height: 100vh; 
            width: 100vw; 
            overflow: hidden; 
            background-color: black; 
        }}
        /* Đảm bảo iframe con chiếm toàn bộ không gian */
        iframe, #intro-container {{ 
            position: absolute; 
            top: 0; 
            left: 0; 
            width: 100vw; 
            height: 100vh; 
        }}
        video {{ 
            width: 100vw; 
            height: 100vh; 
            object-fit: cover; 
            object-position: center; 
        }}
        #intro-text {{
            position: fixed; bottom: 18%; left: 50%; transform: translateX(-50%);
            font-size: clamp(1em, 4vw, 2em); color: white; z-index: 10;
            font-family: 'Playfair Display', serif; text-shadow: 2px 2px 6px rgba(0,0,0,0.8);
            animation: fadeInOut 6s ease-in-out forwards;
        }}
        @keyframes fadeInOut {{
            0% {{ opacity: 0; transform: translate(-50%, 20px); }} 20% {{ opacity: 1; transform: translate(-50%, 0); }}
            80% {{ opacity: 1; transform: translate(-50%, 0); }} 100% {{ opacity: 0; transform: translate(-50%, -10px); }}
        }}
        #fade {{
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: black; opacity: 0; z-index: 10;
            transition: opacity 1s ease-in-out;
        }}
    </style>
    </head>
    <body>
        <video id="introVid" autoplay muted playsinline>
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="fade"></div>
        <script>
            const vid = document.getElementById("introVid");
            const fade = document.getElementById("fade");

            // Sau khi video kết thúc, gửi tín hiệu hoàn thành
            vid.onended = () => {{
                fade.style.opacity = 1;
                setTimeout(() => {{
                    // Gửi tín hiệu hoàn thành intro
                    window.parent.postMessage({{"type": "intro_done"}}, "*");
                }}, 1200);
            }};
            
            // Xử lý lỗi phát hoặc không autoplay được
            vid.onerror = vid.onpause = () => {{
                 // Nếu video dừng do lỗi hoặc người dùng can thiệp, ta vẫn chuyển trang sau 9s
                 setTimeout(() => {{
                     window.parent.postMessage({{"type": "intro_done"}}, "*");
                 }}, 9000); // 9 giây giả định
            }};

            // Đảm bảo video luôn bắt đầu phát
            vid.play().catch(error => {{
                console.log("Autoplay blocked, switching after delay.");
                setTimeout(() => {{
                    window.parent.postMessage({{"type": "intro_done"}}, "*");
                }}, 9000);
            }});
        </script>
    </body>
    </html>
    """
    
    # SỬA LỖI: components.html(height=None) hoặc height=1000 để bao trùm
    # height=800 vẫn có thể bị chia, ta dùng giá trị lớn hơn hoặc None.
    components.html(intro_html, height=1000, scrolling=False) 

    # Dùng biến session state để kiểm soát thời gian chạy.
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()
    
    # Kiểm tra thời gian đã trôi qua
    if time.time() - st.session_state.start_time < 9.5: # 9.5 giây cho an toàn
        time.sleep(1) # Giảm sleep time để tránh lỗi timeout
        st.rerun()
    else:
        # Hoàn thành sau khi đã rerun đủ lần
        st.session_state.intro_done = True
        del st.session_state.start_time
        st.rerun()


# ================== TRANG CHÍNH ==================
# ... (Hàm main_page giữ nguyên) ...
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    
    try:
        with open(bg, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        st.error(f"⚠️ Không tìm thấy ảnh nền: {bg}")
        bg_b64 = ""

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&display=swap');
    .stApp {{
        background-image: url("data:image/jpeg;base64,{bg_b64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        animation: fadeInBg 1s ease-in-out forwards;
    }}
    @keyframes fadeInBg {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    h1 {{
        text-align: center; margin-top: 60px; color: #2E1C14;
        text-shadow: 2px 2px 6px #FFF8DC; font-family: 'Playfair Display', serif;
    }}
    </style>
    """, unsafe_allow_html=True)

    available_music = [m for m in MUSIC_FILES if os.path.exists(m)]
    if available_music:
        chosen = random.choice(available_music)
        with st.sidebar:
            st.subheader("🎵 Nhạc nền")
            st.audio(chosen, start_time=0) 
            st.caption(f"Đang phát: **{os.path.basename(chosen)}**")

    st.markdown("<h1>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)


# ================== LUỒNG CHÍNH ==================
hide_streamlit_ui()

if st.session_state.is_mobile is None:
    st.info("Đang xác định thiết bị và tải...")
elif not st.session_state.intro_done:
    # is_mobile đã có giá trị (True/False)
    intro_screen(st.session_state.is_mobile)
else:
    # Intro đã xong
    main_page(st.session_state.is_mobile)
