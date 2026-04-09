"""
TUDOaqui API - Real Estate Schemas
"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from src.realestate.models import PropertyTypeRE, TransactionType, PropertyStatusRE, LeadStatus, AgentStatus


# ============================================
# Agent Schemas
# ============================================

class AgentBase(BaseModel):
    """Schema base de agente"""
    nome_profissional: str = Field(..., min_length=2, max_length=120)
    bio: str | None = None
    foto_url: str | None = None
    numero_licenca: str | None = None
    telefone_profissional: str | None = None
    email_profissional: str | None = None
    provincias: list[str] | None = None
    especialidades: list[str] | None = None


class AgentCreate(AgentBase):
    """Schema para criar agente"""
    pass


class AgentUpdate(BaseModel):
    """Schema para atualizar agente"""
    nome_profissional: str | None = None
    bio: str | None = None
    foto_url: str | None = None
    numero_licenca: str | None = None
    telefone_profissional: str | None = None
    email_profissional: str | None = None
    provincias: list[str] | None = None
    especialidades: list[str] | None = None


class AgentResponse(AgentBase):
    """Schema de resposta de agente"""
    id: UUID
    user_id: UUID
    rating_medio: float
    total_vendas: int
    total_arrendamentos: int
    plano: str
    status: AgentStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Property Schemas
# ============================================

class REPropertyBase(BaseModel):
    """Schema base de imóvel"""
    titulo: str = Field(..., min_length=3, max_length=150)
    descricao: str | None = None
    tipo: PropertyTypeRE = PropertyTypeRE.APARTAMENTO
    tipo_transacao: TransactionType = TransactionType.VENDA
    endereco: str = Field(..., min_length=5)
    bairro: str | None = None
    cidade: str = Field(..., min_length=2, max_length=100)
    provincia: str = Field(..., min_length=2, max_length=100)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    preco_venda: float | None = None
    preco_arrendamento: float | None = None
    condominio: float | None = None
    area_total: int | None = None
    area_util: int | None = None
    quartos: int = Field(0, ge=0)
    suites: int = Field(0, ge=0)
    banheiros: int = Field(0, ge=0)
    vagas_garagem: int = Field(0, ge=0)
    ano_construcao: int | None = None
    caracteristicas: list[str] | None = None
    imagens: list[str] | None = None
    video_url: str | None = None
    tour_virtual_url: str | None = None
    destaque: bool = False


class REPropertyCreate(REPropertyBase):
    """Schema para criar imóvel"""
    pass


class REPropertyUpdate(BaseModel):
    """Schema para atualizar imóvel"""
    titulo: str | None = None
    descricao: str | None = None
    tipo: PropertyTypeRE | None = None
    tipo_transacao: TransactionType | None = None
    endereco: str | None = None
    bairro: str | None = None
    cidade: str | None = None
    provincia: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    preco_venda: float | None = None
    preco_arrendamento: float | None = None
    condominio: float | None = None
    area_total: int | None = None
    area_util: int | None = None
    quartos: int | None = None
    suites: int | None = None
    banheiros: int | None = None
    vagas_garagem: int | None = None
    ano_construcao: int | None = None
    caracteristicas: list[str] | None = None
    imagens: list[str] | None = None
    video_url: str | None = None
    tour_virtual_url: str | None = None
    destaque: bool | None = None
    status: PropertyStatusRE | None = None


class REPropertyResponse(REPropertyBase):
    """Schema de resposta de imóvel"""
    id: UUID
    agent_id: UUID
    visualizacoes: int
    favoritos: int
    status: PropertyStatusRE
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class REPropertyListResponse(BaseModel):
    """Schema simplificado para listagem"""
    id: UUID
    titulo: str
    tipo: PropertyTypeRE
    tipo_transacao: TransactionType
    cidade: str
    bairro: str | None
    preco_venda: float | None
    preco_arrendamento: float | None
    quartos: int
    area_util: int | None
    imagem_principal: str | None = None
    destaque: bool
    
    model_config = ConfigDict(from_attributes=True)


class REPropertyDetailResponse(REPropertyResponse):
    """Schema detalhado com info do agente"""
    agent_nome: str
    agent_telefone: str | None
    agent_foto: str | None


# ============================================
# Lead Schemas
# ============================================

class LeadCreate(BaseModel):
    """Schema para criar lead"""
    property_id: UUID
    nome: str = Field(..., min_length=2, max_length=120)
    telefone: str = Field(..., min_length=9)
    email: str | None = None
    mensagem: str | None = None
    tipo_interesse: str = "informacao"


class LeadUpdate(BaseModel):
    """Schema para atualizar lead"""
    status: LeadStatus | None = None
    notas_agente: str | None = None
    visita_agendada: datetime | None = None


class LeadResponse(BaseModel):
    """Schema de resposta de lead"""
    id: UUID
    property_id: UUID
    user_id: UUID | None
    agent_id: UUID
    nome: str
    telefone: str
    email: str | None
    mensagem: str | None
    tipo_interesse: str
    status: LeadStatus
    notas_agente: str | None
    visita_agendada: datetime | None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class LeadDetailResponse(LeadResponse):
    """Lead com info do imóvel"""
    property_titulo: str
    property_tipo: PropertyTypeRE
    property_cidade: str


# ============================================
# Favorite Schemas
# ============================================

class FavoriteResponse(BaseModel):
    """Imóvel favorito"""
    id: UUID
    property_id: UUID
    created_at: datetime
    property: REPropertyListResponse | None = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Search Schemas
# ============================================

class REPropertySearchParams(BaseModel):
    """Parâmetros de busca"""
    cidade: str | None = None
    provincia: str | None = None
    bairro: str | None = None
    tipo: PropertyTypeRE | None = None
    tipo_transacao: TransactionType | None = None
    preco_min: float | None = None
    preco_max: float | None = None
    quartos_min: int | None = None
    area_min: int | None = None


# ============================================
# Stats Schemas
# ============================================

class AgentStats(BaseModel):
    """Estatísticas do agente"""
    total_imoveis: int
    imoveis_ativos: int
    total_leads: int
    leads_novos: int
    visitas_agendadas: int
    total_visualizacoes: int
