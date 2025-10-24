import streamlit as st
import base64
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

# ===== FILES =====
VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
SFX = "plane_fly.mp3"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"

st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

# ===== UI =====
def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
    }
    .stApp, .main, .block-container {
        padding: 0 !important; margin: 0 !important;
        width: 100vw !important; height: 100vh !important;
        overflow: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ===== INTRO =====
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    video = VIDEO_MOBILE if is_mobile else VIDEO_PC
    try:
        with open(video, "rb") as f:
            video_b64 = base64.b64encode(f.read()).decode()
        with open(SFX, "rb") as a:
            audio_b64 = base64.b64encode(a.read()).decode()
    except FileNotFoundError as e:
        st.error(f"Lỗi: Thiếu file — {e.filename}")
        st.stop()

    intro_html = f"""
    <html>
    <head>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <style>
        html,body {{margin:0;padding:0;overflow:hidden;background:black;height:100%;}}
        video {{
            position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;
        }}
        #intro-text {{
            position:absolute;top:8%;left:50%;transform:translateX(-50%);
            font-size:clamp(22px,6vw,60px);font-weight:bold;
            color:#f8f4e3;text-align:center;width:90vw;
            font-family:'Playfair Display',serif;
            background:linear-gradient(120deg,#e9dcb5 20%,#fff9e8 40%,#e9dcb5 60%);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            animation:light 6s linear infinite,fade 6s ease-in-out forwards;
        }}
        @keyframes light {{
            0%{{background-position:200% 0;}}
            100%{{background-position:-200% 0;}}
        }}
        @keyframes fade {{
            0%{{opacity:0;}}20%{{opacity:1;}}80%{{opacity:1;}}100%{{opacity:0;}}
        }}
        </style>
    </head>
    <body>
        <video id='v' autoplay muted playsinline>
            <source src='data:video/mp4;base64,{video_b64}' type='video/mp4'>
        </video>
        <audio id='a'>
            <source src='data:audio/mp3;base64,{audio_b64}' type='audio/mp3'>
        </audio>
        <div id='intro-text'>KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>

        <script>
        const v=document.getElementById('v');
        const a=document.getElementById('a');
        let done=false;

        function finish(){{
            if(done)return;
            done=true;
            window.parent.postMessage({{type:'intro_done'}}, '*');
        }}

        v.addEventListener('canplay',()=>v.play().catch(()=>{{}}));
        v.addEventListener('play',()=>{{a.play().catch(()=>{{}});}});
        document.addEventListener('click',()=>{{v.muted=false;v.play();a.play().catch(()=>{{}});}},{{once:true}});
        v.addEventListener('ended',finish);
        </script>
    </body>
    </html>
    """
    components.html(intro_html, height=800, scrolling=False)

    # Lắng nghe postMessage trả về từ JS
    return st_javascript("""
        new Promise(resolve=>{
            window.addEventListener("message",(e)=>{
                if(e.data.type==="intro_done") resolve(true);
            });
        });
    """)


# ===== MAIN =====
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    with open(bg, "rb") as f:
        bg_b64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    html,body,.stApp {{
        height:100vh !important;
        background:
            linear-gradient(to bottom,rgba(255,235,200,0.25),rgba(90,70,50,0.5)),
            url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed !important;
        background-size:cover !important;
        animation:fadeIn .25s ease-in-out forwards;
    }}
    @keyframes fadeIn {{from{{opacity:0}}to{{opacity:1}}}}
    .title {{
        position:absolute;top:8%;width:100%;text-align:center;
        font-size:clamp(30px,5vw,65px);
        color:#fff5d7;font-family:'Playfair Display',serif;
        text-shadow:0 0 18px rgba(0,0,0,0.65);
    }}
    </style>
    <div class="title">TỔ BẢO DƯỠNG SỐ 1</div>
    """, unsafe_allow_html=True)


# ===== FLOW =====
hide_streamlit_ui()

if "is_mobile" not in st.session_state:
    ua = st_javascript("navigator.userAgent")
    if ua:
        st.session_state.is_mobile = not parse(ua).is_pc
        st.rerun()

if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

if not st.session_state.intro_done:
    finished = intro_screen(st.session_state.is_mobile)
    if finished:
        st.session_state.intro_done = True
        st.rerun()
else:
    main_page(st.session_state.is_mobile)
