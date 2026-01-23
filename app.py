import os
from flask import Flask, render_template_string, redirect

# --- 설정 ---
UPLOAD_FOLDER = os.getcwd()
PROGRAM_FILENAME = 'OverView.zip'

# GitHub Releases에서 최신 파일을 받도록 리다이렉트합니다.
GITHUB_OWNER = 'tldud96'
GITHUB_REPO = 'overview-website'
RELEASE_ASSET_NAME = PROGRAM_FILENAME  # 릴리스에 업로드한 파일명과 동일해야 합니다.
DOWNLOAD_URL = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest/download/{RELEASE_ASSET_NAME}"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'supersecretkey_final_version'

# --- 웹사이트 전체 HTML (물리적 줄바꿈   적용 버전) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>OverView - Remote Control Program</title>

    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Jost:wght@400;500;600;700&family=Space+Grotesk:wght@500;600&display=swap" rel="stylesheet">

    <style>
        /* =========================
           Base / Reset
        ========================== */
        :root {
            --bg: #0b0e14;
            --bg2: #0f1420;
            --card: rgba(255, 255, 255, 0.06);
            --card2: rgba(255, 255, 255, 0.10);
            --text: #e9eefc;
            --muted: rgba(233, 238, 252, 0.72);
            --muted2: rgba(233, 238, 252, 0.55);
            --brand: #6c7cff;
            --brand2: #9b5cff;
            --ok: #38d996;
            --warn: #ffcc66;
            --border: rgba(255, 255, 255, 0.10);
            --shadow: 0 20px 60px rgba(0,0,0,0.35);
        }

        * { box-sizing: border-box; }
        html, body { height: 100%; }
        body {
            margin: 0;
            font-family: 'Jost', system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji";
            color: var(--text);
            background: radial-gradient(1200px 700px at 10% 0%, rgba(108,124,255,0.35), transparent 60%),
                        radial-gradient(900px 600px at 100% 10%, rgba(155,92,255,0.30), transparent 55%),
                        linear-gradient(180deg, var(--bg), var(--bg2));
            overflow-x: hidden;
        }

        a { color: inherit; text-decoration: none; }
        .container {
            width: min(1160px, 92vw);
            margin: 0 auto;
        }

        /* =========================
           Top Nav
        ========================== */
        .nav {
            position: sticky;
            top: 0;
            z-index: 50;
            backdrop-filter: blur(12px);
            background: rgba(11, 14, 20, 0.55);
            border-bottom: 1px solid var(--border);
        }
        .nav-inner {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 14px 0;
        }
        .logo {
            display: flex;
            gap: 12px;
            align-items: center;
            font-family: 'Space Grotesk', sans-serif;
            letter-spacing: 0.2px;
        }
        .logo-badge {
            width: 34px;
            height: 34px;
            border-radius: 10px;
            background: linear-gradient(135deg, rgba(108,124,255,1), rgba(155,92,255,1));
            box-shadow: 0 10px 22px rgba(108,124,255,0.25);
        }
        .nav-links {
            display: flex;
            gap: 18px;
            align-items: center;
            color: var(--muted);
            font-weight: 500;
        }
        .nav-links a {
            padding: 8px 10px;
            border-radius: 10px;
            transition: 0.2s ease;
        }
        .nav-links a:hover {
            background: rgba(255,255,255,0.06);
            color: var(--text);
        }

        /* =========================
           Hero
        ========================== */
        .hero {
            padding: 70px 0 34px;
        }
        .hero-grid {
            display: grid;
            grid-template-columns: 1.15fr 0.85fr;
            gap: 34px;
            align-items: center;
        }
        .headline {
            font-family: 'Space Grotesk', sans-serif;
            font-size: clamp(36px, 4.2vw, 56px);
            line-height: 1.02;
            margin: 0 0 16px;
        }
        .subhead {
            font-size: 18px;
            color: var(--muted);
            margin: 0 0 28px;
            line-height: 1.6;
        }
        .cta-row {
            display: flex;
            gap: 14px;
            align-items: center;
            flex-wrap: wrap;
        }
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            padding: 13px 18px;
            border-radius: 14px;
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.06);
            color: var(--text);
            font-weight: 600;
            transition: 0.2s ease;
            cursor: pointer;
            user-select: none;
        }
        .btn:hover {
            transform: translateY(-1px);
            background: rgba(255,255,255,0.09);
        }
        .btn.primary {
            border: none;
            background: linear-gradient(135deg, rgba(108,124,255,1), rgba(155,92,255,1));
            box-shadow: 0 18px 40px rgba(108,124,255,0.26);
        }
        .btn.primary:hover {
            box-shadow: 0 22px 55px rgba(108,124,255,0.35);
        }
        .pill {
            display: inline-flex;
            gap: 10px;
            align-items: center;
            padding: 8px 12px;
            border-radius: 999px;
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.04);
            color: var(--muted);
            font-weight: 500;
            margin-bottom: 14px;
            width: fit-content;
        }
        .pill-dot {
            width: 10px;
            height: 10px;
            border-radius: 99px;
            background: var(--ok);
            box-shadow: 0 0 0 4px rgba(56,217,150,0.15);
        }

        /* Hero right card */
        .hero-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.07), rgba(255,255,255,0.03));
            border: 1px solid var(--border);
            border-radius: 20px;
            box-shadow: var(--shadow);
            overflow: hidden;
        }
        .hero-card-top {
            padding: 18px 18px 0;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }
        .hero-card-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 16px;
            margin: 0;
        }
        .hero-card-tag {
            font-size: 13px;
            color: var(--muted2);
            margin-top: 6px;
        }
        .mini-badges {
            display: flex;
            gap: 8px;
        }
        .mini {
            width: 12px;
            height: 12px;
            border-radius: 99px;
            background: rgba(255,255,255,0.14);
        }
        .hero-card-body {
            padding: 18px;
            display: grid;
            gap: 12px;
        }
        .stat {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 14px;
            border-radius: 16px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
        }
        .stat strong { font-size: 15px; }
        .stat span { font-size: 14px; color: var(--muted); }

        /* =========================
           Sections
        ========================== */
        .section {
            padding: 42px 0;
        }
        .section h2 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 28px;
            margin: 0 0 10px;
        }
        .section p.lead {
            margin: 0 0 22px;
            color: var(--muted);
            line-height: 1.6;
        }

        /* Feature grid */
        .grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
        }
        .card {
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.05);
            border-radius: 18px;
            padding: 18px;
            transition: 0.2s ease;
        }
        .card:hover {
            transform: translateY(-2px);
            background: rgba(255,255,255,0.07);
        }
        .icon {
            width: 44px;
            height: 44px;
            border-radius: 14px;
            display: grid;
            place-items: center;
            background: linear-gradient(135deg, rgba(108,124,255,0.20), rgba(155,92,255,0.20));
            border: 1px solid rgba(108,124,255,0.25);
            margin-bottom: 12px;
        }
        .card h3 {
            margin: 0 0 8px;
            font-size: 18px;
        }
        .card p {
            margin: 0;
            color: var(--muted);
            line-height: 1.55;
        }

        /* FAQ */
        .faq {
            display: grid;
            gap: 10px;
        }
        details {
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.04);
            border-radius: 16px;
            padding: 14px 16px;
        }
        summary {
            cursor: pointer;
            font-weight: 600;
            list-style: none;
        }
        summary::-webkit-details-marker { display: none; }
        details p {
            margin: 10px 0 0;
            color: var(--muted);
            line-height: 1.6;
        }

        /* Footer */
        .footer {
            padding: 36px 0 60px;
            color: var(--muted2);
            border-top: 1px solid var(--border);
            margin-top: 30px;
        }
        .footer-inner {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }

        /* Responsive */
        @media (max-width: 940px) {
            .hero-grid { grid-template-columns: 1fr; }
            .grid { grid-template-columns: 1fr; }
            .nav-links { display: none; }
        }
    </style>
