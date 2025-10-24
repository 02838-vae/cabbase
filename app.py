import streamlit as st
import base64
from streamlit_javascript import st_javascript
import streamlit.components.v1 as components

# ========== CẤU HÌNH ==========
VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
SFX = "plane_fly.mp3"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"

st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

# ========== SESSION STATE ==========
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = False  # Bạn có thể detect user agent nếu muốn

# ========== HÀM INTRO ==========
def intro_screen(is_mobile=False):
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    sfx_file = SFX
    try:
        with open(video_file, "rb") as f:
            video_b64 = base64.b64encode(f.read()).decode()
        with open(sfx_file, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError as e:
        st.error(f"Lỗi file: {e.filename}")
        st.stop()

    # HTML + JS (escape { } bằng {{ }})
    html = f"""
    <video id="intro-video" autoplay muted playsinline
        style="position:fixed; top:0; left:0; width:100vw; height:100vh; object-fit:cover; z-index:10;">
        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
    </video>
    <audio id="intro-audio" preload="auto">
        <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
    </audio>
    <script>
    const vid = document.getElementById('intro-video');
    const audio = document.getElementById('intro-audio');

    vid.play().catch(()=>{{}});
    audio.play().catch(()=>{{}});

    vid.addEventListener('ended', ()=>{{ window.parent.postMessage({{type:'intro_done'}}, '*'); }});

    document.addEventListener('click', ()=>{
        vid.muted = false; vid.play();
        audio.play().catch(()=>{{}});
    }}, {{once:true}});
    </script>
    """
    components.html(html, height=900, scrolling=False)

# ========== HÀM MAIN PAGE ==========
def main_page(is_mobile=False):
    bg_file = BG_MOBILE if is_mobile else BG_PC
    try:
        with open(bg_file, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError as e:
        st.error(f"Lỗi file: {e.filename}")
        st.stop()

    st.markdown(f"""
    <style>
    html, body, .stApp {{
        height:100vh; width:100vw;
        margin:0; padding:0;
        background: url('data:image/jpeg;base64,{bg_b64}') no-repeat center center fixed;
        background-size: cover;
    }}
    .welcome {{
        position:absolute; top:10%; width:100%; text-align:center;
        font-size:clamp(30px,5vw,65px); color:white;
        font-family:'Playfair Display', serif; text-shadow:0 0 20px black;
    }}
    </style>
    <div class="welcome">TỔ BẢO DƯỠNG SỐ 1</div>
    """, unsafe_allow_html=True)

# ========== LUỒNG CHÍNH ==========
if st.session_state.intro_done:
    main_page(st.session_state.is_mobile)
else:
    intro_screen(st.session_state.is_mobile)
    # Lắng nghe message từ JS khi video kết thúc
    done = st_javascript("""
    new Promise((resolve) => {{
        window.addEventListener("message", (event) => {{
            if (event.data.type === "intro_done") {{ resolve(true); }}
        }});
    }});
    """)
    if done:
        st.session_state.intro_done = True
        main_page(st.session_state.is_mobile)
