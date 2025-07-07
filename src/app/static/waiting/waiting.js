const timerEl = document.getElementById('waitTimer');
const cancelBtn = document.getElementById('cancelBtn');
let seconds = 0;
let timerInterval = null;
let ws = null;

function cancelSearch() {
    navigator.sendBeacon('/api/cancel_game');
    localStorage.removeItem('waitingStart');
}


function formatTime(s) {
    const m = Math.floor(s / 60).toString().padStart(2, '0');
    const sec = (s % 60).toString().padStart(2, '0');
    return `${m}:${sec}`;
}

function startTimer() {
    const start = Number(localStorage.getItem('waitingStart')) || Date.now();
    localStorage.setItem('waitingStart', start);
    seconds = Math.floor((Date.now() - start) / 1000);
    timerEl.textContent = formatTime(seconds);
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
    localStorage.removeItem('waitingStart');
    clearInterval(timerInterval);
    window.location.href = `/board/${boardId}?player=${userId}&color=${color}`;
}

async function joinQueue() {
    const res = await fetch('/api/search_game', {method: 'POST'});
    const data = await res.json();
    if (data.board_id) {
        cleanupAndGo(data.board_id, data.color);
    } else {
        const check = await fetch('/api/check_game');
        const chData = await check.json();
        if (chData.board_id) {
            cleanupAndGo(chData.board_id, chData.color);
        }
    }
}

async function joinQueue() {
    await fetch('/api/search_game', {method: 'POST'});
    poll();
}

window.addEventListener('beforeunload', cancelSearch);

cancelBtn.addEventListener('click', async () => {
    await fetch('/api/cancel_game', {method: 'POST'});
    window.removeEventListener('beforeunload', cancelSearch);
    localStorage.removeItem('waitingStart');
    clearInterval(timerInterval);
    window.location.href = '/';
});

startTimer();
setupWebSocket();
joinQueue();
