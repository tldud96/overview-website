import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string, flash
from werkzeug.utils import secure_filename

# --- 설정 ---
# Render.com의 디스크 Mount Path와 로컬 환경을 모두 고려합니다.
UPLOAD_FOLDER = os.getcwd()
PROGRAM_FILENAME = 'OverView.zip'
ALLOWED_EXTENSIONS = {'zip'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'supersecretkey_change_this_later' # 실제 운영 시에는 더 복잡한 키로 변경하세요.

# --- HTML, CSS, JS 코드 ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OverView - 원격 제어 솔루션</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&family=Noto+Sans+KR:wght@400;500;700&display=swap' );
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
        html { scroll-behavior: smooth; }
        body {
            font-family: 'Poppins', 'Noto Sans KR', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.8;
        }
        .container { max-width: 1100px; margin: 0 auto; padding: 0 30px; }
        header {
            background: rgba(10, 14, 39, 0.8);
            backdrop-filter: blur(10px);
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 100;
            border-bottom: 1px solid var(--border-color);
        }
        .navbar { display: flex; justify-content: space-between; align-items: center; height: 70px; }
        .logo {
            font-size: 28px;
            font-weight: 700;
            color: var(--primary-neon);
            text-shadow: 0 0 8px rgba(100, 181, 246, 0.7);
            cursor: pointer;
        }
        .nav-menu { list-style: none; display: flex; }
        .nav-menu li { margin-left: 30px; }
        .nav-menu a {
            color: var(--text-color);
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
            padding: 5px 0;
            border-bottom: 2px solid transparent;
        }
        .nav-menu a:hover {
            color: var(--primary-neon);
            text-shadow: 0 0 3px var(--primary-neon);
            border-bottom-color: var(--primary-neon);
        }
        .section { padding: 120px 0; border-bottom: 1px solid var(--border-color); }
        .section:last-child { border-bottom: none; }
        .section-title {
            font-size: 42px;
            font-weight: 700;
            text-align: center;
            margin-bottom: 60px;
            color: #fff;
            text-shadow: 0 0 8px rgba(100, 181, 246, 0.5);
        }
        #hero {
            height: 100vh;
            min-height: 700px;
            display: flex;
            justify-content: center;
            align-items: center;
            text-align: center;
        }
        .hero-content { max-width: 800px; }
        .hero-content h1 {
            font-size: 56px;
            font-weight: 700;
            color: #fff;
            line-height: 1.3;
            margin: 0;
        }
        .hero-content .highlight {
            display: block;
            font-size: 72px;
            color: #cce7ff;
            text-shadow: 0 0 5px rgba(100, 181, 246, 0.7), 0 0 12px rgba(100, 181, 246, 0.5), 0 0 25px rgba(100, 181, 246, 0.3);
            margin: 10px 0 25px 0;
        }
        .hero-content p {
            font-size: 18px;
            max-width: 600px;
            margin: 0 auto 40px auto;
            color: var(--text-dark);
        }
        .btn {
            display: inline-block;
            padding: 15px 35px;
            background: var(--primary-neon);
            color: var(--bg-color);
            font-weight: 700;
            text-decoration: none;
            border-radius: 50px;
            transition: all 0.3s ease;
            box-shadow: 0 0 15px var(--primary-neon), inset 0 0 5px rgba(255,255,255,0.5);
        }
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 0 25px var(--primary-neon), 0 0 40px var(--secondary-neon), inset 0 0 5px rgba(255,255,255,0.5);
        }
        #download { padding: 120px 0; }
        .download-box {
            background: var(--frame-bg);
            padding: 50px;
            border-radius: 15px;
            text-align: center;
            border: 1px solid var(--border-color);
            box-shadow: 0 0 30px rgba(26, 31, 58, 0.5);
        }
        .download-box h3 {
            font-size: 28px;
            margin-bottom: 15px;
            color: #fff;
            text-shadow: 0 0 8px rgba(100, 181, 246, 0.5);
        }
        .download-box p {
            color: var(--text-dark);
            margin-bottom: 30px;
            font-size: 18px;
        }
        .download-box .btn { transform: scale(1.1); font-size: 18px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; }
        .card {
            background: var(--frame-bg);
            padding: 30px;
            border-radius: 10px;
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
            border-color: var(--primary-neon);
            box-shadow: 0 0 20px rgba(100, 181, 246, 0.2);
        }
        .card h3 { font-size: 22px; color: var(--secondary-neon); margin-bottom: 15px; }
        .card .step-number { font-size: 28px; font-weight: 700; color: var(--border-color); margin-bottom: 10px; }
        .feature-card { text-align: center; }
        .feature-card .icon { font-size: 48px; margin-bottom: 20px; color: var(--primary-neon); text-shadow: 0 0 10px var(--primary-neon); }
        .feature-card h3 { color: var(--secondary-neon); }
        .feature-card p { color: var(--text-dark); font-size: 15px; }
        .faq-item { border-bottom: 1px solid var(--border-color); padding: 20px 0; }
        .faq-item:last-child { border-bottom: none; }
        .faq-question {
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            position: relative;
            padding-right: 30px;
        }
        .faq-question::after {
            content: '+';
            position: absolute;
            right: 0;
            font-size: 24px;
            color: var(--primary-neon);
            transition: transform 0.3s;
        }
        .faq-item.active .faq-question::after { transform: rotate(45deg); }
        .faq-answer {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.5s ease-out;
            padding-top: 0;
            color: var(--text-dark);
        }
        .faq-item.active .faq-answer { padding-top: 15px; }
        footer { text-align: center; padding: 40px 0; color: var(--text-dark); }
    </style>
