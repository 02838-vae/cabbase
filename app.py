def intro_screen(is_mobile=False):
    hide_streamlit_ui()

    video_path = VIDEO_MOBILE if is_mobile else VIDEO_PC
    if not os.path.exists(video_path):
        st.error(f"⚠️ Không tìm thấy video: {video_path}")
        st.session_state.intro_done = True
        st.rerun()
        return

    with open(video_path, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()

    intro_html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <style>
            /* Dùng biến CSS để xử lý lỗi thanh địa chỉ Mobile */
            :root {{
                --dynamic-vh: 100vh; 
            }}
            
            html, body {{
                margin: 0; padding: 0;
                width: 100vw;
                height: var(--dynamic-vh); /* Chiều cao động cho Mobile */
                overflow: hidden; 
                background-color: black;
                font-family: 'Playfair Display', serif;
                touch-action: none;
            }}
            video {{
                position: absolute;
                top: 0; left: 0;
                width: 100vw;
                height: 100%; 
                object-fit: cover;
                /* THAY ĐỔI LỚN: Ưu tiên hiển thị phần DƯỚI cùng của video (nơi có máy bay) */
                object-position: center bottom; 
                z-index: 1;
            }}
            #intro-text {{
                position: absolute;
                left: 50%;
                /* Điều chỉnh vị trí: Đặt dòng chữ cao hơn một chút so với bottom: 18% để tránh bị máy bay che*/
                bottom: 25%; 
                transform: translateX(-50%);
                font-size: clamp(18px, 2.5vw, 40px);
                color: white;
                text-shadow: 2px 2px 6px rgba(0,0,0,0.8);
                z-index: 2;
                animation: fadeInOut 6s ease-in-out forwards;
                text-align: center;
                white-space: nowrap;
            }}
            @keyframes fadeInOut {{
                0% {{ opacity: 0; transform: translate(-50%, 20px); }}
                20% {{ opacity: 1; transform: translate(-50%, 0); }}
                80% {{ opacity: 1; transform: translate(-50%, 0); }}
                100% {{ opacity: 0; transform: translate(-50%, -10px); }}
            }}
            #fade {{
                position: absolute;
                top: 0; left: 0;
                width: 100%;
                height: 100%;
                background: black;
                opacity: 0;
                z-index: 3;
                transition: opacity 1.2s ease-in-out;
            }}
        </style>
    </head>
    <body>
        <video id="introVid" autoplay muted playsinline>
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
        </video>
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="fade"></div>

        <script>
            const vid = document.getElementById("introVid");
            const fade = document.getElementById("fade");
            const root = document.documentElement;

            // XỬ LÝ LỖI MOBILE VIEWPORT
            function setViewportHeight() {{
                let vh = window.innerHeight * 0.01;
                root.style.setProperty('--dynamic-vh', `${{vh * 100}}px`);
            }}

            setViewportHeight();
            window.addEventListener('resize', setViewportHeight);
            window.addEventListener('orientationchange', setViewportHeight);
            
            if ('visualViewport' in window) {{
                window.visualViewport.addEventListener('resize', setViewportHeight);
            }}

            function finishIntro() {{
                fade.style.opacity = 1;
                setTimeout(() => {{
                    window.parent.postMessage({{"type": "intro_done"}}, "*");
                }}, 1000);
            }}

            vid.onended = finishIntro;
            vid.play().catch(() => {{
                console.log("Autoplay bị chặn → fallback");
                setTimeout(finishIntro, 9000);
            }});
        </script>
    </body>
    </html>
    """

    components.html(intro_html, height=1300, scrolling=False)

    # Logic giữ nguyên
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()
    if time.time() - st.session_state.start_time < 9.5:
        time.sleep(1)
        st.rerun()
    else:
        st.session_state.intro_done = True
        st.session_state.start_time = None
        st.rerun()
