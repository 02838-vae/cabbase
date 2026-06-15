import streamlit as st

st.set_page_config(
    page_title="Tổ Bảo Dưỡng Số 1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ẩn UI mặc định Streamlit
st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
.block-container, section.main, .main {
    padding: 0 !important; margin: 0 !important;
    background: transparent !important;
    height: 100vh !important;
    overflow: hidden !important;
}
iframe {
    border: none !important;
    width: 100vw !important;
    height: 100vh !important;
    position: fixed !important;
    top: 0 !important; left: 0 !important;
}
</style>
""", unsafe_allow_html=True)

st.components.v1.html("""
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<style>
  *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

  html, body {
    height: 100%;
    background: #ffffff;
    font-family: 'Inter', sans-serif;
  }

  .page {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 24px;
  }

  .plane-wrap {
    margin-bottom: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .plane-icon {
    width: 72px;
    height: 72px;
    color: #1d6fc4;
    filter: drop-shadow(0 4px 16px rgba(29,111,196,0.18));
  }

  .btn-stack {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    width: 100%;
    max-width: 320px;
  }

  .btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    width: 100%;
    padding: 14px 28px;
    border-radius: 8px;
    font-size: 0.875rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    text-decoration: none;
    cursor: pointer;
    transition: background 0.2s, box-shadow 0.2s, transform 0.15s;
    border: 2px solid #1d6fc4;
    background: #ffffff;
    color: #1d6fc4;
  }

  .btn:hover {
    background: #f0f6ff;
    box-shadow: 0 4px 18px rgba(29,111,196,0.12);
    transform: translateY(-1px);
  }

  .btn svg {
    width: 18px;
    height: 18px;
    flex-shrink: 0;
  }
</style>
</head>
<body>
<div class="page">

  <div class="plane-wrap">
    <svg class="plane-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
         fill="none" stroke="#1d6fc4" stroke-width="1.5"
         stroke-linecap="round" stroke-linejoin="round">
      <path d="M22 2L11 13"/>
      <path d="M22 2L15 22L11 13L2 9L22 2Z"/>
    </svg>
  </div>

  <div class="btn-stack">
    <a class="btn" href="/partnumber" target="_blank">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
           stroke-width="2" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round"
              d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"/>
      </svg>
      Tra Cứu Part Number
    </a>

    <a class="btn" href="/bank" target="_blank">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
           stroke-width="1.8" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round"
              d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25"/>
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 9h.01M9 12h3m-3 3h6"/>
      </svg>
      Ngân Hàng Trắc Nghiệm
    </a>
  </div>

</div>
</body>
</html>
""", height=800, scrolling=False)
