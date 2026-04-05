# Bazar E-Commerce Platform - Quick Start Guide

## Project Overview

Full-stack e-commerce platform with Django REST API backend and Vue.js 3 frontend.

## Architecture

```
MyPlace/                    # Django Backend
├── products/              # Product catalog & reviews
├── users/                 # Authentication & user management
├── orders/                # Cart & orders
└── shop/                  # Main settings

bazar-frontend/            # Vue.js Frontend
├── src/
│   ├── components/       # Reusable UI components
│   ├── views/            # Page components
│   ├── stores/           # Pinia state management
│   ├── services/         # API integration
│   └── router/           # Navigation
```

## Prerequisites

- Python 3.12+
- Node.js 16+
- PostgreSQL 17
- Redis 7 (optional, for caching)

## Backend Setup

### 1. Install Dependencies

```bash
cd MyPlace
pip install -r requirements.txt
```

### 2. Configure Database

Create PostgreSQL database:
```sql
CREATE DATABASE shop_db;
CREATE USER shop_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE shop_db TO shop_user;
```

Update `shop/settings.py` or use environment variables:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'shop_db',
        'USER': 'shop_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

### 5. Load Mock Data (Optional)

```bash
python manage.py loaddata categories products
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Backend will be available at: http://127.0.0.1:8000

- Admin Panel: http://127.0.0.1:8000/admin/
- API Docs: http://127.0.0.1:8000/swagger/

## Frontend Setup

### 1. Install Dependencies

```bash
cd bazar-frontend
npm install
```

### 2. Configure API URL

Create `.env` file:
```
VUE_APP_API_URL=http://127.0.0.1:8000/api
```

### 3. Run Development Server

```bash
npm run serve
```

Frontend will be available at: http://localhost:8080

## Docker Setup (Alternative)

### 1. Build and Run

```bash
cd MyPlace
docker-compose up --build
```

This will start:
- Django backend on port 8000
- PostgreSQL on port 5432
- Redis on port 6379

### 2. Run Migrations

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## Testing the Application

### 1. Register a New User
- Go to http://localhost:8080/register
- Fill in email, name, and password
- Submit to create account

### 2. Browse Products
- Visit http://localhost:8080/catalog
- Use filters and search
- Click on products to view details

### 3. Add to Cart
- Click "Add to Cart" on any product
- View cart at http://localhost:8080/cart
- Update quantities or remove items

### 4. Create Order
- In cart, click "Checkout"
- Enter delivery address and phone
- Submit order

### 5. Become a Seller
- Go to http://localhost:8080/profile
- Click "Become a Seller"
- Access seller panel at http://localhost:8080/seller

### 6. Manage Products (Seller)
- Create new products
- Edit existing products
- Delete products
- View orders

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/token/refresh/` - Refresh token
- `GET /api/auth/me/` - Get profile
- `PATCH /api/auth/me/` - Update profile
- `POST /api/auth/become-seller/` - Become seller

### Products
- `GET /api/products/` - List products
- `GET /api/products/{slug}/` - Product details
- `GET /api/products/{slug}/reviews/` - Product reviews
- `POST /api/products/{slug}/reviews/create/` - Create review
- `GET /api/categories/` - List categories

### Cart & Orders
- `GET /api/cart/` - Get cart
- `POST /api/cart/` - Add to cart
- `PATCH /api/cart/items/{id}/` - Update cart item
- `DELETE /api/cart/items/{id}/` - Remove from cart
- `DELETE /api/cart/` - Clear cart
- `GET /api/orders/` - List orders
- `POST /api/orders/` - Create order

### Seller
- `GET /api/seller/products/` - Seller's products
- `POST /api/seller/products/` - Create product
- `PATCH /api/seller/products/{id}/` - Update product
- `DELETE /api/seller/products/{id}/` - Delete product
- `GET /api/seller/orders/` - Seller's orders

## Features

### User Features
✅ User registration and authentication
✅ JWT token-based security with auto-refresh
✅ Product browsing with search and filters
✅ Product details with images and reviews
✅ Shopping cart management
✅ Order placement and tracking
✅ Review submission (after purchase)
✅ Profile management

### Seller Features
✅ Seller registration
✅ Product CRUD operations
✅ Order management
✅ Product categorization

### Admin Features
✅ Django admin panel with Jazzmin theme
✅ User management
✅ Product moderation
✅ Order management
✅ Category management

## Technology Stack

### Backend
- Django 6.0
- Django REST Framework
- PostgreSQL 17
- Redis 7
- JWT Authentication (simplejwt)
- Swagger/OpenAPI (drf-yasg)
- Docker & Docker Compose

### Frontend
- Vue.js 3 (Composition API)
- Pinia (State Management)
- Vue Router
- Axios (HTTP Client)
- Tailwind CSS
- Vite (Build Tool)

## Project Structure

### Backend Models
- **User**: Custom user model with email authentication
- **Category**: Product categories
- **Product**: Product catalog with images and ratings
- **Review**: Product reviews with ratings
- **Cart**: Shopping cart
- **CartItem**: Cart items
- **Order**: Customer orders
- **OrderItem**: Order line items

### Frontend Pages
- **HomePage**: Landing page with featured products
- **CatalogPage**: Product listing with filters
- **ProductPage**: Product details and reviews
- **CartPage**: Shopping cart
- **OrdersPage**: Order history
- **ProfilePage**: User profile management
- **SellerPage**: Seller dashboard
- **LoginPage**: User login
- **RegisterPage**: User registration

## Development Tips

### Backend
- Use Django shell for testing: `python manage.py shell`
- Check migrations: `python manage.py showmigrations`
- Create migrations: `python manage.py makemigrations`
- Run tests: `python manage.py test`

### Frontend
- Hot reload is enabled in development
- Use Vue DevTools browser extension for debugging
- Check console for API errors
- Pinia DevTools for state inspection

## Troubleshooting

### CORS Issues
Ensure `django-cors-headers` is installed and configured in `settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
]
```

### JWT Token Issues
- Check token expiration in settings
- Verify token is being sent in Authorization header
- Check browser localStorage for tokens

### Database Connection
- Verify PostgreSQL is running
- Check database credentials
- Ensure database exists

### Frontend Build Issues
- Clear node_modules: `rm -rf node_modules && npm install`
- Clear cache: `npm cache clean --force`
- Check Node.js version: `node --version`

## Production Deployment

### Backend
1. Set `DEBUG = False`
2. Configure `ALLOWED_HOSTS`
3. Use environment variables for secrets
4. Set up static file serving
5. Use production WSGI server (Gunicorn)
6. Enable HTTPS

### Frontend
1. Build for production: `npm run build`
2. Serve `dist/` folder with nginx or similar
3. Configure API URL for production
4. Enable gzip compression
5. Set up CDN for static assets

## Support

For issues and questions:
- Backend API docs: http://127.0.0.1:8000/swagger/
- Check Django logs for backend errors
- Check browser console for frontend errors
