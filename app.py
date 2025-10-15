# ---------- TRANG CHÍNH ----------
st.session_state.intro_done = True

bg_path = "cabbase.jpg"

if os.path.exists(bg_path):
    bg_base64 = get_base64(bg_path)
    background_css = f"""
        <style>
        /* Làm nền phủ toàn bộ app */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], [data-testid="stVerticalBlock"] {{
            background: url("data:image/jpeg;base64,{bg_base64}") no-repeat center center fixed !important;
            background-size: cover !important;
        }}

        /* Ẩn mọi nền mặc định của các lớp con */
        [data-testid="stMainBlockContainer"], [data-testid="stMarkdownContainer"], .block-container {{
            background: transparent !important;
        }}

        /* Hộp nội dung */
        .main-box {{
            background-color: rgba(255, 255, 255, 0.82);
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 0 25px rgba(0,0,0,0.4);
            max-width: 900px;
            margin: 8vh auto;
            position: relative;
            z-index: 2;
        }}
        </style>
    """
else:
    background_css = """
        <style>
        .main-box {
            background-color: rgba(255, 255, 255, 0.85);
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 0 20px rgba(0,0,0,0.3);
            max-width: 900px;
            margin: 5rem auto;
        }
        </style>
    """

st.markdown(background_css, unsafe_allow_html=True)

# Nội dung trang chính
st.markdown("<div class='main-box'>", unsafe_allow_html=True)
st.title("✈️ TỔ BẢO DƯỠNG SỐ 1")
st.write("Video intro đã kết thúc — Chào mừng bạn đến với website 🌍")
st.markdown("</div>", unsafe_allow_html=True)
