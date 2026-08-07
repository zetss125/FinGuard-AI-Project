from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Dict, Generator, List, Optional
import sqlite3
import uuid

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "finguard.db"

app = FastAPI(title="FinGuard AI Simple Backend")


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=6)
    income: float = Field(..., ge=0)
    expenses: float = Field(..., ge=0)
    savings: float = Field(..., ge=0)


class LoginRequest(BaseModel):
    username: str
    password: str


class TransactionRequest(BaseModel):
    amount: float = Field(..., gt=0)
    category: str = Field(..., min_length=2)
    location: Optional[str] = "home"
    description: Optional[str] = ""


class CreditRequest(BaseModel):
    note: Optional[str] = ""


class AlertItem(BaseModel):
    id: int
    message: str
    level: str
    created_at: str


class DashboardResponse(BaseModel):
    username: str
    income: float
    expenses: float
    savings: float
    credit_recommendation: str
    credit_risk: str
    recent_alerts: List[AlertItem]


class TransactionResponse(BaseModel):
    fraud_score: int
    fraud_risk: str
    message: str


class LoginResponse(BaseModel):
    token: str
    message: str


def get_db() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def get_db_dependency() -> Generator[sqlite3.Connection, None, None]:
    db = get_db()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            income REAL NOT NULL,
            expenses REAL NOT NULL,
            savings REAL NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT,
            fraud_score INTEGER NOT NULL,
            fraud_risk TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            level TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )
    db.commit()
    db.close()


def hash_password(password: str) -> str:
    return sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, stored_hash: str) -> bool:
    return hash_password(password) == stored_hash


def create_user(db: sqlite3.Connection, data: RegisterRequest) -> Dict:
    cursor = db.cursor()
    created_at = datetime.utcnow().isoformat()
    password_hash = hash_password(data.password)
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, income, expenses, savings, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (data.username, password_hash, data.income, data.expenses, data.savings, created_at),
        )
        db.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists.")
    user_id = cursor.lastrowid
    return get_user_by_id(db, user_id)


def get_user_by_username(db: sqlite3.Connection, username: str) -> Optional[sqlite3.Row]:
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cursor.fetchone()


def get_user_by_id(db: sqlite3.Connection, user_id: int) -> Optional[sqlite3.Row]:
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()


def create_session(db: sqlite3.Connection, user_id: int) -> str:
    token = uuid.uuid4().hex
    created_at = datetime.utcnow().isoformat()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO sessions (user_id, token, created_at) VALUES (?, ?, ?)",
        (user_id, token, created_at),
    )
    db.commit()
    return token


def get_session_by_token(db: sqlite3.Connection, token: str) -> Optional[sqlite3.Row]:
    cursor = db.cursor()
    cursor.execute("SELECT * FROM sessions WHERE token = ?", (token,))
    return cursor.fetchone()


def create_alert(db: sqlite3.Connection, user_id: int, message: str, level: str = "medium") -> None:
    cursor = db.cursor()
    created_at = datetime.utcnow().isoformat()
    cursor.execute(
        "INSERT INTO alerts (user_id, message, level, created_at) VALUES (?, ?, ?, ?)",
        (user_id, message, level, created_at),
    )
    db.commit()


def get_recent_alerts(db: sqlite3.Connection, user_id: int, limit: int = 5) -> List[Dict]:
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, message, level, created_at FROM alerts WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    )
    return [dict(row) for row in cursor.fetchall()]


def compute_fraud_score(amount: float, user: sqlite3.Row, location: str) -> Dict[str, object]:
    score = 10
    if amount >= 1000:
        score += 30
    if amount > user["income"] * 0.3:
        score += 20
    if amount > user["expenses"] * 0.9:
        score += 20
    if location.lower() not in {"home", "office", "local"}:
        score += 15
    score = min(100, score)

    if score >= 60:
        risk = "high"
    elif score >= 35:
        risk = "medium"
    else:
        risk = "low"

    return {"fraud_score": score, "fraud_risk": risk}