</head>
<body>
    <header>
        <nav class="navbar container">
            <a href="/" class="logo">OverView</a>
            <ul class="nav-menu">
                <li><a href="#hero">소개</a></li>
                <li><a href="#download">다운로드</a></li>
                <li><a href="#features">주요 기능</a></li>
                <li><a href="#how-to">사용법</a></li>
                <li><a href="#faq">FAQ</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <section id="hero">
            <div class="hero-content">
                <h1>가장 직관적인 원격 제어 솔루션,
                    <span class="highlight">OverView</span>
                </h1>
                <p>여러 대의 PC를 하나의 화면에서 관리하고, 클릭 한 번으로 즉시 제어하세요. OverView는 강력한 성능과 세련된 인터페이스로 원격 관리의 새로운 기준을 제시합니다.</p>
                <a href="#download" class="btn">지금 바로 시작하기</a>
            </div>
        </section>
        <section id="download" class="section">
            <div class="container">
                <div class="download-box">
                    <h3>지금 바로 OverView를 경험해보세요</h3>
                    <p>최신 버전의 클라이언트 프로그램을 다운로드하여 설치하세요.</p>
                    <a href="{{ url_for('download_file') }}" class="btn">OverView 다운로드</a>
                </div>
            </div>
        </section>
        <section id="features" class="section">
            <div class="container">
                <h2 class="section-title">주요 기능</h2>
                <div class="grid">
                    <div class="card feature-card">
                        <div class="icon">🖥️</div> <h3>실시간 화면 공유</h3> <p>지연 시간을 최소화한 고화질 화면 스트리밍으로 여러 대의 PC를 동시에 모니터링하세요.</p>
                    </div>
                    <div class="card feature-card">
                        <div class="icon">🖱️</div> <h3>원격 키보드/마우스</h3> <p>내 PC를 조작하듯, 원격지 PC의 키보드와 마우스를 완벽하게 제어할 수 있습니다.</p>
                    </div>
                    <div class="card feature-card">
                        <div class="icon">📋</div> <h3>양방향 클립보드</h3> <p>내 PC에서 복사한 텍스트를 원격 PC에 붙여넣거나, 그 반대의 작업도 자유롭게 수행하세요.</p>
                    </div>
                    <div class="card feature-card">
                        <div class="icon">🔊</div> <h3>실시간 사운드</h3> <p>원격 PC에서 재생되는 사운드를 내 PC에서 실시간으로 들으며 작업할 수 있습니다.</p>
                    </div>
                    <div class="card feature-card">
                        <div class="icon">📁</div> <h3>파일 전송</h3> <p>간단한 드래그 앤 드롭(예정)이나 메뉴를 통해 원격 PC와 파일을 손쉽게 주고받을 수 있습니다.</p>
                    </div>
                    <div class="card feature-card">
                        <div class="icon">📊</div> <h3>시스템 모니터링</h3> <p>CPU, 메모리 사용량, 디스크 공간 등 원격 PC의 핵심 시스템 정보를 실시간으로 확인합니다.</p>
                    </div>
                </div>
            </div>
        </section>
        <section id="how-to" class="section">
            <div class="container">
                <h2 class="section-title">기본 사용법</h2>
                <div class="grid">
                    <div class="card">
                        <div class="step-number">01</div> <h3>연결 설정</h3> <p>클라이언트 프로그램을 실행하고, 제어 PC(매니저)의 IP 주소를 입력합니다. 식별하기 쉬운 '이 PC 이름'을 설정한 후 '연결 시작' 버튼을 누르세요.</p>
                    </div>
                    <div class="card">
                        <div class="step-number">02</div> <h3>백그라운드 실행</h3> <p>연결이 시작되면 프로그램 창은 자동으로 사라지고, 작업 표시줄 트레이 아이콘으로 최소화됩니다. 이제 제어 PC에서 원격 관리를 시작할 수 있습니다.</p>
                    </div>
                    <div class="card">
                        <div class="step-number">03</div> <h3>제어권 관리</h3> <p>여러 매니저가 동시에 접속한 경우, 오직 한 명의 매니저만 '제어 모드'로 전환하여 PC를 조작할 수 있습니다. 이는 입력 충돌을 방지하기 위한 기능입니다.</p>
                    </div>
                </div>
            </div>
        </section>
        <section id="faq" class="section">
            <div class="container">
                <h2 class="section-title">자주 묻는 질문</h2>
                <div class="faq-container">
                    <div class="faq-item">
                        <div class="faq-question">Q. 프로그램을 실행했지만 오류가 발생하며 작동하지 않습니다.</div>
                        <div class="faq-answer"> <p>A. 프로그램 실행에 필요한 시스템 드라이버가 설치되지 않았거나 다른 문제일 수 있습니다. <strong>문제를 직접 해결하려고 시도하지 마시고, 즉시 시스템 관리자에게 문의하여 지원을 받으시기 바랍니다.</strong></p> </div>
                    </div>
                    <div class="faq-item">
                        <div class="faq-question">Q. 연결이 되지 않거나 자꾸 끊어집니다.</div>
                        <div class="faq-answer"> <p>A. 먼저 제어 PC(매니저)의 IP 주소가 정확한지 확인해주세요. 또한, 클라이언트 PC와 제어 PC가 동일한 네트워크에 있는지, 방화벽이 포트 443을 차단하고 있지는 않은지 확인해야 합니다. 회사나 공용 네트워크의 경우, 네트워크 보안 정책에 의해 연결이 제한될 수 있습니다.</p> </div>
                    </div>
                    <div class="faq-item">
                        <div class="faq-question">Q. 제어권은 어떻게 얻나요?</div>
                        <div class="faq-answer"> <p>A. 제어권은 제어 PC(매니저) 프로그램에서 설정할 수 있습니다. 여러 클라이언트 화면 중 제어하고 싶은 PC를 선택하고 '제어 모드'로 전환하면 해당 PC의 제어권을 획득하게 됩니다. 동시에 두 명 이상의 매니저가 한 PC를 제어할 수는 없습니다.</p> </div>
                    </div>
                </div>
            </div>
        </section>
    </main>
    <footer>
        <div class="container">
            <p>&copy; 2026 OverView. All rights reserved.</p>
        </div>
    </footer>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const faqItems = document.querySelectorAll('.faq-item');
            faqItems.forEach(item => {
                const question = item.querySelector('.faq-question');
                const answer = item.querySelector('.faq-answer');
                question.addEventListener('click', () => {
                    const isActive = item.classList.toggle('active');
                    if (isActive) { answer.style.maxHeight = answer.scrollHeight + 'px'; } else { answer.style.maxHeight = '0'; }
                });
            });
        });
    </script>
