import streamlit as st
import base64
import time

st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

# ==== CSS chung ====
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

# ==== Hàm hỗ trợ ====
def load_file_as_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# ==== Giao diện intro ====
def intro_screen():
    video_b64 = load_file_as_base64("airplane.mp4")
    audio_b64 = load_file_as_base64("plane_fly.mp3")

    html_code = f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
        html, body {{
            margin:0; padding:0; overflow:hidden; height:100%;
            background:black;
        }}
        video {{
            position:absolute; top:0; left:0;
            width:100%; height:100%;
            object-fit:cover;
            z-index:1;
        }}
        #intro-text {{
            position:absolute;
            top:50%;
            left:50%;
            transform: translate(-50%, -50%);
            font-size: clamp(22px, 5vw, 48px);
            color:white;
            font-family:'Playfair Display',serif;
            font-weight:bold;
            text-shadow: 0 0 25px rgba(255,255,255,0.8);
            text-align:center;
            background: linear-gradient(90deg, #fff, #f6d365, #fda085, #fff);
            background-size: 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shine 5s linear infinite, fadeInOut 6s ease-in-out forwards;
            z-index:2;
        }}
        @keyframes shine {{
            0% {{ background-position: 300%; }}
            100% {{ background-position: -300%; }}
        }}
        @keyframes fadeInOut {{
            0% {{ opacity: 0; }}
            20% {{ opacity: 1; }}
            80% {{ opacity: 1; }}
            100% {{ opacity: 0; }}
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
        <video id="introVid" autoplay playsinline muted>
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        <audio id="planeAudio">
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="fade"></div>
        <script>
        const vid = document.getElementById("introVid");
        const fade = document.getElementById("fade");
        const audio = document.getElementById("planeAudio");

        function startAudio() {{
            audio.volume = 0.7;
            audio.play().catch(()=>{{console.log("Audio blocked")}});

            // Hiệu ứng tăng giảm âm thanh
            let fadeIn = setInterval(() => {{
                if(audio.volume < 1.0) audio.volume += 0.1;
                else clearInterval(fadeIn);
            }}, 400);

            setTimeout(() => {{
                let fadeOut = setInterval(() => {{
                    if(audio.volume > 0.1) audio.volume -= 0.1;
                    else clearInterval(fadeOut);
                }}, 400);
            }}, 3500);
        }}

        vid.addEventListener('play', startAudio);

        vid.addEventListener('ended', () => {{
            fade.style.opacity = 1;
            setTimeout(() => {{
                window.parent.postMessage({{type: "intro_done"}}, "*");
            }}, 1000);
        }});

        vid.play().catch(()=>{{
            console.log("Autoplay blocked");
            setTimeout(() => {{
                window.parent.postMessage({{type: "intro_done"}}, "*");
            }}, 5000);
        }});
        </script>
    </body>
    </html>
    """
    st.components.v1.html(html_code, height=800)

# ==== Trang chính ====
def main_page():
    bg_b64 = load_file_as_base64("cabbase.jpg")
    st.markdown(f"""
    <style>
    .main-bg {{
        background: url("data:image/jpg;base64,{bg_b64}") no-repeat center center fixed;
        background-size: cover;
        height: 100vh;
        display:flex;
        justify-content:center;
        align-items:center;
        color:white;
        font-size:2rem;
        text-shadow:0 0 20px rgba(0,0,0,0.7);
    }}
    </style>
    <div class="main-bg">✈️ Chào mừng đến với CABBASE ✈️</div>
    """, unsafe_allow_html=True)

# ==== Điều khiển trang ====
if "page" not in st.session_state:
    st.session_state.page = "intro"

if st.session_state.page == "intro":
    intro_screen()
    st.markdown("""
    <script>
    window.addEventListener("message", (event) => {
        if (event.data.type === "intro_done") {
            window.parent.location.reload();
        }
    });
    </script>
    """, unsafe_allow_html=True)
    time.sleep(9)
    st.session_state.page = "main"
    st.rerun()
else:
    main_page()
