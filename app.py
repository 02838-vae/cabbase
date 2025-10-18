import streamlit as st
import base64
import os
import random
# Import Streamlit Component API
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

if "intro_complete" not in st.session_state:
    st.session_state["intro_complete"] = False


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


# ---------------- Màn hình Intro (FIX CUỐI CÙNG) ----------------
def intro_screen():
    """Hiển thị video intro và tự động chuyển trang sau khi video kết thúc."""
    
    # Ẩn UI Streamlit chung
    hide_streamlit_ui() 

    if not os.path.exists(VIDEO_INTRO):
        st.error("⚠️ Không tìm thấy file airplane.mp4")
        st.session_state["intro_complete"] = True
        st.rerun()
        return

    # Encode video base64
    with open(VIDEO_INTRO, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()

    # Tạo HTML trực tiếp. Sẽ được nhúng dưới dạng component.
    intro_html_content = f"""
    <style>
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
    
    // Nếu autoplay bị chặn → phát khi user chạm
    v.play().catch(() => {{
        document.body.addEventListener('click', () => v.play(), {{once:true}});
    }});

    // **SỬ DỤNG window.parent.location.reload()**
    // Đây là cách ép buộc Streamlit reload và chạy lại logic Python.
    // Nếu chuyển trạng thái bằng session state không được, ép reload là cách cuối cùng.
    const totalDuration = 7500; // 7.5 giây để đảm bảo video chạy hết

    setTimeout(() => {{
        fadeout.style.opacity = 1;
        setTimeout(() => {{
            // **Quan trọng:** Ép Streamlit reload để chuyển sang trạng thái mới.
            window.parent.location.reload(); 
        }}, 1000); // 1s cho hiệu ứng fade
    }}, totalDuration - 1000); 
    </script>
    """
    # Hiển thị component HTML tùy chỉnh
    html(intro_html_content, height=1, width=1)
    
    # **Logic chuyển trạng thái (Python)**
    # Vì ta dùng window.parent.location.reload() bên JavaScript,
    # ta cần một cơ chế để Python biết trạng thái đã hoàn thành SAU KHI reload.
    # Cơ chế ổn định nhất là sử dụng một nút ẩn bị ẩn khỏi tầm nhìn.
    
    # Tạo một nút ẩn hoàn toàn bằng CSS
    st.markdown("""
    <style>
    #hidden_button_container {
        position: fixed;
        top: -100px;
        left: -100px;
        width: 1px;
        height: 1px;
        overflow: hidden;
    }
    </style>
    <div id="hidden_button_container">
    """, unsafe_allow_html=True)
    
    # Nút này chỉ dùng để kích hoạt st.rerun() sau khi người dùng tương tác
    # Tuy nhiên, vì ta dùng reload() trong JS, ta chỉ cần set session state ở đây
    
    # **Giải pháp Ổn định:** Sau khi JS reload trang, Streamlit sẽ chạy lại
    # và *lần chạy tiếp theo* người dùng sẽ thấy trang chính.
    # Vì logic reload trong JS đã đảm bảo trang Python chạy lại.
    # Ta phải sử dụng một cơ chế chờ để Streamlit không kết thúc quá sớm.
    
    # **Dùng một biến giả để đảm bảo Streamlit không render lại phần này**
    if "reloaded_intro" not in st.session_state:
        st.session_state["reloaded_intro"] = True
    else:
        # Giả sử trang đã reload và video đã chạy.
        # **CƠ CHẾ BẮT LỖI TỐI ƯU:**
        # Nếu đã ở intro quá 8 giây (sau khi reload), chuyển qua trang chính để thoát kẹt
        if "start_time" not in st.session_state:
             st.session_state["start_time"] = time.time()
        
        if time.time() - st.session_state["start_time"] > 8:
            st.session_state["intro_complete"] = True
            del st.session_state["start_time"]
            st.rerun()


# ---------------- Trang chính ----------------
def main_page():
    """Hiển thị trang chính."""
    
    apply_main_css()

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
import time # Cần import time nếu chưa có

if st.session_state["intro_complete"]:
    main_page()
else:
    intro_screen()
