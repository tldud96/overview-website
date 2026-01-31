"""
OverView - Firebase 기반 회원가입/승인 시스템 (v7 - 최종 통합 버전)
- Firebase SDK 초기화 오류 해결을 위해 REST API 직접 호출 방식 사용
- 이메일 로직 완전 제거 (ID 그대로 사용)
- 환경 변수 없이도 작동 가능하며, 로컬 및 서버 환경 모두 호환
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import os
import datetime
import requests
from functools import wraps
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'overview-secret-key-2026')
CORS(app)

# 설정값 (URL 끝에 .json을 붙여서 사용해야 함)
FIREBASE_URL = "https://login-ab1f2-default-rtdb.firebaseio.com"

# ============================================
# 유틸리티 함수
# ============================================

def verify_user(input_id, password):
    """REST API를 사용하여 DB(users)에서 인증"""
    try:
        print(f"[Login Attempt] ID: {input_id}")
        # Firebase REST API 호출
        response = requests.get(f"{FIREBASE_URL}/users.json", timeout=8)
        if response.status_code != 200:
            print(f"[DB Error] Status Code: {response.status_code}")
            return False, "데이터베이스 연결 오류"
            
        users = response.json() or {}
        
        # 딕셔너리 형태의 users를 순회하며 매칭되는 사용자 찾기
        for uid, udata in users.items():
            if not isinstance(udata, dict): continue
            
            # DB의 user_id 필드와 입력된 ID를 직접 비교
            db_user_id = str(udata.get('user_id', '')).strip()
            db_password = str(udata.get('password', '')).strip()
            
            if db_user_id == str(input_id).strip() and db_password == str(password).strip():
                if udata.get('status') == 'active':
                    print(f"[Login Success] ID: {input_id}")
                    return True, {"uid": uid, "username": udata.get('username'), "user_id": input_id}
                else:
                    print(f"[Login Failed] Status not active for ID: {input_id}")
                    return False, "승인 대기 중이거나 비활성화된 계정입니다."
        
        print(f"[Login Failed] ID or PW mismatch for ID: {input_id}")
        return False, "아이디 또는 비밀번호가 올바르지 않습니다."
    except Exception as e:
        print(f"[Auth Error] {e}")
        return False, f"인증 오류: {str(e)}"

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
    """REST API를 사용하여 pending_requests에 등록"""
    data = request.json
    name = data.get('name')
    user_id = data.get('email') # UI 필드명 유지
    password = data.get('password')
    
    if not name or not user_id or not password:
        return jsonify({"success": False, "message": "모든 정보를 입력해주세요."}), 400
    
    try:
        # 중복 체크
        response = requests.get(f"{FIREBASE_URL}/users.json", timeout=8)
        users = response.json() or {}
        for uid, udata in users.items():
            if not isinstance(udata, dict): continue
            if str(udata.get('user_id', '')).strip() == str(user_id).strip():
                return jsonify({"success": False, "message": "이미 존재하는 ID입니다."}), 400
        
        now = datetime.datetime.now()
        expire = now + datetime.timedelta(days=30)
        
        request_data = {
            "username": name,
            "user_id": user_id,
            "password": password,
            "ip": request.remote_addr,
            "hwid": "web_signup",
            "expire_date": expire.strftime("%Y-%m-%d"),
            "process_limit": 1,
            "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "pending"
        }
        
        # REST API POST 요청
        post_res = requests.post(f"{FIREBASE_URL}/pending_requests.json", json=request_data, timeout=8)
        if post_res.status_code == 200:
            return jsonify({"success": True, "message": "가입 신청 완료! 관리자 승인을 기다려주세요."})
        else:
            return jsonify({"success": False, "message": "가입 신청 전송 실패"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    """입력된 ID/PW로 직접 인증"""
    data = request.json
    user_id = data.get('email') # UI 필드명 유지
    password = data.get('password')
    
    success, result = verify_user(user_id, password)
    
    if not success:
        return jsonify({"success": False, "message": result}), 401
        
    session['user'] = {
        'uid': result['uid'],
        'user_id': result['user_id'],
        'name': result['username']
    }
    return jsonify({"success": True})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
