# ... (Khoảng dòng 60)
# Lấy Base64 của tất cả các bài hát
AUDIO_BASE64_LIST = []
for file in AUDIO_FILES:
    b64 = get_base64(file)
    if b64:
        AUDIO_BASE64_LIST.append(b64)
    else:
        st.error(f"❌ Không tìm thấy file âm thanh: {file}.")
        st.stop()

# ... (các phần khác giữ nguyên) ...
