"""
TUDOaqui SuperApp - Backend API Tests with Seed Data Verification
Tests all public endpoints and verifies seed data is present
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndDocs:
    """Health check and documentation endpoints"""
    
    def test_health_endpoint(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["app"] == "TUDOaqui API"
        print(f"✓ Health check passed: {data}")

class TestEventsAPI:
    """Events module API tests"""
    
    def test_list_events_returns_seed_data(self):
        """Test GET /api/v1/events returns 5 seeded events"""
        response = requests.get(f"{BASE_URL}/api/v1/events")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 5, f"Expected 5 events, got {len(data)}"
        
        # Verify event structure
        event = data[0]
        assert "titulo" in event
        assert "local" in event
        assert "data_evento" in event
        print(f"✓ Events API returned {len(data)} events")
        
        # Check for specific seeded events
        titles = [e["titulo"] for e in data]
        assert any("Semba" in t for t in titles), "Missing 'Noite de Semba e Kizomba' event"
        print(f"✓ Seed events verified: {titles[:2]}...")

class TestMarketplaceAPI:
    """Marketplace module API tests"""
    
    def test_list_products_returns_seed_data(self):
        """Test GET /api/v1/marketplace/products returns 8 seeded products"""
        response = requests.get(f"{BASE_URL}/api/v1/marketplace/products")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 8, f"Expected 8 products, got {len(data)}"
        
        # Verify product structure
        product = data[0]
        assert "nome" in product
        assert "preco" in product
        assert "stock" in product
        print(f"✓ Marketplace API returned {len(data)} products")
    
    def test_list_categories_returns_seed_data(self):
        """Test GET /api/v1/marketplace/categories returns 5 categories"""
        response = requests.get(f"{BASE_URL}/api/v1/marketplace/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 5, f"Expected 5 categories, got {len(data)}"
        print(f"✓ Categories API returned {len(data)} categories")

class TestAlojamentoAPI:
    """Alojamento (accommodation) module API tests"""
    
    def test_list_properties_returns_seed_data(self):
        """Test GET /api/v1/alojamento/properties returns 4 seeded properties"""
        response = requests.get(f"{BASE_URL}/api/v1/alojamento/properties")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 4, f"Expected 4 properties, got {len(data)}"
        
        # Verify property structure
        prop = data[0]
        assert "titulo" in prop
        assert "preco_noite" in prop
        assert "quartos" in prop
        print(f"✓ Alojamento API returned {len(data)} properties")

class TestTurismoAPI:
    """Turismo (tourism) module API tests"""
    
    def test_list_experiences_returns_seed_data(self):
        """Test GET /api/v1/turismo/experiences returns 4 seeded experiences"""
        response = requests.get(f"{BASE_URL}/api/v1/turismo/experiences")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 4, f"Expected 4 experiences, got {len(data)}"
        
        # Verify experience structure
        exp = data[0]
        assert "titulo" in exp
        assert "preco" in exp
        assert "duracao_horas" in exp
        print(f"✓ Turismo API returned {len(data)} experiences")

class TestRealEstateAPI:
    """Real estate module API tests"""
    
    def test_list_imoveis_returns_seed_data(self):
        """Test GET /api/v1/realestate/properties returns 5 seeded properties"""
        response = requests.get(f"{BASE_URL}/api/v1/realestate/properties")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 5, f"Expected 5 real estate properties, got {len(data)}"
        
        # Verify property structure
        prop = data[0]
        assert "titulo" in prop
        assert "tipo_transacao" in prop
        assert "quartos" in prop
        print(f"✓ Real Estate API returned {len(data)} properties")
    
    def test_list_agents_returns_seed_data(self):
        """Test GET /api/v1/realestate/agents returns 1 seeded agent"""
        response = requests.get(f"{BASE_URL}/api/v1/realestate/agents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1, f"Expected 1 agent, got {len(data)}"
        
        # Verify agent structure
        agent = data[0]
        assert "nome_profissional" in agent
        assert agent["nome_profissional"] == "Sofia Neto"
        print(f"✓ Agents API returned {len(data)} agent: {agent['nome_profissional']}")

class TestRestaurantesAPI:
    """Restaurantes module API tests"""
    
    def test_list_restaurants_returns_seed_data(self):
        """Test GET /api/v1/restaurantes returns 3 seeded restaurants"""
        response = requests.get(f"{BASE_URL}/api/v1/restaurantes")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3, f"Expected 3 restaurants, got {len(data)}"
        
        # Verify restaurant structure
        restaurant = data[0]
        assert "nome" in restaurant
        assert "categorias" in restaurant
        assert "rating_medio" in restaurant
        
        # Check for specific restaurants
        names = [r["nome"] for r in data]
        assert "Muamba da Mama" in names, "Missing 'Muamba da Mama' restaurant"
        assert "Sushi Lounge Luanda" in names, "Missing 'Sushi Lounge Luanda' restaurant"
        assert "Burger Republic" in names, "Missing 'Burger Republic' restaurant"
        print(f"✓ Restaurantes API returned {len(data)} restaurants: {names}")
    
    def test_get_restaurant_menu(self):
        """Test GET /api/v1/restaurantes/{id}/menu returns menu items"""
        # First get restaurant list to get an ID
        response = requests.get(f"{BASE_URL}/api/v1/restaurantes")
        assert response.status_code == 200
        restaurants = response.json()
        
        if len(restaurants) > 0:
            restaurant_id = restaurants[0]["id"]
            menu_response = requests.get(f"{BASE_URL}/api/v1/restaurantes/{restaurant_id}/menu")
            assert menu_response.status_code == 200
            menu = menu_response.json()
            assert isinstance(menu, list)
            assert len(menu) > 0, "Menu should have categories"
            
            # Verify menu structure
            category = menu[0]
            assert "nome" in category
            assert "items" in category
            print(f"✓ Menu API returned {len(menu)} categories with items")

class TestEntregasAPI:
    """Entregas (deliveries) module API tests"""
    
    def test_estimate_delivery_requires_auth(self):
        """Test POST /api/v1/entregas/estimate requires authentication"""
        response = requests.post(f"{BASE_URL}/api/v1/entregas/estimate", json={
            "origem_latitude": -8.839,
            "origem_longitude": 13.289,
            "destino_latitude": -8.913,
            "destino_longitude": 13.202,
            "tipo": "pacote_pequeno",
            "prioridade": "normal"
        })
        assert response.status_code == 401, "Estimate endpoint should require auth"
        print("✓ Entregas estimate correctly requires authentication")

class TestAuthAPI:
    """Authentication API tests"""
    
    def test_login_sends_otp(self):
        """Test POST /api/v1/auth/login sends OTP"""
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
            "telefone": "+244999888777"  # Test phone
        })
        # May get 200 (success) or 429 (rate limited)
        assert response.status_code in [200, 429], f"Unexpected status: {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            assert "message" in data
            print(f"✓ Login API works: {data['message']}")
        else:
            print("✓ Login API rate limited (expected behavior)")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
