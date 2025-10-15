import streamlit as st

# ============ CẤU HÌNH CƠ BẢN ============
st.set_page_config(page_title="Airplane Intro", layout="wide", initial_sidebar_state="collapsed")

# Ẩn sidebar + header + footer
st.markdown("""
    <style>
    [data-testid="stSidebar"], [data-testid="stToolbar"], header, footer {display: none !important;}
    html, body, [class*="stAppViewContainer"], [class*="stMainBlockContainer"], [class*="stApp"] {
        margin: 0;
        padding: 0;
        height: 100%;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# Trạng thái video intro
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

# ============ PHẦN INTRO ============
if not st.session_state.intro_done:
    # Video trong thư mục static
    video_url = "static/airplane.mp4"

    st.markdown(f"""
    <style>
    video {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        object-fit: cover;
        z-index: -1;
    }}
    .overlay-text {{
        position: fixed;
        bottom: 10%;
        width: 100%;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        color: white;
        text-shadow: 2px 2px 10px black;
        opacity: 0;
        animation: fadeInOut 5s ease-in-out forwards;
        animation-delay: 1s;
    }}
    @keyframes fadeInOut {{
        0% {{opacity: 0;}}
        20% {{opacity: 1;}}
        80% {{opacity: 1;}}
        100% {{opacity: 0;}}
    }}
    </style>

    <video id="introVideo" autoplay muted playsinline>
        <source src="{video_url}" type="video/mp4">
        Trình duyệt của bạn không hỗ trợ thẻ video.
    </video>

    <div class="overlay-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>

    <script>
    // Khi video kết thúc -> reload trang để vào trang chính
    const video = document.getElementById("introVideo");
    video.onended = () => {{
        fetch("/_stcore/stream", {{method:"POST"}}).then(() => window.location.reload());
    }};
    </script>
    """, unsafe_allow_html=True)

    st.stop()

# ============ TRANG CHÍNH ============
st.session_state.intro_done = True

st.markdown("""
    <style>
    .stApp {
        background: url("static/cabbase.jpg") no-repeat center center fixed;
        background-size: cover;
    }
    .main-box {
        background-color: rgba(255, 255, 255, 0.85);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 0 20px rgba(0,0,0,0.3);
        max-width: 900px;
        margin: 5rem auto;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-box'>", unsafe_allow_html=True)
st.title("🌍 Trang Chính")
st.write("Video intro đã kết thúc. Chào mừng bạn đến với website của bạn ✈️")
st.markdown("</div>", unsafe_allow_html=True)
