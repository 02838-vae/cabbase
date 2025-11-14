# pages/partnumber.py

import streamlit as st
import pandas as pd
import base64
import os

# --- CẤU HÌNH ---
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1 - Tra Cứu PN", layout="wide", initial_sidebar_state="collapsed")

# --- HÀM HỖ TRỢ ---
def get_base64_encoded_file(file_path):
    """Mã hóa file ảnh sang base64."""
    # Sửa đường dẫn để tìm file trong thư mục pages/ hoặc thư mục gốc
    path_to_check = file_path
    if "pages/" not in path_to_check:
        # Thử tìm trong thư mục gốc nếu nó là logo.jpg
        if not os.path.exists(path_to_check):
            path_to_check = os.path.join(os.path.dirname(__file__), file_path)
    
    if not os.path.exists(path_to_check) or os.path.getsize(path_to_check) == 0:
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    try:
        with open(path_to_check, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return "iVBORw0KGgoAAAANHHEAAAABJRU5ErkJggg=="

@st.cache_data(show_spinner="Đang tải dữ liệu...")
def load_and_clean(excel_file, sheet):
    """Tải và làm sạch dữ liệu từ sheet Excel."""
    
    try:
        # Đường dẫn file excel, giả định nó nằm trong thư mục pages/
        excel_path = os.path.join(os.path.dirname(__file__), excel_file.replace("pages/", ""))
        
        df = pd.read_excel(excel_path, sheet_name=sheet)
        df.columns = df.columns.str.strip().str.upper()
        df = df.replace(r'^\s*$', pd.NA, regex=True).dropna(how="all")
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].fillna("").astype(str).str.strip()
            if col in ["A/C", "DESCRIPTION", "ITEM", "PART NUMBER"] and df[col].eq("").all():
                return pd.DataFrame()
        return df
    except Exception as e:
        return pd.DataFrame()

# --- BIẾN VÀ ĐƯỜNG DẪN ---
CHOOSE_PROMPT = "-- CHỌN --"
excel_file = "pages/A787.xlsx" # Giả định file excel nằm cùng cấp với thư mục pages/

try:
    # Cần đảm bảo các file này nằm trong thư mục 'pages/'
    pn_bg_pc_base64 = get_base64_encoded_file("pages/PN_PC.jpg")
    pn_bg_mobile_base64 = get_base64_encoded_file("pages/PN_mobile.jpg")
except Exception as e:
    st.error(f"❌ Lỗi khi đọc file ảnh nền: {str(e)}")
    st.stop()

# --- SETUP MUSIC PLAYER ---
logo_base64 = get_base64_encoded_file("logo.jpg") # Cần đảm bảo file này nằm ở thư mục gốc
if len(logo_base64) < 50: # Kiểm tra lại nếu file logo.jpg không tìm thấy ở thư mục gốc
    logo_base64 = get_base64_encoded_file("pages/logo.jpg")
if len(logo_base64) < 50:
    logo_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

BASE_MUSIC_URL = "https://raw.githubusercontent.com/02838-vae/cabbase/main/"
music_files = [f"{BASE_MUSIC_URL}background{i}.mp3" for i in range(1, 7)]

if len(music_files) == 0:
    st.info("ℹ️ Không tìm thấy URL nhạc nền.")

# --- CSS ---
hide_streamlit_style = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;700&display=swap');
#MainMenu, footer, header {{visibility: hidden;}}

.main {{
    padding: 0;
    margin: 0;
    background-color: transparent !important;
    z-index: 10 !important;
}}

.stApp {{
    --logo-bg-url: url('data:image/jpeg;base64,{logo_base64}');
    background: url("data:image/jpeg;base64,{pn_bg_pc_base64}") no-repeat center top fixed !important;
    background-size: cover !important;
    font-family: 'Oswald', sans-serif !important;
    filter: sepia(0.1) brightness(0.95) contrast(1.05) saturate(1.1) !important;
}}

.main > div:first-child {{
    padding-top: 350px !important;
    padding-left: 20px;
    padding-right: 20px;
}}

@media (max-width: 768px) {{
    .stApp {{
        background: url("data:image/jpeg;base64,{pn_bg_mobile_base64}") no-repeat center top scroll !important;
        background-size: cover !important;
    }}
    .main > div:first-child {{ padding-top: 200px !important; }}
}}

@keyframes scrollText {{
    0% {{ transform: translate(100vw, 0);}}
    100% {{ transform: translate(-100%, 0); }}
}}

