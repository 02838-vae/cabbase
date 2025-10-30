import streamlit as st
import base64
import os

# --- CẤU HÌNH BAN ĐẦU ---
st.set_page_config(
    page_title="Tổ Bảo Dưỡng Số 1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Khởi tạo session state
if 'video_ended' not in st.session_state:
    st.session_state.video_ended = False


# --- CÁC HÀM TIỆN ÍCH ---
def get_base64_encoded_file(file_path):
    """Đọc file và trả về Base64 encoded string."""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return None
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    except Exception as e:
        st.error(f"Lỗi khi đọc file {file_path}: {str(e)}")
        return None


# --- MÃ HÓA FILE MEDIA CHÍNH ---
try:
    video_pc_base64 = get_base64_encoded_file("airplane.mp4")
    video_mobile_base64 = get_base64_encoded_file("mobile.mp4")
    audio_base64 = get_base64_encoded_file("plane_fly.mp3")
    bg_pc_base64 = get_base64_encoded_file("cabbase.jpg")
    bg_mobile_base64 = get_base64_encoded_file("mobile.jpg")
    logo_base64 = get_base64_encoded_file("logo.jpg")

    if not all([video_pc_base64, video_mobile_base64, audio_base64, bg_pc_base64, bg_mobile_base64]):
        missing_files = []
        if not video_pc_base64: missing_files.append("airplane.mp4")
        if not video_mobile_base64: missing_files.append("mobile.mp4")
        if not audio_base64: missing_files.append("plane_fly.mp3")
        if not bg_pc_base64: missing_files.append("cabbase.jpg")
        if not bg_mobile_base64: missing_files.append("mobile.jpg")
        st.error("⚠️ Thiếu file media: " + ", ".join(missing_files))
        st.stop()

except Exception as e:
    st.error(f"❌ Lỗi khi đọc file: {str(e)}")
    st.stop()

if not logo_base64:
    logo_base64 = ""
    st.info("ℹ️ Không tìm thấy file logo.jpg")


# --- NHẠC NỀN (TÙY CHỌN) ---
music_files = []
for i in range(1, 7):
    music_base64 = get_base64_encoded_file(f"background{i}.mp3")
    if music_base64:
        music_files.append(music_base64)


# --- NHÚNG FONT ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Sacramento&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)


# --- CSS CHÍNH ---
st.markdown(f"""
<style>
#MainMenu, footer, header {{visibility: hidden;}}
.main, div.block-container {{padding: 0; margin: 0; max-width: 100% !important;}}

/* NỀN CHÍNH */
.stApp {{
    --main-bg-url-pc: url('data:image/jpeg;base64,{bg_pc_base64}');
    --main-bg-url-mobile: url('data:image/jpeg;base64,{bg_mobile_base64}');
}}
.main-content-revealed {{
    background-image: var(--main-bg-url-pc);
    background-size: cover;
    background-position: center;
    filter: sepia(60%) grayscale(20%) brightness(85%) contrast(110%);
}}
@media (max-width:768px) {{
    .main-content-revealed {{
        background-image: var(--main-bg-url-mobile);
    }}
}}

/* TIÊU ĐỀ CHÍNH */
#main-title-container {{
    position: fixed;
    top: 5vh;
    left: 0;
    width: 100%;
    height: 10vh;
    z-index: 20;
    text-align: center;
    opacity: 0;
    transition: opacity 2s;
}}
.video-finished #main-title-container {{opacity: 1;}}
#main-title-container h1 {{
    font-family: 'Playfair Display', serif;
    font-size: 3.5vw;
    font-weight: 900;
    letter-spacing: 5px;
    animation: colorShift 10s ease infinite;
    background: linear-gradient(90deg, #ff0000, #ffff00, #00ff00, #00ffff, #ff00ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}
@keyframes colorShift {{
    0% {{background-position: 0% 50%;}}
    50% {{background-position: 100% 50%;}}
    100% {{background-position: 0% 50%;}}
}}

/* 🌟 2 TIÊU ĐỀ PHỤ 🌟 */
#sub-title-container {{
    position: fixed;
    top: 18vh;
    left: 0;
    width: 100%;
    display: flex;
    justify-content: space-between;
    padding: 0 5vw;
    z-index: 30;
    opacity: 0;
    transition: opacity 2s ease 2s;
}}
.video-finished #sub-title-container {{opacity: 1;}}

.sub-box {{
    flex: 0 0 40%;
    background: rgba(255,255,255,0.08);
    border: 2px solid rgba(255,255,255,0.6);
    color: #fff;
    text-align: center;
    font-family: 'Playfair Display', serif;
    font-weight: 600;
    font-size: 1.8vw;
    padding: 1.2em 0;
    border-radius: 15px;
    cursor: pointer;
    backdrop-filter: blur(5px);
    transition: all 0.3s ease;
    box-shadow: 0 0 12px rgba(255,255,255,0.2);
}}
.sub-box:hover {{
    transform: scale(1.05);
    box-shadow: 0 0 20px rgba(255,255,255,0.6);
    border-color: rgba(255,255,255,0.9);
}}

@media (max-width:768px) {{
    #sub-title-container {{
        position: absolute;
        top: 55vh;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        gap: 20px;
        padding: 0;
    }}
    .sub-box {{
        width: 80%;
        font-size: 4.5vw;
        padding: 1em 0;
        border-radius: 20px;
    }}
}}
</style>
""", unsafe_allow_html=True)


# --- IFRAME VIDEO INTRO ---
video_html = f"""
<video id="intro-video" muted playsinline style="width:100vw;height:100vh;object-fit:cover;position:fixed;top:0;left:0;z-index:1000;">
    <source src="data:video/mp4;base64,{video_pc_base64}" type="video/mp4">
</video>
<script>
const video = document.getElementById('intro-video');
video.play().catch(()=>{{setTimeout(()=>window.parent.document.querySelector('.stApp').classList.add('video-finished','main-content-revealed'),2000);}});
video.addEventListener('ended',()=>{
    const app = window.parent.document.querySelector('.stApp');
    app.classList.add('video-finished','main-content-revealed');
});
</script>
"""
st.components.v1.html(video_html, height=1080, scrolling=False)


# --- TIÊU ĐỀ CHÍNH ---
main_title_text = "TỔ BẢO DƯỠNG SỐ 1"
st.markdown(f"""
<div id="main-title-container">
    <h1>{main_title_text}</h1>
</div>
""", unsafe_allow_html=True)


# --- 2 TIÊU ĐỀ PHỤ ---
st.markdown("""
<div id="sub-title-container">
    <div class="sub-box" onclick="window.location.href='tracuu'">
        Tra cứu Part Number
    </div>
    <div class="sub-box" onclick="window.location.href='nganhang'">
        Ngân hàng Trắc nghiệm
    </div>
</div>
""", unsafe_allow_html=True)


# --- NỘI DUNG CHÍNH ---
st.markdown("<br><br><br><br><h2 style='text-align:center;color:white;'>Nội dung chính sẽ được bổ sung ở đây</h2>", unsafe_allow_html=True)
