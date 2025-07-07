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

    const rand = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;
    const winsVal = rand(0, 20);
    const drawsVal = rand(0, 20);
    const lossesVal = rand(0, 20);
    const totalVal = winsVal + drawsVal + lossesVal;

    document.getElementById('wins').textContent = winsVal;
    document.getElementById('draws').textContent = drawsVal;
    document.getElementById('losses').textContent = lossesVal;
    document.getElementById('total-games').textContent = totalVal;

    const ctx = document.getElementById('stats-chart').getContext('2d');
    let statsChart = createChart(ctx);

    function createChart(ctx) {
        const root = getComputedStyle(document.documentElement);
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Победы', 'Ничьи', 'Поражения'],
                datasets: [{
                    data: [winsVal, drawsVal, lossesVal],
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