@keyframes colorShift {{
    0% {{ background-position: 0% 50%;}}
    50% {{ background-position: 100% 50%;}}
    100% {{ background-position: 0% 50%;}}
}}

#main-title-container {{
    position: static !important;
    width: 100%;
    height: auto;
    overflow: hidden;
    z-index: 995;
    pointer-events: none;
    opacity: 1;
    transition: opacity 2s;
    margin-top: 10px;
    text-align: center;
}}

#main-title-container h1 {{
    font-family: 'Playfair Display', serif;
    font-size: 3vw;
    margin: 0;
    font-weight: 900;
    letter-spacing: 5px;
    white-space: nowrap;
    display: inline-block;
    background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
    background-size: 400% 400%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: colorShift 10s ease infinite, scrollText 15s linear infinite;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    line-height: 1.2;
}}

#main-title-container h1 span.number-fix {{
    font-size: 1em;
    display: inline-block;
    vertical-align: top;
}}

@media (max-width: 768px) {{
    #main-title-container h1 {{
        font-size: 5vw;
        animation-duration: 8s;
    }}
}}

#sub-static-title {{
    position: static;
    margin-top: 20px;
    margin-bottom: 30px;
    z-index: 90;
    background: transparent !important;
    text-align: center;
}}

#sub-static-title h2 {{
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    color: #FFEA00;
    text-align: center;
    text-shadow: 0 0 15px #FFEA00, 0 0 30px rgba(255,234,0,0.8);
    margin-bottom: 20px;
}}

.result-title h3 {{
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    color: #FFEA00;
    text-align: center;
    text-shadow: 0 0 15px #FFEA00, 0 0 30px rgba(255,234,0,0.8);
    margin-bottom: 20px;
}}

@media (max-width: 768px) {{
    #sub-static-title h2, .result-title h3 {{
        font-size: 1.2rem;
        white-space: nowrap;
    }}
}}

@keyframes glow-random-color {{
    0%, 100% {{ box-shadow: 0 0 10px 4px rgba(255, 0, 0, 0.9), 0 0 20px 8px rgba(255, 0, 0, 0.6); }}
    14.28% {{ box-shadow: 0 0 10px 4px rgba(0, 255, 0, 0.9), 0 0 20px 8px rgba(0, 255, 0, 0.6); }}
    28.56% {{ box-shadow: 0 0 10px 4px rgba(0, 0, 255, 0.9), 0 0 20px 8px rgba(0, 0, 255, 0.6); }}
    42.84% {{ box-shadow: 0 0 10px 4px rgba(255, 255, 0, 0.9), 0 0 20px 8px rgba(255, 255, 0, 0.6); }}
    57.14% {{ box-shadow: 0 0 10px 4px rgba(255, 0, 255, 0.9), 0 0 20px 8px rgba(255, 0, 255, 0.6); }}
}}

/* ✅ NÚT VỀ TRANG CHỦ - FIXED */
#back-to-home-btn-container {{
    position: fixed;
    top: 15px;
    left: 15px;
    z-index: 1001;
}}

/* Đã đổi từ #manual-home-btn thành a#manual-home-btn */
a#manual-home-btn {{
    background-color: rgba(0, 0, 0, 0.85);
    color: #FFEA00;
    border: 2px solid #FFEA00;
    padding: 10px 20px;
    border-radius: 8px;
    font-weight: bold;
    font-size: 16px;
    transition: all 0.3s;
    cursor: pointer;
    font-family: 'Oswald', sans-serif;
    text-decoration: none;
    display: inline-block;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
}}

a#manual-home-btn:hover {{
    background-color: #FFEA00;
    color: black;
    transform: scale(1.05);
}}

/* --- MUSIC PLAYER STYLES --- */
#music-player-container {{
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 350px;
    padding: 10px 16px;
    background: rgba(0, 0, 0, 0.85);
    border-radius: 12px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7);
    z-index: 999;
    opacity: 1;
}}

#music-player-container::before {{
    content: '';
    position: absolute;
    top: -3px;
    left: -3px;
    width: calc(100% + 6px);
    height: calc(100% + 6px);
    background-image: var(--logo-bg-url);
    background-size: cover;
    background-position: center;
    filter: contrast(110%) brightness(90%);
    opacity: 0.4;
    z-index: -1;
    border-radius: 12px;
    animation: glow-random-color 7s linear infinite;
}}

