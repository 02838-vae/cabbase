import streamlit as st
import streamlit.components.v1 as components
import base64
import os
import time

# ===== CẤU HÌNH =====
VIDEO_PC = "intro_pc.mp4"
VIDEO_MOBILE = "intro_mobile.mp4"
SFX = "intro.mp3"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"


def hide_ui():
    st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding: 0 !important; margin: 0 !important;}
    </style>
    """, unsafe_allow_html=True)


# ====== COMPONENT INTRO ======
def intro_component(is_mobile=False):
    hide_ui()
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    with open(video_file, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()
    with open(SFX, "rb") as a:
        audio_b64 = base64.b64encode(a.read()).decode()

    html = f"""
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
    html,body{{height:100%;margin:0;background:black;overflow:hidden;}}
    video{{position:fixed;top:0;left:0;width:100vw;height:100vh;object-fit:cover;}}
    #left,#right{{
      position:fixed;top:0;width:50vw;height:100vh;background:black;
      z-index:10;transition:all 1.2s ease-in-out;
    }}
    #left{{left:-50vw;}} #right{{right:-50vw;}}
    body.close #left{{left:0;}} body.close #right{{right:0;}}
    </style>
    </head>
    <body>
      <video id="introVideo" autoplay playsinline muted>
        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
      </video>
      <audio id="introAudio" autoplay>
        <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
      </audio>
      <div id="left"></div><div id="right"></div>
      <script>
        const video = document.getElementById("introVideo");
        video.addEventListener('timeupdate', () => {{
          if(video.currentTime > video.duration - 1.3){{
            document.body.classList.add('close');
          }}
        }});
        video.addEventListener('ended', () => {{
          window.parent.postMessage({{"type":"end_intro"}}, "*");
        }});
      </script>
    </body></html>
    """
    components.html(html, height=1080, scrolling=False, key="intro_html")


# ====== COMPONENT MAIN PAGE ======
def main_page(is_mobile=False):
    hide_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    bg_b64 = base64.b64encode(open(bg, "rb").read()).decode()

    st.markdown(f"""
    <style>
    html,body,.stApp{{height:100vh;margin:0;overflow:hidden;}}
    .app-bg{{
      position:fixed;inset:0;
      background:
        linear-gradient(to bottom, rgba(255,235,200,0.25), rgba(90,70,50,0.5)),
        url("data:image/jpeg;base64,{bg_b64}") center/cover no-repeat;
      z-index:1;
    }}
    #left,#right{{
      position:fixed;top:0;width:50vw;height:100vh;background:black;
      z-index:9;transition:all 1.2s ease-in-out;
    }}
    #left{{left:0;}} #right{{right:0;}}
    body.open #left{{left:-50vw;}} body.open #right{{right:-50vw;}}
    .title{{position:absolute;top:8%;width:100%;text-align:center;
      font-size:clamp(32px,5vw,64px);color:#fff5d7;
      font-family:'Playfair Display',serif;text-shadow:0 0 20px rgba(0,0,0,0.7);
      opacity:0;animation:fadeIn 1.2s ease 0.6s forwards;z-index:3;}}
    @keyframes fadeIn{{to{{opacity:1}}}}
    </style>
    <div id="left"></div><div id="right"></div>
    <div class="app-bg"></div>
    <div class="title">TỔ BẢO DƯỠNG SỐ 1</div>
    <script>
      setTimeout(()=>{{document.body.classList.add('open')}},300);
    </script>
    """, unsafe_allow_html=True)


# ====== MAIN LOGIC ======
def main():
    st.set_page_config(layout="wide", page_title="CABBASE Intro", page_icon="🎬")
    hide_ui()

    # Gửi tín hiệu từ iframe → Streamlit
    components.html("""
    <script>
    window.addEventListener("message", (e)=>{
        if(e.data.type === "end_intro"){
            window.parent.postMessage({type:"streamlit:setComponentValue",value:"end_intro"}, "*");
        }
    });
    </script>
    """, height=0)

    if "intro_done" not in st.session_state:
        st.session_state.intro_done = False
    if "is_mobile" not in st.session_state:
        st.session_state.is_mobile = False

    # Đọc tín hiệu từ component
    val = st.experimental_get_query_params().get("trigger", [""])[0]

    if not st.session_state.intro_done:
        intro_component(st.session_state.is_mobile)
        comp_val = components.html("", height=0, key="msg_receiver")
        # Poll kết quả
        time.sleep(0.2)
        st.stop()
    else:
        main_page(st.session_state.is_mobile)


if __name__ == "__main__":
    main()
