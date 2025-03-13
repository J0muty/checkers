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
    const networkGameButton = buttons[1];
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
