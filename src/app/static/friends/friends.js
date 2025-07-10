document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('friend-search')
    const friendsList = document.getElementById('friends-list')
    const requestsList = document.getElementById('requests-list')
    const requestsBlock = document.getElementById('requests')
    const resultsList = document.getElementById('results-list')
    const resultsBlock = document.getElementById('results')
    const notification = document.getElementById('notification')

    const showNotification = text => {
        notification.textContent = text
        notification.style.display = 'block'
        setTimeout(() => (notification.style.display = 'none'), 2000)
    }

    async function loadFriends() {
        const res = await fetch('/api/friends')
        if (!res.ok) return
        const data = await res.json()
        friendsList.innerHTML = ''
        data.friends.forEach(u => {
            const li = document.createElement('li')
            li.textContent = u.login
            const btnRemove = document.createElement('button')
            btnRemove.className = 'icon-btn'
            btnRemove.innerHTML = '<i class="fa-solid fa-trash"></i>'
            btnRemove.title = 'Удалить'
            btnRemove.addEventListener('click', async () => {
                await fetch(`/api/friend_request?to_id=${u.id}&action=remove`, { method: 'POST' })
                showNotification('Удалён из друзей')
                loadFriends()
            })
            li.appendChild(btnRemove)
            friendsList.appendChild(li)
        })
        requestsList.innerHTML = ''
        const incoming = data.requests.incoming
        if (incoming.length) {
            requestsBlock.style.display = 'block'
            requestsList.innerHTML = ''
            incoming.forEach(u => {
                const li = document.createElement('li')
                li.textContent = u.login
                const btnAccept = document.createElement('button')
                btnAccept.className = 'icon-btn'
                btnAccept.innerHTML = '<i class="fa-solid fa-check"></i>'
                btnAccept.title = 'Принять'
                btnAccept.addEventListener('click', async () => {
                    await fetch(`/api/friend_request?to_id=${u.id}&action=accept`, { method: 'POST' })
                    showNotification('Заявка принята')
                    loadFriends()
                })
                const btnReject = document.createElement('button')
                btnReject.className = 'icon-btn'
                btnReject.innerHTML = '<i class="fa-solid fa-times"></i>'
                btnReject.title = 'Отклонить'
                btnReject.addEventListener('click', async () => {
                    await fetch(`/api/friend_request?to_id=${u.id}&action=reject`, { method: 'POST' })
                    showNotification('Заявка отклонена')
                    loadFriends()
                })
                const btnGroup = document.createElement('div')
                btnGroup.append(btnAccept, btnReject)
                li.appendChild(btnGroup)
                requestsList.appendChild(li)
            })
        } else {
            requestsBlock.style.display = 'none'
        }
    }

    async function searchUsers(q) {
        const res = await fetch('/api/search_users?q=' + encodeURIComponent(q))
        if (!res.ok) return
        const data = await res.json()
        resultsList.innerHTML = ''
        data.users.forEach(u => {
            const li = document.createElement('li')
            li.textContent = u.login
            const btn = document.createElement('button')
            btn.className = 'icon-btn'
            btn.innerHTML = u.requested ? '<i class="fa-solid fa-minus"></i>' : '<i class="fa-solid fa-plus"></i>'
            btn.addEventListener('click', async () => {
                const action = u.requested ? 'cancel' : 'send'
                await fetch(`/api/friend_request?to_id=${u.id}&action=${action}`, { method: 'POST' })
                showNotification(action === 'send' ? 'Запрос отправлен' : 'Запрос отменён')
                searchUsers(searchInput.value.trim())
                loadFriends()
            })
            li.appendChild(btn)
            resultsList.appendChild(li)
        })
        resultsBlock.style.display = data.users.length ? 'block' : 'none'
    }

    searchInput.addEventListener('input', () => {
        const q = searchInput.value.trim()
        if (!q) {
            resultsBlock.style.display = 'none'
            return
        }
        searchUsers(q)
    })

    loadFriends()
})
