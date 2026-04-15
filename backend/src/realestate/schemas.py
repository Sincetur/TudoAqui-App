"""
TUDOaqui API - Real Estate Schemas
"""
from typing import List, Optional
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
    bio: Optional[str] = None
    foto_url: Optional[str] = None
    numero_licenca: Optional[str] = None
    telefone_profissional: Optional[str] = None
    email_profissional: Optional[str] = None
    provincias: Optional[List[str]] = None
    especialidades: Optional[List[str]] = None


class AgentCreate(AgentBase):
    """Schema para criar agente"""
    pass


class AgentUpdate(BaseModel):
    """Schema para atualizar agente"""
    nome_profissional: Optional[str] = None
    bio: Optional[str] = None
    foto_url: Optional[str] = None
    numero_licenca: Optional[str] = None
    telefone_profissional: Optional[str] = None
    email_profissional: Optional[str] = None
    provincias: Optional[List[str]] = None
    especialidades: Optional[List[str]] = None


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
    descricao: Optional[str] = None
    tipo: PropertyTypeRE = PropertyTypeRE.APARTAMENTO
    tipo_transacao: TransactionType = TransactionType.VENDA
    endereco: str = Field(..., min_length=5)
    bairro: Optional[str] = None
    cidade: str = Field(..., min_length=2, max_length=100)
    provincia: str = Field(..., min_length=2, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    preco_venda: Optional[float] = None
    preco_arrendamento: Optional[float] = None
    condominio: Optional[float] = None
    area_total: Optional[int] = None
    area_util: Optional[int] = None
    quartos: int = Field(0, ge=0)
    suites: int = Field(0, ge=0)
    banheiros: int = Field(0, ge=0)
    vagas_garagem: int = Field(0, ge=0)
    ano_construcao: Optional[int] = None
    caracteristicas: Optional[List[str]] = None
    imagens: Optional[List[str]] = None
    video_url: Optional[str] = None
    tour_virtual_url: Optional[str] = None
    destaque: bool = False


class REPropertyCreate(REPropertyBase):
    """Schema para criar imóvel"""
    pass


class REPropertyUpdate(BaseModel):
    """Schema para atualizar imóvel"""
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    tipo: Optional[PropertyTypeRE] = None
    tipo_transacao: Optional[TransactionType] = None
    endereco: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    provincia: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    preco_venda: Optional[float] = None
    preco_arrendamento: Optional[float] = None
    condominio: Optional[float] = None
    area_total: Optional[int] = None
    area_util: Optional[int] = None
    quartos: Optional[int] = None
    suites: Optional[int] = None
    banheiros: Optional[int] = None
    vagas_garagem: Optional[int] = None
    ano_construcao: Optional[int] = None
    caracteristicas: Optional[List[str]] = None
    imagens: Optional[List[str]] = None
    video_url: Optional[str] = None
    tour_virtual_url: Optional[str] = None
    destaque: Optional[bool] = None
    status: Optional[PropertyStatusRE] = None


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
    bairro: Optional[str]
    preco_venda: Optional[float]
    preco_arrendamento: Optional[float]
    quartos: int
    area_util: Optional[int]
    imagem_principal: Optional[str] = None
    destaque: bool
    
    model_config = ConfigDict(from_attributes=True)


class REPropertyDetailResponse(REPropertyResponse):
    """Schema detalhado com info do agente"""
    agent_nome: str
    agent_telefone: Optional[str]
    agent_foto: Optional[str]


# ============================================
# Lead Schemas
# ============================================

class LeadCreate(BaseModel):
    """Schema para criar lead"""
    property_id: UUID
    nome: str = Field(..., min_length=2, max_length=120)
    telefone: str = Field(..., min_length=9)
    email: Optional[str] = None
    mensagem: Optional[str] = None
    tipo_interesse: str = "informacao"


class LeadUpdate(BaseModel):
    """Schema para atualizar lead"""
    status: Optional[LeadStatus] = None
    notas_agente: Optional[str] = None
    visita_agendada: Optional[datetime] = None


class LeadResponse(BaseModel):
    """Schema de resposta de lead"""
    id: UUID
    property_id: UUID
    user_id: Optional[UUID]
    agent_id: UUID
    nome: str
    telefone: str
    email: Optional[str]
    mensagem: Optional[str]
    tipo_interesse: str
    status: LeadStatus
    notas_agente: Optional[str]
    visita_agendada: Optional[datetime]
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
    property: Optional[REPropertyListResponse] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# Search Schemas
# ============================================

class REPropertySearchParams(BaseModel):
    """Parâmetros de busca"""
    cidade: Optional[str] = None
    provincia: Optional[str] = None
    bairro: Optional[str] = None
    tipo: Optional[PropertyTypeRE] = None
    tipo_transacao: Optional[TransactionType] = None
    preco_min: Optional[float] = None
    preco_max: Optional[float] = None
    quartos_min: Optional[int] = None
    area_min: Optional[int] = None


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
