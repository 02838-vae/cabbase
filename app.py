<style>
html, body {
    margin: 0; padding: 0;
    overflow: hidden;
    background: black;
    width: 100vw;
    height: 100vh;
}
video {
    position: absolute;
    top: 0; left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;  /* đảm bảo full màn hình, không còn viền trắng */
}
audio { display: none; }

#intro-text {
    position: absolute;
    top: 12%;  /* <-- đẩy chữ lên gần trên cùng, thay vì 50% */
    left: 50%;
    transform: translateX(-50%);
    width: 90vw;
    text-align: center;
    color: #f8f4e3;
    font-size: clamp(22px, 6vw, 60px);
    font-weight: bold;
    font-family: 'Playfair Display', serif;
    background: linear-gradient(120deg, #e9dcb5 20%, #fff9e8 40%, #e9dcb5 60%);
    background-size: 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 15px rgba(255,255,230,0.4);
    animation: lightSweep 6s linear infinite, fadeInOut 6s ease-in-out forwards;
    line-height: 1.2;
    word-wrap: break-word;
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

#fade {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: black;
    opacity: 0;
    transition: opacity 1.5s ease-in-out;
}
</style>
