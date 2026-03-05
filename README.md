# FastAPI Banking API

A secure banking-style backend API built with FastAPI, featuring JWT authentication, transaction logging, and Dockerized deployment.

---

![Python](https://img.shields.io/badge/Python-3.9-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![Database](https://img.shields.io/badge/Database-SQLite-lightgrey)
![License](https://img.shields.io/badge/License-MIT-yellow)

A RESTful backend API that simulates basic banking operations such as user registration, deposits, withdrawals, transfers, and transaction history tracking.

The project is built using **FastAPI** and **SQLAlchemy** and demonstrates backend development concepts including API design, database modeling, secure authentication, and transaction logging.

Key features of this project include:

- User registration and account creation
- Secure authentication using **JWT tokens**
- Deposit, withdrawal, and fund transfer operations
- Transaction history tracking
- Interactive API documentation using **Swagger UI**
- Containerized deployment using **Docker**

The API simulates core banking operations while enforcing authentication for protected endpoints.


---

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Uvicorn
- Pydantic

---

## Quick Start

Run the API locally in a few steps:

```bash
git clone https://github.com/rutujad9/fastapi-banking-api.git
cd fastapi-banking-api

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

uvicorn main:app --reload
```

Once the server starts, open:

http://127.0.0.1:8000/docs

You can test the API directly using the interactive Swagger UI.

---

## Project Structure

```
banking-api/
│
├── main.py          # API routes and business logic
├── models.py        # database models
├── schemas.py       # request and response schemas
├── database.py      # database connection setup
├── auth.py          # JWT authentication utilities
├── requirements.txt # project dependencies
├── Dockerfile
├── README.md
└── images/          # API documentation screenshots
```

---

## Run with Docker

Build the Docker image:

```bash
docker build -t fastapi-banking-api .
```

Run the container:

```bash
docker run -p 8000:8000 fastapi-banking-api
```

---


## Authentication

This API uses **JWT authentication** to secure banking operations.

### Login

Use the `/login` endpoint to authenticate a user.

After logging in, Swagger UI will automatically attach the JWT token to authenticated requests.

Steps:

1. Register a new user using `/register`
2. Click **Authorize** in Swagger UI
3. Enter your email in the **username** field and your password
4. Swagger will attach the JWT token to all protected requests


### Protected Endpoints

The following endpoints require authentication:

POST `/deposit` — deposit money  
POST `/withdraw` — withdraw money  
POST `/transfer` — transfer funds  
GET `/transactions/{account_id}` — view transaction history

Requests to these endpoints will fail if the user is not authenticated.

---

## Example Features

### Register User
Creates a new user and automatically creates a bank account.

### Deposit Money
Adds money to an account.

### Withdraw Money
Removes money from an account if sufficient balance exists.

### Transfer Money
Transfers funds between two accounts.

### Transaction History
View all transactions related to an account.

---

## Example API Endpoints

POST `/register` — create new user  
POST `/login` — authenticate user and obtain JWT token  
POST `/deposit` — deposit money  
POST `/withdraw` — withdraw money  
POST `/transfer` — transfer funds  
GET `/transactions/{account_id}` — view transaction history

---

## How to Test the API

1. Start the server:

```
uvicorn main:app --reload
```

2. Open the interactive API documentation:

```
http://127.0.0.1:8000/docs
```

3. Use the Swagger interface to test endpoints such as:

- Register a user
- Login and authorize
- Deposit money
- Withdraw money
- Transfer money between accounts
- View transaction history

---


## API Preview

### Swagger API Documentation
![API Docs](images/api-docs.png)

### Register User
![Register](images/register.png)

### Deposit Money
![Deposit](images/deposit.png)

### Transfer Funds
![Transfer](images/transfer.png)

### Transaction History
![Transactions](images/transactions.png)


## License

This project is licensed under the MIT License.

---

## Author

Rutuja Deshmukh  
MSc Informatik — Germany