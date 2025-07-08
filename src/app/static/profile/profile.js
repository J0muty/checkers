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
    } catch (e) {
        console.error('Failed to load stats:', e);
    }
}
document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebarToggle');
    const closeBtn = document.getElementById('sidebarClose');
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');

    toggleBtn.addEventListener('click', () => sidebar.classList.toggle('open'));
    closeBtn.addEventListener('click', () => sidebar.classList.remove('open'));

    if (localStorage.theme === 'dark') {
        document.documentElement.classList.add('dark-mode');
        themeIcon.classList.replace('fa-moon', 'fa-sun');
    }

    themeToggle.addEventListener('click', () => {
        const isDark = document.documentElement.classList.toggle('dark-mode');
        localStorage.theme = isDark ? 'dark' : 'light';
        themeIcon.classList.toggle('fa-moon');
        themeIcon.classList.toggle('fa-sun');
    });
    loadStats();
});
