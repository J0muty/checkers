export function animateButtons() {
    const buttons = document.querySelectorAll('.buttons button');
    buttons.forEach((button, index) => {
        setTimeout(() => {
            button.style.opacity = 1;
            button.style.transform = "translateY(0)";
        }, 200 * index);
    });
}
