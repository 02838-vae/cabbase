import streamlit as st
import base64
import time
import platform

st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

# ==== CSS Global ====
st.markdown("""
<style>
body, html {
    margin: 0;
    padding: 0;
    overflow: hidden;
    height: 100%;
}
.main {
    padding: 0 !important;
}
</style>
""", unsafe_allow_html=True)

# ==== Detect Device ====
def detect_device():
    user_agent = st.session_state.get("ua_string", "")
    is_mobile = any(x in user_agent for x in ["Mobile", "Android", "iPhone", "iPad"])
    return is_mobile

if "ua_string" not in st.session_state:
    try:
        import streamlit.web.server.browser_websocket_handler as browser_ws
        from streamlit.web.server import Server
        ctx = Server.get_current()._get_session_info(None)
        if ctx and ctx.ws.request:
            st.session_state.ua_string = ctx.ws.request.headers.get("User-Agent", "")
        else:
            st.session_state.ua_string = ""
    except Exception:
        st.session_state.ua_string = ""

# ==== Load Binary Files ====
def load_file_as_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# ==== Intro Screen ====
def intro_screen(is_mobile):
    video_file = "mobile.mp4" if is_mobile else "airplane.mp4"
    bg_file = "mobile.jpg" if is_mobile else "cabbase.jpg"
    video_b64 = load_file_as_base64(video_file)
    audio_b64 = load_file_as_base64("plane_fly.mp3")

    html_code = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <style>
        html, body {{
            margin:0; padding:0;
            width:100%; height:100%;
            overflow:hidden; background:black;
            font-family: 'Playfair Display', serif;
        }}
        video {{
            position:absolute; top:0; left:0;
            width:100%; height:100%;
            object-fit: cover;
            z-index:1;
        }}
        #intro-text {{
            position:absolute;
            top:50%;
            left:50%;
            transform: translate(-50%, -50%);
            font-size: clamp(20px, 5vw, 48px);
            color: #fff;
            font-weight: bold;
            text-align:center;
            text-shadow: 0 0 20px rgba(255,255,255,0.6);
            z-index:2;
            background: linear-gradient(90deg, #fff, #d4af37, #fff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-size: 200%;
            animation: shine 5s linear infinite, fadeInOut 5s ease-in-out forwards;
        }}
        @keyframes shine {{
            0% {{ background-position: 200%; }}
            100% {{ background-position: -200%; }}
        }}
        @keyframes fadeInOut {{
            0% {{ opacity:0; }}
            20% {{ opacity:1; }}
            80% {{ opacity:1; }}
            100% {{ opacity:0; }}
        }}
        #fade {{
            position:absolute;
            top:0; left:0;
            width:100%; height:100%;
            background:black;
            opacity:0;
            z-index:3;
            transition: opacity 1s ease-in-out;
        }}
        </style>
    </head>
    <body>
        <video id="introVid" autoplay playsinline>
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <audio id="planeAudio" autoplay>
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>
        <div id="fade"></div>
        <script>
        const vid = document.getElementById("introVid");
        const fade = document.getElementById("fade");
        const audio = document.getElementById("planeAudio");

        function finishIntro() {{
            fade.style.opacity = 1;
            setTimeout(() => {{
                window.parent.postMessage({{"type": "intro_done"}}, "*");
            }}, 1000);
        }}

        vid.addEventListener("ended", finishIntro);
        vid.play().catch(() => {{
            console.log("Autoplay blocked");
            setTimeout(finishIntro, 5000);
        }});
        audio.play().catch(() => {{
            console.log("Audio blocked");
        }});
        </script>
    </body>
    </html>
    """

    st.components.v1.html(html_code, height=800)

# ==== Main Page ====
def main_page(is_mobile):
    bg_path = "mobile.jpg" if is_mobile else "cabbase.jpg"
    bg_b64 = load_file_as_base64(bg_path)

    st.markdown(f"""
    <style>
    .main-container {{
        background: url("data:image/jpg;base64,{bg_b64}") no-repeat center center fixed;
        background-size: cover;
        height: 100vh;
        width: 100%;
        display:flex;
        justify-content:center;
        align-items:center;
        color:white;
        font-size:2rem;
        text-shadow:0 0 15px rgba(0,0,0,0.6);
    }}
    </style>
    <div class="main-container">
        ✈️ Chào mừng đến với CABBASE ✈️
    </div>
    """, unsafe_allow_html=True)

# ==== Controller ====
if "page" not in st.session_state:
    st.session_state.page = "intro"

is_mobile = detect_device()

if st.session_state.page == "intro":
    intro_screen(is_mobile)

    st.markdown("""
    <script>
    window.addEventListener("message", (event) => {
        if (event.data.type === "intro_done") {
            window.parent.location.reload();
        }
    });
    </script>
    """, unsafe_allow_html=True)

    # Sau 9s (5s video + 4s fade) chuyển trang
    time.sleep(9)
    st.session_state.page = "main"
    st.rerun()

else:
    main_page(is_mobile)
