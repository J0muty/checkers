document.addEventListener('DOMContentLoaded', () => {
    const root = document.documentElement;
    const icon = document.getElementById('theme-icon');

    const setTheme = theme => {
        if (theme === 'dark') {
            root.classList.add('dark-mode');
            icon.classList.replace('fa-moon', 'fa-sun');
        localStorage.theme = 'dark';
        } else {
            root.classList.remove('dark-mode');
            icon.classList.replace('fa-sun', 'fa-moon');
            localStorage.theme = 'light';
        }
    };

    setTheme(localStorage.theme === 'dark' ? 'dark' : 'light');

    const toggle = document.getElementById('theme-toggle');
    if (toggle) {
        toggle.addEventListener('click', () => {
            setTheme(root.classList.contains('dark-mode') ? 'light' : 'dark');
        });
    }
});
