import { updateButtonText } from './buttonText.js';
import { initMobileMenu } from './mobileMenu.js';
import { animateButtons } from './animations.js';

document.addEventListener("DOMContentLoaded", () => {
    updateButtonText();
    window.addEventListener("resize", updateButtonText);
    animateButtons();
    initMobileMenu();
});
