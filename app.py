def intro_screen_inline_main(is_mobile=False):
    hide_streamlit_ui()
    video_file = VIDEO_MOBILE if is_mobile else VIDEO_PC
    bg_file = BG_MOBILE if is_mobile else BG_PC
    
    with open(video_file, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode()
    with open(SFX, "rb") as a:
        audio_b64 = base64.b64encode(a.read()).decode()
    with open(bg_file, "rb") as b:
        bg_b64 = base64.b64encode(b.read()).decode()
    
    main_html = f"""
    <div id="main-page" style="display:none; height:100vh; width:100vw; 
        background: url('data:image/jpeg;base64,{bg_b64}') no-repeat center center; 
        background-size: cover; position:absolute; top:0; left:0;">
        <h1 style="text-align:center; margin-top:10vh; color:white; font-size:4vw; 
            font-family:'Playfair Display', serif;">TỔ BẢO DƯỠNG SỐ 1</h1>
    </div>
    """
    
    intro_html = f"""
    <video id="intro-video" muted playsinline webkit-playsinline 
        style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover;">
        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
    </video>
    <audio id="intro-audio" preload="auto">
        <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
    </audio>
    {main_html}
    <script>
    const vid = document.getElementById('intro-video');
    const audio = document.getElementById('intro-audio');
    const mainPage = document.getElementById('main-page');

    function finishIntro() {{
        vid.style.display = 'none';
        audio.pause();
        mainPage.style.display = 'block';
    }}

    vid.addEventListener('canplay', () => vid.play().catch(()=>{{}}));
    vid.addEventListener('play', () => {{
        audio.volume = 1.0; audio.currentTime=0; audio.play().catch(()=>{{}});
    }});
    vid.addEventListener('ended', finishIntro);
    document.addEventListener('click', () => {{
        vid.muted = false; vid.play(); audio.play().catch(()=>{{}});
    }}, {{once:true}});
    </script>
    """
    
    components.html(intro_html, height=800, scrolling=False)
