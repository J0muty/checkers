export function initNavigation() {
    const backBtn = document.getElementById('backBtn');
    const exitBtn = document.getElementById('exitBtn');

    backBtn.addEventListener('click', () => {
        window.location.href = '/';
    });
    exitBtn.addEventListener('click', () => {
        window.location.href = '/logout';
    });
}