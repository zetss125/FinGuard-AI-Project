# FinGuard AI Simple Backend

This backend implements a lightweight financial advisory API for the FinGuard AI simple project. It uses FastAPI and SQLite for storage.

## Setup

1. Open a terminal in the project root:
   ```bash
   cd "c:\courses\AIDI\Semester 2\Knowledge & Expert Systems\Final Project"
   ```
2. Install dependencies:
   ```bash
   python -m pip install -r backend/requirements.txt
   ```

## Run the application

Start the API server:

```bash
python -m uvicorn backend.main:app --reload
```

Open in your browser:

- http://127.0.0.1:8000
- Swagger API docs: http://127.0.0.1:8000/docs

## Endpoints

- `POST /register` - create a new user
- `POST /login` - login and receive a bearer token
- `POST /transactions` - submit a transaction and evaluate fraud risk
- `POST /credit` - get credit recommendation
- `GET /dashboard` - view user summary and alerts
- `GET /alerts` - view recent alerts

## Quick test flow

1. Register a user.
2. Login to get the token.
3. Send transactions with the token in the `Authorization` header.
4. Query `/dashboard` and `/alerts`.
