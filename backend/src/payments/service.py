"""
TUDOaqui API - Payments Service
"""
import secrets
from datetime import datetime, timezone
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.payments.models import (
    Payment, PaymentStatus, PaymentMethod, OrigemTipo,
    LedgerEntry, Wallet
)


class PaymentService:
    """Serviço de pagamentos"""
    
    @staticmethod
    def generate_reference() -> str:
        """Gera referência única de pagamento"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_part = secrets.token_hex(4).upper()
        return f"TDQ-{timestamp}-{random_part}"
    
    async def create_payment(
        self,
        db: AsyncSession,
        user_id: UUID,
        origem_tipo: OrigemTipo,
        origem_id: UUID,
        metodo: PaymentMethod,
        valor: Decimal
    ) -> Payment:
        """Cria novo pagamento"""
        # Calcula taxa de serviço (se aplicável)
        taxa_servico = Decimal("0")
        valor_total = valor + taxa_servico
        
        payment = Payment(
            referencia=self.generate_reference(),
            user_id=user_id,
            origem_tipo=origem_tipo.value,
            origem_id=origem_id,
            metodo=metodo.value,
            valor=valor,
            taxa_servico=taxa_servico,
            valor_total=valor_total,
            status=PaymentStatus.INICIADO.value
        )
        
        db.add(payment)
        await db.commit()
        await db.refresh(payment)
        
        # Inicia processo de pagamento externo
        if metodo == PaymentMethod.MULTICAIXA:
            await self._init_multicaixa_payment(payment)
        elif metodo == PaymentMethod.MOBILEMONEY:
            await self._init_mobilemoney_payment(payment)
        elif metodo == PaymentMethod.WALLET:
            await self._process_wallet_payment(db, payment)
        
        return payment
    
    async def get_payment(self, db: AsyncSession, payment_id: UUID) -> Payment | None:
        """Obtém pagamento por ID"""
        result = await db.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_payment_by_ref(self, db: AsyncSession, referencia: str) -> Payment | None:
        """Obtém pagamento por referência"""
        result = await db.execute(
            select(Payment).where(Payment.referencia == referencia)
        )
        return result.scalar_one_or_none()
    
    async def confirm_payment(
        self,
        db: AsyncSession,
        payment_id: UUID,
        external_ref: str | None = None,
        external_status: str | None = None
    ) -> Payment:
        """Confirma pagamento e processa ledger"""
        payment = await self.get_payment(db, payment_id)
        
        if not payment:
            raise ValueError("Pagamento não encontrado")
        
        if payment.status == PaymentStatus.CONFIRMADO.value:
            return payment  # Já confirmado
        
        payment.status = PaymentStatus.CONFIRMADO.value
        payment.external_ref = external_ref
        payment.external_status = external_status
        payment.confirmado_at = datetime.now(timezone.utc)
        
        # Processa ledger baseado no tipo de origem
        await self._process_ledger(db, payment)
        
        await db.commit()
        await db.refresh(payment)
        
        return payment
    
    async def fail_payment(
        self,
        db: AsyncSession,
        payment_id: UUID,
        reason: str | None = None
    ) -> Payment:
        """Marca pagamento como falhado"""
        payment = await self.get_payment(db, payment_id)
        
        if not payment:
            raise ValueError("Pagamento não encontrado")
        
        payment.status = PaymentStatus.FALHADO.value
        payment.external_status = reason
        
        await db.commit()
        await db.refresh(payment)
        
        return payment
    
    async def _process_ledger(self, db: AsyncSession, payment: Payment):
        """Processa entradas no ledger após confirmação"""
        if payment.origem_tipo == OrigemTipo.RIDE.value:
            await self._process_ride_ledger(db, payment)
        elif payment.origem_tipo == OrigemTipo.TICKET.value:
            await self._process_ticket_ledger(db, payment)
        # Adicionar outros tipos conforme necessário
    
    async def _process_ride_ledger(self, db: AsyncSession, payment: Payment):
        """Processa ledger para corrida"""
        from src.tuendi.rides.models import Ride
        
        # Busca a corrida
        result = await db.execute(
            select(Ride).where(Ride.id == payment.origem_id)
        )
        ride = result.scalar_one_or_none()
        
        if not ride or not ride.motorista:
            return
        
        valor_total = payment.valor
        taxa_plataforma = valor_total * Decimal(str(settings.TAXA_PLATAFORMA))
        valor_motorista = valor_total - taxa_plataforma
        
        # Crédito para o motorista
        from src.tuendi.drivers.models import Driver
        driver_result = await db.execute(
            select(Driver).where(Driver.id == ride.motorista_id)
        )
        driver = driver_result.scalar_one_or_none()
        
        if driver:
            motorista_entry = LedgerEntry(
                payment_id=payment.id,
                origem_tipo=payment.origem_tipo,
                origem_id=payment.origem_id,
                beneficiario_id=driver.user_id,
                tipo="credito",
                valor=valor_motorista,
                descricao=f"Corrida {ride.id}"
            )
            db.add(motorista_entry)
        
        # Crédito para a plataforma (beneficiario_id = NULL)
        plataforma_entry = LedgerEntry(
            payment_id=payment.id,
            origem_tipo=payment.origem_tipo,
            origem_id=payment.origem_id,
            beneficiario_id=None,
            tipo="credito",
            valor=taxa_plataforma,
            descricao=f"Comissão corrida {ride.id}"
        )
        db.add(plataforma_entry)
    
    async def _process_ticket_ledger(self, db: AsyncSession, payment: Payment):
        """Processa ledger para ticket de evento"""
        # TODO: Implementar quando módulo de eventos estiver pronto
        pass
    
    async def _init_multicaixa_payment(self, payment: Payment):
        """Inicia pagamento via Multicaixa Express"""
        # TODO: Integrar com API Multicaixa
        # Por agora, simula processo
        pass
    
    async def _init_mobilemoney_payment(self, payment: Payment):
        """Inicia pagamento via Mobile Money"""
        # TODO: Integrar com API Mobile Money
        pass
    
    async def _process_wallet_payment(self, db: AsyncSession, payment: Payment):
        """Processa pagamento via carteira"""
        wallet = await self.get_wallet(db, payment.user_id)
        
        if not wallet:
            raise ValueError("Carteira não encontrada")
        
        if wallet.saldo < payment.valor_total:
            raise ValueError("Saldo insuficiente")
        
        # Debita da carteira
        wallet.saldo -= payment.valor_total
        
        # Confirma pagamento automaticamente
        payment.status = PaymentStatus.CONFIRMADO.value
        payment.confirmado_at = datetime.now(timezone.utc)
        
        # Processa ledger
        await self._process_ledger(db, payment)
    
    # ============================================
    # Wallet Methods
    # ============================================
    
    async def get_wallet(self, db: AsyncSession, user_id: UUID) -> Wallet | None:
        """Obtém carteira do utilizador"""
        result = await db.execute(
            select(Wallet).where(Wallet.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_or_create_wallet(self, db: AsyncSession, user_id: UUID) -> Wallet:
        """Obtém ou cria carteira"""
        wallet = await self.get_wallet(db, user_id)
        
        if not wallet:
            wallet = Wallet(user_id=user_id)
            db.add(wallet)
            await db.commit()
            await db.refresh(wallet)
        
        return wallet
    
    async def add_to_wallet(
        self,
        db: AsyncSession,
        user_id: UUID,
        valor: Decimal,
        descricao: str = "Carregamento"
    ) -> Wallet:
        """Adiciona valor à carteira"""
        wallet = await self.get_or_create_wallet(db, user_id)
        wallet.saldo += valor
        
        await db.commit()
        await db.refresh(wallet)
        
        return wallet
    
    # ============================================
    # Query Methods
    # ============================================
    
    async def get_user_payments(
        self,
        db: AsyncSession,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> list[Payment]:
        """Lista pagamentos do utilizador"""
        result = await db.execute(
            select(Payment)
            .where(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def get_user_ledger(
        self,
        db: AsyncSession,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> list[LedgerEntry]:
        """Lista entradas do ledger do utilizador"""
        result = await db.execute(
            select(LedgerEntry)
            .where(LedgerEntry.beneficiario_id == user_id)
            .order_by(LedgerEntry.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def get_user_balance(self, db: AsyncSession, user_id: UUID) -> dict:
        """Obtém saldo do utilizador (ganhos - gastos)"""
        # Total de créditos
        creditos_result = await db.execute(
            select(func.sum(LedgerEntry.valor))
            .where(and_(
                LedgerEntry.beneficiario_id == user_id,
                LedgerEntry.tipo == "credito"
            ))
        )
        total_creditos = float(creditos_result.scalar() or 0)
        
        # Total de débitos
        debitos_result = await db.execute(
            select(func.sum(LedgerEntry.valor))
            .where(and_(
                LedgerEntry.beneficiario_id == user_id,
                LedgerEntry.tipo == "debito"
            ))
        )
        total_debitos = float(debitos_result.scalar() or 0)
        
        return {
            "total_creditos": total_creditos,
            "total_debitos": total_debitos,
            "saldo": total_creditos - total_debitos
        }


# Instância global
payment_service = PaymentService()
