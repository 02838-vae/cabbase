import streamlit as st
import base64
import os
import pandas as pd

st.set_page_config(
    page_title="Tổ Bảo Dưỡng Số 1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ĐỌC FILE ---
def get_base64(file_path):
    path = os.path.join(os.path.dirname(__file__), file_path)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

bg_gif     = get_base64("aircraft.gif")
bg_pc_jpg  = get_base64("cabbase.jpg")
bg_mob_jpg = get_base64("mobile.jpg")
logo_b64   = get_base64("logo.jpg") or ""

if bg_gif:
    bg_pc_src  = f"data:image/gif;base64,{bg_gif}"
    bg_mob_src = f"data:image/gif;base64,{bg_gif}"
elif bg_pc_jpg:
    bg_pc_src  = f"data:image/jpeg;base64,{bg_pc_jpg}"
    bg_mob_src = f"data:image/jpeg;base64,{bg_mob_jpg}" if bg_mob_jpg else bg_pc_src
else:
    st.error("Thiếu file ảnh nền")
    st.stop()

# --- SESSION STATE ---
if "page" not in st.session_state:
    st.session_state.page = "home"

# Sync từ query param khi load lần đầu
params = st.query_params.to_dict()
if params.get("page") == "partnumber" and st.session_state.page == "home":
    st.session_state.page = "partnumber"

# --- EXCEL LOADER ---
CHOOSE  = "-- CHỌN --"
EXCEL   = "A787.xlsx"

@st.cache_data(show_spinner="Đang tải dữ liệu...")
def load_sheet(sheet):
    try:
        path = os.path.join(os.path.dirname(__file__), EXCEL)
        df = pd.read_excel(path, sheet_name=sheet)
        df.columns = df.columns.str.strip().str.upper()
        df = df.replace(r'^\s*$', pd.NA, regex=True).dropna(how="all")
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].fillna("").astype(str).str.strip()
        return df
    except Exception:
        return pd.DataFrame()

# ===================== CSS =====================
is_pn = st.session_state.page == "partnumber"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Oswald:wght@500;700&display=swap');

#MainMenu, footer, header {{ visibility: hidden; }}

html, body {{
    height: 100% !important;
    background: #000 !important;
    overflow: {'auto' if is_pn else 'hidden'} !important;
}}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
.block-container, section.main, .main {{
    padding: 0 !important; margin: 0 !important;
    background: transparent !important;
    overflow: {'visible' if is_pn else 'hidden'} !important;
}}
iframe {{
    border: none !important;
    width: 100vw !important;
    height: {'0' if is_pn else '100vh'} !important;
    position: {'relative' if is_pn else 'fixed'} !important;
    top: 0 !important; left: 0 !important;
    pointer-events: {'none' if is_pn else 'all'} !important;
}}

/* ---- TRANG TRA CỨU ---- */
#pn-page {{
    position: relative;
    z-index: 50;
    min-height: 100vh;
    padding: 120px 40px 60px;
    font-family: 'Oswald', sans-serif;
}}

/* Background fixed cho trang tra cứu */
#pn-page::before {{
    content: '';
    position: fixed;
    inset: 0;
    background-image: url('{bg_pc_src}');
    background-size: cover;
    background-position: center;
    filter: sepia(60%) grayscale(20%) brightness(85%) contrast(110%);
    z-index: -1;
}}

/* Logo fixed */
#pn-logo {{
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 100;
    text-align: center;
}}
#pn-logo img {{
    height: 75px;
    width: auto;
    filter: drop-shadow(0 2px 8px rgba(0,0,0,0.7));
    border-radius: 8px;
}}

#pn-title {{
    text-align: center;
    font-family: 'Playfair Display', serif;
    font-size: clamp(1.4rem, 3vw, 2rem);
    color: #FFEA00;
    text-shadow: 0 0 15px #FFEA00, 0 0 30px rgba(255,234,0,0.5);
    margin-bottom: 28px;
    letter-spacing: 3px;
}}

