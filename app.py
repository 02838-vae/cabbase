# app.py — FINAL: video từ file, text top, fade chuyển cảnh chuẩn
import streamlit as st
import os, base64, random
from streamlit_javascript import st_javascript
from user_agents import parse
import time

st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

# --- File cấu hình ---
VIDEO_PC = "media/airplane.mp4"
VIDEO_MOBILE = "media/mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
MUSIC_FILES = ["background.mp3", "background2.mp3", "background3.mp3", "background4.mp3", "background5.mp3"]

# --- State ---
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = None

# --- Xác định thiết bị ---
if st.session_state.is_mobile is None:
    ua = st_javascript("window.navigator.userAgent;")
    if ua:
        st.session_state.is_mobile = not parse(ua).is_pc
        st.rerun()
    else:
        st.stop()

# --- Ẩn giao diện Streamlit ---
def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live] {display:none !important;}
    .stApp, .main, .block-container {padding:0 !important; margin:0 !important; width:100vw !important; min-height:100vh !important;}
    </style>
    """, unsafe_allow_html=True)


# --- Màn hình Intro (video + text + fade chuyển cảnh) ---
def run_intro_overlay(is_mobile: bool):
    video_path = VIDEO_MOBILE if is_mobile else VIDEO_PC
    if not os.path.exists(video_path):
        st.error(f"Không tìm thấy video: {video_path}")
        st.session_state.intro_done = True
        st.rerun()
        return

    # Xây link tuyệt đối để Chrome có thể preload video
    video_url = f"/{video_path}"

    # Dòng chữ top-screen
    text_top = "6%" if is_mobile else "5%"

    js = f"""
    (async () => {{
      // Xóa overlay cũ nếu có
      const old = document.getElementById("intro_overlay");
      if (old) old.remove();

      const overlay = document.createElement("div");
      overlay.id = "intro_overlay";
      overlay.style.cssText = `
        position:fixed;top:0;left:0;width:100vw;height:100vh;
        background:black;z-index:999999;overflow:hidden;
      `;

      // Video element
      const vid = document.createElement("video");
      vid.src = "{video_url}";
      vid.autoplay = true;
      vid.muted = true;
      vid.playsInline = true;
      vid.style.cssText = `
        width:100%;height:100%;
        object-fit:cover;
        object-position:{'center 15%' if is_mobile else 'center'};
        display:block;
      `;

      // Text overlay
      const txt = document.createElement("div");
      txt.innerText = "KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI";
      txt.style.cssText = `
        position:fixed;top:{text_top};left:50%;transform:translateX(-50%);
        font-family:'Cinzel Decorative', 'Cinzel', serif;
        font-weight:700;
        font-size:clamp(18px,4vw,36px);
        color:white;text-shadow:0 0 18px rgba(255,255,255,0.9),0 0 35px rgba(255,215,0,0.6);
        opacity:0;
        z-index:1000000;
        transition:opacity 1.5s ease;
        white-space:nowrap;
      `;

      // Fade div (for transition)
      const fade = document.createElement("div");
      fade.style.cssText = `
        position:fixed;top:0;left:0;width:100%;height:100%;
        background:black;opacity:0;transition:opacity 1.5s ease;
        z-index:1000001;
      `;

      overlay.appendChild(vid);
      document.body.appendChild(overlay);
      document.body.appendChild(txt);
      document.body.appendChild(fade);

      // Hiệu ứng fade-in chữ
      setTimeout(()=>{{ txt.style.opacity = 1; }}, 600);

      // Bắt đầu phát
      try {{
        await vid.play();
      }} catch(e) {{
        console.warn("Autoplay bị chặn:", e);
      }}

      // Khi video sắp hết → fade-out
      let faded = false;
      vid.addEventListener("timeupdate", () => {{
        if (vid.duration && vid.duration - vid.currentTime < 1.2 && !faded) {{
          faded = true;
          fade.style.opacity = 1;
          txt.style.opacity = 0;
        }}
      }});

      // Khi video kết thúc
      return await new Promise(resolve => {{
        vid.addEventListener("ended", () => {{
          setTimeout(() => {{
            overlay.remove(); txt.remove(); fade.remove();
            resolve(true);
          }}, 800);
        }});

        // fallback nếu video lỗi hoặc autoplay bị block
        setTimeout(() => {{
          try {{ overlay.remove(); txt.remove(); fade.remove(); }} catch(e){{}}
          resolve(true);
        }}, 25000);
      }});
    }})();
    """

    res = st_javascript(js)
    if res:
        st.session_state.intro_done = True
        st.rerun()


# --- Trang chính ---
def main_page(is_mobile: bool):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    try:
        with open(bg, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()
    except:
        bg_b64 = ""

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&display=swap');
    .stApp {{
        background-image: url("data:image/jpeg;base64,{bg_b64}");
        background-size: cover;
        background-position: center;
        animation: fadeInMain 1s ease forwards;
    }}
    @keyframes fadeInMain {{ from {{opacity:0}} to {{opacity:1}} }}
    h1 {{
        text-align:center; margin-top:60px; color:#2E1C14;
        text-shadow:2px 2px 6px #FFF8DC;
        font-family:'Playfair Display', serif;
    }}
    </style>
    """, unsafe_allow_html=True)

    avail = [m for m in MUSIC_FILES if os.path.exists(m)]
    if avail:
        chosen = random.choice(avail)
        with st.sidebar:
            st.subheader("🎵 Nhạc nền")
            st.audio(chosen, start_time=0)
            st.caption(f"Đang phát: {os.path.basename(chosen)}")

    st.markdown("<h1>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)


# --- Luồng chính ---
hide_streamlit_ui()
if not st.session_state.intro_done:
    run_intro_overlay(st.session_state.is_mobile)
else:
    main_page(st.session_state.is_mobile)
