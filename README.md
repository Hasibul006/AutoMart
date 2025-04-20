# 🚗 AutoMart - E-commerce Web Application

AutoMart is a feature-rich e-commerce platform built with Django. It allows users to browse products, manage carts, and place orders, while admins can manage products, categories, and users.

## 🛠 Features

### 👥 User Roles
- **Admin**:
  - Add, update, or delete products
  - Add new categories
  - Promote users to admin

- **User**:
  - View product listings and detailed pages
  - Add products to cart and manage them
  - Checkout and place orders
  - View and edit profile information

### 🛒 E-Commerce Functionalities
- Product categorization and filtering
- Cart system with quantity management
- Checkout process with payment method selection
- Order summary and history
- Profile section for users

---

## 🧱 Database Models

### `User`
Custom user model with:
- `fullname`, `phone`, `address`, `profile_image`
- `role` (user/admin)

### `Category`
- `name`, `image`

### `Product`
- `name`, `image`, `description`, `price`, `stock`, `company`
- Linked to a `Category`

### `Cart`
- Linked to `User` and `Product`
- Tracks `quantity`, `added_at`, and `checkout` status

### `Order`
- Linked to `User`
- Stores order details including `fullname`, `phone`, `email`, `address`, `payment_method`, `total_price`, and `ordered_at`

### `OrderItem`
- Linked to `Order` and `Product`
- Tracks individual product quantity and price per order