/* Nút về trang chủ */
.stButton > button {{
    background: rgba(0,0,0,0.85) !important;
    color: #FFEA00 !important;
    border: 2px solid #FFEA00 !important;
    padding: 8px 20px !important;
    border-radius: 8px !important;
    font-family: 'Oswald', sans-serif !important;
    font-weight: bold !important;
    font-size: 15px !important;
    transition: all 0.3s !important;
}}
.stButton > button:hover {{
    background: #FFEA00 !important;
    color: #000 !important;
    transform: scale(1.05) !important;
}}

/* Dropdowns */
div.stSelectbox label p {{
    color: #00FF00 !important;
    font-size: 1.05rem !important;
    font-weight: bold;
    text-shadow: 0 0 5px rgba(0,255,0,0.4);
    font-family: 'Oswald', sans-serif !important;
}}
.stSelectbox div[data-baseweb="select"] {{
    background-color: rgba(0,0,0,0.75) !important;
    border: 1px solid #00FF00 !important;
    border-radius: 8px !important;
}}
.stSelectbox div[data-baseweb="select"] * {{
    color: #fff !important;
}}
ul[data-testid="stSelectboxVirtualDropdown"] {{
    background: #111 !important;
}}
ul[data-testid="stSelectboxVirtualDropdown"] li {{
    color: #fff !important;
}}

hr {{ border-color: rgba(255,255,255,0.2) !important; }}

