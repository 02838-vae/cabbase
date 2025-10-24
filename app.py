import streamlit as st
import base64
import time
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

# ================== CẤU HÌNH ==================
VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
SFX = "plane_fly.mp3"

SHUTTER_PC = "airplane_shutter.jpg"
SHUTTER_MOBILE = "mobile_shutter.jpg"

BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"

st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

GRID_SIZE = 8
SHATTER_DURATION = 1.8  # giây
FADE_TO_BLACK_DELAY = 600  # ms giữa tan vỡ và màn đen
MAIN_FADE_IN_DURATION = 1800  # ms hiệu ứng hiện background

# ================== ẨN UI STREAMLIT ==================
def hide_streamlit_ui():
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


# ================== MÀN INTRO ==================
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    shutter_file = SHUTTER_MOBILE if is_mobile else SHUTTER_PC
    bg_file = BG_MOBILE if is_mobile else BG_PC

    try:
        with open(video_file, "rb") as f:
            video_b64 = base64.b64encode(f.read()).decode()
        with open(SFX, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode()
        with open(shutter_file, "rb") as f:
            shutter_b64 = base64.b64encode(f.read()).decode()
        with open(bg_file, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError as e:
        st.error(f"Không tìm thấy file: {e.filename}")
        st.stop()

    shards_html = "".join([f"<div class='shard' id='shard-{i}'></div>" for i in range(GRID_SIZE * GRID_SIZE)])

    # HTML và JS
    intro_html = f"""
    <html>
    <head>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <style>
    html, body {{
        margin:0; padding:0; overflow:hidden; background:black; height:100%;
    }}
    video {{
        position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover;
    }}
    #intro-text {{
        position:absolute; top:8%; left:50%; transform:translateX(-50%);
        width:90vw; text-align:center; color:#f8f4e3;
        font-size:clamp(22px,6vw,60px); font-weight:bold; font-family:'Playfair Display',serif;
        background:linear-gradient(120deg,#e9dcb5 20%,#fff9e8 40%,#e9dcb5 60%);
        background-size:200%; -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        text-shadow:0 0 15px rgba(255,255,230,0.4);
        animation:lightSweep 6s linear infinite, fadeInOut 6s ease-in-out forwards;
        z-index:10;
    }}
    @keyframes lightSweep {{
        0% {{background-position:200% 0%;}}
        100% {{background-position:-200% 0%;}}
    }}
    @keyframes fadeInOut {{
        0%{{opacity:0;}} 20%{{opacity:1;}} 80%{{opacity:1;}} 100%{{opacity:0;}}
    }}

    #shatter-overlay {{
        position:absolute; top:0; left:0; width:100%; height:100%;
        display:grid; grid-template-columns:repeat({GRID_SIZE},1fr);
        grid-template-rows:repeat({GRID_SIZE},1fr);
        opacity:0; pointer-events:none; z-index:30;
    }}
    .shard {{
        background-image:url("data:image/jpeg;base64,{shutter_b64}");
        background-size:100vw 100vh; opacity:1;
        transition:transform {SHATTER_DURATION}s cubic-bezier(0.68,-0.55,0.27,1.55), opacity 1.5s ease-in-out;
    }}
    #black-fade {{
        position:absolute; top:0; left:0; width:100%; height:100%;
        background:black; opacity:1; z-index:40; transition:opacity 1s ease-in-out;
    }}
    </style>
    </head>
    <body>
        <video id='vid' autoplay muted playsinline>
            <source src='data:video/mp4;base64,{video_b64}' type='video/mp4'>
        </video>
        <audio id='sfx'><source src='data:audio/mp3;base64,{audio_b64}' type='audio/mp3'></audio>
        <div id='intro-text'>KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id='shatter-overlay'>{shards_html}</div>
        <div id='black-fade'></div>

        <script>
        const GRID_SIZE = {GRID_SIZE};
        const SHATTER_DURATION = {int(SHATTER_DURATION*1000)};
        const FADE_TO_BLACK_DELAY = {FADE_TO_BLACK_DELAY};
        const MAIN_FADE_IN_DURATION = {MAIN_FADE_IN_DURATION};

        const vid = document.getElementById('vid');
        const sfx = document.getElementById('sfx');
        const overlay = document.getElementById('shatter-overlay');
        const shards = document.querySelectorAll('.shard');
        const blackFade = document.getElementById('black-fade');
        let ended = false;

        shards.forEach((s,i)=>{
            const row=Math.floor(i/GRID_SIZE);
            const col=i%GRID_SIZE;
            s.style.backgroundPosition=`calc(-${{col}} * 100vw / ${{GRID_SIZE}}) calc(-${{row}} * 100vh / ${{GRID_SIZE}})`;
        });

        function startAudio() {{
            sfx.volume=1;
            sfx.play().catch(()=>{});
        }}

        function finishIntro(){{
            if(ended)return; ended=true;

            overlay.style.opacity=1;
            shards.forEach(s=>{
                const tx=(Math.random()-0.5)*200;
                const ty=(Math.random()-0.5)*200;
                const tr=(Math.random()-0.5)*360;
                const d=Math.random()*0.4;
                s.style.transitionDelay=d+'s';
                s.style.transform=`translate(${tx}vw,${ty}vh) rotate(${tr}deg) scale(0.1)`;
                s.style.opacity=0;
            });

            setTimeout(()=>{{ blackFade.style.opacity=1; }}, SHATTER_DURATION);

            setTimeout(()=>{
                const bg=document.createElement('div');
                bg.style.position='absolute';
                bg.style.top='0'; bg.style.left='0';
                bg.style.width='100%'; bg.style.height='100%';
                bg.style.backgroundImage='url("data:image/jpeg;base64,{bg_b64}")';
                bg.style.backgroundSize='cover';
                bg.style.backgroundPosition='center';
                bg.style.opacity='0';
                bg.style.transition=`opacity ${{MAIN_FADE_IN_DURATION}}ms ease-in-out`;
                bg.style.zIndex='50';
                document.body.appendChild(bg);

                const title=document.createElement('div');
                title.innerText='TỔ BẢO DƯỠNG SỐ 1';
                Object.assign(title.style,{{
                    position:'absolute',top:'8%',width:'100%',textAlign:'center',
                    color:'#fff5d7',fontFamily:"'Playfair Display',serif",
                    fontSize:'clamp(30px,5vw,65px)',
                    textShadow:'0 0 18px rgba(0,0,0,0.65)',
                    opacity:'0',transition:`opacity ${{MAIN_FADE_IN_DURATION}}ms ease-in-out 0.5s`,
                    zIndex:'55'
                }});
                document.body.appendChild(title);

                setTimeout(()=>{
                    bg.style.opacity=1;
                    title.style.opacity=1;
                    blackFade.style.opacity=0;
                },100);
            }, SHATTER_DURATION+FADE_TO_BLACK_DELAY+200);
        }}

        vid.addEventListener('canplay',()=>{
            vid.play().catch(()=>{});
            startAudio();
            blackFade.style.opacity=0;
        });
        vid.addEventListener('ended',finishIntro);
        setTimeout(finishIntro,12000);
        </script>
    </body>
    </html>
    """
    components.html(intro_html, height=800, scrolling=False)


# ================== TRANG CHÍNH ==================
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    try:
        with open(bg, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError as e:
        st.error(f"Lỗi: Không tìm thấy file {e.filename}")
        st.stop()

    st.markdown(f"""
    <style>
    html, body, .stApp {{
        height:100vh !important;
        background:url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed;
        background-size:cover !important;
        animation:fadeInBg 1.5s ease-in-out forwards;
    }}
    @keyframes fadeInBg {{
        from{{opacity:0;}} to{{opacity:1;}}
    }}
    .welcome {{
        position:absolute; top:8%; width:100%; text-align:center;
        font-size:clamp(30px,5vw,65px); color:#fff5d7;
        font-family:'Playfair Display',serif;
        text-shadow:0 0 18px rgba(0,0,0,0.65);
        animation:fadeInText 2s ease-in-out forwards;
    }}
    @keyframes fadeInText {{
        from{{opacity:0; transform:scale(0.97);}}
        to{{opacity:1; transform:scale(1);}}
    }}
    </style>
    <div class="welcome">TỔ BẢO DƯỠNG SỐ 1</div>
    """, unsafe_allow_html=True)


# ================== LUỒNG CHÍNH ==================
hide_streamlit_ui()

if "is_mobile" not in st.session_state:
    ua = st_javascript("window.navigator.userAgent;")
    if ua:
        info = parse(ua)
        st.session_state.is_mobile = not info.is_pc
        st.rerun()
    else:
        st.info("Đang xác định thiết bị...")
        time.sleep(1)
        st.stop()

if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

if not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
    time.sleep(15)
    st.session_state.intro_done = True
    st.rerun()
else:
    main_page(st.session_state.is_mobile)
