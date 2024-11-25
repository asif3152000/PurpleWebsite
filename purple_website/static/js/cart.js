function toggleCart() {
    const cartPanel = document.getElementById("cart-panel");
    cartPanel.classList.toggle("active");
}

function updateCartPanel(cartItems) {
    const cartItemsContainer = document.getElementById("cart-items-container");
    cartItemsContainer.innerHTML = '';

    cartItems.forEach(item => {
        const cartItem = document.createElement('div');
        cartItem.classList.add('cart-item');
        cartItem.innerHTML = `
            <img src="${item.image || 'images/fallback.png'}" alt="${item.name}" onerror="this.onerror=null; this.src='images/fallback.png';">
            <div class="cart-item-details">
                <h4>${item.name}</h4>
                <p class="product-price">$${item.price.toFixed(2)}</p>
                <button class="remove-item" onclick="removeFromCart('${item.name}')">Remove</button>
                <button class="book-now" onclick="bookNow('${item.name}')">Book Now</button>
            </div>
        `;
        cartItemsContainer.appendChild(cartItem);
    });
}

function addToCart(item) {
    fetch('/add_to_cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
        updateCartPanel(data.cart);
    })
    .catch(error => console.error('Error:', error));
}

function removeFromCart(itemName) {
    fetch('/remove_from_cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: itemName })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
        updateCartPanel(data.cart);
    })
    .catch(error => console.error('Error:', error));
}