export function initFloatingLabels() {
    document.querySelectorAll('.input-container input').forEach(input => {
        const container = input.parentElement;
        if (input.value.trim() !== "") {
            container.classList.add('floating');
        }
        input.addEventListener('focus', () => {
            container.classList.add('floating');
        });
        input.addEventListener('blur', () => {
            if (input.value.trim() === "") {
                container.classList.remove('floating');
            }
        });
        input.addEventListener('input', () => {
            if (input.value.trim() !== "") {
                container.classList.add('floating');
            } else if (document.activeElement !== input) {
                container.classList.remove('floating');
            }
        });
    });
}
