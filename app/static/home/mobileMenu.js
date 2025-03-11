export function initMobileMenu() {
    const mobileBar = document.querySelector('.mobile-bar');
    const mobileMenu = document.querySelector('.mobile-menu');
    const mobileMenuClose = document.querySelector('.mobile-menu-close');

    if (mobileBar) {
        mobileBar.addEventListener('click', () => {
            mobileMenu.classList.add('active');
        });
    }
    if (mobileMenuClose) {
        mobileMenuClose.addEventListener('click', () => {
            mobileMenu.classList.remove('active');
        });
    }

    const mobileLogin = document.querySelector('.mobile-login');
    mobileLogin && mobileLogin.addEventListener('click', () => {
        window.location.href = '/login';
    });

    const mobileRegister = document.querySelector('.mobile-register');
    mobileRegister && mobileRegister.addEventListener('click', () => {
        window.location.href = '/register';
    });

    const mobileProfile = document.querySelector('.mobile-profile');
    mobileProfile && mobileProfile.addEventListener('click', () => {
        window.location.href = '/profile';
    });
    const mobileLogout = document.querySelector('.mobile-logout');
    mobileLogout && mobileLogout.addEventListener('click', () => {
        window.location.href = '/logout';
    });
}