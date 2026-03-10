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

bg_pc_jpg  = get_base64("PC.jpg")
bg_mob_jpg = get_base64("mobile.jpg")
logo_b64   = get_base64("logo.jpg") or ""

if not bg_pc_jpg or not bg_mob_jpg:
    st.error("Thiếu file ảnh nền (PC.jpg hoặc mobile.jpg)")
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

  #logo {{
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 20;
    text-align: center;
  }}

  /* Wrapper bọc logo để tạo viền sáng chạy vòng */
  #logo-wrap {{
    position: relative;
    display: inline-block;
    border-radius: 16px;
    padding: 3px;
    overflow: hidden;
  }}

  /* Ánh sáng vàng chạy vòng quanh logo */
  @property --logo-angle {{
    syntax: '<angle>';
    initial-value: 0deg;
    inherits: false;
  }}

  #logo-wrap::before {{
    content: '';
    position: absolute;
    inset: -60%;
    background: conic-gradient(
      from var(--logo-angle, 0deg),
      transparent 0deg,
      transparent 40deg,
      #b8860b 60deg,
      #ffd700 80deg,
      #fffacd 90deg,
      #ffd700 100deg,
      #b8860b 120deg,
      transparent 140deg,
      transparent 360deg
    );
    animation: logo-spin 3s linear infinite;
    z-index: 0;
  }}

  @keyframes logo-spin {{
    to {{ --logo-angle: 360deg; }}
  }}

  /* Fallback cho browser không hỗ trợ @property */
  @supports not (background: conic-gradient(from 0deg, red, blue)) {{
    #logo-wrap::before {{
      inset: 0;
      background: linear-gradient(90deg, transparent, #ffd700, transparent);
      animation: logo-spin-fallback 3s linear infinite;
    }}
    @keyframes logo-spin-fallback {{
      0%   {{ transform: rotate(0deg) scale(3); }}
      100% {{ transform: rotate(360deg) scale(3); }}
    }}
  }}

  /* Nền tối bên trong chỉ lộ viền sáng */
  #logo-wrap::after {{
    content: '';
    position: absolute;
    inset: 3px;
    border-radius: 13px;
    background: rgba(0, 0, 0, 0.45);
    z-index: 1;
  }}

  /* Hào quang ngoài logo */
  #logo-glow {{
    position: absolute;
    inset: -8px;
    border-radius: 22px;
    pointer-events: none;
    animation: logo-glow-pulse 3s ease-in-out infinite;
    box-shadow:
      0 0 14px 4px rgba(255,215,0,0.40),
      0 0 32px 8px rgba(255,215,0,0.18),
      0 0 55px 12px rgba(184,134,11,0.10);
  }}

  @keyframes logo-glow-pulse {{
    0%, 100% {{ opacity: 0.7; }}
    50%       {{ opacity: 1; box-shadow: 0 0 20px 6px rgba(255,215,0,0.60), 0 0 44px 12px rgba(255,215,0,0.28); }}
  }}

  #logo img {{
    position: relative;
    z-index: 2;
    height: 120px;
    width: auto;
    object-fit: contain;
    filter: drop-shadow(0 2px 8px rgba(0,0,0,0.6));
    border-radius: 12px;
    display: block;
  }}

  @media (max-width: 768px) {{
    #logo img {{ height: 55px; }}
    #logo {{ top: 15px; }}
    #logo-wrap {{ border-radius: 12px; padding: 2px; }}
    #logo-wrap::after {{ inset: 2px; border-radius: 10px; }}
    #logo-glow {{ inset: -4px; border-radius: 16px; }}
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
  /* Nền tối bên trong */
  .btn-wrap::after {{
    content: '';
    position: absolute;
    inset: 2px;
    border-radius: 9999px;
    background: hsla(0,0%,10%,1);
    z-index: 1;
  }}

  /* Ánh sáng quét qua - shimmer effect */
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
    overflow: hidden;
  }}

  /* Tia sáng quét qua */
  .btn::before {{
    content: '';
    position: absolute;
    top: 0;
    left: -120%;
    width: 60%;
    height: 100%;
    background: linear-gradient(
      105deg,
      transparent 20%,
      rgba(255, 255, 255, 0.08) 40%,
      rgba(255, 215, 0, 0.18) 50%,
      rgba(255, 255, 255, 0.08) 60%,
      transparent 80%
    );
    transform: skewX(-15deg);
    animation: shimmer 7s ease-in-out infinite;
    z-index: 3;
    pointer-events: none;
    border-radius: 9999px;
  }}

  /* Delay khác nhau cho 2 button */
  .btn-wrap:nth-child(2) .btn::before {{
    animation-delay: 2s;
  }}

  @keyframes shimmer {{
    0%   {{ left: -120%; opacity: 0; }}
    5%   {{ opacity: 1; }}
    45%  {{ left: 130%; opacity: 1; }}
    50%  {{ opacity: 0; }}
    100% {{ left: 130%; opacity: 0; }}
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
    <img class="pc"  src="data:image/jpeg;base64,{bg_pc_jpg}"  alt=""/>
    <img class="mob" src="data:image/jpeg;base64,{bg_mob_jpg}" alt=""/>
  </div>
  <div id="logo">
    <div id="logo-wrap">
      <div id="logo-glow"></div>
      <img src="data:image/jpeg;base64,{logo_b64}" alt="Logo"/>
    </div>
  </div>
  <div id="content">
    <div class="btn-wrap">
      <a class="btn" href="/partnumber" target="_blank">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"/>
        </svg>
        TRA CỨU PART NUMBER
      </a>
    </div>
    <div class="btn-wrap">
      <a class="btn" href="/bank" target="_blank">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25"/>
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 9h.01M9 12h3m-3 3h6"/>
        </svg>
        NGÂN HÀNG TRẮC NGHIỆM
      </a>
    </div>
  </div>
</body>
</html>
""", height=1080, scrolling=False)

# Ẩn toàn bộ UI mặc định của Streamlit
st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
.block-container, section.main, .main {
    padding: 0 !important; margin: 0 !important;
    background: transparent !important;
    height: 100vh !important;
    min-height: 100vh !important;
    overflow: hidden !important;
}
html, body {
    height: 100% !important;
    overflow: hidden !important;
    background: #000 !important;
}
iframe {
    border: none !important;
    width: 100vw !important;
    height: 100vh !important;
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
}
</style>
""", unsafe_allow_html=True)
