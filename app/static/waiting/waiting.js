document.addEventListener('DOMContentLoaded', () => {
    let secondsElapsed = 0;
    const timerElement = document.querySelector('.timer');
    const cancelButton = document.getElementById('cancel-button');
    setInterval(() => {
        secondsElapsed++;
        const minutes = String(Math.floor(secondsElapsed / 60)).padStart(2, '0');
        const seconds = String(secondsElapsed % 60).padStart(2, '0');
        timerElement.textContent = `${minutes}:${seconds}`;
    }, 1000);
    const gameKey = window.gameKey || "";
    if (gameKey) {
        const ws = new WebSocket(`ws://${window.location.host}/ws/game?game_key=${encodeURIComponent(gameKey)}`);

        ws.onopen = () => {
            console.log("Соединение с WebSocket установлено");
        };

        ws.onerror = (error) => {
            console.error("Ошибка WebSocket:", error);
        };

        ws.onclose = (event) => {
            console.log("Соединение с WebSocket закрыто", event);
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.redirect) {
                window.location.href = data.redirect;
            }
        };
    } else {
        console.error('gameKey is not defined');
    }

    cancelButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/waiting/cancel', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();
            if (data.message === "Поиск отменён") {
                window.location.href = '/';
            } else {
                alert(data.message);
            }
        } catch (error) {
            console.error('Ошибка при отмене поиска:', error);
        }
    });
});
