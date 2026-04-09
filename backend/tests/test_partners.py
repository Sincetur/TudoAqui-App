"""
TUDOaqui API - Partner System Tests
Tests for partner registration, payment config, admin management
"""
import pytest
import requests
import os
import subprocess

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_PHONE = "+244912000000"
VENDEDOR_PHONE = "+244911000002"  # Already has partner profile (approved)
ORGANIZADOR_PHONE = "+244911000001"  # Can register as new partner
EXISTING_PARTNER_ID = "70c31bef-4af0-4b97-8ef1-9835062b7de1"


def get_otp(phone):
    """Get OTP from database"""
    cmd = f'su - postgres -c "psql -d tudoaqui -t -A -c \\"SELECT codigo FROM otp_codes WHERE telefone=\'{phone}\' AND verificado=false ORDER BY created_at DESC LIMIT 1;\\""'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


def login_user(session, phone):
    """Login user and return token"""
    # Request OTP
    resp = session.post(f"{BASE_URL}/api/v1/auth/login", json={"telefone": phone})
    if resp.status_code == 429:
        pytest.skip(f"Rate limited for {phone}")
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    
    # Get OTP from DB
    otp = get_otp(phone)
    if not otp:
        pytest.skip(f"No OTP found for {phone}")
    
    # Verify OTP
    resp = session.post(f"{BASE_URL}/api/v1/auth/verify-otp", json={"telefone": phone, "codigo": otp})
    assert resp.status_code == 200, f"OTP verification failed: {resp.text}"
    
    data = resp.json()
    return data.get("access_token")


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def admin_token(api_client):
    """Get admin authentication token"""
    return login_user(api_client, ADMIN_PHONE)


@pytest.fixture(scope="module")
def vendedor_token(api_client):
    """Get vendedor authentication token (existing partner)"""
    return login_user(api_client, VENDEDOR_PHONE)


@pytest.fixture(scope="module")
def organizador_token(api_client):
    """Get organizador authentication token (can register as partner)"""
    return login_user(api_client, ORGANIZADOR_PHONE)


class TestPartnerPublicEndpoints:
    """Test partner payment info endpoint (public for checkout)"""
    
    def test_get_partner_payment_info_approved(self, api_client, vendedor_token):
        """GET /api/v1/partners/{id}/payment-info - approved partner returns payment methods"""
        api_client.headers.update({"Authorization": f"Bearer {vendedor_token}"})
        
        resp = api_client.get(f"{BASE_URL}/api/v1/partners/{EXISTING_PARTNER_ID}/payment-info")
        assert resp.status_code == 200, f"Failed: {resp.text}"
        
        data = resp.json()
        assert "parceiro" in data, "Response should have 'parceiro' field"
        assert "metodos" in data, "Response should have 'metodos' field"
        assert isinstance(data["metodos"], list), "metodos should be a list"
        
        # Check that at least one payment method is available
        print(f"Partner: {data['parceiro']}")
        print(f"Payment methods: {len(data['metodos'])}")
        for m in data["metodos"]:
            print(f"  - {m['nome']} ({m['id']})")
    
    def test_get_partner_payment_info_not_found(self, api_client, vendedor_token):
        """GET /api/v1/partners/{id}/payment-info - non-existent partner returns 404"""
        api_client.headers.update({"Authorization": f"Bearer {vendedor_token}"})
        
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = api_client.get(f"{BASE_URL}/api/v1/partners/{fake_id}/payment-info")
        assert resp.status_code == 404


class TestPartnerProfile:
    """Test partner profile endpoints"""
    
    def test_get_my_partner_existing(self, api_client, vendedor_token):
        """GET /api/v1/partners/me - existing partner returns profile"""
        api_client.headers.update({"Authorization": f"Bearer {vendedor_token}"})
        
        resp = api_client.get(f"{BASE_URL}/api/v1/partners/me")
        assert resp.status_code == 200, f"Failed: {resp.text}"
        
        data = resp.json()
        assert data is not None, "Should return partner data"
        assert "id" in data, "Should have id"
        assert "nome_negocio" in data, "Should have nome_negocio"
        assert "status" in data, "Should have status"
        assert "aceita_unitel_money" in data, "Should have aceita_unitel_money"
        assert "aceita_transferencia" in data, "Should have aceita_transferencia"
        assert "aceita_dinheiro" in data, "Should have aceita_dinheiro"
        
        print(f"Partner profile: {data['nome_negocio']} - Status: {data['status']}")
        print(f"Payment methods: Unitel={data['aceita_unitel_money']}, Transfer={data['aceita_transferencia']}, Cash={data['aceita_dinheiro']}")
    
    def test_get_my_partner_none(self, api_client, organizador_token):
        """GET /api/v1/partners/me - user without partner returns null"""
        api_client.headers.update({"Authorization": f"Bearer {organizador_token}"})
        
        resp = api_client.get(f"{BASE_URL}/api/v1/partners/me")
        # Should return 200 with null or empty response
        assert resp.status_code == 200, f"Failed: {resp.text}"


