document.addEventListener('DOMContentLoaded', () => {
    const searchInput   = document.getElementById('friend-search');
    const friendsList   = document.getElementById('friends-list');
    const requestsList  = document.getElementById('requests-list');
    const requestsBlock = document.getElementById('requests');
    const friendsBlock  = document.getElementById('friends');
    const resultsList   = document.getElementById('results-list');
    const resultsBlock  = document.getElementById('results');

    function showNotification(message, duration = 2500) {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.style.setProperty('--toast-duration', duration + 'ms');
        toast.textContent = message;
        container.appendChild(toast);
        setTimeout(() => {
            toast.remove();
            if (!container.children.length) container.remove();
        }, duration + 300);
    }

    window.showNotification = showNotification;

    async function loadFriends() {
        try {
            const res = await fetch('/api/friends');
            if (!res.ok) return;
            const data = await res.json();

            friendsList.innerHTML = '';
            data.friends.forEach(u => {
                const li = document.createElement('li');
                li.textContent = u.login;

                const btnRemove = document.createElement('button');
                btnRemove.className = 'icon-btn';
                btnRemove.innerHTML = '<i class="fa-solid fa-trash"></i>';
                btnRemove.title = 'Удалить';
                btnRemove.addEventListener('click', async () => {
                    await fetch(`/api/friend_request?to_id=${u.id}&action=remove`, { method: 'POST' });
                    showNotification('Удалён из друзей');
                    loadFriends();
                });

                li.appendChild(btnRemove);
                friendsList.appendChild(li);
            });

            requestsList.innerHTML = '';
            const incoming = data.requests.incoming;

            if (incoming.length) {
                requestsBlock.style.display = 'block';
                incoming.forEach(u => {
                    const li = document.createElement('li');
                    li.textContent = u.login;

                    const btnAccept = document.createElement('button');
                    btnAccept.className = 'icon-btn';
                    btnAccept.innerHTML = '<i class="fa-solid fa-check"></i>';
                    btnAccept.title = 'Принять';
                    btnAccept.addEventListener('click', async () => {
                        await fetch(`/api/friend_request?to_id=${u.id}&action=accept`, { method: 'POST' });
                        showNotification('Заявка принята');
                        loadFriends();
                    });

                    const btnReject = document.createElement('button');
                    btnReject.className = 'icon-btn';
                    btnReject.innerHTML = '<i class="fa-solid fa-times"></i>';
                    btnReject.title = 'Отклонить';
                    btnReject.addEventListener('click', async () => {
                        await fetch(`/api/friend_request?to_id=${u.id}&action=reject`, { method: 'POST' });
                        showNotification('Заявка отклонена');
                        loadFriends();
                    });

                    const btnGroup = document.createElement('div');
                    btnGroup.append(btnAccept, btnReject);
                    li.appendChild(btnGroup);
                    requestsList.appendChild(li);
                });
            } else {
                requestsBlock.style.display = 'none';
            }
        } catch (err) {
            console.error('Failed to load friends:', err);
        }
    }

    async function searchUsers(q) {
        try {
            const res = await fetch('/api/search_users?q=' + encodeURIComponent(q));
            if (!res.ok) return;
            const data = await res.json();

            resultsList.innerHTML = '';
            data.users.forEach(u => {
                const li = document.createElement('li');
                li.textContent = u.login;

                const btn = document.createElement('button');
                btn.className = 'icon-btn';
                btn.innerHTML = u.requested ? '<i class="fa-solid fa-minus"></i>' : '<i class="fa-solid fa-plus"></i>';
                btn.addEventListener('click', async () => {
                    const action = u.requested ? 'cancel' : 'send';
                    await fetch(`/api/friend_request?to_id=${u.id}&action=${action}`, { method: 'POST' });
                    showNotification(action === 'send' ? 'Запрос отправлен' : 'Запрос отменён');
                    searchUsers(searchInput.value.trim());
                    loadFriends();
                });

                li.appendChild(btn);
                resultsList.appendChild(li);
            });

            resultsBlock.style.display = data.users.length ? 'block' : 'none';
        } catch (err) {
            console.error('Failed to search users:', err);
        }
    }

    searchInput.addEventListener('input', () => {
        const q = searchInput.value.trim();
        if (q) {
            friendsBlock.style.display  = 'none';
            requestsBlock.style.display = 'none';
            searchUsers(q);
        } else {
            resultsBlock.style.display  = 'none';
            friendsBlock.style.display  = 'block';
            loadFriends();
        }
    });

    loadFriends();
});
