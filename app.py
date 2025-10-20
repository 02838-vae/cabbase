import streamlit as st
import os
import base64
import random
import time
from user_agents import parse
import streamlit.components.v1 as components
from streamlit_javascript import st_javascript

# ================== CẤU HÌNH & TRẠNG THÁI ==================
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

VIDEO_PC = "media/airplane.mp4"
VIDEO_MOBILE = "media/mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
MUSIC_FILES = [
    "background.mp3", "background2.mp3", "background3.mp3",
    "background4.mp3", "background5.mp3"
]
PLANE_AUDIO = "plane_fly.mp3"

if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = None
if "start_time" not in st.session_state:
    st.session_state.start_time = None

# ================== XÁC ĐỊNH THIẾT BỊ ==================
if st.session_state.is_mobile is None:
    st.session_state.intro_done = False
    ua_string = st_javascript("""window.navigator.userAgent;""")
    if ua_string:
        user_agent = parse(ua_string)
        st.session_state.is_mobile = not user_agent.is_pc
        st.rerun()
    else:
        st.info("Đang xác định thiết bị và tải...")
        st.stop()

# ================== ẨN STREAMLIT UI ==================
def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer,
    iframe[title*="keyboard"], [tabindex="0"][aria-live] {display:none !important; visibility:hidden !important;}
    .stApp, .main, .block-container, [data-testid="stVerticalBlock"] {padding:0 !important; margin:0 !important; width:100vw !important; min-height:100vh !important;}
    [data-testid*="stHtmlComponents"] {position: fixed !important; top:0; left:0; width:100vw !important; height:100vh !important; z-index:9999;}
    </style>
    """, unsafe_allow_html=True)

# ================== MÀN HÌNH INTRO ==================
def intro_screen(is_mobile=False):
    hide_streamlit_ui()

    video_path = VIDEO_MOBILE if is_mobile else VIDEO_PC
    if not os.path.exists(video_path):
        st.error(f"⚠️ Không tìm thấy video: {video_path}")
        st.session_state.intro_done = True
        st.rerun()
        return

    # Base64 video
    with open(video_path, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()
    # Base64 audio máy bay
    if os.path.exists(PLANE_AUDIO):
        with open(PLANE_AUDIO, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode()
    else:
        audio_b64 = ""

    # CSS vị trí video & chữ
    object_position = "center top;" if is_mobile else "center;"
    text_bottom = "35%" if is_mobile else "18%"

    intro_html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <style>
        html, body {{margin:0; padding:0; width:100vw; height:100vh; overflow:hidden; background:black; font-family:'Playfair Display', serif;}}
        video {{position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; object-position:{object_position}; z-index:1;}}
        #intro-text {{
            position:absolute; left:50%; bottom:{text_bottom}; transform:translateX(-50%);
            font-size:clamp(18px, 6vw, 40px); color:white; z-index:2;
            text-shadow:2px 2px 6px rgba(0,0,0,0.8); text-align:center;
        }}
        #fade {{position:absolute; top:0; left:0; width:100%; height:100%; background:black; opacity:0; z-index:3; transition:opacity 1.2s ease-in-out;}}
    </style>
    </head>
    <body>
        <video id="introVid" autoplay muted playsinline>
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        <audio id="planeAudio" playsinline>
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="fade"></div>

        <script>
        const vid=document.getElementById("introVid");
        const audio=document.getElementById("planeAudio");
        const fade=document.getElementById("fade");
        const text=document.getElementById("intro-text");

        // fade chữ từ từ
        text.style.opacity=0;
        text.style.transition="opacity 2s ease-in-out";
        setTimeout(()=>{{text.style.opacity=1;}},500);
        setTimeout(()=>{{text.style.opacity=0;}},4000);

        // Phát audio khi video play
        vid.onplay = ()=>{{ try{{audio.play();}}catch(e){{console.log("Audio blocked")}} }};

        function finishIntro(){{
            fade.style.opacity=1;
            setTimeout(()=>{{window.parent.postMessage({{"type":"intro_done"}}, "*");}},1200);
        }}

        // Chuyển cảnh khi video kết thúc
        vid.onended=finishIntro;

        // fallback timer
        setTimeout(finishIntro,5000);
        </script>
    </body>
    </html>
    """

    components.html(intro_html, height=1300, scrolling=False)

# ================== TRANG CHÍNH ==================
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC

    try:
        with open(bg,"rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()
    except:
        bg_b64=""

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&display=swap');
    .stApp {{
        background-image:url("data:image/jpeg;base64,{bg_b64}");
        background-size:cover;
        background-position:center;
        background-attachment:fixed;
        animation:fadeInBg 1s ease-in-out forwards;
    }}
    @keyframes fadeInBg{{from{{opacity:0;}}to{{opacity:1;}}}}
    h1{{text-align:center;margin-top:60px;color:#2E1C14;text-shadow:2px 2px 6px #FFF8DC;font-family:'Playfair Display', serif;}}
    </style>
    """, unsafe_allow_html=True)

    available_music=[m for m in MUSIC_FILES if os.path.exists(m)]
    if available_music:
        chosen=random.choice(available_music)
        with st.sidebar:
            st.subheader("🎵 Nhạc nền")
            st.audio(chosen, start_time=0)
            st.caption(f"Đang phát: **{os.path.basename(chosen)}**")
    st.markdown("<h1>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)

# ================== LUỒNG CHÍNH ==================
hide_streamlit_ui()

if st.session_state.is_mobile is None:
    pass
elif not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
else:
    main_page(st.session_state.is_mobile)
