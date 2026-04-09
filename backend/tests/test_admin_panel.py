"""
TUDOaqui Admin Panel API Tests
Tests for admin endpoints: stats, users, role/status changes, content listing
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAdminAuth:
    """Test admin authentication and authorization"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token via OTP flow"""
        admin_phone = "+244912000000"
        
        # Step 1: Request OTP
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"telefone": admin_phone})
        assert response.status_code == 200, f"Failed to request OTP: {response.text}"
        
        # Step 2: Get OTP from database
        import subprocess
        result = subprocess.run(
            ['su', '-', 'postgres', '-c', 
             f'psql -d tudoaqui -t -A -c "SELECT codigo FROM otp_codes WHERE telefone=\'{admin_phone}\' AND verificado=false ORDER BY created_at DESC LIMIT 1;"'],
            capture_output=True, text=True
        )
        otp = result.stdout.strip()
        assert otp, f"Failed to get OTP from database: {result.stderr}"
        
        # Step 3: Verify OTP
        response = requests.post(f"{BASE_URL}/api/v1/auth/verify-otp", json={"telefone": admin_phone, "codigo": otp})
        assert response.status_code == 200, f"Failed to verify OTP: {response.text}"
        
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        return data["access_token"]
    
    @pytest.fixture(scope="class")
    def cliente_token(self):
        """Get regular cliente token via OTP flow"""
        cliente_phone = "+244923456789"
        
        # Step 1: Request OTP
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"telefone": cliente_phone})
        assert response.status_code == 200, f"Failed to request OTP: {response.text}"
        
        # Step 2: Get OTP from database
        import subprocess
        result = subprocess.run(
            ['su', '-', 'postgres', '-c', 
             f'psql -d tudoaqui -t -A -c "SELECT codigo FROM otp_codes WHERE telefone=\'{cliente_phone}\' AND verificado=false ORDER BY created_at DESC LIMIT 1;"'],
            capture_output=True, text=True
        )
        otp = result.stdout.strip()
        assert otp, f"Failed to get OTP from database: {result.stderr}"
        
        # Step 3: Verify OTP
        response = requests.post(f"{BASE_URL}/api/v1/auth/verify-otp", json={"telefone": cliente_phone, "codigo": otp})
        assert response.status_code == 200, f"Failed to verify OTP: {response.text}"
        
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        return data["access_token"]
    
    def test_admin_me_returns_admin_role(self, admin_token):
        """Verify admin user has role=admin"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "admin", f"Expected admin role, got {data['role']}"
        assert data["telefone"] == "+244912000000"
    
    def test_cliente_cannot_access_admin_stats(self, cliente_token):
        """Regular cliente should get 403 on admin endpoints"""
        headers = {"Authorization": f"Bearer {cliente_token}"}
        response = requests.get(f"{BASE_URL}/api/v1/admin/stats", headers=headers)
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
    
    def test_cliente_cannot_access_admin_users(self, cliente_token):
        """Regular cliente should get 403 on admin users endpoint"""
        headers = {"Authorization": f"Bearer {cliente_token}"}
        response = requests.get(f"{BASE_URL}/api/v1/admin/users", headers=headers)
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"


class TestAdminStats:
    """Test GET /api/v1/admin/stats endpoint"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token via OTP flow"""
        admin_phone = "+244912000000"
        
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"telefone": admin_phone})
        assert response.status_code == 200
        
        import subprocess
        result = subprocess.run(
            ['su', '-', 'postgres', '-c', 
             f'psql -d tudoaqui -t -A -c "SELECT codigo FROM otp_codes WHERE telefone=\'{admin_phone}\' AND verificado=false ORDER BY created_at DESC LIMIT 1;"'],
            capture_output=True, text=True
        )
        otp = result.stdout.strip()
        
        response = requests.post(f"{BASE_URL}/api/v1/auth/verify-otp", json={"telefone": admin_phone, "codigo": otp})
        return response.json()["access_token"]
    
    def test_admin_stats_returns_totais(self, admin_token):
        """Admin stats should return totais with correct counts"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/v1/admin/stats", headers=headers)
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "totais" in data, "Missing 'totais' in response"
        assert "roles" in data, "Missing 'roles' in response"
        
        # Verify totais keys
        totais = data["totais"]
        expected_keys = ["users", "events", "products", "alojamento", "turismo", "imoveis", "restaurantes"]
        for key in expected_keys:
            assert key in totais, f"Missing '{key}' in totais"
        
        # Verify expected counts (from seed data)
        assert totais["users"] == 8, f"Expected 8 users, got {totais['users']}"
        assert totais["events"] == 5, f"Expected 5 events, got {totais['events']}"
        assert totais["restaurantes"] == 3, f"Expected 3 restaurants, got {totais['restaurantes']}"
    
    def test_admin_stats_returns_role_distribution(self, admin_token):
        """Admin stats should return role distribution"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/v1/admin/stats", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        roles = data["roles"]
        
        # Verify role counts match database
        assert roles.get("admin", 0) == 1, f"Expected 1 admin, got {roles.get('admin', 0)}"
        assert roles.get("cliente", 0) == 1, f"Expected 1 cliente, got {roles.get('cliente', 0)}"
        assert roles.get("organizador", 0) == 1, f"Expected 1 organizador, got {roles.get('organizador', 0)}"
        assert roles.get("vendedor", 0) == 2, f"Expected 2 vendedor, got {roles.get('vendedor', 0)}"
        assert roles.get("anfitriao", 0) == 2, f"Expected 2 anfitriao, got {roles.get('anfitriao', 0)}"
        assert roles.get("agente", 0) == 1, f"Expected 1 agente, got {roles.get('agente', 0)}"


