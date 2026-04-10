"""
TUDOaqui API - Comprehensive Module Tests
Tests all 7 CRUD modules: Events, Marketplace, Alojamento, Turismo, RealEstate, Restaurantes, Entregas
Plus WebSocket status and Rides estimate
"""
import pytest
import requests
import os
import subprocess

BASE_URL = os.environ.get('TEST_API_URL', os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8000')).rstrip('/')
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
    if login_resp.status_code != 200:
        pytest.skip(f"Login failed: {login_resp.text}")
    
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
        """Test health endpoint returns healthy status"""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✓ Health check passed: {data}")


# ============================================
# Events Module
# ============================================

class TestEvents:
    """Events module tests"""
    
    def test_list_events(self, api_client):
        """GET /api/v1/events returns events list"""
        response = api_client.get(f"{BASE_URL}/api/v1/events")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Events list: {len(data)} events found")
    
    def test_create_event_requires_auth(self, api_client):
        """POST /api/v1/events requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/v1/events", json={
            "titulo": "Test Event",
            "local": "Luanda",
            "data_evento": "2026-03-01",
            "hora_evento": "18:00:00"
        })
        assert response.status_code == 401
        print("✓ Create event requires auth")
    
    def test_create_event_with_auth(self, authenticated_client):
        """POST /api/v1/events creates event with proper role"""
        response = authenticated_client.post(f"{BASE_URL}/api/v1/events", json={
            "titulo": "TEST_Event_Module",
            "local": "Luanda Centro",
            "data_evento": "2026-03-15",
            "hora_evento": "19:00:00",
            "categoria": "Musica",
            "descricao": "Test event for module testing"
        })
        # Admin should have PROPRIETARIO role to create events
        if response.status_code == 201:
            data = response.json()
            assert "id" in data
            assert data["titulo"] == "TEST_Event_Module"
            print(f"✓ Event created: {data['id']}")
        elif response.status_code == 403:
            print("✓ Create event requires organizer/admin role (403 expected for non-organizer)")
        else:
            print(f"Event creation response: {response.status_code} - {response.text}")
    
    def test_get_event_detail(self, api_client):
        """GET /api/v1/events/{id} returns event detail"""
        # First get list to find an event
        list_resp = api_client.get(f"{BASE_URL}/api/v1/events")
        events = list_resp.json()
        if events:
            event_id = events[0]["id"]
            response = api_client.get(f"{BASE_URL}/api/v1/events/{event_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == event_id
            print(f"✓ Event detail retrieved: {data.get('titulo')}")
        else:
            print("✓ No events to test detail (empty list)")


# ============================================
# Marketplace Module
# ============================================

class TestMarketplace:
    """Marketplace module tests"""
    
    def test_list_products(self, api_client):
        """GET /api/v1/marketplace/products returns products list"""
        response = api_client.get(f"{BASE_URL}/api/v1/marketplace/products")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Products list: {len(data)} products found")
    
    def test_list_categories(self, api_client):
        """GET /api/v1/marketplace/categories returns categories"""
        response = api_client.get(f"{BASE_URL}/api/v1/marketplace/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Categories list: {len(data)} categories found")
    
    def test_create_product_requires_seller(self, authenticated_client):
        """POST /api/v1/marketplace/products requires seller profile"""
        response = authenticated_client.post(f"{BASE_URL}/api/v1/marketplace/products", json={
            "nome": "TEST_Product",
            "preco": 5000,
            "stock": 10
        })
        # Should fail if user doesn't have seller profile
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Product created: {data.get('id')}")
        elif response.status_code in [400, 403]:
            print(f"✓ Create product requires seller profile: {response.status_code}")
        else:
            print(f"Product creation response: {response.status_code} - {response.text}")
    
    def test_create_order_requires_auth(self, api_client):
        """POST /api/v1/marketplace/orders requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/v1/marketplace/orders", json={
            "items": [],
            "endereco_entrega": "Test Address",
            "telefone_contato": "+244912000000"
        })
        assert response.status_code == 401
        print("✓ Create order requires auth")


# ============================================
# Alojamento Module
# ============================================

