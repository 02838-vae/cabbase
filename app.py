import streamlit as st
import base64
import os
import time

st.set_page_config(page_title="Airplane Intro", layout="wide", initial_sidebar_state="collapsed")

# ===== HÀM PHỤ TRỢ =====
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# ===== TRẠNG THÁI =====
if "show_main" not in st.session_state:
    st.session_state.show_main = False

video_file = "airplane.mp4"

# Ẩn sidebar, header, footer
st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stToolbar"], header, footer {display: none !important;}
html, body, [class*="stAppViewContainer"], [class*="stApp"], [class*="stMainBlockContainer"] {
    margin: 0; padding: 0; height: 100%; overflow: hidden; background: black;
}
</style>
""", unsafe_allow_html=True)

# ===== MÀN HÌNH INTRO =====
if not st.session_state.show_main:
    if os.path.exists(video_file):
        video_data = get_base64(video_file)

        st.markdown(f"""
        <style>
        .video-container {{
            position: fixed;
            inset: 0;
            width: 100vw;
            height: 100vh;
            background: black;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            z-index: 9998;
        }}
        .video-bg {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .intro-text {{
            position: absolute;
            bottom: 12vh;
            width: 100%;
            text-align: center;
            font-size: 42px;
            font-weight: bold;
            color: #fff;
            text-shadow: 0 0 15px rgba(255,255,255,0.8);
            opacity: 0;
            animation:
                appear 3s ease-in forwards,
                floatFade 3s ease-in 5s forwards;
        }}
        @keyframes appear {{
            0% {{opacity:0;transform:translateY(40px);filter:blur(6px);}}
            100% {{opacity:1;transform:translateY(0);filter:blur(0);}}
        }}
        @keyframes floatFade {{
            0% {{opacity:1;transform:translateY(0);}}
            100% {{opacity:0;transform:translateY(-30px);filter:blur(10px);}}
        }}
        </style>

        <div class="video-container">
            <video class="video-bg" autoplay muted playsinline>
                <source src="data:video/mp4;base64,{video_data}" type="video/mp4">
            </video>
            <div class="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        </div>
        """, unsafe_allow_html=True)

        time.sleep(8.5)
        st.session_state.show_main = True
        st.rerun()
    else:
        st.error("❌ Không tìm thấy file airplane.mp4")
        st.stop()

# ===== TRANG CHÍNH =====
img_base64 = get_base64("cabbase.jpg")

st.markdown(f"""
    <style>
    /* Xóa mọi margin, padding của Streamlit */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"] {{
        margin: 0 !important;
        padding: 0 !important;
        height: 100vh !important;
        width: 100vw !important;
        overflow: hidden !important;
        background: none !important;
    }}

    /* Ảnh nền phủ toàn màn hình */
    .background {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: url("data:image/jpeg;base64,{img_base64}") center center / cover no-repeat;
        filter: brightness(0.9) sepia(0.15) saturate(1.05) blur(2px);
        z-index: -2;
    }}

    /* Lớp phủ mờ nhẹ kiểu vintage */
    .overlay {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.25);
        z-index: -1;
    }}

    /* Hộp nội dung chính */
    .main-box {{
        position: relative;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
        color: #fff;
        font-family: "Georgia", serif;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(6px);
        padding: 2.5rem 3rem;
        border-radius: 20px;
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
        max-width: 850px;
    }}
    </style>

    <div class="background"></div>
    <div class="overlay"></div>
    <div class="main-box">
        <h1 style="font-size: 2.5rem; margin-bottom: 1rem;">TỔ BẢO DƯỠNG SỐ 1 ✈️</h1>
        <p style="font-size: 1.2rem;">Chào mừng bạn đến với trang chính — nơi bắt đầu hành trình khám phá bầu trời 🌍</p>
    </div>
""", unsafe_allow_html=True)

