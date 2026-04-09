"""
TUDOaqui SuperApp - Backend API Tests
Tests for all modules: auth, events, marketplace, alojamento, turismo, realestate, entrega, restaurante, drivers
"""
import pytest
import requests
import os
import subprocess

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test phone number
TEST_PHONE = "+244923456789"


def get_otp_from_db(telefone: str) -> str:
    """Get OTP from PostgreSQL database"""
    cmd = f'''su - postgres -c "psql -t -A -d tudoaqui -c \\"SELECT codigo FROM otp_codes WHERE telefone='{telefone}' AND verificado=false ORDER BY created_at DESC LIMIT 1;\\""'''
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    otp = result.stdout.strip()
    return otp


class TestHealthEndpoint:
    """Health check endpoint tests"""
    
    def test_health_check(self):
        """GET /api/health should return healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "app" in data
        assert "version" in data
        print(f"✅ Health check passed: {data}")


class TestOpenAPIDocs:
    """OpenAPI documentation tests"""
    
    def test_docs_accessible(self):
        """GET /docs should return HTML documentation"""
        response = requests.get(f"{BASE_URL}/docs")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "text/html" in response.headers.get("content-type", "")
        print("✅ OpenAPI docs accessible")


class TestAuthFlow:
    """Authentication flow tests - OTP based"""
    
    def test_login_sends_otp(self):
        """POST /api/v1/auth/login should send OTP"""
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"telefone": TEST_PHONE}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "telefone" in data
        assert "expires_in_seconds" in data
        print(f"✅ Login OTP sent: {data}")
    
    def test_verify_otp_and_get_token(self):
        """POST /api/v1/auth/verify-otp should return tokens"""
        # First, request OTP
        login_response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"telefone": TEST_PHONE}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        
        # Get OTP from database
        otp = get_otp_from_db(TEST_PHONE)
        assert otp, "Failed to get OTP from database"
        print(f"📱 OTP retrieved from DB: {otp}")
        
        # Verify OTP
        verify_response = requests.post(
            f"{BASE_URL}/api/v1/auth/verify-otp",
            json={"telefone": TEST_PHONE, "codigo": otp}
        )
        assert verify_response.status_code == 200, f"Expected 200, got {verify_response.status_code}: {verify_response.text}"
        
        data = verify_response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        print(f"✅ OTP verified, token received. User: {data['user']}")
        return data["access_token"]
    
    def test_auth_me_with_token(self):
        """GET /api/v1/auth/me should return user info with valid token"""
        # Get token first
        token = self.test_verify_otp_and_get_token()
        
        # Call /me endpoint
        response = requests.get(
            f"{BASE_URL}/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data
        assert "telefone" in data
        print(f"✅ Auth /me passed: {data}")
    
    def test_auth_me_without_token(self):
        """GET /api/v1/auth/me should return 401 without token"""
        response = requests.get(f"{BASE_URL}/api/v1/auth/me")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ Auth /me correctly returns 401 without token")


# Helper to get auth token
def get_auth_token() -> str:
    """Helper function to get auth token for authenticated tests"""
    # Request OTP
    requests.post(f"{BASE_URL}/api/v1/auth/login", json={"telefone": TEST_PHONE})
    
    # Get OTP from DB
    otp = get_otp_from_db(TEST_PHONE)
    if not otp:
        pytest.skip("Could not get OTP from database")
    
    # Verify OTP
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/verify-otp",
        json={"telefone": TEST_PHONE, "codigo": otp}
    )
    if response.status_code != 200:
        pytest.skip(f"Could not get auth token: {response.text}")
    
    return response.json()["access_token"]


class TestEventsModule:
    """Events module tests"""
    
    def test_list_events_public(self):
        """GET /api/v1/events should return list (may be empty)"""
        response = requests.get(f"{BASE_URL}/api/v1/events")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Events list returned: {len(data)} events")
    
    def test_list_events_with_auth(self):
        """GET /api/v1/events with auth should work"""
        token = get_auth_token()
        response = requests.get(
            f"{BASE_URL}/api/v1/events",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✅ Events list with auth passed")


class TestMarketplaceModule:
    """Marketplace module tests"""
    
    def test_list_products_public(self):
        """GET /api/v1/marketplace/products should return list"""
        response = requests.get(f"{BASE_URL}/api/v1/marketplace/products")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Marketplace products list returned: {len(data)} products")
    
    def test_list_sellers_public(self):
        """GET /api/v1/marketplace/sellers should return list"""
        response = requests.get(f"{BASE_URL}/api/v1/marketplace/sellers")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Marketplace sellers list returned: {len(data)} sellers")
    
    def test_list_categories_public(self):
        """GET /api/v1/marketplace/categories should return list"""
        response = requests.get(f"{BASE_URL}/api/v1/marketplace/categories")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Marketplace categories list returned: {len(data)} categories")


class TestAlojamentoModule:
    """Alojamento (accommodation) module tests"""
    
    def test_list_properties_public(self):
        """GET /api/v1/alojamento/properties should return list"""
        response = requests.get(f"{BASE_URL}/api/v1/alojamento/properties")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Alojamento properties list returned: {len(data)} properties")


class TestTurismoModule:
    """Turismo (tourism) module tests"""
    
    def test_list_experiences_public(self):
        """GET /api/v1/turismo/experiences should return list"""
        response = requests.get(f"{BASE_URL}/api/v1/turismo/experiences")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Turismo experiences list returned: {len(data)} experiences")


class TestRealEstateModule:
    """Real Estate module tests"""
    
    def test_list_properties_public(self):
        """GET /api/v1/realestate/properties should return list"""
        response = requests.get(f"{BASE_URL}/api/v1/realestate/properties")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Real Estate properties list returned: {len(data)} properties")
    
    def test_list_agents_public(self):
        """GET /api/v1/realestate/agents should return list"""
        response = requests.get(f"{BASE_URL}/api/v1/realestate/agents")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Real Estate agents list returned: {len(data)} agents")


class TestEntregaModule:
    """Tuendi Entrega (delivery) module tests"""
    
    def test_estimate_delivery_requires_auth(self):
        """POST /api/v1/entregas/estimate should require auth"""
        response = requests.post(
            f"{BASE_URL}/api/v1/entregas/estimate",
            json={
                "origem_latitude": -8.8383,
                "origem_longitude": 13.2344,
                "destino_latitude": -8.8500,
                "destino_longitude": 13.2500,
                "tipo": "pacote",
                "prioridade": "normal"
            }
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("✅ Entregas estimate correctly requires auth")
    
    def test_estimate_delivery_with_auth(self):
        """POST /api/v1/entregas/estimate with auth should work"""
        token = get_auth_token()
        response = requests.post(
            f"{BASE_URL}/api/v1/entregas/estimate",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "origem_latitude": -8.8383,
                "origem_longitude": 13.2344,
                "destino_latitude": -8.8500,
                "destino_longitude": 13.2500,
                "tipo": "pacote",
                "prioridade": "normal"
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "distancia_km" in data
        assert "total" in data
        print(f"✅ Entregas estimate passed: {data}")


class TestRestauranteModule:
    """Tuendi Restaurante module tests"""
    
    def test_list_restaurants_public(self):
        """GET /api/v1/restaurantes should return list (public endpoint)"""
        response = requests.get(f"{BASE_URL}/api/v1/restaurantes")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Restaurantes list returned: {len(data)} restaurants")


class TestDriversModule:
    """Tuendi Drivers module tests"""
    
    def test_register_driver_requires_auth(self):
        """POST /api/v1/drivers/register should require auth"""
        response = requests.post(
            f"{BASE_URL}/api/v1/drivers/register",
            json={
                "veiculo": "carro",
                "matricula": "LD-00-00-AA",
                "marca": "Toyota",
                "modelo": "Corolla",
                "ano": 2020,
                "cor": "Branco"
            }
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("✅ Drivers register correctly requires auth")
    
    def test_register_driver_with_auth(self):
        """POST /api/v1/drivers/register with auth should work or return appropriate error"""
        token = get_auth_token()
        response = requests.post(
            f"{BASE_URL}/api/v1/drivers/register",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "veiculo": "carro",
                "matricula": "LD-00-00-AA",
                "marca": "Toyota",
                "modelo": "Corolla",
                "ano": 2020,
                "cor": "Branco"
            }
        )
        # Could be 201 (created), 200 (already exists), or 400 (validation error)
        assert response.status_code in [200, 201, 400], f"Expected 200/201/400, got {response.status_code}: {response.text}"
        print(f"✅ Drivers register with auth: status {response.status_code}")


class TestAuthenticatedEndpoints:
    """Tests for endpoints that require authentication"""
    
    def test_my_tickets_requires_auth(self):
        """GET /api/v1/events/tickets/my should require auth"""
        response = requests.get(f"{BASE_URL}/api/v1/events/tickets/my")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ Events tickets/my correctly requires auth")
    
    def test_my_orders_marketplace_requires_auth(self):
        """GET /api/v1/marketplace/orders/my should require auth"""
        response = requests.get(f"{BASE_URL}/api/v1/marketplace/orders/my")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ Marketplace orders/my correctly requires auth")
    
    def test_my_bookings_alojamento_requires_auth(self):
        """GET /api/v1/alojamento/bookings/my should require auth"""
        response = requests.get(f"{BASE_URL}/api/v1/alojamento/bookings/my")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ Alojamento bookings/my correctly requires auth")
    
    def test_my_bookings_turismo_requires_auth(self):
        """GET /api/v1/turismo/bookings/my should require auth"""
        response = requests.get(f"{BASE_URL}/api/v1/turismo/bookings/my")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ Turismo bookings/my correctly requires auth")
    
    def test_my_favorites_realestate_requires_auth(self):
        """GET /api/v1/realestate/favorites should require auth"""
        response = requests.get(f"{BASE_URL}/api/v1/realestate/favorites")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ Real Estate favorites correctly requires auth")
    
    def test_my_deliveries_requires_auth(self):
        """GET /api/v1/entregas/my should require auth"""
        response = requests.get(f"{BASE_URL}/api/v1/entregas/my")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ Entregas /my correctly requires auth")


class TestAuthenticatedEndpointsWithToken:
    """Tests for authenticated endpoints with valid token"""
    
    def test_my_tickets_with_auth(self):
        """GET /api/v1/events/tickets/my with auth should return list"""
        token = get_auth_token()
        response = requests.get(
            f"{BASE_URL}/api/v1/events/tickets/my",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Events tickets/my with auth: {len(data)} tickets")
    
    def test_my_orders_marketplace_with_auth(self):
        """GET /api/v1/marketplace/orders/my with auth should return list"""
        token = get_auth_token()
        response = requests.get(
            f"{BASE_URL}/api/v1/marketplace/orders/my",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Marketplace orders/my with auth: {len(data)} orders")
    
    def test_my_bookings_alojamento_with_auth(self):
        """GET /api/v1/alojamento/bookings/my with auth should return list"""
        token = get_auth_token()
        response = requests.get(
            f"{BASE_URL}/api/v1/alojamento/bookings/my",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Alojamento bookings/my with auth: {len(data)} bookings")
    
    def test_my_bookings_turismo_with_auth(self):
        """GET /api/v1/turismo/bookings/my with auth should return list"""
        token = get_auth_token()
        response = requests.get(
            f"{BASE_URL}/api/v1/turismo/bookings/my",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Turismo bookings/my with auth: {len(data)} bookings")
    
    def test_my_favorites_realestate_with_auth(self):
        """GET /api/v1/realestate/favorites with auth should return list"""
        token = get_auth_token()
        response = requests.get(
            f"{BASE_URL}/api/v1/realestate/favorites",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Real Estate favorites with auth: {len(data)} favorites")
    
    def test_my_deliveries_with_auth(self):
        """GET /api/v1/entregas/my with auth should return list"""
        token = get_auth_token()
        response = requests.get(
            f"{BASE_URL}/api/v1/entregas/my",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Entregas /my with auth: {len(data)} deliveries")
    
    def test_my_orders_restaurante_with_auth(self):
        """GET /api/v1/restaurantes/orders/my with auth should return list"""
        token = get_auth_token()
        response = requests.get(
            f"{BASE_URL}/api/v1/restaurantes/orders/my",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Restaurantes orders/my with auth: {len(data)} orders")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
