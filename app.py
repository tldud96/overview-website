import os
import time
import json
from flask import Flask, render_template_string, redirect, jsonify, request, send_file
from datetime import datetime, timedelta
import random

# =========================
# GitHub Releases 다운로드 설정
# =========================
GITHUB_OWNER = "tldud96"
GITHUB_REPO = "overview-website"
PROGRAM_FILENAME = "OverView.zip"
DOWNLOAD_URL = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest/download/{PROGRAM_FILENAME}"

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey_final_version"

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
            padding: 16px 0;
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            font-size: 20px;
            font-weight: 700;
            color: var(--accent-blue);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .logo i {
            font-size: 24px;
        }

        .nav-right {
            display: flex;
            gap: 16px;
            align-items: center;
        }

        .btn {
            padding: 8px 20px;
            border: 1px solid var(--border-color);
            background-color: transparent;
            color: var(--text-primary);
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .btn:hover {
            background-color: var(--dark-hover);
            border-color: var(--accent-blue);
            color: var(--accent-blue);
        }

        .btn-primary {
            background-color: var(--accent-blue);
            border-color: var(--accent-blue);
            color: var(--dark-bg);
            font-weight: 500;
        }

        .btn-primary:hover {
            background-color: var(--accent-cyan);
            border-color: var(--accent-cyan);
        }

        /* ========== Tab Navigation ========== */
        .tab-nav {
            display: flex;
            gap: 0;
            border-bottom: 1px solid var(--border-color);
            background-color: var(--dark-panel);
            padding: 0 20px;
        }

        .tab-item {
            padding: 12px 24px;
            background-color: transparent;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 13px;
            border-bottom: 2px solid transparent;
            transition: all 0.2s ease;
            position: relative;
        }

        .tab-item:hover {
            color: var(--text-primary);
        }

        .tab-item.active {
            color: var(--accent-blue);
            border-bottom-color: var(--accent-blue);
        }

        /* ========== Main Content ========== */
        main {
            padding: 24px 0;
        }

        .section {
            margin-bottom: 40px;
        }

        .section-title {
            font-size: 18px;
            font-weight: 500;
            margin-bottom: 20px;
            color: var(--text-primary);
            padding: 0 20px;
        }

        /* ========== Hero Section ========== */
        .hero {
            background-color: var(--dark-panel);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            padding: 40px;
            margin: 0 20px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            align-items: center;
        }

        .hero-text h1 {
            font-size: 36px;
            line-height: 1.3;
            margin-bottom: 16px;
            color: var(--text-primary);
        }

        .hero-text h1 .highlight {
            color: var(--accent-blue);
        }

        .hero-text p {
            font-size: 14px;
            color: var(--text-secondary);
            margin-bottom: 24px;
            line-height: 1.8;
        }

        .hero-buttons {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }

        .hero-image {
            background-color: var(--dark-hover);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 300px;
        }

        .hero-image img {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }

        /* ========== Features Grid ========== */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
            padding: 0 20px;
        }

        .feature-card {
            background-color: var(--dark-panel);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            padding: 20px;
            transition: all 0.2s ease;
            cursor: pointer;
        }

        .feature-card:hover {
            background-color: var(--dark-hover);
            border-color: var(--accent-blue);
        }

        .feature-icon {
            font-size: 28px;
            color: var(--accent-blue);
            margin-bottom: 12px;
        }

        .feature-card h3 {
            font-size: 15px;
            margin-bottom: 8px;
            color: var(--text-primary);
        }

        .feature-card p {
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.6;
        }

        /* ========== Dashboard Section ========== */
        .dashboard-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 20px;
            margin-bottom: 16px;
        }

        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            padding: 0 20px;
            margin-bottom: 24px;
        }

        .status-card {
            background-color: var(--dark-panel);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            padding: 16px;
            transition: all 0.2s ease;
        }

        .status-card:hover {
            background-color: var(--dark-hover);
            border-color: var(--accent-blue);
        }

        .status-card.offline {
            opacity: 0.6;
        }

        .status-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }

        .status-name {
            font-weight: 500;
            color: var(--text-primary);
            font-size: 14px;
        }

        .status-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: var(--status-online);
        }

        .status-indicator.offline {
            background-color: var(--status-offline);
        }

        .status-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            font-size: 12px;
        }

        .status-label {
            color: var(--text-secondary);
        }

        .status-value {
            color: var(--accent-blue);
            font-weight: 500;
        }

        .progress-bar {
            width: 100%;
            height: 3px;
            background-color: var(--dark-hover);
            border-radius: 2px;
            overflow: hidden;
            margin-top: 4px;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(to right, var(--accent-blue), var(--accent-cyan));
            border-radius: 2px;
            transition: width 0.3s ease;
        }

        /* ========== Charts Grid ========== */
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 16px;
            padding: 0 20px;
        }

        .chart-card {
            background-color: var(--dark-panel);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            padding: 20px;
            transition: all 0.2s ease;
        }

        .chart-card:hover {
            background-color: var(--dark-hover);
            border-color: var(--accent-blue);
        }

        .chart-title {
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 16px;
            color: var(--text-primary);
        }

        .chart-container {
            position: relative;
            height: 250px;
        }

        /* ========== Details Grid ========== */
        .details-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
            padding: 0 20px;
        }

        .detail-card {
            background-color: var(--dark-panel);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            padding: 20px;
            transition: all 0.2s ease;
        }

        .detail-card:hover {
            background-color: var(--dark-hover);
            border-color: var(--accent-blue);
        }

        .detail-icon {
            font-size: 28px;
            color: var(--accent-cyan);
            margin-bottom: 12px;
        }

        .detail-card h3 {
            font-size: 14px;
            margin-bottom: 8px;
            color: var(--text-primary);
        }

        .detail-card p {
            font-size: 12px;
            color: var(--text-secondary);
            line-height: 1.6;
        }

        /* ========== CTA Section ========== */
        .cta-section {
            background-color: var(--dark-panel);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            padding: 40px;
            margin: 0 20px;
            text-align: center;
        }

        .cta-section h2 {
            font-size: 28px;
            margin-bottom: 12px;
            color: var(--text-primary);
        }

        .cta-section p {
            font-size: 14px;
            color: var(--text-secondary);
            margin-bottom: 24px;
        }

        /* ========== Footer ========== */
        footer {
            background-color: var(--dark-panel);
            border-top: 1px solid var(--border-color);
            padding: 24px 0;
            margin-top: 40px;
        }

        .footer-content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 32px;
            margin-bottom: 24px;
            padding: 0 20px;
        }

        .footer-section h4 {
            color: var(--text-primary);
            margin-bottom: 12px;
            font-size: 13px;
        }

        .footer-section ul {
            list-style: none;
        }

        .footer-section ul li {
            margin-bottom: 8px;
        }

        .footer-section ul li a {
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 12px;
            transition: color 0.2s ease;
        }

        .footer-section ul li a:hover {
            color: var(--accent-blue);
        }

        .footer-bottom {
            border-top: 1px solid var(--border-color);
            padding-top: 16px;
            text-align: center;
            font-size: 12px;
            color: var(--text-secondary);
            padding: 0 20px;
        }

        /* ========== Status Bar ========== */
        .status-bar {
            background-color: var(--dark-panel);
            border-top: 1px solid var(--border-color);
            padding: 8px 20px;
            font-size: 11px;
            color: var(--text-secondary);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .status-bar-left {
            display: flex;
            gap: 24px;
        }

        .status-bar-item {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .status-indicator-small {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: var(--status-online);
        }

        /* ========== QR Code ========== */
        .qr-code-container {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: var(--dark-panel);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 12px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
            z-index: 999;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .qr-code-container:hover {
            border-color: var(--accent-blue);
            box-shadow: 0 12px 32px rgba(0, 168, 232, 0.3);
            transform: translateY(-4px);
        }

        .qr-code-container img {
            width: 140px;
            height: 140px;
            border-radius: 4px;
            display: block;
        }

        .qr-label {
            text-align: center;
            font-size: 11px;
            color: var(--text-secondary);
            margin-top: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* ========== Responsive ========== */
        @media (max-width: 768px) {
            .hero {
                grid-template-columns: 1fr;
            }

            .hero-text h1 {
                font-size: 24px;
            }

            .charts-grid {
                grid-template-columns: 1fr;
            }

            .cta-section h2 {
                font-size: 20px;
            }

            .footer-content {
                grid-template-columns: 1fr;
            }

            .qr-code-container {
                bottom: 80px;
                right: 10px;
            }
        }

        /* ========== Animations ========== */
        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }

        .fade-in {
            animation: fadeIn 0.3s ease-out;
        }
    </style>
</head>

<body>
<header>
    <div class="container header-content">
        <a href="/" class="logo">
            <i class="fas fa-monitor"></i>
            OverView
        </a>
        <div class="nav-right">
            <button class="btn">로그인</button>
            <a href="/download" class="btn btn-primary">
                <i class="fas fa-download"></i>
                다운로드
            </a>
        </div>
    </div>
</header>

<div class="tab-nav">
    <button class="tab-item active">개요</button>
    <button class="tab-item">기능</button>
    <button class="tab-item">대시보드</button>
    <button class="tab-item">상세 정보</button>
</div>

<main>
    <div class="container">
        <!-- Hero Section -->
        <section class="section">
            <div class="hero fade-in">
                <div class="hero-text">
                    <h1>가장 직관적인<br><span class="highlight">원격 제어 솔루션</span></h1>
                    <p>여러 대의 PC를 하나의 화면에서 안정적으로 관리하세요. 실시간 모니터링, 원격 제어, 파일 전송까지 모든 기능을 한 곳에서.</p>
                    <div class="hero-buttons">
                        <a href="/download" class="btn btn-primary">
                            <i class="fas fa-download"></i>
                            지금 다운로드
                        </a>
                        <button class="btn">
                            <i class="fas fa-play"></i>
                            데모 보기
                        </button>
                    </div>
                </div>
                <div class="hero-image">
                    <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'%3E%3Crect fill='%231A1F2E' width='400' height='300'/%3E%3Crect x='20' y='20' width='360' height='260' rx='4' fill='%23252D3D' stroke='%2300A8E8' stroke-width='2'/%3E%3Crect x='40' y='40' width='320' height='40' rx='2' fill='%2300A8E8' opacity='0.2'/%3E%3Ccircle cx='60' cy='60' r='3' fill='%2300A8E8'/%3E%3Ccircle cx='80' cy='60' r='3' fill='%2300A8E8'/%3E%3Ccircle cx='100' cy='60' r='3' fill='%2300A8E8'/%3E%3Crect x='40' y='100' width='100' height='80' rx='2' fill='%2300A8E8' opacity='0.15'/%3E%3Crect x='160' y='100' width='100' height='80' rx='2' fill='%2300D9FF' opacity='0.15'/%3E%3Crect x='280' y='100' width='80' height='80' rx='2' fill='%2300A8E8' opacity='0.1'/%3E%3C/svg%3E" alt="Dashboard Preview">
                </div>
            </div>
        </section>

        <!-- Features Section -->
        <section class="section">
            <h2 class="section-title">강력한 기능들</h2>
            <div class="features-grid">
                <div class="feature-card fade-in">
                    <div class="feature-icon"><i class="fas fa-desktop"></i></div>
                    <h3>실시간 화면 공유</h3>
                    <p>다중 PC 화면을 동시에 모니터링하고 관리하세요</p>
                </div>
                <div class="feature-card fade-in">
                    <div class="feature-icon"><i class="fas fa-bolt"></i></div>
                    <h3>원격 제어</h3>
                    <p>지연 없는 키보드와 마우스 입력으로 즉시 제어</p>
                </div>
                <div class="feature-card fade-in">
                    <div class="feature-icon"><i class="fas fa-folder"></i></div>
                    <h3>파일 전송</h3>
                    <p>단일·다중 PC에 파일을 빠르게 배포</p>
                </div>
            </div>
        </section>

        <!-- Dashboard Section -->
        <section class="section">
            <div class="dashboard-header">
                <h2 class="section-title" style="margin: 0;">인터랙티브 대시보드</h2>
            </div>

            <!-- System Status Cards -->
            <div class="status-grid">
                {% for system in system_status %}
                <div class="status-card {% if system.status == 'offline' %}offline{% endif %} fade-in">
                    <div class="status-header">
                        <span class="status-name">{{ system.name }}</span>
                        <div class="status-indicator {% if system.status == 'offline' %}offline{% endif %}"></div>
                    </div>
                    <div class="status-item">
                        <span class="status-label">CPU</span>
                        <span class="status-value">{{ system.cpu }}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {{ system.cpu }}%"></div>
                    </div>
                    <div class="status-item">
                        <span class="status-label">메모리</span>
                        <span class="status-value">{{ system.memory }} GB</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">디스크</span>
                        <span class="status-value">{{ system.disk }} GB</span>
                    </div>
                </div>
                {% endfor %}
            </div>

            <!-- Charts -->
            <div class="charts-grid">
                <div class="chart-card fade-in">
                    <h3 class="chart-title">CPU 사용률 추이</h3>
                    <div class="chart-container">
                        <canvas id="cpuChart"></canvas>
                    </div>
                </div>
                <div class="chart-card fade-in">
                    <h3 class="chart-title">네트워크 상태</h3>
                    <div class="chart-container">
                        <canvas id="networkChart"></canvas>
                    </div>
                </div>
            </div>
        </section>

        <!-- Details Section -->
        <section class="section">
            <h2 class="section-title">상세 기능 안내</h2>
            <div class="details-grid">
                <div class="detail-card fade-in">
                    <div class="detail-icon"><i class="fas fa-desktop"></i></div>
                    <h3>다중 PC 실시간 모니터링</h3>
                    <p>여러 클라이언트 PC 화면을 하나의 관리 화면에서 동시에 확인할 수 있습니다.</p>
                </div>
                <div class="detail-card fade-in">
                    <div class="detail-icon"><i class="fas fa-bolt"></i></div>
                    <h3>즉시 원격 제어</h3>
                    <p>원하는 PC를 선택해 즉시 원격 제어할 수 있으며, 실제 로컬 환경과 유사한 조작감을 제공합니다.</p>
                </div>
                <div class="detail-card fade-in">
                    <div class="detail-icon"><i class="fas fa-lock"></i></div>
                    <h3>제어권 충돌 방지</h3>
                    <p>동시에 여러 관리자가 접속하더라도, 단일 사용자만 제어권을 가질 수 있도록 설계되어 입력 충돌을 방지합니다.</p>
                </div>
                <div class="detail-card fade-in">
                    <div class="detail-icon"><i class="fas fa-keyboard"></i></div>
                    <h3>고급 키보드 입력 처리</h3>
                    <p>한/영 전환, 한자키, 반복 입력 등 실제 키보드 입력과 최대한 동일한 동작을 지원합니다.</p>
                </div>
            </div>
        </section>

        <!-- CTA Section -->
        <section class="section">
            <div class="cta-section fade-in">
                <h2>지금 OverView를 시작하세요</h2>
                <p>무료로 다운로드하고 원격 관리의 새로운 경험을 해보세요</p>
                <a href="/download" class="btn btn-primary">
                    <i class="fas fa-download"></i>
                    지금 다운로드
                </a>
            </div>
        </section>
    </div>
</main>

<footer>
    <div class="container">
        <div class="footer-content">
            <div class="footer-section">
                <h4>OverView</h4>
                <p style="font-size: 12px; color: var(--text-secondary);">원격 관리의 미래를 만들어갑니다</p>
            </div>
            <div class="footer-section">
                <h4>제품</h4>
                <ul>
                    <li><a href="#">기능</a></li>
                    <li><a href="#">가격</a></li>
                    <li><a href="#">다운로드</a></li>
                </ul>
            </div>
            <div class="footer-section">
                <h4>지원</h4>
                <ul>
                    <li><a href="#">문서</a></li>
                    <li><a href="#">FAQ</a></li>
                    <li><a href="#">연락처</a></li>
                </ul>
            </div>
            <div class="footer-section">
                <h4>법률</h4>
                <ul>
                    <li><a href="#">개인정보</a></li>
                    <li><a href="#">이용약관</a></li>
                    <li><a href="#">라이선스</a></li>
                </ul>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; 2026 OverView. All Rights Reserved.</p>
        </div>
    </div>
</footer>

<div class="status-bar">
    <div class="status-bar-left">
        <div class="status-bar-item">
            <div class="status-indicator-small"></div>
            SYSTEM READY | ACTIVE 1
        </div>
        <div class="status-bar-item">
            CONTROL IP: 192.168.1.100
        </div>
    </div>
    <div class="status-bar-item">
        {{ current_time }}
    </div>
</div>

<!-- QR Code -->
<div class="qr-code-container">
    <img src="/qr-code" alt="QR Code">
    <div class="qr-label">@AHCONSULT</div>
</div>

<script>
    // Tab navigation
    document.querySelectorAll('.tab-item').forEach((tab, index) => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('.tab-item').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });

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
                    grid: { display: false },
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
                data: [85.6, 18.2],
                backgroundColor: [
                    'rgba(0, 168, 232, 0.8)',
                    'rgba(0, 217, 255, 0.8)'
                ],
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
    return redirect(DOWNLOAD_URL + f"?v={int(time.time())}", code=302)

@app.route("/api/dashboard")
def api_dashboard():
    """대시보드 데이터 API"""
    return jsonify({
        "cpu_data": generate_cpu_data(),
        "system_status": get_system_status(),
        "timestamp": datetime.now().isoformat()
    })

@app.route("/qr-code")
def qr_code():
    """QR 코드 이미지 제공"""
    qr_path = os.path.join(os.path.dirname(__file__), 'qr_code.png')
    if os.path.exists(qr_path):
        return send_file(qr_path, mimetype='image/png')
    else:
        return redirect('https://via.placeholder.com/140')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
