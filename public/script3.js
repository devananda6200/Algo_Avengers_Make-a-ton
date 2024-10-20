fetch('content.json')
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        const itemList = document.getElementById('item-list');
        data.items.forEach(item => {
            const li = document.createElement('li');
            li.textContent = `${item.name} - $${item.price}`;
            itemList.appendChild(li);
        });
    })
    .catch(error => console.error('There was a problem with the fetch operation:', error));
