from flask import Flask, render_template_string, send_file, jsonify, redirect
from datetime import datetime
import random
import os

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config["SECRET_KEY"] = "supersecretkey_final_version"

# GitHub Releases 다운로드 설정
GITHUB_OWNER = "tldud96"
GITHUB_REPO = "overview-website"
PROGRAM_FILENAME = "OverView.zip"
DOWNLOAD_URL = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest/download/{PROGRAM_FILENAME}"

# =========================
# 대시보드 데이터 생성
# =========================
def generate_cpu_data():
    """CPU 사용률 시계열 데이터 생성"""
    data = []
    for i in range(24):
        hour = f"{i:02d}:00"
        usage = random.randint(20, 60)
        data.append({"time": hour, "usage": usage})
    return data

def get_system_status():
    """시스템 상태 데이터"""
    return [
        {"id": 1, "name": "PC-01", "status": "online", "cpu": 32, "memory": 12.6, "disk": 157},
        {"id": 2, "name": "PC-02", "status": "online", "cpu": 28, "memory": 8.2, "disk": 234},
        {"id": 3, "name": "PC-03", "status": "offline", "cpu": 0, "memory": 0, "disk": 0},
        {"id": 4, "name": "PC-04", "status": "online", "cpu": 45, "memory": 15.3, "disk": 89},
    ]

