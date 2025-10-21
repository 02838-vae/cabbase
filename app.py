# app.py (robust localStorage polling version)
import streamlit as st
import base64
import time
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
SFX = "plane_fly.mp3"

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

# detect device once
if "is_mobile" not in st.session_state:
    ua_string = st_javascript("window.navigator.userAgent;")
    if ua_string:
        ua = parse(ua_string)
        st.session_state.is_mobile = not ua.is_pc
        st.rerun()
    else:
        st.info("Đang xác định thiết bị...")
        st.stop()

# Build the intro HTML (returns string). This HTML will set localStorage key 'cabbase_intro_done' when shutter closes.
def build_intro_html(is_mobile=False):
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    with open(video_file, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()
    with open(SFX, "rb") as a:
        audio_b64 = base64.b64encode(a.read()).decode()

    html = f"""
    <!doctype html>
    <html>
    <head>
      <meta name='viewport' content='width=device-width, initial-scale=1.0'>
      <style>
        html,body{{margin:0;padding:0;height:100vh;width:100vw;overflow:hidden;background:black}}
        video{{position:fixed;top:0;left:0;width:100vw;height:100vh;object-fit:cover;z-index:1;background:black}}
        #intro-text{{position:absolute;top:12%;left:50%;transform:translateX(-50%);z-index:2;
                     color:#f8f4e3;font-family:'Playfair Display',serif;font-weight:700;
                     font-size:clamp(22px,6vw,60px);text-shadow:0 0 15px rgba(255,255,230,0.4)}}
        /* shutters */
        #left,#right{{position:fixed;top:0;height:100vh;width:50vw;background:black;z-index:3;transition:all 1s ease-in-out}}
        #left{{left:-50vw}} #right{{right:-50vw}}
        .close #left{{left:0}} .close #right{{right:0}}
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
      <div id="left"></div><div id="right"></div>

      <script>
        const vid = document.getElementById('vid');
        const audio = document.getElementById('sfx');
        let finished = false;

        function finishIntro(){{
          if(finished) return;
          finished = true;
          // close shutters (1s)
          document.body.classList.add('close');
          // after close animation completes (we wait 1s), hold black for 300ms then set flag
          setTimeout(()=>{{ 
            // ensure full black background
            document.body.style.background = 'black';
            // small hold for cinematic feel
            setTimeout(()=>{{
              // set localStorage flag for Streamlit to detect
              try{{ localStorage.setItem('cabbase_intro_done', Date.now().toString()); }}catch(e){{console.warn(e)}}
            }}, 300);
          }}, 1000);
        }}

        vid.addEventListener('canplay', ()=> vid.play().catch(()=>{{}}));
        vid.addEventListener('play', ()=> {{ try{{ audio.play().catch(()=>{{}}); }}catch(e){{}} }});
        vid.addEventListener('ended', finishIntro);
        // fallback in case ended doesn't fire
        setTimeout(finishIntro, 9000);
      </script>
    </body>
    </html>
    """
    return html

# main page markup (contains shutters starting closed; we open them via a class on body)
def main_page(is_mobile=False):
    bg = BG_MOBILE if is_mobile else BG_PC
    with open(bg, "rb") as f:
        bg_b64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
      html,body,.stApp{{height:100vh !important;margin:0 !important;padding:0 !important;overflow:hidden !important}}
      .app-bg {{
        position:fixed;inset:0;background:
          linear-gradient(to bottom, rgba(255,235,200,0.25) 0%, rgba(160,130,90,0.35) 50%, rgba(90,70,50,0.5) 100%),
          url("data:image/jpeg;base64,{bg_b64}") center/cover fixed no-repeat;
        filter:brightness(1.05) contrast(1.1) saturate(1.05);
        z-index:1;
      }}
      .welcome{{position:absolute;top:8%;width:100%;text-align:center;font-size:clamp(30px,5vw,65px);color:#fff5d7;
               font-family:'Playfair Display',serif;text-shadow:0 0 18px rgba(0,0,0,0.65);z-index:2;opacity:0;
               animation:fadeIn 1.2s ease-in-out 0.6s forwards}}
      @keyframes fadeIn{{to{{opacity:1}}}}
      /* shutters overlay on main page */
      #left,#right{{position:fixed;top:0;height:100vh;width:50vw;background:black;z-index:9;transition:all 1.2s ease-in-out}}
      #left{{left:0}} #right{{right:0}}
      body.open #left{{left:-50vw}} body.open #right{{right:-50vw}}
    </style>

    <div class="app-bg"></div>
    <div id="left"></div><div id="right"></div>
    <div class="welcome">TỔ BẢO DƯỠNG SỐ 1</div>

    <script>
      // When main page loads, open shutters after a tiny delay to allow paint
      setTimeout(()=>{{ document.body.classList.add('open'); }}, 100);
    </script>
    """, unsafe_allow_html=True)

# ---------- flow ----------
hide_streamlit_ui()
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

if not st.session_state.intro_done:
    # Render intro component (HTML)
    html_str = build_intro_html(st.session_state.is_mobile)
    components.html(html_str, height=900, scrolling=False, key="intro_html")
    # Poll localStorage for the flag set by the intro iframe's JS
    # We'll poll for up to ~6 seconds (adjust as needed)
    found = False
    for _ in range(60):
        try:
            val = st_javascript("localStorage.getItem('cabbase_intro_done');")
        except Exception:
            val = None
        if val:
            found = True
            break
        time.sleep(0.1)
    # if found, mark done and rerun to render main page (which opens shutters)
    if found:
        st.session_state.intro_done = True
        # optional: clear the flag to avoid re-triggering later
        st_javascript("localStorage.removeItem('cabbase_intro_done');")
        st.experimental_rerun()
    else:
        # fallback: if polling timed out, go to main page anyway
        st.session_state.intro_done = True
        st.experimental_rerun()
else:
    main_page(st.session_state.is_mobile)
