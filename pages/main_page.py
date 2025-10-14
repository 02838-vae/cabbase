import streamlit as st

st.set_page_config(page_title="Main Page", layout="wide")

# CSS cho background ảnh
st.markdown(
    """
    <style>
    .stApp {
        background: url("cabbase.jpg") no-repeat center center fixed;
        background-size: cover;
    }
    .main-box {
        background-color: rgba(255, 255, 255, 0.8);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 0 20px rgba(0,0,0,0.3);
        max-width: 900px;
        margin: 5rem auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Nội dung chính
st.markdown("<div class='main-box'>", unsafe_allow_html=True)
st.title("🌟 Trang Chính")
st.write("Chào mừng bạn đến với ứng dụng của chúng tôi!")
st.write("Video intro đã kết thúc và đây là nội dung chính.")
st.markdown("</div>", unsafe_allow_html=True)