class TestPartnerRegistration:
    """Test partner registration"""
    
    def test_register_partner_already_exists(self, api_client, vendedor_token):
        """POST /api/v1/partners/register - already registered returns 400"""
        api_client.headers.update({"Authorization": f"Bearer {vendedor_token}"})
        
        resp = api_client.post(f"{BASE_URL}/api/v1/partners/register", json={
            "nome_negocio": "Test Business",
            "descricao": "Test description",
            "provincia": "Luanda",
            "cidade": "Luanda"
        })
        assert resp.status_code == 400, f"Should fail for existing partner: {resp.text}"
        assert "parceiro" in resp.text.lower() or "registado" in resp.text.lower()


class TestPartnerPaymentConfig:
    """Test partner payment configuration"""
    
    def test_update_payment_config(self, api_client, vendedor_token):
        """PUT /api/v1/partners/me/payment - update payment config"""
        api_client.headers.update({"Authorization": f"Bearer {vendedor_token}"})
        
        resp = api_client.put(f"{BASE_URL}/api/v1/partners/me/payment", json={
            "unitel_money_numero": "+244923456789",
            "unitel_money_titular": "Ana Ferreira",
            "aceita_unitel_money": True,
            "banco_nome": "BAI",
            "banco_conta": "123456789",
            "banco_iban": "AO06 0040 0000 1234567890123",
            "banco_titular": "Ana Ferreira",
            "aceita_transferencia": True,
            "aceita_dinheiro": True
        })
        assert resp.status_code == 200, f"Failed: {resp.text}"
        
        data = resp.json()
        assert "partner" in data, "Should return updated partner"
        partner = data["partner"]
        assert partner["aceita_unitel_money"] == True
        assert partner["aceita_transferencia"] == True
        assert partner["aceita_dinheiro"] == True
        print(f"Payment config updated: Unitel={partner['unitel_money_numero']}, Bank={partner['banco_nome']}")
    
    def test_update_payment_unitel_without_number(self, api_client, vendedor_token):
        """PUT /api/v1/partners/me/payment - Unitel Money without number fails"""
        api_client.headers.update({"Authorization": f"Bearer {vendedor_token}"})
        
        resp = api_client.put(f"{BASE_URL}/api/v1/partners/me/payment", json={
            "aceita_unitel_money": True,
            "unitel_money_numero": None,  # Missing number
            "aceita_transferencia": False,
            "aceita_dinheiro": True
        })
        assert resp.status_code == 400, f"Should fail without Unitel number: {resp.text}"
    
    def test_update_payment_transfer_without_iban(self, api_client, vendedor_token):
        """PUT /api/v1/partners/me/payment - Transfer without IBAN fails"""
        api_client.headers.update({"Authorization": f"Bearer {vendedor_token}"})
        
        resp = api_client.put(f"{BASE_URL}/api/v1/partners/me/payment", json={
            "aceita_unitel_money": False,
            "aceita_transferencia": True,
            "banco_iban": None,  # Missing IBAN
            "aceita_dinheiro": True
        })
        assert resp.status_code == 400, f"Should fail without IBAN: {resp.text}"


