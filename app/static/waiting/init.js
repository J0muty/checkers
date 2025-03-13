import { initTimer } from './timer.js';
import { initWebSocket } from './ws.js';
import { initCancelButton } from './cancelButton.js';

document.addEventListener('DOMContentLoaded', () => {
    const timerElement = document.querySelector('.timer');
    const cancelButton = document.getElementById('cancel-button');
    initTimer(timerElement);
    const gameKey = window.gameKey || "";
    initWebSocket(gameKey);
    initCancelButton(cancelButton);
});