import streamlit as st
import base64
import os
import random
import time

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
    [data-testid="stDecoration"],
    header, footer, [data-testid="stToolbar"],
    iframe, svg, [title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
        visibility: hidden !important;
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
    </style>
    """, unsafe_allow_html=True)


# ---------------- Màn hình Intro (Đã sửa lỗi) ----------------
def intro_screen():
    """Hiển thị video intro và tự động chuyển trang sau khi video kết thúc."""
    hide_streamlit_ui()

    if not os.path.exists(VIDEO_INTRO):
        st.error("⚠️ Không tìm thấy file airplane.mp4")
        st.session_state["intro_complete"] = True
        st.rerun()
        return

    # **Sử dụng Form ẩn để kích hoạt State Change:**
    # Khi JavaScript nhấn nút "Done", Streamlit sẽ xử lý logic Python.
    with st.form("intro_form", clear_on_submit=False):
        # Nút submit ẩn. Cần có một nút để JS click.
        st.form_submit_button("Done", key="intro_done_button", help="Nút ẩn kích hoạt chuyển trang.")
        
        # Encode video base64
        with open(VIDEO_INTRO, "rb") as f:
            video_b64 = base64.b64encode(f.read()).decode()

        # Tạo HTML trực tiếp
        intro_html = f"""
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
        /* Ẩn hoàn toàn form Streamlit để người dùng không thấy */
        [data-testid="stForm"] {{
            display: none !important;
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
        
        // Tìm nút ẩn trong form
        const form = window.parent.document.querySelector('[data-testid="stForm"]');
        const doneButton = form ? form.querySelector('button') : null;

        // Nếu autoplay bị chặn → phát khi user chạm (cần thiết cho mobile)
        v.play().catch(() => {{
            document.body.addEventListener('click', () => v.play(), {{once:true}});
        }});

        // Kích hoạt fadeout và sau đó nhấn nút Streamlit để chuyển trang
        // 6500ms là thời gian chạy video + text animation
        setTimeout(() => {{
            fadeout.style.opacity = 1;
            setTimeout(() => {{
                // Kích hoạt Streamlit bằng cách nhấn nút ẩn
                if (doneButton) {{
                    doneButton.click();
                }} else {{
                    console.error("Nút Streamlit ẩn không tìm thấy.");
                }}
            }}, 1000); // 1s cho hiệu ứng fade
        }}, 6500); 
        </script>
        """

        # Hiển thị video trực tiếp (không iframe)
        st.markdown(intro_html, unsafe_allow_html=True)

    # Logic chuyển trạng thái dựa trên việc nút ẩn được click
    if st.session_state.get("intro_done_button"):
        st.session_state["intro_complete"] = True
        st.session_state["intro_done_button"] = False # Đặt lại trạng thái nút
        st.rerun() # Kích hoạt chuyển trang


# ---------------- Trang chính ----------------
def main_page():
    """Hiển thị trang chính."""
    hide_streamlit_ui()
    apply_main_css()

    # Nhạc nền
    available = [m for m in MUSIC_FILES if os.path.exists(m)]
    if available:
        track = random.choice(available)
        with st.sidebar:
            st.subheader("🎶 Nhạc nền")
            # Lưu ý: Người dùng vẫn cần click vào control audio để bắt đầu phát
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
