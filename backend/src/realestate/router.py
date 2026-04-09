"""
TUDOaqui API - Real Estate Router
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.users.models import User, UserRole
from src.auth.dependencies import get_current_user, require_roles
from src.realestate.models import PropertyTypeRE, TransactionType, PropertyStatusRE, LeadStatus
from src.realestate.schemas import (
    AgentCreate, AgentUpdate, AgentResponse,
    REPropertyCreate, REPropertyUpdate, REPropertyResponse, REPropertyListResponse, REPropertyDetailResponse,
    LeadCreate, LeadUpdate, LeadResponse, LeadDetailResponse,
    FavoriteResponse, AgentStats
)
from src.realestate.service import realestate_service


router = APIRouter(prefix="/realestate", tags=["Imobiliário"])


# ============================================
# Agents - Público
# ============================================

@router.get("/agents", response_model=list[AgentResponse])
async def list_agents(
    provincia: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Lista agentes aprovados."""
    agents = await realestate_service.list_agents(db, provincia=provincia, limit=limit, offset=offset)
    return [
        AgentResponse(
            id=a.id,
            user_id=a.user_id,
            nome_profissional=a.nome_profissional,
            bio=a.bio,
            foto_url=a.foto_url,
            numero_licenca=a.numero_licenca,
            telefone_profissional=a.telefone_profissional,
            email_profissional=a.email_profissional,
            provincias=a.provincias.get("items", []) if a.provincias else None,
            especialidades=a.especialidades.get("items", []) if a.especialidades else None,
            rating_medio=float(a.rating_medio),
            total_vendas=a.total_vendas,
            total_arrendamentos=a.total_arrendamentos,
            plano=a.plano,
            status=a.status,
            created_at=a.created_at
        )
        for a in agents
    ]