def compute_credit_advice(user: sqlite3.Row) -> Dict[str, str]:
    income = user["income"]
    expenses = user["expenses"]
    savings = user["savings"]
    if income <= 0:
        return {
            "credit_recommendation": "Income data is required to evaluate credit.",
            "credit_risk": "unknown",
        }

    expense_ratio = expenses / income
    savings_ratio = savings / max(income, 1)

    if expense_ratio > 0.7:
        return {
            "credit_recommendation": "Reduce monthly expenses and avoid new debt.",
            "credit_risk": "high",
        }
    if savings_ratio < 0.15:
        return {
            "credit_recommendation": "Build savings before taking new credit.",
            "credit_risk": "medium",
        }

    return {
        "credit_recommendation": "Your finances are stable for a small loan.",
        "credit_risk": "low",
    }


security = HTTPBearer(auto_error=False)

def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: sqlite3.Connection = Depends(get_db_dependency),
) -> sqlite3.Row:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must be Bearer token.",
        )
    token = credentials.credentials
    session = get_session_by_token(db, token)
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")
    user = get_user_by_id(db, session["user_id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    return user


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/", summary="Health check")
def root() -> Dict[str, str]:
    return {"status": "FinGuard AI backend is running"}


@app.post("/register", summary="Register a new user")
def register(data: RegisterRequest, db: sqlite3.Connection = Depends(get_db_dependency)) -> Dict[str, str]:
    user = create_user(db, data)
    return {"message": "User registered successfully.", "username": user["username"]}


@app.post("/login", response_model=LoginResponse, summary="Login and receive a token")
def login(data: LoginRequest, db: sqlite3.Connection = Depends(get_db_dependency)) -> LoginResponse:
    user = get_user_by_username(db, data.username)
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    token = create_session(db, user["id"])
    return LoginResponse(token=token, message="Login successful.")


@app.post("/transactions", response_model=TransactionResponse, summary="Add a transaction and evaluate fraud risk")
def add_transaction(
    payload: TransactionRequest,
    user: sqlite3.Row = Depends(verify_token),
    db: sqlite3.Connection = Depends(get_db_dependency),
) -> TransactionResponse:
    result = compute_fraud_score(payload.amount, user, payload.location or "home")
    cursor = db.cursor()
    created_at = datetime.utcnow().isoformat()
    cursor.execute(
        "INSERT INTO transactions (user_id, amount, category, location, description, fraud_score, fraud_risk, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (user["id"], payload.amount, payload.category, payload.location or "home", payload.description, result["fraud_score"], result["fraud_risk"], created_at),
    )
    db.commit()

    if result["fraud_score"] >= 60:
        create_alert(
            db,
            user["id"],
            f"High fraud risk detected for a transaction of ${payload.amount:.2f}.",
            level="high",
        )
    elif result["fraud_score"] >= 35:
        create_alert(
            db,
            user["id"],
            f"Medium fraud risk for a transaction of ${payload.amount:.2f}.",
            level="medium",
        )

    return TransactionResponse(
        fraud_score=result["fraud_score"],
        fraud_risk=result["fraud_risk"],
        message="Transaction recorded and evaluated.",
    )


@app.post("/credit", summary="Get a credit recommendation")
def credit_advice(
    _: CreditRequest,
    user: sqlite3.Row = Depends(verify_token),
    db: sqlite3.Connection = Depends(get_db_dependency),
) -> Dict[str, str]:
    advice = compute_credit_advice(user)
    if advice["credit_risk"] == "high":
        create_alert(db, user["id"], "High credit risk based on current income and expenses.", level="high")
    return advice


@app.get("/dashboard", response_model=DashboardResponse, summary="View the user dashboard")
def dashboard(
    user: sqlite3.Row = Depends(verify_token),
    db: sqlite3.Connection = Depends(get_db_dependency),
) -> DashboardResponse:
    advice = compute_credit_advice(user)
    alerts = get_recent_alerts(db, user["id"], limit=5)
    return DashboardResponse(
        username=user["username"],
        income=user["income"],
        expenses=user["expenses"],
        savings=user["savings"],
        credit_recommendation=advice["credit_recommendation"],
        credit_risk=advice["credit_risk"],
        recent_alerts=[AlertItem(**alert) for alert in alerts],
    )


@app.get("/alerts", response_model=List[AlertItem], summary="List recent alerts")
def alerts(
    user: sqlite3.Row = Depends(verify_token),
    db: sqlite3.Connection = Depends(get_db_dependency),
) -> List[AlertItem]:
    alerts_data = get_recent_alerts(db, user["id"], limit=10)
    return [AlertItem(**alert) for alert in alerts_data]