class TestAdminUsers:
    """Test GET /api/v1/admin/users endpoint"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token via OTP flow"""
        admin_phone = "+244912000000"
        
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"telefone": admin_phone})
        assert response.status_code == 200
        
        import subprocess
        result = subprocess.run(
            ['su', '-', 'postgres', '-c', 
             f'psql -d tudoaqui -t -A -c "SELECT codigo FROM otp_codes WHERE telefone=\'{admin_phone}\' AND verificado=false ORDER BY created_at DESC LIMIT 1;"'],
            capture_output=True, text=True
        )
        otp = result.stdout.strip()
        
        response = requests.post(f"{BASE_URL}/api/v1/auth/verify-otp", json={"telefone": admin_phone, "codigo": otp})
        return response.json()["access_token"]
    
    def test_admin_users_returns_all_users(self, admin_token):
        """Admin users endpoint should return all 8 users"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/v1/admin/users", headers=headers)
        
        assert response.status_code == 200, f"Failed: {response.text}"
        users = response.json()
        
        assert isinstance(users, list), "Expected list of users"
        assert len(users) == 8, f"Expected 8 users, got {len(users)}"
        
        # Verify user structure
        for user in users:
            assert "id" in user, "Missing 'id' in user"
            assert "telefone" in user, "Missing 'telefone' in user"
            assert "role" in user, "Missing 'role' in user"
            assert "status" in user, "Missing 'status' in user"
    
    def test_admin_users_filter_by_role(self, admin_token):
        """Admin users endpoint should filter by role"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Filter by vendedor role
        response = requests.get(f"{BASE_URL}/api/v1/admin/users?role=vendedor", headers=headers)
        assert response.status_code == 200
        users = response.json()
        
        assert len(users) == 2, f"Expected 2 vendedores, got {len(users)}"
        for user in users:
            assert user["role"] == "vendedor", f"Expected vendedor role, got {user['role']}"
    
    def test_admin_users_search_by_phone(self, admin_token):
        """Admin users endpoint should search by phone"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Search for admin phone
        response = requests.get(f"{BASE_URL}/api/v1/admin/users?search=912000000", headers=headers)
        assert response.status_code == 200
        users = response.json()
        
        assert len(users) >= 1, "Expected at least 1 user matching search"
        found_admin = any(u["telefone"] == "+244912000000" for u in users)
        assert found_admin, "Admin user not found in search results"


class TestAdminRoleChange:
    """Test PUT /api/v1/admin/users/{id}/role endpoint"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token via OTP flow"""
        admin_phone = "+244912000000"
        
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"telefone": admin_phone})
        assert response.status_code == 200
        
        import subprocess
        result = subprocess.run(
            ['su', '-', 'postgres', '-c', 
             f'psql -d tudoaqui -t -A -c "SELECT codigo FROM otp_codes WHERE telefone=\'{admin_phone}\' AND verificado=false ORDER BY created_at DESC LIMIT 1;"'],
            capture_output=True, text=True
        )
        otp = result.stdout.strip()
        
        response = requests.post(f"{BASE_URL}/api/v1/auth/verify-otp", json={"telefone": admin_phone, "codigo": otp})
        return response.json()["access_token"]
    
    def test_admin_can_change_user_role(self, admin_token):
        """Admin should be able to change user role"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get a cliente user to change
        response = requests.get(f"{BASE_URL}/api/v1/admin/users?role=cliente", headers=headers)
        assert response.status_code == 200
        users = response.json()
        
        if len(users) == 0:
            pytest.skip("No cliente users to test role change")
        
        user_id = users[0]["id"]
        original_role = users[0]["role"]
        
        # Change role to vendedor
        response = requests.put(f"{BASE_URL}/api/v1/admin/users/{user_id}/role?role=vendedor", headers=headers)
        assert response.status_code == 200, f"Failed to change role: {response.text}"
        
        data = response.json()
        assert data["role"] == "vendedor", f"Expected vendedor, got {data['role']}"
        
        # Verify change persisted
        response = requests.get(f"{BASE_URL}/api/v1/admin/users?search={users[0]['telefone']}", headers=headers)
        assert response.status_code == 200
        updated_users = response.json()
        assert len(updated_users) >= 1
        assert updated_users[0]["role"] == "vendedor"
        
        # Revert back to original role
        response = requests.put(f"{BASE_URL}/api/v1/admin/users/{user_id}/role?role={original_role}", headers=headers)
        assert response.status_code == 200
    
    def test_admin_invalid_role_returns_400(self, admin_token):
        """Invalid role should return 400"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get any user
        response = requests.get(f"{BASE_URL}/api/v1/admin/users", headers=headers)
        users = response.json()
        user_id = users[0]["id"]
        
        # Try invalid role
        response = requests.put(f"{BASE_URL}/api/v1/admin/users/{user_id}/role?role=invalid_role", headers=headers)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"


