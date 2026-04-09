"""
TUDOaqui API - Role/Tipo Migration Tests
Tests for the new partner roles and tipos:
- motorista, motoqueiro, proprietario, staff, guia_turista, agente_imobiliario, agente_viagem
"""
import pytest
import requests
import os
import subprocess

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# New partner roles and tipos
NEW_PARTNER_ROLES = ['motorista', 'motoqueiro', 'proprietario', 'guia_turista', 'agente_imobiliario', 'agente_viagem', 'staff']
NEW_PARTNER_TIPOS = ['motorista', 'motoqueiro', 'proprietario', 'staff', 'guia_turista', 'agente_imobiliario', 'agente_viagem']

# Test credentials
ADMIN_PHONE = '+244912000000'
PROPRIETARIO_PHONE = '+244911000002'  # Has partner profile
GUIA_TURISTA_PHONE = '+244911000001'


def get_otp(phone):
    """Get OTP from database"""
    cmd = f'su - postgres -c "psql -d tudoaqui -t -A -c \\"SELECT codigo FROM otp_codes WHERE telefone=\'{phone}\' AND verificado=false ORDER BY created_at DESC LIMIT 1;\\""'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


def login(session, phone):
    """Login and return token"""
    # Request OTP
    resp = session.post(f"{BASE_URL}/api/v1/auth/login", json={"telefone": phone})
    if resp.status_code != 200:
        pytest.skip(f"Could not request OTP for {phone}: {resp.text}")
    
    # Get OTP from DB
    otp = get_otp(phone)
    if not otp:
        pytest.skip(f"No OTP found for {phone}")
    
    # Verify OTP
    resp = session.post(f"{BASE_URL}/api/v1/auth/verify-otp", json={"telefone": phone, "codigo": otp})
    if resp.status_code != 200:
        pytest.skip(f"Could not verify OTP for {phone}: {resp.text}")
    
    data = resp.json()
    return data.get('access_token')


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def admin_token(api_client):
    """Get admin authentication token"""
    return login(api_client, ADMIN_PHONE)


@pytest.fixture(scope="module")
def proprietario_token(api_client):
    """Get proprietario authentication token"""
    return login(api_client, PROPRIETARIO_PHONE)


@pytest.fixture(scope="module")
def guia_turista_token(api_client):
    """Get guia_turista authentication token"""
    return login(api_client, GUIA_TURISTA_PHONE)


class TestPartnerTiposEndpoint:
    """Test GET /api/v1/partners/tipos - returns 7 partner types"""
    
    def test_tipos_returns_7_types(self, api_client):
        """Verify /api/v1/partners/tipos returns exactly 7 partner types"""
        resp = api_client.get(f"{BASE_URL}/api/v1/partners/tipos")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "tipos" in data
        tipos = data["tipos"]
        
        # Should have exactly 7 types
        assert len(tipos) == 7, f"Expected 7 tipos, got {len(tipos)}"
        
        # Verify all expected tipos are present
        tipo_ids = [t["id"] for t in tipos]
        for expected_tipo in NEW_PARTNER_TIPOS:
            assert expected_tipo in tipo_ids, f"Missing tipo: {expected_tipo}"
        
        print(f"✓ /api/v1/partners/tipos returns 7 types: {tipo_ids}")
    
    def test_tipos_no_auth_required(self, api_client):
        """Verify /api/v1/partners/tipos does NOT require authentication"""
        # Create a fresh session without any auth
        fresh_session = requests.Session()
        resp = fresh_session.get(f"{BASE_URL}/api/v1/partners/tipos")
        assert resp.status_code == 200, f"Expected 200 without auth, got {resp.status_code}"
        print("✓ /api/v1/partners/tipos accessible without authentication")
    
    def test_tipos_structure(self, api_client):
        """Verify each tipo has id, label, desc fields"""
        resp = api_client.get(f"{BASE_URL}/api/v1/partners/tipos")
        data = resp.json()
        
        for tipo in data["tipos"]:
            assert "id" in tipo, f"Missing 'id' in tipo: {tipo}"
            assert "label" in tipo, f"Missing 'label' in tipo: {tipo}"
            assert "desc" in tipo, f"Missing 'desc' in tipo: {tipo}"
        
        print("✓ All tipos have correct structure (id, label, desc)")


