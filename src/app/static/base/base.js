document.addEventListener('DOMContentLoaded', () => {
    const root = document.documentElement;
    const icon = document.getElementById('theme-icon');

    const setTheme = theme => {
        if (theme === 'dark') {
            root.classList.add('dark-mode');
            if (icon) icon.classList.replace('fa-moon', 'fa-sun');
        } else {
            root.classList.remove('dark-mode');
            if (icon) icon.classList.replace('fa-sun', 'fa-moon');
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
