"""
TUDOaqui API - Payments Module Tests
Tests for payment endpoints including bank info, payment methods, CRUD operations,
and admin payment management.
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test data
ADMIN_PHONE = "+244912000000"
TEST_USER_PHONE = "+244911000001"


class TestPaymentsSetup:
    """Setup and helper methods for payment tests"""
    
    @staticmethod
    def get_otp(phone):
        """Get OTP from database"""
        import subprocess
        cmd = f'su - postgres -c "psql -d tudoaqui -t -A -c \\"SELECT codigo FROM otp_codes WHERE telefone=\'{phone}\' AND verificado=false ORDER BY created_at DESC LIMIT 1;\\""'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    
    @staticmethod
    def login(session, phone):
        """Login and return token"""
        # Request OTP
        resp = session.post(f"{BASE_URL}/api/v1/auth/login", json={"telefone": phone})
        if resp.status_code not in [200, 429]:  # 429 = rate limited, OTP already sent
            return None
        
        # Get OTP from DB
        otp = TestPaymentsSetup.get_otp(phone)
        if not otp:
            return None
        
        # Verify OTP
        resp = session.post(f"{BASE_URL}/api/v1/auth/verify-otp", json={"telefone": phone, "codigo": otp})
        if resp.status_code == 200:
            data = resp.json()
            return data.get("access_token")
        return None


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def admin_token(api_client):
    """Get admin authentication token"""
    token = TestPaymentsSetup.login(api_client, ADMIN_PHONE)
    if not token:
        pytest.skip("Admin authentication failed - skipping admin tests")
    return token


@pytest.fixture(scope="module")
def user_token(api_client):
    """Get regular user authentication token"""
    token = TestPaymentsSetup.login(api_client, TEST_USER_PHONE)
    if not token:
        pytest.skip("User authentication failed - skipping user tests")
    return token


@pytest.fixture
def admin_client(api_client, admin_token):
    """Session with admin auth header"""
    api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
    return api_client


@pytest.fixture
def user_client(api_client, user_token):
    """Session with user auth header"""
    api_client.headers.update({"Authorization": f"Bearer {user_token}"})
    return api_client


# ============================================
# Bank Info Tests
# ============================================

class TestBankInfo:
    """Tests for GET /api/v1/payments/bank-info"""
    
    def test_get_bank_info_returns_bai_details(self, user_client):
        """Bank info should return correct BAI bank details"""
        response = user_client.get(f"{BASE_URL}/api/v1/payments/bank-info")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "banco" in data
        assert "BAI" in data["banco"], f"Expected BAI bank, got {data['banco']}"
        assert data["conta"] == "20967898310001", f"Wrong account number: {data['conta']}"
        assert "AO06 0040 0000 0967898310151" in data["iban"], f"Wrong IBAN: {data['iban']}"
        assert data["swift"] == "BAIPAOLU", f"Wrong SWIFT: {data['swift']}"
        assert "titular" in data
        assert "instrucoes" in data
        print(f"✓ Bank info returned correctly: {data['banco']}")
    
    def test_bank_info_requires_auth(self, api_client):
        """Bank info should require authentication"""
        # Remove auth header
        api_client.headers.pop("Authorization", None)
        response = api_client.get(f"{BASE_URL}/api/v1/payments/bank-info")
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Bank info requires authentication")


# ============================================
# Payment Methods Tests
# ============================================

class TestPaymentMethods:
    """Tests for GET /api/v1/payments/methods"""
    
    def test_get_payment_methods(self, user_client):
        """Should return available payment methods"""
        response = user_client.get(f"{BASE_URL}/api/v1/payments/methods")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "metodos" in data
        metodos = data["metodos"]
        assert len(metodos) >= 2, f"Expected at least 2 methods, got {len(metodos)}"
        
        # Check transferencia is active
        transferencia = next((m for m in metodos if m["id"] == "transferencia"), None)
        assert transferencia is not None, "Transferencia method not found"
        assert transferencia["ativo"] == True, "Transferencia should be active"
        
        # Check dinheiro is active
        dinheiro = next((m for m in metodos if m["id"] == "dinheiro"), None)
        assert dinheiro is not None, "Dinheiro method not found"
        assert dinheiro["ativo"] == True, "Dinheiro should be active"
        
        # Check multicaixa is inactive
        multicaixa = next((m for m in metodos if m["id"] == "multicaixa"), None)
        assert multicaixa is not None, "Multicaixa method not found"
        assert multicaixa["ativo"] == False, "Multicaixa should be inactive"
        
        print(f"✓ Payment methods returned: {[m['id'] for m in metodos]}")


# ============================================
# Payment CRUD Tests
# ============================================

class TestPaymentCRUD:
    """Tests for payment creation and listing"""
    
    def test_create_payment_transferencia(self, user_client):
        """Should create a payment with metodo=transferencia"""
        test_uuid = str(uuid.uuid4())
        payload = {
            "origem_tipo": "marketplace",
            "origem_id": test_uuid,
            "metodo": "transferencia",
            "valor": 5000.00,
            "comprovativo_ref": "TRF-TEST-123456",
            "notas": "Test payment via transferencia"
        }
        
        response = user_client.post(f"{BASE_URL}/api/v1/payments", json=payload)
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data
        assert "referencia" in data
        assert data["metodo"] == "transferencia"
        assert data["valor"] == 5000.00
        assert data["status"] == "pendente"
        assert data["comprovativo_ref"] == "TRF-TEST-123456"
        
        print(f"✓ Created transferencia payment: {data['referencia']}")
        return data
    
    def test_create_payment_dinheiro(self, user_client):
        """Should create a payment with metodo=dinheiro"""
        test_uuid = str(uuid.uuid4())
        payload = {
            "origem_tipo": "restaurante",
            "origem_id": test_uuid,
            "metodo": "dinheiro",
            "valor": 2500.00,
            "notas": "Test cash payment"
        }
        
        response = user_client.post(f"{BASE_URL}/api/v1/payments", json=payload)
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["metodo"] == "dinheiro"
        assert data["valor"] == 2500.00
        assert data["status"] == "pendente"
        
        print(f"✓ Created dinheiro payment: {data['referencia']}")
        return data
    
    def test_list_user_payments(self, user_client):
        """Should list user's payments"""
        response = user_client.get(f"{BASE_URL}/api/v1/payments")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Expected list of payments"
        
        if len(data) > 0:
            payment = data[0]
            assert "id" in payment
            assert "referencia" in payment
            assert "metodo" in payment
            assert "valor" in payment
            assert "status" in payment
        
        print(f"✓ Listed {len(data)} user payments")


