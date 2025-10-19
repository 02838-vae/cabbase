import streamlit as st
import os, base64, random, time
from user_agents import parse
from streamlit_javascript import st_javascript
import streamlit.components.v1 as components

st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

MEDIA_DIR = "media"
VIDEO_PC = os.path.join(MEDIA_DIR, "airplane.mp4")
VIDEO_MOBILE = os.path.join(MEDIA_DIR, "mobile.mp4")
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
MUSIC_FILES = [f"background{i}.mp3" for i in range(1, 6)]

if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = None
if "intro_start" not in st.session_state:
    st.session_state.intro_start = None


# --- Detect device ---
if st.session_state.is_mobile is None:
    ua = st_javascript("window.navigator.userAgent;")
    if ua:
        user_agent = parse(ua)
        st.session_state.is_mobile = not user_agent.is_pc
        st.rerun()
    else:
        st.stop()


def hide_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live] {display:none !important;}
    .stApp, .main, .block-container {padding:0 !important; margin:0 !important; width:100vw !important; height:100vh !important;}
    [data-testid*="stHtmlComponents"] {position:fixed !important; top:0; left:0; width:100vw !important; height:100vh !important; z-index:9999;}
    </style>
    """, unsafe_allow_html=True)


def intro_screen(is_mobile: bool):
    hide_ui()
    video_path = VIDEO_MOBILE if is_mobile else VIDEO_PC

    if not os.path.exists(video_path):
        st.session_state.intro_done = True
        st.rerun()
        return

    with open(video_path, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()

    text_top = "5%" if is_mobile else "10%"
    font_size = "clamp(18px, 5vw, 38px)"
    object_pos = "center 15%" if is_mobile else "center"

    html = f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&display=swap" rel="stylesheet">
        <style>
        html,body{{margin:0;padding:0;overflow:hidden;background:black;height:100%;}}
        video{{position:fixed;top:0;left:0;width:100vw;height:100vh;object-fit:cover;object-position:{object_pos};z-index:1;}}
        #title{{position:fixed;top:{text_top};left:50%;transform:translateX(-50%);color:white;
            font-family:'Cinzel Decorative',serif;font-size:{font_size};
            text-shadow:0 0 25px rgba(255,255,255,0.9),0 0 35px rgba(255,215,0,0.8);
            opacity:0;white-space:nowrap;z-index:2;animation:fadeText 6s ease-in-out forwards;}}
        @keyframes fadeText{{0%{{opacity:0;transform:translate(-50%,20px);}}
        15%{{opacity:1;transform:translate(-50%,0);}}80%{{opacity:1;}}100%{{opacity:0;}}}}
        #fade{{position:fixed;top:0;left:0;width:100vw;height:100vh;background:black;opacity:0;transition:opacity 2s ease-in-out;z-index:3;}}
        </style>
    </head>
    <body>
        <video id="vid" autoplay muted playsinline preload="auto">
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        <div id="title">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="fade"></div>
        <script>
        const vid=document.getElementById('vid');
        const fade=document.getElementById('fade');
        vid.addEventListener('timeupdate',()=>{{
            if(vid.duration && vid.duration-vid.currentTime<1.5)fade.style.opacity=1;
        }});
        </script>
    </body>
    </html>
    """

    components.html(html, height=800, scrolling=False)

    # Khi video load, lấy duration để tính thời gian kết thúc
    duration = st_javascript("""
        new Promise(resolve=>{
            const vid=document.querySelector('video');
            if(!vid) resolve(null);
            else vid.onloadedmetadata=()=>resolve(vid.duration);
        });
    """)

    if duration is None:
        st.stop()

    # Polling kiểm tra thời gian thực
    if st.session_state.intro_start is None:
        st.session_state.intro_start = time.time()

    elapsed = time.time() - st.session_state.intro_start
    if elapsed < duration + 1.5:
        st.stop()
    else:
        st.session_state.intro_done = True
        st.session_state.intro_start = None
        st.rerun()


def main_page(is_mobile: bool):
    hide_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    bg_b64 = base64.b64encode(open(bg, "rb").read()).decode() if os.path.exists(bg) else ""

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&display=swap');
    .stApp {{
        background-image:url("data:image/jpeg;base64,{bg_b64}");
        background-size:cover; background-position:center;
        animation:fadeIn 1s ease-in forwards;
    }}
    @keyframes fadeIn {{ from{{opacity:0}} to{{opacity:1}} }}
    h1 {{
        text-align:center; margin-top:80px; color:#2E1C14;
        text-shadow:2px 2px 6px #FFF8DC;
        font-family:'Playfair Display', serif;
    }}
    </style>
    """, unsafe_allow_html=True)

    available = [m for m in MUSIC_FILES if os.path.exists(m)]
    if available:
        chosen = random.choice(available)
        with st.sidebar:
            st.subheader("🎵 Nhạc nền")
            st.audio(chosen, start_time=0)
            st.caption(f"Đang phát: {os.path.basename(chosen)}")

    st.markdown("<h1>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)


hide_ui()
if not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
else:
    main_page(st.session_state.is_mobile)
