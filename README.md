# Django E-Commerce Shop API

A full-featured e-commerce REST API built with Django and Django REST Framework, featuring JWT authentication, product catalog, shopping cart, orders management, reviews system, and seller panel.

## 🚀 Tech Stack

- **Backend Framework**: Django 6.0
- **API Framework**: Django REST Framework 3.16
- **Database**: PostgreSQL 17
- **Cache**: Redis 7
- **Authentication**: JWT (djangorestframework-simplejwt)
- **API Documentation**: Swagger/OpenAPI (drf-yasg)
- **Admin Panel**: Django Jazzmin
- **Containerization**: Docker & Docker Compose
- **WSGI Server**: Gunicorn

## 📦 Features

### Authentication System
- User registration and login with JWT tokens
- Token refresh and blacklist on logout
- User profile management
- Become a seller functionality
- Rate limiting on login (5 attempts/minute)

### Product Catalog
- Categories and products with images
- Product search and filtering
- Sorting by price, date, rating
- Pagination (12 items per page)
- Average ratings and review counts

### Shopping Cart
- Add/remove items from cart
- Update item quantities
- Auto-calculate cart totals
- One cart per user

### Orders Management
- Create orders from cart
- Order history
- Order status tracking (pending/confirmed/shipped/delivered/cancelled)
- Cancel pending orders
- Price snapshot at order time

### Reviews System
- Rate products (1-5 stars)
- Write reviews with comments
- One review per user per product
- Must purchase product before reviewing
- Auto-update product ratings

### Seller Panel
- Create and manage products
- View orders containing seller's products
- Full CRUD operations on own products
- Seller-only permissions

## 🐳 Quick Start with Docker

### Prerequisites
- Docker
- Docker Compose

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd MyPlace
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Update `.env` file with your settings (optional, defaults work for development)

4. Build and run with Docker Compose:
```bash
docker-compose up --build
```

The application will be available at:
- **API**: http://localhost:8000
- **Swagger Documentation**: http://localhost:8000/swagger/
- **Admin Panel**: http://localhost:8000/admin/

5. Create a superuser (in a new terminal):
```bash
docker-compose exec web python manage.py createsuperuser
```

### Stopping the Application
```bash
docker-compose down
```

### Stopping and removing volumes (database data):
```bash
docker-compose down -v
```

## 📚 API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login (returns JWT tokens)
- `POST /api/auth/logout/` - Logout (blacklist token)
- `POST /api/auth/token/refresh/` - Refresh access token
- `GET /api/auth/me/` - Get current user profile
- `PATCH /api/auth/me/` - Update user profile
- `POST /api/auth/become-seller/` - Become a seller

### Products & Categories
- `GET /api/categories/` - List all categories
- `GET /api/categories/{slug}/` - Category details
- `GET /api/products/` - List products (with filters, search, pagination)
- `GET /api/products/{slug}/` - Product details
- `GET /api/products/{slug}/reviews/` - Get product reviews
- `POST /api/products/{slug}/reviews/create/` - Add review (requires auth)

### Shopping Cart
- `GET /api/cart/` - Get user's cart
- `POST /api/cart/` - Add item to cart
- `DELETE /api/cart/` - Clear cart
- `PATCH /api/cart/items/{id}/` - Update item quantity
- `DELETE /api/cart/items/{id}/` - Remove item from cart

### Orders
- `GET /api/orders/` - List user's orders
- `POST /api/orders/` - Create order from cart
- `GET /api/orders/{id}/` - Order details
- `PATCH /api/orders/{id}/` - Cancel order (pending only)

### Seller Panel (Requires seller status)
- `GET /api/seller/products/` - List seller's products
- `POST /api/seller/products/` - Create new product
- `GET /api/seller/products/{id}/` - Product details
- `PUT /api/seller/products/{id}/` - Update product (full)
- `PATCH /api/seller/products/{id}/` - Update product (partial)
- `DELETE /api/seller/products/{id}/` - Delete product
- `GET /api/seller/orders/` - Orders with seller's products

### Reviews
- `DELETE /api/reviews/{id}/` - Delete own review

## 🔧 Development Setup (Without Docker)

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL database and update `.env` file

4. Run migrations:
```bash
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run development server:
```bash
python manage.py runserver
```

## 📊 Database Schema

### Main Models
- **User**: Custom user model with email authentication
- **Category**: Product categories
- **Product**: Products with pricing, stock, ratings
- **ProductImage**: Product images
- **Review**: Product reviews and ratings
- **Cart**: User shopping carts
- **CartItem**: Items in cart
- **Order**: Customer orders
- **OrderItem**: Items in orders

## 🔐 Security Features

- JWT token authentication
- Token blacklisting on logout
- Password validation (min 8 characters)
- Rate limiting on login endpoint
- CORS configuration
- Environment-based secrets
- Seller-only permissions for product management

## 📸 Screenshots

*Coming soon...*

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

Built with ❤️ using Django and DRF

---

For more information, visit the [Swagger Documentation](http://localhost:8000/swagger/) after running the application.