</body>
</html>
"""

UPLOAD_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OverView - 파일 업로드</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap' );
        :root { --bg-color: #0a0e27; --frame-bg: #1a1f3a; --primary-neon: #64b5f6; --secondary-neon: #4dffaf; --text-color: #e0e0e0; --text-dark: #a0a0a0; --border-color: #2a3f7f; }
        body { font-family: 'Poppins', 'Noto Sans KR', sans-serif; background-color: var(--bg-color); color: var(--text-color); line-height: 1.8; }
        .upload-container { padding-top: 120px; min-height: 100vh; display: flex; flex-direction: column; align-items: center; }
        .section-title { font-size: 42px; font-weight: 700; text-align: center; margin-bottom: 60px; color: #fff; text-shadow: 0 0 8px rgba(100, 181, 246, 0.5); }
        .upload-form { background: var(--frame-bg); padding: 40px; border-radius: 10px; border: 1px solid var(--border-color); width: 100%; max-width: 500px; }
        .upload-form input[type="file"] { border: 2px dashed var(--border-color); padding: 20px; width: 100%; border-radius: 5px; margin-bottom: 20px; color: var(--text-dark); }
        .btn { display: inline-block; padding: 15px 35px; background: var(--primary-neon); color: var(--bg-color); font-weight: 700; text-decoration: none; border-radius: 50px; transition: all 0.3s ease; box-shadow: 0 0 15px var(--primary-neon), inset 0 0 5px rgba(255,255,255,0.5); }
        .btn:hover { transform: translateY(-3px); box-shadow: 0 0 25px var(--primary-neon), 0 0 40px var(--secondary-neon), inset 0 0 5px rgba(255,255,255,0.5); }
        .upload-form .btn { width: 100%; border: none; cursor: pointer; }
        .flash-message { padding: 15px; margin-bottom: 20px; border-radius: 5px; width: 100%; max-width: 500px; text-align: center; }
        .flash-success { background-color: #1e4620; color: #a7d7a9; border: 1px solid #3c8d40; }
        .flash-error { background-color: #4a1c1c; color: #f1b0b0; border: 1px solid #c53030; }
    </style>
</head>
<body>
    <div class="upload-container">
        <h1 class="section-title">OverView 파일 관리</h1>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash-message flash-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <form method="post" enctype="multipart/form-data" class="upload-form">
            <p style="color: var(--text-dark); margin-bottom: 20px;">
                업로드할 클라이언트 프로그램을 선택하세요.  

                파일 이름은 반드시 <strong>{{ program_filename }}</strong> 이어야 합니다.
            </p>
            <input type="file" name="file">
            <button type="submit" class="btn">업로드</button>
        </form>
    </div>
</body>
</html>
"""

