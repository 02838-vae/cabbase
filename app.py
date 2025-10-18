import streamlit as st
import base64
import os
import random
import time
from streamlit.components.v1 import html

# ---------------- Cấu hình ----------------
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

VIDEO_INTRO = "airplane.mp4"
PC_BACKGROUND = "cabbase.jpg"
MOBILE_BACKGROUND = "mobile.jpg"
MUSIC_FILES = [
    "background.mp3",
    "background2.mp3",
    "background3.mp3",
    "background4.mp3",
    "background5.mp3"
]

# **QUAN TRỌNG:** Tự động chuyển qua trang chính sau 8 giây nếu intro chưa hoàn thành
INTRO_DURATION_SEC = 7.5

if "intro_complete" not in st.session_state:
    st.session_state["intro_complete"] = False
if "intro_start_time" not in st.session_state:
    st.session_state["intro_start_time"] = time.time()


# ---------------- CSS ẩn header Streamlit ----------------
def hide_streamlit_ui():
    """Ẩn các thành phần giao diện mặc định của Streamlit."""
    st.markdown("""
    <style>
    /* Ẩn UI chính của Streamlit */
    [data-testid="stDecoration"],
    header, footer, [data-testid="stToolbar"],
    iframe, svg, [title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
        visibility: hidden !important;
    }
    /* Đảm bảo nội dung Streamlit bị ẩn hoàn toàn khi intro đang chạy */
    .stApp > div:nth-child(1) > div:nth-child(1) {
        visibility: hidden;
    }
    /* Fix cho lỗi màn hình đen: Đặt nền trang luôn là màu đen khi ở Intro */
    .stApp {
        background-color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ---------------- CSS nền trang chính ----------------
def apply_main_css():
    """Áp dụng CSS nền trang chính."""
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("{PC_BACKGROUND}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        transition: background 1s ease-in-out;
        background-color: transparent !important; /* Đảm bảo hình nền hiển thị */
    }}
    @media only screen and (max-width: 768px) {{
        .stApp {{
            background-image: url("{MOBILE_BACKGROUND}");
        }}
    }}
    h1 {{
        font-family: 'Times New Roman', serif;
        color: #4E342E;
        text-shadow: 2px 2px 4px #FFF8DC;
    }}
    /* Tắt ẩn Streamlit UI khi ở trang chính */
    .stApp > div:nth-child(1) > div:nth-child(1) {{
        visibility: visible !important;
    }}
    </style>
    """, unsafe_allow_html=True)


