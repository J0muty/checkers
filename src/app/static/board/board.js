const boardElement = document.getElementById('board');
const historyList = document.getElementById('historyList');

let boardState = [];

const letters = ['', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', ''];
const numbers = ['', '8', '7', '6', '5', '4', '3', '2', '1', ''];

function createBoard() {
    for (let row = 0; row < 10; row++) {
        boardState[row] = [];
        for (let col = 0; col < 10; col++) {
            const cell = document.createElement('div');
            cell.classList.add('square');

            if (row === 0 || row === 9) {
                cell.classList.add('label', row === 0 ? 'label-top' : 'label-bottom');
                cell.textContent = letters[col];
                boardState[row][col] = null;
            } else if (col === 0 || col === 9) {
                cell.classList.add('label', col === 0 ? 'label-left' : 'label-right');
                cell.textContent = numbers[row];
                boardState[row][col] = null;
            } else {
                const r = row - 1;
                const c = col - 1;
                const isDark = (r + c) % 2 !== 0;

                if (isDark) {
                    cell.classList.add('dark');
                } else {
                    cell.classList.add('light');
                }

                if (!isDark && r < 3) {
                    addPiece(cell, 'black');
                    boardState[row][col] = 'black';
                } else if (isDark && r > 4) {
                    addPiece(cell, 'white');
                    boardState[row][col] = 'white';
                } else {
                    boardState[row][col] = null;
                }
            }
            boardElement.appendChild(cell);
        }
    }
}

function addPiece(square, color) {
    const piece = document.createElement('div');
    piece.classList.add('piece', color);
    square.appendChild(piece);
}

createBoard();
