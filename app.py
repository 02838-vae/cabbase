import streamlit as st
import streamlit.components.v1 as components
import base64
import os


# ===================== CẤU HÌNH CƠ BẢN =====================
st.set_page_config(page_title="Cabbase", layout="wide", page_icon="✈️")

VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"


# ===================== ẨN GIAO DIỆN STREAMLIT =====================
def hide_ui():
    st.markdown("""
    <style>
    #MainMenu, header, footer {visibility:hidden;}
    .block-container {padding:0 !important; margin:0 !important;}
    </style>
    """, unsafe_allow_html=True)


# ===================== HIỂN THỊ INTRO =====================
def intro_component(is_mobile=False):
    hide_ui()
    video_path = VIDEO_MOBILE if is_mobile and os.path.exists(VIDEO_MOBILE) else VIDEO_PC

    if not os.path.exists(video_path):
        st.error(f"❌ Không tìm thấy video: {video_path}")
        st.stop()

    with open(video_path, "rb") as f:
        video_data = base64.b64encode(f.read()).decode()

    html = f"""
    <html>
    <head>
    <style>
    html,body {{
        margin:0; padding:0; height:100%; background:black; overflow:hidden;
    }}
    video {{
        position:fixed; top:0; left:0;
        width:100vw; height:100vh;
        object-fit:cover;
    }}
    #left, #right {{
        position:fixed; top:0; width:50vw; height:100vh;
        background:black; z-index:10;
        transition:all 1.2s ease-in-out;
    }}
    #left {{ left:-50vw; }}
    #right {{ right:-50vw; }}
    body.close #left {{ left:0; }}
    body.close #right {{ right:0; }}
    #fade {{
        position:fixed; inset:0;
        background:black; opacity:0;
        z-index:11; transition:opacity 0.4s ease-in-out;
    }}
    body.fadeout #fade {{ opacity:1; }}
    </style>
    </head>
    <body>
        <video id="introVideo" autoplay playsinline muted>
            <source src="data:video/mp4;base64,{video_data}" type="video/mp4">
        </video>
        <div id="left"></div>
        <div id="right"></div>
        <div id="fade"></div>

        <script>
        const video = document.getElementById("introVideo");
        let done = false;

        video.addEventListener("timeupdate", () => {{
            if (video.currentTime > video.duration - 1.3 && !done) {{
                done = true;
                document.body.classList.add("close");
                setTimeout(() => {{
                    document.body.classList.add("fadeout");
                }}, 900);
            }}
        }});

        video.addEventListener("ended", () => {{
            setTimeout(() => {{
                window.parent.postMessage({{"type":"end_intro"}}, "*");
            }}, 1100);
        }});
        </script>
    </body>
    </html>
    """

    # Không dùng key để tránh TypeError
    components.html(html, height=1080, scrolling=False)


# ===================== TRANG CHÍNH =====================
def main_page(is_mobile=False):
    hide_ui()
    bg_path = BG_MOBILE if is_mobile else BG_PC
    bg_b64 = ""
    if os.path.exists(bg_path):
        with open(bg_path, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    html,body,.stApp {{
        height:100vh !important; margin:0; padding:0;
        background:black; overflow:hidden;
    }}
    .bg {{
        position:fixed; inset:0;
        background: url("data:image/jpeg;base64,{bg_b64}") center/cover no-repeat;
        z-index:1;
    }}
    #left,#right {{
        position:fixed; top:0; width:50vw; height:100vh;
        background:black; z-index:10;
        transition:all 1.2s ease-in-out;
    }}
    #left {{ left:0; }}
    #right {{ right:0; }}
    body.open #left {{ left:-50vw; }}
    body.open #right {{ right:-50vw; }}
    .title {{
        position:absolute; top:10%; width:100%;
        text-align:center; color:white;
        font-size:clamp(30px,5vw,60px);
        font-family:'Playfair Display',serif;
        text-shadow:0 0 18px rgba(0,0,0,0.65);
        z-index:20; opacity:0;
        animation:fadeIn 1.5s ease forwards 0.8s;
    }}
    @keyframes fadeIn {{ to {{ opacity:1; }} }}
    </style>

    <div id="left"></div>
    <div id="right"></div>
    <div class="bg"></div>
    <div class="title">TỔ BẢO DƯỠNG SỐ 1</div>

    <script>
    setTimeout(() => {{
        document.body.classList.add('open');
    }}, 200);
    </script>
    """, unsafe_allow_html=True)


# ===================== ỨNG DỤNG CHÍNH =====================
def main():
    hide_ui()

    if "intro_done" not in st.session_state:
        st.session_state.intro_done = False
    if "is_mobile" not in st.session_state:
        st.session_state.is_mobile = False

    # JS xác định thiết bị (mobile/PC)
    components.html("""
    <script>
    const isMobile = window.innerWidth < 768;
    window.parent.postMessage({type:'set_device', isMobile:isMobile}, '*');
    </script>
    """, height=0)

    # JS nhận tín hiệu kết thúc intro
    components.html("""
    <script>
    window.addEventListener("message", (e)=>{
        if(e.data.type === "end_intro"){
            window.parent.postMessage({type:"streamlit:setComponentValue",value:"end_intro"}, "*");
        }
    });
    </script>
    """, height=0)

    # Hiển thị intro hoặc trang chính
    if not st.session_state.intro_done:
        intro_component(st.session_state.is_mobile)
        st.stop()
    else:
        main_page(st.session_state.is_mobile)


if __name__ == "__main__":
    main()
