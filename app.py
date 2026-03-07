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

bg_pc    = get_base64("cabbase.jpg")
bg_mobile = get_base64("mobile.jpg")

if not bg_pc or not bg_mobile:
    st.error("Thiếu file ảnh nền (cabbase.jpg hoặc mobile.jpg)")
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
    background-image: url('data:image/jpeg;base64,{bg_pc}');
    background-size: cover;
    background-position: center;
    filter: sepia(60%) grayscale(20%) brightness(85%) contrast(110%);
    z-index: 0;
  }}

  @media (max-width: 768px) {{
    #bg {{
      background-image: url('data:image/jpeg;base64,{bg_mobile}');
    }}
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

  .btn {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 1rem 2rem;
    border-radius: 9999px;
    background: hsla(0,0%,12%,1);
    border: none;
    cursor: pointer;
    text-decoration: none;
    color: #fff;
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 1px;
    font-family: sans-serif;
    box-shadow: inset 0 0.5px rgba(255,255,255,0.3), 0 4px 15px rgba(0,0,0,0.5);
    transition: all 0.3s ease;
    min-width: 260px;
    justify-content: center;
  }}

  .btn:hover {{
    background: hsla(0,0%,22%,1);
    box-shadow: 0 0 20px 6px rgba(255,215,0,0.4), inset 0 0.5px rgba(255,255,255,0.3);
    transform: scale(1.05);
  }}

  .btn svg {{
    width: 22px; height: 22px;
    flex-shrink: 0;
  }}

  @media (max-width: 768px) {{
    .btn {{ width: 100%; min-width: unset; padding: 0.9rem 1.5rem; }}
  }}
</style>
</head>
<body>
  <div id="bg"></div>
  <div id="content">
    <a class="btn" href="/partnumber" target="_self">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"/>
      </svg>
      TRA CỨU PART NUMBER
    </a>
    <a class="btn" href="/bank" target="_self">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
      NGÂN HÀNG TRẮC NGHIỆM
    </a>
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
