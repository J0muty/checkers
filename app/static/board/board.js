window.addEventListener('load', function() {
    const canvas = document.getElementById("board");
    const ctx = canvas.getContext("2d");

    function adjustCanvas() {
        const size = 400;
        canvas.width = size;
        canvas.height = size;
    }

    function drawBoard() {
        const size = canvas.width;
        const cellSize = size / 8;
        for (let i = 0; i < 8; i++) {
            for (let j = 0; j < 8; j++) {
                if ((i + j) % 2 === 1) {
                    ctx.fillStyle = "#971616";
                } else {
                    ctx.fillStyle = "#ffffff";
                }
                ctx.fillRect(j * cellSize, i * cellSize, cellSize, cellSize);
            }
        }
        ctx.fillStyle = "#f0f0f0";
        let fontSize = Math.max(12, Math.min(Math.round(cellSize / 3), 24));
        ctx.font = fontSize + "px Arial";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        const letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
        const sizeOffset = cellSize * 0.3 - cellSize;
        for (let i = 0; i < 8; i++) {
            let x = (i + 0.5) * cellSize;
            ctx.fillText(letters[i], x, -cellSize * 0.3 + cellSize);
        }
        for (let i = 0; i < 8; i++) {
            let x = (i + 0.5) * cellSize;
            ctx.fillText(letters[i], x, canvas.height + sizeOffset);
        }
        ctx.textAlign = "left";
        ctx.textBaseline = "top";
        for (let i = 0; i < 8; i++) {
            let y = i * cellSize + cellSize / 2;
            ctx.fillText((8 - i).toString(), cellSize * 0.1, y);
        }
        ctx.textAlign = "right";
        for (let i = 0; i < 8; i++) {
            let y = i * cellSize + cellSize / 2;
            ctx.fillText((8 - i).toString(), canvas.width - cellSize * 0.1, y);
        }
    }

    function drawPieces(pieces) {
        const size = canvas.width;
        const cellSize = size / 8;

        pieces.forEach(piece => {
            let fillColor = piece.color === 1 ? "#ffffff" : "#000000";
            let cx = piece.x * cellSize + cellSize / 2;
            let cy = piece.y * cellSize + cellSize / 2;
            let radius = cellSize * 0.3;

            ctx.fillStyle = fillColor;
            ctx.beginPath();
            ctx.arc(cx, cy, radius, 0, 2 * Math.PI);
            ctx.fill();
        });
    }

    function init() {
        adjustCanvas();
        drawBoard();
        drawPieces(piecesData);
    }

    init();

    document.getElementById("give-up-button").addEventListener("click", async function() {
        try {
            let response = await fetch("/give_up", {
                method: "POST"
            });
            let data = await response.json();
            window.location.href = "/";
        } catch (error) {
            console.error("Ошибка при сдаче:", error);
        }
    });

    document.getElementById("main-menu-button").addEventListener("click", function() {
        window.location.href = "/";
    });

    document.getElementById("main-menu-button-modal").addEventListener("click", function() {
        window.location.href = "/";
    });
});
