import os
import time
import json
from flask import Flask, render_template_string, redirect, jsonify, request
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
# 웹사이트 HTML (Glassmorphism + Zen Blue)
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
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Noto+Sans+KR:wght@400;500;700&display=swap');

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary-blue: #0057FF;
            --cyan-accent: #00D1FF;
            --bg-light: #FFFFFF;
            --bg-soft: #F8FAFC;
            --text-dark: #1F2937;
            --text-muted: #6B7280;
            --border-light: #E5E7EB;
            --glass-bg: rgba(255, 255, 255, 0.7);
            --glass-border: rgba(255, 255, 255, 0.2);
            --glass-blur: 10px;
        }

        body {
            font-family: 'Noto Sans KR', 'Poppins', sans-serif;
            background: linear-gradient(to bottom, #FFFFFF, rgba(219, 234, 254, 0.3), #FFFFFF);
            color: var(--text-dark);
            line-height: 1.6;
            min-height: 100vh;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Poppins', 'Noto Sans KR', sans-serif;
            font-weight: 700;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        /* ========== Navigation ========== */
        header {
            position: fixed;
            top: 0;
            width: 100%;
            z-index: 100;
            backdrop-filter: blur(10px);
            background: rgba(255, 255, 255, 0.7);
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
        }

        header.scrolled {
            background: rgba(255, 255, 255, 0.9);
            box-shadow: 0 8px 32px rgba(0, 87, 255, 0.08);
        }

        .navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            height: 70px;
        }

        .logo {
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(to right, var(--primary-blue), var(--cyan-accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .logo i {
            width: 32px;
            height: 32px;
            background: linear-gradient(135deg, var(--primary-blue), var(--cyan-accent));
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            -webkit-background-clip: unset;
            -webkit-text-fill-color: unset;
            background-clip: unset;
        }

        .nav-menu {
            display: flex;
            list-style: none;
            gap: 32px;
        }

        .nav-menu a {
            color: var(--text-dark);
            text-decoration: none;
            font-size: 14px;
            transition: color 0.3s ease;
        }

        .nav-menu a:hover {
            color: var(--primary-blue);
        }

        .nav-buttons {
            display: flex;
            gap: 12px;
        }

        .btn {
            padding: 10px 24px;
            border-radius: 8px;
            border: none;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .btn-primary {
            background: linear-gradient(to right, var(--primary-blue), var(--cyan-accent));
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 24px rgba(0, 87, 255, 0.3);
        }

        .btn-secondary {
            background: transparent;
            color: var(--primary-blue);
            border: 1px solid rgba(0, 87, 255, 0.2);
        }

        .btn-secondary:hover {
            background: rgba(0, 87, 255, 0.05);
        }

        .mobile-menu-btn {
            display: none;
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: var(--text-dark);
        }

        /* ========== Hero Section ========== */
        #hero {
            padding-top: 120px;
            padding-bottom: 80px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            position: relative;
            overflow: hidden;
        }

        .hero-bg {
            position: absolute;
            top: 0;
            right: 0;
            width: 500px;
            height: 500px;
            background: radial-gradient(circle, rgba(0, 209, 255, 0.15), transparent);
            border-radius: 50%;
            filter: blur(60px);
            z-index: -1;
        }

        .hero-bg-2 {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 500px;
            height: 500px;
            background: radial-gradient(circle, rgba(0, 87, 255, 0.15), transparent);
            border-radius: 50%;
            filter: blur(60px);
            z-index: -1;
        }

        .hero-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 60px;
            align-items: center;
        }

        .hero-text h1 {
            font-size: 56px;
            line-height: 1.2;
            margin-bottom: 24px;
            color: var(--text-dark);
        }

        .hero-text h1 .gradient {
            background: linear-gradient(to right, var(--primary-blue), var(--cyan-accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .hero-text p {
            font-size: 18px;
            color: var(--text-muted);
            margin-bottom: 32px;
            line-height: 1.8;
        }

        .hero-buttons {
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
        }

        .hero-image {
            position: relative;
            animation: float 3s ease-in-out infinite;
        }

        .hero-image-glass {
            background: rgba(255, 255, 255, 0.6);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(0, 87, 255, 0.1);
            border-radius: 20px;
            padding: 8px;
            box-shadow: 0 20px 48px rgba(0, 87, 255, 0.12);
        }

        .hero-image-glass img {
            width: 100%;
            height: auto;
            border-radius: 16px;
            display: block;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }

        /* ========== Features Section ========== */
        #features {
            padding: 100px 0;
            background: linear-gradient(to bottom, transparent, rgba(219, 234, 254, 0.2), transparent);
        }

        .section-title {
            font-size: 48px;
            text-align: center;
            margin-bottom: 16px;
            color: var(--text-dark);
        }

        .section-subtitle {
            text-align: center;
            color: var(--text-muted);
            font-size: 18px;
            max-width: 600px;
            margin: 0 auto 60px;
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 32px;
        }

        .feature-card {
            background: var(--glass-bg);
            backdrop-filter: blur(10px);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 32px;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .feature-card:hover {
            background: rgba(255, 255, 255, 0.8);
            box-shadow: 0 8px 32px rgba(0, 87, 255, 0.08);
            border-color: rgba(0, 87, 255, 0.15);
            transform: translateY(-4px);
        }

        .feature-icon {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, var(--primary-blue), var(--cyan-accent));
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
            margin-bottom: 16px;
            transition: transform 0.3s ease;
        }

        .feature-card:hover .feature-icon {
            transform: scale(1.1);
        }

        .feature-card h3 {
            font-size: 20px;
            margin-bottom: 12px;
            color: var(--text-dark);
        }

        .feature-card p {
            color: var(--text-muted);
            font-size: 15px;
            line-height: 1.6;
        }

        /* ========== Dashboard Section ========== */
        #dashboard {
            padding: 100px 0;
        }

        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }

        .status-card {
            background: var(--glass-bg);
            backdrop-filter: blur(10px);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 20px;
            transition: all 0.3s ease;
        }

        .status-card.online:hover {
            background: rgba(255, 255, 255, 0.8);
            box-shadow: 0 8px 32px rgba(0, 87, 255, 0.08);
            border-color: rgba(0, 87, 255, 0.15);
        }

        .status-card.offline {
            opacity: 0.5;
        }

        .status-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }

        .status-name {
            font-weight: 600;
            color: var(--text-dark);
        }

        .status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #10B981;
        }

        .status-indicator.offline {
            background: #9CA3AF;
        }

        .status-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            font-size: 14px;
        }

        .status-label {
            color: var(--text-muted);
        }

        .status-value {
            font-weight: 600;
            color: var(--primary-blue);
        }

        .progress-bar {
            width: 100%;
            height: 4px;
            background: rgba(0, 87, 255, 0.1);
            border-radius: 2px;
            overflow: hidden;
            margin-top: 4px;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(to right, var(--primary-blue), var(--cyan-accent));
            border-radius: 2px;
            transition: width 0.3s ease;
        }

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 32px;
        }

        .chart-card {
            background: var(--glass-bg);
            backdrop-filter: blur(10px);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 32px;
            transition: all 0.3s ease;
        }

        .chart-card:hover {
            box-shadow: 0 8px 32px rgba(0, 87, 255, 0.08);
            border-color: rgba(0, 87, 255, 0.15);
        }

        .chart-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 24px;
            color: var(--text-dark);
        }

        .chart-container {
            position: relative;
            height: 280px;
        }

        /* ========== Details Section ========== */
        #details {
            padding: 100px 0;
            background: linear-gradient(to bottom, transparent, rgba(219, 234, 254, 0.2), transparent);
        }

        .details-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 32px;
            max-width: 1000px;
            margin: 0 auto;
        }

        .detail-card {
            background: var(--glass-bg);
            backdrop-filter: blur(10px);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 32px;
            transition: all 0.3s ease;
        }

        .detail-card:hover {
            background: rgba(255, 255, 255, 0.8);
            box-shadow: 0 8px 32px rgba(0, 87, 255, 0.08);
            border-color: rgba(0, 87, 255, 0.15);
            transform: translateY(-4px);
        }

        .detail-icon {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, var(--cyan-accent), var(--primary-blue));
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
            margin-bottom: 16px;
        }

        .detail-card h3 {
            font-size: 18px;
            margin-bottom: 12px;
            color: var(--text-dark);
        }

        .detail-card p {
            color: var(--text-muted);
            font-size: 14px;
            line-height: 1.6;
        }

        /* ========== CTA Section ========== */
        #cta {
            padding: 100px 0;
            position: relative;
            overflow: hidden;
        }

        .cta-bg {
            position: absolute;
            top: 0;
            right: 0;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, rgba(0, 87, 255, 0.2), transparent);
            border-radius: 50%;
            filter: blur(60px);
            z-index: -1;
        }

        .cta-bg-2 {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, rgba(0, 209, 255, 0.2), transparent);
            border-radius: 50%;
            filter: blur(60px);
            z-index: -1;
        }

        .cta-content {
            text-align: center;
        }

        .cta-content h2 {
            font-size: 48px;
            margin-bottom: 16px;
            color: var(--text-dark);
        }

        .cta-content p {
            font-size: 18px;
            color: var(--text-muted);
            margin-bottom: 32px;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }

        /* ========== Footer ========== */
        footer {
            background: linear-gradient(to bottom, rgba(0, 0, 0, 0.02), rgba(0, 0, 0, 0.05));
            border-top: 1px solid rgba(255, 255, 255, 0.2);
            padding: 60px 0 20px;
            color: var(--text-muted);
            font-size: 14px;
        }

        .footer-content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 40px;
            margin-bottom: 40px;
        }

        .footer-section h4 {
            color: var(--text-dark);
            margin-bottom: 16px;
            font-size: 14px;
        }

        .footer-section ul {
            list-style: none;
        }

        .footer-section ul li {
            margin-bottom: 8px;
        }

        .footer-section ul li a {
            color: var(--text-muted);
            text-decoration: none;
            transition: color 0.3s ease;
        }

        .footer-section ul li a:hover {
            color: var(--primary-blue);
        }

        .footer-bottom {
            border-top: 1px solid rgba(0, 0, 0, 0.05);
            padding-top: 20px;
            text-align: center;
        }

        /* ========== Responsive ========== */
        @media (max-width: 768px) {
            .nav-menu {
                display: none;
            }

            .nav-buttons {
                display: none;
            }

            .mobile-menu-btn {
                display: block;
            }

            .hero-content {
                grid-template-columns: 1fr;
                gap: 40px;
            }

            .hero-text h1 {
                font-size: 36px;
            }

            .hero-buttons {
                flex-direction: column;
            }

            .btn {
                width: 100%;
                justify-content: center;
            }

            .section-title {
                font-size: 32px;
            }

            .charts-grid {
                grid-template-columns: 1fr;
            }

            .cta-content h2 {
                font-size: 32px;
            }
        }

        /* ========== Animations ========== */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .fade-in-up {
            animation: fadeInUp 0.6s ease-out;
        }
    </style>
