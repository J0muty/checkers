export function initMenu() {
    const friendsBtn = document.getElementById('friendsBtn');
    const topBtn = document.getElementById('topBtn');
    const statsBtn = document.getElementById('statsBtn');
    const friendsBtnHamburger = document.getElementById('friendsBtnHamburger');
    const topBtnHamburger = document.getElementById('topBtnHamburger');
    const statsBtnHamburger = document.getElementById('statsBtnHamburger');
    const hamburgerIcon = document.querySelector('.hamburger-menu i');
    const dropdownMenu = document.querySelector('.hamburger-menu .dropdown-menu');

    const commonAction = (msg) => () => {
        alert(msg);
        dropdownMenu.classList.remove('show');
    };

    friendsBtn.addEventListener('click', () => alert('Открыть список друзей'));
    topBtn.addEventListener('click', () => alert('Открыть топ игроков'));
    statsBtn.addEventListener('click', () => alert('Открыть статистику'));

    friendsBtnHamburger.addEventListener('click', commonAction('Открыть список друзей'));
    topBtnHamburger.addEventListener('click', commonAction('Открыть топ игроков'));
    statsBtnHamburger.addEventListener('click', commonAction('Открыть статистику'));

    hamburgerIcon.addEventListener('click', (event) => {
        event.stopPropagation();
        dropdownMenu.classList.toggle('show');
    });

    document.addEventListener('click', (event) => {
        if (!document.querySelector('.hamburger-menu').contains(event.target)) {
            dropdownMenu.classList.remove('show');
        }
    });
}