#music-player-container * {{
    position: relative;
    z-index: 5;
}}

#music-player-container .controls,
#music-player-container .time-info {{
    color: #fff;
    text-shadow: 0 0 7px #000;
}}

#music-player-container .controls {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin-bottom: 8px;
}}

#music-player-container .control-btn {{
    background: rgba(255, 255, 255, 0.2);
    border: 2px solid #FFFFFF;
    color: #FFD700;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    font-size: 16px;
    font-weight: bold;
}}

#music-player-container .control-btn:hover {{
    background: rgba(255, 215, 0, 0.5);
    transform: scale(1.15);
}}

#music-player-container .control-btn.play-pause {{
    width: 44px;
    height: 44px;
    font-size: 20px;
}}

#music-player-container .progress-container {{
    width: 100%;
    height: 6px;
    background: rgba(0, 0, 0, 0.5);
    border-radius: 3px;
    cursor: pointer;
    margin-bottom: 6px;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.4);
}}

#music-player-container .progress-bar {{
    height: 100%;
    background: linear-gradient(90deg, #FFD700, #FFA500);
    border-radius: 3px;
    width: 0%;
    transition: width 0.1s linear;
}}

#music-player-container .time-info {{
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    font-family: monospace;
}}

@media (max-width: 768px) {{
    #music-player-container {{
        width: calc(100% - 40px);
        right: 20px;
        left: 20px;
        bottom: 15px;
        padding: 10px 12px;
    }}
    #music-player-container .control-btn {{
        width: 40px;
        height: 40px;
        font-size: 18px;
    }}
    #music-player-container .control-btn.play-pause {{
        width: 48px;
        height: 48px;
        font-size: 22px;
    }}
}}

/* --- CSS CHO DROPDOWN & BẢNG KẾT QUẢ --- */
div.stSelectbox label p, div[data-testid*="column"] label p {{
    color: #00FF00 !important;
    font-size: 1.25rem !important;
    font-weight: bold;
    text-shadow: 0 0 5px rgba(0,255,0,0.5);
}}

.stSelectbox div[data-baseweb="select"] {{
    background-color: rgba(0, 0, 0, 0.7);
    border: 1px solid #00FF00;
    border-radius: 8px;
}}

.stSelectbox div[data-baseweb="select"] div[data-testid="stTextInput"] {{
    color: #FFFFFF !important;
}}

.custom-table th {{
    background-color: #1E8449 !important;
    color: #FFFFFF !important;
    padding: 14px;
    border: 2px solid #2ECC71;
    font-size: 1.1rem;
    font-weight: bold;
    text-align: center !important;
    font-family: 'Oswald', sans-serif;
}}

.custom-table td {{
    padding: 12px;
    text-align: center !important;
    border: 1px solid #333333;
    vertical-align: middle;
    font-size: 1rem;
    color: #000000;
    background-color: #FFFFFF !important;
    font-family: Arial, sans-serif;
}}

.table-container {{
    display: flex;
    justify-content: flex-start;
    width: 100%;
    margin-top: 20px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    padding-bottom: 15px;
}}

.custom-table {{
    min-width: 100%;
    width: max-content;
    margin: 0;
    border-collapse: collapse;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
}}

</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- LOGIC CHÍNH ---

# ✅ NÚT VỀ TRANG CHỦ - ĐÃ CHỈNH SỬA SỬ DỤNG THẺ <a>
st.markdown("""
<div id="back-to-home-btn-container">
    <a id="manual-home-btn" href="/?skip_intro=1" target="_self">
        🏠 Về Trang Chủ
    </a>
</div>
""", unsafe_allow_html=True)


# --- HIỂN THỊ TIÊU ĐỀ ---
main_title_text = "TỔ BẢO DƯỠNG SỐ <span class='number-fix'>1</span>"
st.markdown(f'<div id="main-title-container"><h1>{main_title_text}</h1></div>', unsafe_allow_html=True)
st.markdown('<div id="sub-static-title"><h2>TRA CỨU PART NUMBER</h2></div>', unsafe_allow_html=True)

# --- DROPDOWN & XỬ LÝ DỮ LIỆU ---
try:
    if not os.path.exists(excel_file):
        st.error(f"❌ Không tìm thấy file Excel: {excel_file}")
        st.stop()

    excel_path = os.path.join(os.path.dirname(__file__), excel_file.replace("pages/", ""))
    sheet_names = pd.ExcelFile(excel_path).sheet_names
