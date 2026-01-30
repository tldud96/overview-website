/**
 * OverView - 메인 JavaScript
 */

// 로그아웃 함수
async function logout() {
    try {
        const response = await fetch('/api/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            window.location.href = '/';
        } else {
            alert('로그아웃 중 오류가 발생했습니다.');
        }
    } catch (error) {
        console.error('Logout error:', error);
        alert('로그아웃 중 오류가 발생했습니다.');
    }
}

// 페이지 로드 시 실행
document.addEventListener('DOMContentLoaded', () => {
    // 필요한 초기화 코드
    console.log('OverView 애플리케이션 로드됨');
});

// 스크롤 애니메이션
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.boxShadow = '0 8px 24px rgba(0, 212, 255, 0.3)';
    } else {
        navbar.style.boxShadow = 'var(--shadow-md)';
    }
});
