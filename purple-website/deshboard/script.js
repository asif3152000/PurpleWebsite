// Sample Data
const products = [
  { name: "Laptop", price: "$1000", stock: 10 },
  { name: "Headphones", price: "$50", stock: 100 },
];

const orders = [
  { id: "001", product: "Laptop", status: "Shipped", date: "2024-11-20" },
  { id: "002", product: "Headphones", status: "Pending", date: "2024-11-22" },
];

// Load Products
function loadProducts() {
  const productList = document.getElementById("product-list");
  productList.innerHTML = "";
  products.forEach((product, index) => {
    productList.innerHTML += `
      <tr>
        <td>${product.name}</td>
        <td>${product.price}</td>
        <td>${product.stock}</td>
        <td>
          <button onclick="editProduct(${index})">Edit</button>
          <button onclick="deleteProduct(${index})">Delete</button>
        </td>
      </tr>
    `;
  });
}

// Load Orders
function loadOrders() {
  const orderList = document.getElementById("order-list");
  orderList.innerHTML = "";
  orders.forEach(order => {
    orderList.innerHTML += `
      <tr>
        <td>${order.id}</td>
        <td>${order.product}</td>
        <td>${order.status}</td>
        <td>${order.date}</td>
      </tr>
    `;
  });
}

// Add Product
function addProduct() {
  const name = prompt("Enter product name:");
  const price = prompt("Enter product price:");
  const stock = prompt("Enter product stock:");
  if (name && price && stock) {
    products.push({ name, price: `$${price}`, stock: Number(stock) });
    loadProducts();
  }
}

// Edit Product
function editProduct(index) {
  const product = products[index];
  const name = prompt("Edit product name:", product.name);
  const price = prompt("Edit product price:", product.price.slice(1));
  const stock = prompt("Edit product stock:", product.stock);
  if (name && price && stock) {
    products[index] = { name, price: `$${price}`, stock: Number(stock) };
    loadProducts();
  }
}

// Delete Product
function deleteProduct(index) {
  if (confirm("Are you sure you want to delete this product?")) {
    products.splice(index, 1);
    loadProducts();
  }
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  loadProducts();
  loadOrders();
});
