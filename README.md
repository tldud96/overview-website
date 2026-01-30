# OverView - Firebase 기반 회원가입/승인 시스템

Flask + Firebase를 기반으로 한 원격 제어 솔루션 웹 애플리케이션입니다. 회원가입, 로그인, 관리자 승인, 파일 다운로드 등의 기능을 제공합니다.

## 주요 기능

### 사용자 기능
- **회원가입**: 새로운 사용자 등록 (관리자 승인 필요)
- **로그인**: 승인된 사용자 로그인
- **대시보드**: 계정 정보 및 상태 확인
- **다운로드**: 승인된 사용자만 파일 다운로드 가능

### 관리자 기능
- **승인 대기 목록**: 신규 가입 신청 조회
- **회원가입 승인/거절**: 사용자 승인 또는 거절
- **사용자 관리**: 승인된 사용자 목록 조회 및 관리
- **계정 상태 관리**: 사용자 상태 및 만료일 설정

### 알림 기능
- **텔레그램 알림**: 신규 가입, 승인, 거절 시 텔레그램으로 알림 전송

## 기술 스택

- **백엔드**: Flask (Python)
- **데이터베이스**: Firebase Realtime Database
- **인증**: Firebase Authentication
- **알림**: Telegram Bot API
- **프론트엔드**: HTML5, CSS3, JavaScript
- **디자인**: 다크 테마 + 사이버펑크 스타일

## 설치 및 실행

### 1. 필수 요구사항
- Python 3.7 이상
- Firebase 프로젝트 (serviceAccountKey.json)
- Telegram Bot Token 및 Chat ID

### 2. 설치

```bash
# 저장소 클론
cd overview-firebase-app

# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 3. 설정

#### Firebase 설정
1. Firebase 콘솔에서 프로젝트 생성
2. 서비스 계정 키 다운로드 (JSON 형식)
3. `serviceAccountKey.json` 파일을 프로젝트 루트에 저장

#### Telegram 설정
`app.py`의 다음 부분을 수정하세요:

```python
TELEGRAM_TOKEN = "your_telegram_bot_token"
ADMIN_CHAT_ID = your_admin_chat_id
```

#### Firebase URL 설정
`app.py`의 다음 부분을 수정하세요:

```python
FIREBASE_URL = 'https://your-firebase-project.firebaseio.com/'
```

### 4. 실행

```bash
python app.py
```

서버가 `http://localhost:5000`에서 시작됩니다.

## 디렉토리 구조

```
overview-firebase-app/
├── app.py                      # Flask 메인 애플리케이션
├── serviceAccountKey.json      # Firebase 서비스 계정 키
├── requirements.txt            # Python 의존성
├── README.md                   # 이 파일
├── templates/                  # HTML 템플릿
│   ├── index.html             # 메인 페이지
│   ├── signup.html            # 회원가입 페이지
│   ├── login.html             # 로그인 페이지
│   ├── download.html          # 다운로드 페이지
│   └── dashboard.html         # 대시보드 페이지
├── static/                     # 정적 파일
│   ├── css/
│   │   └── style.css          # 메인 스타일시트
│   └── js/
│       ├── main.js            # 메인 JavaScript
│       └── auth.js            # 인증 관련 JavaScript
└── downloads/                  # 다운로드 파일 저장소
```

## API 엔드포인트

### 인증 관련
- `POST /api/signup` - 회원가입
- `POST /api/login` - 로그인
- `POST /api/logout` - 로그아웃
- `POST /api/check-username` - 사용자 ID 중복 확인

### 사용자 관련
- `GET /api/user/info` - 현재 사용자 정보 조회
- `GET /api/get-ip` - 클라이언트 IP 주소 조회

### 다운로드 관련
- `POST /api/download/verify` - 다운로드 권한 확인
- `GET /api/download/file` - 파일 다운로드

### 관리자 관련
- `GET /admin/requests` - 승인 대기 목록 조회
- `POST /admin/approve/<uid>` - 회원가입 승인
- `DELETE /admin/reject/<uid>` - 회원가입 거절
- `GET /admin/users` - 사용자 목록 조회
- `POST /admin/update-user/<uid>` - 사용자 정보 업데이트

## Firebase 데이터베이스 구조

```
{
  "remote_requests": {
    "uid": {
      "name": "사용자명",
      "username": "사용자ID",
      "email": "email@overview.com",
      "ip": "IP주소",
      "timestamp": 1234567890,
      "requested_at": "2026-01-30T12:00:00",
      "status": "pending"
    }
  },
  "users": {
    "uid": {
      "name": "사용자명",
      "username": "사용자ID",
      "email": "email@overview.com",
      "status": "active",
      "expire_date": "2026-12-31",
      "allowed_ip": "IP주소",
      "created_at": "2026-01-30T12:00:00",
      "email_domain": "overview.com"
    }
  },
  "download_logs": {
    "uid": {
      "timestamp": 1234567890,
      "ip": "IP주소",
      "downloaded_at": "2026-01-30T12:00:00"
    }
  }
}
```

## 보안 고려사항

1. **비밀번호**: Firebase Authentication에서 안전하게 관리
2. **세션**: Flask 세션을 통해 관리 (프로덕션에서는 더 강력한 세션 관리 필요)
3. **HTTPS**: 프로덕션 환경에서는 반드시 HTTPS 사용
4. **API 키**: 환경 변수로 관리 (`.env` 파일 사용 권장)
5. **관리자 인증**: 현재는 간단한 UID 확인, 프로덕션에서는 더 강력한 인증 필요

## 사용 예시

### 회원가입
1. `/signup` 페이지 방문
2. 이름, ID, 비밀번호 입력
3. ID 중복확인 클릭
4. 가입하기 버튼 클릭
5. 관리자 승인 대기

### 로그인
1. `/login` 페이지 방문
2. ID와 비밀번호 입력
3. 로그인 버튼 클릭
4. 대시보드로 이동

### 파일 다운로드
1. `/download` 페이지 방문
2. 로그인 (미로그인 시)
3. 다운로드 버튼 클릭
4. 파일 다운로드 시작

## 문제 해결

### Firebase 연결 오류
- `serviceAccountKey.json` 파일 경로 확인
- Firebase URL 확인
- Firebase 프로젝트 권한 확인

### 텔레그램 알림 미수신
- Telegram Bot Token 확인
- Admin Chat ID 확인
- 네트워크 연결 확인

### 로그인 실패
- Firebase Authentication 활성화 확인
- 사용자 ID와 비밀번호 확인
- 관리자 승인 여부 확인

## 라이선스

MIT License

## 지원

문제가 발생하면 이슈를 등록해주세요.
