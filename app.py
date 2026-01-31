"""
OverView - Firebase 기반 회원가입/승인 시스템 (v3 - 개별 환경변수 방식)
Render 환경 변수 PEM Padding 문제 완전 해결 버전
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

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'overview-secret-key-2026')
CORS(app)

# 설정값
FIREBASE_URL = os.environ.get('FIREBASE_URL', 'https://login-ab1f2-default-rtdb.firebaseio.com/')
FIREBASE_WEB_API_KEY = os.environ.get('FIREBASE_WEB_API_KEY')

# Firebase 초기화 (개별 환경변수 방식)
if not firebase_admin._apps:
    try:
        # 개별 환경변수에서 읽기
        project_id = os.environ.get('FB_PROJECT_ID')
        client_email = os.environ.get('FB_CLIENT_EMAIL')
        private_key = os.environ.get('FB_PRIVATE_KEY')
        
        if project_id and client_email and private_key:
            # private_key 내의 실제 줄바꿈 처리 및 불필요한 따옴표 제거
            formatted_key = private_key.replace('\\n', '\n').strip().strip('"').strip("'")
            
            # 인증 객체 생성
            cred_dict = {
                "type": "service_account",
                "project_id": project_id,
                "client_email": client_email,
                "private_key": formatted_key,
                "token_uri": "https://oauth2.googleapis.com/token",
            }
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})
            print("Firebase Initialized successfully with individual env vars")
        else:
            # 로컬 파일 fallback
            SERVICE_ACCOUNT_FILE = "firebase_key.json"
            if os.path.exists(SERVICE_ACCOUNT_FILE):
                cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
                firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})
                print("Firebase Initialized via local file")
            else:
                print("Firebase Error: Missing environment variables or key file")
    except Exception as e:
        print(f"Firebase Init Error: {e}")

# ============================================
# 유틸리티 함수
# ============================================

def verify_with_firebase_auth(email, password):
    if "@" not in email:
        email = f"{email}@admin.com"
    elif not email.endswith("@admin.com"):
        username = email.split("@")[0]
        email = f"{username}@admin.com"

    # Firebase Web API를 사용한 비밀번호 검증 (우선순위)
    if FIREBASE_WEB_API_KEY:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        response = requests.post(url, json=payload)
        res_data = response.json()
        
        if response.status_code == 200:
            return True, res_data
        else:
            return False, res_data.get('error', {}).get('message', 'Login failed')
    
    # API Key가 없는 경우: 데이터베이스의 password_plain과 비교
    try:
        user = auth.get_user_by_email(email)
        user_data = db.reference(f'users/{user.uid}').get()
        
        if user_data and user_data.get('password_plain') == password:
            return True, {"localId": user.uid, "displayName": user.display_name or user_data.get('name') or email.split('@')[0]}
        else:
            return False, "비밀번호가 일치하지 않습니다."
    except Exception as e:
        return False, f"사용자를 찾을 수 없습니다: {str(e)}"

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
    
    user_data = db.reference(f'users/{uid}').get()
    if not user_data or user_data.get('status') != 'active':
        return jsonify({"success": False, "message": "승인되지 않았거나 비활성화된 계정입니다."}), 403

    display_name = user_data.get('name') or result.get('displayName') or email.split('@')[0]

    session['user'] = {'uid': uid, 'email': email, 'name': display_name}
    return jsonify({"success": True})

@app.route('/te/logout', methods=['POST'])
def api_logout():
    session.pop('user', None)
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