except Exception as e:
    st.error(f"❌ Lỗi khi đọc file Excel: {str(e)}")
    st.stop()

sheet_options = [CHOOSE_PROMPT] + sheet_names

st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
df_base = pd.DataFrame()
df_filtered = pd.DataFrame()
aircraft = CHOOSE_PROMPT
desc = CHOOSE_PROMPT
item = CHOOSE_PROMPT

with col1:
    zone = st.selectbox("📂 Zone", sheet_options, key="zone_select")
zone_selected = (zone and zone != CHOOSE_PROMPT)
if zone_selected:
    df_base = load_and_clean(excel_file, zone)
    df_filtered = df_base.copy()

ac_exists = "A/C" in df_base.columns
aircraft_selected = False
if zone_selected and ac_exists:
    aircraft_options = [CHOOSE_PROMPT] + sorted(df_base["A/C"].dropna().unique().tolist())
    with col2:
        aircraft = st.selectbox("✈️ Loại máy bay", aircraft_options, key="aircraft_select")
    aircraft_selected = (aircraft and aircraft != CHOOSE_PROMPT)
    if aircraft_selected:
        df_filtered = df_base[df_base["A/C"] == aircraft].copy()
elif zone_selected:
    aircraft_selected = True
    df_filtered = df_base.copy()

desc_exists = "DESCRIPTION" in df_filtered.columns
desc_selected = False
if aircraft_selected and zone_selected and desc_exists:
    descs_options = [CHOOSE_PROMPT] + sorted(df_filtered["DESCRIPTION"].dropna().unique().tolist())
    with col3:
        desc = st.selectbox("🔑 Mô tả chi tiết", descs_options, key="desc_select")
    desc_selected = (desc and desc != CHOOSE_PROMPT)
    if desc_selected:
        df_filtered = df_filtered[df_filtered["DESCRIPTION"] == desc].copy()

item_exists = "ITEM" in df_filtered.columns
item_selected = False
if (aircraft_selected and zone_selected) and item_exists and (desc_selected or not desc_exists):
    items_options = [CHOOSE_PROMPT] + sorted(df_filtered["ITEM"].dropna().unique().tolist())
    with col4:
        item = st.selectbox("📌 Item", items_options, key="item_select")
    item_selected = (item and item != CHOOSE_PROMPT)
    if item_selected:
        df_filtered = df_filtered[df_filtered["ITEM"] == item].copy()

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("---")

# --- HIỂN THỊ KẾT QUẢ ---
all_criteria_met = zone_selected and aircraft_selected and (desc_selected or not desc_exists) and (item_selected or not item_exists)