</head>
<body>

    <!-- NAV -->
    <div class="nav">
        <div class="container nav-inner">
            <div class="logo">
                <div class="logo-badge"></div>
                <div>
                    <div style="font-size:15px; font-weight:700;">OverView</div>
                    <div style="font-size:12px; color: var(--muted2); margin-top:2px;">Remote Control Program</div>
                </div>
            </div>

            <div class="nav-links">
                <a href="#features">Features</a>
                <a href="#faq">FAQ</a>
                <a href="#download">Download</a>
            </div>
        </div>
    </div>

    <!-- HERO -->
    <div class="hero">
        <div class="container hero-grid">
            <div>
                <div class="pill">
                    <div class="pill-dot"></div>
                    <div>항상 최신 버전 유지 · 자동 업데이트</div>
                </div>

                <h1 class="headline">Fast, Stable,<br/>Remote Control Experience</h1>

                <p class="subhead">
                    OverView는 여러 대의 PC를 효율적으로 관리하고 원격 제어할 수 있도록 설계된 프로그램입니다.
                    안정적인 연결, 직관적인 UI, 빠른 반응 속도를 제공합니다.
                </p>

                <div class="cta-row" id="download">
                    <a class="btn primary" href="/download">
                        <span>⬇</span> 다운로드
                    </a>
                    <a class="btn" href="#features">기능 보기</a>
                </div>

                <div style="margin-top:14px; color: var(--muted2); font-size: 13px;">
                    * 다운로드 버튼을 누르면 최신 파일을 받습니다.
                </div>
            </div>

            <div class="hero-card">
                <div class="hero-card-top">
                    <div>
                        <p class="hero-card-title">Status</p>
                        <div class="hero-card-tag">Production-ready</div>
                    </div>
                    <div class="mini-badges">
                        <div class="mini"></div>
                        <div class="mini"></div>
                        <div class="mini"></div>
                    </div>
                </div>
                <div class="hero-card-body">
                    <div class="stat"><strong>Latency</strong><span>Low</span></div>
                    <div class="stat"><strong>Multi-Client</strong><span>Supported</span></div>
                    <div class="stat"><strong>Security</strong><span>Auth & Roles</span></div>
                    <div class="stat"><strong>Update</strong><span>Auto Deploy</span></div>
                </div>
            </div>
        </div>
    </div>

    <!-- FEATURES -->
    <div class="section" id="features">
        <div class="container">
            <h2>주요 기능</h2>
            <p class="lead">
                실사용을 기준으로 필요한 기능을 깔끔하게 담았습니다.
            </p>

            <div class="grid">
                <div class="card">
                    <div class="icon">⚡</div>
                    <h3>빠른 반응 속도</h3>
                    <p>원격 화면/입력 전달을 최적화하여 지연을 줄였습니다.</p>
                </div>

                <div class="card">
                    <div class="icon">🖥️</div>
                    <h3>다중 PC 관리</h3>
                    <p>여러 클라이언트를 동시에 관리하고 그룹 단위로 운영할 수 있습니다.</p>
                </div>

                <div class="card">
                    <div class="icon">🔒</div>
                    <h3>로그인 기반 접근</h3>
                    <p>권한/역할(Role) 기반으로 매니저/클라이언트 구분 운영이 가능합니다.</p>
                </div>
            </div>
        </div>
    </div>

    <!-- FAQ -->
    <div class="section" id="faq">
        <div class="container">
            <h2>FAQ</h2>
            <p class="lead">자주 묻는 질문을 정리했습니다.</p>

            <div class="faq">
                <details>
                    <summary>Q. 다운로드 버튼을 누르면 어떤 파일이 받아지나요?</summary>
                    <p>항상 최신 버전의 프로그램 zip 파일을 다운로드합니다.</p>
                </details>

                <details>
                    <summary>Q. 업데이트는 어떻게 되나요?</summary>
                    <p>GitHub 저장소 변경사항 또는 릴리스 업데이트 시 최신 파일을 내려받도록 구성할 수 있습니다.</p>
                </details>

                <details>
                    <summary>Q. 설치가 필요한가요?</summary>
                    <p>배포 형태에 따라 다르며, 일반적으로 zip을 풀고 실행하면 됩니다.</p>
                </details>
            </div>
        </div>
    </div>

    <!-- FOOTER -->
    <div class="footer">
        <div class="container footer-inner">
            <div>© OverView</div>
            <div style="display:flex; gap:10px;">
                <a href="#features">Features</a>
                <a href="#faq">FAQ</a>
                <a href="#download">Download</a>
            </div>
        </div>
    </div>

    <script>
        // FAQ 아코디언 애니메이션을 조금 더 부드럽게
        document.addEventListener('DOMContentLoaded', () => {
            const details = document.querySelectorAll('details');
            details.forEach(d => {
                d.addEventListener('toggle', () => {
                    if (d.open) {
                        details.forEach(other => {
                            if (other !== d) other.open = false;
                        });
                    }
                });
            });
        });
    </script>
</body>
</html>
"""

# --- Flask 라우트(경로) 정의 ---

@app.route('/')
def index():
    """메인 웹페이지를 렌더링합니다."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/download')
def download_file():
    """다운로드 요청을 GitHub Releases(최신)로 리다이렉트합니다."""
    return redirect(DOWNLOAD_URL, code=302)

if __name__ == '__main__':
    # 로컬 테스트 서버 실행
    print("로컬 테스트 서버를 시작합니다. http://127.0.0.1:5001 에서 접속하세요." )
    app.run(host='0.0.0.0', port=5001, debug=True)
