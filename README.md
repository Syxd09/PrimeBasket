# PrimeBasket API Documentation

This document describes the API endpoints available in the PrimeBasket project.

## Authentication Endpoints

### Register
*   **Method:** `POST`
*   **URL:** `/api/auth/register/`
*   **Request (example):**

    ```json
    {
        "username": "newuser",
        "password": "password123",
        "email": "newuser@example.com"
    }
    ```
*   **Response (example - success):**

    ```json
    {
        "id": 1,
        "username": "newuser",
        "email": "newuser@example.com"
    }
    ```

### Login
*   **Method:** `POST`
*   **URL:** `/api/auth/login/`
*   **Request (example):**

    ```json
    {
        "username": "existinguser",
        "password": "password123"
    }
    ```
*   **Response (example - success):**

    ```json
    {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcwOTc5NzYwMCwiaWF0IjoxNzA5Nzk3MzAwLCJqdGkiOiI0YjQzYjQzYjQzYjQzYjQzYjQzYjQzYjQzYjQzIiwidXNlcl9pZCI6MX0.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzA5Nzk3OTAwLCJpYXQiOjE3MDk3OTczMDAsImp0aSI6IjQzNDM0MzQzNDM0MzQzNDM0MzQzNDM0MzQzNDMiLCJ1c2VyX2lkIjoxfQ.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "user": {
            "id": 1,
            "username": "existinguser",
            "email": "existinguser@example.com"
        }
    }
    ```
*   **Response (example - failure):**

    ```json
    {
        "detail": "Invalid Credentials"
    }
    ```

### Reset Password
*   **Method:** `POST`
*   **URL:** `/api/auth/reset-password/`
*   **Requires authentication (JWT token in the `Authorization` header).**
*   **Request (example):**

    ```json
    {
        "password": "newpassword123"
    }
    ```
*   **Response (example - success):**

    ```json
    {
        "status": "success",
        "code": 200,
        "message": "Password updated successfully",
        "data": []
    }
    ```

### Dashboard
*   **Method:** `GET`
*   **URL:** `/api/dashboard/`
*   **Requires authentication (JWT token in the `Authorization` header).**
*   **Request (example):**

    ```
    GET /api/dashboard/ HTTP/1.1
    Authorization: Bearer <access_token>
    ```
*   **Response (example - success):**

    ```json
    {
        "message": "Welcome to Dashboard",
        "user": {
            "id": 1,
            "username": "existinguser",
            "email": "existinguser@example.com"
        }
    }
    ```

## Shop Endpoints

### Get Products
*   **Method:** `GET`
*   **URL:** `/api/shop/products/`
*   **Parameters:** `category`, `brand`, `sort` (optional)
*   **Request (example):**

    ```
    GET /api/shop/products/?category=electronics&brand=apple&sort=price_asc HTTP/1.1
    ```
*   **Response (example - success):**

    ```json
    [
        {
            "id": 1,
            "product": "iPhone 13",
            "brand": "Apple",
            "category": "Electronics",
            "description": "The latest iPhone...",
            "sale_price": 799.00,
            "rating": 4.5
        },
        {
            "id": 2,
            "product": "Samsung Galaxy S22",
            "brand": "Samsung",
            "category": "Electronics",
            "description": "The latest Samsung...",
            "sale_price": 749.00,
            "rating": 4.3
        }
    ]
    ```

### Search Products
*   **Method:** `GET`
*   **URL:** `/api/shop/search/`
*   **Parameters:** `q` (query string)
*   **Request (example):**

    ```
    GET /api/shop/search/?q=phone HTTP/1.1
    ```
*   **Response (example - success):**

    ```json
    [
        {
            "id": 1,
            "product": "iPhone 13",
            "brand": "Apple",
            "category": "Electronics",
            "description": "The latest iPhone...",
            "sale_price": 799.00,
            "rating": 4.5
        },
        {
            "id": 2,
            "product": "Samsung Galaxy S22",
            "brand": "Samsung",
            "category": "Electronics",
            "description": "The latest Samsung...",
            "sale_price": 749.00,
            "rating": 4.3
        }
    ]
    ```

### Add to Cart
*   **Method:** `POST`
*   **URL:** `/api/shop/cart/add/`
*   **Request (example):**

    ```json
    {
        "product_id": 1
    }
    ```
*   **Response (example - success):**

    ```json
    [
        {
            "id": 1,
            "product": 1,
            "quantity": 1
        }
    ]
    ```
*   **Response (example - failure - product not found):**

    ```json
    {
        "error": "Product not found"
    }
    ```

### Remove from Cart
*   **Method:** `POST`
*   **URL:** `/api/shop/cart/remove/`
*   **Request (example):**

    ```json
    {
        "product_id": 1
    }
    ```
*   **Response (example - success):**

    ```json
    [
        {
            "id": 2,
            "product": 2,
            "quantity": 1
        }
    ]
    ```

### Update Cart Quantity
*   **Method:** `POST`
*   **URL:** `/api/shop/cart/update/`
*   **Request (example):**

    ```json
    {
        "product_id": 1,
        "quantity": 2
    }
    ```
*   **Response (example - success):**

    ```json
    [
        {
            "id": 1,
            "product": 1,
            "quantity": 2
        }
    ]