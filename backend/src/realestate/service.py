"""
TUDOaqui API - Real Estate Service
"""
from typing import List, Optional
from datetime import datetime, timezone
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select, and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.realestate.models import (
    RealEstateAgent, AgentStatus,
    RealEstateProperty, PropertyTypeRE, TransactionType, PropertyStatusRE,
    Lead, LeadStatus,
    PropertyFavorite
)
from src.users.models import User, UserRole


class RealEstateService:
    """Serviço de Real Estate"""
    
    # ============================================
    # Agent Management
    # ============================================
    
    async def register_agent(
        self,
        db: AsyncSession,
        user_id: UUID,
        data: dict
    ) -> RealEstateAgent:
        """Regista novo agente imobiliário"""
        # Verifica se já é agente
        result = await db.execute(
            select(RealEstateAgent).where(RealEstateAgent.user_id == user_id)
        )
        if result.scalar_one_or_none():
            raise ValueError("Utilizador já é agente registado")
        
        # Atualiza role do usuário
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if user:
            user.role = UserRole.AGENTE_IMOBILIARIO.value
        
        agent = RealEstateAgent(
            user_id=user_id,
            nome_profissional=data["nome_profissional"],
            bio=data.get("bio"),
            foto_url=data.get("foto_url"),
            numero_licenca=data.get("numero_licenca"),
            telefone_profissional=data.get("telefone_profissional"),
            email_profissional=data.get("email_profissional"),
            provincias={"items": data.get("provincias", [])},
            especialidades={"items": data.get("especialidades", [])},
            status=AgentStatus.PENDENTE.value
        )
        
        db.add(agent)
        await db.commit()
        await db.refresh(agent)
        return agent
    
    async def get_agent(self, db: AsyncSession, agent_id: UUID) -> Optional[RealEstateAgent]:
        """Obtém agente por ID"""
        result = await db.execute(
            select(RealEstateAgent)
            .where(RealEstateAgent.id == agent_id)
            .options(joinedload(RealEstateAgent.user))
        )
        return result.scalar_one_or_none()
    
    async def get_agent_by_user(self, db: AsyncSession, user_id: UUID) -> Optional[RealEstateAgent]:
        """Obtém agente pelo user_id"""
        result = await db.execute(
            select(RealEstateAgent).where(RealEstateAgent.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def update_agent(
        self,
        db: AsyncSession,
        agent_id: UUID,
        data: dict
    ) -> RealEstateAgent:
        """Atualiza agente"""
        agent = await self.get_agent(db, agent_id)
        if not agent:
            raise ValueError("Agente não encontrado")
        
        for field, value in data.items():
            if value is not None:
                if field in ["provincias", "especialidades"]:
                    value = {"items": value}
                setattr(agent, field, value)
        
        await db.commit()
        await db.refresh(agent)
        return agent
    
    async def list_agents(
        self,
        db: AsyncSession,
        provincia: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[RealEstateAgent]:
        """Lista agentes aprovados"""
        query = select(RealEstateAgent).where(
            RealEstateAgent.status == AgentStatus.APROVADO.value
        )
        
        # TODO: Filtrar por província quando JSON search disponível
        
        query = query.order_by(RealEstateAgent.rating_medio.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    # ============================================
    # Property Management
    # ============================================
    
    async def create_property(
        self,
        db: AsyncSession,
        agent_id: UUID,
        data: dict
    ) -> RealEstateProperty:
        """Cria novo imóvel"""
        prop = RealEstateProperty(
            agent_id=agent_id,
            titulo=data["titulo"],
            descricao=data.get("descricao"),
            tipo=data.get("tipo", PropertyTypeRE.APARTAMENTO.value),
            tipo_transacao=data.get("tipo_transacao", TransactionType.VENDA.value),
            endereco=data["endereco"],
            bairro=data.get("bairro"),
            cidade=data["cidade"],
            provincia=data["provincia"],
            latitude=Decimal(str(data["latitude"])) if data.get("latitude") else None,
            longitude=Decimal(str(data["longitude"])) if data.get("longitude") else None,
            preco_venda=Decimal(str(data["preco_venda"])) if data.get("preco_venda") else None,
            preco_arrendamento=Decimal(str(data["preco_arrendamento"])) if data.get("preco_arrendamento") else None,
            condominio=Decimal(str(data["condominio"])) if data.get("condominio") else None,
            area_total=data.get("area_total"),
            area_util=data.get("area_util"),
            quartos=data.get("quartos", 0),
            suites=data.get("suites", 0),
            banheiros=data.get("banheiros", 0),
            vagas_garagem=data.get("vagas_garagem", 0),
            ano_construcao=data.get("ano_construcao"),
            caracteristicas={"items": data.get("caracteristicas", [])},
            imagens={"urls": data.get("imagens", [])},
            video_url=data.get("video_url"),
            tour_virtual_url=data.get("tour_virtual_url"),
            destaque=data.get("destaque", False),
            status=PropertyStatusRE.PENDENTE.value
        )
        
        db.add(prop)
        await db.commit()
        await db.refresh(prop)
        return prop
    
    async def get_property(self, db: AsyncSession, property_id: UUID) -> Optional[RealEstateProperty]:
        """Obtém imóvel por ID"""
        result = await db.execute(
            select(RealEstateProperty)
            .where(RealEstateProperty.id == property_id)
            .options(joinedload(RealEstateProperty.agent).joinedload(RealEstateAgent.user))
        )
        return result.scalar_one_or_none()
    
    async def update_property(
        self,
        db: AsyncSession,
        property_id: UUID,
        data: dict
    ) -> RealEstateProperty:
        """Atualiza imóvel"""
        prop = await self.get_property(db, property_id)
        if not prop:
            raise ValueError("Imóvel não encontrado")
        
        for field, value in data.items():
            if value is not None:
                if field in ["preco_venda", "preco_arrendamento", "condominio", "latitude", "longitude"]:
                    value = Decimal(str(value)) if value else None
                if field == "caracteristicas":
                    value = {"items": value}
                if field == "imagens":
                    value = {"urls": value}
                setattr(prop, field, value)
        
        await db.commit()
        await db.refresh(prop)
        return prop
    
    async def list_properties(
        self,
        db: AsyncSession,
        cidade: Optional[str] = None,
        provincia: Optional[str] = None,
        bairro: Optional[str] = None,
        tipo: Optional[PropertyTypeRE] = None,
        tipo_transacao: Optional[TransactionType] = None,
        preco_min: Optional[float] = None,
        preco_max: Optional[float] = None,
        quartos_min: Optional[int] = None,
        area_min: Optional[int] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[RealEstateProperty]:
        """Lista imóveis"""
        query = select(RealEstateProperty).where(
            RealEstateProperty.status == PropertyStatusRE.ATIVO.value
        )
        
        if cidade:
            query = query.where(RealEstateProperty.cidade.ilike(f"%{cidade}%"))
        if provincia:
            query = query.where(RealEstateProperty.provincia == provincia)
        if bairro:
            query = query.where(RealEstateProperty.bairro.ilike(f"%{bairro}%"))
        if tipo:
            query = query.where(RealEstateProperty.tipo == tipo.value)
        if tipo_transacao:
            query = query.where(RealEstateProperty.tipo_transacao == tipo_transacao.value)
        if quartos_min:
            query = query.where(RealEstateProperty.quartos >= quartos_min)
        if area_min:
            query = query.where(RealEstateProperty.area_util >= area_min)
        
        # Filtro de preço baseado no tipo de transação
        if preco_min or preco_max:
            price_filters = []
            if preco_min:
                price_filters.append(or_(
                    RealEstateProperty.preco_venda >= preco_min,
                    RealEstateProperty.preco_arrendamento >= preco_min
                ))
            if preco_max:
                price_filters.append(or_(
                    RealEstateProperty.preco_venda <= preco_max,
                    RealEstateProperty.preco_arrendamento <= preco_max
                ))
            if price_filters:
                query = query.where(and_(*price_filters))
        
        # Destaque primeiro, depois por data
        query = query.order_by(
            RealEstateProperty.destaque.desc(),
            RealEstateProperty.created_at.desc()
        ).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def list_agent_properties(
        self,
        db: AsyncSession,
        agent_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[RealEstateProperty]:
        """Lista imóveis do agente"""
        result = await db.execute(
            select(RealEstateProperty)
            .where(RealEstateProperty.agent_id == agent_id)
            .order_by(RealEstateProperty.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def publish_property(self, db: AsyncSession, property_id: UUID) -> RealEstateProperty:
        """Publica imóvel"""
        prop = await self.get_property(db, property_id)
        if not prop:
            raise ValueError("Imóvel não encontrado")
        
        prop.status = PropertyStatusRE.ATIVO.value
        await db.commit()
        await db.refresh(prop)
        return prop
    
    async def increment_views(self, db: AsyncSession, property_id: UUID):
        """Incrementa visualizações"""
        prop = await self.get_property(db, property_id)
        if prop:
            prop.visualizacoes += 1
            await db.commit()
    
    # ============================================
    # Leads
    # ============================================
    
    async def create_lead(
        self,
        db: AsyncSession,
        user_id: Optional[UUID],
        data: dict
    ) -> Lead:
        """Cria lead/contacto"""
        prop = await self.get_property(db, data["property_id"])
        if not prop:
            raise ValueError("Imóvel não encontrado")
        
        lead = Lead(
            property_id=data["property_id"],
            user_id=user_id,
            agent_id=prop.agent_id,
            nome=data["nome"],
            telefone=data["telefone"],
            email=data.get("email"),
            mensagem=data.get("mensagem"),
            tipo_interesse=data.get("tipo_interesse", "informacao"),
            status=LeadStatus.NOVO.value
        )
        
        db.add(lead)
        await db.commit()
        await db.refresh(lead)
        return lead
    
    async def get_lead(self, db: AsyncSession, lead_id: UUID) -> Optional[Lead]:
        """Obtém lead por ID"""
        result = await db.execute(
            select(Lead)
            .where(Lead.id == lead_id)
            .options(joinedload(Lead.property))
        )
        return result.scalar_one_or_none()
    
    async def update_lead(
        self,
        db: AsyncSession,
        lead_id: UUID,
        data: dict
    ) -> Lead:
        """Atualiza lead"""
        lead = await self.get_lead(db, lead_id)
        if not lead:
            raise ValueError("Lead não encontrado")
        
        for field, value in data.items():
            if value is not None:
                setattr(lead, field, value)
        
        await db.commit()
        await db.refresh(lead)
        return lead
    
    async def list_agent_leads(
        self,
        db: AsyncSession,
        agent_id: UUID,
        status: Optional[LeadStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Lead]:
        """Lista leads do agente"""
        query = select(Lead).where(Lead.agent_id == agent_id)
        
        if status:
            query = query.where(Lead.status == status.value)
        
        query = query.options(joinedload(Lead.property))
        query = query.order_by(Lead.created_at.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.unique().scalars().all()
    
    # ============================================
    # Favorites
    # ============================================
    
    async def add_favorite(
        self,
        db: AsyncSession,
        user_id: UUID,
        property_id: UUID
    ) -> PropertyFavorite:
        """Adiciona aos favoritos"""
        # Verifica se já é favorito
        result = await db.execute(
            select(PropertyFavorite).where(and_(
                PropertyFavorite.user_id == user_id,
                PropertyFavorite.property_id == property_id
            ))
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing
        
        # Verifica imóvel
        prop = await self.get_property(db, property_id)
        if not prop:
            raise ValueError("Imóvel não encontrado")
        
        favorite = PropertyFavorite(
            user_id=user_id,
            property_id=property_id
        )
        
        db.add(favorite)
        prop.favoritos += 1
        
        await db.commit()
        await db.refresh(favorite)
        return favorite
    
    async def remove_favorite(
        self,
        db: AsyncSession,
        user_id: UUID,
        property_id: UUID
    ) -> bool:
        """Remove dos favoritos"""
        result = await db.execute(
            select(PropertyFavorite).where(and_(
                PropertyFavorite.user_id == user_id,
                PropertyFavorite.property_id == property_id
            ))
        )
        favorite = result.scalar_one_or_none()
        
        if not favorite:
            return False
        
        prop = await self.get_property(db, property_id)
        if prop and prop.favoritos > 0:
            prop.favoritos -= 1
        
        await db.delete(favorite)
        await db.commit()
        return True
    
    async def list_user_favorites(
        self,
        db: AsyncSession,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[PropertyFavorite]:
        """Lista favoritos do usuário"""
        result = await db.execute(
            select(PropertyFavorite)
            .where(PropertyFavorite.user_id == user_id)
            .options(joinedload(PropertyFavorite.property))
            .order_by(PropertyFavorite.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.unique().scalars().all()
    
    # ============================================
    # Stats
    # ============================================
    
    async def get_agent_stats(self, db: AsyncSession, agent_id: UUID) -> dict:
        """Estatísticas do agente"""
        # Total imóveis
        imoveis_result = await db.execute(
            select(func.count(RealEstateProperty.id))
            .where(RealEstateProperty.agent_id == agent_id)
        )
        total_imoveis = imoveis_result.scalar() or 0
        
        # Imóveis ativos
        ativos_result = await db.execute(
            select(func.count(RealEstateProperty.id))
            .where(and_(
                RealEstateProperty.agent_id == agent_id,
                RealEstateProperty.status == PropertyStatusRE.ATIVO.value
            ))
        )
        imoveis_ativos = ativos_result.scalar() or 0
        
        # Total leads
        leads_result = await db.execute(
            select(func.count(Lead.id))
            .where(Lead.agent_id == agent_id)
        )
        total_leads = leads_result.scalar() or 0
        
        # Leads novos
        novos_result = await db.execute(
            select(func.count(Lead.id))
            .where(and_(
                Lead.agent_id == agent_id,
                Lead.status == LeadStatus.NOVO.value
            ))
        )
        leads_novos = novos_result.scalar() or 0
        
        # Visitas agendadas
        visitas_result = await db.execute(
            select(func.count(Lead.id))
            .where(and_(
                Lead.agent_id == agent_id,
                Lead.status == LeadStatus.VISITA_AGENDADA.value
            ))
        )
        visitas_agendadas = visitas_result.scalar() or 0
        
        # Total visualizações
        views_result = await db.execute(
            select(func.sum(RealEstateProperty.visualizacoes))
            .where(RealEstateProperty.agent_id == agent_id)
        )
        total_visualizacoes = views_result.scalar() or 0
        
        return {
            "total_imoveis": total_imoveis,
            "imoveis_ativos": imoveis_ativos,
            "total_leads": total_leads,
            "leads_novos": leads_novos,
            "visitas_agendadas": visitas_agendadas,
            "total_visualizacoes": total_visualizacoes
        }


# Instância global
realestate_service = RealEstateService()
