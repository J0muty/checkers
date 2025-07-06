const boardElement = document.getElementById('board');
const historyList = document.getElementById('historyList');
const timer1 = document.getElementById('timer1');
const timer2 = document.getElementById('timer2');
const player1 = document.querySelector('.player1');
const player2 = document.querySelector('.player2');
const returnButton = document.getElementById('returnButton');
const letters = ['', 'A','B','C','D','E','F','G','H',''];
const numbers = ['', '8','7','6','5','4','3','2','1',''];

let boardState = [];
let selected = null;
let possibleMoves = [];
let timers = {white: 600, black: 600, turn: 'white'};
let timerStart = Date.now();
let timerInterval = null;
let turn = 'white';
let gameOver = false;
let multiCapture = false;
let viewingHistory = false;

async function fetchBoard() {
    const data = await (await fetch(`/api/board/${boardId}`)).json();
    boardState = data.board;
    timers = data.timers;
    timerStart = Date.now();
    turn = data.timers.turn;
    historyList.innerHTML = '';
    data.history.forEach((m, i) => {
        const li = document.createElement('li');
        li.textContent = m;
        li.dataset.index = i + 1;
        li.addEventListener('click', onHistoryClick);
        historyList.appendChild(li);
    });
    viewingHistory = false;
    returnButton.style.display = 'none';
    setActivePlayer(turn);
    startTimers();
    renderBoard();
}

async function fetchMoves(r, c) {
    return await (await fetch(
        `/api/moves/${boardId}?row=${r}&col=${c}&player=${turn}`
    )).json();
}

async function fetchCaptures(r, c) {
    return await (await fetch(
        `/api/captures/${boardId}?row=${r}&col=${c}&player=${turn}`
    )).json();
}

function renderBoard() {
    boardElement.innerHTML = '';
    for (let row = 0; row < 10; row++) {
        for (let col = 0; col < 10; col++) {
            const cell = document.createElement('div');
            cell.classList.add('square');
            cell.dataset.row = row;
            cell.dataset.col = col;

            if (row === 0 || row === 9) {
                cell.classList.add('label', row === 0 ? 'label-top' : 'label-bottom');
                cell.textContent = letters[col];
            } else if (col === 0 || col === 9) {
                cell.classList.add('label', col === 0 ? 'label-left' : 'label-right');
                cell.textContent = numbers[row];
            } else {
                const r = row - 1;
                const c = col - 1;
                cell.classList.add((r + c) % 2 ? 'dark' : 'light');

                if (selected && selected.row === r && selected.col === c) {
                    cell.classList.add('selected');
                }
                if (possibleMoves.some(m => m[0] === r && m[1] === c)) {
                    cell.classList.add('highlight');
                }

                const piece = boardState[r][c];
                if (piece) {
                    const p = document.createElement('div');
                    p.classList.add('piece', piece.toLowerCase() === 'w' ? 'white' : 'black');
                    if (piece === piece.toUpperCase()) p.classList.add('king');
                    cell.appendChild(p);
                }

                cell.addEventListener('click', onCellClick);
            }

            boardElement.appendChild(cell);
        }
    }
}

async function onCellClick(e) {
    if (gameOver || viewingHistory) return;

    const row = +e.currentTarget.dataset.row;
    const col = +e.currentTarget.dataset.col;
    if (row === 0 || row === 9 || col === 0 || col === 9) return;

    const r = row - 1;
    const c = col - 1;

    if (multiCapture && !possibleMoves.some(m => m[0] === r && m[1] === c)) {
        return;
    }

    const piece = boardState[r][c];

    if (!selected) {
        if (!piece || (piece.toLowerCase() === 'w' ? 'white' : 'black') !== turn) return;
        const caps = await fetchCaptures(r, c);
        if (caps.length) {
            possibleMoves = caps;
            selected = { row: r, col: c, isCapture: true };
        } else {
            const moves = await fetchMoves(r, c);
            if (!moves.length) return;
            possibleMoves = moves;
            selected = { row: r, col: c, isCapture: false };
        }
        renderBoard();
        return;
    }

    if (possibleMoves.some(m => m[0] === r && m[1] === c)) {
        const prev = selected;
        const res = await fetch(`/api/move/${boardId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                start: [prev.row, prev.col],
                end:   [r, c],
                player: turn
            })
        });
        const data = await res.json();
        if (!res.ok) {
            alert(data.detail || 'Неверный ход');
            return;
        }

        boardState = data.board;
        timers = data.timers;
        timerStart = Date.now();
        turn = data.timers.turn;
        updateHistory(data.history);
        setActivePlayer(turn);
        startTimers();

        if (prev.isCapture) {
            const nextCaps = await fetchCaptures(r, c);
            if (nextCaps.length) {
                selected = { row: r, col: c, isCapture: true };
                possibleMoves = nextCaps;
                multiCapture = true;
                renderBoard();
                return;
            }
        }
        multiCapture = false;

        if (data.status) {
            if (data.status === 'white_win')      alert('Белые победили!');
            else if (data.status === 'black_win') alert('Чёрные победили!');
            else if (data.status === 'draw')      alert('Ничья!');
            gameOver = true;
            window.location.href = '/';
            return;
        }
    }

    if (!multiCapture) {
        selected = null;
        possibleMoves = [];
    }
    renderBoard();
}

function updateHistory(history) {
    historyList.innerHTML = '';
    history.forEach((m, i) => {
        const li = document.createElement('li');
        li.textContent = m;
        li.dataset.index = i + 1;
        li.addEventListener('click', onHistoryClick);
        historyList.appendChild(li);
    });
}

async function onHistoryClick(e) {
    const idx = parseInt(e.currentTarget.dataset.index);
    const data = await (await fetch(`/api/snapshot/${boardId}/${idx}`)).json();
    boardState = data;
    clearInterval(timerInterval);
    viewingHistory = true;
    returnButton.style.display = 'block';
    renderBoard();
}

function coord(p) {
    return 'ABCDEFGH'[p.col] + (8 - p.row);
}

function setActivePlayer(p) {
    player1.classList.toggle('active', p === 'white');
    player2.classList.toggle('active', p === 'black');
}

function formatTime(t) {
    const m = Math.floor(t / 60).toString().padStart(2, '0');
    const s = Math.floor(t % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
}

function updateTimerDisplay() {
    const elapsed = (Date.now() - timerStart) / 1000;
    let w = timers.white;
    let b = timers.black;
    if (timers.turn === 'white') w = Math.max(0, w - elapsed);
    else b = Math.max(0, b - elapsed);
    timer1.textContent = formatTime(w);
    timer2.textContent = formatTime(b);
}

function startTimers() {
    clearInterval(timerInterval);
    updateTimerDisplay();
    timerInterval = setInterval(updateTimerDisplay, 1000);
}

fetchBoard();

returnButton.addEventListener('click', () => {
    fetchBoard();
});