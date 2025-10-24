import streamlit as st
import base64

def intro_screen():
    st.markdown(
        """
        <style>
        /* ==== RESET TẤT CẢ ==== */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
            margin: 0 !important;
            padding: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            overflow: hidden !important;
            background: black !important;
        }

        /* XÓA MỌI VIỀN TRẮNG CỦA STREAMLIT */
        [data-testid="stToolbar"],
        [data-testid="stHeader"],
        [data-testid="stSidebar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        footer {
            display: none !important;
        }

        /* ==== VIDEO FULL MÀN HÌNH ==== */
        video {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            object-fit: cover;
            border: none;
            outline: none;
            margin: 0;
            padding: 0;
            display: block;
            background: black;
        }

        /* ==== ẢNH TĨNH (FRAME CUỐI) ==== */
        #static-frame {
            position: fixed;
            top: 0; left: 0;
            width: 100vw; height: 100vh;
            background-image: url("data:image/jpeg;base64,{shutter_b64}");
            background-size: cover;
            background-position: center;
            opacity: 0;
            z-index: 20;
            transition: opacity 0.1s linear;
        }

        /* ==== TIÊU ĐỀ TRÊN VIDEO ==== */
        #intro-text {
            position: absolute;
            top: 8%;
            left: 50%;
            transform: translateX(-50%);
            white-space: nowrap; /* Giữ tiêu đề 1 dòng */
            color: #f8f4e3;
            font-size: clamp(24px, 6vw, 60px);
            font-weight: bold;
            font-family: 'Playfair Display', serif;
            text-align: center;
            background: linear-gradient(120deg, #e9dcb5 20%, #fff9e8 40%, #e9dcb5 60%);
            background-size: 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 15px rgba(255,255,230,0.4);
            animation: lightSweep 6s linear infinite, fadeInOut 6s ease-in-out forwards;
            z-index: 10;
        }

        @keyframes lightSweep {
            0% { background-position: 200% 0%; }
            100% { background-position: -200% 0%; }
        }

        @keyframes fadeInOut {
            0% { opacity: 0; }
            20% { opacity: 1; }
            80% { opacity: 1; }
            100% { opacity: 0; }
        }

        /* ==== HIỆU ỨNG TAN VỠ ==== */
        #shatter-overlay {
            position: fixed;
            top: 0; left: 0;
            width: 100vw; height: 100vh;
            display: grid;
            grid-template-columns: repeat({GRID_SIZE}, 1fr);
            grid-template-rows: repeat({GRID_SIZE}, 1fr);
            opacity: 0;
            pointer-events: none;
            z-index: 30;
        }

        .shard {
            position: relative;
            background-image: url("data:image/jpeg;base64,{shutter_b64}");
            background-size: 100vw 100vh;
            transition: transform {SHATTER_DURATION}s cubic-bezier(0.68, -0.55, 0.27, 1.55), opacity 1.5s ease-in-out;
            opacity: 1;
        }

        .reconstructing .shard {
            transform: translate(0, 0) rotate(0deg) scale(1) !important;
            transition: transform {RECONSTRUCT_DURATION}s cubic-bezier(0.19, 1, 0.22, 1), opacity {RECONSTRUCT_DURATION}s ease-in-out;
            background-image: url("data:image/jpeg;base64,{bg_b64}") !important;
            opacity: 1 !important;
        }

        /* ==== MÀN HÌNH ĐEN ==== */
        #black-fade {
            position: fixed;
            top: 0; left: 0;
            width: 100vw; height: 100vh;
            background: black;
            opacity: 1;
            z-index: 40;
            transition: opacity 1s ease-in-out;
            pointer-events: none;
        }
        </style>

        <div id="intro-wrapper">
            <video autoplay muted playsinline>
                <source src="airplane.mp4" type="video/mp4">
            </video>
            <div id="intro-text">KHÁM PHÁ THẾ GIỚI CÙNG CHÚNG TÔI</div>
            <div id="static-frame"></div>
            <div id="shatter-overlay"></div>
            <div id="black-fade"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # === JS điều khiển hiệu ứng (bạn có thể thêm nếu cần) ===
    st.markdown(
        """
        <script>
        document.addEventListener("DOMContentLoaded", function() {
            const video = document.querySelector("video");
            const blackFade = document.getElementById("black-fade");
            setTimeout(() => {
                blackFade.style.opacity = 0;
            }, 500); // mờ dần lớp đen
        });
        </script>
        """,
        unsafe_allow_html=True,
    )

# Gọi hàm intro
intro_screen()
