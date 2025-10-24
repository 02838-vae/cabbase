import streamlit as st
import base64
from user_agents import parse
from streamlit_javascript import st_javascript
import streamlit.components.v1 as components

# ==== FILES ====
VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
SFX = "plane_fly.mp3"

st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

# ==== CSS ẨN UI ====
def hide_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
    }
    .stApp, .main, .block-container {
        padding: 0 !important; margin: 0 !important;
        width: 100vw !important; height: 100vh !important; overflow: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ==== TRANG INTRO ====
def intro_screen(is_mobile=False):
    hide_ui()
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC

    # Đọc video + âm thanh
    with open(video_file, "rb") as v:
        video_b64 = base64.b64encode(v.read()).decode()
    try:
        with open(SFX, "rb") as s:
            audio_b64 = base64.b64encode(s.read()).decode()
    except FileNotFoundError:
        audio_b64 = None

    intro_html = f"""
    <html>
    <head>
      <meta name='viewport' content='width=device-width, initial-scale=1.0'>
      <style>
        html,body{{margin:0;padding:0;overflow:hidden;background:black;height:100%;}}
        video{{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;}}
        #intro-text{{
            position:absolute;top:8%;left:50%;transform:translateX(-50%);
            width:90vw;text-align:center;font-family:'Playfair Display',serif;
            color:#f8f4e3;font-weight:bold;
            font-size:clamp(22px,6vw,60px);
            text-shadow:0 0 12px rgba(255,255,255,0.3);
            animation:fade 6s ease-in-out forwards;
        }}
        @keyframes fade{{0%{{opacity:0;}}10%{{opacity:1;}}90%{{opacity:1;}}100%{{opacity:0;}}}}
      </style>
    </head>
    <body>
      <video id="intro" autoplay muted playsinline>
        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4" />
      </video>
      {f"<audio id='sfx'><source src='data:audio/mp3;base64,{audio_b64}' type='audio/mp3'></audio>" if audio_b64 else ""}
      <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>

      <script>
        const video = document.getElementById("intro");
        const audio = document.getElementById("sfx");

        // Khi kết thúc intro -> đánh dấu vào localStorage
        video.addEventListener("ended", () => {{
            localStorage.setItem("intro_done", "true");
            window.location.reload();
        }});

        // Cho phép bật tiếng khi người dùng click
        document.addEventListener("click", () => {{
            video.muted = false;
            if (audio) audio.play().catch(()=>{{}});
        }});
      </script>
    </body>
    </html>
    """

    components.html(intro_html, height=800, scrolling=False)


# ==== TRANG CHÍNH ====
def main_page(is_mobile=False):
    hide_ui()
    bg_file = BG_MOBILE if is_mobile else BG_PC
    with open(bg_file, "rb") as b:
        bg_b64 = base64.b64encode(b.read()).decode()

    st.markdown(f"""
    <style>
    html,body,.stApp {{
        height:100vh !important;
        background:
          linear-gradient(to bottom,rgba(255,235,200,0.25),rgba(90,70,50,0.5)),
          url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed !important;
        background-size:cover !important;
        animation:fadeIn .3s ease-in-out forwards;
    }}
    @keyframes fadeIn{{from{{opacity:0}}to{{opacity:1}}}}
    .title{{
        position:absolute;top:8%;width:100%;text-align:center;
        color:#fff5d7;font-family:'Playfair Display',serif;
        font-size:clamp(30px,5vw,65px);
        text-shadow:0 0 18px rgba(0,0,0,0.65);
    }}
    </style>
    <div class="title">TỔ BẢO DƯỠNG SỐ 1</div>
    """, unsafe_allow_html=True)


# ==== LUỒNG CHÍNH ====
hide_ui()

if "is_mobile" not in st.session_state:
    ua = st_javascript("navigator.userAgent || ''")
    st.session_state.is_mobile = not parse(ua).is_pc if ua else False
    st.experimental_rerun()

# Kiểm tra xem intro đã xem chưa (dùng localStorage)
intro_done = st_javascript("localStorage.getItem('intro_done') === 'true'")

if intro_done:
    main_page(st.session_state.is_mobile)
else:
    intro_screen(st.session_state.is_mobile)
