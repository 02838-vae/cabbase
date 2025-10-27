import streamlit as st
from streamlit_player import st_player

# -----------------
# Cấu hình Trang
# -----------------
st.set_page_config(
    page_title="Streamlit Player Demo",
    layout="wide"  # Đặt layout rộng để tối đa hóa không gian
)

st.title("Streamlit Player Demo (Sửa lỗi TypeError 'width')")
st.markdown("""
Chào mừng! Lỗi `TypeError: st_player() got an unexpected keyword argument 'width'`
thường xảy ra vì hàm `st_player()` không hỗ trợ trực tiếp tham số `width`.
Nó thường tự động điều chỉnh độ rộng theo container.
""")

# -----------------
# Phần 1: Sử dụng cơ bản (Tự động full width)
# -----------------
st.header("1. Cơ bản (Full Container Width)")

# ✅ ĐÚNG: Chỉ truyền URL và các tham số được hỗ trợ (ví dụ: height)
# KHÔNG dùng 'width' ở đây!
st_player(
    url="https://www.youtube.com/watch?v=A2dY2W_bL58", # URL của video mẫu
    height=300, # height là tham số được hỗ trợ
    playing=True,
    key="youtube_player_basic"
)

st.caption("Player này tự động chiếm toàn bộ chiều rộng của cột chính.")

# -----------------
# Phần 2: Kiểm soát độ rộng bằng cách dùng st.columns
# -----------------
st.header("2. Kiểm soát độ rộng bằng st.columns()")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.subheader("Video ở cột giữa (hẹp hơn)")
    
    # ✅ ĐÚNG: Đặt player vào một cột hẹp hơn
    # Player tự động co lại theo độ rộng của col2 (tỷ lệ 2/4)
    st_player(
        url="https://vimeo.com/248308436", # URL video Vimeo mẫu
        height=200,
        loop=True,
        key="vimeo_player_column"
    )

with col1:
    st.info("Cột này trống (tỷ lệ 1/4)")
    
with col3:
    st.warning("Cột này trống (tỷ lệ 1/4)")

st.caption("Để kiểm soát độ rộng, hãy đặt player vào một container hoặc cột có kích thước cụ thể.")

# -----------------
# Phần 3: Kiểm tra trạng thái
# -----------------
st.header("3. Trạng thái Player")

# Bạn có thể dùng tham số 'key' để truy xuất trạng thái của player
st.subheader("Trạng thái của Player cơ bản (dùng key)")
player_status = st_player(
    url="https://soundcloud.com/futureclassic/ry-x-bad-love-b-w-howling-exclusive-mix", # SoundCloud mẫu
    key="soundcloud_player_status"
)

if player_status:
    st.json(player_status)
else:
    st.text("Đang chờ player tải...")
