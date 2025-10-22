import streamlit as st
import streamlit.components.v1 as components
import base64
import os
import time


# ========== CẤU HÌNH ==========
st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
SFX = "plane_fly.mp3"


# ========== ẨN UI STREAMLIT ==========
def hide_ui():
    st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding: 0 !important; margin: 0 !important;}
    </style>
    """, unsafe_allow_html=True)


# ========== INTRO ==========
def intro_component(is_mobile=False):
    hide_ui()

    # Xác định video phù hợp
    video_file = VIDEO_MOBILE if is_mobile and os.path.exists(VIDEO_MOBILE) else VIDEO_PC
    if not os.path.exists(video_file):
        st.error(f"❌ Không tìm thấy video intro: {video_file}")
        st.stop()

    # Đọc video và âm thanh
    with open(video_file, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()

    audio_b64 = ""
    if os.path.exists(SFX):
        with open(SFX, "rb") as a:
            audio_b64 = base64.b64encode(a.read()).decode()

    # HTML Intro với hiệu ứng shutter
    html = f"""
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
    html,body {{
      margin:0; padding:0; height:100%; background:black; overflow:hidden;
    }}
    video {{
      position:fixed; top:0; left:0; width:100vw; height:100vh;
      object-fit:cover;
    }}
    #left,#right {{
      position:fixed; top:0; width:50vw; height:100vh;
      background:black; z-index:10;
      transition:all 1.2s ease-in-out;
    }}
    #left {{ left:-50vw; }}
    #right {{ right:-50vw; }}
    body.close #left {{ left:0; }}
    body.close #right {{ right:0; }}
    #fade {{
      position:fixed; inset:0; background:black; opacity:0;
      z-index:11; transition:opacity 0.4s ease-in-out;
    }}
    body.fadeout #fade {{ opacity:1; }}
    </style>
    </head>
    <body>
      <video id="introVideo" autoplay playsinline muted>
        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
      </video>
      {"<audio id='introAudio' autoplay><source src='data:audio/mp3;base64," + audio_b64 + "' type='audio/mp3'></audio>" if audio_b64 else ""}
      <div id="left"></div><div id="right"></div><div id="fade"></div>

      <script>
        const video = document.getElementById("introVideo");
        let ended = false;

        video.addEventListener('timeupdate', () => {{
          if(video.currentTime > video.duration - 1.3 && !ended){{
            document.body.classList.add('close');
            ended = true;
            setTimeout(() => {{
              document.body.classList.add('fadeout');
            }}, 1000);
          }}
        }});

        video.addEventListener('ended', () => {{
          setTimeout(() => {{
            window.parent.postMessage({{"type":"end_intro"}}, "*");
          }}, 1200);
        }});
      </script>
    </body>
    </html>
    """

    components.html(html, height=1080, scrolling=False, key="intro_html")


# ========== TRANG CHÍNH ==========
def main_page(is_mobile=False):
    hide_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    bg_b64 = ""
    if os.path.exists(bg):
        with open(bg, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()
    else:
        st.warning(f"⚠️ Không tìm thấy ảnh nền: {bg}")

    st.markdown(f"""
    <style>
    html,body,.stApp {{
      height:100vh !important; margin:0; padding:0;
      overflow:hidden; background:black;
    }}
    .app-bg {{
      position:fixed; inset:0;
      background:
        linear-gradient(to bottom, rgba(255,235,200,0.25), rgba(90,70,50,0.5)),
        url("data:image/jpeg;base64,{bg_b64}") center/cover no-repeat;
      z-index:1;
    }}
    #left,#right {{
      position:fixed; top:0; width:50vw; height:100vh;
      background:black; z-index:9; transition:all 1.2s ease-in-out;
    }}
    #left {{ left:0; }}
    #right {{ right:0; }}
    body.open #left {{ left:-50vw; }}
    body.open #right {{ right:-50vw; }}
    .welcome {{
      position:absolute; top:8%; width:100%;
      text-align:center; font-size:clamp(30px,5vw,65px);
      color:#fff5d7; font-family:'Playfair Display',serif;
      text-shadow:0 0 18px rgba(0,0,0,0.65);
      opacity:0; animation:fadeIn 1.2s ease-in-out 0.6s forwards;
      z-index:3;
    }}
    @keyframes fadeIn {{ to {{ opacity:1; }} }}
    </style>

    <div id="left"></div><div id="right"></div>
    <div class="app-bg"></div>
    <div class="welcome">TỔ BẢO DƯỠNG SỐ 1</div>

    <script>
      // Mở màn shutter ra khi trang chính hiển thị
      setTimeout(()=>{{document.body.classList.add('open')}},300);
    </script>
    """, unsafe_allow_html=True)


# ========== LUỒNG CHÍNH ==========
def main():
    hide_ui()

    # Dùng session_state để lưu trạng thái intro
    if "intro_done" not in st.session_state:
        st.session_state.intro_done = False

    # Tự xác định thiết bị (mobile / PC) dựa vào chiều rộng màn hình
    components.html("""
    <script>
    const isMobile = window.innerWidth < 768;
    window.parent.postMessage({type:'set_device', isMobile}, '*');
    </script>
    """, height=0)

    # Lắng nghe tín hiệu từ intro
    components.html("""
    <script>
    window.addEventListener("message", (e)=>{
        if(e.data.type === "end_intro"){
            window.parent.postMessage({type:"streamlit:setComponentValue",value:"end_intro"}, "*");
        }
    });
    </script>
    """, height=0)

    # Cờ thiết bị
    if "is_mobile" not in st.session_state:
        st.session_state.is_mobile = False

    # Query param (API mới)
    params = st.query_params

    if not st.session_state.intro_done:
        intro_component(st.session_state.is_mobile)
        st.stop()
    else:
        main_page(st.session_state.is_mobile)


if __name__ == "__main__":
    main()
