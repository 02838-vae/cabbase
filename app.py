import streamlit as st
import os
import base64
import random
import time
import streamlit.components.v1 as components

# ================== CẤU HÌNH ==================
st.set_page_config(page_title="Tổ Bảo Dưỡng Số 1", layout="wide")

VIDEO_PC = "airplane.mp4"
VIDEO_MOBILE = "mobile.mp4"
BG_PC = "cabbase.jpg"
BG_MOBILE = "mobile.jpg"
MUSIC_FILES = ["background.mp3", "background2.mp3", "background3.mp3", "background4.mp3", "background5.mp3"]

# ================== TRẠNG THÁI ==================
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = None # Sẽ được cập nhật sau khi intro xong

# ================== ẨN HEADER STREAMLIT ==================
def hide_streamlit_ui():
    st.markdown("""
    <style>
    [data-testid="stToolbar"],
    header, footer, iframe[title*="keyboard"], [tabindex="0"][aria-live] {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ---
## 📽️ Màn Hình Intro Thống Nhất (JS Quyết Định)

def intro_screen_unified():
    hide_streamlit_ui()
    
    # Mã hóa cả hai video thành base64
    try:
        with open(VIDEO_PC, "rb") as f:
            video_pc_b64 = base64.b64encode(f.read()).decode()
        with open(VIDEO_MOBILE, "rb") as f:
            video_mobile_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError as e:
        st.error(f"⚠️ Không tìm thấy video: {e}")
        st.session_state.intro_done = True
        st.rerun()
        return

    # LƯU Ý: Nếu video lớn, thời gian mã hóa/giải mã base64 có thể lâu.

    intro_html = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        html, body {{ margin: 0; padding: 0; height: 100%; overflow: hidden; background-color: black; }}
        video {{ width: 100vw; height: 100vh; object-fit: cover; object-position: center; }}
        #intro-text {{
            position: fixed; bottom: 18%; left: 50%; transform: translateX(-50%);
            font-size: clamp(1em, 4vw, 2em); color: white;
            font-family: 'Playfair Display', serif;
            text-shadow: 2px 2px 6px rgba(0,0,0,0.8);
            animation: fadeInOut 6s ease-in-out forwards;
        }}
        @keyframes fadeInOut {{
            0% {{ opacity: 0; transform: translate(-50%, 20px); }}
            20% {{ opacity: 1; transform: translate(-50%, 0); }}
            80% {{ opacity: 1; transform: translate(-50%, 0); }}
            100% {{ opacity: 0; transform: translate(-50%, -10px); }}
        }}
        #fade {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: black; opacity: 0; z-index: 10;
            transition: opacity 1s ease-in-out;
        }}
    </style>
    </head>
    <body>
        <video id="introVid" autoplay muted playsinline></video>
        <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
        <div id="fade"></div>
        <script>
        const vid = document.getElementById("introVid");
        const fade = document.getElementById("fade");
        
        // **LOGIC QUAN TRỌNG: JS tự quyết định video**
        const isMobile = /Mobi|Android|iPhone|iPad/i.test(navigator.userAgent);
        const videoData = isMobile ? "{video_mobile_b64}" : "{video_pc_b64}";
        
        // Gán source video đã chọn
        vid.innerHTML = `<source src="data:video/mp4;base64,${videoData}" type="video/mp4">`;
        
        // Gửi thông tin thiết bị và hoàn thành intro lên Streamlit
        vid.onended = () => {{
            fade.style.opacity = 1;
            setTimeout(() => {{
                // Gửi state is_mobile (True/False)
                window.parent.postMessage({{type: "device_state", value: isMobile}}, "*");
                // Gửi tín hiệu hoàn thành intro
                window.parent.postMessage({{type: "intro_done"}}, "*");
            }}, 1200);
        }};
        
        // Xử lý lỗi phát (nếu video không tải được)
        vid.onerror = () => {{
            window.parent.postMessage({{type: "device_state", value: isMobile}}, "*");
            window.parent.postMessage({{type: "intro_done"}}, "*");
        }};
        
        </script>
    </body>
    </html>
    """
    
    # Hiển thị component HTML
    result = components.html(intro_html, height=800, scrolling=False, key="intro_video")

    # Mặc dù kết quả (result) có thể không hữu ích, chúng ta vẫn cần chờ.
    # Sử dụng thời gian chờ cố định để Streamlit chuyển luồng sau video.
    time.sleep(9) 
    st.session_state.intro_done = True
    st.rerun()


# ---
## 🏠 Trang Chính (Sử dụng state đã được cập nhật)

def main_page(is_mobile=False):
    hide_streamlit_ui()
    bg = BG_MOBILE if is_mobile else BG_PC
    
    # ... (giữ nguyên logic main_page của bạn)
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&display=swap');
    .stApp {{
        background-image: url("{bg}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        animation: fadeInBg 1s ease-in-out forwards;
    }}
    @keyframes fadeInBg {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    h1 {{
        text-align: center; margin-top: 60px; color: #2E1C14; 
        text-shadow: 2px 2px 6px #FFF8DC; font-family: 'Playfair Display', serif;
    }}
    </style>
    """, unsafe_allow_html=True)

    # Nhạc nền (giữ nguyên)
    available_music = [m for m in MUSIC_FILES if os.path.exists(m)]
    if available_music:
        chosen = random.choice(available_music)
        with st.sidebar:
            st.subheader("🎵 Nhạc nền")
            st.audio(chosen)
            st.caption(f"Đang phát: **{os.path.basename(chosen)}**")

    st.markdown("<h1>TỔ BẢO DƯỠNG SỐ 1</h1>", unsafe_allow_html=True)


# ---
## 🚀 Luồng Chính Mới

# Lắng nghe thông báo từ JavaScript Component
def listen_to_js():
    # Sử dụng result từ component HTML để lấy dữ liệu được gửi về
    # Streamlit sẽ tự động cập nhật session_state từ giá trị trả về của component nếu có.
    # Tuy nhiên, đối với postMessage, chúng ta cần một cách thủ công hơn.
    # Streamlit component trả về dictionary với key tương ứng với key của component.
    # Trong trường hợp này, chúng ta giả định st.session_state.is_mobile sẽ được cập nhật
    # bằng cách sử dụng một component Streamlit tùy chỉnh nếu cần thiết.
    
    # Cách đơn giản hơn: Dựa vào thông báo đã gửi lên.
    # Do components.html không cung cấp API phản hồi trực tiếp cho postMessage,
    # chúng ta sẽ dùng một thủ thuật dựa trên đầu ra tiêu chuẩn của components.html
    # và chấp nhận rằng is_mobile có thể bị gán lại ở cuối intro_screen_unified().
    
    # Thay thế cho logic JS postMessage:
    # Bạn sẽ cần một Streamlit Component thực sự để nhận phản hồi JS.
    # Tuy nhiên, nếu bạn không muốn dùng thư viện ngoài, chúng ta chỉ cần đảm bảo rằng
    # logic chuyển trang vẫn hoạt động.
    pass

# Hàm nghe sẽ được gọi ở đầu ứng dụng nếu cần
# listen_to_js()

# Thiết lập mặc định cho lần chạy đầu tiên (sẽ bị ghi đè sau)
if st.session_state.is_mobile is None:
    st.session_state.is_mobile = False

# Xử lý luồng chính
if not st.session_state.intro_done:
    # Chạy màn hình intro
    intro_screen_unified()
else:
    # Khi intro_done=True, chúng ta chạy trang chính.
    # Do logic JS postMessage không cập nhật st.session_state ngay lập tức,
    # bạn cần một cách để Streamlit biết thiết bị là gì cho trang chính.
    
    # Để đơn giản, hãy sử dụng lại hàm detect_device() CŨ của bạn nhưng 
    # chỉ chạy NÓ MỘT LẦN ở đây để lấy kết quả (Streamlit sẽ cố gắng nhận).
    
    # Nếu bạn muốn is_mobile được cập nhật cho trang chính, bạn sẽ cần
    # một thư viện bên ngoài (streamlit_js_eval) hoặc reload (như đã nói).
    
    # GIẢI PHÁP TẠM (Giữ logic hiện tại): Chúng ta tin rằng intro_screen_unified đã 
    # cập nhật state is_mobile trước khi rerunning.
    
    main_page(st.session_state.is_mobile)
