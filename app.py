import streamlit as st
import os, base64, random
from user_agents import parse
from streamlit_javascript import st_javascript
import streamlit.components.v1 as components

# ================== CẤU HÌNH ==================
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

VIDEO_PC = "media/airplane.mp4"
VIDEO_MOBILE = "media/mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
MUSIC_FILES = [
    "background.mp3", "background2.mp3", "background3.mp3",
    "background4.mp3", "background5.mp3"
]

# ================== TRẠNG THÁI ==================
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = None

# ================== XÁC ĐỊNH THIẾT BỊ ==================
if st.session_state.is_mobile is None:
    ua = st_javascript("window.navigator.userAgent;")
    if ua:
        st.session_state.is_mobile = not parse(ua).is_pc
        st.rerun()
    else:
        st.stop()

# ================== ẨN UI STREAMLIT ==================
def hide_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live] {
        display:none !important;
        visibility:hidden !important;
    }
    .stApp, .main, .block-container {
        padding:0 !important; margin:0 !important;
        width:100vw !important; height:100vh !important;
        overflow:hidden !important;
    }
    [data-testid*="stHtmlComponents"] {
        position:fixed !important; top:0; left:0;
        width:100vw !important; height:100vh !important;
        z-index:9999 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ================== MÀN HÌNH INTRO ==================
def intro_screen(is_mobile=False):
    hide_ui()
    video_path = VIDEO_MOBILE if is_mobile else VIDEO_PC
    if not os.path.exists(video_path):
        st.session_state.intro_done = True
        st.rerun()
        return

    with open(video_path, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()

    text_position = "8%" if is_mobile else "10%"
    font_size = "clamp(20px, 5vw, 45px)"
    object_pos = "center 10%" if is_mobile else "center"

    intro_html = f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&display=swap" rel="stylesheet">
        <style>
            html, body {{
                margin:0; padding:0;
                width:100vw; height:100vh;
                overflow:hidden; background:black;
            }}
            video {{
                position:fixed; top:0; left:0;
                width:100%; height:100%;
                object-fit:cover; object-position:{object_pos};
                z-index:1;
            }}
            #intro-text {{
                position:fixed; top:{text_position}; left:50%;
                transform:translateX(-50%);
                color:white;
                font-family:'Cinzel Decorative', serif;
                font-size:{font_size};
                text-shadow:0 0 30px rgba(255,255,255,0.9), 0 0 45px rgba(255,215,0,0.8);
                opacity:0; white-space:nowrap;
                z-index:3;
                animation:fadeText 5s ease-in-out forwards;
            }}
            @keyframes fadeText {{
                0% {{opacity:0; transform:translate(-50%,20px);}}
                15% {{opacity:1; transform:translate(-50%,0);}}
                85% {{opacity:1;}}
                100% {{opacity:0; transform:translate(-50%,-10px);}}
            }}
            #fade {{
                position:fixed; top:0; left:0;
                width:100%; height:100%;
                background:black;
                opacity:0;
                transition:opacity 4s ease-in-out;
                z-index:2;
            }}
        </style>
    </head>
    <body>
        <video id="introVid" autoplay muted playsinline>
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="fade"></div>
        <script>
            const vid = document.getElementById("introVid");
            const fade = document.getElementById("fade");
            let done = false;

            function goNext() {{
                if (done) return;
                done = true;
                fade.style.opacity = 1;
                setTimeout(() => {{
                    window.location.href = window.location.href + "?done=1";
                }}, 4000);
            }}

            vid.addEventListener('ended', goNext);
            vid.play().catch(() => {{
                console.log("Autoplay bị chặn, fallback sau 9s");
                setTimeout(goNext, 9000);
            }});

            // fallback nếu không có onended
            setTimeout(goNext, 9000);
        </script>
    </body>
    </html>
    """

    components.html(intro_html, height=900, scrolling=False)
    done = st_javascript("window.location.search.includes('done=1');")
    if done:
        st.session_state.intro_done = True
        st.rerun()
    else:
        st.stop()

# ================== TRANG CHÍNH ==================
def main_page(is_mobile=False):
    hide_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    bg_b64 = base64.b64encode(open(bg, "rb").read()).decode() if os.path.exists(bg) else ""

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&display=swap');
    .stApp {{
        background-image:url("data:image/jpeg;base64,{bg_b64}");
        background-size:cover;
        background-position:center;
        animation:fadeIn 1s ease-in forwards;
    }}
    @keyframes fadeIn {{from{{opacity:0}}to{{opacity:1}}}}
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
            st.audio(chosen)
            st.caption(f"Đang phát: {os.path.basename(chosen)}")

    st.markdown("<h1>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)

# ================== LUỒNG CHÍNH ==================
hide_ui()
if not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
else:
    main_page(st.session_state.is_mobile)
