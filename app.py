import streamlit as st
from pathlib import Path

# -------------------------
# Cấu hình trang
# -------------------------
st.set_page_config(page_title="Trang Intro", page_icon="✈️", layout="wide")

# -------------------------
# CSS để overlay chữ trên video
# -------------------------
st.markdown(
    """
    <style>
    .video-container {
        position: relative;
        width: 100%;
        max-width: 1000px;
        margin: auto;
    }
    .video-overlay {
        position: absolute;
        top: 10%;
        width: 100%;
        text-align: center;
        font-size: 2rem;
        color: white;
        font-weight: bold;
        text-shadow: 2px 2px 4px #000;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------
# Detect mobile/desktop
# -------------------------
user_agent = st.session_state.get("user_agent", "")
if not user_agent:
    # Lấy user agent từ JS
    st.write(
        """
        <script>
        const userAgent = navigator.userAgent;
        fetch('/_stcore/user_agent', {method:'POST', body:userAgent});
        </script>
        """,
        unsafe_allow_html=True
    )
    user_agent = "desktop"  # fallback

# Lựa chọn video dựa vào user agent
is_mobile = "Mobi" in user_agent
video_file = "mobile.mp4" if is_mobile else "airplane.mp4"

# -------------------------
# Video + Overlay text
# -------------------------
video_path = Path(video_file)
audio_path = Path("plane_fly.mp3")

st.markdown(
    f"""
    <div class="video-container">
        <video autoplay muted playsinline id="introVideo" width="100%">
            <source src="{video_path}" type="video/mp4">
        </video>
        <div class="video-overlay">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    </div>
    <audio autoplay>
        <source src="{audio_path}" type="audio/mpeg">
    </audio>
    """,
    unsafe_allow_html=True
)