# =========================
# 웹사이트 HTML (OverView 프로그램 스타일)
# =========================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OverView - 원격 제어 솔루션</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>

    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=Noto+Sans+KR:wght@400;500;700&display=swap');

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --dark-bg: #0F1419;
            --dark-panel: #1A1F2E;
            --dark-hover: #252D3D;
            --accent-blue: #00A8E8;
            --accent-cyan: #00D9FF;
            --text-primary: #E0E0E0;
            --text-secondary: #A0A0A0;
            --border-color: #2A3548;
            --status-online: #00FF41;
            --status-offline: #FF4444;
        }

        body {
            font-family: 'Roboto', 'Noto Sans KR', sans-serif;
            background-color: var(--dark-bg);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Roboto', 'Noto Sans KR', sans-serif;
            font-weight: 500;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }

        /* ========== Header ========== */
        header {
            background-color: var(--dark-panel);
            border-bottom: 1px solid var(--border-color);
            padding: 15px 0;
            position: sticky;
            top: 0;
            z-index: 100;
            animation: slideDown 0.5s ease-out;
        }

        @keyframes slideDown {
            from {
                transform: translateY(-100%);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }

        header .container {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .nav-buttons {
            display: flex;
            gap: 15px;
        }

        button {
            background-color: var(--dark-hover);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s ease;
        }

        button:hover {
            background-color: var(--accent-blue);
            border-color: var(--accent-blue);
            color: #000;
        }

        /* ========== Hero Section ========== */
        .hero {
            padding: 80px 0;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            align-items: center;
            animation: fadeInUp 0.8s ease-out;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .hero h1 {
            font-size: 48px;
            line-height: 1.2;
            margin-bottom: 20px;
            color: var(--text-primary);
        }

        .hero h1 .highlight {
            color: var(--accent-cyan);
        }

        .hero p {
            font-size: 16px;
            color: var(--text-secondary);
            margin-bottom: 30px;
            line-height: 1.8;
        }

        .hero-buttons {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan));
            color: #000;
            padding: 12px 30px;
            border: none;
            border-radius: 4px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 168, 232, 0.3);
        }

        .hero-image {
            background: linear-gradient(135deg, rgba(0, 168, 232, 0.1), rgba(0, 217, 255, 0.1));
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 300px;
            animation: float 3s ease-in-out infinite;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }

        .hero-image img {
            max-width: 100%;
            height: auto;
        }

        /* ========== Features Section ========== */
        .features {
            padding: 60px 0;
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 30px;
            margin-bottom: 60px;
        }

        .feature-card {
            background-color: var(--dark-panel);
            border: 1px solid var(--border-color);
            padding: 30px;
            border-radius: 8px;
            transition: all 0.3s ease;
            animation: slideInUp 0.6s ease-out;
        }

        @keyframes slideInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .feature-card:hover {
            border-color: var(--accent-blue);
            background-color: var(--dark-hover);
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 168, 232, 0.2);
        }

        .feature-icon {
            font-size: 40px;
            margin-bottom: 15px;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .feature-card h3 {
            font-size: 18px;
            margin-bottom: 10px;
            color: var(--text-primary);
        }

        .feature-card p {
            font-size: 14px;
            color: var(--text-secondary);
        }

        /* ========== Dashboard Section ========== */
        .dashboard-section {
            padding: 60px 0;
            background-color: var(--dark-panel);
            border-radius: 8px;
            padding: 40px;
            margin-bottom: 60px;
        }

        .dashboard-section h2 {
            font-size: 28px;
            margin-bottom: 30px;
            color: var(--accent-blue);
        }

        .system-cards {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 40px;
        }

        .system-card {
            background-color: var(--dark-bg);
            border: 1px solid var(--border-color);
            padding: 20px;
            border-radius: 8px;
            transition: all 0.3s ease;
            animation: bounceIn 0.6s ease-out;
        }

        @keyframes bounceIn {
            0% {
                opacity: 0;
                transform: scale(0.9);
            }
            100% {
                opacity: 1;
                transform: scale(1);
            }
        }

        .system-card:hover {
            border-color: var(--accent-cyan);
            background-color: var(--dark-hover);
        }

        .system-card h4 {
            font-size: 16px;
            margin-bottom: 15px;
            color: var(--accent-blue);
        }

        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .status-indicator.online {
            background-color: var(--status-online);
        }

        .status-indicator.offline {
            background-color: var(--status-offline);
        }

        .system-info {
            font-size: 13px;
            color: var(--text-secondary);
            margin-bottom: 10px;
        }

        .progress-bar {
            background-color: rgba(0, 168, 232, 0.2);
            border-radius: 4px;
            height: 6px;
            margin-bottom: 5px;
            overflow: hidden;
        }

        .progress-fill {
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan));
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s ease;
        }

        .charts-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }

        .chart-wrapper {
            background-color: var(--dark-bg);
            border: 1px solid var(--border-color);
            padding: 20px;
            border-radius: 8px;
            height: 300px;
        }

        /* ========== QR Code ========== */
        .qr-code-container {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background-color: var(--dark-panel);
            border: 2px solid var(--accent-blue);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            z-index: 1000;
            animation: slideInRight 0.6s ease-out;
            box-shadow: 0 0 20px rgba(0, 168, 232, 0.3);
            transition: all 0.3s ease;
        }

        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(100px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        .qr-code-container:hover {
            transform: translateY(-5px);
            box-shadow: 0 0 30px rgba(0, 217, 255, 0.5);
        }

        .qr-code-container img {
            width: 120px;
            height: 120px;
            border-radius: 4px;
        }

        .qr-label {
            font-size: 12px;
            color: var(--accent-cyan);
            margin-top: 10px;
            font-weight: 600;
        }

        /* ========== Footer ========== */
        footer {
            background-color: var(--dark-panel);
            border-top: 1px solid var(--border-color);
            padding: 40px 0;
            margin-top: 60px;
        }

        .footer-content {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 30px;
            margin-bottom: 30px;
        }

        .footer-section h4 {
            font-size: 14px;
            margin-bottom: 15px;
            color: var(--accent-blue);
        }

        .footer-section a {
            display: block;
            font-size: 13px;
            color: var(--text-secondary);
            text-decoration: none;
            margin-bottom: 8px;
            transition: color 0.3s ease;
        }

        .footer-section a:hover {
            color: var(--accent-cyan);
        }

        .footer-bottom {
            border-top: 1px solid var(--border-color);
            padding-top: 20px;
            text-align: center;
            font-size: 12px;
            color: var(--text-secondary);
        }

        .status-bar {
            background-color: var(--dark-panel);
            border-top: 1px solid var(--border-color);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: var(--text-secondary);
            position: fixed;
            bottom: 0;
            width: 100%;
            left: 0;
        }

        @media (max-width: 768px) {
            .hero {
                grid-template-columns: 1fr;
            }
            .features {
                grid-template-columns: 1fr;
            }
            .system-cards {
                grid-template-columns: repeat(2, 1fr);
            }
            .charts-container {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>

<!-- Header -->
<header>
    <div class="container">
        <div class="logo">OverView</div>
        <div class="nav-buttons">
            <button>로그인</button>
            <button onclick="window.location.href='/download'">다운로드</button>
        </div>
    </div>
</header>

<!-- Hero Section -->
<div class="container">
    <section class="hero">
        <div>
            <h1>가장 직관적인 <br><span class="highlight">원격 제어 솔루션</span></h1>
            <p>여러 대의 PC를 하나의 화면에서 안정적으로 관리하세요. 실시간 모니터링, 원격 제어, 파일 전송까지 모든 기능을 한 곳에서.</p>
            <div class="hero-buttons">
                <button class="btn-primary" onclick="window.location.href='/download'">지금 다운로드</button>
                <button class="btn-primary" onclick="openDemo()" style="background: transparent; border: 2px solid var(--accent-blue); color: var(--accent-blue);">데모 보기</button>
            </div>
        </div>
        <div class="hero-image">
            <div style="text-align: center; color: var(--text-secondary);">
                <i class="fas fa-desktop" style="font-size: 60px; margin-bottom: 20px; opacity: 0.5;"></i>
                <p>원격 관리 화면</p>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section class="features">
        <div class="feature-card">
            <div class="feature-icon"><i class="fas fa-desktop"></i></div>
            <h3>실시간 화면 공유</h3>
            <p>다중 PC 화면을 동시에 모니터링하고 관리하세요</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon"><i class="fas fa-bolt"></i></div>
            <h3>원격 제어</h3>
            <p>지연 없는 키보드와 마우스 입력으로 즉시 제어</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon"><i class="fas fa-folder"></i></div>
            <h3>파일 전송</h3>
            <p>단일·다중 PC에 파일을 빠르게 배포</p>
        </div>
    </section>

    <!-- Dashboard Section -->
    <section class="dashboard-section">
        <h2>인터랙티브 대시보드</h2>
        
        <div class="system-cards">
            {% for pc in system_status %}
            <div class="system-card">
                <h4>{{ pc.name }}</h4>
                <div>
                    <span class="status-indicator {{ pc.status }}"></span>
                    <span style="font-size: 12px; color: var(--text-secondary);">{{ pc.status | upper }}</span>
                </div>
                <div class="system-info">CPU {{ pc.cpu }}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ pc.cpu }}%"></div>
                </div>
                <div class="system-info">메모리 {{ pc.memory }} GB</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ (pc.memory / 32 * 100) | int }}%"></div>
                </div>
                <div class="system-info">디스크 {{ pc.disk }} GB</div>
            </div>
            {% endfor %}
        </div>

        <div class="charts-container">
            <div class="chart-wrapper">
                <canvas id="cpuChart"></canvas>
            </div>
            <div class="chart-wrapper">
                <canvas id="networkChart"></canvas>
            </div>
        </div>
    </section>

    <!-- CTA Section -->
    <section style="text-align: center; padding: 60px 0; margin-bottom: 100px;">
        <h2 style="font-size: 32px; margin-bottom: 20px;">지금 OverView를 시작하세요</h2>
        <p style="color: var(--text-secondary); margin-bottom: 30px;">무료로 다운로드하고 원격 관리의 새로운 경험을 해보세요</p>
        <button class="btn-primary" onclick="window.location.href='/download'">지금 다운로드</button>
    </section>

    <!-- Footer -->
    <footer>
        <div class="footer-content">
            <div class="footer-section">
                <h4>기능</h4>
                <a href="#">실시간 모니터링</a>
                <a href="#">원격 제어</a>
                <a href="#">파일 전송</a>
            </div>
            <div class="footer-section">
                <h4>지원</h4>
                <a href="#">문서</a>
                <a href="#">FAQ</a>
                <a href="#">연락처</a>
            </div>
            <div class="footer-section">
                <h4>회사</h4>
                <a href="#">소개</a>
                <a href="#">블로그</a>
                <a href="#">채용</a>
            </div>
            <div class="footer-section">
                <h4>법률</h4>
                <a href="#">개인정보</a>
                <a href="#">이용약관</a>
                <a href="#">라이선스</a>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; 2026 OverView. All rights reserved.</p>
        </div>
    </footer>
