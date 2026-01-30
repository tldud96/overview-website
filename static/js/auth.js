/**
 * OverView - 인증 관련 JavaScript
 */

// 클라이언트 IP 가져오기
async function getClientIP() {
    try {
        const response = await fetch('/api/get-ip');
        const data = await response.json();
        return data.ip;
    } catch (error) {
        console.error('Error getting IP:', error);
        return 'unknown';
    }
}

// 폼 제출 시 IP 추가
document.addEventListener('DOMContentLoaded', async () => {
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        const ip = await getClientIP();
        
        // 폼 제출 전에 IP 추가
        signupForm.addEventListener('submit', async (e) => {
            // IP를 폼 데이터에 추가하는 로직은 signup.html에서 처리
        });
    }
});
