"""
TUDOaqui API - GPS Tracking & Rides Tests
Tests for:
- WebSocket status endpoint
- Ride estimate endpoint
- Auth login/verify-otp
- Driver online/location endpoints
- Ride request/accept/start/finish flow
- GPS tracking endpoints
"""
import pytest
import requests
import os
import subprocess
import time
from uuid import UUID

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test phone numbers
ADMIN_PHONE = "+244912000000"
TEST_DRIVER_PHONE = "+244911000001"  # Carlos Mendes - organizador (can be driver)
TEST_CLIENT_PHONE = "+244911000002"  # Ana Ferreira - vendedor


def get_otp(phone: str) -> str:
    """Get OTP from database"""
    cmd = f'su - postgres -c "psql -d tudoaqui -t -A -c \\"SELECT codigo FROM otp_codes WHERE telefone=\'{phone}\' AND verificado=false ORDER BY created_at DESC LIMIT 1;\\""'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


def get_auth_token(phone: str) -> str:
    """Get auth token for a phone number"""
    # Request OTP
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"telefone": phone})
    if response.status_code == 429:
        # Rate limited, wait and retry
        time.sleep(5)
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"telefone": phone})
    
    if response.status_code != 200:
        pytest.skip(f"Could not request OTP for {phone}: {response.status_code} - {response.text}")
    
    # Get OTP from DB
    time.sleep(0.5)
    otp = get_otp(phone)
    if not otp:
        pytest.skip(f"Could not get OTP from DB for {phone}")
    
    # Verify OTP
    response = requests.post(f"{BASE_URL}/api/v1/auth/verify-otp", json={
        "telefone": phone,
        "codigo": otp
    })
    
    if response.status_code != 200:
        pytest.skip(f"Could not verify OTP for {phone}: {response.status_code} - {response.text}")
    
    return response.json().get("access_token")


class TestWebSocketStatus:
    """Test WebSocket status endpoint"""
    
    def test_ws_status_returns_connection_stats(self):
        """GET /api/v1/ws/status returns connection stats"""
        response = requests.get(f"{BASE_URL}/api/v1/ws/status")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total_connections" in data
        assert "online_drivers" in data
        assert "active_rides" in data
        assert isinstance(data["total_connections"], int)
        assert isinstance(data["online_drivers"], int)
        assert isinstance(data["active_rides"], int)
        print(f"WS Status: {data}")


