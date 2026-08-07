import json
import time
import urllib.request
from urllib.error import HTTPError

BASE_URL = "http://127.0.0.1:8000"


def request(path, method="GET", data=None, token=None):
    url = BASE_URL + path
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        print(f"HTTP {exc.code}: {exc.read().decode('utf-8')}")
        raise


if __name__ == "__main__":
    print("Starting FinGuard backend test client")
    print("Make sure the server is running at http://127.0.0.1:8000")

    timestamp = int(time.time())
    user = {
        "username": f"student1_{timestamp}",
        "password": "secure123",
        "income": 2200,
        "expenses": 1200,
        "savings": 300,
    }

    print("Registering user...")
    try:
        print(request("/register", method="POST", data=user))
    except HTTPError as exc:
        if exc.code == 400:
            print("User registration failed because the username already exists. Continuing with login.")
        else:
            raise

    print("Logging in...")
    token_response = request("/login", method="POST", data={"username": user["username"], "password": user["password"]})
    token = token_response["token"]
    print(f"Token: {token}")

    print("Submitting sample transaction...")
    transaction = {
        "amount": 950,
        "category": "groceries",
        "location": "local",
        "description": "Weekly shopping",
    }
    print(request("/transactions", method="POST", data=transaction, token=token))

    print("Requesting dashboard...")
    print(request("/dashboard", method="GET", token=token))

    print("Requesting alerts...")
    print(request("/alerts", method="GET", token=token))
