export function updateButtonText() {
    const buttons = document.querySelectorAll('.buttons button');
    if (window.innerWidth <= 230) {
        buttons.forEach(button => {
            if (button.textContent.includes("Одиночная игра")) {
                button.textContent = "Одиночная";
            } else if (button.textContent.includes("Сетевая игра")) {
                button.textContent = "Сетевая";
            }
        });
    } else {
        buttons.forEach(button => {
            if (button.textContent === "Одиночная") {
                button.textContent = "Одиночная игра";
            } else if (button.textContent === "Сетевая") {
                button.textContent = "Сетевая игра";
            }
        });
    }
}
