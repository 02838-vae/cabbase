import streamlit as st
import base64
import time
from streamlit_javascript import st_javascript
from user_agents import parse
import streamlit.components.v1 as components

# ========== CẤU HÌNH ==========
st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
SFX = "plane_fly.mp3"


# ========== ẨN UI STREAMLIT ==========
def hide_streamlit_ui():
    st.markdown("""
    <style>
    /* Ẩn các thành phần UI mặc định của Streamlit */
    [data-testid="stToolbar"], header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
    }
    /* Đặt ứng dụng chiếm toàn bộ màn hình */
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


# ========== HÀM CALLBACK (MỚI) ==========
def finish_intro_callback():
    """Được gọi khi nút ẩn 'Trigger Intro Finish' được click bởi JavaScript."""
    st.session_state.intro_done = True
    # Không cần st.rerun() vì Streamlit tự rerun khi button được click

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


# ========== MÀN HÌNH INTRO (Đã Tối Ưu Hóa JS Timing) ==========
def intro_screen(is_mobile=False):
    hide_streamlit_ui()
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    try:
        with open(video_file, "rb") as f:
            video_b64 = base64.b64encode(f.read()).decode()
        with open(SFX, "rb") as a:
            audio_b64 = base64.b64encode(a.read()).decode()
    except FileNotFoundError as e:
        st.error(f"Lỗi: Không tìm thấy tệp đa phương tiện: {e}")
        st.stop()

    # Thời gian video: 5s. Tổng chuyển cảnh: 4s (Đóng màn chập 1s, chờ chuyển trạng thái 3s)
    
    intro_html = f"""
    <html>
    <head>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <style>
        html, body {{
            margin: 0; padding: 0; border: 0;
            overflow: hidden;
            width: 100vw; height: 100vh;
            background: black;
        }}
        video {{
            position: fixed;
            top: 0; left: 0;
            width: 100vw;
            height: 100vh;
            object-fit: cover;
            z-index: 1;
        }}
        audio {{ display: none; }}
        #intro-text {{
            position: absolute; top: 12%; left: 50%; transform: translateX(-50%); width: 90vw;
            text-align: center; color: #f8f4e3; font-size: clamp(22px, 6vw, 60px);
            font-weight: bold; font-family: 'Playfair Display', serif; z-index: 2;
            background: linear-gradient(120deg, #e9dcb5 20%, #fff9e8 40%, #e9dcb5 60%);
            background-size: 200%; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            text-shadow: 0 0 15px rgba(255,255,230,0.4);
            animation: lightSweep 6s linear infinite, fadeInOut 6s ease-in-out forwards;
        }}
        @keyframes lightSweep {{ 0% {{ background-position: 200% 0%; }} 100% {{ background-position: -200% 0%; }} }}
        @keyframes fadeInOut {{ 0% {{ opacity: 0; }} 20% {{ opacity: 1; }} 80% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}

        /* --- SHUTTER EFFECT --- */
        #left-shutter, #right-shutter {{
            position: fixed; top: 0; width: 50vw; height: 100vh;
            background: black; z-index: 3; transition: all 1s ease-in-out;
        }}
        #left-shutter {{ left: -50vw; }}
        #right-shutter {{ right: -50vw; }}
        .shutter-close #left-shutter {{ left: 0; }}
        .shutter-close #right-shutter {{ right: 0; }}
        </style>
    </head>
    <body>
        <video id='introVid' autoplay muted playsinline>
            <source src='data:video/mp4;base64,{video_b64}' type='video/mp4'>
        </video>
        <audio id='flySfx'>
            <source src='data:audio/mp3;base64,{audio_b64}' type='audio/mp3'>
        </audio>
        <div id='intro-text'>KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>

        <div id='left-shutter'></div>
        <div id='right-shutter'></div>

        <script>
        const vid = document.getElementById('introVid');
        const audio = document.getElementById('flySfx');
        let ended = false;

        function finishIntro() {{
            if (ended) return;
            ended = true;
            document.body.classList.add('shutter-close');

            // 1. Màn đen hoàn toàn
            setTimeout(() => {{
                document.body.style.background = "black";
            }}, 1000); // Đợi 1s cho transition màn chập hoàn tất

            // 2. Gửi tín hiệu sang Streamlit (sau 3.5s từ khi đóng màn chập)
            setTimeout(() => {{
                window.parent.postMessage({{type: 'intro_done_internal'}}, '*');
            }}, 3500); 
        }}

        vid.addEventListener('canplay', () => {{ vid.play().catch(() => console.log('Autoplay bị chặn')); }});
        vid.addEventListener('play', () => {{ 
            audio.volume = 1.0; audio.currentTime = 0;
            audio.play().catch(() => console.log('Autoplay âm thanh bị chặn'));
        }});

        document.addEventListener('click', () => {{
            vid.muted = false; vid.play();
            audio.volume = 1.0; audio.currentTime = 0;
            audio.play().catch(()=>{{}});
        }}, {{once:true}});

        vid.addEventListener('ended', finishIntro);
        
        // Cơ chế dự phòng JS: Gọi finishIntro sau 5.5s (5s video + 0.5s trễ)
        setTimeout(finishIntro, 5500); 
        </script>
    </body>
    </html>
    """

    components.html(intro_html, height=1080, scrolling=False)


# ========== TRANG CHÍNH ==========
def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    try:
        with open(bg, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError as e:
        st.error(f"Lỗi: Không tìm thấy tệp hình nền: {e}")
        st.stop()


    st.markdown(f"""
    <style>
    html, body, .stApp {{
        height: 100vh !important;
        background: 
            linear-gradient(to bottom, rgba(255, 235, 200, 0.25) 0%, rgba(160, 130, 90, 0.35) 50%, rgba(90, 70, 50, 0.5) 100%),
            url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed !important;
        background-size: cover !important;
        overflow: hidden !important;
        margin: 0 !important; padding: 0 !important; position: relative;
        filter: brightness(1.05) contrast(1.1) saturate(1.05);
    }}
    .welcome {{
        position: absolute; top: 8%; width: 100%; text-align: center;
        font-size: clamp(30px, 5vw, 65px); color: #fff5d7; font-family: 'Playfair Display', serif;
        text-shadow: 0 0 18px rgba(0,0,0,0.65), 0 0 30px rgba(255,255,180,0.25);
        background: linear-gradient(120deg, #f3e6b4 20%, #fff7d6 40%, #f3e6b4 60%);
        background-size: 200%; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: textLight 10s linear infinite, fadeIn 2s ease-in-out forwards;
    }}
    @keyframes textLight {{ 0% {{ background-position: 200% 0%; }} 100% {{ background-position: -200% 0%; }} }}
    @keyframes fadeIn {{ from {{ opacity: 0; transform: scale(0.97); }} to {{ opacity: 1; transform: scale(1); }} }}

    /* Shutter mở */
    #left-shutter, #right-shutter {{
        position: fixed; top: 0; width: 50vw; height: 100vh;
        background: black; z-index: 10; transition: all 1.2s ease-in-out;
    }}
    #left-shutter {{ left: 0; }}
    #right-shutter {{ right: 0; }}
    body.open-shutter #left-shutter {{ left: -50vw; }}
    body.open-shutter #right-shutter {{ right: -50vw; }}
    
    /* Ẩn nút kích hoạt của Streamlit */
    div.stButton:has(button[kind="secondaryFormSubmit"]) {
        display: none !important;
    }
    </style>

    <div id="left-shutter"></div>
    <div id="right-shutter"></div>
    <div class="welcome">TỔ BẢO DƯỠNG SỐ 1</div>

    <script>
    setTimeout(() => {{
        document.body.classList.add('open-shutter');
    }}, 100);
    </script>
    """, unsafe_allow_html=True)


# ========== LUỒNG CHÍNH (ĐÃ KHẮC PHỤC) ==========
hide_streamlit_ui()
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False


if not st.session_state.intro_done:
    
    # 1. Khởi tạo một nút ẩn và callback
    btn_placeholder = st.empty()
    # Nút này sẽ được JavaScript "click"
    btn_placeholder.button("Trigger Intro Finish", on_click=finish_intro_callback, key="trigger_intro_finish", type="secondary")
    
    # 2. Render intro screen (chứa video và hiệu ứng đóng màn chập)
    intro_screen(st.session_state.is_mobile)
    
    # 3. Listener lắng nghe tín hiệu từ JS và click nút
    st.markdown("""
    <script>
    window.addEventListener("message", (event) => {
        if (event.data.type === "intro_done_internal") {
            // Tìm nút ẩn (theo data-testid) và kích hoạt sự kiện click
            // stFormSubmitButton là data-testid mặc định cho nút secondary/default
            const triggerButton = window.parent.document.querySelector('[data-testid="stFormSubmitButton"] > button');
            if (triggerButton) {
                triggerButton.click();
            } else {
                console.warn("Could not find Streamlit trigger button to click.");
            }
        }
    });
    </script>
    """, unsafe_allow_html=True)
    
    # 4. Cơ chế Dự phòng Python Timer
    # Tổng thời gian: 5s Video + 3.5s JS (chờ gửi tín hiệu) = 8.5s. Dùng 8.6s làm dự phòng.
    time.sleep(8.6)
    if not st.session_state.intro_done:
        st.session_state.intro_done = True
        st.rerun()

else:
    # 5. Nếu intro_done là True, hiển thị trang chính
    main_page(st.session_state.is_mobile)
