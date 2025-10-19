# app.py — Full working: overlay video (top text) via st_javascript, then transition to main page
import streamlit as st
import os, base64, random
from streamlit_javascript import st_javascript
from user_agents import parse
import time

st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

# --- File paths (đảm bảo tồn tại) ---
VIDEO_PC = "media/airplane.mp4"
VIDEO_MOBILE = "media/mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
MUSIC_FILES = ["background.mp3", "background2.mp3", "background3.mp3", "background4.mp3", "background5.mp3"]

# --- Session state ---
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = None

# --- Detect device via st_javascript (top-level) ---
if st.session_state.is_mobile is None:
    ua = st_javascript("window.navigator.userAgent;")
    if ua:
        st.session_state.is_mobile = not parse(ua).is_pc
        st.rerun()
    else:
        st.stop()

# --- Helper: encode video to base64 (choose file per device) ---
def video_base64_for_device(is_mobile: bool):
    path = VIDEO_MOBILE if is_mobile else VIDEO_PC
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return b64

# --- Hide streamlit UI chrome and make app full viewport ---
def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live] {display:none !important;}
    .stApp, .main, .block-container { padding:0 !important; margin:0 !important; width:100vw !important; min-height:100vh !important; }
    </style>
    """, unsafe_allow_html=True)

# --- Intro overlay implemented in top-level JS via st_javascript ---
def run_intro_overlay(is_mobile: bool):
    b64 = video_base64_for_device(is_mobile)
    if not b64:
        st.error(f"Không tìm thấy video cho {'mobile' if is_mobile else 'PC'}")
        st.session_state.intro_done = True
        st.rerun()
        return

    # text position: show at top of screen (user requested)
    # On mobile we place slightly lower to avoid browser UI, but still top area.
    text_top_pct = "6%" if is_mobile else "6%"

    # Build JS with embedded data-uri (note: large string). Promise resolves when video ended (or fallback).
    js = f"""
    (async () => {{
      // remove any previous overlay if exists (safety)
      try {{ let prev = document.getElementById('st_intro_overlay'); if (prev) prev.remove(); }} catch(e){{}}

      const overlay = document.createElement('div');
      overlay.id = 'st_intro_overlay';
      overlay.style.position = 'fixed';
      overlay.style.top = '0';
      overlay.style.left = '0';
      overlay.style.width = '100vw';
      overlay.style.height = '100vh';
      overlay.style.zIndex = '9999999';
      overlay.style.background = 'black';
      overlay.style.display = 'flex';
      overlay.style.alignItems = 'center';
      overlay.style.justifyContent = 'center';
      overlay.style.overflow = 'hidden';
      overlay.style.pointerEvents = 'none';

      // video element
      const vid = document.createElement('video');
      vid.id = 'intro_video_element';
      vid.setAttribute('playsinline', '');
      vid.setAttribute('webkit-playsinline', '');
      vid.autoplay = true;
      vid.muted = true;
      vid.loop = false;
      vid.style.width = '100%';
      vid.style.height = '100%';
      vid.style.objectFit = 'cover';
      vid.style.objectPosition = 'center';
      vid.style.display = 'block';
      vid.style.pointerEvents = 'none';
      vid.src = 'data:video/mp4;base64,{b64}';

      // text overlay at top
      const txt = document.createElement('div');
      txt.id = 'intro_text_overlay';
      txt.innerText = 'KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI';
      txt.style.position = 'fixed';
      txt.style.top = '{text_top_pct}';
      txt.style.left = '50%';
      txt.style.transform = 'translateX(-50%)';
      txt.style.zIndex = '10000000';
      txt.style.pointerEvents = 'none';
      txt.style.fontFamily = "Cinzel, 'Cinzel Decorative', serif, serif";
      txt.style.fontWeight = '700';
      txt.style.fontSize = 'clamp(16px, 4.5vw, 36px)';
      txt.style.color = 'white';
      txt.style.textShadow = '0 0 14px rgba(255,255,255,0.85), 0 0 30px rgba(255,215,0,0.6)';
      txt.style.opacity = '0';
      txt.style.whiteSpace = 'nowrap';
      txt.style.transition = 'opacity 0.9s ease';

      // fade overlay div to black when finishing
      const fadeDiv = document.createElement('div');
      fadeDiv.id = 'intro_fade_div';
      fadeDiv.style.position = 'fixed';
      fadeDiv.style.top = '0'; fadeDiv.style.left = '0';
      fadeDiv.style.width = '100vw'; fadeDiv.style.height = '100vh';
      fadeDiv.style.zIndex = '99999998';
      fadeDiv.style.background = 'black';
      fadeDiv.style.opacity = '0';
      fadeDiv.style.transition = 'opacity 1.2s ease-in-out';
      fadeDiv.style.pointerEvents = 'none';

      overlay.appendChild(vid);
      document.body.appendChild(overlay);
      document.body.appendChild(txt);
      document.body.appendChild(fadeDiv);

      // ensure controls off and autoplay attempt
      try {{
        await vid.play();
      }} catch(e) {{
        // if autoplay blocked, try unmuting later or allow user interaction -- fallback will handle
        console.warn('Autoplay may be blocked:', e);
      }}

      // text fade-in slightly after start (so user sees)
      setTimeout(()=>{{ txt.style.opacity = '1'; }}, 400);

      // On mobile adjust objectPosition to show aircraft higher (improve visibility)
      if ({'true' if is_mobile else 'false'}) {{
        vid.style.objectPosition = 'center 20%';
      }} else {{
        vid.style.objectPosition = 'center';
      }}

      // When video near end (<=1s) trigger fade
      let endedFlag = false;
      vid.addEventListener('timeupdate', () => {{
        try {{
          if (!isFinite(vid.duration)) return;
          if ((vid.duration - vid.currentTime) <= 1.0 && !endedFlag) {{
            endedFlag = true;
            fadeDiv.style.opacity = '1';
            txt.style.opacity = '0';
          }}
        }} catch(e){{console.warn(e)}}
      }});

      // On ended, cleanup overlay and resolve
      vid.addEventListener('ended', () => {{
        // small delay to allow fade
        setTimeout(() => {{
          try {{
            // remove overlay elements
            const el = document.getElementById('st_intro_overlay');
            if (el) el.remove();
            const t = document.getElementById('intro_text_overlay');
            if (t) t.remove();
            const f = document.getElementById('intro_fade_div');
            if (f) f.remove();
          }} catch(e){{console.warn(e)}}
          // resolve promise => Python continues
          resolvePromise(true);
        }}, 700);
      }});

      // Fallback: if video can't play or hangs, resolve after 18s
      const fallbackTimer = setTimeout(() => {{
        try {{
          const el = document.getElementById('st_intro_overlay'); if (el) el.remove();
          const t = document.getElementById('intro_text_overlay'); if (t) t.remove();
          const f = document.getElementById('intro_fade_div'); if (f) f.remove();
        }} catch(e){{console.warn(e)}}
        resolvePromise(false);
      }}, 18000);

      // We'll implement resolvePromise by attaching it to window for st_javascript to await
      function resolvePromise(val) {{
        if (window._st_intro_resolved) return;
        window._st_intro_resolved = true;
        clearTimeout(fallbackTimer);
        // small delay to ensure DOM cleaned
        setTimeout(()=>{{ window._st_intro_result = val; }}, 10);
      }}

      // Wait loop: poll until window._st_intro_result set (by ended or fallback)
      while (typeof window._st_intro_result === 'undefined') {{
        await new Promise(r => setTimeout(r, 150));
      }}
      return window._st_intro_result;
    }})();
    """

    # st_javascript will await the promise returned by the async IIFE
    res = st_javascript(js)
    # res is True if video ended normally, False if fallback
    if res:
        st.session_state.intro_done = True
        # short pause to ensure any fade animations finish visually
        time.sleep(0.2)
        st.rerun()
    else:
        # fallback: still move on to main page
        st.session_state.intro_done = True
        time.sleep(0.2)
        st.rerun()


# --- Main page renderer ---
def main_page(is_mobile: bool):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    if not os.path.exists(bg):
        st.error(f"Ảnh nền không tìm thấy: {bg}")
        bg_b64 = ""
    else:
        with open(bg, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode("ascii")

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&display=swap');
    .stApp {{
        background-image: url("data:image/jpeg;base64,{bg_b64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        animation: fadeInMain 1s ease-in-out forwards;
    }}
    @keyframes fadeInMain {{ from {{opacity:0}} to {{opacity:1}} }}
    h1 {{ text-align:center; margin-top:60px; color:#2E1C14; text-shadow:2px 2px 6px #FFF8DC; font-family:'Playfair Display', serif; }}
    </style>
    """, unsafe_allow_html=True)

    # sidebar audio
    avail = [m for m in MUSIC_FILES if os.path.exists(m)]
    if avail:
        chosen = random.choice(avail)
        with st.sidebar:
            st.subheader("🎵 Nhạc nền")
            st.audio(chosen, start_time=0)
            st.caption(f"Đang phát: {os.path.basename(chosen)}")

    st.markdown("<h1>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)


# ====== FLOW ======
hide_streamlit_ui()
if not st.session_state.intro_done:
    run_intro_overlay(st.session_state.is_mobile)
else:
    main_page(st.session_state.is_mobile)