</head>

<body>
<header>
    <nav class="navbar container">
        <a href="/" class="logo">
            <i class="fas fa-monitor"></i>
            OverView
        </a>
        <ul class="nav-menu">
            <li><a href="#features">기능</a></li>
            <li><a href="#dashboard">대시보드</a></li>
            <li><a href="#details">상세 정보</a></li>
        </ul>
        <div class="nav-buttons">
            <button class="btn btn-secondary">로그인</button>
            <a href="/download" class="btn btn-primary">
                <i class="fas fa-download"></i>
                다운로드
            </a>
        </div>
        <button class="mobile-menu-btn"><i class="fas fa-bars"></i></button>
    </nav>
</header>

<main>
    <!-- Hero Section -->
    <section id="hero">
        <div class="hero-bg"></div>
        <div class="hero-bg-2"></div>
        <div class="container hero-content fade-in-up">
            <div class="hero-text">
                <h1>가장 직관적인<br><span class="gradient">원격 제어 솔루션</span></h1>
                <p>여러 대의 PC를 하나의 화면에서 안정적으로 관리하세요. 실시간 모니터링, 원격 제어, 파일 전송까지 모든 기능을 한 곳에서.</p>
                <div class="hero-buttons">
                    <a href="/download" class="btn btn-primary">
                        <i class="fas fa-download"></i>
                        지금 다운로드
                    </a>
                    <button class="btn btn-secondary">
                        <i class="fas fa-play"></i>
                        데모 보기
                    </button>
                </div>
            </div>
            <div class="hero-image">
                <div class="hero-image-glass">
                    <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'%3E%3Crect fill='%23E0F2FE' width='400' height='300'/%3E%3Crect x='20' y='20' width='360' height='260' rx='8' fill='%23FFFFFF' stroke='%230057FF' stroke-width='2'/%3E%3Crect x='40' y='40' width='320' height='40' rx='4' fill='%230057FF' opacity='0.1'/%3E%3Ccircle cx='60' cy='60' r='4' fill='%230057FF'/%3E%3Ccircle cx='80' cy='60' r='4' fill='%230057FF'/%3E%3Ccircle cx='100' cy='60' r='4' fill='%230057FF'/%3E%3Crect x='40' y='100' width='100' height='80' rx='4' fill='%230057FF' opacity='0.2'/%3E%3Crect x='160' y='100' width='100' height='80' rx='4' fill='%2300D1FF' opacity='0.2'/%3E%3Crect x='280' y='100' width='80' height='80' rx='4' fill='%230057FF' opacity='0.15'/%3E%3C/svg%3E" alt="Dashboard Preview">
                </div>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section id="features">
        <div class="container">
            <h2 class="section-title">강력한 기능들</h2>
            <p class="section-subtitle">OverView는 원격 관리에 필요한 모든 기능을 제공합니다</p>
            <div class="features-grid">
                <div class="feature-card fade-in-up">
                    <div class="feature-icon"><i class="fas fa-desktop"></i></div>
                    <h3>실시간 화면 공유</h3>
                    <p>다중 PC 화면을 동시에 모니터링하고 관리하세요</p>
                </div>
                <div class="feature-card fade-in-up" style="animation-delay: 0.1s;">
                    <div class="feature-icon"><i class="fas fa-bolt"></i></div>
                    <h3>원격 제어</h3>
                    <p>지연 없는 키보드와 마우스 입력으로 즉시 제어</p>
                </div>
                <div class="feature-card fade-in-up" style="animation-delay: 0.2s;">
                    <div class="feature-icon"><i class="fas fa-folder"></i></div>
                    <h3>파일 전송</h3>
                    <p>단일·다중 PC에 파일을 빠르게 배포</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Dashboard Section -->
    <section id="dashboard">
        <div class="container">
            <h2 class="section-title">인터랙티브 대시보드</h2>
            <p class="section-subtitle">실시간 시스템 모니터링으로 데이터를 더 직관적으로 탐색하고, 추세를 더 잘 이해하며, 간편히 저장하고 공유하세요</p>

            <!-- System Status Cards -->
            <div class="status-grid">
                {% for system in system_status %}
                <div class="status-card {% if system.status == 'online' %}online{% else %}offline{% endif %}">
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
                <div class="chart-card">
                    <h3 class="chart-title">CPU 사용률 추이</h3>
                    <div class="chart-container">
                        <canvas id="cpuChart"></canvas>
                    </div>
                </div>
                <div class="chart-card">
                    <h3 class="chart-title">네트워크 상태</h3>
                    <div class="chart-container">
                        <canvas id="networkChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Details Section -->
    <section id="details">
        <div class="container">
            <h2 class="section-title">상세 기능 안내</h2>
            <div class="details-grid">
                <div class="detail-card fade-in-up">
                    <div class="detail-icon"><i class="fas fa-desktop"></i></div>
                    <h3>다중 PC 실시간 모니터링</h3>
                    <p>여러 클라이언트 PC 화면을 하나의 관리 화면에서 동시에 확인할 수 있습니다. 각 PC는 실시간으로 갱신되며 대규모 환경에서도 효율적인 관리가 가능합니다.</p>
                </div>
                <div class="detail-card fade-in-up" style="animation-delay: 0.1s;">
                    <div class="detail-icon"><i class="fas fa-bolt"></i></div>
                    <h3>즉시 원격 제어</h3>
                    <p>원하는 PC를 선택해 즉시 원격 제어할 수 있으며, 실제 로컬 환경과 유사한 조작감을 제공합니다.</p>
                </div>
                <div class="detail-card fade-in-up" style="animation-delay: 0.2s;">
                    <div class="detail-icon"><i class="fas fa-lock"></i></div>
                    <h3>제어권 충돌 방지</h3>
                    <p>동시에 여러 관리자가 접속하더라도, 단일 사용자만 제어권을 가질 수 있도록 설계되어 입력 충돌을 방지합니다.</p>
                </div>
                <div class="detail-card fade-in-up" style="animation-delay: 0.3s;">
                    <div class="detail-icon"><i class="fas fa-keyboard"></i></div>
                    <h3>고급 키보드 입력 처리</h3>
                    <p>한/영 전환, 한자키, 반복 입력 등 실제 키보드 입력과 최대한 동일한 동작을 지원합니다.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- CTA Section -->
    <section id="cta">
        <div class="cta-bg"></div>
        <div class="cta-bg-2"></div>
        <div class="container cta-content">
            <h2>지금 OverView를 시작하세요</h2>
            <p>무료로 다운로드하고 원격 관리의 새로운 경험을 해보세요</p>
            <a href="/download" class="btn btn-primary" style="margin: 0 auto;">
                <i class="fas fa-download"></i>
                지금 다운로드
            </a>
        </div>
    </section>
</main>

<footer>
    <div class="container">
        <div class="footer-content">
            <div class="footer-section">
                <h4>OverView</h4>
                <p>원격 관리의 미래를 만들어갑니다</p>
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

<script>
    // Header scroll effect
    window.addEventListener('scroll', function() {
        const header = document.querySelector('header');
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
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
                borderColor: '#0057FF',
                backgroundColor: 'rgba(0, 87, 255, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: '#0057FF',
                pointBorderColor: '#FFFFFF',
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
                    grid: { color: 'rgba(0, 0, 0, 0.05)' },
                    ticks: { color: '#6B7280' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#6B7280' }
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
                    'rgba(0, 87, 255, 0.8)',
                    'rgba(0, 209, 255, 0.8)'
                ],
                borderRadius: 8,
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
                    grid: { color: 'rgba(0, 0, 0, 0.05)' },
                    ticks: { color: '#6B7280' }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: '#6B7280' }
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
    return render_template_string(HTML_TEMPLATE, cpu_data=cpu_data, system_status=system_status)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