# --- Flask 라우트(경로) 정의 ---

def allowed_file(filename):
    """파일 확장자 및 이름 확인"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS and \
           filename == PROGRAM_FILENAME

@app.route('/')
def index():
    """메인 웹페이지를 렌더링합니다."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/download')
def download_file():
    """파일 다운로드 링크를 처리합니다."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], PROGRAM_FILENAME, as_attachment=True)

@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    """파일 업로드 페이지를 처리합니다."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('파일 부분이 없습니다', 'error')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('선택된 파일이 없습니다', 'error')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # uploads 폴더가 없으면 생성
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash(f"'{filename}' 파일이 성공적으로 업로드되었습니다.", 'success')
            return redirect(request.url)
        else:
            flash(f"업로드 실패: 파일 이름이 '{PROGRAM_FILENAME}'이 아니거나 허용되지 않는 확장자입니다.", 'error')
            return redirect(request.url)
    return render_template_string(UPLOAD_PAGE_TEMPLATE, program_filename=PROGRAM_FILENAME)

if __name__ == '__main__':
    # 'uploads' 폴더가 없으면 생성
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    # 로컬 테스트 서버 실행
    print("로컬 테스트 서버를 시작합니다. https://127.0.0.1:5001 에서 접속하세요." )
    app.run(host='0.0.0.0', port=5001, debug=True, ssl_context='adhoc')


