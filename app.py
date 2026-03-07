import streamlit as st
import base64
import os

st.set_page_config(
    page_title="Tổ Bảo Dưỡng Số 1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ĐỌC FILE BACKGROUND ---
def get_base64(file_path):
    path = os.path.join(os.path.dirname(__file__), file_path)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

bg_pc_gif  = get_base64("PC.gif")
bg_mob_gif = get_base64("mobile.gif")

if not bg_pc_gif or not bg_mob_gif:
    st.error("Thiếu file GIF nền (PC.gif hoặc mobile.gif)")
    st.stop()

# --- TOÀN BỘ GIAO DIỆN QUA st.components để tránh Streamlit override ---
st.components.v1.html(f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  html, body {{
    width: 100%; height: 100%;
    overflow: hidden;
    background: #000;
  }}

  #bg {{
    position: fixed;
    inset: 0;
    z-index: 0;
    overflow: hidden;
  }}

  #bg img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
    filter: sepia(60%) grayscale(20%) brightness(85%) contrast(110%);
  }}

  #bg img.pc  {{ display: block; }}
  #bg img.mob {{ display: none; }}

  @media (max-width: 768px) {{
    #bg img.pc  {{ display: none; }}
    #bg img.mob {{ display: block; }}
  }}

  #content {{
    position: fixed;
    inset: 0;
    z-index: 10;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 80px;
  }}

  @media (max-width: 768px) {{
    #content {{
      flex-direction: column;
      justify-content: center;
      gap: 20px;
      padding: 0 20px;
    }}
  }}

  /* Wrapper để chứa hiệu ứng ánh sáng chạy vòng */
  .btn-wrap {{
    position: relative;
    border-radius: 9999px;
    padding: 2px; /* độ dày viền sáng */
    min-width: 260px;
    overflow: hidden;
  }}

  /* Ánh sáng vàng chạy vòng quanh */
  .btn-wrap::before {{
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 9999px;
    background: conic-gradient(
      from var(--angle, 0deg),
      transparent 0deg,
      transparent 60deg,
      #ffd700 90deg,
      #fff8a0 110deg,
      #ffd700 130deg,
      transparent 160deg,
      transparent 360deg
    );
    animation: spin-light 2.5s linear infinite;
    z-index: 0;
  }}

  @property --angle {{
    syntax: '<angle>';
    initial-value: 0deg;
    inherits: false;
  }}

  @keyframes spin-light {{
    to {{ --angle: 360deg; }}
  }}

  /* Fallback cho browser không hỗ trợ @property */
  @supports not (background: conic-gradient(from 0deg, red, blue)) {{
    .btn-wrap::before {{
      animation: spin-fallback 2.5s linear infinite;
      background: linear-gradient(90deg, transparent, #ffd700, transparent);
    }}
    @keyframes spin-fallback {{
      0%   {{ transform: rotate(0deg) scale(2); }}
      100% {{ transform: rotate(360deg) scale(2); }}
    }}
  }}

  /* Nền đen bên trong che phần giữa, chỉ lộ viền sáng */
  .btn-wrap::after {{
    content: '';
    position: absolute;
    inset: 2px;
    border-radius: 9999px;
    background: hsla(0,0%,10%,1);
    z-index: 1;
  }}

  .btn {{
    position: relative;
    z-index: 2;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 1rem 2rem;
    border-radius: 9999px;
    background: transparent;
    border: none;
    cursor: pointer;
    text-decoration: none;
    color: #fff;
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 1px;
    font-family: sans-serif;
    width: 100%;
    transition: all 0.3s ease;
  }}

  .btn-wrap:hover .btn {{
    color: #ffd700;
    text-shadow: 0 0 10px rgba(255,215,0,0.7);
  }}

  .btn-wrap:hover::before {{
    animation-duration: 1.2s;
  }}

  .btn svg {{
    width: 22px; height: 22px;
    flex-shrink: 0;
  }}

  @media (max-width: 768px) {{
    .btn-wrap {{ width: 100%; min-width: unset; }}
    .btn {{ padding: 0.9rem 1.5rem; }}
  }}
</style>
</head>
<body>
  <div id="bg">
    <img class="pc"  src="data:image/gif;base64,{bg_pc_gif}"  alt=""/>
    <img class="mob" src="data:image/gif;base64,{bg_mob_gif}" alt=""/>
  </div>
  <div id="content">
    <div class="btn-wrap">
      <a class="btn" href="/partnumber" target="_self">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"/>
        </svg>
        TRA CỨU PART NUMBER
      </a>
    </div>
    <div class="btn-wrap">
      <a class="btn" href="/bank" target="_self">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        NGÂN HÀNG TRẮC NGHIỆM
      </a>
    </div>
  </div>
</body>
</html>
""", height=800, scrolling=False)

# Ẩn toàn bộ UI mặc định của Streamlit
st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
.block-container, section.main, .main {
    padding: 0 !important; margin: 0 !important;
    background: transparent !important;
}
iframe { border: none !important; }
</style>
""", unsafe_allow_html=True)
