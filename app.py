import streamlit as st
import base64
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

# ========== CẤU HÌNH ==========
VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
SFX = "plane_fly.mp3"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"

st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

# ========== HÀM ẨN UI STREAMLIT ==========
def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live] {display: none !important;}
    .stApp, .main, .block-container {padding:0 !important; margin:0 !important; width:100vw !important; height:100vh !important; overflow:hidden !important;}
    </style>
    """, unsafe_allow_html=True)

# ========== INTRO SCREEN ==========
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    bg_file = BG_MOBILE if is_mobile else BG_PC

    try:
        with open(video_file, "rb") as f:
            video_b64 = base64.b64encode(f.read()).decode()
        with open(SFX, "rb") as a:
            audio_b64 = base64.b64encode(a.read()).decode()
        with open(bg_file, "rb") as b:
            bg_b64 = base64.b64encode(b.read()).decode()
    except FileNotFoundError as e:
        st.error(f"Lỗi: Không tìm thấy file tài nguyên. Vui lòng kiểm tra: {e.filename}")
        st.stop()

    intro_html = f"""
    <html>
    <head>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <style>
    html, body {{margin:0;padding:0;overflow:hidden;background:black;height:100%;}}
    video {{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;}}
    audio {{display:none;}}
    #intro-text {{
        position:absolute; top:8%; left:50%; transform:translate(-50%,0);
        width:90vw; text-align:center; color:#f8f4e3;
        font-size:clamp(22px,6vw,60px); font-weight:bold; font-family:'Playfair Display', serif;
        background:linear-gradient(120deg,#e9dcb5 20%,#fff9e8 40%,#e9dcb5 60%);
        background-size:200%; -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        text-shadow:0 0 15px rgba(255,255,230,0.4);
        animation: lightSweep 6s linear infinite, fadeInOut 6s ease-in-out forwards;
        line-height:1.2; word-wrap:break-word; z-index:10;
    }}
    @keyframes lightSweep {{0%{{background-position:200% 0%;}} 100%{{background-position:-200% 0%;}}}}
    @keyframes fadeInOut {{0%{{opacity:0;}}20%{{opacity:1;}}80%{{opacity:1;}}100%{{opacity:0;}}}}
    #black-fade {{
        position:absolute; top:0; left:0; width:100%; height:100%;
        background:black; opacity:1; z-index:40; transition:opacity 1s ease-in-out; pointer-events:none;
    }}
    </style>
    </head>
    <body>
    <video id='introVid' autoplay muted playsinline>
        <source src='data:video/mp4;base64,{video_b64}' type='video/mp4'>
    </video>
    <audio id='flySfx'><source src='data:audio/mp3;base64,{audio_b64}' type='audio/mp3'></audio>
    <div id='intro-text'>KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
    <div id='black-fade'></div>

    <script>
    const vid = document.getElementById('introVid');
    const audio = document.getElementById('flySfx');
    const blackFade = document.getElementById('black-fade');
    let ended = false;

    function finishIntro() {{
        if (ended) return;
        ended = true;
        blackFade.style.opacity = 1;
        setTimeout(() => {{
            window.location.href = "?intro_done=true";
        }}, 1000);
    }}

    vid.addEventListener('canplay', () => {{
        vid.play().catch(()=>console.log('Autoplay bị chặn'));
        blackFade.style.opacity = 0;
    }});
    vid.addEventListener('play', () => {{
        audio.volume = 1.0;
        audio.currentTime = 0;
        audio.play().catch(()=>console.log('Autoplay âm thanh bị chặn'));
    }});
    document.addEventListener('click', () => {{
        vid.muted = false;
        vid.play();
        audio.volume = 1.0;
        audio.currentTime = 0;
        audio.play().catch(()=>{{}});
        blackFade.style.opacity = 0;
    }}, {{once:true}});

    vid.addEventListener('ended', finishIntro);
    setTimeout(finishIntro, 9000);
    </script>
    </body>
    </html>
    """
    components.html(intro_html, height=800, scrolling=False)

# ========== MAIN PAGE ==========
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    try:
        with open(bg, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError as e:
        st.error(f"Lỗi: Không tìm thấy file tài nguyên: {e.filename}")
        st.stop()

    st.markdown(f"""
    <style>
    html, body, .stApp {{
        height:100vh !important;
        background:
            linear-gradient(to bottom, rgba(255,235,200,0.25) 0%, rgba(160,130,90,0.35) 50%, rgba(90,70,50,0.5) 100%),
            url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed !important;
        background-size:cover !important; overflow:hidden !important; margin:0 !important; padding:0 !important; position:relative;
        filter: brightness(1.05) contrast(1.1) saturate(1.05); animation: fadeInBg 0.5s ease-in-out forwards;
    }}
    @keyframes fadeInBg {{from{{opacity:0;}}to{{opacity:1;}}}}
    .welcome {{
        position:absolute; top:8%; width:100%; text-align:center;
        font-size:clamp(30px,5vw,65px); color:#fff5d7;
        font-family:'Playfair Display', serif;
        text-shadow:0 0 18px rgba(0,0,0,0.65),0 0 30px rgba(255,255,180,0.25);
        background:linear-gradient(120deg,#f3e6b4 20%,#fff7d6 40%,#f3e6b4 60%);
        background-size:200%; -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        animation:textLight 10s linear infinite, fadeIn 1s ease-in-out forwards; letter-spacing:2px; z-index:3;
    }}
    @keyframes textLight {{0%{{background-position:200% 0%;}}100%{{background-position:-200% 0%;}}}}
    @keyframes fadeIn {{from{{opacity:0; transform:scale(0.97);}}to{{opacity:1; transform:scale(1);}}}}
    </style>
    <div class="welcome">TỔ BẢO DƯỠNG SỐ 1</div>
    """, unsafe_allow_html=True)

# ========== MAIN LOGIC ==========
hide_streamlit_ui()

# Detect mobile
if "is_mobile" not in st.session_state:
    ua_string = st_javascript("window.navigator.userAgent;")
    if ua_string:
        ua = parse(ua_string)
        st.session_state.is_mobile = not ua.is_pc
        st.rerun()
    else:
        st.info("Đang xác định thiết bị...")
        st.stop()

# Check query param using st.query_params
query_params = st.query_params
if "intro_done" in query_params and query_params["intro_done"][0] == "true":
    st.session_state.intro_done = True
elif "intro_done" not in st.session_state:
    st.session_state.intro_done = False

# Render
if not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
else:
    main_page(st.session_state.is_mobile)
