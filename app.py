import streamlit as st
import base64
import time
import os
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components


# ========== CẤU HÌNH VÀ TÀI NGUYÊN ==========

# File video và âm thanh intro
VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
SFX = "plane_fly.mp3"

# File ảnh tĩnh cho hiệu ứng SHATTER/RECONSTRUCT (Ảnh chụp từ frame cuối video)
SHUTTER_PC = "airplane_shutter.jpg"
SHUTTER_MOBILE = "mobile_shutter.jpg"

# File ảnh nền của trang chính (sẽ hiện ra sau khi ghép lại)
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"

st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

# Kích thước lưới và thời gian
GRID_SIZE = 8
SHATTER_DURATION = 1.8  # Thời gian hiệu ứng tan vỡ (giây)
RECONSTRUCT_DURATION = 1.8 # Thời gian hiệu ứng ghép lại (giây)
BLACKOUT_DELAY = 0.2    # Thời gian màn hình đen

# Số lượng cột sóng âm
WAVE_COLUMNS = 16 

# ========== HÀM PHỤ TRỢ ==========

def hide_streamlit_ui():
    """Ẩn các thành phần UI mặc định của Streamlit."""
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

def encode_audio_files(base_path="."):
    """Đọc và mã hóa Base64 cho các file nhạc nền."""
    audio_data = {}
    for i in range(1, 7):
        filename = f"background{i}.mp3"
        filepath = os.path.join(base_path, filename)
        try:
            with open(filepath, "rb") as f:
                b64_data = base64.b64encode(f.read()).decode()
                audio_data[filename] = f"data:audio/mp3;base64,{b64_data}"
        except FileNotFoundError:
            pass
    return audio_data


