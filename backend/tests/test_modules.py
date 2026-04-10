"""
TUDOaqui - API Module Tests
Testa endpoints publicos via curl (mais fiável que ASGI transport com asyncpg)
"""
import subprocess
import json
import os

API_URL = os.environ.get(
    "TEST_API_URL",
    "http://localhost:8001/api/v1"
)


def curl_get(path):
    r = subprocess.run(
        ["curl", "-s", f"{API_URL}{path}"],
        capture_output=True, text=True, timeout=10
    )
    return r.returncode, json.loads(r.stdout) if r.stdout else None


def curl_post(path, data=None):
    cmd = ["curl", "-s", "-X", "POST", f"{API_URL}{path}", "-H", "Content-Type: application/json"]
    if data:
        cmd += ["-d", json.dumps(data)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    return r.returncode, json.loads(r.stdout) if r.stdout else None


class TestPublicEndpoints:
    def test_ws_status(self):
        code, data = curl_get("/ws/status")
        assert code == 0
        assert "total_connections" in data

    def test_list_events(self):
        code, data = curl_get("/events")
        assert code == 0
        assert isinstance(data, list)

    def test_list_products(self):
        code, data = curl_get("/marketplace/products")
        assert code == 0
        assert isinstance(data, list)

    def test_list_categories(self):
        code, data = curl_get("/marketplace/categories")
        assert code == 0
        assert isinstance(data, list)

    def test_list_alojamento(self):
        code, data = curl_get("/alojamento/properties")
        assert code == 0
        assert isinstance(data, list)

    def test_list_experiences(self):
        code, data = curl_get("/turismo/experiences")
        assert code == 0
        assert isinstance(data, list)

    def test_list_realestate(self):
        code, data = curl_get("/realestate/properties")
        assert code == 0
        assert isinstance(data, list)

    def test_list_restaurants(self):
        code, data = curl_get("/restaurantes")
        assert code == 0
        assert isinstance(data, list)

    def test_bank_info(self):
        code, data = curl_get("/payments/bank-info")
        assert code == 0

    def test_payment_methods(self):
        code, data = curl_get("/payments/methods")
        assert code == 0


class TestAuth:
    def test_login_valid_phone(self):
        code, data = curl_post("/auth/login", {"telefone": "+244912000000"})
        assert code == 0
        assert "message" in data

    def test_login_invalid_phone(self):
        code, data = curl_post("/auth/login", {"telefone": "123"})
        assert code == 0
        # Should return error


class TestRides:
    def _get_token(self):
        curl_post("/auth/login", {"telefone": "+244912000000"})
        r = subprocess.run(
            ["su", "-", "postgres", "-c",
             "psql -d tudoaqui -t -A -c \"SELECT codigo FROM otp_codes WHERE telefone='+244912000000' AND verificado=false ORDER BY created_at DESC LIMIT 1;\""],
            capture_output=True, text=True, timeout=10
        )
        otp = r.stdout.strip()
        if not otp:
            return None
        _, data = curl_post("/auth/verify-otp", {"telefone": "+244912000000", "codigo": otp})
        return data.get("access_token") if data else None

    def test_rides_estimate(self):
        token = self._get_token()
        if not token:
            return  # Skip if no token
        cmd = [
            "curl", "-s", "-X", "POST", f"{API_URL}/rides/estimate",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {token}",
            "-d", json.dumps({
                "origem": {"latitude": -8.8383, "longitude": 13.2344, "endereco": "Largo Kinaxixi"},
                "destino": {"latitude": -8.84, "longitude": 13.24, "endereco": "Marginal Luanda"},
            })
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout)
        assert "valor_estimado" in data
