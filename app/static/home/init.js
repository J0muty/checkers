import { updateButtonText } from './buttonText.js';
import { initMobileMenu } from './mobileMenu.js';
import { animateButtons } from './animations.js';

document.addEventListener("DOMContentLoaded", () => {
    updateButtonText();
    window.addEventListener("resize", updateButtonText);
    animateButtons();
    initMobileMenu();
});

document.addEventListener("DOMContentLoaded", () => {
    const buttons = document.querySelectorAll('.buttons button');
    const singlePlayerButton = buttons[0];
    const networkGameButton = buttons[1];
    singlePlayerButton.addEventListener('click', () => {
        const modal = document.getElementById('modal');
        modal.style.display = 'flex';
    });
    const closeModalBtn = document.querySelector('.modal-close');
    closeModalBtn.addEventListener('click', () => {
        const modal = document.getElementById('modal');
        modal.style.display = 'none';
    });
    window.addEventListener('click', e => {
        const modal = document.getElementById('modal');
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
    networkGameButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/game/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const result = await response.json();
            if (result.redirect) {
                window.location.href = result.redirect;
            } else {
                window.location.href = '/waiting';
            }
        } catch (error) {
            alert('Ошибка сети или сервера');
        }
    });
});
