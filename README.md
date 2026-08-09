# Ecommerce Platform - Backend

This is the backend API for the Ecommerce platform, built with **Django** and **Django REST Framework (DRF)**.

## Architecture & Core Technologies
- **Django 5 & DRF:** The core web framework and API engine.
- **Django & DRF:** Core web framework and API engine.
- **SimpleJWT:** Handles authentication via stateless JWT tokens. Custom configured to send tokens in `HttpOnly` cookies for enhanced XSS protection.
- **SQLite / PostgreSQL:** (Default configured database)

## Key Features & Implementations

### 1. Authentication & Security
- **HttpOnly Cookies:** Access and refresh tokens are managed strictly via cookies. A custom `CustomJWTAuthentication` class verifies these cookies for protected API endpoints.
- **Authentication:** JWT-based authentication via `SimpleJWT`, with a custom `CustomJWTAuthentication` class used for API endpoints.

### 2. Conversations (Chat API)
- The backend exposes REST endpoints for conversation and message history. Real-time WebSocket-based features were removed; consumers and WebSocket routing are no longer present.

### 3. Shopping Flow
- **Cart & Wishlist:** Fully modeled in `models.py`. API views handle adding/removing products.
- **Checkout & Orders:** Order generation connects to a single `Payment` instance. Fully relational structure where an `Order` has multiple `OrderItem` objects linking to specific `Products`.

### 4. Vendor/Store System
- Products are linked to specific `Store` instances, which are owned by users (Sellers).

## Setup & Running Locally

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Run the Server:**
   Use the standard Django runserver for local API testing:
   ```bash
   python manage.py runserver
   ```

## Key API Endpoints
- `/user_login/` / `/user_register/` - Auth
- `/api/products/` - Product Catalog
- `/cart/` / `/wishlist/` - User Lists
- `/order/` - Order Management
- `/chat/rooms/` - Chat system
-- WebSocket endpoints removed in this backend.
