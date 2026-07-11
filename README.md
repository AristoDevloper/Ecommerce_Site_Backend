# Ecommerce Platform - Backend

This is the backend API and websocket server for the Ecommerce platform, built with **Django**, **Django REST Framework (DRF)**, and **Django Channels**.

## Architecture & Core Technologies
- **Django 5 & DRF:** The core web framework and API engine.
- **Django Channels & Daphne:** Provides ASGI support for real-time WebSocket connections (used for the live messaging system).
- **SimpleJWT:** Handles authentication via stateless JWT tokens. Custom configured to send tokens in `HttpOnly` cookies for enhanced XSS protection.
- **SQLite / PostgreSQL:** (Default configured database)

## Key Features & Implementations

### 1. Authentication & Security
- **HttpOnly Cookies:** Access and refresh tokens are managed strictly via cookies. A custom `CustomJWTAuthentication` class verifies these cookies for protected API endpoints.
- **WebSocket Auth:** A custom `JWTAuthMiddlewareStack` in `middleware.py` intercepts WebSocket connection requests and authenticates users using the same `HttpOnly` cookie strategy.

### 2. Live Conversations (Real-Time Chat)
- **WebSockets:** Built using Django Channels.
- Consumers (`consumers.py`) manage connections using `AsyncWebsocketConsumer`. They verify that:
  - The conversation UUID actually exists.
  - The connecting user is a participant (buyer or seller).
- Messages are broadcasted in real-time to specific `room_groups` and saved sequentially into the database.
- A REST API (`ChatRoomView` and `ChatMessageView`) is used to fetch historical message data and generate new rooms between a user and a store.

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

3. **Run the Server (ASGI for WebSockets):**
   *Do not use the standard runserver if testing WebSockets.* Use Daphne:
   ```bash
   daphne -p 8000 Ecommerce_Site_Backend.asgi:application
   ```
   Or standard runserver (for API only):
   ```bash
   python manage.py runserver
   ```

## Key API Endpoints
- `/user_login/` / `/user_register/` - Auth
- `/api/products/` - Product Catalog
- `/cart/` / `/wishlist/` - User Lists
- `/order/` - Order Management
- `/chat/rooms/` - Chat system
- `ws://localhost:8000/ws/chat/<room_name>/<uuid>/` - WebSocket Connection
