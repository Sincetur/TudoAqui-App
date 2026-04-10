"""
TUDOaqui API - Iteration 9 Endpoint Tests
Tests for: marketplace/categories, turismo/bookings/my, events, marketplace/products,
turismo/experiences, alojamento/properties, ws/status, and auth-required endpoints
"""
import pytest
import requests
import os
import subprocess

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://read-store-15.preview.emergentagent.com').rstrip('/')
ADMIN_PHONE = "+244912000000"


def get_otp(phone):
    """Get OTP from database"""
    cmd = f'su - postgres -c "psql -d tudoaqui -t -A -c \\"SELECT codigo FROM otp_codes WHERE telefone=\'{phone}\' AND verificado=false ORDER BY created_at DESC LIMIT 1;\\""'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


def get_auth_token(phone=ADMIN_PHONE):
    """Login and get auth token"""
    # Request OTP
    login_resp = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"telefone": phone})
    if login_resp.status_code not in [200, 429]:
        pytest.skip(f"Login failed: {login_resp.text}")
    
    if login_resp.status_code == 429:
        # Rate limited - try to get existing OTP
        pass
    
    # Get OTP from DB
    otp = get_otp(phone)
    if not otp:
        pytest.skip("Could not retrieve OTP from database")
    
    # Verify OTP
    verify_resp = requests.post(f"{BASE_URL}/api/v1/auth/verify-otp", json={"telefone": phone, "codigo": otp})
    if verify_resp.status_code != 200:
        pytest.skip(f"OTP verification failed: {verify_resp.text}")
    
    return verify_resp.json().get("access_token")


@pytest.fixture(scope="module")
def auth_token():
    """Get auth token for admin user"""
    return get_auth_token()


@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture
def authenticated_client(api_client, auth_token):
    """Session with auth header"""
    api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return api_client


# ============================================
# Health Check
# ============================================

class TestHealth:
    """Health endpoint tests"""
    
    def test_health_check(self, api_client):
        """Test /api/health returns healthy status"""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✓ Health check passed: {data}")


# ============================================
# Marketplace Categories (NEW ENDPOINT)
# ============================================

class TestMarketplaceCategories:
    """Test GET /api/v1/marketplace/categories endpoint"""
    
    def test_list_categories_exists(self, api_client):
        """GET /api/v1/marketplace/categories returns 200"""
        response = api_client.get(f"{BASE_URL}/api/v1/marketplace/categories")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Marketplace categories: {len(data)} categories found")


# ============================================
# Turismo Bookings/My (NEW ENDPOINT)
# ============================================

class TestTurismoBookingsMy:
    """Test GET /api/v1/turismo/bookings/my endpoint"""
    
    def test_bookings_my_requires_auth(self, api_client):
        """GET /api/v1/turismo/bookings/my requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/v1/turismo/bookings/my")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Turismo bookings/my requires auth (401)")
    
    def test_bookings_my_with_auth(self, authenticated_client):
        """GET /api/v1/turismo/bookings/my returns bookings with auth"""
        response = authenticated_client.get(f"{BASE_URL}/api/v1/turismo/bookings/my")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Turismo bookings/my: {len(data)} bookings found")


# ============================================
# Events Endpoints
# ============================================

class TestEvents:
    """Events module tests"""
    
    def test_list_events(self, api_client):
        """GET /api/v1/events returns 200"""
        response = api_client.get(f"{BASE_URL}/api/v1/events")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Events list: {len(data)} events found")
    
    def test_tickets_purchase_requires_auth(self, api_client):
        """POST /api/v1/events/tickets/purchase requires auth"""
        response = api_client.post(f"{BASE_URL}/api/v1/events/tickets/purchase", json={
            "ticket_type_id": "00000000-0000-0000-0000-000000000000",
            "quantidade": 1
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Events tickets/purchase requires auth (401)")


# ============================================
# Marketplace Products
# ============================================

class TestMarketplaceProducts:
    """Marketplace products tests"""
    
    def test_list_products(self, api_client):
        """GET /api/v1/marketplace/products returns 200"""
        response = api_client.get(f"{BASE_URL}/api/v1/marketplace/products")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Marketplace products: {len(data)} products found")
    
    def test_create_order_requires_auth(self, api_client):
        """POST /api/v1/marketplace/orders requires auth"""
        response = api_client.post(f"{BASE_URL}/api/v1/marketplace/orders", json={
            "items": [],
            "endereco_entrega": "Test Address",
            "telefone_contato": "+244912000000"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Marketplace orders requires auth (401)")


# ============================================
# Turismo Experiences
# ============================================

class TestTurismoExperiences:
    """Turismo experiences tests"""
    
    def test_list_experiences(self, api_client):
        """GET /api/v1/turismo/experiences returns 200"""
        response = api_client.get(f"{BASE_URL}/api/v1/turismo/experiences")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Turismo experiences: {len(data)} experiences found")
    
    def test_create_booking_requires_auth(self, api_client):
        """POST /api/v1/turismo/bookings requires auth"""
        response = api_client.post(f"{BASE_URL}/api/v1/turismo/bookings", json={
            "experience_id": "00000000-0000-0000-0000-000000000000",
            "schedule_id": "00000000-0000-0000-0000-000000000000",
            "adultos": 2
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Turismo bookings requires auth (401)")


# ============================================
# Alojamento Properties
# ============================================

class TestAlojamentoProperties:
    """Alojamento properties tests"""
    
    def test_list_properties(self, api_client):
        """GET /api/v1/alojamento/properties returns 200"""
        response = api_client.get(f"{BASE_URL}/api/v1/alojamento/properties")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Alojamento properties: {len(data)} properties found")
    
    def test_create_booking_requires_auth(self, api_client):
        """POST /api/v1/alojamento/bookings requires auth"""
        response = api_client.post(f"{BASE_URL}/api/v1/alojamento/bookings", json={
            "property_id": "00000000-0000-0000-0000-000000000000",
            "data_checkin": "2026-03-01",
            "data_checkout": "2026-03-05",
            "adultos": 2
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Alojamento bookings requires auth (401)")


# ============================================
# WebSocket Status
# ============================================

class TestWebSocketStatus:
    """WebSocket status tests"""
    
    def test_ws_status(self, api_client):
        """GET /api/v1/ws/status returns connection status"""
        response = api_client.get(f"{BASE_URL}/api/v1/ws/status")
        assert response.status_code == 200
        data = response.json()
        assert "total_connections" in data
        assert "online_drivers" in data
        assert "active_rides" in data
        print(f"✓ WebSocket status: {data}")


# ============================================
# Restaurantes Orders
# ============================================

class TestRestaurantesOrders:
    """Restaurantes orders tests"""
    
    def test_list_restaurants(self, api_client):
        """GET /api/v1/restaurantes returns 200"""
        response = api_client.get(f"{BASE_URL}/api/v1/restaurantes")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Restaurantes: {len(data)} restaurants found")
    
    def test_create_order_requires_auth(self, api_client):
        """POST /api/v1/restaurantes/orders requires auth"""
        response = api_client.post(f"{BASE_URL}/api/v1/restaurantes/orders", json={
            "restaurant_id": "00000000-0000-0000-0000-000000000000",
            "items": [],
            "endereco_entrega": "Test Address"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Restaurantes orders requires auth (401)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
