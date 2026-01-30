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

app = Flask(__name__)
app.secret_key = 'overview-secret-key-2026'
CORS(app)

# Firebase 설정
SERVICE_ACCOUNT_FILE = "serviceAccountKey.json"
FIREBASE_URL = 'https://main-d9759-default-rtdb.firebaseio.com/'
TELEGRAM_TOKEN = "8087683880:AAEHaQeumeYcVIKf7r4F7AFgsoCsDzBuuiA"
ADMIN_CHAT_ID = 6681290555

# Firebase Web API Key
FIREBASE_WEB_API_KEY = os.environ.get('FIREBASE_WEB_API_KEY', '')

# Firebase 초기화
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
    firebase_admin.initialize_app(cred, {
        'databaseURL': FIREBASE_URL
    })

# Firebase REST API 키 (serviceAccountKey.json에서 추출)
try:
    with open(SERVICE_ACCOUNT_FILE, 'r') as f:
        firebase_config = json.load(f)
        FIREBASE_PROJECT_ID = firebase_config.get('project_id')
except:
    FIREBASE_PROJECT_ID = None

# ============================================
# 유틸리티 함수
# ============================================

def send_telegram_notification(message):
    """관리자에게 텔레그램 알림 전송"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": ADMIN_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        requests.post(url, data=data, timeout=5)
    except Exception as e:
        print(f"텔레그램 알림 실패: {e}")

def get_client_ip():
    """클라이언트 IP 주소 반환"""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
    return request.environ.get('REMOTE_ADDR', 'unknown')

def login_required(f):
    """로그인 확인 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================
# 라우트 설정
# ============================================

@app.route('/')
def index():
    """메인 페이지"""
    user = session.get('user_id')
    return render_template('index.html', user=user)

@app.route('/dashboard')
@login_required
def dashboard():
    """대시보드 페이지 (이제 다운로드 페이지로 통합하거나 유지)"""
    return render_template('dashboard.html')

@app.route('/download')
@login_required
def download_page():
    """다운로드 페이지"""
    return render_template('download.html')

@app.route('/login', methods=['GET'])
def login_page():
    """로그인 페이지"""
    if 'user_id' in session:
        return redirect(url_for('download_page'))
    return render_template('login.html')

@app.route('/signup', methods=['GET'])
def signup_page():
    """회원가입 페이지"""
    return render_template('signup.html')

# ============================================
# API 엔드포인트
# ============================================

@app.route('/api/signup', methods=['POST'])
def api_signup():
    """회원가입 API"""
    try:
        data = request.get_json()
        required_fields = ['name', 'username', 'password', 'confirm_password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"success": False, "message": f"{field} 필드가 누락되었습니다."}), 400
        
        name = data['name'].strip()
        username = data['username'].strip()
        password = data['password']
        confirm_password = data['confirm_password']
        ip = get_client_ip()
        
        if len(username) < 6:
            return jsonify({"success": False, "message": "사용자 ID는 6자 이상이어야 합니다."}), 400
        if len(password) < 6:
            return jsonify({"success": False, "message": "비밀번호는 6자 이상이어야 합니다."}), 400
        if password != confirm_password:
            return jsonify({"success": False, "message": "비밀번호가 일치하지 않습니다."}), 400
        
        email = f"{username}@admin.com"
        try:
            # 먼저 기존 Auth 사용자가 있는지 확인
            try:
                user = auth.get_user_by_email(email)
                uid = user.uid
                # 기존 사용자가 있다면 비밀번호 업데이트 (재가입 처리)
                auth.update_user(uid, password=password, display_name=name)
            except auth.UserNotFoundError:
                # 없으면 새로 생성
                user = auth.create_user(email=email, password=password, display_name=name)
                uid = user.uid
        except Exception as e:
            return jsonify({"success": False, "message": f"인증 계정 처리 중 오류: {str(e)}"}), 500
        
        # 승인 대기 목록 추가 (비밀번호 원문 포함)
        db.reference(f'remote_requests/{uid}').set({
            'name': name, 'username': username, 'email': email, 'password': password, 'ip': ip,
            'timestamp': int(datetime.datetime.now().timestamp()),
            'requested_at': datetime.datetime.now().isoformat(), 'status': 'pending'
        })
        
        send_telegram_notification(f"🆕 <b>신규 회원가입 신청</b>\n\n👤 이름: {name}\n🆔 ID: {username}\n🔑 PW: {password}\n🌐 IP: {ip}")
        return jsonify({"success": True, "message": "가입 신청 완료. 관리자 승인을 기다려주세요."}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    """로그인 API"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({"success": False, "message": "ID와 비밀번호를 입력해주세요."}), 400
        
        email = f"{username}@admin.com"
        
        # 데이터베이스(RTDB)에서 사용자 직접 검색 및 비밀번호 비교
        users_ref = db.reference('users')
        all_users = users_ref.get() or {}
        
        user_data = None
        target_uid = None
        
        for uid, data in all_users.items():
            # DB의 username과 password_plain이 입력값과 정확히 일치하는지 확인
            if data.get('username') == username and str(data.get('password_plain')) == str(password):
                user_data = data
                target_uid = uid
                break
        
        if not user_data:
            return jsonify({"success": False, "message": "ID 또는 비밀번호가 일치하지 않습니다."}), 401
            
        # 승인 여부 확인 로직 유지
        if user_data.get('status') != 'active':
            return jsonify({"success": False, "message": "계정이 비활성화되었습니다.", "status": "inactive"}), 403
        
        # 만료 확인
        expire_date_str = user_data.get('expire_date', '2026-12-31')
        try:
            if datetime.datetime.strptime(expire_date_str, '%Y-%m-%d') < datetime.datetime.now():
                return jsonify({"success": False, "message": "계정이 만료되었습니다.", "status": "expired"}), 403
        except: pass
        
        # 세션 설정
        session['user_id'] = target_uid
        session['username'] = username
        session['name'] = user_data.get('name')
        
        return jsonify({"success": True, "message": "로그인 성공"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": "로그인 중 오류 발생"}), 500

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"success": True, "message": "로그아웃되었습니다."}), 200

@app.route('/api/admin/delete_user', methods=['POST'])
def api_admin_delete_user():
    """관리자용 사용자 삭제 API (Auth + DB 동시 삭제)"""
    try:
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({"success": False, "message": "삭제할 사용자 ID가 필요합니다."}), 400
            
        # 1. DB에서 사용자 찾기
        users_ref = db.reference('users')
        all_users = users_ref.get()
        target_uid = None
        
        if all_users:
            for uid, user_data in all_users.items():
                if user_data.get('username') == username:
                    target_uid = uid
                    break
        
        if not target_uid:
            return jsonify({"success": False, "message": "해당 사용자를 DB에서 찾을 수 없습니다."}), 404
            
        # 2. Firebase Auth에서 삭제
        try:
            auth.delete_user(target_uid)
        except auth.UserNotFoundError:
            pass # 이미 Auth에서 삭제된 경우 무시
            
        # 3. Firebase DB에서 삭제
        users_ref.child(target_uid).delete()
        
        return jsonify({"success": True, "message": f"사용자 {username}이(가) 완전히 삭제되었습니다."}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
