"""
OverView - Firebase 기반 회원가입/승인 시스템 (수정 버전)
새로운 Firebase 데이터베이스 및 키 적용
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, auth, db
import os
import datetime
import requests
from functools import wraps
import json
import tempfile
from dotenv import load_dotenv

# 로컬 .env 파일 로드
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'overview-secret-key-2026')
CORS(app)

# 새로운 Firebase 설정
FIREBASE_URL = os.environ.get('FIREBASE_URL', 'https://login-ab1f2-default-rtdb.firebaseio.com/')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', "8087683880:AAEHaQeumeYcVIKf7r4F7AFgsoCsDzBuuiA")
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID', "6681290555")
FIREBASE_WEB_API_KEY = os.environ.get('FIREBASE_WEB_API_KEY')

# Firebase 초기화
if not firebase_admin._apps:
    service_account_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
    if service_account_json:
        try:
            if service_account_json.startswith('{'):
                # JSON 파싱 후 private_key의 줄바꿈 문자 처리
                key_dict = json.loads(service_account_json)
                if 'private_key' in key_dict:
                    key_dict['private_key'] = key_dict['private_key'].replace('\\n', '\n')
                
                cred = credentials.Certificate(key_dict)
                firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})
            else:
                cred = credentials.Certificate(service_account_json)
                firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})
        except Exception as e:
            print(f"Firebase Init Error: {e}")
    else:
        # 새로운 키 파일 이름 적용
        SERVICE_ACCOUNT_FILE = "firebase_key.json"
        if os.path.exists(SERVICE_ACCOUNT_FILE):
            cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
            firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})

# ============================================
# 유틸리티 함수
# ============================================

def verify_with_firebase_auth(email, password):
    # 이메일 형식 통일 (@admin.com)
    if "@" not in email:
        email = f"{email}@admin.com"
    elif not email.endswith("@admin.com"):
        username = email.split("@")[0]
        email = f"{username}@admin.com"

    if not FIREBASE_WEB_API_KEY:
        try:
            user = auth.get_user_by_email(email)
            return True, {"localId": user.uid, "displayName": user.display_name or email.split('@')[0]}
        except:
            return False, "API Key missing and user not found"

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    response = requests.post(url, json=payload)
    res_data = response.json()
    
    if response.status_code == 200:
        return True, res_data
    else:
        return False, res_data.get('error', {}).get('message', 'Login failed')

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
    return render_template('download.html')

# ============================================
# API 엔드포인트
# ============================================

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.json
    username, password, name = data.get('email'), data.get('password'), data.get('name')
    
    # 이메일 형식 강제 변환
    if "@" in username:
        username = username.split("@")[0]
    email = f"{username}@admin.com"
    
    try:
        user = auth.create_user(email=email, password=password, display_name=name)
        db.reference(f'users/{user.uid}').set({
            'username': username,
            'email': email,
            'name': name,
            'password_plain': password,
            'status': 'pending',
            'allowed_ip': 'any',
            'expire_date': '2026-12-31',
            'created_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'max_sessions_per_pc_default': 2
        })
        return jsonify({"success": True, "message": "가입 완료 (승인 대기 중)"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    email, password = data.get('email'), data.get('password')
    
    success, result = verify_with_firebase_auth(email, password)
    
    if not success:
        return jsonify({"success": False, "message": "이메일 또는 비밀번호가 올바르지 않습니다."}), 401
        
    uid = result.get('localId')
    
    # 사용자 상태 확인 (active 여부)
    user_data = db.reference(f'users/{uid}').get()
    if not user_data or user_data.get('status') != 'active':
        return jsonify({"success": False, "message": "승인되지 않았거나 비활성화된 계정입니다."}), 403

    display_name = user_data.get('name') or result.get('displayName') or email.split('@')[0]

    session['user'] = {'uid': uid, 'email': email, 'name': display_name}
    return jsonify({"success": True})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user', None)
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
