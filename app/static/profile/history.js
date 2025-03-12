export function initHistory() {
    const historyBody = document.getElementById('historyBody');
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    const hideBtn = document.getElementById('hideBtn');

    const historyData = [
        { date: "2025-03-10", rating: 1234, result: "Победа" },
        { date: "2025-03-08", rating: 1220, result: "Поражение" }
    ];

    function getRandomGame() {
        const day = ("0" + (Math.floor(Math.random() * 28) + 1)).slice(-2);
        const rating = Math.floor(Math.random() * 100) + 1200;
        const result = Math.random() > 0.5 ? "Победа" : "Поражение";
        return { date: `2025-03-${day}`, rating, result };
    }

    historyData.push({ date: "2025-03-10", rating: 1234, result: "Победа" });
    historyData.push({ date: "2025-03-08", rating: 1220, result: "Поражение" });
    for (let i = 0; i < 10; i++) {
        historyData.push(getRandomGame());
    }

    if (historyData.length === 0) {
        loadMoreBtn.style.display = "none";
        hideBtn.style.display = "none";
        return;
    }

    const rowsPerPage = 5;
    let currentPage = 0;

    function renderRows() {
        const start = currentPage * rowsPerPage;
        const end = start + rowsPerPage;
        const rows = historyData.slice(start, end);

        rows.forEach(game => {
            const tr = document.createElement('tr');
            tr.style.opacity = 0;

            const tdDate = document.createElement('td');
            tdDate.textContent = game.date;
            const tdRating = document.createElement('td');
            tdRating.textContent = game.rating;
            const tdResult = document.createElement('td');
            tdResult.textContent = game.result;

            tr.appendChild(tdDate);
            tr.appendChild(tdRating);
            tr.appendChild(tdResult);
            historyBody.appendChild(tr);

            setTimeout(() => {
                tr.style.transition = "opacity 0.5s ease";
                tr.style.opacity = 1;
            }, 50);
        });

        currentPage++;
        loadMoreBtn.style.display = (historyData.length > rowsPerPage && currentPage * rowsPerPage < historyData.length) ? "block" : "none";
    }

    renderRows();

    loadMoreBtn.addEventListener('click', () => {
        renderRows();
        hideBtn.style.display = "block";
    });

    hideBtn.addEventListener('click', () => {
        const rows = Array.from(historyBody.children);
        const rowsToRemove = rows.slice(rowsPerPage);

        rowsToRemove.forEach(row => {
            row.style.transition = "opacity 0.3s ease, transform 0.3s ease";
            row.style.transformOrigin = "top";
            row.offsetHeight;
            row.style.opacity = 0;
            row.style.transform = "scaleY(0)";
        });

        setTimeout(() => {
            rowsToRemove.forEach(row => {
                if (row.parentNode === historyBody) {
                    historyBody.removeChild(row);
                }
            });
            currentPage = 1;
            loadMoreBtn.style.display = (historyData.length > rowsPerPage && currentPage * rowsPerPage < historyData.length) ? "block" : "none";
            hideBtn.style.display = "none";
        }, 300);
    });
}