@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Obtém detalhes de um agente."""
    agent = await realestate_service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agente não encontrado")
    
    return AgentResponse(
        id=agent.id,
        user_id=agent.user_id,
        nome_profissional=agent.nome_profissional,
        bio=agent.bio,
        foto_url=agent.foto_url,
        numero_licenca=agent.numero_licenca,
        telefone_profissional=agent.telefone_profissional,
        email_profissional=agent.email_profissional,
        provincias=agent.provincias.get("items", []) if agent.provincias else None,
        especialidades=agent.especialidades.get("items", []) if agent.especialidades else None,
        rating_medio=float(agent.rating_medio),
        total_vendas=agent.total_vendas,
        total_arrendamentos=agent.total_arrendamentos,
        plano=agent.plano,
        status=agent.status,
        created_at=agent.created_at
    )


# ============================================
# Agents - Gestão
# ============================================

@router.post("/agents/register", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def register_agent(
    request: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Regista-se como agente imobiliário."""
    try:
        agent = await realestate_service.register_agent(db, current_user.id, request.model_dump())
        return await get_agent(agent.id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/agents/me/profile", response_model=AgentResponse)
async def get_my_agent_profile(
    current_user: User = Depends(require_roles(UserRole.AGENTE, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Obtém perfil de agente do usuário."""
    agent = await realestate_service.get_agent_by_user(db, current_user.id)
    if not agent:
        raise HTTPException(status_code=404, detail="Perfil de agente não encontrado")
    return await get_agent(agent.id, db)


@router.put("/agents/me", response_model=AgentResponse)
async def update_my_agent(
    request: AgentUpdate,
    current_user: User = Depends(require_roles(UserRole.AGENTE, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Atualiza perfil de agente."""
    agent = await realestate_service.get_agent_by_user(db, current_user.id)
    if not agent:
        raise HTTPException(status_code=404, detail="Perfil de agente não encontrado")
    
    try:
        agent = await realestate_service.update_agent(db, agent.id, request.model_dump(exclude_unset=True))
        return await get_agent(agent.id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/agents/me/stats", response_model=AgentStats)
async def get_my_stats(
    current_user: User = Depends(require_roles(UserRole.AGENTE, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Estatísticas do agente."""
    agent = await realestate_service.get_agent_by_user(db, current_user.id)
    if not agent:
        raise HTTPException(status_code=404, detail="Perfil de agente não encontrado")
    
    stats = await realestate_service.get_agent_stats(db, agent.id)
    return AgentStats(**stats)


# ============================================
# Properties - Público
# ============================================

@router.get("/properties", response_model=list[REPropertyListResponse])
async def list_properties(
    cidade: str | None = None,
    provincia: str | None = None,
    bairro: str | None = None,
    tipo: PropertyTypeRE | None = None,
    tipo_transacao: TransactionType | None = None,
    preco_min: float | None = None,
    preco_max: float | None = None,
    quartos_min: int | None = None,
    area_min: int | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Lista imóveis disponíveis."""
    properties = await realestate_service.list_properties(
        db, cidade=cidade, provincia=provincia, bairro=bairro,
        tipo=tipo, tipo_transacao=tipo_transacao,
        preco_min=preco_min, preco_max=preco_max,
        quartos_min=quartos_min, area_min=area_min,
        limit=limit, offset=offset
    )
    return [
        REPropertyListResponse(
            id=p.id,
            titulo=p.titulo,
            tipo=p.tipo,
            tipo_transacao=p.tipo_transacao,
            cidade=p.cidade,
            bairro=p.bairro,
            preco_venda=float(p.preco_venda) if p.preco_venda else None,
            preco_arrendamento=float(p.preco_arrendamento) if p.preco_arrendamento else None,
            quartos=p.quartos,
            area_util=p.area_util,
            imagem_principal=p.imagens.get("urls", [None])[0] if p.imagens else None,
            destaque=p.destaque
        )
        for p in properties
    ]


@router.get("/properties/{property_id}", response_model=REPropertyDetailResponse)
async def get_property(
    property_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Obtém detalhes de um imóvel."""
    prop = await realestate_service.get_property(db, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    # Incrementa visualizações
    await realestate_service.increment_views(db, property_id)
    
    return REPropertyDetailResponse(
        id=prop.id,
        agent_id=prop.agent_id,
        titulo=prop.titulo,
        descricao=prop.descricao,
        tipo=prop.tipo,
        tipo_transacao=prop.tipo_transacao,
        endereco=prop.endereco,
        bairro=prop.bairro,
        cidade=prop.cidade,
        provincia=prop.provincia,
        latitude=float(prop.latitude) if prop.latitude else None,
        longitude=float(prop.longitude) if prop.longitude else None,
        preco_venda=float(prop.preco_venda) if prop.preco_venda else None,
        preco_arrendamento=float(prop.preco_arrendamento) if prop.preco_arrendamento else None,
        condominio=float(prop.condominio) if prop.condominio else None,
        area_total=prop.area_total,
        area_util=prop.area_util,
        quartos=prop.quartos,
        suites=prop.suites,
        banheiros=prop.banheiros,
        vagas_garagem=prop.vagas_garagem,
        ano_construcao=prop.ano_construcao,
        caracteristicas=prop.caracteristicas.get("items", []) if prop.caracteristicas else None,
        imagens=prop.imagens.get("urls", []) if prop.imagens else None,
        video_url=prop.video_url,
        tour_virtual_url=prop.tour_virtual_url,
        destaque=prop.destaque,
        visualizacoes=prop.visualizacoes,
        favoritos=prop.favoritos,
        status=prop.status,
        created_at=prop.created_at,
        agent_nome=prop.agent.nome_profissional,
        agent_telefone=prop.agent.telefone_profissional,
        agent_foto=prop.agent.foto_url
    )


# ============================================
# Properties - Gestão (Agente)
# ============================================

@router.post("/properties", response_model=REPropertyResponse, status_code=status.HTTP_201_CREATED)
async def create_property(
    request: REPropertyCreate,
    current_user: User = Depends(require_roles(UserRole.AGENTE, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Cria novo imóvel."""
    agent = await realestate_service.get_agent_by_user(db, current_user.id)
    if not agent:
        raise HTTPException(status_code=400, detail="Perfil de agente não encontrado")
    
    prop = await realestate_service.create_property(db, agent.id, request.model_dump())
    return await get_property_simple(prop.id, db)


async def get_property_simple(property_id: UUID, db: AsyncSession) -> REPropertyResponse:
    """Helper para retornar resposta simples"""
    prop = await realestate_service.get_property(db, property_id)
    return REPropertyResponse(
        id=prop.id,
        agent_id=prop.agent_id,
        titulo=prop.titulo,
        descricao=prop.descricao,
        tipo=prop.tipo,
        tipo_transacao=prop.tipo_transacao,
        endereco=prop.endereco,
        bairro=prop.bairro,
        cidade=prop.cidade,
        provincia=prop.provincia,
        latitude=float(prop.latitude) if prop.latitude else None,
        longitude=float(prop.longitude) if prop.longitude else None,
        preco_venda=float(prop.preco_venda) if prop.preco_venda else None,
        preco_arrendamento=float(prop.preco_arrendamento) if prop.preco_arrendamento else None,
        condominio=float(prop.condominio) if prop.condominio else None,
        area_total=prop.area_total,
        area_util=prop.area_util,
        quartos=prop.quartos,
        suites=prop.suites,
        banheiros=prop.banheiros,
        vagas_garagem=prop.vagas_garagem,
        ano_construcao=prop.ano_construcao,
        caracteristicas=prop.caracteristicas.get("items", []) if prop.caracteristicas else None,
        imagens=prop.imagens.get("urls", []) if prop.imagens else None,
        video_url=prop.video_url,
        tour_virtual_url=prop.tour_virtual_url,
        destaque=prop.destaque,
        visualizacoes=prop.visualizacoes,
        favoritos=prop.favoritos,
        status=prop.status,
        created_at=prop.created_at
    )


@router.get("/properties/my/list", response_model=list[REPropertyResponse])
async def list_my_properties(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_roles(UserRole.AGENTE, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Lista imóveis do agente."""
    agent = await realestate_service.get_agent_by_user(db, current_user.id)
    if not agent:
        raise HTTPException(status_code=400, detail="Perfil de agente não encontrado")
    
    properties = await realestate_service.list_agent_properties(db, agent.id, limit, offset)
    return [await get_property_simple(p.id, db) for p in properties]


@router.put("/properties/{property_id}", response_model=REPropertyResponse)
async def update_property(
    property_id: UUID,
    request: REPropertyUpdate,
    current_user: User = Depends(require_roles(UserRole.AGENTE, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Atualiza imóvel."""
    prop = await realestate_service.get_property(db, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    agent = await realestate_service.get_agent_by_user(db, current_user.id)
    if not agent or (prop.agent_id != agent.id and current_user.role != UserRole.ADMIN.value):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        prop = await realestate_service.update_property(db, property_id, request.model_dump(exclude_unset=True))
        return await get_property_simple(prop.id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/properties/{property_id}/publish", response_model=REPropertyResponse)
async def publish_property(
    property_id: UUID,
    current_user: User = Depends(require_roles(UserRole.AGENTE, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Publica imóvel."""
    prop = await realestate_service.get_property(db, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    agent = await realestate_service.get_agent_by_user(db, current_user.id)
    if not agent or (prop.agent_id != agent.id and current_user.role != UserRole.ADMIN.value):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    prop = await realestate_service.publish_property(db, property_id)
    return await get_property_simple(prop.id, db)


# ============================================
# Leads
# ============================================

@router.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    request: LeadCreate,
    current_user: User | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cria contacto/lead para um imóvel."""
    try:
        user_id = current_user.id if current_user else None
        lead = await realestate_service.create_lead(db, user_id, request.model_dump())
        return LeadResponse(
            id=lead.id,
            property_id=lead.property_id,
            user_id=lead.user_id,
            agent_id=lead.agent_id,
            nome=lead.nome,
            telefone=lead.telefone,
            email=lead.email,
            mensagem=lead.mensagem,
            tipo_interesse=lead.tipo_interesse,
            status=lead.status,
            notas_agente=lead.notas_agente,
            visita_agendada=lead.visita_agendada,
            created_at=lead.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/leads", response_model=list[LeadDetailResponse])
async def list_my_leads(
    status: LeadStatus | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_roles(UserRole.AGENTE, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Lista leads do agente."""
    agent = await realestate_service.get_agent_by_user(db, current_user.id)
    if not agent:
        raise HTTPException(status_code=400, detail="Perfil de agente não encontrado")
    
    leads = await realestate_service.list_agent_leads(db, agent.id, status, limit, offset)
    return [
        LeadDetailResponse(
            id=lead.id,
            property_id=lead.property_id,
            user_id=lead.user_id,
            agent_id=lead.agent_id,
            nome=lead.nome,
            telefone=lead.telefone,
            email=lead.email,
            mensagem=lead.mensagem,
            tipo_interesse=lead.tipo_interesse,
            status=lead.status,
            notas_agente=lead.notas_agente,
            visita_agendada=lead.visita_agendada,
            created_at=lead.created_at,
            property_titulo=lead.property.titulo,
            property_tipo=lead.property.tipo,
            property_cidade=lead.property.cidade
        )
        for lead in leads
    ]


@router.put("/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: UUID,
    request: LeadUpdate,
    current_user: User = Depends(require_roles(UserRole.AGENTE, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Atualiza lead."""
    lead = await realestate_service.get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    
    agent = await realestate_service.get_agent_by_user(db, current_user.id)
    if not agent or (lead.agent_id != agent.id and current_user.role != UserRole.ADMIN.value):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        lead = await realestate_service.update_lead(db, lead_id, request.model_dump(exclude_unset=True))
        return LeadResponse(
            id=lead.id,
            property_id=lead.property_id,
            user_id=lead.user_id,
            agent_id=lead.agent_id,
            nome=lead.nome,
            telefone=lead.telefone,
            email=lead.email,
            mensagem=lead.mensagem,
            tipo_interesse=lead.tipo_interesse,
            status=lead.status,
            notas_agente=lead.notas_agente,
            visita_agendada=lead.visita_agendada,
            created_at=lead.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# Favorites
# ============================================

@router.post("/favorites/{property_id}", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    property_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Adiciona imóvel aos favoritos."""
    try:
        favorite = await realestate_service.add_favorite(db, current_user.id, property_id)
        return FavoriteResponse(
            id=favorite.id,
            property_id=favorite.property_id,
            created_at=favorite.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/favorites/{property_id}")
async def remove_favorite(
    property_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove imóvel dos favoritos."""
    removed = await realestate_service.remove_favorite(db, current_user.id, property_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Favorito não encontrado")
    return {"status": "success", "message": "Removido dos favoritos"}


@router.get("/favorites", response_model=list[FavoriteResponse])
async def list_my_favorites(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lista favoritos do usuário."""
    favorites = await realestate_service.list_user_favorites(db, current_user.id, limit, offset)
    return [
        FavoriteResponse(
            id=f.id,
            property_id=f.property_id,
            created_at=f.created_at,
            property=REPropertyListResponse(
                id=f.property.id,
                titulo=f.property.titulo,
                tipo=f.property.tipo,
                tipo_transacao=f.property.tipo_transacao,
                cidade=f.property.cidade,
                bairro=f.property.bairro,
                preco_venda=float(f.property.preco_venda) if f.property.preco_venda else None,
                preco_arrendamento=float(f.property.preco_arrendamento) if f.property.preco_arrendamento else None,
                quartos=f.property.quartos,
                area_util=f.property.area_util,
                imagem_principal=f.property.imagens.get("urls", [None])[0] if f.property.imagens else None,
                destaque=f.property.destaque
            ) if f.property else None
        )
        for f in favorites
    ]
