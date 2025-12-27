from fastapi.testclient import TestClient
from backend.main import app
import time

client = TestClient(app)

def test_rate_limiting():
    print("Testing Rate Limiting...")
    # Hit login endpoint 6 times
    for i in range(6):
        response = client.post("/api/v1/token", data={"username": "test", "password": "password"})
        print(f"Request {i+1}: {response.status_code}")
        if response.status_code == 429:
            print("✅ Rate Limiting working (429 received)")
            return
    print("❌ Rate Limiting failed (no 429 received)")

def test_security_headers():
    print("\nTesting Security Headers...")
    response = client.get("/")
    headers = response.headers
    
    required_headers = [
        "X-Frame-Options",
        "X-Content-Type-Options",
        "Strict-Transport-Security",
        "Content-Security-Policy"
    ]
    
    for header in required_headers:
        if header in headers:
            print(f"✅ {header}: {headers[header]}")
        else:
            print(f"❌ {header} missing")

if __name__ == "__main__":
    test_rate_limiting()
    test_security_headers()
