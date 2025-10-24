# --- PHẦN CSS CHÍNH (STREAMLIT APP) ---
optimized_css = f"""
<style>
/* Ẩn các thành phần mặc định của Streamlit */
#MainMenu, footer, header {{visibility: hidden;}}

/* Container chính */
div.block-container {{
    padding: 0;
    margin: 0;
    max-width: 100% !important;
}}

/* Iframe video intro */
iframe:first-of-type {{
    transition: opacity 1s ease-out, visibility 1s ease-out;
    opacity: 1;
    visibility: visible;
    width: 100vw !important;
    height: 100vh !important;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1000;
}}

/* Video đã kết thúc */
.video-finished iframe:first-of-type {{
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
    height: 1px !important;
}}

/* Nền full-screen cho main content */
.stApp {{
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
}}

/* Reveal grid */
.reveal-grid {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    display: grid;
    grid-template-columns: repeat(20, 1fr);
    grid-template-rows: repeat(12, 1fr);
    z-index: 500;
    pointer-events: none;
}}

.grid-cell {{
    background-color: white;
    opacity: 1;
    transition: opacity 0.5s ease-out;
}}

.main-content-revealed {{
    background-image: var(--main-bg-url-pc);
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    filter: sepia(30%) grayscale(10%) brightness(95%);
    transition: filter 2s ease-out;
}}

/* Mobile background */
@media (max-width: 768px) {{
    .main-content-revealed {{
        background-image: var(--main-bg-url-mobile);
    }}
    .reveal-grid {{
        grid-template-columns: repeat(10, 1fr);
        grid-template-rows: repeat(20, 1fr);
    }}
}}

/* === TIÊU ĐỀ TRANG CHÍNH (STAY STRONG) === */
#main-title-container {{
    position: fixed;
    top: 5vh;
    left: 50%;
    transform: translate(-50%, 0);
    width: 90%;
    text-align: center;
    z-index: 20;
    pointer-events: none;
}}

#main-title-container h1 {{
    font-family: 'Stay Strong', cursive !important;
    font-size: 3.5vw; 
    margin: 0;
    font-weight: 400;
    letter-spacing: 2px;
    color: white;
    text-shadow: 3px 3px 6px rgba(0,0,0,0.9);
}}

@media (max-width: 768px) {{
    #main-title-container h1 {{
        font-size: 7vw; 
    }}
}}

/* === TIÊU ĐỀ VIDEO INTRO (SACRAMENTO) === */
#intro-text {{
    position: fixed;
    top: 5vh;
    width: 100%;
    text-align: center;
    color: #FFD700;
    font-size: 3vw;
    font-family: 'Sacramento', cursive !important;
    font-weight: 400;
    text-shadow: 3px 3px 6px rgba(0,0,0,0.8);
    z-index: 100;
    pointer-events: none;
    opacity: 0;
    filter: blur(10px);
    transition: opacity 1.5s ease-out, filter 1.5s ease-out;
}}

#intro-text.text-shown {{
    opacity: 1;
    filter: blur(0);
}}

@media (max-width: 768px) {{
    #intro-text {{
        font-size: 6vw;
    }}
}}
</style>
"""

st.markdown(optimized_css, unsafe_allow_html=True)
