import streamlit as st
import time

# --- Cấu hình trang ---
st.set_page_config(page_title="Airplane App", layout="centered")

# --- Dùng session_state để lưu trạng thái intro ---
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

# --- Nếu intro chưa chạy ---
if not st.session_state.intro_done:
    st.markdown("<h1 style='text-align:center;'>✈️ Welcome Aboard!</h1>", unsafe_allow_html=True)
    st.video("airplane.mp4")

    # Giả sử video dài 10 giây, bạn có thể chỉnh tùy theo độ dài thực tế
    time.sleep(10)

    # Đánh dấu là đã xem intro
    st.session_state.intro_done = True
    st.rerun()

else:
    # --- Khi đã xem intro, chuyển sang trang chính ---
    st.switch_page("pages/main_page.py")
