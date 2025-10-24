import streamlit as st
from streamlit_javascript import st_javascript
from user_agents import parse
import time
import streamlit.components.v1 as components
import base64

# ======= FILES & CONFIG =======
VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
SFX = "plane_fly.mp3"

BROKEN_IMAGE_PC = "airplane_shutter.jpg"
BROKEN_IMAGE_MOBILE = "mobile_shutter.jpg"

BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"

GLASS_ROWS = 10
GLASS_COLS = 10
BREAK_DURATION = 1.5
REVEAL_GRID = 8
REVEAL_DURATION = 3.5

st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

# ======= HIDE STREAMLIT UI =======
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

# ======= INTRO SCREEN =======
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    broken_image = BROKEN_IMAGE_MOBILE if is_mobile else BROKEN_IMAGE_PC
    bg_file = BG_MOBILE if is_mobile else BG_PC

    # Encode images (lightweight)
    with open(broken_image, "rb") as f:
        broken_b64 = base64.b64encode(f.read()).decode()
    with open(bg_file, "rb") as f:
        bg_b64 = base64.b64encode(f.read()).decode()

    intro_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name='viewport' content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
        <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        html, body {{ width:100%; height:100%; overflow:hidden; background:#000; }}
        #container {{ position:absolute; top:0; left:0; width:100%; height:100%; background:#000; }}
        #main-page-bg {{
            position:absolute; top:0; left:0; width:100%; height:100%;
            background-image:url("data:image/jpeg;base64,{bg_b64}");
            background-size:cover; background-position:center; z-index:0; opacity:0;
            transition: opacity 1s;
        }}
        #main-page-bg.visible {{ opacity:1; }}
        video {{ position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; z-index:1; }}
        audio {{ display:none; }}
        #intro-text {{
            position:absolute; top:8%; left:50%; transform:translate(-50%,0); width:90%;
            text-align:center; color:#f8f4e3; font-size:clamp(22px,6vw,60px);
            font-weight:bold; font-family:'Playfair Display', serif;
            background: linear-gradient(120deg,#e9dcb5 20%,#fff9e8 40%,#e9dcb5 60%);
            background-size:200%;
            -webkit-background-clip:text;
            -webkit-text-fill-color:transparent;
            text-shadow:0 0 15px rgba(255,255,230,0.4);
            animation: lightSweep 6s linear infinite, fadeInOut 6s ease-in-out forwards;
            z-index:10;
        }}
        @keyframes lightSweep {{ 0%{{background-position:200% 0%;}} 100%{{background-position:-200% 0%;}} }}
        @keyframes fadeInOut {{ 0%{{opacity:0;}} 20%{{opacity:1;}} 80%{{opacity:1;}} 100%{{opacity:0;}} }}

        #broken-glass-container {{ position:absolute; top:0; left:0; width:100%; height:100%; opacity:0; z-index:5; pointer-events:none; }}
        #broken-glass-container.active {{ opacity:1; }}
        .broken-piece {{ position:absolute; background-image:url("data:image/jpeg;base64,{broken_b64}"); background-size:100% 100%; overflow:hidden; }}

        #reveal-overlay {{ position:absolute; top:0; left:0; width:100%; height:100%; display:grid; grid-template-columns:repeat({REVEAL_GRID},1fr); grid-template-rows:repeat({REVEAL_GRID},1fr); z-index:20; pointer-events:none; }}
        .reveal-tile {{ background:#000; opacity:1; }}

        #main-text {{
            position:absolute; top:8%; left:50%; transform:translate(-50%,0); width:90%; text-align:center;
            font-size:clamp(30px,5vw,65px); color:#fff5d7; font-family:'Playfair Display', serif;
            text-shadow:0 0 18px rgba(0,0,0,0.65),0 0 30px rgba(255,255,180,0.25);
            background:linear-gradient(120deg,#f3e6b4 20%,#fff7d6 40%,#f3e6b4 60%);
            background-size:200%; -webkit-background-clip:text; -webkit-text-fill-color:transparent;
            animation:textLight 10s linear infinite; letter-spacing:2px; z-index:25; opacity:0;
        }}
        @keyframes textLight {{ 0%{{background-position:200% 0%;}} 100%{{background-position:-200% 0%;}} }}
        </style>
    </head>
    <body>
        <div id="container">
            <div id="main-page-bg"></div>
            
            <video id='introVid' autoplay muted playsinline>
                <source src='{video_file}' type='video/mp4'>
            </video>
            <audio id='flySfx'>
                <source src='{SFX}' type='audio/mp3'>
            </audio>

            <div id='intro-text'>KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
            <div id='broken-glass-container'></div>
            <div id='reveal-overlay'></div>
            <div id='main-text'>TỔ BẢO DƯỠNG SỐ 1</div>
        </div>

        <script>
        const GLASS_ROWS={GLASS_ROWS}, GLASS_COLS={GLASS_COLS}, BREAK_DURATION={BREAK_DURATION};
        const REVEAL_GRID={REVEAL_GRID}, REVEAL_DURATION={REVEAL_DURATION};
        const vid=document.getElementById('introVid'), audio=document.getElementById('flySfx');
        const glassContainer=document.getElementById('broken-glass-container');
        const revealOverlay=document.getElementById('reveal-overlay');
        const introText=document.getElementById('intro-text'), mainText=document.getElementById('main-text');
        const mainBg=document.getElementById('main-page-bg');
        let ended=false;

        function createBrokenPieces() {{
            const pieceWidth=100/GLASS_COLS, pieceHeight=100/GLASS_ROWS;
            for(let r=0;r<GLASS_ROWS;r++){{
                for(let c=0;c<GLASS_COLS;c++){{
                    const piece=document.createElement('div');
                    piece.className='broken-piece';
                    piece.style.left=(c*pieceWidth)+'%';
                    piece.style.top=(r*pieceHeight)+'%';
                    piece.style.width=pieceWidth+'%';
                    piece.style.height=pieceHeight+'%';
                    piece.style.backgroundPosition=`${{-c*pieceWidth}}% ${{-r*pieceHeight}}%`;
                    piece.style.backgroundSize=`${{GLASS_COLS*100}}% ${{GLASS_ROWS*100}}%`;
                    glassContainer.appendChild(piece);
                }}
            }}
        }}

        function createRevealGrid() {{
            for(let i=0;i<REVEAL_GRID*REVEAL_GRID;i++){{
                const tile=document.createElement('div');
                tile.className='reveal-tile';
                revealOverlay.appendChild(tile);
            }}
        }}

        function breakGlass() {{
            document.querySelectorAll('.broken-piece').forEach(piece => {{
                const angle=Math.random()*360, distance=100+Math.random()*500;
                const x=Math.cos(angle*Math.PI/180)*distance;
                const y=Math.sin(angle*Math.PI/180)*distance;
                const rotation=Math.random()*720-360, delay=Math.random()*0.3;
                gsap.to(piece,{{x:x,y:y,rotation:rotation,opacity:0,duration:BREAK_DURATION,delay:delay,ease:"power2.out"}});
            }});
        }}

        function revealMainPage() {{
            const tiles=document.querySelectorAll('.reveal-tile');
            const center=Math.floor(REVEAL_GRID/2);
            mainBg.classList.add('visible');
            gsap.to(mainText,{{opacity:1,duration:1,ease:"power2.inOut"}});
            tiles.forEach((tile,index) => {{
                const row=Math.floor(index/REVEAL_GRID), col=index%REVEAL_GRID;
                const distance=Math.abs(row-center)+Math.abs(col-center);
                const delay=distance*(REVEAL_DURATION/(REVEAL_GRID*2));
                gsap.to(tile,{{opacity:0,duration:0.4,delay:delay,ease:"power2.inOut",onComplete:function(){{
                    if(index===tiles.length-1) revealOverlay.style.display='none';
                }}}});
            }});
        }}

        function finishIntro() {{
            if(ended) return;
            ended=true;
            vid.style.opacity=0;
            introText.style.display='none';
            glassContainer.classList.add('active');
            setTimeout(()=>breakGlass(),100);
            setTimeout(()=>{{ glassContainer.style.opacity=0; revealMainPage(); }}, BREAK_DURATION*1000+200);
            setTimeout(()=>{{ window.parent.postMessage({{type:'intro_done'}},'*'); }}, BREAK_DURATION*1000+REVEAL_DURATION*1000+500);
        }}

        createBrokenPieces();
        createRevealGrid();

        vid.addEventListener('loadeddata', ()=>{{ vid.play().catch(e=>console.log('Video blocked',e)); }});

        let interacted=false;
        ['click','touchstart'].forEach(evt => document.addEventListener(evt, ()=>{{
            if(!interacted){{
                interacted=true;
                vid.muted=false;
                vid.play().catch(e=>console.log('Video blocked on interaction',e));
                audio.currentTime=0;
                audio.volume=1;
                audio.play().catch(e=>console.log('Audio blocked',e));
            }}
        }}, {{once:true}}));

        vid.addEventListener('ended', finishIntro);
        setTimeout(finishIntro,9000);
        </script>
    </body>
    </html>
    """
    components.html(intro_html, height=800, scrolling=False)


# ======= MAIN PAGE =======
def main_page(is_mobile=False):
    hide_streamlit_ui()
    st.markdown("""
    <style>
    html, body, .stApp { background:black; height:100vh; }
    </style>
    """, unsafe_allow_html=True)


# ======= MAIN LOOP =======
hide_streamlit_ui()

if "is_mobile" not in st.session_state:
    ua_string = st_javascript("window.navigator.userAgent;")
    if ua_string:
        ua = parse(ua_string)
        st.session_state.is_mobile = not ua.is_pc
        st.rerun()
    else:
        st.info("Đang xác định thiết bị...")
        time.sleep(1)
        st.stop()

if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

intro_screen(st.session_state.is_mobile)

st.markdown("""
<script>
window.addEventListener("message", (event) => {
    if (event.data.type === "intro_done") {
        console.log('Intro completed!');
    }
});
</script>
""", unsafe_allow_html=True)