class TestAdminPartnerManagement:
    """Test admin partner management endpoints"""
    
    def test_admin_list_partners(self, api_client, admin_token):
        """GET /api/v1/partners/admin/all - list all partners"""
        api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
        
        resp = api_client.get(f"{BASE_URL}/api/v1/partners/admin/all")
        assert resp.status_code == 200, f"Failed: {resp.text}"
        
        data = resp.json()
        assert isinstance(data, list), "Should return list of partners"
        print(f"Total partners: {len(data)}")
        
        if len(data) > 0:
            partner = data[0]
            assert "id" in partner
            assert "nome_negocio" in partner
            assert "status" in partner
            print(f"First partner: {partner['nome_negocio']} - {partner['status']}")
    
    def test_admin_list_partners_filter_status(self, api_client, admin_token):
        """GET /api/v1/partners/admin/all?status_filter=aprovado - filter by status"""
        api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
        
        resp = api_client.get(f"{BASE_URL}/api/v1/partners/admin/all?status_filter=aprovado")
        assert resp.status_code == 200, f"Failed: {resp.text}"
        
        data = resp.json()
        for partner in data:
            assert partner["status"] == "aprovado", f"Partner {partner['id']} has wrong status"
        print(f"Approved partners: {len(data)}")
    
    def test_admin_partner_stats(self, api_client, admin_token):
        """GET /api/v1/partners/admin/stats - get partner statistics"""
        api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
        
        resp = api_client.get(f"{BASE_URL}/api/v1/partners/admin/stats")
        assert resp.status_code == 200, f"Failed: {resp.text}"
        
        data = resp.json()
        assert "total" in data, "Should have total"
        assert "pendentes" in data, "Should have pendentes"
        assert "aprovados" in data, "Should have aprovados"
        assert "suspensos" in data, "Should have suspensos"
        
        print(f"Partner stats: Total={data['total']}, Pending={data['pendentes']}, Approved={data['aprovados']}, Suspended={data['suspensos']}")
    
    def test_admin_suspend_partner(self, api_client, admin_token):
        """PUT /api/v1/partners/admin/{id}/suspend - suspend partner"""
        api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
        
        resp = api_client.put(f"{BASE_URL}/api/v1/partners/admin/{EXISTING_PARTNER_ID}/suspend", json={
            "nota": "Test suspension"
        })
        assert resp.status_code == 200, f"Failed: {resp.text}"
        
        data = resp.json()
        assert data["partner"]["status"] == "suspenso"
        print(f"Partner suspended: {data['partner']['nome_negocio']}")
    
    def test_admin_approve_partner(self, api_client, admin_token):
        """PUT /api/v1/partners/admin/{id}/approve - approve partner"""
        api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
        
        resp = api_client.put(f"{BASE_URL}/api/v1/partners/admin/{EXISTING_PARTNER_ID}/approve", json={
            "nota": "Test approval"
        })
        assert resp.status_code == 200, f"Failed: {resp.text}"
        
        data = resp.json()
        assert data["partner"]["status"] == "aprovado"
        print(f"Partner approved: {data['partner']['nome_negocio']}")
    
    def test_admin_reject_partner_not_found(self, api_client, admin_token):
        """PUT /api/v1/partners/admin/{id}/reject - non-existent partner returns 404"""
        api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
        
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = api_client.put(f"{BASE_URL}/api/v1/partners/admin/{fake_id}/reject", json={
            "nota": "Test rejection"
        })
        assert resp.status_code == 404


class TestPartnerAccessControl:
    """Test access control for partner endpoints"""
    
    def test_admin_endpoints_require_admin(self, api_client, vendedor_token):
        """Admin endpoints should reject non-admin users"""
        api_client.headers.update({"Authorization": f"Bearer {vendedor_token}"})
        
        # Try to access admin stats
        resp = api_client.get(f"{BASE_URL}/api/v1/partners/admin/stats")
        assert resp.status_code == 403, f"Should be forbidden for non-admin: {resp.text}"
        
        # Try to access admin list
        resp = api_client.get(f"{BASE_URL}/api/v1/partners/admin/all")
        assert resp.status_code == 403, f"Should be forbidden for non-admin: {resp.text}"
    
    def test_partner_endpoints_require_auth(self, api_client):
        """Partner endpoints should require authentication"""
        # Remove auth header
        api_client.headers.pop("Authorization", None)
        
        resp = api_client.get(f"{BASE_URL}/api/v1/partners/me")
        assert resp.status_code == 401, f"Should require auth: {resp.text}"


class TestPartnerPaymentInfoForCheckout:
    """Test partner payment info retrieval for checkout flow"""
    
    def test_get_payment_info_has_unitel_money(self, api_client, vendedor_token):
        """Verify Unitel Money payment method is returned"""
        api_client.headers.update({"Authorization": f"Bearer {vendedor_token}"})
        
        resp = api_client.get(f"{BASE_URL}/api/v1/partners/{EXISTING_PARTNER_ID}/payment-info")
        assert resp.status_code == 200
        
        data = resp.json()
        unitel_method = next((m for m in data["metodos"] if m["id"] == "unitelmoney"), None)
        
        if unitel_method:
            assert "dados" in unitel_method
            assert "numero" in unitel_method["dados"]
            print(f"Unitel Money: {unitel_method['dados']['numero']}")
        else:
            print("Unitel Money not configured for this partner")
    
    def test_get_payment_info_has_transfer(self, api_client, vendedor_token):
        """Verify bank transfer payment method is returned"""
        api_client.headers.update({"Authorization": f"Bearer {vendedor_token}"})
        
        resp = api_client.get(f"{BASE_URL}/api/v1/partners/{EXISTING_PARTNER_ID}/payment-info")
        assert resp.status_code == 200
        
        data = resp.json()
        transfer_method = next((m for m in data["metodos"] if m["id"] == "transferencia"), None)
        
        if transfer_method:
            assert "dados" in transfer_method
            assert "iban" in transfer_method["dados"]
            print(f"Bank Transfer: {transfer_method['dados']['banco']} - IBAN: {transfer_method['dados']['iban']}")
        else:
            print("Bank transfer not configured for this partner")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
