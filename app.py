import os
import time
from flask import Flask, render_template_string, redirect

# =========================
# GitHub Releases 다운로드 설정
# =========================
GITHUB_OWNER = "tldud96"
GITHUB_REPO = "overview-website"
PROGRAM_FILENAME = "OverView.zip"   # Releases에 업로드한 파일명과 동일해야 함
DOWNLOAD_URL = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest/download/{PROGRAM_FILENAME}"

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey_final_version"

# =========================
# 웹사이트 HTML
# =========================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OverView - 원격 제어 솔루션</title>

    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&family=Noto+Sans+KR:wght@400;500;700&display=swap');
        :root {
            --bg-color: #0a0e27;
            --frame-bg: #1a1f3a;
            --primary-neon: #64b5f6;
            --secondary-neon: #4dffaf;
            --text-color: #e0e0e0;
            --text-dark: #a0a0a0;
            --border-color: #2a3f7f;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Poppins','Noto Sans KR',sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.8;
        }
        .container { max-width: 1100px; margin: 0 auto; padding: 0 30px; }
        header {
            position: fixed; top: 0; width: 100%;
            background: rgba(10,14,39,0.85);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border-color);
            z-index: 100;
        }
        .navbar {
            display: flex; justify-content: space-between; align-items: center;
            height: 70px;
        }
        .logo {
            font-size: 28px; font-weight: 700;
            color: var(--primary-neon);
            text-decoration: none;
        }
        .nav-menu { list-style: none; display: flex; }
        .nav-menu li { margin-left: 30px; }
        .nav-menu a {
            color: var(--text-color);
            text-decoration: none;
            font-weight: 500;
        }
        .section {
            padding: 120px 0;
            border-bottom: 1px solid var(--border-color);
        }
        .section-title {
            font-size: 42px;
            font-weight: 700;
            text-align: center;
            margin-bottom: 60px;
        }
        #hero {
            height: 100vh;
            display: flex;
            align-items: center;
            text-align: center;
        }
        .hero-content h1 {
            font-size: 56px;
            color: #fff;
        }
        .highlight {
            display: block;
            font-size: 72px;
            color: #cce7ff;
            margin: 15px 0 30px;
        }
        .btn {
            display: inline-block;
            padding: 15px 40px;
            background: var(--primary-neon);
            color: var(--bg-color);
            font-weight: 700;
            border-radius: 50px;
            text-decoration: none;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit,minmax(300px,1fr));
            gap: 30px;
        }
        .card {
            background: var(--frame-bg);
            padding: 30px;
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }
        .card h3 {
            margin-bottom: 15px;
            color: var(--secondary-neon);
        }
        footer {
            text-align: center;
            padding: 40px 0;
            color: var(--text-dark);
        }
    </style>
</head>

<body>
<header>
    <nav class="navbar container">
        <a href="/" class="logo">OverView</a>
        <ul class="nav-menu">
            <li><a href="#hero">소개</a></li>
            <li><a href="#download">다운로드</a></li>
            <li><a href="#features">기능</a></li>
            <li><a href="#details">상세 설명</a></li>
        </ul>
    </nav>
</header>

<main>
<section id="hero">
    <div class="container hero-content">
        <h1>가장 직관적인 원격 제어 솔루션
            <span class="highlight">OverView</span>
        </h1>
        <p>여러 대의 PC를 하나의 화면에서 안정적으로 관리하세요.</p>
    </div>
</section>

<section id="download" class="section">
    <div class="container" style="text-align:center;">
        <h2 class="section-title">다운로드</h2>
        <a href="/download" class="btn">최신 버전 다운로드</a>
    </div>
</section>

<section id="features" class="section">
    <div class="container">
        <h2 class="section-title">주요 기능 요약</h2>
        <div class="grid">
            <div class="card"><h3>실시간 화면 공유</h3><p>다중 PC 화면을 동시에 모니터링</p></div>
            <div class="card"><h3>원격 키보드 / 마우스</h3><p>지연 없는 입력 전달</p></div>
            <div class="card"><h3>파일 전송</h3><p>단일·다중 PC 파일 배포</p></div>
        </div>
    </div>
</section>

<!-- 🔥 여기서부터 추가된 상세 설명 섹션 -->
<section id="details" class="section">
    <div class="container">
        <h2 class="section-title">OverView 상세 기능 안내</h2>

        <div class="grid">
            <div class="card">
                <h3>🖥️ 다중 PC 실시간 모니터링</h3>
                <p>
                    여러 클라이언트 PC 화면을 하나의 관리 화면에서 동시에 확인할 수 있습니다.
                    각 PC는 실시간으로 갱신되며 대규모 환경에서도 효율적인 관리가 가능합니다.
                </p>
            </div>

            <div class="card">
                <h3>🖱️ 즉시 원격 제어</h3>
                <p>
                    원하는 PC를 선택해 즉시 원격 제어할 수 있으며,
                    실제 로컬 환경과 유사한 조작감을 제공합니다.
                </p>
            </div>

            <div class="card">
                <h3>🔐 제어권 충돌 방지</h3>
                <p>
                    동시에 여러 관리자가 접속하더라도,
                    단일 사용자만 제어권을 가질 수 있도록 설계되어
                    입력 충돌을 방지합니다.
                </p>
            </div>

            <div class="card">
                <h3>⌨️ 고급 키보드 입력 처리</h3>
                <p>
                    한/영 전환, 한자키, 반복 입력 등
                    실제 키보드 입력과 최대한 동일한 동작을 지원합니다.
                </p>
            </div>

            <div class="card">
                <h3>📋 양방향 클립보드</h3>
                <p>
                    제어 PC와 클라이언트 PC 간 텍스트 복사/붙여넣기를
                    간편하게 수행할 수 있습니다.
                </p>
            </div>

            <div class="card">
                <h3>📁 파일 전송 및 배포</h3>
                <p>
                    단일 또는 다수의 PC에 파일을 전송하여
                    업데이트 및 설정 배포를 효율적으로 처리할 수 있습니다.
                </p>
            </div>
        </div>
    </div>
</section>
</main>

<footer>
    <div class="container">
        <p>© 2026 OverView. All Rights Reserved.</p>
    </div>
</footer>
</body>
</html>
"""

# =========================
# Flask 라우트
# =========================
@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/download")
def download():
    # 캐시 방지용 쿼리
    return redirect(DOWNLOAD_URL + f"?v={int(time.time())}", code=302)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
