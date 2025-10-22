import streamlit as st
import streamlit.components.v1 as components
import base64
import os
import time
from user_agents import parse
from streamlit_javascript import st_javascript

# ========== CẤU HÌNH ==========
st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
SFX = "plane_fly.mp3"

# ========== ẨN GIAO DIỆN STREAMLIT ==========
def hide_ui():
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

# ========== MÀN HÌNH INTRO ==========
def intro_component(is_mobile=False):
    hide_ui()

    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    if not os.path.exists(video_file):
        st.error(f"❌ Không tìm thấy video intro: {video_file}")
        st.stop()

    with open(video_file, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()

    if os.path.exists(SFX):
        with open(SFX, "rb") as a:
            audio_b64 = base64.b64encode(a.read()).decode()
    else:
        audio_b64 = ""

    html = f"""
    <html>
    <head>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <style>
    html,body{{margin:0;padding:0;overflow:hidden;background:black;height:100%;}}
    video{{position:fixed;top:0;left:0;width:100vw;height:100vh;object-fit:cover;}}
    #intro-text{{
        position:absolute;
        top:20%;
        left:50%;
        transform:translateX(-50%);
        text-align:center;
        color:#f8f4e3;
        font-size:clamp(22px,6vw,60px);
        font-weight:bold;
        font-family:'Playfair Display',serif;
        background:linear-gradient(120deg,#e9dcb5 20%,#fff9e8 40%,#e9dcb5 60%);
        background-size:200%;
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        text-shadow:0 0 15px rgba(255,255,230,0.4);
        animation:lightSweep 6s linear infinite, fadeInOut 6s ease-in-out forwards;
    }}
    @keyframes lightSweep{{0%{{background-position:200% 0%;}}100%{{background-position:-200% 0%;}}}}
    @keyframes fadeInOut{{0%{{opacity:0;}}20%{{opacity:1;}}80%{{opacity:1;}}100%{{opacity:0;}}}}

    /* Shutter effect */
    #left,#right{{
      position:fixed;top:0;width:50vw;height:100vh;background:black;
      z-index:10;transition:all 1.2s ease-in-out;
    }}
    #left{{left:-50vw;}} #right{{right:-50vw;}}
    body.close #left{{left:0;}} body.close #right{{right:0;}}
    body.open #left{{left:-50vw;}} body.open #right{{right:-50vw;}}
    </style>
    </head>
    <body>
      <video id='introVid' autoplay playsinline muted>
        <source src='data:video/mp4;base64,{video_b64}' type='video/mp4'>
      </video>
      {"<audio id='flySfx'><source src='data:audio/mp3;base64," + audio_b64 + "' type='audio/mp3'></audio>" if audio_b64 else ""}
      <div id='intro-text'>KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
      <div id='left'></div><div id='right'></div>

      <script>
        const vid=document.getElementById('introVid');
        const audio=document.getElementById('flySfx');
        let shutterClosed=false;

        vid.addEventListener('canplay',()=>{{vid.play().catch(()=>{{}});}});
        vid.addEventListener('play',()=>{{
            if(audio){{audio.currentTime=0;audio.play().catch(()=>{{}});}}
        }});
        vid.addEventListener('timeupdate',()=>{{
            if(vid.currentTime>vid.duration-1.2 && !shutterClosed){{
                document.body.classList.add('close');
                shutterClosed=true;
            }}
        }});
        vid.addEventListener('ended',()=>{{
            setTimeout(()=>{{
                window.parent.postMessage({{type:'intro_done'}}, '*');
            }},700);
        }});
      </script>
    </body></html>
    """
    components.html(html, height=1080, scrolling=False, key="intro_html")

# ========== TRANG CHÍNH ==========
def main_page(is_mobile=False):
    hide_ui()
    bg = BG_MOBILE if is_mobile else BG_PC

    if not os.path.exists(bg):
        st.error(f"❌ Không tìm thấy hình nền: {bg}")
        st.stop()

    with open(bg, "rb") as f:
        bg_b64 = base64.b64encode(f.read()).decode()

    html = f"""
    <html>
    <head>
    <style>
    html,body{{margin:0;height:100%;overflow:hidden;background:black;}}
    .bg{{position:fixed;inset:0;background:url('data:image/jpeg;base64,{bg_b64}')center/cover no-repeat;z-index:1;}}
    .title{{
        position:absolute;top:8%;width:100%;text-align:center;
        color:#fff5d7;font-family:'Playfair Display',serif;
        font-size:clamp(30px,5vw,65px);
        text-shadow:0 0 18px rgba(0,0,0,0.65);
        animation:fadeIn 2s ease forwards 0.5s;
        opacity:0;z-index:5;
    }}
    @keyframes fadeIn{{to{{opacity:1;}}}}
    #left,#right{{
        position:fixed;top:0;width:50vw;height:100vh;background:black;
        z-index:10;transition:all 1.2s ease-in-out;
    }}
    #left{{left:0;}} #right{{right:0;}}
    body.open #left{{left:-50vw;}} body.open #right{{right:-50vw;}}
    </style>
    </head>
    <body>
      <div id="left"></div><div id="right"></div>
      <div class="bg"></div>
      <div class="title">TỔ BẢO DƯỠNG SỐ 1</div>
      <script>
        setTimeout(()=>{{document.body.classList.add('open');}},200);
      </script>
    </body></html>
    """
    components.html(html, height=1080, scrolling=False, key="main_html")

# ========== LUỒNG CHÍNH ==========
hide_ui()
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

def main():
    if not st.session_state.intro_done:
        intro_component(st.session_state.is_mobile)
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
        st.session_state.intro_done = True
        st.rerun()
    else:
        main_page(st.session_state.is_mobile)

main()