/* Bảng kết quả */
.result-title {{
    text-align: center;
    font-family: 'Playfair Display', serif;
    font-size: clamp(1.1rem, 2.5vw, 1.7rem);
    color: #FFEA00;
    text-shadow: 0 0 12px #FFEA00;
    margin: 16px 0 8px;
}}
.table-wrap {{
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    padding-bottom: 20px;
}}
.custom-table {{
    width: max-content; min-width: 100%;
    border-collapse: collapse;
    box-shadow: 0 4px 20px rgba(0,0,0,0.6);
}}
.custom-table th {{
    background: #1E8449 !important; color: #fff !important;
    padding: 12px 16px; border: 2px solid #2ECC71;
    font-size: 1rem; font-weight: bold; text-align: center;
    font-family: 'Oswald', sans-serif; white-space: nowrap;
}}
.custom-table td {{
    padding: 10px 14px; text-align: center;
    border: 1px solid #333;
    background: #fff !important; color: #000 !important;
    font-size: 0.95rem; font-family: Arial, sans-serif; white-space: nowrap;
}}
.pn-cell {{ color: #C0392B !important; font-weight: bold !important; }}
.hint-box {{
    text-align: center;
    background: rgba(0,255,0,0.08);
    border: 1px solid #00FF00;
    border-radius: 10px;
    padding: 12px 24px;
    margin: 15px auto;
    max-width: fit-content;
    color: #FFFFE0;
    font-size: 1rem;
    font-family: 'Oswald', sans-serif;
}}

@media(max-width:768px) {{
    #pn-page {{ padding: 110px 16px 40px; }}
    #pn-logo img {{ height: 55px; }}
}}
</style>
""", unsafe_allow_html=True)

# ===================== IFRAME NỀN (trang chủ) =====================
if st.session_state.page == "home":
    st.components.v1.html(f"""
<!DOCTYPE html><html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  *{{margin:0;padding:0;box-sizing:border-box;}}
  html,body{{width:100%;height:100%;overflow:hidden;background:#000;}}

  #bg{{position:fixed;inset:0;z-index:0;overflow:hidden;}}
  #bg img{{width:100%;height:100%;object-fit:cover;object-position:center;
           filter:sepia(60%) grayscale(20%) brightness(85%) contrast(110%);}}
  .pc{{display:block;}} .mob{{display:none;}}
  @media(max-width:768px){{.pc{{display:none;}}.mob{{display:block;}}}}

  #logo{{position:fixed;top:20px;left:50%;transform:translateX(-50%);z-index:20;}}
  #logo img{{height:80px;width:auto;filter:drop-shadow(0 2px 8px rgba(0,0,0,0.7));border-radius:8px;}}
  @media(max-width:768px){{#logo img{{height:55px;}}#logo{{top:12px;}}}}

  #content{{
    position:fixed;inset:0;z-index:10;
    display:flex;align-items:center;justify-content:space-between;padding:0 80px;
  }}
  @media(max-width:768px){{
    #content{{flex-direction:column;justify-content:center;gap:20px;padding:0 20px;}}
  }}

  @property --angle{{syntax:'<angle>';initial-value:0deg;inherits:false;}}
  @keyframes spin-light{{to{{--angle:360deg;}}}}
  @keyframes shimmer{{
    0%{{left:-120%;opacity:0;}}5%{{opacity:1;}}
    45%{{left:130%;opacity:1;}}50%{{opacity:0;}}100%{{left:130%;opacity:0;}}
  }}

  .btn-wrap{{position:relative;border-radius:9999px;padding:2px;min-width:260px;overflow:hidden;}}
  .btn-wrap::before{{
    content:'';position:absolute;inset:0;border-radius:9999px;
    background:conic-gradient(from var(--angle,0deg),
      transparent 0deg,transparent 60deg,#ffd700 90deg,
      #fff8a0 110deg,#ffd700 130deg,transparent 160deg,transparent 360deg);
    animation:spin-light 2.5s linear infinite;z-index:0;
  }}
  .btn-wrap::after{{
    content:'';position:absolute;inset:2px;border-radius:9999px;
    background:hsla(0,0%,10%,1);z-index:1;
  }}
  .btn{{
    position:relative;z-index:2;
    display:flex;align-items:center;justify-content:center;gap:12px;
    padding:1rem 2rem;border-radius:9999px;background:transparent;
    border:none;cursor:pointer;text-decoration:none;color:#fff;
    font-size:1rem;font-weight:600;letter-spacing:1px;
    font-family:sans-serif;width:100%;transition:all 0.3s;overflow:hidden;
  }}
  .btn::before{{
    content:'';position:absolute;top:0;left:-120%;width:60%;height:100%;
    background:linear-gradient(105deg,transparent 20%,rgba(255,255,255,0.08) 40%,
      rgba(255,215,0,0.18) 50%,rgba(255,255,255,0.08) 60%,transparent 80%);
    transform:skewX(-15deg);animation:shimmer 7s ease-in-out infinite;
    z-index:3;pointer-events:none;
  }}
  .btn-wrap:nth-child(2) .btn::before{{animation-delay:2s;}}
  .btn-wrap:hover .btn{{color:#ffd700;text-shadow:0 0 10px rgba(255,215,0,0.7);}}
  .btn-wrap:hover::before{{animation-duration:1.2s;}}
  .btn svg{{width:22px;height:22px;flex-shrink:0;}}
  @media(max-width:768px){{
    .btn-wrap{{width:100%;min-width:unset;}}
    .btn{{padding:0.9rem 1.5rem;}}
  }}
</style>
</head>
<body>
  <div id="bg">
    <img class="pc"  src="{bg_pc_src}"  alt=""/>
    <img class="mob" src="{bg_mob_src}" alt=""/>
  </div>
  <div id="logo"><img src="data:image/jpeg;base64,{logo_b64}" alt="Logo"/></div>
  <div id="content">
    <div class="btn-wrap">
      <a class="btn" href="?page=partnumber" target="_self">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"/>
        </svg>
        TRA CỨU PART NUMBER
      </a>
    </div>
    <div class="btn-wrap">
      <a class="btn" href="/bank" target="_self">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25"/>
        </svg>
        NGÂN HÀNG TRẮC NGHIỆM
      </a>
    </div>
  </div>
</body>
</html>
""", height=1080, scrolling=False)

# ===================== TRANG TRA CỨU =====================
elif st.session_state.page == "partnumber":

    st.markdown(f'<div id="pn-logo"><img src="data:image/jpeg;base64,{logo_b64}" alt="Logo"/></div>', unsafe_allow_html=True)
    st.markdown('<div id="pn-page">', unsafe_allow_html=True)

    if st.button("🏠 Về Trang Chủ", key="back_home"):
        st.session_state.page = "home"
        st.query_params.clear()
        for k in ["zone_sel","ac_sel","desc_sel","item_sel"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    st.markdown('<div id="pn-title">TRA CỨU PART NUMBER</div>', unsafe_allow_html=True)

    excel_path = os.path.join(os.path.dirname(__file__), EXCEL)
    try:
        sheet_names = pd.ExcelFile(excel_path).sheet_names
    except Exception as e:
        st.error(f"Không mở được file {EXCEL}: {e}")
        st.stop()

    col1, col2, col3, col4 = st.columns(4)
    df_base = pd.DataFrame()
    df_filt = pd.DataFrame()

    with col1:
        zone = st.selectbox("📂 Zone", [CHOOSE] + sheet_names, key="zone_sel")
    zone_ok = zone != CHOOSE
    if zone_ok:
        df_base = load_sheet(zone)
        df_filt  = df_base.copy()

    ac_ok = False
    if zone_ok and "A/C" in df_base.columns:
        with col2:
            ac = st.selectbox("✈️ Loại máy bay", [CHOOSE] + sorted(df_base["A/C"].dropna().unique().tolist()), key="ac_sel")
        ac_ok = ac != CHOOSE
        if ac_ok:
            df_filt = df_base[df_base["A/C"] == ac].copy()
    elif zone_ok:
        ac_ok = True

    desc_ok = False
    if zone_ok and ac_ok and "DESCRIPTION" in df_filt.columns:
        with col3:
            desc = st.selectbox("🔑 Mô tả chi tiết", [CHOOSE] + sorted(df_filt["DESCRIPTION"].dropna().unique().tolist()), key="desc_sel")
        desc_ok = desc != CHOOSE
        if desc_ok:
            df_filt = df_filt[df_filt["DESCRIPTION"] == desc].copy()
    elif zone_ok and ac_ok:
        desc_ok = True

    item_ok = False
    if zone_ok and ac_ok and desc_ok and "ITEM" in df_filt.columns:
        with col4:
            item = st.selectbox("🔌 Item", [CHOOSE] + sorted(df_filt["ITEM"].dropna().unique().tolist()), key="item_sel")
        item_ok = item != CHOOSE
        if item_ok:
            df_filt = df_filt[df_filt["ITEM"] == item].copy()
    elif zone_ok and ac_ok and desc_ok:
        item_ok = True

    all_ok = zone_ok and ac_ok and desc_ok and item_ok
    st.markdown("---")

    if not zone_ok:
        st.markdown('<div class="hint-box">💡 Vui lòng <strong>chọn Zone</strong> để bắt đầu tra cứu.</div>', unsafe_allow_html=True)
    elif not all_ok:
        nf = ("Loại máy bay" if not ac_ok and "A/C" in df_base.columns
              else "Mô tả chi tiết" if not desc_ok and "DESCRIPTION" in df_filt.columns
              else "Item")
        st.markdown(f'<div class="hint-box">💡 Vui lòng <strong>chọn {nf}</strong> để tiếp tục.</div>', unsafe_allow_html=True)
    else:
        df_show = df_filt.copy()
        for c in ["A/C","DESCRIPTION","ITEM"]:
            if c in df_show.columns:
                df_show.drop(columns=[c], inplace=True)

        if len(df_show) == 0:
            st.warning("⚠️ Không tìm thấy kết quả phù hợp.")
        else:
            st.markdown('<div class="result-title">KẾT QUẢ TRA CỨU</div>', unsafe_allow_html=True)
            df_show = df_show.reset_index(drop=True)
            df_show.insert(0, "STT", range(1, len(df_show) + 1))
            if "PART NUMBER" in df_show.columns:
                pn = df_show.pop("PART NUMBER")
                df_show.insert(1, "PART NUMBER", pn)

            headers = "".join(f"<th>{c}</th>" for c in df_show.columns)
            rows = ""
            for _, row in df_show.iterrows():
                rows += "<tr>"
                for c in df_show.columns:
                    cls = ' class="pn-cell"' if c == "PART NUMBER" else ""
                    rows += f"<td{cls}>{row[c]}</td>"
                rows += "</tr>"

            st.markdown(f"""
            <div class="table-wrap">
              <table class="custom-table">
                <thead><tr>{headers}</tr></thead>
                <tbody>{rows}</tbody>
              </table>
            </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
