export function initWebSocket(gameKey) {
    if (!gameKey) {
        console.error('gameKey is not defined');
        return;
    }

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
}