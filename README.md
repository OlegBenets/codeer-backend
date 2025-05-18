# Codeer Backend

## Description  
**Codeer** is a Django REST Framework (DRF) application designed as a freelance IT services platform.  
Users can register, create service offers, place orders for available offers, and submit reviews.

---

## Features

- User registration and authentication  
- Create, update, and manage service offers  
- Place and manage orders  
- Submit and manage reviews  
- Retrieve general platform and user profile information  
- Admin panel for managing data  

---

## Installation

### Prerequisites

- Python 3.10 or higher  
- pip package manager  
- Virtual environment recommended  

### Setup Instructions

1. Clone the repository  
```bash
git clone https://github.com/OlegBenets/codeer-backend.git
cd codeer-backend/Backend
```

### Create and activate a virtual environment

```bash
python -m venv venv
# On Linux/macOS
source venv/bin/activate
# On Windows
venv\Scripts\activate

pip install -r requirements.txt
```

### Apply migrations

```bash
python manage.py migrate
```

### Start the development server
```bash
python manage.py runserver
```
- API is accessible at: http://127.0.0.1:8000/

## API Endpoints

### Offers
- `GET /api/offers/`  
  List all offers with filtering and search.

- `POST /api/offers/`  
  Create a new offer.

- `GET /api/offers/{id}/`  
  Get details of a specific offer.

- `PATCH /api/offers/{id}/`  
  Update an offer.

- `DELETE /api/offers/{id}/`  
  Delete an offer.

- `GET /api/offers/offerdetails/{id}/`  
  Get details for a specific offer detail.

---

### Orders
- `GET /api/orders/`  
  Retrieve orders for the logged-in user.

- `POST /api/orders/`  
  Place a new order.

- `GET /api/orders/{id}/`  
  Get details of a specific order.

- `PATCH /api/orders/{id}/`  
  Update an order’s status.

- `DELETE /api/orders/{id}/`  
  Delete an order (admin only).

- `GET /api/orders/order-count/{business_user_id}/`  
  Count active orders for a business user.

- `GET /api/orders/completed-order-count/{business_user_id}/`  
  Count completed orders for a business user.

---

### Reviews
- `GET /api/reviews/`  
  List all reviews.

- `POST /api/reviews/`  
  Create a new review.

- `GET /api/reviews/{id}/`  
  Get details of a specific review.

- `PATCH /api/reviews/{id}/`  
  Update a review.

- `DELETE /api/reviews/{id}/`  
  Delete a review.

---

### User Profiles
- `GET /api/profiles/{id}/`  
  Retrieve a user profile.

- `PATCH /api/profiles/{id}/`  
  Update user profile.

- `GET /api/profiles/business/`  
  List all business users.

- `GET /api/profiles/customer/`  
  List all customer profiles.

---

### General Information
- `GET /api/base-info/`  
  Retrieve platform-wide information.

---

### Authentication
- `POST /api/login/`  
  User login.

- `POST /api/registration/`  
  User registration.

---

## Usage Notes
- Token-based authentication (DRF Token Authentication) is used.  
- Media files are stored and served from the `/media/` directory.  
- Use API testing tools like Postman or Insomnia to explore endpoints.

---

## Development Environment
- Django 5.x  
- Django REST Framework  
- PostgreSQL recommended (SQLite compatible)  
- Python 3.12  