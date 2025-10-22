import streamlit as st
import streamlit.components.v1 as components
import base64, os, time
from streamlit_javascript import st_javascript
from user_agents import parse

# ======= CẤU HÌNH =======
st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
SFX = "plane_fly.mp3"

# ======= ẨN UI =======
def hide_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer {display:none!important;}
    .block-container {padding:0!important; margin:0!important;}
    </style>
    """, unsafe_allow_html=True)

# ======= XÁC ĐỊNH THIẾT BỊ =======
if "is_mobile" not in st.session_state:
    ua_string = st_javascript("window.navigator.userAgent;")
    if ua_string:
        ua = parse(ua_string)
        st.session_state.is_mobile = not ua.is_pc
        st.rerun()
    else:
        st.write("Đang xác định thiết bị...")
        st.stop()

# ======= MÀN HÌNH INTRO =======
def intro_component(is_mobile=False):
    hide_ui()
    video_path = VIDEO_MOBILE if is_mobile else VIDEO_PC

    if not os.path.exists(video_path):
        st.error(f"❌ Không tìm thấy video: {video_path}")
        st.stop()

    with open(video_path, "rb") as f:
        video_data = base64.b64encode(f.read()).decode()
    audio_b64 = ""
    if os.path.exists(SFX):
        with open(SFX, "rb") as a:
            audio_b64 = base64.b64encode(a.read()).decode()

    html = f"""
    <html>
    <head>
    <style>
    html,body{{margin:0;height:100%;background:black;overflow:hidden;}}
    video{{
        position:fixed;top:0;left:0;width:100vw;height:100vh;object-fit:cover;
    }}
    #left,#right{{
        position:fixed;top:0;width:50vw;height:100vh;background:black;z-index:10;
        transition:all 1s ease-in-out;
    }}
    #left{{left:-50vw;}} #right{{right:-50vw;}}
    body.close #left{{left:0;}} body.close #right{{right:0;}}
    #fade{{position:fixed;inset:0;background:black;opacity:0;transition:opacity 0.5s ease;z-index:9;}}
    body.fade #fade{{opacity:1;}}
    </style>
    </head>
    <body>
      <video id="introVid" autoplay muted playsinline>
        <source src="data:video/mp4;base64,{video_data}" type="video/mp4">
      </video>
      {"<audio id='flySfx'><source src='data:audio/mp3;base64,"+audio_b64+"' type='audio/mp3'></audio>" if audio_b64 else ""}
      <div id="left"></div><div id="right"></div><div id="fade"></div>
      <script>
      const vid = document.getElementById('introVid');
      const audio = document.getElementById('flySfx');
      let shutterClosed = false;
      vid.addEventListener('timeupdate', () => {{
          if (vid.currentTime > vid.duration - 1.3 && !shutterClosed) {{
              shutterClosed = true;
              document.body.classList.add('close');
              setTimeout(()=>document.body.classList.add('fade'),800);
              setTimeout(()=>{{window.parent.location.reload();}},1300);
          }}
      }});
      vid.addEventListener('play', ()=>{{ if(audio) audio.play().catch(()=>{{}}); }});
      </script>
    </body>
    </html>
    """
    components.html(html, height=1080, scrolling=False)

# ======= TRANG CHÍNH =======
def main_page(is_mobile=False):
    hide_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    bg_b64 = ""
    if os.path.exists(bg):
        with open(bg, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    html,body,.stApp{{margin:0;height:100vh;background:black;overflow:hidden;}}
    .bg{{position:fixed;inset:0;background:url("data:image/jpeg;base64,{bg_b64}")center/cover no-repeat;z-index:1;}}
    #left,#right{{
        position:fixed;top:0;width:50vw;height:100vh;background:black;z-index:10;
        transition:all 1s ease-in-out;
    }}
    #left{{left:0;}} #right{{right:0;}}
    body.open #left{{left:-50vw;}} body.open #right{{right:-50vw;}}
    .title{{
        position:absolute;top:10%;width:100%;text-align:center;
        color:white;font-size:clamp(30px,5vw,65px);
        font-family:'Playfair Display',serif;text-shadow:0 0 18px rgba(0,0,0,0.7);
        opacity:0;animation:fadeIn 1.2s ease forwards 0.7s;z-index:20;
    }}
    @keyframes fadeIn{{to{{opacity:1;}}}}
    </style>
    <div id="left"></div><div id="right"></div>
    <div class="bg"></div>
    <div class="title">TỔ BẢO DƯỠNG SỐ 1</div>
    <script>
    setTimeout(()=>{{document.body.classList.add('open');}},200);
    </script>
    """, unsafe_allow_html=True)

# ======= LUỒNG CHÍNH =======
hide_ui()
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

if not st.session_state.intro_done:
    intro_component(st.session_state.is_mobile)
    st.session_state.intro_done = True
    st.stop()
else:
    main_page(st.session_state.is_mobile)