# ========== MÀN HÌNH INTRO (Giữ nguyên) ==========
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    shutter_file = SHUTTER_MOBILE if is_mobile else SHUTTER_PC
    bg_file = BG_MOBILE if is_mobile else BG_PC
    
    try:
        with open(video_file, "rb") as f:
            video_b64 = base64.b64encode(f.read()).decode()
        with open(SFX, "rb") as a:
            audio_b64 = base64.b64encode(a.read()).decode()
        with open(shutter_file, "rb") as s:
            shutter_b64 = base64.b64encode(s.read()).decode()
        with open(bg_file, "rb") as b:
            bg_b64 = base64.b64encode(b.read()).decode()
            
    except FileNotFoundError as e:
        st.error(f"Lỗi: Không tìm thấy file tài nguyên. Vui lòng kiểm tra: {e.filename}")
        st.stop()
    
    shards_html = "".join([f"<div class='shard' id='shard-{i}'></div>" for i in range(GRID_SIZE * GRID_SIZE)])

    js_shatter_duration = SHATTER_DURATION * 1000
    js_reconstruct_duration = RECONSTRUCT_DURATION * 1000
    js_blackout_delay = BLACKOUT_DELAY * 1000


    intro_html = f"""
    <html>
    <head>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <style>
        /* CSS Intro (Giữ nguyên) */
        html, body {{
            margin: 0; padding: 0;
            overflow: hidden;
            background: black;
            height: 100%;
        }}
        #pre-load-bg {{ display: none; background-image: url("data:image/jpeg;base64,{bg_b64}"); }}
        video {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;
        }}
        #static-frame {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;
            background-image: url("data:image/jpeg;base64,{shutter_b64}");
            background-size: cover; opacity: 0; z-index: 20; transition: opacity 0.1s linear;
        }}
        audio {{ display: none; }}
        #intro-text {{
            position: absolute; 
            top: 8%; 
            left: 50%; 
            transform: translate(-50%, 0); 
            width: 90vw; text-align: center; color: #f8f4e3;
            font-size: clamp(22px, 6vw, 60px); font-weight: bold; font-family: 'Playfair Display', serif;
            background: linear-gradient(120deg, #e9dcb5 20%, #fff9e8 40%, #e9dcb5 60%);
            background-size: 200%; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            text-shadow: 0 0 15px rgba(255,255,230,0.4);
            animation: lightSweep 6s linear infinite, fadeInOut 6s ease-in-out forwards;
            line-height: 1.2; word-wrap: break-word; z-index: 10;
        }}
        @keyframes lightSweep {{ 0% {{ background-position: 200% 0%; }} 100% {{ background-position: -200% 0%; }} }}
        @keyframes fadeInOut {{ 0% {{ opacity: 0; }} 20% {{ opacity: 1; }} 80% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}

        #shatter-overlay {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            display: grid; grid-template-columns: repeat({GRID_SIZE}, 1fr); grid-template-rows: repeat({GRID_SIZE}, 1fr);
            opacity: 0; pointer-events: none; z-index: 30; 
        }}
        .shard {{
            position: relative;
            background-image: url("data:image/jpeg;base64,{shutter_b64}"); 
            background-size: 100vw 100vh;
            transition: transform {SHATTER_DURATION}s cubic-bezier(0.68, -0.55, 0.27, 1.55), opacity 1.5s ease-in-out; 
            opacity: 1; 
        }}
        
        .reconstructing .shard {{
            transform: translate(0, 0) rotate(0deg) scale(1) !important; 
            transition: transform {RECONSTRUCT_DURATION}s cubic-bezier(0.19, 1, 0.22, 1), opacity {RECONSTRUCT_DURATION}s ease-in-out; 
            background-image: url("data:image/jpeg;base64,{bg_b64}") !important;
            opacity: 1 !important; 
        }}

        #black-fade {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: black; opacity: 1; z-index: 40;
            transition: opacity 1s ease-in-out; pointer-events: none;
        }}

        </style>
    </head>
    <body>
        <div id="pre-load-bg"></div>
        <video id='introVid' autoplay muted playsinline>
            <source src='data:video/mp4;base64,{video_b64}' type='video/mp4'>
        </video>
        <div id='static-frame'></div>
        <audio id='flySfx'> <source src='data:audio/mp3;base64,{audio_b64}' type='audio/mp3'></audio>
        <div id='intro-text'>KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>

        <div id='shatter-overlay'>{shards_html}</div>
        <div id='black-fade'></div>


        <script>
        const GRID_SIZE = {GRID_SIZE};
        const SHATTER_DURATION = {js_shatter_duration};
        const RECONSTRUCT_DURATION = {js_reconstruct_duration};
        const BLACKOUT_DELAY = {js_blackout_delay};

        const vid = document.getElementById('introVid');
        const audio = document.getElementById('flySfx');
        const staticFrame = document.getElementById('static-frame');
        const shatterOverlay = document.getElementById('shatter-overlay');
        const shards = document.querySelectorAll('.shard');
        const blackFade = document.getElementById('black-fade');
        let ended = false;
        let initialTransforms = []; 

        shards.forEach((shard, index) => {{
            const row = Math.floor(index / GRID_SIZE);
            const col = index % GRID_SIZE;
            shard.style.backgroundPosition = 'calc(-' + col + ' * 100vw / ' + GRID_SIZE + ') calc(-' + row + ' * 100vh / ' + GRID_SIZE + ')';
            const randX = (Math.random() - 0.5) * 200; 
            const randY = (Math.random() - 0.5) * 200; 
            const randR = (Math.random() - 0.5) * 360; 
            const delay = Math.random() * 0.5; 
            initialTransforms.push({{randX, randY, randR, delay}});
        }});

        function finishIntro() {{
            if (ended) return;
            ended = true;
            
            vid.style.opacity = 0; 
            staticFrame.style.opacity = 1; 
            
            // BƯỚC 1: Bắt đầu Tan Vỡ
            setTimeout(() => {{ 
                blackFade.style.opacity = 0; 
                shatterOverlay.style.opacity = 1; 
                staticFrame.style.opacity = 0; 
                
                shatterOverlay.classList.remove('reconstructing');
                shatterOverlay.classList.add('shattering');
                shards.forEach((shard, index) => {{
                    const t = initialTransforms[index];
                    shard.style.transform = 'translate(' + t.randX + 'vw, ' + t.randY + 'vh) rotate(' + t.randR + 'deg) scale(0.1)';
                    shard.style.transitionDelay = t.delay + 's';
                    shard.style.opacity = 0; 
                }});
            }}, 10);
            
            // BƯỚC 2: Màn Hình Đen & TẮT NHẠC
            setTimeout(() => {{
                shatterOverlay.style.opacity = 0; 
                blackFade.style.opacity = 1; 
                audio.pause(); 
                audio.currentTime = 0;
            }}, SHATTER_DURATION * 1000); 

            // BƯỚC 3: Ghép Lại
            setTimeout(() => {{
                shatterOverlay.style.opacity = 1; 
                blackFade.style.opacity = 0; 
                
                shatterOverlay.classList.remove('shattering');
                shatterOverlay.classList.add('reconstructing'); 
                
                shards.forEach((shard, index) => {{
                    shard.style.transitionDelay = (RECONSTRUCT_DURATION / 1000 - initialTransforms[index].delay) + 's';
                }});

                // BƯỚC 4: Thông báo hoàn thành - Tải lại trang NGAY LẬP TỨC
                setTimeout(() => {{
                    window.parent.postMessage({{type: 'intro_done'}}, '*');
                }}, RECONSTRUCT_DURATION * 1000 + 10); 

            }}, SHATTER_DURATION * 1000 + BLACKOUT_DELAY * 1000); 

        }}

        vid.addEventListener('canplay', () => {{
            vid.play().catch(() => console.log('Autoplay bị chặn'));
            blackFade.style.opacity = 0; 
        }});
        vid.addEventListener('play', () => {{
            audio.volume = 1.0;
            audio.currentTime = 0;
            audio.play().catch(() => console.log('Autoplay âm thanh bị chặn'));
        }});
        document.addEventListener('click', () => {{
            vid.muted = false;
            vid.play();
            audio.volume = 1.0;
            audio.currentTime = 0;
            audio.play().catch(()=>{{}}); 
            blackFade.style.opacity = 0; 
        }}, {{once:true}});

        vid.addEventListener('ended', finishIntro);
        setTimeout(finishIntro, 9000); 

        blackFade.style.opacity = 1;

        </script>
    </body>
    </html>
    """
    components.html(intro_html, height=800, scrolling=False)

