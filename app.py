import streamlit as st
import os
import base64
import random
import time
import streamlit.components.v1 as components
# Không cần import html nữa vì chúng ta đã đơn giản hóa cách nhúng Base64

# ================== CẤU HÌNH ==================
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
MUSIC_FILES = ["background.mp3", "background2.mp3", "background3.mp3", "background4.mp3", "background5.mp3"]

# ================== TRẠNG THÁI ==================
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "is_mobile" not in st.session_state:
    # Mặc định là False (PC) cho lần tải đầu tiên, sẽ được cập nhật sau intro
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


# ================== MÀN HÌNH INTRO THỐNG NHẤT (Sử dụng logic chọn video đơn giản) ==================
def intro_screen_unified():
    hide_streamlit_ui()
    
    # 1. Mã hóa cả hai video thành base64
    try:
        with open(VIDEO_PC, "rb") as f:
            video_pc_b64 = base64.b64encode(f.read()).decode()
        with open(VIDEO_MOBILE, "rb") as f:
            video_mobile_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError as e:
        st.error(f"⚠️ Không tìm thấy video: {e}")
        st.session_state.intro_done = True
        st.rerun()
        return
        
    intro_html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        html, body {{ margin: 0; padding: 0; height: 100%; overflow: hidden; background-color: black; }}
        video {{ width: 100vw; height: 100vh; object-fit: cover; object-position: center; }}
        #intro-text {{
            position: fixed; bottom: 18%; left: 50%; transform: translateX(-50%);
            font-size: clamp(1em, 4vw, 2em); color: white;
            font-family: 'Playfair Display', serif;
            text-shadow: 2px 2px 6px rgba(0,0,0,0.8);
            animation: fadeInOut 6s ease-in-out forwards;
        }}
        @keyframes fadeInOut {{
            0% {{ opacity: 0; transform: translate(-50%, 20px); }}
            20% {{ opacity: 1; transform: translate(-50%, 0); }}
            80% {{ opacity: 1; transform: translate(-50%, 0); }}
            100% {{ opacity: 0; transform: translate(-50%, -10px); }}
        }}
        #fade {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: black; opacity: 0; z-index: 10;
            transition: opacity 1s ease-in-out;
        }}
    </style>
    </head>
    <body>
        <video id="introVid" autoplay muted playsinline>
            <source id="pc_source" src="data:video/mp4;base64,{video_pc_b64}" type="video/mp4" data-mobile="false">
            <source id="mobile_source" src="data:video/mp4;base64,{video_mobile_b64}" type="video/mp4" data-mobile="true">
        </video>
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="fade"></div>
        <script>
        const vid = document.getElementById("introVid");
        const fade = document.getElementById("fade");
        
        // **LOGIC CHỌN VIDEO ĐÃ ĐƯỢC ĐƠN GIẢN HÓA**
        const isMobile = /Mobi|Android|iPhone|iPad/i.test(navigator.userAgent);
        
        // Lấy source phù hợp
        const mobileSource = document.getElementById("mobile_source");
        const pcSource = document.getElementById("pc_source");

        if (isMobile) {{
            // Loại bỏ PC source để trình duyệt chỉ thấy mobile
            vid.removeChild(pcSource);
        }} else {{
            // Loại bỏ Mobile source để trình duyệt chỉ thấy PC
            vid.removeChild(mobileSource);
        }}
        
        // Tải lại video để kích hoạt nguồn mới
        vid.load(); 

        // Gửi thông tin thiết bị và hoàn thành intro lên Streamlit
        const finishIntro = (isMobileDevice) => {{
            fade.style.opacity = 1;
            setTimeout(() => {{
                // Gửi state is_mobile và tín hiệu hoàn thành intro
                window.parent.postMessage({{type: "device_state", value: isMobileDevice}}, "*"); 
                window.parent.postMessage({{type: "intro_done", is_mobile: isMobileDevice}}, "*");
            }}, 1200);
        }};

        vid.onended = () => {{ finishIntro(isMobile); }};
        vid.onerror = () => {{ finishIntro(isMobile); }};
        
        </script>
    </body>
    </html>
    """
    
    components.html(intro_html, height=800, scrolling=False, key="intro_video")

    # Dùng thời gian chờ cố định để Streamlit chuyển luồng sau video
    time.sleep(9) 
    st.session_state.intro_done = True
    # Cập nhật is_mobile bằng cách đọc lại thông báo (nếu có)
    # Tạm thời gán bằng True/False, nếu Streamlit không nhận được postMessage
    st.session_state.is_mobile = st.session_state.is_mobile if st.session_state.is_mobile is not None else False
    st.rerun()


# ================== TRANG CHÍNH ==================
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    
    # Đọc và mã hóa ảnh nền thành Base64
    try:
        with open(bg, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        st.error(f"⚠️ Không tìm thấy ảnh nền: {bg}")
        bg_b64 = "" # Fallback

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
    @keyframes fadeInBg {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    h1 {{
        text-align: center;
        margin-top: 60px;
        color: #2E1C14;
        text-shadow: 2px 2px 6px #FFF8DC;
        font-family: 'Playfair Display', serif;
    }}
    </style>
    """, unsafe_allow_html=True)

    # Nhạc nền
    available_music = [m for m in MUSIC_FILES if os.path.exists(m)]
    if available_music:
        chosen = random.choice(available_music)
        with st.sidebar:
            st.subheader("🎵 Nhạc nền")
            st.audio(chosen)
            st.caption(f"Đang phát: **{os.path.basename(chosen)}**")

    st.markdown("<h1>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)


# ================== LUỒNG CHÍNH ==================
hide_streamlit_ui()

# Luồng chính đơn giản:
if not st.session_state.intro_done:
    # Chạy màn hình intro (JS tự chọn video)
    intro_screen_unified()
else:
    # Sau khi intro xong, chạy trang chính với state is_mobile
    main_page(st.session_state.is_mobile)
