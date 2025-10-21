import streamlit as st
import base64
import time

st.set_page_config(page_title="Tổ bảo dưỡng số 1", page_icon="✈️", layout="wide")

# Detect device type (simple UA-based)
ua = st.query_params.get("ua", [""])[0] if "ua" in st.query_params else ""
if not ua:
    ua = st.runtime.media_file_storage._get_client_metadata().get("User-Agent", "")

is_mobile = any(x in ua.lower() for x in ["iphone", "android", "mobile"])
st.session_state.is_mobile = is_mobile

# Select media based on device
VIDEO_FILE = "mobile.mp4" if is_mobile else "airplane.mp4"
BACKGROUND_IMG = "mobile.jpg" if is_mobile else "cabbase.jpg"
AUDIO_FILE = "plane_fly.mp3"

# Convert background to base64
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_b64 = get_base64(BACKGROUND_IMG)

# ----------------------- INTRO SCREEN -----------------------
def intro_screen():
    intro_html = f"""
    <style>
    html, body {{
        margin: 0;
        padding: 0;
        overflow: hidden;
        height: 100%;
        background: #000;
    }}
    video {{
        width: 100vw;
        height: 100vh;
        object-fit: cover;
        display: block;
    }}
    .overlay {{
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
    }}
    h1 {{
        font-family: 'Courier New', monospace;
        font-size: { '5vw' if is_mobile else '3vw' };
        color: white;
        text-align: center;
        text-shadow: 3px 3px 8px rgba(0,0,0,0.8);
        letter-spacing: 3px;
        width: 100%;
        white-space: normal;
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

    <video id="vid" playsinline>
        <source src="data:video/mp4;base64,{get_base64(VIDEO_FILE)}" type="video/mp4">
    </video>

    <audio id="aud" autoplay>
        <source src="data:audio/mp3;base64,{get_base64(AUDIO_FILE)}" type="audio/mp3">
    </audio>

    <div class="overlay">
        <h1>✈️ Chào mừng đến với Tổ bảo dưỡng số 1 ✈️</h1>
    </div>

    <div id="shatter"></div>

    <script>
    const vid = document.getElementById("vid");
    const aud = document.getElementById("aud");
    const shatter = document.getElementById("shatter");

    const ROWS = 7;
    const COLS = 12;

    // Tạo ô lưới mảnh
    for (let r = 0; r < ROWS; r++) {{
        for (let c = 0; c < COLS; c++) {{
            const d = document.createElement('div');
            d.className = 'shard';
            shatter.appendChild(d);
        }}
    }}

    function captureAndShatter() {{
        const displayW = window.innerWidth;
        const displayH = window.innerHeight;

        const canvas = document.createElement('canvas');
        canvas.width = displayW;
        canvas.height = displayH;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(vid, 0, 0, displayW, displayH);
        const dataURL = canvas.toDataURL('image/png');

        const shards = Array.from(shatter.children);
        const cellW = displayW / 12;
        const cellH = displayH / 7;

        shatter.style.gridTemplateColumns = `repeat(12, 1fr)`;
        shatter.style.gridTemplateRows = `repeat(7, 1fr)`;

        shards.forEach((tile, idx) => {{
            const row = Math.floor(idx / 12);
            const col = idx % 12;
            tile.style.backgroundImage = `url('${dataURL}')`;
            tile.style.backgroundSize = `${displayW}px ${displayH}px`;
            tile.style.backgroundPosition = `-${Math.round(col * cellW)}px -${Math.round(row * cellH)}px`;
            tile.style.width = `${cellW}px`;
            tile.style.height = `${cellH}px`;
            tile.style.opacity = '1';
        }});

        // Vỡ mảnh
        shards.forEach(tile => {{
            const angle = (Math.random() - 0.5) * 2 * Math.PI;
            const dist = 200 + Math.random() * 200;
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
        }}, 1800);
    }}

    vid.addEventListener("play", () => {{
        aud.volume = 0.9;
        aud.play().catch(()=>{{}});
    }});

    vid.addEventListener("ended", captureAndShatter);
    vid.play().catch(()=>{{console.log("Autoplay blocked")}})
    </script>
    """

    st.markdown(intro_html, unsafe_allow_html=True)


# ----------------------- MAIN PAGE -----------------------
def main_page():
    page_html = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background: linear-gradient(to bottom, rgba(240,230,200,0.95), rgba(190,160,120,0.95)),
                    url("data:image/jpg;base64,{bg_b64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    h1 {{
        text-align: center;
        font-family: 'Georgia', serif;
        color: #2b1d0e;
        text-shadow: 1px 1px 3px rgba(255,255,255,0.8);
        font-size: { '8vw' if is_mobile else '4vw' };
        margin-top: 4vh;
    }}
    </style>
    <h1>Tổ bảo dưỡng số 1</h1>
    """
    st.markdown(page_html, unsafe_allow_html=True)


# ----------------------- RUN APP -----------------------
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

if not st.session_state.intro_done:
    intro_screen()
    st.markdown(
        """
        <script>
        window.addEventListener("message", (e) => {
            if (e.data && e.data.type === "intro_done") {
                window.parent.location.reload();
            }
        });
        </script>
        """,
        unsafe_allow_html=True,
    )
else:
    main_page()
