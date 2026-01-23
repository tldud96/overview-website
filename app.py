import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string, flash
from werkzeug.utils import secure_filename

# 현재 작업 디렉토리를 파일 저장 폴더로 사용합니다.
UPLOAD_FOLDER = os.getcwd()
# 프로그램 파일명을 'OverView.zip'으로 변경합니다.
PROGRAM_FILENAME = 'OverView.zip'
ALLOWED_EXTENSIONS = {'zip'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'supersecretkey_change_this_later'

# --- HTML, CSS, JS 코드 ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OverView - 원격 제어 솔루션</title>
    <style>
        /* CSS 스타일은 이전과 동일합니다. */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&family=Noto+Sans+KR:wght@400;500;700&display=swap' );
        :root { --bg-color: #0a0e27; --frame-bg: #1a1f3a; --primary-neon: #64b5f6; --secondary-neon: #4dffaf; --text-color: #e0e0e0; --text-dark: #a0a0a0; --border-color: #2a3f7f; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html { scroll-behavior: smooth; }
        body { font-family: 'Poppins', 'Noto Sans KR', sans-serif; background-color: var(--bg-color); color: var(--text-color); line-height: 1.8; }
        .container { max-width: 1100px; margin: 0 auto; padding: 0 30px; }
        header { background: rgba(10, 14, 39, 0.8); backdrop-filter: blur(10px); position: fixed; width: 100%; top: 0; z-index: 100; border-bottom: 1px solid var(--border-color); }
        .navbar { display: flex; justify-content: space-between; align-items: center; height: 70px; }
        .logo { font-size: 28px; font-weight: 700; color: var(--primary-neon); text-shadow: 0 0 8px rgba(100, 181, 246, 0.7); cursor: pointer; }
        .nav-menu { list-style: none; display: flex; }
        .nav-menu li { margin-left: 30px; }
        .nav-menu a { color: var(--text-color); text-decoration: none; font-weight: 500; transition: all 0.3s ease; padding: 5px 0; border-bottom: 2px solid transparent; }
        .nav-menu a:hover { color: var(--primary-neon); text-shadow: 0 0 3px var(--primary-neon); border-bottom-color: var(--primary-neon); }
        .section { padding: 120px 0; border-bottom: 1px solid var(--border-color); }
        .section:last-child { border-bottom: none; }
        .section-title { font-size: 42px; font-weight: 700; text-align: center; margin-bottom: 60px; color: #fff; text-shadow: 0 0 8px rgba(100, 181, 246, 0.5); }
        #hero { height: 100vh; min-height: 700px; display: flex; justify-content: center; align-items: center; text-align: center; }
        .hero-content { max-width: 800px; }
        .hero-content h1 { font-size: 56px; font-weight: 700; color: #fff; line-height: 1.3; margin: 0; }
        .hero-content .highlight { display: block; font-size: 72px; color: #cce7ff; text-shadow: 0 0 5px rgba(100, 181, 246, 0.7), 0 0 12px rgba(100, 181, 246, 0.5), 0 0 25px rgba(100, 181, 246, 0.3); margin: 10px 0 25px 0; }
        .hero-content p { font-size: 18px; max-width: 600px; margin: 0 auto 40px auto; color: var(--text-dark); }
        .btn { display: inline-block; padding: 15px 35px; background: var(--primary-neon); color: var(--bg-color); font-weight: 700; text-decoration: none; border-radius: 50px; transition: all 0.3s ease; box-shadow: 0 0 15px var(--primary-neon), inset 0 0 5px rgba(255,255,255,0.5); }
        .btn:hover { transform: translateY(-3px); box-shadow: 0 0 25px var(--primary-neon), 0 0 40px var(--secondary-neon), inset 0 0 5px rgba(255,255,255,0.5); }
        #download { padding: 120px 0; }
        .download-box { background: var(--frame-bg); padding: 50px; border-radius: 15px; text-align: center; border: 1px solid var(--border-color); box-shadow: 0 0 30px rgba(26, 31, 58, 0.5); }
        .download-box h3 { font-size: 28px; margin-bottom: 15px; color: #fff; text-shadow: 0 0 8px rgba(100, 181, 246, 0.5); }
        .download-box p { color: var(--text-dark); margin-bottom: 30px; font-size: 18px; }
        .download-box .btn { transform: scale(1.1); font-size: 18px; }
        /* ... 나머지 CSS는 동일 ... */
    </style>
</head>
<body>
    <!-- ... 나머지 HTML은 동일 ... -->
    <main>
        <!-- ... -->
        <section id="download" class="section">
            <div class="container">
                <div class="download-box">
                    <h3>지금 바로 OverView를 경험해보세요</h3>
                    <p>최신 버전의 클라이언트 프로그램을 다운로드하여 설치하세요.</p>
                    <a href="{{ url_for('download_file') }}" class="btn">OverView 다운로드</a>
                </div>
            </div>
        </section>
        <!-- ... -->
    </main>
    <!-- ... -->
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
    """파일 다운로드 링크를 처리합니다."""
    # 현재 작업 디렉토리에서 PROGRAM_FILENAME을 찾아 다운로드합니다.
    return send_from_directory(app.config['UPLOAD_FOLDER'], PROGRAM_FILENAME, as_attachment=True)

# 파일 업로드 기능은 현재 구조에서 불필요하므로 제거하거나 주석 처리합니다.
# GitHub를 통해 직접 파일을 올리는 것이 더 확실한 방법입니다.

if __name__ == '__main__':
    # 로컬 테스트 서버 실행
    print("로컬 테스트 서버를 시작합니다. https://127.0.0.1:5001 에서 접속하세요." )
    app.run(host='0.0.0.0', port=5001, debug=True, ssl_context='adhoc')

