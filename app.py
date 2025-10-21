import streamlit as st
import streamlit.components.v1 as components
import base64
import os
import time

# ====== CẤU HÌNH FILE ======
VIDEO_PC = "intro_pc.mp4"
VIDEO_MOBILE = "intro_mobile.mp4"
SFX = "intro.mp3"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"


# ====== HÀM ẨN GIAO DIỆN STREAMLIT ======
def hide_streamlit_ui():
    st.markdown(
        """
        <style>
        #MainMenu, footer, header {visibility: hidden;}
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ====== HÀM HIỂN THỊ VIDEO INTRO CÓ SHUTTER ======
def intro_component(is_mobile=False):
    hide_streamlit_ui()

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
      html,body {{
        height:100%; margin:0; background:black; overflow:hidden;
      }}
      video {{
        position:fixed; top:0; left:0;
        width:100vw; height:100vh; object-fit:cover;
      }}
      #left,#right {{
        position:fixed; top:0; width:50vw; height:100vh;
        background:black; z-index:10;
        transition:all 1s ease-in-out;
      }}
      #left{{left:-50vw;}}
      #right{{right:-50vw;}}
      body.close #left{{left:0;}}
      body.close #right{{right:0;}}
    </style>
    </head>
    <body>
      <video id="introVideo" autoplay playsinline>
        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
      </video>
      <audio id="introAudio" autoplay>
        <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
      </audio>
      <div id="left"></div><div id="right"></div>
      <script>
        const video = document.getElementById("introVideo");
        const audio = document.getElementById("introAudio");

        // Khi video gần hết, đóng màn
        video.addEventListener('timeupdate', () => {{
          if(video.currentTime > video.duration - 1.5){{
            document.body.classList.add('close');
          }}
        }});

        // Khi video kết thúc -> gửi tín hiệu sang Streamlit
        video.addEventListener('ended', () => {{
          window.parent.postMessage({{"type":"end_intro"}}, "*");
        }});
      </script>
    </body>
    </html>
    """
    components.html(html, height=1080, scrolling=False, key="intro_comp")


# ====== HÀM TRANG CHÍNH (CÓ HIỆU ỨNG SHUTTER MỞ RA) ======
def main_page(is_mobile=False):
    hide_streamlit_ui()

    bg = BG_MOBILE if is_mobile else BG_PC
    bg_b64 = ""

    # Đọc file nền an toàn
    if os.path.exists(bg):
        with open(bg, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()
    else:
        st.warning(f"⚠️ Không tìm thấy file nền: {bg}")

    st.markdown(f"""
    <style>
      html,body,.stApp {{
        height:100vh !important;
        margin:0 !important;
        padding:0 !important;
        overflow:hidden !important;
      }}
      .app-bg {{
        position:fixed; inset:0;
        background:
          linear-gradient(to bottom, rgba(255,235,200,0.25) 0%, rgba(160,130,90,0.35) 50%, rgba(90,70,50,0.5) 100%),
          url("data:image/jpeg;base64,{bg_b64}") center/cover fixed no-repeat;
        filter:brightness(1.05) contrast(1.1) saturate(1.05);
        z-index:1;
      }}
      .welcome {{
        position:absolute; top:8%; width:100%; text-align:center;
        font-size:clamp(30px,5vw,65px); color:#fff5d7;
        font-family:'Playfair Display',serif;
        text-shadow:0 0 18px rgba(0,0,0,0.65);
        z-index:2; opacity:0; animation:fadeIn 1.2s ease-in-out 0.6s forwards;
      }}
      @keyframes fadeIn {{ to{{opacity:1}} }}
      #left,#right {{
        position:fixed; top:0; height:100vh; width:50vw;
        background:black; z-index:9;
        transition:all 1.2s ease-in-out;
      }}
      #left{{left:0;}} #right{{right:0;}}
      body.open #left{{left:-50vw;}} body.open #right{{right:-50vw;}}
    </style>

    <div class="app-bg"></div>
    <div id="left"></div><div id="right"></div>
    <div class="welcome">TỔ BẢO DƯỠNG SỐ 1</div>

    <script>
      setTimeout(()=>{{ document.body.classList.add('open'); }}, 300);
    </script>
    """, unsafe_allow_html=True)


# ====== LOGIC CHÍNH ======
def main():
    st.set_page_config(page_title="CABBASE Intro", page_icon="🎬", layout="wide")

    # Phát hiện thiết bị (đơn giản)
    if "user_agent" not in st.session_state:
        st.session_state.user_agent = st.runtime.scriptrunner.get_script_run_ctx().session.client.request.headers.get("User-Agent", "")
    is_mobile = "Mobile" in st.session_state.user_agent or "Android" in st.session_state.user_agent

    if "intro_done" not in st.session_state:
        st.session_state.intro_done = False

    if not st.session_state.intro_done:
        intro_component(is_mobile)
        # Lắng nghe tín hiệu từ iframe
        components.html("""
        <script>
        window.addEventListener("message", (event) => {
          if(event.data.type === "end_intro") {
            window.parent.postMessage({type: "streamlit:setComponentValue", value: true}, "*");
          }
        });
        </script>
        """, height=0)
        result = st.session_state.get("intro_result", False)
        if result:
            st.session_state.intro_done = True
            st.experimental_rerun()
    else:
        main_page(is_mobile)


if __name__ == "__main__":
    main()
