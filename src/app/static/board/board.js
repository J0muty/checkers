const boardElement = document.getElementById('board');
const historyList = document.getElementById('historyList');
const letters = ['', 'A','B','C','D','E','F','G','H',''];
const numbers = ['', '8','7','6','5','4','3','2','1',''];

let boardState = [];
let selected = null;
let possibleMoves = [];
let turn = 'white';

async function fetchBoard() {
    boardState = await (await fetch('/api/board')).json();
    renderBoard();
}

async function fetchMoves(r, c) {
    return await (await fetch(
        `/api/moves?row=${r}&col=${c}&player=${turn}`
    )).json();
}

async function fetchCaptures(r, c) {
    return await (await fetch(
        `/api/captures?row=${r}&col=${c}&player=${turn}`
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
                cell.classList.add(
                    'label',
                    row === 0 ? 'label-top' : 'label-bottom'
                );
                cell.textContent = letters[col];
            } else if (col === 0 || col === 9) {
                cell.classList.add(
                    'label',
                    col === 0 ? 'label-left' : 'label-right'
                );
                cell.textContent = numbers[row];
            } else {
                const r = row - 1;
                const c = col - 1;
                cell.classList.add((r + c) % 2 ? 'dark' : 'light');

                if (
                    selected &&
                    selected.row === r &&
                    selected.col === c
                ) {
                    cell.classList.add('selected');
                }
                if (
                    possibleMoves.some(
                        m => m[0] === r && m[1] === c
                    )
                ) {
                    cell.classList.add('highlight');
                }

                const piece = boardState[r][c];
                if (piece) {
                    const p = document.createElement('div');
                    p.classList.add(
                        'piece',
                        piece.toLowerCase() === 'w'
                            ? 'white'
                            : 'black'
                    );
                    if (piece === piece.toUpperCase()) {
                        p.classList.add('king');
                    }
                    cell.appendChild(p);
                }
            }

            cell.addEventListener('click', onCellClick);
            boardElement.appendChild(cell);
        }
    }
}

async function onCellClick(e) {
    const row = +e.currentTarget.dataset.row;
    const col = +e.currentTarget.dataset.col;
    if (
        row === 0 ||
        row === 9 ||
        col === 0 ||
        col === 9
    )
        return;

    const r = row - 1;
    const c = col - 1;
    const piece = boardState[r][c];

    if (!selected) {
        if (
            !piece ||
            (piece.toLowerCase() === 'w'
                ? 'white'
                : 'black') !== turn
        )
            return;
        const caps = await fetchCaptures(r, c);
        if (caps.length) {
            selected = { row: r, col: c };
            possibleMoves = caps;
        } else {
            const moves = await fetchMoves(r, c);
            if (!moves.length) return;
            selected = { row: r, col: c };
            possibleMoves = moves;
        }
        renderBoard();
        return;
    }

    if (
        possibleMoves.some(
            m => m[0] === r && m[1] === c
        )
    ) {
        const prev = { ...selected };
        const res = await fetch('/api/move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                start: [selected.row, selected.col],
                end: [r, c],
                player: turn
            })
        });
        if (res.ok) {
            boardState = await res.json();
            addToHistory(prev, { row: r, col: c });
            const wasCapture =
                Math.abs(r - prev.row) > 1;
            if (wasCapture) {
                const nextCaps = await fetchCaptures(
                    r,
                    c
                );
                if (nextCaps.length) {
                    selected = { row: r, col: c };
                    possibleMoves = nextCaps;
                    renderBoard();
                    return;
                }
            }
            turn = turn === 'white' ? 'black' : 'white';
        }
    }

    selected = null;
    possibleMoves = [];
    renderBoard();
}

function addToHistory(s, e) {
    const li = document.createElement('li');
    li.textContent = `${coord(s)} → ${coord(e)}`;
    historyList.appendChild(li);
}

function coord(p) {
    return 'ABCDEFGH'[p.col] + (8 - p.row);
}

fetchBoard();

