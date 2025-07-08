document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.getElementById('sidebarToggle');
    const closeBtn = document.getElementById('sidebarClose');
    const themeToggle = document.getElementById('theme-toggle');
    const icon = document.getElementById('theme-icon');

    toggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });
    closeBtn.addEventListener('click', () => {
        sidebar.classList.remove('open');
    });
    if (localStorage.theme === 'dark') {
        document.documentElement.classList.add('dark-mode');
        icon.classList.replace('fa-moon', 'fa-sun');
    }
    themeToggle.addEventListener('click', () => {
        const dark = document.documentElement.classList.toggle('dark-mode');
        localStorage.theme = dark ? 'dark' : 'light';
        icon.classList.toggle('fa-moon');
        icon.classList.toggle('fa-sun');
        updateChartColors();
    });

    const ctx = document.getElementById('stats-chart').getContext('2d');
    let statsChart = createChart(ctx);

    async function loadStats() {
        try {
            const res = await fetch('/api/stats');
            if (!res.ok) return;
            const data = await res.json();
            document.getElementById('wins').textContent = data.wins;
            document.getElementById('draws').textContent = data.draws;
            document.getElementById('losses').textContent = data.losses;
            document.getElementById('total-games').textContent = data.total_games;
            document.getElementById('elo').textContent = data.elo;
            document.getElementById('rank').textContent = data.rank;
            statsChart.data.datasets[0].data = [data.wins, data.draws, data.losses];
            statsChart.update();
        } catch (e) {
            console.error('Failed to load stats', e);
        }
    }

    loadStats();

    function createChart(ctx) {
        const root = getComputedStyle(document.documentElement);
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Победы', 'Ничьи', 'Поражения'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: [
                        root.getPropertyValue('--accent-color').trim(),
                        root.getPropertyValue('--button-color').trim(),
                        root.getPropertyValue('--secondary-text-color').trim()
                    ],
                    hoverOffset: 8,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: root.getPropertyValue('--text-color').trim(),
                            font: { family: root.getPropertyValue('--font-family').trim() }
                        }
                    }
                },
                cutout: '60%'
            }
        });
    }

    function updateChartColors() {
        const root = getComputedStyle(document.documentElement);
        statsChart.options.plugins.legend.labels.color = root.getPropertyValue('--text-color').trim();
        statsChart.data.datasets[0].backgroundColor = [
            root.getPropertyValue('--accent-color').trim(),
            root.getPropertyValue('--button-color').trim(),
            root.getPropertyValue('--secondary-text-color').trim()
        ];
        statsChart.update();
    }
});
