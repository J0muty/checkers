const timerEl = document.getElementById('waitTimer');
const cancelBtn = document.getElementById('cancelBtn');
let seconds = 0;
let timerInterval = null;
let ws = null;

function cancelSearch() {
    navigator.sendBeacon('/api/cancel_game');
}

function formatTime(s) {
    const m = Math.floor(s / 60).toString().padStart(2, '0');
    const sec = (s % 60).toString().padStart(2, '0');
    return `${m}:${sec}`;
}

async function startTimer() {
    const res = await fetch('/api/user_status');
    const data = await res.json();
    const start = data.waiting_since
        ? data.waiting_since * 1000
        : Date.now();
    seconds = Math.floor((Date.now() - start) / 1000);
    timerEl.textContent = formatTime(seconds);
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        seconds += 1;
        timerEl.textContent = formatTime(seconds);
    }, 1000);
}

function buildWsUrl() {
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    return `${proto}://${location.host}/ws/waiting/${userId}`;
}

function setupWebSocket() {
    ws = new WebSocket(buildWsUrl());
    ws.addEventListener('message', e => {
        const data = JSON.parse(e.data);
        if (data.board_id) {
            cleanupAndGo(data.board_id, data.color);
        }
    });
    ws.addEventListener('close', () => {
        setTimeout(setupWebSocket, 1000);
    });
}

function cleanupAndGo(boardId, color) {
    window.removeEventListener('beforeunload', cancelSearch);
    clearInterval(timerInterval);
    window.location.href = `/board/${boardId}?player=${userId}&color=${color}`;
}

async function joinQueue() {
    const res = await fetch('/api/search_game', { method: 'POST' });
    const data = await res.json();
    if (data.board_id) {
        cleanupAndGo(data.board_id, data.color);
    } else {
        await startTimer();
    }
}

window.addEventListener('beforeunload', () => {
    if (!performance.getEntriesByType ||
        performance.getEntriesByType('navigation')[0].type !== 'reload') {
        cancelSearch();
    }
});

cancelBtn.addEventListener('click', async () => {
    await fetch('/api/cancel_game', { method: 'POST' });
    window.removeEventListener('beforeunload', cancelSearch);
    clearInterval(timerInterval);
    window.location.href = '/';
});

document.addEventListener('DOMContentLoaded', async () => {
    setupWebSocket();

    const res = await fetch('/api/user_status');
    const data = await res.json();

    if (data.board_id) {
        cleanupAndGo(data.board_id, data.color);
    } else if (data.waiting_since) {
        await startTimer();
    } else {
        await joinQueue();
    }
});