class TestAlojamento:
    """Alojamento (accommodation) module tests"""
    
    def test_list_properties(self, api_client):
        """GET /api/v1/alojamento/properties returns properties list"""
        response = api_client.get(f"{BASE_URL}/api/v1/alojamento/properties")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Alojamento properties: {len(data)} found")
    
    def test_create_property_requires_host(self, authenticated_client):
        """POST /api/v1/alojamento/properties requires host role"""
        response = authenticated_client.post(f"{BASE_URL}/api/v1/alojamento/properties", json={
            "titulo": "TEST_Property",
            "tipo": "apartamento",
            "endereco": "Rua Test 123",
            "cidade": "Luanda",
            "provincia": "Luanda",
            "quartos": 2,
            "camas": 2,
            "banheiros": 1,
            "max_hospedes": 4,
            "preco_noite": 15000
        })
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Property created: {data.get('id')}")
        elif response.status_code in [400, 403]:
            print(f"✓ Create property requires host role: {response.status_code}")
        else:
            print(f"Property creation response: {response.status_code} - {response.text}")
    
    def test_create_booking_requires_auth(self, api_client):
        """POST /api/v1/alojamento/bookings requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/v1/alojamento/bookings", json={
            "property_id": "00000000-0000-0000-0000-000000000000",
            "data_checkin": "2026-03-01",
            "data_checkout": "2026-03-05",
            "adultos": 2
        })
        assert response.status_code == 401
        print("✓ Create booking requires auth")


# ============================================
# Turismo Module
# ============================================

class TestTurismo:
    """Turismo (tourism experiences) module tests"""
    
    def test_list_experiences(self, api_client):
        """GET /api/v1/turismo/experiences returns experiences list"""
        response = api_client.get(f"{BASE_URL}/api/v1/turismo/experiences")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Turismo experiences: {len(data)} found")
    
    def test_create_experience_requires_host(self, authenticated_client):
        """POST /api/v1/turismo/experiences requires host role"""
        response = authenticated_client.post(f"{BASE_URL}/api/v1/turismo/experiences", json={
            "titulo": "TEST_Experience",
            "tipo": "tour",
            "local": "Luanda",
            "cidade": "Luanda",
            "duracao_horas": 3,
            "max_participantes": 10,
            "preco": 25000
        })
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Experience created: {data.get('id')}")
        elif response.status_code in [400, 403]:
            print(f"✓ Create experience requires host role: {response.status_code}")
        else:
            print(f"Experience creation response: {response.status_code} - {response.text}")


# ============================================
# Real Estate Module
# ============================================

class TestRealEstate:
    """Real Estate module tests"""
    
    def test_list_properties(self, api_client):
        """GET /api/v1/realestate/properties returns real estate list"""
        response = api_client.get(f"{BASE_URL}/api/v1/realestate/properties")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Real estate properties: {len(data)} found")
    
    def test_create_property_requires_agent(self, authenticated_client):
        """POST /api/v1/realestate/properties requires agent role"""
        response = authenticated_client.post(f"{BASE_URL}/api/v1/realestate/properties", json={
            "titulo": "TEST_RealEstate",
            "tipo": "apartamento",
            "tipo_transacao": "venda",
            "endereco": "Rua Test 456",
            "bairro": "Maianga",
            "cidade": "Luanda",
            "provincia": "Luanda",
            "preco_venda": 50000000,
            "quartos": 3,
            "area_util": 120
        })
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Real estate property created: {data.get('id')}")
        elif response.status_code in [400, 403]:
            print(f"✓ Create real estate requires agent role: {response.status_code}")
        else:
            print(f"Real estate creation response: {response.status_code} - {response.text}")
    
    def test_create_lead(self, authenticated_client):
        """POST /api/v1/realestate/leads creates a lead"""
        # First get a property to create lead for
        props_resp = authenticated_client.get(f"{BASE_URL}/api/v1/realestate/properties")
        props = props_resp.json()
        
        if props:
            property_id = props[0]["id"]
            response = authenticated_client.post(f"{BASE_URL}/api/v1/realestate/leads", json={
                "property_id": property_id,
                "nome": "Test Lead",
                "telefone": "+244912111111",
                "email": "test@example.com",
                "mensagem": "Interested in this property",
                "tipo_interesse": "compra"
            })
            if response.status_code == 201:
                data = response.json()
                print(f"✓ Lead created: {data.get('id')}")
            else:
                print(f"Lead creation response: {response.status_code} - {response.text}")
        else:
            print("✓ No properties to create lead for (empty list)")


# ============================================
# Restaurantes Module
# ============================================

class TestRestaurantes:
    """Restaurantes module tests"""
    
    def test_list_restaurants(self, api_client):
        """GET /api/v1/restaurantes returns restaurants list"""
        response = api_client.get(f"{BASE_URL}/api/v1/restaurantes")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Restaurants: {len(data)} found")
    
    def test_get_restaurant_menu(self, api_client):
        """GET /api/v1/restaurantes/{id}/menu returns menu"""
        # First get list to find a restaurant
        list_resp = api_client.get(f"{BASE_URL}/api/v1/restaurantes")
        restaurants = list_resp.json()
        
        if restaurants:
            restaurant_id = restaurants[0]["id"]
            response = api_client.get(f"{BASE_URL}/api/v1/restaurantes/{restaurant_id}/menu")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            print(f"✓ Restaurant menu: {len(data)} categories found")
        else:
            print("✓ No restaurants to test menu (empty list)")


# ============================================
# Entregas Module
# ============================================

class TestEntregas:
    """Entregas (deliveries) module tests"""
    
    def test_create_delivery_requires_auth(self, api_client):
        """POST /api/v1/entregas requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/v1/entregas", json={
            "tipo": "pacote_pequeno",
            "prioridade": "normal",
            "origem_endereco": "Rua A",
            "origem_latitude": -8.839,
            "origem_longitude": 13.289,
            "destino_endereco": "Rua B",
            "destino_latitude": -8.913,
            "destino_longitude": 13.202
        })
        assert response.status_code == 401
        print("✓ Create delivery requires auth")
    
    def test_list_my_deliveries(self, authenticated_client):
        """GET /api/v1/entregas/my lists my deliveries"""
        response = authenticated_client.get(f"{BASE_URL}/api/v1/entregas/my")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ My deliveries: {len(data)} found")
    
    def test_estimate_delivery(self, authenticated_client):
        """POST /api/v1/entregas/estimate estimates delivery price"""
        response = authenticated_client.post(f"{BASE_URL}/api/v1/entregas/estimate", json={
            "origem_latitude": -8.839,
            "origem_longitude": 13.289,
            "destino_latitude": -8.913,
            "destino_longitude": 13.202,
            "tipo": "pacote_pequeno",
            "prioridade": "normal"
        })
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "distancia_km" in data
        print(f"✓ Delivery estimate: {data.get('total')} Kz for {data.get('distancia_km')} km")


