"""
TUDOaqui API - SMS Provider Service
Integração com Africa's Talking para envio de OTP
"""
import httpx
import logging
from typing import Literal
from abc import ABC, abstractmethod

from src.config import settings

logger = logging.getLogger(__name__)


class SMSProvider(ABC):
    """Interface base para providers de SMS"""
    
    @abstractmethod
    async def send_sms(self, phone: str, message: str) -> dict:
        """Envia SMS para o número especificado"""
        pass


class MockSMSProvider(SMSProvider):
    """Provider mock para desenvolvimento/testes"""
    
    async def send_sms(self, phone: str, message: str) -> dict:
        logger.info(f"[SMS MOCK] Para: {phone}")
        logger.info(f"[SMS MOCK] Mensagem: {message}")
        print(f"\n{'='*50}")
        print("📱 SMS MOCK - Desenvolvimento")
        print("=" * 50)
        print(f"Para: {phone}")
        print(f"Mensagem: {message}")
        print(f"{'='*50}\n")
        
        return {
            "status": "success",
            "provider": "mock",
            "message_id": "mock-message-id",
            "phone": phone
        }


class AfricasTalkingSMSProvider(SMSProvider):
    """
    Provider Africa's Talking para envio real de SMS.
    Documentação: https://africastalking.com/sms
    """
    
    # URLs da API
    SANDBOX_URL = "https://api.sandbox.africastalking.com/version1/messaging"
    PRODUCTION_URL = "https://api.africastalking.com/version1/messaging"
    
    def __init__(self):
        self.api_key = settings.AFRICASTALKING_API_KEY
        self.username = settings.AFRICASTALKING_USERNAME
        self.sender_id = settings.AFRICASTALKING_SENDER_ID
        self.use_sandbox = settings.AFRICASTALKING_SANDBOX
        
        # Valida configuração
        if not self.api_key or not self.username:
            logger.warning("Africa's Talking credentials não configuradas!")
    
    @property
    def base_url(self) -> str:
        """Retorna URL baseada no ambiente"""
        return self.SANDBOX_URL if self.use_sandbox else self.PRODUCTION_URL
    
    async def send_sms(self, phone: str, message: str) -> dict:
        """
        Envia SMS via Africa's Talking API.
        
        Args:
            phone: Número com código do país (+244...)
            message: Texto da mensagem
            
        Returns:
            Dict com status, message_id e detalhes
        """
        if not self.api_key or not self.username:
            logger.error("Africa's Talking não configurado - usando mock")
            return await MockSMSProvider().send_sms(phone, message)
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "apiKey": self.api_key,
        }
        
        payload = {
            "username": self.username,
            "to": phone,
            "message": message,
        }
        
        # Adiciona sender ID se configurado
        if self.sender_id:
            payload["from"] = self.sender_id
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    data=payload,
                    timeout=15.0
                )
                
                logger.info(f"Africa's Talking response: {response.status_code}")
                
                if response.status_code == 201:
                    result = response.json()
                    sms_data = result.get("SMSMessageData", {})
                    recipients = sms_data.get("Recipients", [])
                    
                    if recipients:
                        recipient = recipients[0]
                        status = recipient.get("status", "Unknown")
                        
                        if status == "Success":
                            logger.info(f"SMS enviado para {phone} - ID: {recipient.get('messageId')}")
                            return {
                                "status": "success",
                                "provider": "africastalking",
                                "message_id": recipient.get("messageId"),
                                "phone": phone,
                                "cost": recipient.get("cost"),
                                "status_code": recipient.get("statusCode")
                            }
                        else:
                            logger.error(f"SMS falhou: {status}")
                            return {
                                "status": "error",
                                "provider": "africastalking",
                                "message": f"Delivery failed: {status}",
                                "phone": phone
                            }
                    else:
                        error_msg = sms_data.get("Message", "No recipients")
                        logger.error(f"SMS error: {error_msg}")
                        return {
                            "status": "error",
                            "provider": "africastalking",
                            "message": error_msg,
                            "phone": phone
                        }
                else:
                    logger.error(f"API error: {response.status_code} - {response.text}")
                    return {
                        "status": "error",
                        "provider": "africastalking",
                        "message": f"API error: {response.status_code}",
                        "details": response.text
                    }
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout ao enviar SMS para {phone}")
            return {
                "status": "error",
                "provider": "africastalking",
                "message": "SMS service timeout"
            }
        except Exception as e:
            logger.error(f"Erro ao enviar SMS: {str(e)}")
            return {
                "status": "error",
                "provider": "africastalking",
                "message": str(e)
            }


def get_sms_provider() -> SMSProvider:
    """
    Factory para obter o provider de SMS configurado.
    
    Retorna MockSMSProvider se SMS_PROVIDER=mock
    Retorna AfricasTalkingSMSProvider se SMS_PROVIDER=africastalking
    """
    provider_name = settings.SMS_PROVIDER.lower()
    
    if provider_name == "africastalking":
        return AfricasTalkingSMSProvider()
    else:
        return MockSMSProvider()


# Instância global
sms_provider = get_sms_provider()
