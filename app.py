import streamlit as st
import base64
import os

# --- CẤU HÌNH BAN ĐẦU ---
st.set_page_config(
    page_title="Tổ Bảo Dưỡng Số 1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Khởi tạo session state
if 'video_ended' not in st.session_state:
    st.session_state.video_ended = False

# --- CÁC HÀM TIỆN ÍCH ---

def get_base64_encoded_file(file_path):
    """Đọc file và trả về Base64 encoded string."""
    # Sửa đường dẫn nếu cần thiết để phù hợp với môi trường triển khai
    path_to_check = os.path.join(os.path.dirname(__file__), file_path)
    if not os.path.exists(path_to_check) or os.path.getsize(path_to_check) == 0:
        # Nếu không tìm thấy file, trả về None
        return None
    try:
        with open(path_to_check, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    except Exception as e:
        # st.error(f"Lỗi khi đọc file {file_path}: {str(e)}") # Bỏ comment khi debug
        return None


# Mã hóa các file media chính (bắt buộc)
try:
    # Đảm bảo các file này nằm cùng thư mục hoặc chỉnh lại đường dẫn
    video_path = "video_chao.mp4"
    bg_music_path = "bg_music.mp3"
    
    video_base64 = get_base64_encoded_file(video_path)
    music_base64 = get_base64_encoded_file(bg_music_path)
    
    if video_base64 is None:
        st.error(f"Không tìm thấy hoặc file '{video_path}' trống. Vui lòng kiểm tra lại đường dẫn.")
        video_html = ""
    else:
        video_html = f"""
        <video id="intro-video" width="100%" height="100%" autoplay muted playsinline>
            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
            Trình duyệt của bạn không hỗ trợ thẻ video.
        </video>
        """

    # Lấy danh sách các file nhạc nền phụ (nếu có)
    music_folder = os.path.join(os.path.dirname(__file__), "music")
    music_files = []
    if os.path.exists(music_folder) and os.path.isdir(music_folder):
        for filename in os.listdir(music_folder):
            if filename.endswith(('.mp3', '.ogg', '.wav')):
                full_path = os.path.join("music", filename)
                base64_data = get_base64_encoded_file(full_path)
                if base64_data:
                    music_files.append({
                        "name": filename,
                        "data": base64_data,
                        "mime": "audio/mp3" if filename.endswith('.mp3') else "audio/mpeg"
                    })

except Exception as e:
    st.error(f"Lỗi chung khi tải media: {str(e)}")
    video_html = ""
    music_files = []


# --- JAVASCRIPT/CSS/HTML CHÍNH ---

# Chứa tất cả CSS và JavaScript trong một block duy nhất
full_script = f"""
<style>
/* === CSS TOÀN CỤC === */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
:root {{
    --color-primary: #1e3a8a; /* Blue-800 */
    --color-secondary: #fcd34d; /* Amber-300 */
    --color-text-light: #f9fafb; /* Gray-50 */
    --color-text-dark: #1f2937; /* Gray-800 */
    --color-bg-dark: #111827; /* Gray-900 */
    --color-bg-card: #1f2937; /* Gray-800 */
    --color-border-card: #374151; /* Gray-700 */
}}

body {{
    font-family: 'Inter', sans-serif;
    color: var(--color-text-light);
    background-color: var(--color-bg-dark);
    margin: 0;
    padding: 0;
    overflow: hidden; /* Quan trọng để tránh thanh cuộn */
}}

/* Ẩn các thành phần mặc định của Streamlit */
#root > div:nth-child(1) > div > div > div:nth-child(1) {{
    display: none !important;
}}
header {{
    visibility: hidden;
}}
.st-emotion-cache-z5fcl4, .st-emotion-cache-1cypcdb {{ /* Ẩn footer và main block padding */
    padding: 0 !important;
    margin: 0 !important;
}}
.st-emotion-cache-1v04u9 {{
    padding: 0px 0px;
}}

/* --- VIDEO CONTAINER --- */
#video-container {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 100;
    opacity: 1;
    transition: opacity 2s ease-out;
}}

.video-finished #video-container {{
    opacity: 0;
    pointer-events: none;
}}

#intro-video {{
    object-fit: cover;
    width: 100%;
    height: 100%;
}}

/* --- MAIN TITLE (SAU KHI VIDEO KẾT THÚC) --- */
#main-title-container {{
    position: fixed;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    z-index: 1000;
    opacity: 0;
    transition: opacity 2s ease-out 3s;
    text-align: center;
    pointer-events: none;
    line-height: 1;
}}

.video-finished #main-title-container {{
    opacity: 1;
}}

#main-title-container h1 {{
    font-size: 6rem; /* Kích thước lớn trên PC */
    font-weight: 700;
    color: var(--color-secondary);
    text-shadow: 0 0 20px rgba(252, 211, 77, 0.6);
    margin: 0;
    padding: 0;
    animation: pulseGlow 5s infinite alternate;
}}

@keyframes pulseGlow {{
    0% {{
        text-shadow: 0 0 10px var(--color-secondary), 0 0 20px var(--color-secondary);
    }}
    100% {{
        text-shadow: 0 0 30px var(--color-secondary), 0 0 40px rgba(252, 211, 77, 0.8);
    }}
}}

/* --- MUSIC PLAYER --- */
#music-player-container {{
    position: fixed;
    right: 20px;
    bottom: 20px;
    background-color: var(--color-bg-card);
    border: 1px solid var(--color-border-card);
    padding: 10px 15px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 15px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
    z-index: 10000;
    opacity: 0;
    transition: opacity 2s ease-out 3s;
}}

.video-finished #music-player-container {{
    opacity: 1;
}}

.controls {{
    display: flex;
    gap: 5px;
}}

.control-btn {{
    background: var(--color-primary);
    color: var(--color-text-light);
    border: none;
    border-radius: 8px;
    padding: 8px 12px;
    cursor: pointer;
    font-size: 1.1rem;
    transition: background 0.2s, transform 0.1s;
}}

.control-btn:hover {{
    background: #1d4ed8; /* Blue-700 */
}}

.control-btn:active {{
    transform: scale(0.95);
}}

.progress-container {{
    flex-grow: 1;
    height: 6px;
    width: 100px;
    background: #374151; /* Gray-700 */
    border-radius: 3px;
    cursor: pointer;
    overflow: hidden;
}}

.progress-bar {{
    height: 100%;
    width: 0%;
    background: var(--color-secondary);
    transition: width 0.1s linear;
}}

.time-info {{
    font-size: 0.8rem;
    color: #9ca3af; /* Gray-400 */
}}

.time-info span:last-child {{
    margin-left: 5px;
}}


/* === CSS MỚI CHO NAVIGATION BUTTON (UIverse Dark Mode) === */

.nav-container {{
    position: fixed;
    /* Định vị container ở giữa chiều cao màn hình */
    top: 50%; 
    transform: translateY(-50%);
    
    /* THAY ĐỔI LỚN: Dùng Flexbox để xếp các button cạnh nhau trên PC */
    display: flex;
    align-items: center;
    gap: 40px; /* Khoảng cách giữa 2 button */
    
    /* Định vị container: Button đầu tiên (Part Number) ở 15% (như cũ) */
    left: 15%; 
    
    padding: 40px;
    opacity: 0;
    transition: opacity 2s ease-out 3s;
    z-index: 10000;
}}

.video-finished .nav-container {{
    opacity: 1;
}}

.button {{
    position: relative;
    background-color: var(--color-bg-card);
    border: 1px solid var(--color-border-card);
    border-radius: 12px;
    padding: 10px 25px 10px 20px;
    color: var(--color-text-light);
    font-size: 1.1rem;
    font-weight: 700;
    text-decoration: none;
    overflow: hidden;
    cursor: pointer;
    display: flex;
    align-items: center;
    transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
}}

.button:hover {{
    transform: scale(1.05);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5), 0 0 30px var(--color-secondary);
}}

.button:active {{
    transform: scale(0.98);
}}

.sparkle {{
    width: 20px;
    height: 20px;
    margin-right: 10px;
    color: var(--color-secondary);
}}

/* Hiệu ứng viền chuyển động */
.dots_border {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border-radius: 12px;
    overflow: hidden;
    pointer-events: none;
}}

.dots_border::before {{
    content: "";
    position: absolute;
    width: 300%;
    height: 300%;
    background: conic-gradient(
        transparent,
        transparent,
        transparent,
        #fcd34d, /* Amber-300 */
        #eab308, /* Amber-600 */
        #fcd34d,
        transparent,
        transparent,
        transparent
    );
    top: -100%;
    left: -100%;
    z-index: -1;
    animation: rotate 4s linear infinite;
}}

.button:hover .dots_border::before {{
    animation: rotate 1s linear infinite; /* Tăng tốc khi hover */
}}

@keyframes rotate {{
    0% {{
        transform: rotate(0deg);
    }}
    100% {{
        transform: rotate(360deg);
    }}
}}

/* --- MEDIA QUERIES (RESPONSIVE) --- */
@media (max-width: 1024px) {{
    #main-title-container h1 {{
        font-size: 4rem;
    }}
}}

@media (max-width: 768px) {{
    #main-title-container h1 {{
        font-size: 3rem;
    }}
    
    .nav-container {{
        left: 50%;
        transform: translate(-50%, -50%);
        width: 100%;
        padding: 20px;
        /* THAY ĐỔI LỚN: Trên mobile, các button xếp chồng lên nhau theo cột (column) */
        flex-direction: column; 
        gap: 15px;
    }}

    .button {{
        width: 90%;
        justify-content: center;
        padding: 15px 10px;
    }}
    
    #music-player-container {{
        right: 50%;
        transform: translateX(50%);
        bottom: 10px;
        gap: 10px;
    }}
    .progress-container {{
        width: 70px;
    }}
    .control-btn {{
        padding: 6px 10px;
        font-size: 1rem;
    }}
}}


</style>

<script>
    // --- JAVASCRIPT LOGIC ---
    
    document.addEventListener('DOMContentLoaded', function() {{
        const video = document.getElementById('intro-video');
        const mainContainer = document.querySelector('.st-emotion-cache-1v04u9');
        const mainTitleContainer = document.getElementById('main-title-container');
        const musicPlayerContainer = document.getElementById('music-player-container');
        const navContainer = document.querySelector('.nav-container');

        // Khởi tạo Streamlit state (quan trọng để giữ state sau khi Streamlit refresh)
        function setStreamlitState(key, value) {{
            // Sử dụng Streamlit custom component bridge (nếu có) hoặc in ra console để debug
            console.log(`Setting state {{key}}: {{value}}`);
        }}

        // --- 1. VIDEO LOGIC ---
        if (video) {{
            video.onended = function() {{
                mainContainer.classList.add('video-finished');
                setStreamlitState('video_ended', true);
            }};

            // Nếu video đã kết thúc (dựa trên session state từ Python)
            if ({st.session_state.video_ended}) {{
                mainContainer.classList.add('video-finished');
                if (video.parentElement) {{
                    video.parentElement.style.opacity = 0;
                    video.parentElement.style.pointerEvents = 'none';
                }}
            }} else {{
                video.onloadeddata = function() {{
                    // Bỏ muted và cho phép phát trên mobile sau khi người dùng tương tác
                    // Đây chỉ là một mẹo nhỏ vì autoplay/muted là yêu cầu cứng của trình duyệt
                }};
            }}
        }} else {{
             // Nếu không có video, hiển thị nội dung chính ngay lập tức
             mainContainer.classList.add('video-finished');
             setStreamlitState('video_ended', true);
        }}


        // --- 2. MUSIC PLAYER LOGIC ---
        const playPauseBtn = document.getElementById('play-pause-btn');
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        const progressBar = document.getElementById('progress-bar');
        const progressContainer = document.getElementById('progress-container');
        const currentTimeEl = document.getElementById('current-time');
        const durationEl = document.getElementById('duration');
        
        let currentTrackIndex = 0;
        let audio = new Audio();
        
        const musicFiles = {music_files if music_files else '[]'}; // Lấy danh sách nhạc từ Python
        
        if (musicFiles.length > 0) {{
            
            // Hàm định dạng thời gian
            function formatTime(seconds) {{
                const min = Math.floor(seconds / 60);
                const sec = Math.floor(seconds % 60);
                return `${{min}}:${{sec < 10 ? '0' : ''}}${{sec}}`;
            }}

            // Hàm tải track
            function loadTrack(index) {{
                if (audio) audio.pause();
                const track = musicFiles[index];
                
                // Giải mã Base64 và gán cho audio src
                audio = new Audio(`data:${{track.mime}};base64,${{track.data}}`);
                
                audio.loop = false; // Nghe hết bài rồi chuyển bài
                
                // Cập nhật thông tin thời gian khi metadata được tải
                audio.onloadedmetadata = function() {{
                    durationEl.textContent = formatTime(audio.duration);
                    currentTimeEl.textContent = formatTime(0);
                    progressBar.style.width = '0%';
                }};

                // Cập nhật thanh tiến trình
                audio.ontimeupdate = function() {{
                    const progress = (audio.currentTime / audio.duration) * 100;
                    progressBar.style.width = `${{progress}}%`;
                    currentTimeEl.textContent = formatTime(audio.currentTime);
                }};

                // Tự động chuyển bài khi kết thúc
                audio.onended = function() {{
                    nextTrack();
                }};

                // Đảm bảo nút hiển thị đúng trạng thái
                audio.onplay = () => playPauseBtn.textContent = '⏸';
                audio.onpause = () => playPauseBtn.textContent = '▶';
                
                // Tự động phát khi tải xong (chỉ lần đầu)
                if (index === 0) {{
                     // Tự động phát nhạc nền nhẹ nhàng (nếu trình duyệt cho phép)
                     audio.volume = 0.5;
                     audio.play().catch(e => console.log("Autoplay failed:", e));
                }}
            }}
            
            // Hàm phát/dừng
            function playPauseTrack() {{
                if (audio.paused) {{
                    audio.play();
                }} else {{
                    audio.pause();
                }}
            }}

            // Hàm chuyển bài kế tiếp
            function nextTrack() {{
                currentTrackIndex = (currentTrackIndex + 1) % musicFiles.length;
                loadTrack(currentTrackIndex);
                audio.play();
            }}

            // Hàm chuyển bài trước đó
            function prevTrack() {{
                currentTrackIndex = (currentTrackIndex - 1 + musicFiles.length) % musicFiles.length;
                loadTrack(currentTrackIndex);
                audio.play();
            }}
            
            // Xử lý click trên thanh tiến trình
            progressContainer.onclick = function(e) {{
                const clickX = e.offsetX;
                const width = progressContainer.clientWidth;
                const duration = audio.duration;
                audio.currentTime = (clickX / width) * duration;
            }};

            // Gắn sự kiện vào các nút
            playPauseBtn.onclick = playPauseTrack;
            nextBtn.onclick = nextTrack;
            prevBtn.onclick = prevTrack;

            // Khởi động
            loadTrack(currentTrackIndex);
            
        }} else if (musicPlayerContainer) {{
            // Ẩn music player nếu không có file nhạc nào
            musicPlayerContainer.style.display = 'none';
        }}
        
    }});
</script>
"""

# Chạy Python và HTML/CSS/JS

# Chạy JS và CSS
st.markdown(full_script, unsafe_allow_html=True)

# --- VIDEO CHÀO MỪNG ---
st.markdown(f"""
<div id="video-container">
    {video_html}
</div>
""", unsafe_allow_html=True)


# --- TIÊU ĐỀ CHÍNH (XUẤT HIỆN SAU KHI VIDEO KẾT THÚC) ---
main_title_text = "TỔ BẢO DƯỠNG SỐ 1"

# Nhúng tiêu đề
st.markdown(f"""
<div id="main-title-container">
    <h1>{main_title_text}</h1>
</div>
""", unsafe_allow_html=True)

# --- MUSIC PLAYER ---
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

# --- NAVIGATION BUTTON MỚI (UIverse Style) ---
# Tên trang phụ là partnumber.py nên link href là /partnumber
st.markdown("""
<div class="nav-container">
    <!-- BUTTON 1: TRA CỨU PART NUMBER -->
    <a href="/partnumber" target="_self" class="button">
        <div class="dots_border"></div>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="sparkle" > 
            <path class="path" stroke-linejoin="round" stroke-linecap="round" stroke="currentColor" fill="currentColor" d="M10 17a7 7 0 100-14 7 7 0 000 14zM21 21l-4-4" ></path> 
        </svg> 
        <span class="text_button">TRA CỨU PART NUMBER</span> 
    </a>
    
    <!-- BUTTON 2: NGÂN HÀNG TRẮC NGHIỆM (MỚI) -->
    <a href="/quiz" target="_self" class="button">
        <div class="dots_border"></div>
        <!-- Icon Sách/Kiến Thức (dùng icon chung là sparkle/search để giữ nguyên hiệu ứng) -->
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="sparkle">
             <!-- Icon Book - Lucide (biểu tượng cho trắc nghiệm/kiến thức) -->
             <path class="path" stroke-linejoin="round" stroke-linecap="round" stroke="currentColor" fill="currentColor" d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"></path>
        </svg>
        <span class="text_button">NGÂN HÀNG TRẮC NGHIỆM</span>
    </a>
</div>
""", unsafe_allow_html=True)

# --- NỘI DUNG CHÍNH (Có thể đặt thêm nội dung dưới đây nếu cần) ---
# st.markdown("Thêm các thành phần khác tại đây.")
