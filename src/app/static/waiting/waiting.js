const timerEl = document.getElementById('waitTimer');
const cancelBtn = document.getElementById('cancelBtn');
let seconds = 0;

function cancelSearch() {
    navigator.sendBeacon('/api/cancel_game');
}


function formatTime(s) {
    const m = Math.floor(s / 60).toString().padStart(2, '0');
    const sec = (s % 60).toString().padStart(2, '0');
    return `${m}:${sec}`;
}

function startTimer() {
    timerEl.textContent = formatTime(seconds);
    setInterval(() => {
        seconds += 1;
        timerEl.textContent = formatTime(seconds);
    }, 1000);
}

async function poll() {
    const res = await fetch('/api/check_game');
    const data = await res.json();
    if (data.board_id) {
        window.removeEventListener('beforeunload', cancelSearch);
        window.location.href = `/board/${data.board_id}?player=${userId}&color=${data.color}`;
    } else {
        setTimeout(poll, 2000);
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
    window.location.href = '/';
});

startTimer();
joinQueue();
