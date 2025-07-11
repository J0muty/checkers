const statusBox = document.getElementById('statusBox');
const timerEl = document.getElementById('statusTimer');
const returnBtn = document.getElementById('statusReturn');
const leaveBtn = document.getElementById('statusLeave');
const leaveModal = document.getElementById('leaveModal');
const leaveYes = document.getElementById('leaveYes');
const leaveNo = document.getElementById('leaveNo');
const singleBtn = document.getElementById('singleBtn');
const singleModal = document.getElementById('singleModal');
const singleCloseBtn = document.getElementById('singleCloseBtn');
const startSingleBtn = document.getElementById('startSingleBtn');

let timerInterval = null;
let waitingWs = null;
let boardWs = null;
let currentBoardId = null;

function buildWaitingWsUrl() {
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    return `${proto}://${location.host}/ws/waiting/${userId}`;
}

function buildBoardWsUrl(boardId) {
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    return `${proto}://${location.host}/ws/board/${boardId}`;
}

function formatTime(sec) {
    const m = Math.floor(sec / 60).toString().padStart(2, '0');
    const s = Math.floor(sec % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
}

function startInterval(fn) {
    clearInterval(timerInterval);
    timerInterval = setInterval(fn, 1000);
    fn();
}

function setupWaitingWs() {
    if (waitingWs) return;
    waitingWs = new WebSocket(buildWaitingWsUrl());
    waitingWs.addEventListener('message', () => {
        updateStatus();
    });
    waitingWs.addEventListener('close', () => {
        waitingWs = null;
        if (statusBox.style.display === 'flex' && !currentBoardId) {
            setTimeout(setupWaitingWs, 1000);
        }
    });
}

function setupBoardWs(boardId) {
    if (boardWs && currentBoardId === boardId) return;
    if (boardWs) {
        boardWs.close();
        boardWs = null;
    }
    currentBoardId = boardId;
    boardWs = new WebSocket(buildBoardWsUrl(boardId));
    boardWs.addEventListener('message', e => {
        const data = JSON.parse(e.data);
        if (data.status) {
            updateStatus();
        }
    });
    boardWs.addEventListener('close', () => {
        boardWs = null;
        if (currentBoardId) {
            setTimeout(() => setupBoardWs(currentBoardId), 1000);
        }
    });
}

function closeAllWs() {
    if (waitingWs) {
        waitingWs.close();
        waitingWs = null;
    }
    if (boardWs) {
        boardWs.close();
        boardWs = null;
    }
    currentBoardId = null;
}

async function updateStatus() {
    const res = await fetch('/api/user_status');
    if (!res.ok) return;
    const data = await res.json();
    if (data.board_id) {
        setupBoardWs(data.board_id);
        if (waitingWs) {
            waitingWs.close();
            waitingWs = null;
        }
        statusBox.style.display = 'flex';
        returnBtn.onclick = () => {
            window.location.href = `/board/${data.board_id}?player=${userId}&color=${data.color}`;
        };
        leaveBtn.onclick = () => {
            leaveModal.classList.add('active');
        };
        leaveYes.onclick = async () => {
            leaveModal.classList.remove('active');
            await fetch(`/api/resign/${data.board_id}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({player: data.color})
            });
            updateStatus();
        };
        leaveNo.onclick = () => leaveModal.classList.remove('active');
        startInterval(async () => {
            const tRes = await fetch(`/api/timers/${data.board_id}`);
            if (!tRes.ok) return;
            const t = await tRes.json();
            timerEl.textContent = formatTime(t[data.color]);
        });
    } else if (data.waiting_since) {
        if (!waitingWs) {
            setupWaitingWs();
        }
        if (boardWs) {
            boardWs.close();
            boardWs = null;
            currentBoardId = null;
        }
        statusBox.style.display = 'flex';
        returnBtn.onclick = () => {
            window.location.href = '/waiting';
        };
        leaveBtn.onclick = async () => {
            await fetch('/api/cancel_game', {method: 'POST'});
            updateStatus();
        };
        startInterval(() => {
            const sec = Math.floor((Date.now() - data.waiting_since * 1000) / 1000);
            timerEl.textContent = formatTime(sec);
        });
    } else {
        closeAllWs();
        statusBox.style.display = 'none';
        clearInterval(timerInterval);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    updateStatus();
    if (singleBtn) {
        singleBtn.addEventListener('click', () => {
            singleModal.classList.add('active');
        });
        singleCloseBtn.addEventListener('click', () => {
            singleModal.classList.remove('active');
        });
        startSingleBtn.addEventListener('click', () => {
            const diff = document.querySelector('input[name="difficulty"]:checked').value;
            const color = document.querySelector('input[name="spcolor"]:checked').value;
            const id = crypto.randomUUID();
            window.location.href = `/singleplayer/${id}?difficulty=${diff}&color=${color}`;
        });
    }
    [leaveModal, singleModal].forEach(overlay => {
        overlay.addEventListener('click', e => {
            if (e.target === overlay) overlay.classList.remove('active');
        });
    });
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') {
            [leaveModal, singleModal].forEach(o => o.classList.remove('active'));
        }
    });
});
