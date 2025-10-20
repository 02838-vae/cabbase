import streamlit as st
import base64
import time

st.set_page_config(page_title="Cabbase", page_icon="✈️", layout="wide")

# CSS để ẩn toàn bộ phần UI Streamlit
st.markdown("""
<style>
#MainMenu, header, footer {visibility: hidden;}
.block-container {padding: 0 !important; margin: 0 !important;}
</style>
""", unsafe_allow_html=True)

# Phát hiện thiết bị
user_agent = st.query_params.get("user_agent", [""])[0] or st.session_state.get("user_agent", "")
if not user_agent:
    import re
    user_agent = st.runtime.scriptrunner.get_script_run_ctx().request.headers.get("User-Agent", "")
st.session_state["user_agent"] = user_agent
is_mobile = "mobile" in user_agent.lower()

# Chọn file video và background
video_file = "mobile.mp4" if is_mobile else "airplane.mp4"
bg_image = "mobile.jpg" if is_mobile else "cabbase.jpg"

# Chuyển trang chính sau intro
if "page" not in st.session_state:
    st.session_state.page = "intro"

if st.session_state.page == "intro":
    with open(video_file, "rb") as v:
        vid_data = v.read()
    video_base64 = base64.b64encode(vid_data).decode()

    # Đọc file âm thanh máy bay
    with open("plane_fly.mp3", "rb") as a:
        audio_data = a.read()
    audio_base64 = base64.b64encode(audio_data).decode()

    st.markdown(f"""
    <div style="
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        overflow: hidden; z-index: 1;
    ">
        <video id="introVideo" autoplay playsinline muted style="
            width: 100vw; height: 100vh; object-fit: cover;
        ">
            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
        </video>
        <audio id="planeSound">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        <div class="fade-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    </div>

    <script>
    const vid = document.getElementById("introVideo");
    const audio = document.getElementById("planeSound");
    vid.volume = 1.0;
    audio.volume = 0.5;

    // Phát đồng thời video và âm thanh
    vid.onplay = () => {{
        audio.play();
    }};

    // Hiệu ứng chữ mờ dần và ánh sáng quét chậm suốt 5s
    const text = document.querySelector('.fade-text');
    text.animate([
        {{ opacity: 0, filter: 'brightness(1)' }},
        {{ opacity: 1, filter: 'brightness(2)' }},
        {{ opacity: 1, filter: 'brightness(1.5)' }},
        {{ opacity: 0, filter: 'brightness(1)' }}
    ], {{
        duration: 5000,
        easing: 'ease-in-out',
        iterations: 1
    }});

    // Sau 9s chuyển trang
    setTimeout(() => {{
        window.parent.postMessage({{type: 'SWITCH_PAGE'}}, '*');
    }}, 9000);
    </script>

    <style>
    .fade-text {{
        position: absolute;
        top: 50%;
        width: 100%;
        text-align: center;
        font-family: 'Cinzel', serif;
        font-weight: 700;
        font-size: 4vw;
        color: white;
        text-shadow: 0 0 25px rgba(255,255,255,0.7);
        animation: glow 5s linear forwards;
    }}

    @keyframes glow {{
        0% {{ filter: brightness(0.6); }}
        50% {{ filter: brightness(2); }}
        100% {{ filter: brightness(1); opacity: 0; }}
    }}
    </style>
    """, unsafe_allow_html=True)

    # Khi nhận tín hiệu từ JS, đổi sang trang chính
    st.session_state.page = "main"

elif st.session_state.page == "main":
    st.markdown(f"""
    <style>
    body {{
        background: url("{bg_image}") no-repeat center center fixed;
        background-size: cover;
    }}
    audio {{
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 90%;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center; color:white;'>🌍 Trang chính Cabbase</h1>", unsafe_allow_html=True)
    st.audio("background.mp3")
