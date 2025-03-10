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
}
