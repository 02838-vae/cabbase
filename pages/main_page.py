import streamlit as st

st.set_page_config(page_title="Main Page", layout="wide")

# --- CSS: đặt hình nền ---
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("cabbase.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    .main-content {{
        background-color: rgba(255, 255, 255, 0.8);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 0 20px rgba(0,0,0,0.3);
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- Nội dung chính ---
st.markdown("<div class='main-content'>", unsafe_allow_html=True)
st.title("🌟 Trang Chính")
st.write("Chào mừng bạn đến với ứng dụng Streamlit!")
st.write("Video intro đã kết thúc và đây là trang nội dung chính của bạn.")

col1, col2 = st.columns(2)
with col1:
    st.header("✈️ Thông tin chuyến bay")
    st.write("Bạn có thể thêm các thành phần, dữ liệu, biểu đồ tại đây.")
with col2:
    st.image("https://placehold.co/400x200", caption="Ảnh minh họa")

st.markdown("</div>", unsafe_allow_html=True)
