import streamlit as st
import base64
from user_agents import parse
from streamlit_javascript import st_javascript
import streamlit.components.v1 as components

# ========== CẤU HÌNH ==========
st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
SFX = "plane_fly.mp3"


# ========== ẨN UI STREAMLIT ==========
def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
    }
    .stApp, .main, .block-container {
        padding: 0 !important;
        margin: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        overflow: hidden !important;
        background: black !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ========== XÁC ĐỊNH THIẾT BỊ ==========
if "is_mobile" not in st.session_state:
    ua_string = st_javascript("window.navigator.userAgent;")
    if ua_string:
        ua = parse(ua_string)
        st.session_state.is_mobile = not ua.is_pc
        st.rerun()
    else:
        st.info("Đang xác định thiết bị...")
        st.stop()


# ========== BUILD HTML (TRẢ VỀ CHUỖI) ==========
def build_intro_html(is_mobile=False):
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    with open(video_file, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()
    with open(SFX, "rb") as a:
        audio_b64 = base64.b64encode(a.read()).decode()

    html = f"""
    <html>
    <head>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <style>
    html, body {{
        margin: 0; padding: 0; overflow: hidden;
        width: 100vw; height: 100vh; background: black;
    }}
    video {{
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        object-fit: cover;
        z-index: 1;
    }}
    #intro-text {{
        position: absolute;
        top: 12%;
        left: 50%;
        transform: translateX(-50%);
        color: #f8f4e3;
        font-size: clamp(22px, 6vw, 60px);
        font-weight: bold;
        font-family: 'Playfair Display', serif;
        text-shadow: 0 0 15px rgba(255,255,230,0.4);
        z-index: 2;
    }}
    #left, #right {{
        position: fixed;
        top: 0; width: 50vw; height: 100vh;
        background: black;
        z-index: 3;
        transition: all 1s ease-in-out;
    }}
    #left {{ left: -50vw; }}
    #right {{ right: -50vw; }}
    .close #left {{ left: 0; }}
    .close #right {{ right: 0; }}
    </style>
    </head>
    <body>
        <video id="vid" autoplay muted playsinline>
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        <audio id="sfx">
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="left"></div>
        <div id="right"></div>
        <script>
        const vid = document.getElementById('vid');
        const audio = document.getElementById('sfx');
        let ended = false;

        function finishIntro() {{
            if (ended) return;
            ended = true;
            // 1s để shutter đóng, + 300ms màn đen (tùy chỉnh)
            document.body.classList.add('close');
            setTimeout(() => {{
                // Gửi giá trị về Streamlit: components.html sẽ trả "done"
                Streamlit.setComponentValue("done");
            }}, 1300);
        }}

        vid.addEventListener('canplay', () => vid.play().catch(()=>{{}}));
        vid.addEventListener('play', () => {{
            audio.play().catch(()=>{{}});
        }});
        vid.addEventListener('ended', finishIntro);
        // Fallback timeout (in case ended not fired)
        setTimeout(finishIntro, 9000);
        </script>
    </body>
    </html>
    """
    return html


# ========== TRANG CHÍNH ==========
def main_page(is_mobile=False):
    bg = BG_MOBILE if is_mobile else BG_PC
    with open(bg, "rb") as f:
        bg_b64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    html, body, .stApp {{
        height: 100vh !important;
        background: 
            linear-gradient(to bottom, rgba(255, 235, 200, 0.25) 0%, rgba(160, 130, 90, 0.35) 50%, rgba(90, 70, 50, 0.5) 100%),
            url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed !important;
        background-size: cover !important;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
        position: relative;
    }}
    .welcome {{
        position: absolute;
        top: 8%;
        width: 100%;
        text-align: center;
        font-size: clamp(30px, 5vw, 65px);
        color: #fff5d7;
        font-family: 'Playfair Display', serif;
        text-shadow: 0 0 18px rgba(0,0,0,0.65);
        opacity: 0;
        animation: fadeIn 1.2s ease-in-out 0.4s forwards;
    }}
    @keyframes fadeIn {{
        to {{ opacity: 1; }}
    }}
    #left, #right {{
        position: fixed;
        top: 0; width: 50vw; height: 100vh;
        background: black;
        z-index: 10;
        transition: all 1.2s ease-in-out;
    }}
    #left {{ left: 0; }}
    #right {{ right: 0; }}
    body.open #left {{ left: -50vw; }}
    body.open #right {{ right: -50vw; }}
    </style>

    <div id="left"></div>
    <div id="right"></div>
    <div class="welcome">TỔ BẢO DƯỠNG SỐ 1</div>

    <script>
    // Mở shutter ngay khi trang chính render (sau một tick)
    setTimeout(()=>{{document.body.classList.add('open');}},100);
    </script>
    """, unsafe_allow_html=True)


# ========== LUỒNG CHÍNH ==========
hide_streamlit_ui()
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

if not st.session_state.intro_done:
    # Build HTML string, then call components.html ONCE and capture return value.
    html_string = build_intro_html(st.session_state.is_mobile)
    result = components.html(html_string, height=1080, scrolling=False, key="intro_comp")
    # components.html will return the value passed to Streamlit.setComponentValue(...)
    if result == "done":
        # set flag and rerun to show main_page where shutter will open
        st.session_state.intro_done = True
        st.experimental_rerun()
else:
    main_page(st.session_state.is_mobile)