# -------------------------------------------------------------
## Thanh Phát Nhạc (Claymorphism + Visualizer Sóng âm)
def audio_player_component(audio_uris):
    
    # Tạo HTML cho 16 cột sóng âm
    wave_columns_html = "".join([
        f'<div class="visualizer-colum1" style="animation-delay: {3.99 - i * 0.1}s;">'
        '<div class="visualizer-row"></div>'
        '</div>'
        for i in range(WAVE_COLUMNS)
    ])
    
    # Tạo danh sách URIs cho JS
    js_audio_list = [f"{{uri: '{uri}'}}" for uri in audio_uris.values()]
    audio_list_str = "[" + ", ".join(js_audio_list) + "]"
    
    # Định nghĩa khối CSS Visualizer như một chuỗi thô (Raw String)
    # TÁCH CSS VÀO st.markdown (BÊN DƯỚI) ĐỂ KHẮC PHỤC LỖI CÚ PHÁP LẶP LẠI
    visualizer_css = """
    @keyframes Rofa {
        0% { height: 0%; } 5% { height: 100%; } 10% { height: 90%; } 15% { height: 80%; }
        20% { height: 70%; } 25% { height: 0%; } 30% { height: 70%; } 35% { height: 0%; }
        40% { height: 60%; } 45% { height: 0%; } 50% { height: 50%; } 55% { height: 0%; }
        60% { height: 40%; } 65% { height: 0%; } 70% { height: 30%; } 75% { height: 0%; }
        80% { height: 20%; } 85% { height: 0%; } 90% { height: 10%; } 95% { height: 5%; }
        100% { height: 0; }
    }
    .music-player {
        background: rgba(255, 255, 255, 0.9); padding: 8px; border-radius: 20px; 
        box-shadow: inset 3px 3px 6px rgba(255, 255, 255, 0.7), inset -3px -3px 6px rgba(0, 0, 0, 0.1),
            8px 8px 16px rgba(0, 0, 0, 0.2), -8px -8px 16px rgba(255, 255, 255, 0.6);
        display: flex; align-items: center; gap: 12px; backdrop-filter: blur(5px); 
        -webkit-backdrop-filter: blur(5px); height: 55px; width: 100%; max-width: 280px; 
    }
    .controls-group { display: flex; gap: 8px; align-items: center; }
    .music-player button {
        background: #e0e0f0; border: none; color: #6a6a80; cursor: pointer; padding: 0;
        border-radius: 12px; width: 35px; height: 35px; display: flex; justify-content: center;
        align-items: center; box-shadow: 3px 3px 6px rgba(0, 0, 0, 0.15), -3px -3px 6px rgba(255, 255, 255, 0.8);
        transition: all 0.2s ease; outline: none;
    }
    .music-player button:active, .music-player button.active {
        box-shadow: inset 3px 3px 6px rgba(0, 0, 0, 0.2), inset -3px -3px 6px rgba(255, 255, 255, 0.7);
        transform: scale(0.95);
    }
    .music-player svg { stroke: #6a6a80; fill: #6a6a80; width: 16px; height: 16px; }
    #play-pause-btn { width: 40px; height: 40px; border-radius: 15px; background: #dddde5; }
    .visualizer-container {
        display: flex; align-items: flex-end; height: 40px; padding: 0 5px;
        gap: 3px; border-radius: 5px; background: #eee; transition: opacity 0.3s;
        opacity: 0.4; 
    }
    .visualizer-colum1 {
        width: 3px; height: 100%; border-radius: 1px; display: inline-block; position: relative;
    }
    .visualizer-colum1 .visualizer-row {
        width: 100%; height: 100%; border-radius: 1px; background: linear-gradient(to top, #c7a46e, #e9dcb5); 
        position: absolute; animation: Rofa 10s infinite ease-in-out; bottom: 0; transform-origin: bottom; 
    }
    """
    
    # Tách CSS ra khỏi components.html và đặt vào st.markdown
    # Điều này giúp Streamlit xử lý CSS dễ dàng hơn.
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css?family=Allerta&display=swap');
    * {{ font-family: 'Allerta', sans-serif; }}
    {visualizer_css}
    </style>
    """, unsafe_allow_html=True)
    
    # Chỉ giữ lại HTML và JS trong components.html
    html_code = f"""
    <div class="music-player-container">
        <div class="music-player">
            <audio id="background-audio" preload="auto" loop></audio>
            
            <div class="controls-group">
                <button id="prev-btn" title="Previous Track">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polygon points="19 20 9 12 19 4 19 20"></polygon><line x1="5" y1="19" x2="5" y2="5"></line>
                    </svg>
                </button>
                <button id="play-pause-btn" title="Play/Pause">
                    <svg id="play-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="0" stroke-linecap="round" stroke-linejoin="round">
                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                    </svg>
                    <svg id="pause-icon" style="display:none;" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="0" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="6" y="4" width="4" height="16" rx="1"></rect><rect x="14" y="4" width="4" height="16" rx="1"></rect>
                    </svg>
                </button>
                <button id="next-btn" title="Next Track">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polygon points="5 4 15 12 5 20 5 4"></polygon><line x1="19" y1="5" x2="19" y2="19"></line>
                    </svg>
                </button>
            </div>

            <div class="visualizer-container">
                 {wave_columns_html}
            </div>
            
        </div>
    </div>

    <script>
        const audio = document.getElementById('background-audio');
        const playPauseBtn = document.getElementById('play-pause-btn');
        const playIcon = document.getElementById('play-icon');
        const pauseIcon = document.getElementById('pause-icon');
        const visualizer = document.querySelector('.visualizer-container');

        const playlist = {audio_list_str};
        let currentTrackIndex = 0;
        let isPlaying = false;
        
        function updatePlayPauseIcon() {{
            if (isPlaying) {{
                playIcon.style.display = 'none';
                pauseIcon.style.display = 'block';
                visualizer.style.opacity = '1'; 
            }} else {{
                playIcon.style.display = 'block';
                pauseIcon.style.display = 'none';
                visualizer.style.opacity = '0.4'; 
            }}
        }}

        function loadTrack(index) {{
            if (playlist.length === 0) return;
            currentTrackIndex = (index % playlist.length + playlist.length) % playlist.length;
            audio.src = playlist[currentTrackIndex].uri;
            audio.load();
        }}
        
        function playTrack() {{
            if (!audio.src) loadTrack(currentTrackIndex);
            
            playPauseBtn.classList.remove('active');
            playPauseBtn.classList.add('active'); 
            
            audio.play().then(() => {{
                isPlaying = true;
                updatePlayPauseIcon();
            }}).catch(error => {{
                console.log("Autoplay blocked or playback failed:", error);
                isPlaying = true; 
                updatePlayPauseIcon();
            }}).finally(() => {{
                 setTimeout(() => playPauseBtn.classList.remove('active'), 150);
            }});
        }}
        
        function pauseTrack() {{
            audio.pause();
            isPlaying = false;
            updatePlayPauseIcon();
        }}
        
        function togglePlayPause() {{
            if (isPlaying) {{
                pauseTrack();
            }} else {{
                playTrack();
            }}
        }}

        function nextTrack() {{
            loadTrack(currentTrackIndex + 1);
            if (isPlaying) playTrack();
        }}
        
        function prevTrack() {{
            loadTrack(currentTrackIndex - 1);
            if (isPlaying) playTrack();
        }}

        // --- Event Listeners ---
        document.getElementById('play-pause-btn').addEventListener('click', togglePlayPause);
        document.getElementById('next-btn').addEventListener('click', nextTrack);
        document.getElementById('prev-btn').addEventListener('click', prevTrack);
        
        audio.addEventListener('ended', nextTrack); 
        
        loadTrack(0);

        window.addEventListener('load', () => {{
             updatePlayPauseIcon();
        }});
        
        // Kích hoạt player khi có click bất kỳ (cho Autoplay)
        document.body.addEventListener('click', () => {{
            if (!isPlaying && audio.paused) {{
                playTrack();
            }}
        }}, {{once: true}}); 

    </script>
    """
    
    components.html(html_code, height=65) 


# -------------------------------------------------------------
## TRANG CHÍNH
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    try:
        with open(bg, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError as e:
        st.error(f"Lỗi: Không tìm thấy file tài nguyên: {e.filename}")
        st.stop()
        
    if st.session_state.get('audio_uris'):
        audio_player_component(st.session_state.audio_uris)


    st.markdown(f"""
    <style>
    /* CSS NỀN VÀ TIÊU ĐỀ (Giữ nguyên) */
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
        animation: fadeInBg 0.5s ease-in-out forwards; 
    }}
    
    @keyframes fadeInBg {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    .welcome {{
        position: absolute;
        top: 8%;
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
        animation: textLight 10s linear infinite, fadeIn 1s ease-in-out forwards; 
        letter-spacing: 2px;
        z-index: 3;
    }}

    /* KHẮC PHỤC LỖI "BAY" CỦA PLAYER */
    iframe[title*="streamlit_component"] {{
        position: fixed !important;
        top: 15px !important;
        left: 15px !important;
        z-index: 1000 !important;
        background: transparent !important;
        height: 65px !important; 
        width: 300px !important; /* Đủ rộng cho player + visualizer */
        border: none !important;
        transition: none !important; 
    }}

    /* ... (Phần CSS khác) ... */
    
    </style>


    <div class="welcome">TỔ BẢO DƯỠNG SỐ 1</div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.get('audio_uris'):
        st.warning("Không tìm thấy file nhạc nào để phát. Vui lòng kiểm tra file background1-6.mp3.")


# -------------------------------------------------------------
## LUỒNG CHÍNH CỦA ỨNG DỤNG
hide_streamlit_ui()

# 1. Xác định thiết bị
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

# 2. Mã hóa file nhạc LẦN ĐẦU
if "audio_uris" not in st.session_state or not st.session_state.get('audio_uris'):
    st.session_state.audio_uris = encode_audio_files()

# 3. Quản lý trạng thái Intro
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

if not st.session_state.intro_done:
    intro_screen(st.session_state.is_mobile)
    
    st.markdown("""
    <script>
    window.addEventListener("message", (event) => {
        if (event.data.type === "intro_done") {
            window.parent.location.reload(); 
        }
    });
    </script>
    """, unsafe_allow_html=True)

    if not st.session_state.get('intro_timeout_set', False):
        st.session_state.intro_timeout_set = True
        time.sleep(15) 
        if not st.session_state.intro_done:
             st.session_state.intro_done = True
             st.rerun()

else:
    main_page(st.session_state.is_mobile)