class TestAuthFlow:
    """Test authentication flow"""
    
    def test_login_sends_otp(self):
        """POST /api/v1/auth/login sends OTP"""
        # Use a test phone that won't be rate limited
        test_phone = "+244911888888"
        
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
            "telefone": test_phone
        })
        
        # Accept 200 or 429 (rate limited)
        assert response.status_code in [200, 429], f"Expected 200 or 429, got {response.status_code}: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert "telefone" in data
            assert "expires_in_seconds" in data
            print(f"OTP sent to {data['telefone']}, expires in {data['expires_in_seconds']}s")
        else:
            print("Rate limited - OTP already sent recently")
    
    def test_verify_otp_returns_token(self):
        """POST /api/v1/auth/verify-otp returns token"""
        test_phone = "+244911777777"
        
        # Request OTP
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"telefone": test_phone})
        if response.status_code == 429:
            pytest.skip("Rate limited")
        
        assert response.status_code == 200
        
        # Get OTP from DB
        time.sleep(0.5)
        otp = get_otp(test_phone)
        if not otp:
            pytest.skip("Could not get OTP from DB")
        
        # Verify OTP
        response = requests.post(f"{BASE_URL}/api/v1/auth/verify-otp", json={
            "telefone": test_phone,
            "codigo": otp
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert len(data["access_token"]) > 0
        print(f"Token received for user: {data['user'].get('telefone')}")


class TestRideEstimate:
    """Test ride estimate endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for tests"""
        return get_auth_token(TEST_CLIENT_PHONE)
    
    def test_ride_estimate_calculates_correctly(self, auth_token):
        """POST /api/v1/rides/estimate calculates ride estimate"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Luanda coordinates
        payload = {
            "origem": {
                "latitude": -8.8383,
                "longitude": 13.2344,
                "endereco": "Largo da Mutamba, Luanda"
            },
            "destino": {
                "latitude": -8.8147,
                "longitude": 13.2302,
                "endereco": "Aeroporto 4 de Fevereiro, Luanda"
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/rides/estimate", json=payload, headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "distancia_km" in data
        assert "duracao_estimada_min" in data
        assert "valor_estimado" in data
        assert "motoristas_disponiveis" in data
        assert data["distancia_km"] > 0
        assert data["duracao_estimada_min"] > 0
        assert data["valor_estimado"] > 0
        print(f"Estimate: {data['distancia_km']}km, {data['duracao_estimada_min']}min, {data['valor_estimado']}Kz")
    
    def test_ride_estimate_requires_endereco(self, auth_token):
        """POST /api/v1/rides/estimate requires endereco field"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Missing endereco
        payload = {
            "origem": {
                "latitude": -8.8383,
                "longitude": 13.2344
            },
            "destino": {
                "latitude": -8.8147,
                "longitude": 13.2302
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/rides/estimate", json=payload, headers=headers)
        
        # Should fail validation
        assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"


class TestDriverEndpoints:
    """Test driver-specific endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin auth token"""
        return get_auth_token(ADMIN_PHONE)
    
    @pytest.fixture(scope="class")
    def driver_setup(self, admin_token):
        """Setup a test driver"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Check if admin already has driver profile
        response = requests.get(f"{BASE_URL}/api/v1/drivers/me", headers=headers)
        
        if response.status_code == 200:
            driver = response.json()
            # Approve if pending
            if driver.get("status") == "pendente":
                requests.post(f"{BASE_URL}/api/v1/drivers/{driver['id']}/approve", headers=headers)
            return {"token": admin_token, "driver": driver}
        
        # Register as driver
        response = requests.post(f"{BASE_URL}/api/v1/drivers/register", json={
            "veiculo": "Toyota Corolla Test",
            "matricula": "LD-TEST-99",
            "cor_veiculo": "Branco",
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 2020
        }, headers=headers)
        
        if response.status_code == 201:
            driver = response.json()
            # Approve the driver
            requests.post(f"{BASE_URL}/api/v1/drivers/{driver['id']}/approve", headers=headers)
            return {"token": admin_token, "driver": driver}
        elif response.status_code == 400 and "já é motorista" in response.text:
            # Already registered, get profile
            response = requests.get(f"{BASE_URL}/api/v1/drivers/me", headers=headers)
            return {"token": admin_token, "driver": response.json()}
        else:
            pytest.skip(f"Could not setup driver: {response.status_code} - {response.text}")
    
    def test_driver_online_toggle(self, driver_setup):
        """POST /api/v1/drivers/me/online toggles driver online status"""
        headers = {"Authorization": f"Bearer {driver_setup['token']}"}
        
        # Go online with location
        response = requests.post(f"{BASE_URL}/api/v1/drivers/me/online", json={
            "online": True,
            "latitude": -8.8383,
            "longitude": 13.2344
        }, headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["online"] == True
        assert data["latitude"] is not None
        assert data["longitude"] is not None
        print(f"Driver online at ({data['latitude']}, {data['longitude']})")
        
        # Go offline
        response = requests.post(f"{BASE_URL}/api/v1/drivers/me/online", json={
            "online": False
        }, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["online"] == False
        print("Driver offline")
    
    def test_driver_location_update(self, driver_setup):
        """POST /api/v1/drivers/me/location updates driver GPS location"""
        headers = {"Authorization": f"Bearer {driver_setup['token']}"}
        
        # First go online
        requests.post(f"{BASE_URL}/api/v1/drivers/me/online", json={
            "online": True,
            "latitude": -8.8383,
            "longitude": 13.2344
        }, headers=headers)
        
        # Update location
        response = requests.post(f"{BASE_URL}/api/v1/drivers/me/location", json={
            "latitude": -8.8400,
            "longitude": 13.2350
        }, headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert abs(float(data["latitude"]) - (-8.84)) < 0.001
        assert abs(float(data["longitude"]) - 13.235) < 0.001
        print(f"Driver location updated to ({data['latitude']}, {data['longitude']})")
    
    def test_pending_rides_nearby(self, driver_setup):
        """GET /api/v1/rides/pending/nearby lists pending rides near coordinates"""
        headers = {"Authorization": f"Bearer {driver_setup['token']}"}
        
        response = requests.get(f"{BASE_URL}/api/v1/rides/pending/nearby", params={
            "latitude": -8.8383,
            "longitude": 13.2344
        }, headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} pending rides nearby")


class TestRideFlow:
    """Test complete ride flow: request -> accept -> start -> finish"""
    
    @pytest.fixture(scope="class")
    def client_token(self):
        """Get client auth token"""
        return get_auth_token(TEST_CLIENT_PHONE)
    
    @pytest.fixture(scope="class")
    def driver_token(self):
        """Get driver auth token (admin)"""
        return get_auth_token(ADMIN_PHONE)
    
    @pytest.fixture(scope="class")
    def setup_driver(self, driver_token):
        """Ensure driver is registered and approved"""
        headers = {"Authorization": f"Bearer {driver_token}"}
        
        # Check if already a driver
        response = requests.get(f"{BASE_URL}/api/v1/drivers/me", headers=headers)
        
        if response.status_code == 404:
            # Register as driver
            response = requests.post(f"{BASE_URL}/api/v1/drivers/register", json={
                "veiculo": "Toyota Corolla Test",
                "matricula": "LD-TEST-99",
                "cor_veiculo": "Branco",
                "marca": "Toyota",
                "modelo": "Corolla",
                "ano": 2020
            }, headers=headers)
            
            if response.status_code == 201:
                driver = response.json()
                # Approve
                requests.post(f"{BASE_URL}/api/v1/drivers/{driver['id']}/approve", headers=headers)
        
        # Go online
        requests.post(f"{BASE_URL}/api/v1/drivers/me/online", json={
            "online": True,
            "latitude": -8.8383,
            "longitude": 13.2344
        }, headers=headers)
        
        return driver_token
    
    def test_ride_request_creates_ride(self, client_token):
        """POST /api/v1/rides/request creates a new ride"""
        headers = {"Authorization": f"Bearer {client_token}"}
        
        # Cancel any existing ride first
        response = requests.get(f"{BASE_URL}/api/v1/rides/current", headers=headers)
        if response.status_code == 200 and response.json():
            ride = response.json()
            requests.post(f"{BASE_URL}/api/v1/rides/{ride['id']}/cancel", headers=headers)
        
        # Request new ride
        payload = {
            "origem_endereco": "Largo da Mutamba, Luanda Centro",
            "origem_latitude": -8.8383,
            "origem_longitude": 13.2344,
            "destino_endereco": "Aeroporto 4 de Fevereiro, Luanda",
            "destino_latitude": -8.8147,
            "destino_longitude": 13.2302
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/rides/request", json=payload, headers=headers)
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data
        assert data["status"] == "solicitada"
        assert data["origem_endereco"] == payload["origem_endereco"]
        assert data["destino_endereco"] == payload["destino_endereco"]
        print(f"Ride created: {data['id']}, status: {data['status']}")
        
        return data["id"]
    
    def test_full_ride_flow(self, client_token, setup_driver):
        """Test complete ride flow: request -> accept -> start -> finish -> tracking"""
        client_headers = {"Authorization": f"Bearer {client_token}"}
        driver_headers = {"Authorization": f"Bearer {setup_driver}"}
        
        # 1. Cancel any existing ride
        response = requests.get(f"{BASE_URL}/api/v1/rides/current", headers=client_headers)
        if response.status_code == 200 and response.json():
            ride = response.json()
            requests.post(f"{BASE_URL}/api/v1/rides/{ride['id']}/cancel", headers=client_headers)
        
        # 2. Request ride
        payload = {
            "origem_endereco": "Largo da Mutamba, Luanda Centro",
            "origem_latitude": -8.8383,
            "origem_longitude": 13.2344,
            "destino_endereco": "Aeroporto 4 de Fevereiro, Luanda",
            "destino_latitude": -8.8147,
            "destino_longitude": 13.2302
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/rides/request", json=payload, headers=client_headers)
        assert response.status_code == 201, f"Request failed: {response.status_code} - {response.text}"
        ride_id = response.json()["id"]
        print(f"1. Ride requested: {ride_id}")
        
        # 3. Driver accepts ride
        response = requests.post(f"{BASE_URL}/api/v1/rides/{ride_id}/accept", headers=driver_headers)
        assert response.status_code == 200, f"Accept failed: {response.status_code} - {response.text}"
        assert response.json()["status"] == "aceite"
        print(f"2. Ride accepted, status: {response.json()['status']}")
        
        # 4. Add tracking point via REST
        response = requests.post(f"{BASE_URL}/api/v1/rides/{ride_id}/tracking", params={
            "latitude": -8.8390,
            "longitude": 13.2340,
            "speed": 30.5,
            "bearing": 45.0
        }, headers=driver_headers)
        assert response.status_code == 200, f"Tracking failed: {response.status_code} - {response.text}"
        print(f"3. Tracking point added")
        
        # 5. Driver starts ride
        response = requests.post(f"{BASE_URL}/api/v1/rides/{ride_id}/start", headers=driver_headers)
        assert response.status_code == 200, f"Start failed: {response.status_code} - {response.text}"
        assert response.json()["status"] == "em_curso"
        print(f"4. Ride started, status: {response.json()['status']}")
        
        # 6. Add more tracking points
        for i in range(3):
            response = requests.post(f"{BASE_URL}/api/v1/rides/{ride_id}/tracking", params={
                "latitude": -8.8390 + (i * 0.001),
                "longitude": 13.2340 + (i * 0.001),
                "speed": 35.0 + i,
                "bearing": 45.0 + (i * 5)
            }, headers=driver_headers)
            assert response.status_code == 200
        print(f"5. Added 3 more tracking points")
        
        # 7. Driver finishes ride
        response = requests.post(f"{BASE_URL}/api/v1/rides/{ride_id}/finish", headers=driver_headers)
        assert response.status_code == 200, f"Finish failed: {response.status_code} - {response.text}"
        assert response.json()["status"] == "finalizada"
        print(f"6. Ride finished, status: {response.json()['status']}")
        
        # 8. Get tracking history
        response = requests.get(f"{BASE_URL}/api/v1/rides/{ride_id}/tracking", headers=client_headers)
        assert response.status_code == 200, f"Get tracking failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "ride_id" in data
        assert "points" in data
        assert len(data["points"]) >= 4  # At least 4 tracking points
        print(f"7. Tracking history: {len(data['points'])} points")
        
        # Verify tracking point structure
        if data["points"]:
            point = data["points"][0]
            assert "latitude" in point
            assert "longitude" in point
            assert "recorded_at" in point
            print(f"   First point: ({point['latitude']}, {point['longitude']}) at {point['recorded_at']}")


class TestTrackingEndpoints:
    """Test GPS tracking endpoints specifically"""
    
    @pytest.fixture(scope="class")
    def client_token(self):
        return get_auth_token(TEST_CLIENT_PHONE)
    
    @pytest.fixture(scope="class")
    def driver_token(self):
        return get_auth_token(ADMIN_PHONE)
    
    def test_get_tracking_requires_auth(self):
        """GET /api/v1/rides/{ride_id}/tracking requires authentication"""
        fake_ride_id = "00000000-0000-0000-0000-000000000000"
        response = requests.get(f"{BASE_URL}/api/v1/rides/{fake_ride_id}/tracking")
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_post_tracking_requires_driver_role(self, client_token):
        """POST /api/v1/rides/{ride_id}/tracking requires motorista role"""
        headers = {"Authorization": f"Bearer {client_token}"}
        fake_ride_id = "00000000-0000-0000-0000-000000000000"
        
        response = requests.post(f"{BASE_URL}/api/v1/rides/{fake_ride_id}/tracking", params={
            "latitude": -8.8383,
            "longitude": 13.2344
        }, headers=headers)
        
        # Should fail with 403 (not a driver) or 404 (ride not found)
        assert response.status_code in [403, 404], f"Expected 403 or 404, got {response.status_code}: {response.text}"
    
    def test_get_tracking_returns_404_for_nonexistent_ride(self, client_token):
        """GET /api/v1/rides/{ride_id}/tracking returns 404 for nonexistent ride"""
        headers = {"Authorization": f"Bearer {client_token}"}
        fake_ride_id = "00000000-0000-0000-0000-000000000000"
        
        response = requests.get(f"{BASE_URL}/api/v1/rides/{fake_ride_id}/tracking", headers=headers)
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