</div>

<!-- QR Code -->
<div class="qr-code-container">
    <img src="data:image/png;base64,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" alt="QR Code">
    <div class="qr-label">@AHCONSULT</div>
</div>

<!-- Demo Modal -->
<div id="demoModal" class="modal" style="display: none; position: fixed; z-index: 2000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.7);">
    <div class="modal-content" style="background-color: var(--dark-panel); margin: 10% auto; padding: 30px; border: 1px solid var(--border-color); border-radius: 8px; width: 80%; max-width: 600px; max-height: 80vh; overflow-y: auto;">
        <span class="close" onclick="closeDemo()" style="color: var(--accent-cyan); float: right; font-size: 28px; font-weight: bold; cursor: pointer;">&times;</span>
        <h2 style="margin-bottom: 20px; color: var(--accent-blue);">📚 프로그램 사용 방법</h2>
        <div style="display: grid; grid-template-columns: 1fr; gap: 20px;">
            <div style="background-color: var(--dark-bg); padding: 15px; border-radius: 4px; border-left: 3px solid var(--accent-blue);">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <span style="background-color: var(--accent-blue); color: #000; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; margin-right: 10px;">1</span>
                    <h4>프로그램 다운로드</h4>
                </div>
                <p style="color: var(--text-secondary); font-size: 13px;">OverView 설치 파일을 다운로드하고 실행합니다. Windows 10 이상에서 지원됩니다.</p>
            </div>
            <div style="background-color: var(--dark-bg); padding: 15px; border-radius: 4px; border-left: 3px solid var(--accent-blue);">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <span style="background-color: var(--accent-blue); color: #000; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; margin-right: 10px;">2</span>
                    <h4>계정 생성 및 로그인</h4>
                </div>
                <p style="color: var(--text-secondary); font-size: 13px;">프로그램을 실행하면 로그인 화면이 나타납니다. 계정을 생성하고 로그인하세요.</p>
            </div>
            <div style="background-color: var(--dark-bg); padding: 15px; border-radius: 4px; border-left: 3px solid var(--accent-blue);">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <span style="background-color: var(--accent-blue); color: #000; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; margin-right: 10px;">3</span>
                    <h4>PC 연결</h4>
                </div>
                <p style="color: var(--text-secondary); font-size: 13px;">관리할 PC들을 프로그램에 추가합니다. 각 PC에 클라이언트를 설치하면 자동으로 연결됩니다.</p>
            </div>
            <div style="background-color: var(--dark-bg); padding: 15px; border-radius: 4px; border-left: 3px solid var(--accent-blue);">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <span style="background-color: var(--accent-blue); color: #000; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; margin-right: 10px;">4</span>
                    <h4>화면 모니터링</h4>
                </div>
                <p style="color: var(--text-secondary); font-size: 13px;">메인 화면에서 모든 연결된 PC의 화면을 실시간으로 확인할 수 있습니다.</p>
            </div>
            <div style="background-color: var(--dark-bg); padding: 15px; border-radius: 4px; border-left: 3px solid var(--accent-blue);">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <span style="background-color: var(--accent-blue); color: #000; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; margin-right: 10px;">5</span>
                    <h4>원격 제어</h4>
                </div>
                <p style="color: var(--text-secondary); font-size: 13px;">원하는 PC를 선택하면 마우스와 키보드로 원격 제어가 가능합니다. 마치 직접 조작하는 것처럼!</p>
            </div>
            <div style="background-color: var(--dark-bg); padding: 15px; border-radius: 4px; border-left: 3px solid var(--accent-blue);">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <span style="background-color: var(--accent-blue); color: #000; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; margin-right: 10px;">6</span>
                    <h4>파일 전송</h4>
                </div>
                <p style="color: var(--text-secondary); font-size: 13px;">드래그 앤 드롭으로 파일을 여러 PC에 동시에 전송할 수 있습니다. 효율적인 파일 관리!</p>
            </div>
        </div>
    </div>