# ---------------- Màn hình Intro (Tối ưu lần cuối) ----------------
def intro_screen():
    """Hiển thị video intro và tự động chuyển trang sau khi video kết thúc."""
    
    hide_streamlit_ui() 

    if not os.path.exists(VIDEO_INTRO):
        st.error("⚠️ Không tìm thấy file airplane.mp4")
        st.session_state["intro_complete"] = True
        st.rerun()
        return

    # **CƠ CHẾ THOÁT KHỎI MÀN HÌNH ĐEN (PYTHON FALLBACK)**
    # Nếu refresh và đã ở trạng thái intro quá 8.5 giây, tự động chuyển trang
    if time.time() - st.session_state["intro_start_time"] > INTRO_DURATION_SEC + 1:
        st.session_state["intro_complete"] = True
        st.rerun()
        return

    # Encode video base64
    with open(VIDEO_INTRO, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()

    # HTML content
    intro_html_content = f"""
    <style>
    /* CSS nhúng để đảm bảo video luôn được hiển thị */
    html, body {{
        margin: 0; padding: 0;
        width: 100%; height: 100%;
        overflow: hidden;
        background-color: black;
    }}
    video {{
        position: fixed;
        top: 0; left: 0;
        width: 100vw;
        height: 100vh;
        object-fit: cover;
        z-index: -1;
    }}
    #intro-text {{
        position: fixed;
        bottom: 10%;
        left: 50%;
        transform: translateX(-50%);
        font-size: clamp(1em, 5vw, 1.8em);
        color: white;
        font-family: 'Times New Roman', serif;
        text-shadow: 2px 2px 8px black;
        animation: fadeInOut 6s forwards;
        z-index: 10;
    }}
    @keyframes fadeInOut {{
        0% {{ opacity: 0; }}
        15% {{ opacity: 1; }}
        85% {{ opacity: 1; }}
        100% {{ opacity: 0; }}
    }}
    #fadeout {{
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        background: black;
        opacity: 0;
        transition: opacity 1s ease-in-out;
        z-index: 20;
    }}
    </style>

    <video id="introVideo" autoplay muted playsinline preload="auto">
        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
    </video>

    <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    <div id="fadeout"></div>

    <script>
    const v = document.getElementById('introVideo');
    const fadeout = document.getElementById('fadeout');
    
    // Kích hoạt video (cần cho mobile)
    v.play().catch(() => {{
        document.body.addEventListener('click', () => v.play(), {{once:true}});
    }});

    // **Thay vì reload, ta sẽ sử dụng postMessage để kích hoạt Python**
    const totalDuration = {INTRO_DURATION_SEC} * 1000; 

    setTimeout(() => {{
        fadeout.style.opacity = 1;
        setTimeout(() => {{
            // **Thông báo cho Streamlit qua parent window**
            window.parent.postMessage({{type: 'intro_done'}}, '*');
            
            // **Thêm một fallback nhẹ: Chuyển hướng sau khi post message**
            setTimeout(() => {{
                // Ép reload nếu Streamlit không phản hồi postMessage
                window.parent.location.reload(); 
            }}, 500); 
        }}, 1000); // 1s cho hiệu ứng fade
    }}, totalDuration - 1000); 
    </script>
    """
    
    # Hiển thị component HTML tùy chỉnh
    html(intro_html_content, height=1, width=1)
    
    # **Cơ chế nghe PostMessage từ JavaScript (không áp dụng trong Streamlit)**
    # Vì Streamlit không có API đơn giản để lắng nghe postMessage, 
    # ta vẫn phải dựa vào timeout (Python Fallback) hoặc thủ thuật Form/Button.
    
    # Ở đây, ta chỉ cần dựa vào Python Fallback Timeout và JS reload nhẹ.
    st.markdown("</div>", unsafe_allow_html=True) # Kết thúc div ẩn (nếu có)
    
    # **Thêm nút ẩn có thể click thủ công**
    # Nút này KHÔNG được ẩn bằng CSS, nó sẽ bị ẩn bởi 'visibility: hidden' chung.
    # Nhưng nếu bạn bị kẹt màn hình đen, bạn có thể cố gắng click vào khu vực này.
    
    if st.button("Bỏ qua Intro", key="skip_intro"):
        st.session_state["intro_complete"] = True
        st.rerun()


# ---------------- Trang chính ----------------
def main_page():
    """Hiển thị trang chính."""
    
    apply_main_css()
    # Reset thời gian bắt đầu khi vào trang chính
    if "intro_start_time" in st.session_state:
         del st.session_state["intro_start_time"] 

    # Nhạc nền
    available = [m for m in MUSIC_FILES if os.path.exists(m)]
    if available:
        track = random.choice(available)
        with st.sidebar:
            st.subheader("🎶 Nhạc nền")
            st.audio(track, format="audio/mp3", loop=True)
            st.caption(f"Đang phát: **{os.path.basename(track)}**")

    # Tiêu đề
    st.markdown("""
    <h1 style='text-align:center; font-size:3.2em; margin-top:50px;'>
        TỔ BẢO DƯỠNG SỐ 1
    </h1>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:70vh'></div>", unsafe_allow_html=True)


# ---------------- Logic chính ----------------
if st.session_state["intro_complete"]:
    main_page()
else:
    intro_screen()