# ============================================
# Comprovativo Tests
# ============================================

class TestComprovativo:
    """Tests for submitting transfer proof"""
    
    def test_submit_comprovativo(self, user_client):
        """Should submit comprovativo for a transfer payment"""
        # First create a payment
        test_uuid = str(uuid.uuid4())
        create_payload = {
            "origem_tipo": "marketplace",
            "origem_id": test_uuid,
            "metodo": "transferencia",
            "valor": 3000.00
        }
        
        create_resp = user_client.post(f"{BASE_URL}/api/v1/payments", json=create_payload)
        assert create_resp.status_code == 201
        payment = create_resp.json()
        payment_id = payment["id"]
        
        # Submit comprovativo
        comprovativo_payload = {
            "comprovativo_ref": "TRF-COMP-789012",
            "notas": "Comprovativo submitted"
        }
        
        response = user_client.put(
            f"{BASE_URL}/api/v1/payments/{payment_id}/comprovativo",
            json=comprovativo_payload
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["comprovativo_ref"] == "TRF-COMP-789012"
        assert data["status"] == "pendente"
        
        print(f"✓ Submitted comprovativo for payment {payment_id}")


# ============================================
# Admin Payment Tests
# ============================================

class TestAdminPayments:
    """Tests for admin payment management"""
    
    def test_admin_list_all_payments(self, admin_client):
        """Admin should be able to list all payments"""
        response = admin_client.get(f"{BASE_URL}/api/v1/payments/admin/all")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Expected list of payments"
        
        print(f"✓ Admin listed {len(data)} total payments")
    
    def test_admin_payment_stats(self, admin_client):
        """Admin should get payment statistics"""
        response = admin_client.get(f"{BASE_URL}/api/v1/payments/admin/stats")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total" in data
        assert "pendentes" in data
        assert "confirmados" in data
        assert "receita_total" in data
        assert "por_metodo" in data
        
        print(f"✓ Admin stats: total={data['total']}, pendentes={data['pendentes']}, confirmados={data['confirmados']}")
    
    def test_admin_confirm_payment(self, admin_client, user_client):
        """Admin should be able to confirm a payment"""
        # First create a payment as user
        user_client.headers.update(admin_client.headers)  # Use same session
        
        # Login as user to create payment
        user_token = TestPaymentsSetup.login(user_client, TEST_USER_PHONE)
        if user_token:
            user_client.headers.update({"Authorization": f"Bearer {user_token}"})
        
        test_uuid = str(uuid.uuid4())
        create_payload = {
            "origem_tipo": "marketplace",
            "origem_id": test_uuid,
            "metodo": "transferencia",
            "valor": 1500.00,
            "comprovativo_ref": "TRF-CONFIRM-TEST"
        }
        
        create_resp = user_client.post(f"{BASE_URL}/api/v1/payments", json=create_payload)
        if create_resp.status_code != 201:
            pytest.skip("Could not create payment for confirm test")
        
        payment = create_resp.json()
        payment_id = payment["id"]
        
        # Now confirm as admin
        admin_token = TestPaymentsSetup.login(admin_client, ADMIN_PHONE)
        if admin_token:
            admin_client.headers.update({"Authorization": f"Bearer {admin_token}"})
        
        response = admin_client.put(
            f"{BASE_URL}/api/v1/payments/{payment_id}/confirm",
            json={"nota": "Confirmed by admin test"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["status"] == "confirmado"
        
        print(f"✓ Admin confirmed payment {payment_id}")
    
    def test_admin_reject_payment(self, api_client):
        """Admin should be able to reject a payment"""
        # Create fresh session for this test
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Login as user to create payment
        user_token = TestPaymentsSetup.login(session, TEST_USER_PHONE)
        if not user_token:
            pytest.skip("Could not login as user for reject test")
        
        session.headers.update({"Authorization": f"Bearer {user_token}"})
        
        test_uuid = str(uuid.uuid4())
        create_payload = {
            "origem_tipo": "marketplace",
            "origem_id": test_uuid,
            "metodo": "dinheiro",
            "valor": 800.00
        }
        
        create_resp = session.post(f"{BASE_URL}/api/v1/payments", json=create_payload)
        if create_resp.status_code != 201:
            pytest.skip("Could not create payment for reject test")
        
        payment = create_resp.json()
        payment_id = payment["id"]
        
        # Now reject as admin with fresh session
        admin_session = requests.Session()
        admin_session.headers.update({"Content-Type": "application/json"})
        admin_token = TestPaymentsSetup.login(admin_session, ADMIN_PHONE)
        if not admin_token:
            pytest.skip("Could not login as admin for reject test")
        
        admin_session.headers.update({"Authorization": f"Bearer {admin_token}"})
        
        response = admin_session.put(
            f"{BASE_URL}/api/v1/payments/{payment_id}/reject",
            json={"nota": "Rejected by admin test"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["status"] == "falhado"
        
        print(f"✓ Admin rejected payment {payment_id}")
    
    def test_admin_filter_payments_by_status(self, admin_client):
        """Admin should filter payments by status"""
        response = admin_client.get(f"{BASE_URL}/api/v1/payments/admin/all?status_filter=pendente")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        for payment in data:
            assert payment["status"] == "pendente", f"Expected pendente, got {payment['status']}"
        
        print(f"✓ Admin filtered {len(data)} pendente payments")
    
    def test_admin_filter_payments_by_metodo(self, admin_client):
        """Admin should filter payments by metodo"""
        response = admin_client.get(f"{BASE_URL}/api/v1/payments/admin/all?metodo=transferencia")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        for payment in data:
            assert payment["metodo"] == "transferencia", f"Expected transferencia, got {payment['metodo']}"
        
        print(f"✓ Admin filtered {len(data)} transferencia payments")


# ============================================
# Authorization Tests
# ============================================

class TestPaymentAuthorization:
    """Tests for payment authorization"""
    
    def test_admin_endpoints_require_admin_role(self, user_client):
        """Admin endpoints should reject non-admin users"""
        # Try to access admin endpoints as regular user
        response = user_client.get(f"{BASE_URL}/api/v1/payments/admin/all")
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Admin endpoints require admin role")
    
    def test_unauthenticated_cannot_create_payment(self, api_client):
        """Unauthenticated users cannot create payments"""
        api_client.headers.pop("Authorization", None)
        
        payload = {
            "origem_tipo": "marketplace",
            "origem_id": str(uuid.uuid4()),
            "metodo": "dinheiro",
            "valor": 1000.00
        }
        
        response = api_client.post(f"{BASE_URL}/api/v1/payments", json=payload)
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Unauthenticated users cannot create payments")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
