"""
TUDOaqui API - Real Estate Models
Módulo Real Estate: Imobiliário
"""
from datetime import datetime
from enum import Enum
from uuid import UUID
from decimal import Decimal
from sqlalchemy import String, DateTime, Integer, Numeric, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.sql import func
import uuid

from src.database import Base


class PropertyTypeRE(str, Enum):
    APARTAMENTO = "apartamento"
    CASA = "casa"
    VIVENDA = "vivenda"
    TERRENO = "terreno"
    COMERCIAL = "comercial"
    ESCRITORIO = "escritorio"
    ARMAZEM = "armazem"


class TransactionType(str, Enum):
    VENDA = "venda"
    ARRENDAMENTO = "arrendamento"
    AMBOS = "ambos"


class PropertyStatusRE(str, Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"
    VENDIDO = "vendido"
    ARRENDADO = "arrendado"
    PENDENTE = "pendente"


class LeadStatus(str, Enum):
    NOVO = "novo"
    CONTACTADO = "contactado"
    QUALIFICADO = "qualificado"
    VISITA_AGENDADA = "visita_agendada"
    NEGOCIACAO = "negociacao"
    FECHADO = "fechado"
    PERDIDO = "perdido"


class AgentStatus(str, Enum):
    PENDENTE = "pendente"
    APROVADO = "aprovado"
    SUSPENSO = "suspenso"


class RealEstateAgent(Base):
    """Agente imobiliário"""
    __tablename__ = "real_estate_agents"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )
    
    nome_profissional: Mapped[str] = mapped_column(String(120), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    foto_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Licença
    numero_licenca: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Contato profissional
    telefone_profissional: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email_profissional: Mapped[str | None] = mapped_column(String(150), nullable=True)
    
    # Área de atuação
    provincias: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # Array de províncias
    especialidades: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # Tipos de imóvel
    
    # Stats
    rating_medio: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=5.00)
    total_vendas: Mapped[int] = mapped_column(Integer, default=0)
    total_arrendamentos: Mapped[int] = mapped_column(Integer, default=0)
    
    # Plano de subscrição
    plano: Mapped[str] = mapped_column(String(30), default="basic")  # basic, pro, premium
    plano_expira_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    status: Mapped[str] = mapped_column(String(20), default=AgentStatus.PENDENTE)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    user = relationship("User", backref="agent_profile")
    properties = relationship("RealEstateProperty", back_populates="agent", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Agent {self.nome_profissional}>"


class RealEstateProperty(Base):
    """Imóvel para venda/arrendamento"""
    __tablename__ = "real_estate_properties"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    agent_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("real_estate_agents.id"),
        nullable=False
    )
    
    # Detalhes básicos
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    tipo: Mapped[str] = mapped_column(String(30), default=PropertyTypeRE.APARTAMENTO)
    tipo_transacao: Mapped[str] = mapped_column(String(20), default=TransactionType.VENDA)
    
    # Localização
    endereco: Mapped[str] = mapped_column(Text, nullable=False)
    bairro: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cidade: Mapped[str] = mapped_column(String(100), nullable=False)
    provincia: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 8), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(11, 8), nullable=True)
    
    # Preços
    preco_venda: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    preco_arrendamento: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    condominio: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    
    # Características
    area_total: Mapped[int | None] = mapped_column(Integer, nullable=True)  # m²
    area_util: Mapped[int | None] = mapped_column(Integer, nullable=True)  # m²
    quartos: Mapped[int] = mapped_column(Integer, default=0)
    suites: Mapped[int] = mapped_column(Integer, default=0)
    banheiros: Mapped[int] = mapped_column(Integer, default=0)
    vagas_garagem: Mapped[int] = mapped_column(Integer, default=0)
    
    ano_construcao: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Características extras (JSON)
    caracteristicas: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    # Imagens
    imagens: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    video_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    tour_virtual_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Stats
    visualizacoes: Mapped[int] = mapped_column(Integer, default=0)
    favoritos: Mapped[int] = mapped_column(Integer, default=0)
    
    destaque: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default=PropertyStatusRE.PENDENTE)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    agent = relationship("RealEstateAgent", back_populates="properties")
    leads = relationship("Lead", back_populates="property", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<RealEstateProperty {self.titulo}>"


class Lead(Base):
    """Lead/Contacto interessado"""
    __tablename__ = "real_estate_leads"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    property_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("real_estate_properties.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"),
        nullable=True  # Pode ser lead anónimo
    )
    agent_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("real_estate_agents.id"),
        nullable=False
    )
    
    # Dados do lead
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    
    mensagem: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Interesse
    tipo_interesse: Mapped[str] = mapped_column(String(20), default="informacao")  # informacao, visita, proposta
    
    status: Mapped[str] = mapped_column(String(20), default=LeadStatus.NOVO)
    
    # Notas internas do agente
    notas_agente: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Data de visita agendada
    visita_agendada: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    property = relationship("RealEstateProperty", back_populates="leads")
    agent = relationship("RealEstateAgent", backref="leads")
    user = relationship("User", backref="real_estate_leads")


class PropertyFavorite(Base):
    """Imóveis favoritos do usuário"""
    __tablename__ = "property_favorites"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    property_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("real_estate_properties.id", ondelete="CASCADE"),
        nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
