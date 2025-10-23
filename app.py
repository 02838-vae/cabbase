import streamlit as st
import base64

# ========== CẤU HÌNH TRANG ==========
st.set_page_config(page_title="Cinematic Intro", page_icon="🎬", layout="wide")

# ========== NỘI DUNG TRANG CHÍNH ==========
def main_page():
    bg_file = "your_background.jpg"  # thay bằng ảnh nền chính của bạn
    with open(bg_file, "rb") as f:
        bg_b64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    html, body, .stApp {{
        height: 100vh !important;
        background: 
            linear-gradient(to bottom, rgba(255, 235, 200, 0.25) 0%, rgba(160, 130, 90, 0.35) 50%, rgba(90, 70, 50, 0.5) 100%),
            url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed !important;
        background-size: cover !important;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
        position: relative;
        filter: brightness(1.05) contrast(1.1) saturate(1.05);
        animation: cinematicReveal 1.8s ease-out forwards;
        transform-origin: center;
    }}
    @keyframes cinematicReveal {{
        0% {{ opacity: 0; transform: scale(1.03); filter: blur(6px); }}
        100% {{ opacity: 1; transform: scale(1.0); filter: blur(0px); }}
    }}

    .stApp::after {{
        content: "";
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: radial-gradient(circle, rgba(0,0,0,0) 60%, rgba(0,0,0,0.35) 100%);
        pointer-events: none;
        z-index: 2;
    }}

    .welcome {{
        position: absolute;
        top: 8%;
        width: 100%;
        text-align: center;
        font-size: clamp(35px, 5vw, 70px);
        color: #fff5d7;
        font-family: 'Playfair Display', serif;
        text-shadow: 0 0 18px rgba(0,0,0,0.65), 0 0 30px rgba(255,255,180,0.25);
        background: linear-gradient(120deg, #f3e6b4 20%, #fff7d6 40%, #f3e6b4 60%);
        background-size: 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: textLight 10s linear infinite, fadeIn 2s ease-out forwards; 
        letter-spacing: 2px;
        z-index: 3;
    }}
    @keyframes textLight {{
        0% {{ background-position: 200% 0%; }}
        100% {{ background-position: -200% 0%; }}
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(15px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    </style>

    <div class="welcome">TỔ BẢO DƯỠNG SỐ 1</div>
    """, unsafe_allow_html=True)

# ========== GIAO DIỆN INTRO ==========
def intro_page():
    video_path = "airplane.mp4"  # video bạn muốn chạy

    with open(video_path, "rb") as f:
        video_bytes = f.read()
    video_b64 = base64.b64encode(video_bytes).decode()

    st.markdown(f"""
    <style>
    body, html, .stApp {{
        margin: 0; padding: 0;
        background-color: black !important;
        overflow: hidden;
        height: 100vh;
    }}
    .video-container {{
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        overflow: hidden;
        background-color: black;
        display: flex;
        justify-content: center;
        align-items: center;
    }}
    video {{
        width: 100%;
        height: 100%;
        object-fit: cover;
    }}
    .fragment {{
        position: absolute;
        width: 20vw; height: 20vh;
        background: black;
        opacity: 0;
        transition: transform 1s ease-out, opacity 1s ease-out;
    }}
    .black-fade {{
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: black;
        opacity: 0;
        transition: opacity 1s ease-in-out;
        z-index: 10;
    }}
    </style>

    <div class="video-container">
        <video id="introVideo" autoplay muted playsinline>
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        <div id="fragments"></div>
        <div class="black-fade"></div>
    </div>

    <script>
    const video = document.getElementById('introVideo');
    const fragments = document.getElementById('fragments');
    const blackFade = document.querySelector('.black-fade');
    const rows = 4, cols = 8;
    const SHATTER_DELAY = 1000;       // sau 1s tan vỡ
    const SHATTER_DURATION = 1200;    // tan vỡ trong 1.2s
    const FADE_DELAY = 1000;          // màn đen 1s trước khi vào trang chính

    // Tạo các mảnh
    for (let r = 0; r < rows; r++) {{
        for (let c = 0; c < cols; c++) {{
            const frag = document.createElement('div');
            frag.classList.add('fragment');
            frag.style.top = (r * 25) + 'vh';
            frag.style.left = (c * 12.5) + 'vw';
            frag.style.width = '12.5vw';
            frag.style.height = '25vh';
            fragments.appendChild(frag);
        }}
    }}

    video.addEventListener('ended', () => {{
        setTimeout(() => {{
            // Tan vỡ
            document.querySelectorAll('.fragment').forEach(frag => {{
                frag.style.opacity = 1;
                const angle = Math.random() * 2 * Math.PI;
                const distance = 200 + Math.random() * 300;
                frag.style.transform = `translate(${{Math.cos(angle) * distance}}px, ${{Math.sin(angle) * distance}}px) rotate(${{Math.random() * 720 - 360}}deg)`;
            }});
        }}, SHATTER_DELAY);

        // Sau tan vỡ → fade đen mượt
        setTimeout(() => {{
            blackFade.style.opacity = 1;
            setTimeout(() => {{
                window.parent.postMessage({{ type: 'intro_done' }}, '*');
            }}, FADE_DELAY);
        }}, SHATTER_DELAY + SHATTER_DURATION);
    }});
    </script>
    """, unsafe_allow_html=True)

# ========== MAIN APP ==========
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

intro_placeholder = st.empty()

if not st.session_state.intro_done:
    intro_page()

    # Nhận tín hiệu từ JS
    st.markdown("""
    <script>
    window.addEventListener('message', (event) => {
        if (event.data.type === 'intro_done') {
            window.parent.location.reload();
            window.parent.postMessage({ type: 'intro_done' }, '*');
        }
    });
    </script>
    """, unsafe_allow_html=True)
else:
    main_page()
