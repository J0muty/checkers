document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('theme-toggle');
    const icon = document.getElementById('theme-icon');
    const body = document.body;

    const setTheme = theme => {
        if (theme === 'dark') {
            body.classList.add('dark-mode');
            icon.classList.replace('fa-moon', 'fa-sun');
        localStorage.theme = 'dark';
        } else {
            body.classList.remove('dark-mode');
            icon.classList.replace('fa-sun', 'fa-moon');
            localStorage.theme = 'light';
        }
    };

    setTheme(localStorage.theme === 'dark' ? 'dark' : 'light');

    toggle.addEventListener('click', () => {
        setTheme(body.classList.contains('dark-mode') ? 'light' : 'dark');
    });
});
