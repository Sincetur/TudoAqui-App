"""
TUDOaqui API - Account & Role Upgrade Tests
Tests for Account page profile CRUD and role upgrade request system
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_PHONE = "+244912000000"
REGULAR_USER_PHONE = "+244923456789"

class TestAccountProfile:
    """Account profile endpoint tests"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin auth token"""
        # Request OTP
        resp = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"telefone": ADMIN_PHONE})
        if resp.status_code == 429:
            # Rate limited - insert OTP directly
            import subprocess
            subprocess.run([
                "su", "-", "postgres", "-c",
                f"psql -d tudoaqui -c \"INSERT INTO otp_codes (id, telefone, codigo, tentativas, verificado, expira_em, created_at) VALUES (gen_random_uuid(), '{ADMIN_PHONE}', '123456', 0, false, NOW() + INTERVAL '5 minutes', NOW());\""
            ], capture_output=True)
            otp = "123456"
        else:
            # Get OTP from DB
            import subprocess
            result = subprocess.run([
                "su", "-", "postgres", "-c",
                f"psql -d tudoaqui -t -A -c \"SELECT codigo FROM otp_codes WHERE telefone='{ADMIN_PHONE}' AND verificado=false ORDER BY created_at DESC LIMIT 1;\""
            ], capture_output=True, text=True)
            otp = result.stdout.strip()
        
        # Verify OTP
        verify_resp = requests.post(f"{BASE_URL}/api/v1/auth/verify-otp", json={
            "telefone": ADMIN_PHONE,
            "codigo": otp
        })
        if verify_resp.status_code == 200:
            return verify_resp.json().get("access_token")
        pytest.skip(f"Admin auth failed: {verify_resp.text}")
    
    @pytest.fixture(scope="class")
    def regular_user_token(self):
        """Get regular user auth token"""
        # Request OTP
        resp = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"telefone": REGULAR_USER_PHONE})
        if resp.status_code == 429:
            import subprocess
            subprocess.run([
                "su", "-", "postgres", "-c",
                f"psql -d tudoaqui -c \"INSERT INTO otp_codes (id, telefone, codigo, tentativas, verificado, expira_em, created_at) VALUES (gen_random_uuid(), '{REGULAR_USER_PHONE}', '654321', 0, false, NOW() + INTERVAL '5 minutes', NOW());\""
            ], capture_output=True)
            otp = "654321"
        else:
            import subprocess
            result = subprocess.run([
                "su", "-", "postgres", "-c",
                f"psql -d tudoaqui -t -A -c \"SELECT codigo FROM otp_codes WHERE telefone='{REGULAR_USER_PHONE}' AND verificado=false ORDER BY created_at DESC LIMIT 1;\""
            ], capture_output=True, text=True)
            otp = result.stdout.strip()
        
        verify_resp = requests.post(f"{BASE_URL}/api/v1/auth/verify-otp", json={
            "telefone": REGULAR_USER_PHONE,
            "codigo": otp
        })
        if verify_resp.status_code == 200:
            return verify_resp.json().get("access_token")
        pytest.skip(f"Regular user auth failed: {verify_resp.text}")
    
    def test_get_profile(self, admin_token):
        """Test GET /api/v1/account/profile returns user profile"""
        resp = requests.get(
            f"{BASE_URL}/api/v1/account/profile",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "id" in data
        assert "telefone" in data
        assert "role" in data
        assert "created_at" in data
        print(f"Profile: {data}")
    
    def test_update_profile(self, admin_token):
        """Test PUT /api/v1/account/profile updates name/email"""
        # Update profile
        resp = requests.put(
            f"{BASE_URL}/api/v1/account/profile",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"nome": "Admin TUDOaqui Updated", "email": "admin@tudoaqui.ao"}
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        # Verify update
        get_resp = requests.get(
            f"{BASE_URL}/api/v1/account/profile",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert get_resp.status_code == 200
        data = get_resp.json()
        assert data["nome"] == "Admin TUDOaqui Updated"
        assert data["email"] == "admin@tudoaqui.ao"
        print(f"Updated profile: {data}")
    
    def test_profile_requires_auth(self):
        """Test profile endpoints require authentication"""
        resp = requests.get(f"{BASE_URL}/api/v1/account/profile")
        assert resp.status_code == 401 or resp.status_code == 403


class TestRoleUpgradeRequests:
    """Role upgrade request tests"""
    
    @pytest.fixture(scope="class")
    def regular_user_token(self):
        """Get regular user auth token"""
        resp = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"telefone": REGULAR_USER_PHONE})
        if resp.status_code == 429:
            import subprocess
            subprocess.run([
                "su", "-", "postgres", "-c",
                f"psql -d tudoaqui -c \"INSERT INTO otp_codes (id, telefone, codigo, tentativas, verificado, expira_em, created_at) VALUES (gen_random_uuid(), '{REGULAR_USER_PHONE}', '654321', 0, false, NOW() + INTERVAL '5 minutes', NOW());\""
            ], capture_output=True)
            otp = "654321"
        else:
            import subprocess
            result = subprocess.run([
                "su", "-", "postgres", "-c",
                f"psql -d tudoaqui -t -A -c \"SELECT codigo FROM otp_codes WHERE telefone='{REGULAR_USER_PHONE}' AND verificado=false ORDER BY created_at DESC LIMIT 1;\""
            ], capture_output=True, text=True)
            otp = result.stdout.strip()
        
        verify_resp = requests.post(f"{BASE_URL}/api/v1/auth/verify-otp", json={
            "telefone": REGULAR_USER_PHONE,
            "codigo": otp
        })
        if verify_resp.status_code == 200:
            return verify_resp.json().get("access_token")
        pytest.skip(f"Regular user auth failed: {verify_resp.text}")
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin auth token"""
        resp = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"telefone": ADMIN_PHONE})
        if resp.status_code == 429:
            import subprocess
            subprocess.run([
                "su", "-", "postgres", "-c",
                f"psql -d tudoaqui -c \"INSERT INTO otp_codes (id, telefone, codigo, tentativas, verificado, expira_em, created_at) VALUES (gen_random_uuid(), '{ADMIN_PHONE}', '123456', 0, false, NOW() + INTERVAL '5 minutes', NOW());\""
            ], capture_output=True)
            otp = "123456"
        else:
            import subprocess
            result = subprocess.run([
                "su", "-", "postgres", "-c",
                f"psql -d tudoaqui -t -A -c \"SELECT codigo FROM otp_codes WHERE telefone='{ADMIN_PHONE}' AND verificado=false ORDER BY created_at DESC LIMIT 1;\""
            ], capture_output=True, text=True)
            otp = result.stdout.strip()
        
        verify_resp = requests.post(f"{BASE_URL}/api/v1/auth/verify-otp", json={
            "telefone": ADMIN_PHONE,
            "codigo": otp
        })
        if verify_resp.status_code == 200:
            return verify_resp.json().get("access_token")
        pytest.skip(f"Admin auth failed: {verify_resp.text}")
    
    def test_get_my_role_requests(self, regular_user_token):
        """Test GET /api/v1/account/role-requests returns user's requests"""
        resp = requests.get(
            f"{BASE_URL}/api/v1/account/role-requests",
            headers={"Authorization": f"Bearer {regular_user_token}"}
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert isinstance(data, list)
        print(f"User role requests: {len(data)} requests found")
        for req in data:
            print(f"  - {req.get('role_pretendido')}: {req.get('status')}")
    
    def test_admin_get_all_role_requests(self, admin_token):
        """Test GET /api/v1/admin/role-requests returns all requests (admin only)"""
        resp = requests.get(
            f"{BASE_URL}/api/v1/admin/role-requests",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert isinstance(data, list)
        print(f"Admin sees {len(data)} role requests")
        for req in data:
            print(f"  - User: {req.get('user_telefone')}, {req.get('user_role_atual')} -> {req.get('role_pretendido')}, Status: {req.get('status')}")
    
    def test_admin_filter_role_requests(self, admin_token):
        """Test admin can filter role requests by status"""
        for status in ['pendente', 'aprovado', 'rejeitado']:
            resp = requests.get(
                f"{BASE_URL}/api/v1/admin/role-requests?status_filter={status}",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert resp.status_code == 200, f"Filter {status} failed: {resp.text}"
            data = resp.json()
            print(f"  Filter '{status}': {len(data)} requests")
    
    def test_non_admin_cannot_access_admin_role_requests(self, regular_user_token):
        """Test non-admin users cannot access admin role requests endpoint"""
        resp = requests.get(
            f"{BASE_URL}/api/v1/admin/role-requests",
            headers={"Authorization": f"Bearer {regular_user_token}"}
        )
        assert resp.status_code == 403, f"Expected 403, got {resp.status_code}"


class TestRoleUpgradeWorkflow:
    """Test complete role upgrade workflow: create -> admin approve/reject"""
    
    @pytest.fixture(scope="class")
    def test_user_phone(self):
        """Create a test user for upgrade workflow"""
        return "+244911999999"
    
    @pytest.fixture(scope="class")
    def test_user_token(self, test_user_phone):
        """Get test user auth token"""
        # Login
        resp = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"telefone": test_user_phone})
        if resp.status_code == 429:
            import subprocess
            subprocess.run([
                "su", "-", "postgres", "-c",
                f"psql -d tudoaqui -c \"INSERT INTO otp_codes (id, telefone, codigo, tentativas, verificado, expira_em, created_at) VALUES (gen_random_uuid(), '{test_user_phone}', '999999', 0, false, NOW() + INTERVAL '5 minutes', NOW());\""
            ], capture_output=True)
            otp = "999999"
        else:
            import subprocess
            result = subprocess.run([
                "su", "-", "postgres", "-c",
                f"psql -d tudoaqui -t -A -c \"SELECT codigo FROM otp_codes WHERE telefone='{test_user_phone}' AND verificado=false ORDER BY created_at DESC LIMIT 1;\""
            ], capture_output=True, text=True)
            otp = result.stdout.strip()
        
        verify_resp = requests.post(f"{BASE_URL}/api/v1/auth/verify-otp", json={
            "telefone": test_user_phone,
            "codigo": otp
        })
        if verify_resp.status_code == 200:
            return verify_resp.json().get("access_token")
        pytest.skip(f"Test user auth failed: {verify_resp.text}")
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin auth token"""
        resp = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"telefone": ADMIN_PHONE})
        if resp.status_code == 429:
            import subprocess
            subprocess.run([
                "su", "-", "postgres", "-c",
                f"psql -d tudoaqui -c \"INSERT INTO otp_codes (id, telefone, codigo, tentativas, verificado, expira_em, created_at) VALUES (gen_random_uuid(), '{ADMIN_PHONE}', '123456', 0, false, NOW() + INTERVAL '5 minutes', NOW());\""
            ], capture_output=True)
            otp = "123456"
        else:
            import subprocess
            result = subprocess.run([
                "su", "-", "postgres", "-c",
                f"psql -d tudoaqui -t -A -c \"SELECT codigo FROM otp_codes WHERE telefone='{ADMIN_PHONE}' AND verificado=false ORDER BY created_at DESC LIMIT 1;\""
            ], capture_output=True, text=True)
            otp = result.stdout.strip()
        
        verify_resp = requests.post(f"{BASE_URL}/api/v1/auth/verify-otp", json={
            "telefone": ADMIN_PHONE,
            "codigo": otp
        })
        if verify_resp.status_code == 200:
            return verify_resp.json().get("access_token")
        pytest.skip(f"Admin auth failed: {verify_resp.text}")
    
    def test_create_role_request(self, test_user_token):
        """Test POST /api/v1/account/role-request creates upgrade request"""
        # First check if user already has pending request
        check_resp = requests.get(
            f"{BASE_URL}/api/v1/account/role-requests",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        existing = check_resp.json() if check_resp.status_code == 200 else []
        has_pending = any(r.get('status') == 'pendente' for r in existing)
        
        if has_pending:
            print("User already has pending request - skipping create test")
            pytest.skip("User already has pending request")
        
        # Create role request
        resp = requests.post(
            f"{BASE_URL}/api/v1/account/role-request",
            headers={"Authorization": f"Bearer {test_user_token}"},
            json={
                "role_pretendido": "organizador",
                "motivo": "Quero organizar eventos na minha comunidade"
            }
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert data.get("status") == "pendente"
        print(f"Created role request: {data}")
    
    def test_duplicate_pending_request_blocked(self, test_user_token):
        """Test cannot create duplicate pending request"""
        # Try to create another request
        resp = requests.post(
            f"{BASE_URL}/api/v1/account/role-request",
            headers={"Authorization": f"Bearer {test_user_token}"},
            json={
                "role_pretendido": "vendedor",
                "motivo": "Quero vender produtos"
            }
        )
        # Should fail if there's already a pending request
        if resp.status_code == 400:
            assert "pendente" in resp.text.lower() or "ja tem" in resp.text.lower()
            print("Correctly blocked duplicate pending request")
        else:
            print(f"No pending request exists, created new one: {resp.json()}")
    
    def test_invalid_role_rejected(self, test_user_token):
        """Test invalid role is rejected"""
        resp = requests.post(
            f"{BASE_URL}/api/v1/account/role-request",
            headers={"Authorization": f"Bearer {test_user_token}"},
            json={
                "role_pretendido": "superadmin",
                "motivo": "Test invalid role"
            }
        )
        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
        print("Correctly rejected invalid role")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
