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

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config["SECRET_KEY"] = "supersecretkey_final_version"

# QR Code Base64 (프로그램 실행 후 Base64로 변환)
QR_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAZQAAAG+CAYAAAC08vLwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAP+lSURBVHhezP0HnxxF0u4N8+nOvbt4eS/hvd9lFxa3wHrWW5A0kmbkhZB3IOGNQIDw3iMJ2fEz3T3dM/Fc/4iM7pqR2Puc89zv+3tyJrqysrLSREbGFZmVlXWe/f/bTfzvUHj4HXeacMozp4n0Ey+u5+3h8izj5LUMi3Bc5zep4s4RPCXGJFeN3sk184qQzL0TWnU6o/7Og7jWKjS5xFCkkrU/11/GnfpXDeukUCmZl6F9+9lUnHvb4fqptF38kh6lH9MlkTXkb5bwya4au6mTcaUVacjR3t7mkTI00c5r3Fq6VpUBj44HP+koALLxVvHn/dzVUl4N+ShfKVte59hOtcQV8Rv5lUyKK7covaA8n9BJ5NdxpNAUT5rKu6Uj6SpmXMRxTyEbj/KTP2Xk2InLMQkeJZ/KIekc"

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
            position: relative;
            overflow: hidden;
        }

        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s ease;
        }

        .btn:hover::before {
            left: 100%;
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
            opacity: 0;
            animation: slideInUp 0.6s ease-out forwards;
        }

        .section:nth-child(1) { animation-delay: 0s; }
        .section:nth-child(2) { animation-delay: 0.1s; }
        .section:nth-child(3) { animation-delay: 0.2s; }
        .section:nth-child(4) { animation-delay: 0.3s; }

        @keyframes slideInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
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
            transition: all 0.3s ease;
            animation: slideInUp 0.8s ease-out;
        }

        .hero:hover {
            border-color: var(--accent-blue);
            box-shadow: 0 0 20px rgba(0, 168, 232, 0.1);
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
            animation: float 3s ease-in-out infinite;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }

        @keyframes glow {
            0%, 100% { box-shadow: 0 0 20px rgba(0, 168, 232, 0.3); }
            50% { box-shadow: 0 0 40px rgba(0, 217, 255, 0.6); }
        }

        @keyframes shimmer {
            0% { background-position: -1000px 0; }
            100% { background-position: 1000px 0; }
        }

        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-50px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(50px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        @keyframes bounceIn {
            0% {
                opacity: 0;
                transform: scale(0.3);
            }
            50% {
                opacity: 1;
                transform: scale(1.05);
            }
            70% {
                transform: scale(0.9);
            }
            100% {
                transform: scale(1);
            }
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

        @keyframes rotateIn {
            from {
                opacity: 0;
                transform: rotate(-10deg) scale(0.9);
            }
            to {
                opacity: 1;
                transform: rotate(0) scale(1);
            }
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
            transition: all 0.3s ease;
            cursor: pointer;
            animation: bounceIn 0.6s ease-out forwards;
        }

        .feature-card:nth-child(1) { animation-delay: 0.1s; }
        .feature-card:nth-child(2) { animation-delay: 0.2s; }
        .feature-card:nth-child(3) { animation-delay: 0.3s; }

        .feature-card:hover {
            background-color: var(--dark-hover);
            border-color: var(--accent-blue);
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 168, 232, 0.2);
        }

        .feature-icon {
            font-size: 28px;
            color: var(--accent-blue);
            margin-bottom: 12px;
            transition: all 0.3s ease;
            animation: rotateIn 0.6s ease-out;
        }

        .feature-card:hover .feature-icon {
            color: var(--accent-cyan);
            transform: scale(1.2) rotate(10deg);
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
            transition: all 0.3s ease;
            animation: fadeInUp 0.6s ease-out forwards;
        }

        .status-card:nth-child(1) { animation-delay: 0.1s; }
        .status-card:nth-child(2) { animation-delay: 0.2s; }
        .status-card:nth-child(3) { animation-delay: 0.3s; }
        .status-card:nth-child(4) { animation-delay: 0.4s; }

        .status-card:hover {
            background-color: var(--dark-hover);
            border-color: var(--accent-blue);
            transform: translateY(-3px);
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
            animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .status-indicator.offline {
            background-color: var(--status-offline);
            animation: none;
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
            transition: all 0.3s ease;
            animation: slideInUp 0.7s ease-out;
        }

        .chart-card:hover {
            background-color: var(--dark-hover);
            border-color: var(--accent-blue);
            box-shadow: 0 10px 30px rgba(0, 168, 232, 0.1);
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

        /* ========== Demo Section ========== */
        .demo-section {
            background-color: var(--dark-panel);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            padding: 30px;
            margin: 0 20px;
        }

        .demo-title {
            font-size: 20px;
            font-weight: 500;
            margin-bottom: 24px;
            color: var(--text-primary);
        }

        .demo-steps {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }

        .demo-step {
            background-color: var(--dark-hover);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            padding: 20px;
            transition: all 0.3s ease;
            position: relative;
            padding-left: 50px;
            animation: fadeInUp 0.6s ease-out forwards;
        }

        .demo-step:nth-child(1) { animation-delay: 0.1s; }
        .demo-step:nth-child(2) { animation-delay: 0.2s; }
        .demo-step:nth-child(3) { animation-delay: 0.3s; }
        .demo-step:nth-child(4) { animation-delay: 0.4s; }
        .demo-step:nth-child(5) { animation-delay: 0.5s; }
        .demo-step:nth-child(6) { animation-delay: 0.6s; }

        .demo-step:hover {
            border-color: var(--accent-blue);
            transform: translateX(5px);
        }

        .demo-step-number {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            width: 30px;
            height: 30px;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan));
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            color: var(--dark-bg);
            font-size: 14px;
        }

        .demo-step h4 {
            font-size: 15px;
            margin-bottom: 8px;
            color: var(--text-primary);
        }

        .demo-step p {
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.6;
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
            transition: all 0.3s ease;
            animation: rotateIn 0.6s ease-out forwards;
        }

        .detail-card:nth-child(1) { animation-delay: 0.1s; }
        .detail-card:nth-child(2) { animation-delay: 0.2s; }
        .detail-card:nth-child(3) { animation-delay: 0.3s; }
        .detail-card:nth-child(4) { animation-delay: 0.4s; }

        .detail-card:hover {
            background-color: var(--dark-hover);
            border-color: var(--accent-blue);
            transform: translateY(-5px);
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
            animation: pulse 2s ease-in-out infinite;
        }

        /* ========== QR Code ========== */
        .qr-code-container {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: var(--dark-panel);
            border: 2px solid var(--accent-blue);
            border-radius: 8px;
            padding: 12px;
            box-shadow: 0 8px 24px rgba(0, 168, 232, 0.4);
            z-index: 9999;
            transition: all 0.3s ease;
            cursor: pointer;
            animation: slideInRight 0.8s ease-out, glow 2s ease-in-out infinite;
            animation-delay: 0s, 0.8s;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        .qr-code-container:hover {
            border-color: var(--accent-blue);
            box-shadow: 0 12px 32px rgba(0, 168, 232, 0.3);
            transform: translateY(-4px);
        }

        .qr-code-container img {
            width: 150px;
            height: 150px;
            border-radius: 4px;
            display: block;
            background-color: white;
            padding: 2px;
        }

        .qr-label {
            text-align: center;
            font-size: 11px;
            color: var(--text-secondary);
            margin-top: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* ========== Modal ========== */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.8);
            animation: fadeIn 0.3s ease;
        }

        .modal-content {
            background-color: var(--dark-panel);
            margin: 5% auto;
            padding: 30px;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            width: 90%;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
            animation: slideDown 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes slideDown {
            from { transform: translateY(-50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        .close {
            color: var(--text-secondary);
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            transition: color 0.2s ease;
        }

        .close:hover {
            color: var(--accent-blue);
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
                bottom: 20px;
                right: 10px;
                width: auto;
            }

            .demo-steps {
                grid-template-columns: 1fr;
            }
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
            <div class="hero">
                <div class="hero-text">
                    <h1>가장 직관적인<br><span class="highlight">원격 제어 솔루션</span></h1>
                    <p>여러 대의 PC를 하나의 화면에서 안정적으로 관리하세요. 실시간 모니터링, 원격 제어, 파일 전송까지 모든 기능을 한 곳에서.</p>
                    <div class="hero-buttons">
                        <a href="/download" class="btn btn-primary">
                            <i class="fas fa-download"></i>
                            지금 다운로드
                        </a>
                        <button class="btn" onclick="openDemo()">
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
            </div>
        </section>

        <!-- Demo Section -->
        <section class="section">
            <div class="demo-section">
                <h3 class="demo-title">📚 프로그램 사용 방법</h3>
                <div class="demo-steps">
                    <div class="demo-step">
                        <div class="demo-step-number">1</div>
                        <h4>프로그램 다운로드</h4>
                        <p>OverView 설치 파일을 다운로드하고 실행합니다. Windows 10 이상에서 지원됩니다.</p>
                    </div>
                    <div class="demo-step">
                        <div class="demo-step-number">2</div>
                        <h4>계정 생성 및 로그인</h4>
                        <p>프로그램을 실행하면 로그인 화면이 나타납니다. 계정을 생성하고 로그인하세요.</p>
                    </div>
                    <div class="demo-step">
                        <div class="demo-step-number">3</div>
                        <h4>PC 연결</h4>
                        <p>관리할 PC들을 프로그램에 추가합니다. 각 PC에 클라이언트를 설치하면 자동으로 연결됩니다.</p>
                    </div>
                    <div class="demo-step">
                        <div class="demo-step-number">4</div>
                        <h4>화면 모니터링</h4>
                        <p>메인 화면에서 모든 연결된 PC의 화면을 실시간으로 확인할 수 있습니다.</p>
                    </div>
                    <div class="demo-step">
                        <div class="demo-step-number">5</div>
                        <h4>원격 제어</h4>
                        <p>원하는 PC를 선택하면 마우스와 키보드로 원격 제어가 가능합니다. 마치 직접 조작하는 것처럼!</p>
                    </div>
                    <div class="demo-step">
                        <div class="demo-step-number">6</div>
                        <h4>파일 전송</h4>
                        <p>드래그 앤 드롭으로 파일을 여러 PC에 동시에 전송할 수 있습니다. 효율적인 파일 관리!</p>
                    </div>
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
                <div class="status-card {% if system.status == 'offline' %}offline{% endif %}">
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
        </section>

        <!-- Details Section -->
        <section class="section">
            <h2 class="section-title">상세 기능 안내</h2>
            <div class="details-grid">
                <div class="detail-card">
                    <div class="detail-icon"><i class="fas fa-desktop"></i></div>
                    <h3>다중 PC 실시간 모니터링</h3>
                    <p>여러 클라이언트 PC 화면을 하나의 관리 화면에서 동시에 확인할 수 있습니다.</p>
                </div>
                <div class="detail-card">
                    <div class="detail-icon"><i class="fas fa-bolt"></i></div>
                    <h3>즉시 원격 제어</h3>
                    <p>원하는 PC를 선택해 즉시 원격 제어할 수 있으며, 실제 로컬 환경과 유사한 조작감을 제공합니다.</p>
                </div>
                <div class="detail-card">
                    <div class="detail-icon"><i class="fas fa-lock"></i></div>
                    <h3>제어권 충돌 방지</h3>
                    <p>동시에 여러 관리자가 접속하더라도, 단일 사용자만 제어권을 가질 수 있도록 설계되어 입력 충돌을 방지합니다.</p>
                </div>
                <div class="detail-card">
                    <div class="detail-icon"><i class="fas fa-keyboard"></i></div>
                    <h3>고급 키보드 입력 처리</h3>
                    <p>한/영 전환, 한자키, 반복 입력 등 실제 키보드 입력과 최대한 동일한 동작을 지원합니다.</p>
                </div>
            </div>
        </section>

        <!-- CTA Section -->
        <section class="section">
            <div class="cta-section">
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
    <img src="/static/qr.png" alt="QR Code">
    <div class="qr-label">@AHCONSULT</div>
</div>

<!-- Demo Modal -->
<div id="demoModal" class="modal">
    <div class="modal-content">
        <span class="close" onclick="closeDemo()">&times;</span>
        <h2 style="margin-bottom: 20px; color: var(--accent-blue);">📚 프로그램 사용 방법</h2>
        <div class="demo-steps" style="grid-template-columns: 1fr;">
            <div class="demo-step">
                <div class="demo-step-number">1</div>
                <h4>프로그램 다운로드</h4>
                <p>OverView 설치 파일을 다운로드하고 실행합니다. Windows 10 이상에서 지원됩니다.</p>
            </div>
            <div class="demo-step">
                <div class="demo-step-number">2</div>
                <h4>계정 생성 및 로그인</h4>
                <p>프로그램을 실행하면 로그인 화면이 나타납니다. 계정을 생성하고 로그인하세요.</p>
            </div>
            <div class="demo-step">
                <div class="demo-step-number">3</div>
                <h4>PC 연결</h4>
                <p>관리할 PC들을 프로그램에 추가합니다. 각 PC에 클라이언트를 설치하면 자동으로 연결됩니다.</p>
            </div>
            <div class="demo-step">
                <div class="demo-step-number">4</div>
                <h4>화면 모니터링</h4>
                <p>메인 화면에서 모든 연결된 PC의 화면을 실시간으로 확인할 수 있습니다.</p>
            </div>
            <div class="demo-step">
                <div class="demo-step-number">5</div>
                <h4>원격 제어</h4>
                <p>원하는 PC를 선택하면 마우스와 키보드로 원격 제어가 가능합니다. 마치 직접 조작하는 것처럼!</p>
            </div>
            <div class="demo-step">
                <div class="demo-step-number">6</div>
                <h4>파일 전송</h4>
                <p>드래그 앤 드롭으로 파일을 여러 PC에 동시에 전송할 수 있습니다. 효율적인 파일 관리!</p>
            </div>
        </div>
    </div>
</div>

<script>
    // Tab navigation
    document.querySelectorAll('.tab-item').forEach((tab, index) => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('.tab-item').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
