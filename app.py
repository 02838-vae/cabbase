import streamlit as st
import base64
import time
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components
import os

# ========== CẤU HÌNH ==========
st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
SFX = "plane_fly.mp3"

# check files exist (optional - helpful for debugging)
missing = [p for p in (VIDEO_PC, VIDEO_MOBILE, BG_PC, BG_MOBILE, SFX) if not os.path.exists(p) and p in (VIDEO_PC, VIDEO_MOBILE, BG_PC, BG_MOBILE, SFX)]
# (we won't abort; existing code will show errors if files missing)

# ========== ẨN UI STREAMLIT ==========
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

# ========== MÀN HÌNH INTRO (với Shattered Transition) ==========
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC

    if not os.path.exists(video_file):
        st.error(f"⚠️ Không tìm thấy video: {video_file}")
        st.session_state.intro_done = True
        st.rerun()
        return

    if not os.path.exists(SFX):
        st.warning("⚠️ Không tìm thấy file âm thanh SFX; tiếp tục mà không có SFX.")

    # encode video + audio
    with open(video_file, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()
    audio_b64 = ""
    if os.path.exists(SFX):
        with open(SFX, "rb") as a:
            audio_b64 = base64.b64encode(a.read()).decode()

    # Shattered effect implemented in JS:
    # - draw current video frame to canvas
    # - slice into tiles (rows x cols)
    # - create divs using canvas data URL clipped to tile positions
    # - animate tiles with translate/rotate/opacity
    # - after animation -> postMessage intro_done
    intro_html = f"""
    <!doctype html>
    <html lang="vi">
    <head>
      <meta name="viewport" content="width=device-width,initial-scale=1.0">
      <style>
        html,body{{margin:0;padding:0;height:100%;background:#000;overflow:hidden}}
        #wrapper{{position:fixed;inset:0;}}
        video{{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;z-index:1}}
        #intro-text{{position:absolute;z-index:2;left:50%;top:50%;transform:translate(-50%,-50%);width:90vw;max-width:95%;text-align:center;
            color:#f8f4e3;font-family:'Playfair Display',serif;font-weight:700;
            font-size:clamp(22px,6vw,60px);line-height:1.15;
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            background:linear-gradient(120deg,#e9dcb5 20%,#fff9e8 40%,#e9dcb5 60%);
            background-size:200%;text-shadow:0 0 15px rgba(255,255,230,0.4);
            }}
        /* mosaic container used during transition */
        #shatter-container{{position:absolute;inset:0;z-index:3;pointer-events:none;display:grid;grid-template-columns:repeat(12,1fr);grid-template-rows:repeat(7,1fr)}}
        .shard{{position:relative;overflow:hidden;background-repeat:no-repeat;background-size:100% 100%;opacity:1;transform-origin:center center}}
        /* fade overlay (if needed) */
        #fade-overlay{{position:absolute;inset:0;background:#000;opacity:0;z-index:4;pointer-events:none;transition:opacity .9s ease}}
      </style>
    </head>
    <body>
      <div id="wrapper">
        <video id="introVid" autoplay muted playsinline preload="auto">
          <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>

        {"<audio id='flySfx'><source src='data:audio/mp3;base64," + audio_b64 + "' type='audio/mp3'></audio>" if audio_b64 else ""}

        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="shatter-container" aria-hidden="true"></div>
        <div id="fade-overlay"></div>
      </div>

      <script>
      (function() {{
        const vid = document.getElementById('introVid');
        const sfx = document.getElementById('flySfx');
        const shatter = document.getElementById('shatter-container');
        const fade = document.getElementById('fade-overlay');
        let triggered = false;

        // attempt to play sfx when video plays
        vid.addEventListener('play', () => {{
            if(sfx){{ sfx.currentTime = 0; sfx.volume = 0.9; sfx.play().catch(e => console.log('SFX blocked', e)); }}
        }});

        // utility: wait for next animation frame + small delay
        function wait(ms) {{
            return new Promise(res => setTimeout(res, ms));
        }}

        // create shards grid but keep hidden initially
        const ROWS = 7;
        const COLS = 12;

        // create child divs (shards)
        for(let r=0;r<ROWS;r++) {{
            for(let c=0;c<COLS;c++) {{
                const d = document.createElement('div');
                d.className = 'shard';
                // set grid position by CSS grid auto-placement (order) - each cell will be sized by grid
                shatter.appendChild(d);
            }}
        }}

        // draw current frame to canvas and set shard backgrounds
        async function captureAndShatter() {{
            try {{
                // create canvas sized to video displayed size
                const vw = vid.videoWidth;
                const vh = vid.videoHeight;

                // compute displayed size
                const rect = vid.getBoundingClientRect();
                const displayW = rect.width;
                const displayH = rect.height;

                // create an offscreen canvas sized to display size
                const canvas = document.createElement('canvas');
                canvas.width = displayW;
                canvas.height = displayH;
                const ctx = canvas.getContext('2d');

                // draw current frame onto canvas scaled to display size
                ctx.drawImage(vid, 0, 0, displayW, displayH);

                // get data URL of full frame
                const dataURL = canvas.toDataURL('image/png');

                // set each shard background to the full dataURL but adjust background-position so it shows portion
                const shards = Array.from(shatter.children);
                const cellW = displayW / {COLS};
                const cellH = displayH / {ROWS};

                // force shatter grid template size to match display size
                shatter.style.gridTemplateColumns = `repeat({{cols}}, 1fr)`.replace('{{cols}}', {COLS});
                shatter.style.gridTemplateRows = `repeat({{rows}}, 1fr)`.replace('{{rows}}', {ROWS});

                shards.forEach((tile, idx) => {{
                    const row = Math.floor(idx / {COLS});
                    const col = idx % {COLS};
                    // background-size should match video display size so portion is correct
                    tile.style.backgroundImage = `url('${{dataURL}}')`;
                    tile.style.backgroundSize = `${{displayW}}px ${{displayH}}px`;
                    tile.style.backgroundPosition = `-${{Math.round(col * cellW)}}px -${{Math.round(row * cellH)}}px`;
                    tile.style.width = `${{cellW}}px`;
                    tile.style.height = `${{cellH}}px`;
                    tile.style.opacity = '0';
                }});

                // reveal shards and animate them in a "shatter outward" pattern
                // randomize order for organic effect
                const order = shards.map((s,i)=>i).sort(()=>Math.random()-0.5);

                // small delay to ensure UI paints
                await wait(40);

                // fade in shards quickly (so they replace the video)
                shards.forEach((tile, i) => {{
                    setTimeout(() => {{
                        tile.style.transition = 'opacity 180ms linear';
                        tile.style.opacity = '1';
                    }}, i * 8);
                }});

                // pause video to freeze frame behind shards
                try {{ vid.pause(); }} catch(e){{console.log(e)}}

                // after short delay, animate shards outward
                await wait(220);

                order.forEach((idx, i) => {{
                    const tile = shards[idx];
                    // compute center of tile relative to center of screen for direction
                    const rectTile = tile.getBoundingClientRect();
                    const centerX = rectTile.left + rectTile.width/2 - window.innerWidth/2;
                    const centerY = rectTile.top + rectTile.height/2 - window.innerHeight/2;
                    // direction vector
                    const dirX = centerX / (window.innerWidth/2) || (Math.random()-0.5);
                    const dirY = centerY / (window.innerHeight/2) || (Math.random()-0.5);
                    const magnitude = 60 + Math.random()*260; // px
                    const rotate = (Math.random()-0.5)*60; // deg
                    const delay = i * 12; // stagger
                    tile.style.transition = `transform 900ms cubic-bezier(.2,.8,.2,1) ${delay}ms, opacity 700ms linear ${delay}ms`;
                    tile.style.transform = `translate(${{dirX * magnitude}}px, ${{dirY * magnitude}}px) rotate(${{rotate}}deg) scale(1.05)`;
                    tile.style.opacity = '0';
                }});

                // fade overlay to smooth transition to main page
                setTimeout(()=>{{ fade.style.opacity = '1'; }}, 900);

                // after animation ends, signal Streamlit to switch
                setTimeout(() => {{ window.parent.postMessage({{type:'intro_done'}}, '*'); }}, 1300);

            }} catch (err) {{
                console.error('Shatter failed', err);
                // fallback: just finish
                window.parent.postMessage({{type:'intro_done'}}, '*');
            }}
        }}

        // trigger shatter when near end
        vid.addEventListener('timeupdate', () => {{
            if(vid.duration && (vid.duration - vid.currentTime <= 1.2) && !triggered) {{
                triggered = true;
                captureAndShatter();
            }}
        }});

        // also guard if ended event fires
        vid.addEventListener('ended', () => {{
            if(!triggered) {{
                triggered = true;
                // small timeout to allow last frame to be available
                setTimeout(captureAndShatter, 60);
            }}
        }});

        // safety: if no 'timeupdate' due to autoplay block, fallback timer
        setTimeout(()=>{{ if(!triggered && !vid.paused) {{ /* nothing */ }} }}, 10000);

      }})();
      </script>
    </body>
    </html>
    """

    # embed iframe-like HTML (components.html)
    components.html(intro_html, height=800, scrolling=False)

# ========== TRANG CHÍNH ==========
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    if not os.path.exists(bg):
        st.error(f"⚠️ Không tìm thấy ảnh nền: {bg}")
        bg_b64 = ""
    else:
        with open(bg, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    html, body, .stApp {{
        height: 100vh !important;
        background:
            linear-gradient(to bottom, rgba(255, 240, 210, 0.2) 0%, rgba(180, 140, 90, 0.3) 50%, rgba(90, 70, 50, 0.35) 100%),
            url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed !important;
        background-size: cover !important;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
        position: relative;
        filter: brightness(1.05) contrast(1.05) saturate(1.05);
        animation: fadeInBg 1.0s ease-in-out forwards;
    }}
    @keyframes fadeInBg {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}

    .welcome {{
        position: absolute;
        top: 7%;
        width: 100%;
        text-align: center;
        font-size: clamp(30px, 5vw, 65px);
        color: #fff5d7;
        font-family: 'Playfair Display', serif;
        text-shadow: 0 0 18px rgba(0,0,0,0.65), 0 0 30px rgba(255,255,180,0.25);
        background: linear-gradient(120deg, #f3e6b4 20%, #fff7d6 40%, #f3e6b4 60%);
        background-size: 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 2px;
        z-index: 3;
    }}
    </style>

    <div class="welcome">TỔ BẢO DƯỠNG SỐ 1</div>
    """, unsafe_allow_html=True)

# ========== LUỒNG CHÍNH ==========
hide_streamlit_ui()
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

if not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
    # listen for message from iframe/html to reload
    st.markdown("""
    <script>
    window.addEventListener("message", (event) => {
        if (event.data && event.data.type === "intro_done") {
            // reload to switch to main page
            window.parent.location.reload();
        }
    });
    </script>
    """, unsafe_allow_html=True)
    # safety fallback: after 10s mark intro_done
    time.sleep(9.5)
    st.session_state.intro_done = True
    st.rerun()
else:
    main_page(st.session_state.is_mobile)