if zone_selected:
    if all_criteria_met:
        df_display = df_filtered.copy()

        if "DESCRIPTION" in df_display.columns:
            df_display = df_display.drop(columns=["DESCRIPTION"])
        if "ITEM" in df_display.columns:
            df_display = df_display.drop(columns=["ITEM"])
        if "A/C" in df_display.columns:
            df_display = df_display.drop(columns=["A/C"])

        if len(df_display) > 0:
            st.markdown('<div class="result-title"><h3>KẾT QUẢ TRA CỨU</h3></div>', unsafe_allow_html=True)

            df_display = df_display.reset_index(drop=True)
            df_display.insert(0, "STT", range(1, len(df_display) + 1))

            if "PART NUMBER" in df_display.columns:
                pn_col = df_display.pop("PART NUMBER")
                df_display.insert(1, "PART NUMBER", pn_col)

            html_parts = ['<div class="table-container">']
            html_parts.append('<table class="custom-table">')

            html_parts.append('<thead><tr>')
            for col in df_display.columns:
                html_parts.append(f'<th>{str(col)}</th>')
            html_parts.append('</tr></thead>')

            html_parts.append('<tbody>')
            for idx, row in df_display.iterrows():
                html_parts.append('<tr>')
                for col in df_display.columns:
                    val = row[col]
                    style = "color: #FF69B4; font-weight: bold;" if col == "PART NUMBER" else ""
                    html_parts.append(f'<td style="{style}">{str(val)}</td>')
                html_parts.append('</tr>')
            html_parts.append('</tbody></table>')
            html_parts.append('</div>')

            st.markdown(''.join(html_parts), unsafe_allow_html=True)
        else:
            st.markdown("---")
            st.warning("⚠️ **Không tìm thấy kết quả phù hợp** với các tiêu chí đã chọn.")

    elif not all_criteria_met:
        st.markdown("---")
        prompt_text = "Zone"
        if zone_selected and not aircraft_selected and ac_exists:
            prompt_text = "Loại máy bay"
        elif zone_selected and aircraft_selected and desc_exists and not desc_selected:
            prompt_text = "Mô tả chi tiết"
        elif zone_selected and aircraft_selected and item_exists and (desc_selected or not desc_exists) and not item_selected:
            prompt_text = "Item"

        st.markdown(
            f"""
            <div style='
                text-align: center;
                background-color: rgba(0,255,0, 0.1);
                border: 1px solid #00FF00;
                padding: 10px 25px;
                border-radius: 12px;
                margin: 15px auto;
                max-width: fit-content;
            '>
                <p style='
                    font-size: 1.1rem;
                    margin: 0;
                    text-shadow: 0 0 5px #FFFFE0;
                '>
                    <font color="#FFFFE0">💡 Vui lòng <strong>chọn {prompt_text}</strong> để tiếp tục tra cứu.</font>
                </p>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.markdown("---")
        st.warning("⚠️ **Không có dữ liệu Part Number** trong Zone này.")

# --- MUSIC PLAYER HTML ---
if len(music_files) > 0:
    st.markdown("""
<div id="music-player-container">
    <div class="controls">
        <button class="control-btn" id="prev-btn">⏮</button>
        <button class="control-btn play-pause" id="play-pause-btn">▶</button>
        <button class="control-btn" id="next-btn">⏭</button>
    </div>
    <div class="progress-container" id="progress-container">
        <div class="progress-bar" id="progress-bar"></div>
    </div>
    <div class="time-info">
        <span id="current-time">0:00</span>
        <span id="duration">0:00</span>
    </div>
</div>
""", unsafe_allow_html=True)

    # ✅ JAVASCRIPT KHỞI TẠO MUSIC PLAYER - ĐÃ SỬA LỖI ESCAPING F-STRING
    music_sources_js = ",\n            ".join([f"'{url}'" for url in music_files])

    st.components.v1.html(f"""
    <script>
        console.log("🎵 Initializing partnumber music player (using localStorage for state)");
        // Dùng setTimeout để đảm bảo các button được tạo ra trước
        setTimeout(function() {{
            const musicSources = [
                {music_sources_js}
            ];
            
            if (musicSources.length === 0) {{
                console.error("❌ No music sources");
                return;
            }}
            
            // ✅ LẤY TRẠNG THÁI TỪ LOCALSTORAGE
            let currentTrack = parseInt(localStorage.getItem('st_music_track')) || 0;
            let isPlaying = localStorage.getItem('st_music_playing') === 'true';
            let savedTime = parseFloat(localStorage.getItem('st_music_time')) || 0;
            
            if (currentTrack >= musicSources.length) {{
                currentTrack = 0;
                localStorage.setItem('st_music_track', '0');
            }}
            
            const audio = new Audio();
            audio.volume = 0.3;
            
            const playPauseBtn = window.parent.document.getElementById('play-pause-btn');
            const prevBtn = window.parent.document.getElementById('prev-btn');
            const nextBtn = window.parent.document.getElementById('next-btn');
            const progressBar = window.parent.document.getElementById('progress-bar');
            const progressContainer = window.parent.document.getElementById('progress-container');
            const currentTimeEl = window.parent.document.getElementById('current-time');
            const durationEl = window.parent.document.getElementById('duration');
            
            if (!playPauseBtn || !prevBtn || !nextBtn) {{
                console.error("❌ Music player buttons not found");
                return;
            }}
            
            // ✅ CẬP NHẬT ICON BAN ĐẦU
            if (isPlaying) {{
                 playPauseBtn.textContent = '⏸';
            }} else {{
                 playPauseBtn.textContent = '▶';
            }}

            // ===============================================
            // ✅ KHỐI ĐỊNH NGHĨA HÀM (Đảm bảo định nghĩa trước khi gọi)
            // ===============================================
            
            function formatTime(seconds) {{
                if (isNaN(seconds) || seconds < 0) return '0:00';
                const mins = Math.floor(seconds / 60);
                const secs = Math.floor(seconds % 60);
                return mins + ':' + String(secs).padStart(2, '0');
            }}
            
            function loadTrack(index) {{
                console.log("💿 Loading: " + musicSources[index]);
                audio.src = musicSources[index];
                audio.load();
                
                // ✅ THỬ ÁP DỤNG THỜI GIAN ĐÃ LƯU KHI METADATA ĐƯỢC TẢI
                audio.addEventListener('loadedmetadata', function listener() {{
                    if (index === currentTrack && savedTime > 0) {{
                        audio.currentTime = savedTime;
                        // Đặt lại savedTime để nó không áp dụng khi chuyển bài sau này
                        savedTime = 0; 
                        localStorage.removeItem('st_music_time'); 
                        // ✅ SỬA LỖI PYTHON SYNTAX BẰNG CÁCH ESCAPE DẤU NGOẶC NHỌN PYTHON
                        console.log(`▶️ Continue from ${{formatTime(audio.currentTime)}}`); 
                    }}
                    audio.removeEventListener('loadedmetadata', listener);
                }});
            }}
            
            function togglePlayPause() {{
                if (isPlaying) {{
                    audio.pause();
                    playPauseBtn.textContent = '▶';
                    isPlaying = false;
                    localStorage.setItem('st_music_playing', 'false'); // ✅ LƯU TRẠNG THÁI
                    console.log("⏸ Paused");
                }} else {{
                    audio.play().then(() => {{
                        playPauseBtn.textContent = '⏸';
                        isPlaying = true;
                        localStorage.setItem('st_music_playing', 'true'); // ✅ LƯU TRẠNG THÁI
                        console.log("▶️ Playing");
                    }}).catch(e => {{
                        console.error("❌ Play error:", e.message);
                    }});
                }}
            }}
            
            function nextTrack() {{
                currentTrack = (currentTrack + 1) % musicSources.length;
                loadTrack(currentTrack);
                localStorage.setItem('st_music_track', currentTrack.toString()); // ✅ LƯU TRACK
                localStorage.removeItem('st_music_time'); // ✅ XÓA THỜI GIAN CŨ
                if (isPlaying) audio.play().catch(e => console.error(e));
            }}
            
            function prevTrack() {{
                currentTrack = (currentTrack - 1 + musicSources.length) % musicSources.length;
                loadTrack(currentTrack);
                localStorage.setItem('st_music_track', currentTrack.toString()); // ✅ LƯU TRACK
                localStorage.removeItem('st_music_time'); // ✅ XÓA THỜI GIAN CŨ
                if (isPlaying) audio.play().catch(e => console.error(e));
            }}
            
            // ===============================================
            // ✅ KHỐI XỬ LÝ SỰ KIỆN VÀ KHỞI TẠO
            // ===============================================
            
            audio.addEventListener('timeupdate', () => {{
                if (audio.duration) {{
                    const progress = (audio.currentTime / audio.duration) * 100;
                    progressBar.style.width = progress + '%';
                    currentTimeEl.textContent = formatTime(audio.currentTime);
                    localStorage.setItem('st_music_time', audio.currentTime.toString()); // ✅ LƯU VỊ TRÍ
                }}
            }});
            
            audio.addEventListener('loadedmetadata', () => {{
                durationEl.textContent = formatTime(audio.duration);
            }});
            
            audio.addEventListener('ended', nextTrack);
            
            audio.addEventListener('error', (e) => {{
                console.error("❌ Track load error, skipping");
                nextTrack();
            }});
            
            playPauseBtn.addEventListener('click', togglePlayPause);
            nextBtn.addEventListener('click', nextTrack);
            prevBtn.addEventListener('click', prevTrack);
            
            progressContainer.addEventListener('click', (e) => {{
                const rect = progressContainer.getBoundingClientRect();
                const percent = (e.clientX - rect.left) / rect.width;
                if (!isNaN(audio.duration)) {{
                    audio.currentTime = percent * audio.duration;
                    localStorage.setItem('st_music_time', audio.currentTime.toString()); // ✅ LƯU VỊ TRÍ MỚI
                }}
            }});
            
            loadTrack(currentTrack); // ✅ LOAD BÀI HÁT ĐÃ LƯU
            
            // ✅ NẾU ĐANG PHÁT, BẮT ĐẦU PHÁT LẠI SAU KHI TẢI
            if (isPlaying) {{
                audio.play().catch(e => console.error("Auto play failed:", e.message));
            }}
            
            console.log("✅ Music player ready!");
            
        }}, 1500);
    </script>
    """, height=0)
