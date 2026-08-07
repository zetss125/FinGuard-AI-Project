# Python Code Explanation for FinGuard AI

This document explains the main Python files in the project so a team member can answer questions about how the app works.

## 1. `backend/main.py`

This is the main backend application.

### What it does

* Defines the API server using FastAPI.
* Handles user registration and login.
* Protects important endpoints with bearer token authentication.
* Evaluates transaction fraud risk.
* Provides credit recommendation advice.
* Stores data in a local SQLite database.

### Key sections

#### Imports and setup

* `fastapi`, `Depends`, `HTTPException`, `status` — used for API routing and request handling.
* `HTTPBearer`, `HTTPAuthorizationCredentials` — used for bearer token authentication.
* `sqlite3` — provides the database connection.
* `uuid` — used to generate session tokens.
* `sha256` — hashes passwords for secure storage.
* `datetime` — stores timestamps for records.

#### Data models

The app uses Pydantic models to validate input and output:

* `RegisterRequest` — required fields for new users.
* `LoginRequest` — username and password for login.
* `TransactionRequest` — transaction fields for fraud evaluation.
* `CreditRequest` — optional credit request note.
* `AlertItem`, `DashboardResponse`, `TransactionResponse`, `LoginResponse` — response models.

#### Database functions

* `get_db()` opens a SQLite connection.
* `init_db()` creates tables: `users`, `sessions`, `transactions`, `alerts`.
* `create_user()` and `get_user_by_username()` manage users.
* `create_session()` and `get_session_by_token()` manage login sessions.
* `create_alert()` and `get_recent_alerts()` manage alert records.

#### Authentication

* `hash_password()` hashes passwords with SHA-256.
* `verify_password()` compares a plaintext password with a stored hash.
* `security = HTTPBearer(auto_error=False)` makes FastAPI understand bearer tokens.
* `verify_token()` checks the token and returns the authenticated user.

Protected routes use `Depends(verify_token)` so they require a valid `Authorization: Bearer <token>` header.

#### Business rules

* `compute_fraud_score()` calculates a fraud score based on transaction amount, income, expenses, and location.
* `compute_credit_advice()` returns credit advice based on expense ratio and savings ratio.

#### API endpoints

* `GET /` — health check.
* `POST /register` — register a new user.
* `POST /login` — verify credentials and return a token.
* `POST /transactions` — evaluate fraud risk for a transaction and save it.
* `POST /credit` — return credit advice.
* `GET /dashboard` — return user summary and recent alerts.
* `GET /alerts` — return recent alerts.

### Notes for questions

* The app uses explicit rules rather than machine learning.
* The fraud risk score is easy to explain because it adds fixed points for known risk factors.
* The token session system is simple and stored in SQLite.

## 2. `backend/test_client.py`

This file is a simple test script for the API.

### What it does

* Registers a new user with random username suffix.
* Logs in and stores the returned token.
* Sends a sample transaction request.
* Requests the dashboard and alerts.

### Why it is useful

* It verifies the backend works end to end.
* It shows how to include the bearer token in requests.
* It is helpful for testing without a frontend.

### Important details

* Uses Python standard library `urllib.request`.
* Sends JSON requests with `Content-Type: application/json`.
* Adds the `Authorization` header for protected requests.

## 3. Optional helper scripts

### `generate_report.py`

This helper script converts the explanation markdown into a Word document (`.docx`). It is not part of the app logic and is only used for documentation.

### `generate_video_pdf.py`

This helper script converts the video guideline markdown into a PDF file. It is also only for documentation and demo preparation.

## 4. How the backend code is organized

The backend follows a clear structure:

* Request validation and response models are declared at the top.
* Database setup and helper functions are grouped together.
* Security and authentication are centralized in `verify_token()`.
* Business logic functions are separate from API route handlers.
* Each route is a small wrapper around the core logic.

## 5. Common questions and answers

### Q: How does login work?
A: `/login` checks the username and password, and if correct it creates a session token in the `sessions` table.

### Q: How is fraud calculated?
A: The app uses a score-based expert system. It adds points for large amounts, high relative cost, and unusual locations. The total score becomes a risk label.

### Q: Why use SQLite?
A: SQLite is easy to set up and good for a small project or demo. It keeps the app simple for testing.

### Q: Why no frontend?
A: This repository contains the backend API. The frontend can be any client that calls the API endpoints.

---

This file is meant to help team members explain the Python code clearly and accurately during review or presentation.