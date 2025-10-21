import streamlit as st
import base64
import time
import streamlit.components.v1 as components

st.set_page_config(page_title="Tổ bảo dưỡng số 1", page_icon="✈️", layout="wide")

# ======== FILES =========
VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
AUDIO = "plane_fly.mp3"

# ======== UTILS =========
def get_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def hide_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"] {
        display: none !important;
    }
    .stApp, .block-container {
        padding: 0 !important;
        margin: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ======== INTRO =========
def intro_screen(is_mobile):
    video_src = VIDEO_MOBILE if is_mobile else VIDEO_PC
    bg_b64 = get_base64(video_src)
    audio_b64 = get_base64(AUDIO)

    html = f"""
    <html>
    <head>
    <style>
    html, body {{
        margin: 0;
        padding: 0;
        overflow: hidden;
        height: 100%;
        background: black;
    }}
    video {{
        width: 100vw;
        height: 100vh;
        object-fit: cover;
        position: absolute;
        top: 0; left: 0;
    }}
    audio {{ display: none; }}
    h1 {{
        position: absolute;
        top: 45%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
        color: white;
        font-family: 'Playfair Display', serif;
        font-size: clamp(22px, 6vw, 60px);
        text-shadow: 0 0 20px rgba(255,255,255,0.9);
        width: 90%;
        letter-spacing: 3px;
        animation: glow 6s linear infinite;
    }}
    @keyframes glow {{
        0% {{ text-shadow: 0 0 5px #fff, 0 0 10px #ffd700; }}
        50% {{ text-shadow: 0 0 20px #ffe066, 0 0 30px #fff; }}
        100% {{ text-shadow: 0 0 5px #fff, 0 0 10px #ffd700; }}
    }}
    #shatter {{
        position: absolute;
        top: 0; left: 0;
        width: 100%;
        height: 100%;
        display: grid;
        pointer-events: none;
    }}
    .shard {{
        background-repeat: no-repeat;
        background-size: cover;
        transition: transform 1s ease-out, opacity 1.5s ease-out;
    }}
    </style>
    </head>

    <body>
        <video id="vid" autoplay muted playsinline>
            <source src="data:video/mp4;base64,{bg_b64}" type="video/mp4">
        </video>
        <audio id="aud">
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>
        <h1>KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</h1>
        <div id="shatter"></div>

        <script>
        const vid = document.getElementById("vid");
        const aud = document.getElementById("aud");
        const shatter = document.getElementById("shatter");
        const ROWS = 7, COLS = 12;

        for (let r = 0; r < ROWS; r++) {{
            for (let c = 0; c < COLS; c++) {{
                const d = document.createElement('div');
                d.className = 'shard';
                shatter.appendChild(d);
            }}
        }}

        function shatterEffect() {{
            const w = window.innerWidth;
            const h = window.innerHeight;
            const canvas = document.createElement('canvas');
            canvas.width = w; canvas.height = h;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(vid, 0, 0, w, h);
            const img = canvas.toDataURL('image/png');
            const shards = Array.from(shatter.children);
            const cellW = w / COLS;
            const cellH = h / ROWS;
            shatter.style.gridTemplateColumns = `repeat(${COLS}, 1fr)`;
            shatter.style.gridTemplateRows = `repeat(${ROWS}, 1fr)`;

            shards.forEach((tile, i) => {{
                const row = Math.floor(i / COLS);
                const col = i % COLS;
                tile.style.backgroundImage = `url('${img}')`;
                tile.style.backgroundSize = `${w}px ${h}px`;
                tile.style.backgroundPosition = `-${col * cellW}px -${row * cellH}px`;
                tile.style.width = `${cellW}px`;
                tile.style.height = `${cellH}px`;
                tile.style.opacity = '1';
            }});

            shards.forEach(tile => {{
                const angle = (Math.random() - 0.5) * 2 * Math.PI;
                const dist = 150 + Math.random() * 150;
                const dx = Math.cos(angle) * dist;
                const dy = Math.sin(angle) * dist;
                const rot = (Math.random() - 0.5) * 720;
                setTimeout(() => {{
                    tile.style.transform = `translate(${dx}px, ${dy}px) rotate(${rot}deg)`;
                    tile.style.opacity = '0';
                }}, Math.random() * 300);
            }});

            setTimeout(() => {{
                window.parent.postMessage({{type: "intro_done"}}, "*");
            }}, 2200);
        }}

        vid.addEventListener("play", () => {{
            aud.volume = 0.9;
            aud.play().catch(()=>{{}});
        }});
        vid.addEventListener("ended", shatterEffect);
        </script>
    </body>
    </html>
    """
    components.html(html, height=800, scrolling=False)

# ======== MAIN =========
def main_page(is_mobile):
    bg_b64 = get_base64(BG_MOBILE if is_mobile else BG_PC)
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background:
            linear-gradient(to bottom, rgba(250,240,200,0.9), rgba(190,160,120,0.9)),
            url("data:image/jpg;base64,{bg_b64}");
        background-size: cover;
        background-position: center;
    }}
    h1 {{
        text-align: center;
        font-family: 'Georgia', serif;
        color: #2b1d0e;
        font-size: {'7vw' if is_mobile else '4vw'};
        margin-top: 4vh;
        text-shadow: 1px 1px 3px rgba(255,255,255,0.9);
        animation: fadeIn 2s ease-in-out forwards;
    }}
    @keyframes fadeIn {{
        from {{opacity: 0; transform: translateY(-20px);}}
        to {{opacity: 1; transform: translateY(0);}}
    }}
    </style>
    <h1>TỔ BẢO DƯỠNG SỐ 1</h1>
    """, unsafe_allow_html=True)

# ======== APP FLOW =========
hide_ui()

# Nhận thông điệp từ JavaScript
components.html("""
<script>
const isMobile = /android|iphone|ipad|ipod/i.test(navigator.userAgent);
window.parent.postMessage({type: "device_check", isMobile}, "*");
</script>
""", height=0)

# Nhận giá trị từ JS (Streamlit sẽ tự reload)
msg = st.experimental_get_query_params()
if "device" in msg:
    st.session_state.is_mobile = (msg["device"][0] == "1")

# Nếu chưa có device -> chèn script để set URL param
if "is_mobile" not in st.session_state:
    components.html("""
    <script>
    const isMobile = /android|iphone|ipad|ipod/i.test(navigator.userAgent);
    const url = new URL(window.location.href);
    url.searchParams.set('device', isMobile ? '1' : '0');
    window.location.replace(url);
    </script>
    """, height=0)
    st.stop()

if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

if not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
    time.sleep(9)
    st.session_state.intro_done = True
    st.rerun()
else:
    main_page(st.session_state.is_mobile)