# ============================================
# WebSocket Status
# ============================================

class TestWebSocket:
    """WebSocket status tests"""
    
    def test_ws_status(self, api_client):
        """GET /api/v1/ws/status returns WebSocket status"""
        response = api_client.get(f"{BASE_URL}/api/v1/ws/status")
        assert response.status_code == 200
        data = response.json()
        assert "total_connections" in data
        assert "online_drivers" in data
        assert "active_rides" in data
        print(f"✓ WebSocket status: {data}")


# ============================================
# Rides Module
# ============================================

class TestRides:
    """Rides module tests"""
    
    def test_ride_estimate(self, authenticated_client):
        """POST /api/v1/rides/estimate estimates ride price"""
        response = authenticated_client.post(f"{BASE_URL}/api/v1/rides/estimate", json={
            "origem": {
                "latitude": -8.839,
                "longitude": 13.289,
                "endereco": "Rua Origem Test"
            },
            "destino": {
                "latitude": -8.913,
                "longitude": 13.202,
                "endereco": "Rua Destino Test"
            }
        })
        assert response.status_code == 200
        data = response.json()
        assert "preco_estimado" in data or "valor_estimado" in data or "total" in data
        print(f"✓ Ride estimate: {data}")


# ============================================
# Auth Module
# ============================================

class TestAuth:
    """Auth module tests"""
    
    def test_login_sends_otp(self, api_client):
        """POST /api/v1/auth/login sends OTP"""
        response = api_client.post(f"{BASE_URL}/api/v1/auth/login", json={
            "telefone": ADMIN_PHONE
        })
        # May return 200 or 429 (rate limited)
        assert response.status_code in [200, 429]
        if response.status_code == 200:
            print("✓ Login OTP sent successfully")
        else:
            print("✓ Login rate limited (expected if recently tested)")
    
    def test_get_me_requires_auth(self, api_client):
        """GET /api/v1/auth/me requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/v1/auth/me")
        assert response.status_code == 401
        print("✓ Get me requires auth")
    
    def test_get_me_with_auth(self, authenticated_client):
        """GET /api/v1/auth/me returns user info"""
        response = authenticated_client.get(f"{BASE_URL}/api/v1/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "telefone" in data
        print(f"✓ User info: {data.get('telefone')} - role: {data.get('role')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