</div>

<!-- Status Bar -->
<div class="status-bar">
    <div>SYSTEM READY | ACTIVE 1</div>
    <div>CONTROL IP: 192.168.1.100</div>
    <div>{{ current_time }}</div>
</div>

<script>
    // Demo Modal
    function openDemo() {
        document.getElementById('demoModal').style.display = 'block';
    }

    function closeDemo() {
        document.getElementById('demoModal').style.display = 'none';
    }

    window.onclick = function(event) {
        const modal = document.getElementById('demoModal');
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }

    // CPU Chart
    const cpuCtx = document.getElementById('cpuChart').getContext('2d');
    new Chart(cpuCtx, {
        type: 'line',
        data: {
            labels: {{ cpu_data | tojson | safe }}.map(d => d.time),
            datasets: [{
                label: 'CPU 사용률 (%)',
                data: {{ cpu_data | tojson | safe }}.map(d => d.usage),
                borderColor: '#00A8E8',
                backgroundColor: 'rgba(0, 168, 232, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 3,
                pointBackgroundColor: '#00A8E8',
                pointBorderColor: '#1A1F2E',
                pointBorderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#A0A0A0', font: { size: 11 } }
                },
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#A0A0A0', font: { size: 11 } }
                }
            }
        }
    });

    // Network Chart
    const networkCtx = document.getElementById('networkChart').getContext('2d');
    new Chart(networkCtx, {
        type: 'bar',
        data: {
            labels: ['다운로드', '업로드'],
            datasets: [{
                label: '속도 (Mbps)',
                data: [85, 45],
                backgroundColor: ['#00A8E8', '#00D9FF'],
                borderColor: ['#00A8E8', '#00D9FF'],
                borderRadius: 2,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#A0A0A0', font: { size: 11 } }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: '#A0A0A0', font: { size: 11 } }
                }
            }
        }
    });
</script>

</body>
</html>
"""

# =========================
# Flask 라우트
# =========================
@app.route("/")
def index():
    cpu_data = generate_cpu_data()
    system_status = get_system_status()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template_string(HTML_TEMPLATE, cpu_data=cpu_data, system_status=system_status, current_time=current_time)

@app.route("/download")
def download():
    return redirect(DOWNLOAD_URL)

@app.route("/qr")
def serve_qr():
    """QR 코드 이미지 직접 서빙"""
    qr_path = os.path.join(os.path.dirname(__file__), 'qr_code.png')
    if os.path.exists(qr_path):
        return send_file(qr_path, mimetype='image/png')
    else:
        # 파일이 없으면 빈 이미지 반환
        return "QR Code not found", 404

@app.route("/api/dashboard")
def api_dashboard():
    """API 엔드포인트 - JSON 형식의 대시보드 데이터"""
    return jsonify({
        "cpu_data": generate_cpu_data(),
        "system_status": get_system_status(),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