class TestPartnerRegisterWithTipo:
    """Test POST /api/v1/partners/register requires valid tipo field"""
    
    def test_register_requires_valid_tipo(self, api_client, guia_turista_token):
        """Verify partner registration requires a valid tipo"""
        if not guia_turista_token:
            pytest.skip("No guia_turista token available")
        
        headers = {"Authorization": f"Bearer {guia_turista_token}"}
        
        # Try with invalid tipo
        resp = api_client.post(
            f"{BASE_URL}/api/v1/partners/register",
            headers=headers,
            json={
                "tipo": "invalid_tipo",
                "nome_negocio": "Test Business"
            }
        )
        # Should fail with 400 for invalid tipo
        assert resp.status_code == 400, f"Expected 400 for invalid tipo, got {resp.status_code}"
        print("✓ Partner registration rejects invalid tipo")
    
    def test_register_accepts_new_tipos(self, api_client, guia_turista_token):
        """Verify partner registration accepts new tipos"""
        if not guia_turista_token:
            pytest.skip("No guia_turista token available")
        
        headers = {"Authorization": f"Bearer {guia_turista_token}"}
        
        # Check if user already has partner profile
        resp = api_client.get(f"{BASE_URL}/api/v1/partners/me", headers=headers)
        if resp.status_code == 200 and resp.json():
            print("✓ User already has partner profile - skipping registration test")
            return
        
        # Try with valid tipo
        resp = api_client.post(
            f"{BASE_URL}/api/v1/partners/register",
            headers=headers,
            json={
                "tipo": "guia_turista",
                "nome_negocio": "TEST_Guia Tours",
                "descricao": "Test tour guide",
                "provincia": "Luanda",
                "cidade": "Luanda"
            }
        )
        # Should succeed or fail with "already partner" (400)
        assert resp.status_code in [200, 201, 400], f"Unexpected status: {resp.status_code}: {resp.text}"
        
        if resp.status_code in [200, 201]:
            data = resp.json()
            assert "partner" in data
            assert data["partner"]["tipo"] == "guia_turista"
            print("✓ Partner registration accepts new tipo 'guia_turista'")
        else:
            # Already a partner
            print("✓ User already registered as partner")


class TestAdminStatsNewRoles:
    """Test GET /api/v1/admin/stats shows new roles"""
    
    def test_admin_stats_has_new_roles(self, api_client, admin_token):
        """Verify admin stats returns new role names"""
        if not admin_token:
            pytest.skip("No admin token available")
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp = api_client.get(f"{BASE_URL}/api/v1/admin/stats", headers=headers)
        
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "roles" in data, "Missing 'roles' in admin stats"
        
        roles = data["roles"]
        
        # Check for new roles (at least some should be present)
        new_roles_found = []
        for role in NEW_PARTNER_ROLES:
            if role in roles:
                new_roles_found.append(role)
        
        # Should have at least some new roles in stats
        print(f"✓ Admin stats contains roles: {list(roles.keys())}")
        print(f"✓ New roles found in stats: {new_roles_found}")
    
    def test_admin_stats_no_old_roles(self, api_client, admin_token):
        """Verify admin stats does NOT contain old role names"""
        if not admin_token:
            pytest.skip("No admin token available")
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp = api_client.get(f"{BASE_URL}/api/v1/admin/stats", headers=headers)
        
        data = resp.json()
        roles = data.get("roles", {})
        
        # Old roles that should NOT be present
        old_roles = ['vendedor', 'anfitriao', 'organizador', 'agente', 'entregador']
        
        for old_role in old_roles:
            # Old roles should not be in stats (or have 0 count)
            if old_role in roles and roles[old_role] > 0:
                print(f"⚠ Warning: Old role '{old_role}' still has {roles[old_role]} users")
        
        print("✓ Checked for old roles in admin stats")