class TestAdminStatusChange:
    """Test PUT /api/v1/admin/users/{id}/status endpoint"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token via OTP flow"""
        admin_phone = "+244912000000"
        
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"telefone": admin_phone})
        assert response.status_code == 200
        
        import subprocess
        result = subprocess.run(
            ['su', '-', 'postgres', '-c', 
             f'psql -d tudoaqui -t -A -c "SELECT codigo FROM otp_codes WHERE telefone=\'{admin_phone}\' AND verificado=false ORDER BY created_at DESC LIMIT 1;"'],
            capture_output=True, text=True
        )
        otp = result.stdout.strip()
        
        response = requests.post(f"{BASE_URL}/api/v1/auth/verify-otp", json={"telefone": admin_phone, "codigo": otp})
        return response.json()["access_token"]
    
    def test_admin_can_suspend_user(self, admin_token):
        """Admin should be able to suspend a user"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get a non-admin user
        response = requests.get(f"{BASE_URL}/api/v1/admin/users?role=cliente", headers=headers)
        assert response.status_code == 200
        users = response.json()
        
        if len(users) == 0:
            pytest.skip("No cliente users to test status change")
        
        user_id = users[0]["id"]
        original_status = users[0]["status"]
        
        # Suspend user
        response = requests.put(f"{BASE_URL}/api/v1/admin/users/{user_id}/status?user_status=suspenso", headers=headers)
        assert response.status_code == 200, f"Failed to suspend user: {response.text}"
        
        data = response.json()
        assert data["status"] == "suspenso"
        
        # Revert back to original status
        response = requests.put(f"{BASE_URL}/api/v1/admin/users/{user_id}/status?user_status={original_status}", headers=headers)
        assert response.status_code == 200


class TestAdminContent:
    """Test admin content listing endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin token via OTP flow"""
        admin_phone = "+244912000000"
        
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"telefone": admin_phone})
        assert response.status_code == 200
        
        import subprocess
        result = subprocess.run(
            ['su', '-', 'postgres', '-c', 
             f'psql -d tudoaqui -t -A -c "SELECT codigo FROM otp_codes WHERE telefone=\'{admin_phone}\' AND verificado=false ORDER BY created_at DESC LIMIT 1;"'],
            capture_output=True, text=True
        )
        otp = result.stdout.strip()
        
        response = requests.post(f"{BASE_URL}/api/v1/auth/verify-otp", json={"telefone": admin_phone, "codigo": otp})
        return response.json()["access_token"]
    
    def test_admin_events_returns_all_events(self, admin_token):
        """Admin events endpoint should return all events"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/v1/admin/events", headers=headers)
        
        assert response.status_code == 200, f"Failed: {response.text}"
        events = response.json()
        
        assert isinstance(events, list)
        assert len(events) == 5, f"Expected 5 events, got {len(events)}"
        
        # Verify event structure
        for event in events:
            assert "id" in event
            assert "titulo" in event
            assert "local" in event
            assert "status" in event
    
    def test_admin_restaurants_returns_all_restaurants(self, admin_token):
        """Admin restaurants endpoint should return all restaurants"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/v1/admin/restaurants", headers=headers)
        
        assert response.status_code == 200, f"Failed: {response.text}"
        restaurants = response.json()
        
        assert isinstance(restaurants, list)
        assert len(restaurants) == 3, f"Expected 3 restaurants, got {len(restaurants)}"
        
        # Verify restaurant structure
        for r in restaurants:
            assert "id" in r
            assert "nome" in r
            assert "cidade" in r
    
    def test_admin_sellers_returns_all_sellers(self, admin_token):
        """Admin sellers endpoint should return all sellers"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/v1/admin/sellers", headers=headers)
        
        assert response.status_code == 200, f"Failed: {response.text}"
        sellers = response.json()
        
        assert isinstance(sellers, list)
        # At least 1 seller from seed data
        assert len(sellers) >= 1, f"Expected at least 1 seller, got {len(sellers)}"
    
    def test_admin_agents_returns_all_agents(self, admin_token):
        """Admin agents endpoint should return all agents"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/v1/admin/agents", headers=headers)
        
        assert response.status_code == 200, f"Failed: {response.text}"
        agents = response.json()
        
        assert isinstance(agents, list)
        # At least 1 agent from seed data
        assert len(agents) >= 1, f"Expected at least 1 agent, got {len(agents)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
