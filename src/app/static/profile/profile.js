async function loadStats() {
    try {
        const res = await fetch('/api/stats');
        if (!res.ok) return;
        const data = await res.json();
        document.getElementById('total-games').textContent = data.total_games;
        document.getElementById('wins').textContent = data.wins;
        document.getElementById('draws').textContent = data.draws;
        document.getElementById('losses').textContent = data.losses;
        document.getElementById('elo').textContent = data.elo;
        document.getElementById('rank').textContent = data.rank;
        const icon = document.querySelector('.rank-icon');
        if (icon) {
            icon.src = `/static/images/profile/ranks/${encodeURIComponent(data.rank)}.png`;
            icon.alt = data.rank;
        }
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('total-games')) {
        loadStats();
    }
});
