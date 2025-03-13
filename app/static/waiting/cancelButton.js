export function initCancelButton(cancelButton) {
    cancelButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/waiting/cancel', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();
            if (data.message === "Поиск отменён") {
                window.location.href = '/';
            } else {
                alert(data.message);
            }
        } catch (error) {
            console.error('Ошибка при отмене поиска:', error);
        }
    });
}