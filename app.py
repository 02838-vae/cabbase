import streamlit as st
import os, base64, random, time
from user_agents import parse
from streamlit_javascript import st_javascript
import streamlit.components.v1 as components

st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

# ===== File paths =====
MEDIA_DIR = "media"
VIDEO_PC = os.path.join(MEDIA_DIR, "airplane.mp4")
VIDEO_MOBILE = os.path.join(MEDIA_DIR, "mobile.mp4")
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
MUSIC_FILES = [f"background{i}.mp3" for i in range(1, 6)]

# ===== State =====
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = None
if "start_time" not in st.session_state:
    st.session_state.start_time = None


# ===== Detect device =====
if st.session_state.is_mobile is None:
    ua = st_javascript("window.navigator.userAgent;")
    if ua:
        user_agent = parse(ua)
        st.session_state.is_mobile = not user_agent.is_pc
        st.rerun()
    else:
        st.stop()


# ===== Hide Streamlit UI =====
def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer,
    iframe[title*="keyboard"], [tabindex="0"][aria-live] {display:none !important;}
    .stApp, .main, .block-container {
        padding:0 !important; margin:0 !important;
        width:100vw !important; min-height:100vh !important;
    }
    [data-testid*="stHtmlComponents"] {
        position:fixed !important; top:0; left:0;
        width:100vw !important; height:100vh !important;
        z-index:9999;
    }
    </style>
    """, unsafe_allow_html=True)


# ===== Intro video =====
def intro_screen(is_mobile: bool):
    hide_streamlit_ui()
    video_path = VIDEO_MOBILE if is_mobile else VIDEO_PC

    # Check path existence
    if not os.path.exists(video_path):
        st.warning(f"Không tìm thấy video: {video_path}")
        st.session_state.intro_done = True
        st.rerun()
        return

    # Convert path for browser access
    abs_path = os.path.abspath(video_path)
    file_url = f"file://{abs_path}"

    # Adjustments
    text_top = "5%" if is_mobile else "8%"
    object_pos = "center 10%" if is_mobile else "center"

    intro_html = f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&display=swap" rel="stylesheet">
        <style>
            html, body {{
                margin:0; padding:0; height:100%; width:100%;
                overflow:hidden; background:black;
            }}
            video {{
                position:fixed; top:0; left:0;
                width:100vw; height:100vh;
                object-fit:cover; object-position:{object_pos};
                z-index:1;
            }}
            #intro-text {{
                position:fixed; top:{text_top}; left:50%;
                transform:translateX(-50%);
                font-family:'Cinzel Decorative', serif;
                font-size:clamp(18px, 5vw, 36px);
                color:white; text-shadow:0 0 18px rgba(255,255,255,0.9),0 0 35px rgba(255,215,0,0.6);
                opacity:0; white-space:nowrap;
                z-index:2;
                animation: fadeText 6s ease-in-out forwards;
            }}
            @keyframes fadeText {{
                0% {{ opacity:0; transform:translate(-50%,10px); }}
                15% {{ opacity:1; transform:translate(-50%,0); }}
                80% {{ opacity:1; transform:translate(-50%,0); }}
                100% {{ opacity:0; transform:translate(-50%,-10px); }}
            }}
            #fade {{
                position:fixed; top:0; left:0;
                width:100vw; height:100vh;
                background:black; opacity:0;
                transition:opacity 1.2s ease-in-out;
                z-index:3;
            }}
        </style>
    </head>
    <body>
        <video id="introVid" autoplay muted playsinline preload="auto">
            <source src="{file_url}" type="video/mp4">
        </video>
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="fade"></div>

        <script>
        const vid = document.getElementById('introVid');
        const fade = document.getElementById('fade');

        function finishIntro() {{
            fade.style.opacity = 1;
            setTimeout(() => {{
                window.parent.postMessage({{type:'intro_done'}}, '*');
            }}, 1200);
        }}

        vid.onended = finishIntro;

        vid.addEventListener('timeupdate', () => {{
            if (vid.duration && vid.duration - vid.currentTime < 1.3) {{
                fade.style.opacity = 1;
            }}
        }});

        vid.play().catch(() => {{
            console.warn("Autoplay blocked");
            setTimeout(finishIntro, 10000);
        }});
        </script>
    </body>
    </html>
    """

    components.html(intro_html, height=1000, scrolling=False)

    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()
    if time.time() - st.session_state.start_time < 35:
        time.sleep(1)
        st.rerun()
    else:
        st.session_state.intro_done = True
        st.session_state.start_time = None
        st.rerun()


# ===== Main page =====
def main_page(is_mobile: bool):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC

    try:
        with open(bg, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()
    except:
        bg_b64 = ""

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
        text-align:center; margin-top:60px; color:#2E1C14;
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


# ===== Flow =====
hide_streamlit_ui()
if not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
else:
    main_page(st.session_state.is_mobile)
