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
- Token authentication
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
    "token": "<token>",
    "message": "Login successful."
  }
  ```

### Protected endpoints

For the following endpoints, use the token value only. Paste the token itself (for example, `6171f19093e248d6b4fc1f7c6110a049`) without adding any header or prefix text.

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

- Use Swagger’s `Authorize` button and paste only the token value.
- If you receive `401` or `422` on a protected endpoint, the token is missing, expired, or was entered incorrectly.

## Testing

You can run the included test client:

```powershell
C:\Users\rawad\AppData\Local\Microsoft\WindowsApps\python3.13.exe backend/test_client.py
```

This will register a new user, log in, submit a transaction, and fetch the dashboard and alerts.
