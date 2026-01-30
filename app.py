"""
OverView - Firebase 기반 회원가입/승인 시스템
Flask 웹 애플리케이션 (디자인 개편 및 로직 최적화 버전)
"""

from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, auth, db
import os
import datetime
import requests
import hashlib
from functools import wraps
import json
import tempfile

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'overview-secret-key-2026')
CORS(app)

# Firebase 설정
FIREBASE_URL = os.environ.get('FIREBASE_URL', 'https://main-d9759-default-rtdb.firebaseio.com/')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', "8087683880:AAEHaQeumeYcVIKf7r4F7AFgsoCsDzBuuiA")
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID', "6681290555")

# Firebase 초기화
if not firebase_admin._apps:
    service_account_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
    
    if service_account_json:
        # 환경 변수에서 JSON 데이터를 읽어 임시 파일 생성
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
                temp_file.write(service_account_json)
                temp_file_path = temp_file.name
            
            cred = credentials.Certificate(temp_file_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': FIREBASE_URL
            })
            
            # 프로젝트 ID 추출
            firebase_config = json.loads(service_account_json)
            FIREBASE_PROJECT_ID = firebase_config.get('project_id')
            
            # 임시 파일 삭제
            os.unlink(temp_file_path)
        except Exception as e:
            print(f"Firebase initialization error: {e}")
            FIREBASE_PROJECT_ID = None
    else:
        # 로컬 파일 시도 (serviceAccountKey.json)
        SERVICE_ACCOUNT_FILE = "serviceAccountKey.json"
        if os.path.exists(SERVICE_ACCOUNT_FILE):
            cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
            firebase_admin.initialize_app(cred, {
                'databaseURL': FIREBASE_URL
            })
            with open(SERVICE_ACCOUNT_FILE, 'r') as f:
                firebase_config = json.load(f)
                FIREBASE_PROJECT_ID = firebase_config.get('project_id')
        else:
            print("Warning: No Firebase credentials found.")
            FIREBASE_PROJECT_ID = None

# ============================================
# 유틸리티 함수
# ============================================

def send_telegram_notification(message):
    """관리자에게 텔레그램 알림 전송"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": ADMIN_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram error: {e}")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================
# 라우트 설정
# ============================================

@app.route('/')
def index():
    return render_template('index.html', user=session.get('user'))

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    if 'user' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/download')
@login_required
def download():
    user_id = session['user']['uid']
    user_ref = db.reference(f'users/{user_id}')
    user_data = user_ref.get()
    
    if user_data and user_data.get('status') == 'approved':
        return render_template('download.html')
    else:
        return render_template('login.html', error="관리자의 승인이 필요합니다.")

# ============================================
# API 엔드포인트
# ============================================

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    
    if not email or not password:
        return jsonify({"success": False, "message": "이메일과 비밀번호를 입력해주세요."}), 400
        
    try:
        # Firebase Auth 사용자 생성
        user = auth.create_user(
            email=email,
            password=password,
            display_name=name
        )
        
        # DB에 사용자 정보 저장 (대기 상태)
        db.reference(f'users/{user.uid}').set({
            'email': email,
            'name': name,
            'status': 'pending',
            'created_at': datetime.datetime.now().isoformat()
        })
        
        # 텔레그램 알림 전송
        notification = f"🔔 <b>신규 가입 신청</b>\n\n이름: {name}\n이메일: {email}\n상태: 승인 대기 중"
        send_telegram_notification(notification)
        
        return jsonify({"success": True, "message": "가입 신청이 완료되었습니다. 관리자 승인 후 이용 가능합니다."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    # 이 앱은 보안상 Firebase Auth 클라이언트 SDK를 통해 로그인하는 것이 권장되지만,
    # 현재 서버 로직에서는 DB의 상태를 확인하는 용도로 사용합니다.
    # (실제 프로덕션에서는 Firebase Auth ID Token을 검증하는 방식이 좋습니다.)
    
    try:
        # 이메일로 사용자 조회
        user = auth.get_user_by_email(email)
        user_data = db.reference(f'users/{user.uid}').get()
        
        if not user_data:
            return jsonify({"success": False, "message": "등록되지 않은 사용자입니다."}), 404
            
        if user_data.get('status') != 'approved':
            return jsonify({"success": False, "message": "관리자의 승인이 대기 중입니다."}), 403
            
        # 세션 저장
        session['user'] = {
            'uid': user.uid,
            'email': email,
            'name': user_data.get('name')
        }
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": "로그인 정보가 올바르지 않거나 승인되지 않았습니다."}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user', None)
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
