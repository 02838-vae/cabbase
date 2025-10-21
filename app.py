import streamlit as st
import base64
import time
from streamlit.components.v1 import html as components

st.set_page_config(page_title="Tổ bảo dưỡng số 1", layout="wide")

# === Xác định thiết bị ===
ua = st.session_state.get("ua", "")
if not ua:
    ua = st.query_params.get("ua", [""])[0] if "ua" in st.query_params else ""
    st.session_state.ua = ua

is_mobile = any(k in ua.lower() for k in ["iphone", "android", "mobile", "ipad"])

# === Chọn file video, background theo thiết bị ===
video_file = "mobile.mp4" if is_mobile else "airplane.mp4"
bg_image_file = "mobile.jpg" if is_mobile else "cabbase.jpg"
audio_file = "plane_fly.mp3"

# === Chuyển file sang base64 ===
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

video_b64 = get_base64(video_file)
bg_b64 = get_base64(bg_image_file)
audio_b64 = get_base64(audio_file)

# === Hiển thị video intro + âm thanh + chữ ===
components(f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
html, body {{
  margin: 0; padding: 0;
  width: 100%; height: 100%;
  overflow: hidden; background: black;
}}
video {{
  width: 100%; height: 100%;
  object-fit: cover;
}}
#text-overlay {{
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  text-align: center;
  font-family: 'Arial Black', sans-serif;
  font-size: { "24px" if is_mobile else "48px" };
  color: white;
  text-shadow: 0 0 30px rgba(255,255,255,0.8);
  overflow: hidden;
  white-space: nowrap;
  animation: shine 5s linear forwards;
}}

@keyframes shine {{
  0% {{ color: rgba(255,255,255,0.1); }}
  100% {{ color: rgba(255,255,255,1); }}
}}

.fade-out {{
  animation: fadeOut 2s ease-in-out forwards;
}}

@keyframes fadeOut {{
  from {{ opacity: 1; }}
  to {{ opacity: 0; }}
}}
</style>
</head>
<body>
  <video id="introVid" autoplay muted playsinline>
    <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
  </video>

  <audio id="planeAudio" preload="auto">
    <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
  </audio>

  <div id="text-overlay">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>

  <script>
    const vid = document.getElementById("introVid");
    const audio = document.getElementById("planeAudio");
    const text = document.getElementById("text-overlay");

    vid.addEventListener("play", () => {{
      audio.volume = 1.0;
      audio.play().catch(err => console.log("Autoplay blocked", err));
    }});

    // Làm mờ dần video sau 5s, rồi chuyển trang sau 9s
    setTimeout(() => {{
      vid.classList.add("fade-out");
      text.classList.add("fade-out");
    }}, 5000);

    setTimeout(() => {{
      window.parent.postMessage({{ type: "showMainPage" }}, "*");
    }}, 9000);
  </script>
</body>
</html>
""", height=1000, scrolling=False)

# === Cơ chế chuyển cảnh ===
msg = st.experimental_get_query_params().get("msg", [""])[0]
if msg == "main":
    st.markdown(
        f"""
        <style>
        .main-bg {{
          position: fixed;
          top: 0; left: 0;
          width: 100%; height: 100%;
          background: url(data:image/jpg;base64,{bg_b64}) center/cover no-repeat;
          z-index: -1;
        }}
        </style>
        <div class="main-bg"></div>
        """,
        unsafe_allow_html=True,
    )
    st.title("Tổ bảo dưỡng số 1")
else:
    # JavaScript listener để chuyển sang trang chính
    components("""
    <script>
    window.addEventListener("message", (e) => {
        if (e.data && e.data.type === "showMainPage") {
            window.location.search = "?msg=main";
        }
    });
    </script>
    """)
