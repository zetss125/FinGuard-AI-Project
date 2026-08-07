# FinGuard AI Simple Backend

## Project Summary

FinGuard AI is a student-level financial decision support system. It provides user registration, login, transaction evaluation, credit recommendation, and dashboard/alert views.

The backend is implemented with FastAPI and uses SQLite for data persistence. Fraud detection is performed with a simple rule-based scoring method.

## Technologies

- Python 3.13
- FastAPI
- Uvicorn
- SQLite
- Pydantic
- HTTP Bearer authentication
- python-docx (for generating documentation)

## Setup Instructions

1. Open a terminal in the project root:
   ```powershell
   cd "C:\courses\AIDI\Semester 2\Knowledge & Expert Systems\Final Project"
   ```
2. Install dependencies:
   ```powershell
   C:\Users\rawad\AppData\Local\Microsoft\WindowsApps\python3.13.exe -m pip install -r backend/requirements.txt
   ```
3. Install the report generation dependency if needed:
   ```powershell
   C:\Users\rawad\AppData\Local\Microsoft\WindowsApps\python3.13.exe -m pip install python-docx
   ```

## Run the backend

Start the API server:

```powershell
C:\Users\rawad\AppData\Local\Microsoft\WindowsApps\python3.13.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open Swagger UI in your browser:

- http://127.0.0.1:8000/docs

## API Endpoints

### Register

- `POST /register`
- Body:
  ```json
  {
    "username": "user1",
    "password": "user123",
    "income": 10000,
    "expenses": 4000,
    "savings": 50000
  }
  ```

### Login

- `POST /login`
- Body:
  ```json
  {
    "username": "user1",
    "password": "user123"
  }
  ```
- Response contains a token:
  ```json
  {
    "token": "<bearer-token>",
    "message": "Login successful."
  }
  ```

### Protected endpoints

For the following endpoints, include the header:

```
Authorization: Bearer <token>
```

### Submit a transaction

- `POST /transactions`
- Body:
  ```json
  {
    "amount": 6000,
    "category": "Family",
    "location": "home",
    "description": "Sending a family emergency funds"
  }
  ```

### Get credit recommendation

- `POST /credit`
- Body:
  ```json
  {
    "note": "Optional note"
  }
  ```

### View dashboard

- `GET /dashboard`

### View alerts

- `GET /alerts`

## Notes

- Use Swagger’s `Authorize` button to enter your token in the form `Bearer <token>`.
- If you receive `422` on a protected endpoint, the token header is missing or malformed.

## Testing

You can run the included test client:

```powershell
C:\Users\rawad\AppData\Local\Microsoft\WindowsApps\python3.13.exe backend/test_client.py
```

This will register a new user, log in, submit a transaction, and fetch the dashboard and alerts.