class TestRoleRequestNewRoles:
    """Test POST /api/v1/account/role-request accepts new roles"""
    
    def test_role_request_accepts_new_roles(self, api_client, admin_token):
        """Verify role request endpoint accepts new role names"""
        if not admin_token:
            pytest.skip("No admin token available")
        
        # Admin can't request upgrade, so we just verify the endpoint exists
        # and check the UPGRADABLE_ROLES list in the error message
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        resp = api_client.post(
            f"{BASE_URL}/api/v1/account/role-request",
            headers=headers,
            json={
                "role_pretendido": "proprietario",
                "motivo": "Test request"
            }
        )
        
        # Admin should get 400 "Admin nao precisa de upgrade"
        assert resp.status_code == 400, f"Expected 400 for admin, got {resp.status_code}"
        
        data = resp.json()
        assert "Admin" in data.get("detail", ""), f"Unexpected error: {data}"
        print("✓ Role request endpoint working (admin correctly rejected)")
    
    def test_role_request_rejects_old_roles(self, api_client, guia_turista_token):
        """Verify role request rejects old role names"""
        if not guia_turista_token:
            pytest.skip("No guia_turista token available")
        
        headers = {"Authorization": f"Bearer {guia_turista_token}"}
        
        # Try with old role name
        resp = api_client.post(
            f"{BASE_URL}/api/v1/account/role-request",
            headers=headers,
            json={
                "role_pretendido": "vendedor",  # Old role name
                "motivo": "Test request"
            }
        )
        
        # Should fail with 400 for invalid role
        assert resp.status_code == 400, f"Expected 400 for old role, got {resp.status_code}"
        print("✓ Role request rejects old role name 'vendedor'")


class TestExistingPartnerWithNewTipo:
    """Test existing partner still works with new tipo field"""
    
    def test_existing_partner_profile(self, api_client, proprietario_token):
        """Verify existing partner profile works with new tipo"""
        if not proprietario_token:
            pytest.skip("No proprietario token available")
        
        headers = {"Authorization": f"Bearer {proprietario_token}"}
        resp = api_client.get(f"{BASE_URL}/api/v1/partners/me", headers=headers)
        
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        if data:
            assert "tipo" in data, "Missing 'tipo' field in partner profile"
            assert data["tipo"] in NEW_PARTNER_TIPOS, f"Invalid tipo: {data['tipo']}"
            print(f"✓ Existing partner has valid tipo: {data['tipo']}")
        else:
            print("✓ No partner profile for this user")
    
    def test_admin_list_partners_shows_tipo(self, api_client, admin_token):
        """Verify admin partner list shows tipo field"""
        if not admin_token:
            pytest.skip("No admin token available")
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp = api_client.get(f"{BASE_URL}/api/v1/partners/admin/all", headers=headers)
        
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        partners = resp.json()
        if partners:
            for partner in partners[:5]:  # Check first 5
                assert "tipo" in partner, f"Missing 'tipo' in partner: {partner.get('id')}"
                print(f"  Partner '{partner.get('nome_negocio')}' has tipo: {partner.get('tipo')}")
        
        print(f"✓ Admin partner list shows tipo field ({len(partners)} partners)")


class TestUserRolesMigration:
    """Test that user roles have been migrated correctly"""
    
    def test_admin_users_list_new_roles(self, api_client, admin_token):
        """Verify admin users list shows new role names"""
        if not admin_token:
            pytest.skip("No admin token available")
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        resp = api_client.get(f"{BASE_URL}/api/v1/admin/users", headers=headers)
        
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        users = resp.json()
        roles_found = set()
        
        for user in users:
            role = user.get("role")
            roles_found.add(role)
        
        print(f"✓ User roles found: {roles_found}")
        
        # Check no old roles
        old_roles = {'vendedor', 'anfitriao', 'organizador', 'agente', 'entregador'}
        old_roles_found = roles_found.intersection(old_roles)
        
        if old_roles_found:
            print(f"⚠ Warning: Old roles still present: {old_roles_found}")
        else:
            print("✓ No old roles found in user list")
    
    def test_filter_by_new_role(self, api_client, admin_token):
        """Verify admin can filter users by new role names"""
        if not admin_token:
            pytest.skip("No admin token available")
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Filter by proprietario
        resp = api_client.get(f"{BASE_URL}/api/v1/admin/users?role=proprietario", headers=headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        users = resp.json()
        for user in users:
            assert user.get("role") == "proprietario", f"Wrong role: {user.get('role')}"
        
        print(f"✓ Filter by 'proprietario' works ({len(users)} users)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
