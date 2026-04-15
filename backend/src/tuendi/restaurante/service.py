"""
TUDOaqui API - Tuendi Restaurante Service
"""
from typing import List, Optional, Tuple
import secrets
import math
from datetime import datetime, timezone, time
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.tuendi.restaurante.models import (
    Restaurant, RestaurantStatus,
    MenuCategory, MenuItem, MenuItemStatus,
    FoodOrder, FoodOrderStatus, FoodOrderItem,
    RestaurantReview
)


class RestauranteService:
    """Serviço de Restaurantes"""
    
    TAXA_PLATAFORMA = Decimal("0.10")  # 10%
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcula distância usando Haversine"""
        R = 6371
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    @staticmethod
    def generate_code() -> str:
        return ''.join(secrets.choice('0123456789') for _ in range(4))
    
    # ============================================
    # Restaurant Management
    # ============================================
    
    async def create_restaurant(
        self,
        db: AsyncSession,
        owner_id: UUID,
        data: dict
    ) -> Restaurant:
        """Cria novo restaurante"""
        restaurant = Restaurant(
            owner_id=owner_id,
            nome=data["nome"],
            descricao=data.get("descricao"),
            logo_url=data.get("logo_url"),
            banner_url=data.get("banner_url"),
            endereco=data["endereco"],
            cidade=data["cidade"],
            latitude=Decimal(str(data["latitude"])),
            longitude=Decimal(str(data["longitude"])),
            hora_abertura=data.get("hora_abertura", time(8, 0)),
            hora_fecho=data.get("hora_fecho", time(22, 0)),
            dias_funcionamento={"dias": data.get("dias_funcionamento", [0,1,2,3,4,5,6])},
            raio_entrega_km=data.get("raio_entrega_km", 10),
            tempo_preparo_min=data.get("tempo_preparo_min", 30),
            pedido_minimo=Decimal(str(data.get("pedido_minimo", 0))),
            taxa_entrega=Decimal(str(data.get("taxa_entrega", 0))),
            categorias={"items": data.get("categorias", [])},
            telefone=data["telefone"],
            status=RestaurantStatus.PENDENTE.value
        )
        
        db.add(restaurant)
        await db.commit()
        await db.refresh(restaurant)
        return restaurant
    
    async def get_restaurant(self, db: AsyncSession, restaurant_id: UUID) -> Optional[Restaurant]:
        """Obtém restaurante por ID"""
        result = await db.execute(
            select(Restaurant)
            .where(Restaurant.id == restaurant_id)
            .options(
                joinedload(Restaurant.menu_categories).joinedload(MenuCategory.items)
            )
        )
        return result.unique().scalar_one_or_none()
    
    async def get_restaurant_by_owner(self, db: AsyncSession, owner_id: UUID) -> Optional[Restaurant]:
        """Obtém restaurante pelo owner"""
        result = await db.execute(
            select(Restaurant).where(Restaurant.owner_id == owner_id)
        )
        return result.scalar_one_or_none()
    
    async def update_restaurant(
        self,
        db: AsyncSession,
        restaurant_id: UUID,
        data: dict
    ) -> Restaurant:
        """Atualiza restaurante"""
        restaurant = await self.get_restaurant(db, restaurant_id)
        if not restaurant:
            raise ValueError("Restaurante não encontrado")
        
        for field, value in data.items():
            if value is not None:
                if field in ["pedido_minimo", "taxa_entrega", "latitude", "longitude"]:
                    value = Decimal(str(value))
                if field == "dias_funcionamento":
                    value = {"dias": value}
                if field == "categorias":
                    value = {"items": value}
                setattr(restaurant, field, value)
        
        await db.commit()
        await db.refresh(restaurant)
        return restaurant
    
    async def list_restaurants(
        self,
        db: AsyncSession,
        cidade: Optional[str] = None,
        categoria: Optional[str] = None,
        user_lat: Optional[float] = None,
        user_lon: Optional[float] = None,
        raio_km: float = 10,
        aberto_agora: bool = False,
        limit: int = 20,
        offset: int = 0
    ) -> List[Tuple[Restaurant, Optional[float]]]:
        """Lista restaurantes com distância"""
        query = select(Restaurant).where(
            Restaurant.status == RestaurantStatus.APROVADO.value
        )
        
        if cidade:
            query = query.where(Restaurant.cidade.ilike(f"%{cidade}%"))
        
        if aberto_agora:
            query = query.where(Restaurant.aberto.is_(True))
        
        # TODO: Filtrar por categoria em JSONB
        
        query = query.order_by(Restaurant.rating_medio.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        restaurants = result.scalars().all()
        
        # Calcular distâncias
        results = []
        for r in restaurants:
            distance = None
            if user_lat and user_lon:
                distance = self.calculate_distance(
                    user_lat, user_lon, float(r.latitude), float(r.longitude)
                )
                # Filtrar por raio
                if distance > raio_km:
                    continue
            results.append((r, distance))
        
        # Ordenar por distância se disponível
        if user_lat and user_lon:
            results.sort(key=lambda x: x[1] if x[1] else float('inf'))
        
        return results
    
    # ============================================
    # Menu Management
    # ============================================
    
    async def create_category(
        self,
        db: AsyncSession,
        restaurant_id: UUID,
        data: dict
    ) -> MenuCategory:
        """Cria categoria do menu"""
        category = MenuCategory(
            restaurant_id=restaurant_id,
            nome=data["nome"],
            descricao=data.get("descricao"),
            ordem=data.get("ordem", 0)
        )
        
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category
    
    async def create_menu_item(
        self,
        db: AsyncSession,
        restaurant_id: UUID,
        data: dict
    ) -> MenuItem:
        """Cria item do menu"""
        item = MenuItem(
            restaurant_id=restaurant_id,
            category_id=data["category_id"],
            nome=data["nome"],
            descricao=data.get("descricao"),
            imagem_url=data.get("imagem_url"),
            preco=Decimal(str(data["preco"])),
            preco_promocional=Decimal(str(data["preco_promocional"])) if data.get("preco_promocional") else None,
            tempo_preparo_min=data.get("tempo_preparo_min"),
            opcoes={"opcoes": data.get("opcoes", [])},
            info_nutricional=data.get("info_nutricional"),
            popular=data.get("popular", False),
            status=MenuItemStatus.ATIVO.value
        )
        
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item
    
    async def update_menu_item(
        self,
        db: AsyncSession,
        item_id: UUID,
        data: dict
    ) -> MenuItem:
        """Atualiza item do menu"""
        result = await db.execute(
            select(MenuItem).where(MenuItem.id == item_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            raise ValueError("Item não encontrado")
        
        for field, value in data.items():
            if value is not None:
                if field in ["preco", "preco_promocional"]:
                    value = Decimal(str(value)) if value else None
                if field == "opcoes":
                    value = {"opcoes": value}
                setattr(item, field, value)
        
        await db.commit()
        await db.refresh(item)
        return item
    
    async def get_menu(self, db: AsyncSession, restaurant_id: UUID) -> List[MenuCategory]:
        """Obtém menu completo"""
        result = await db.execute(
            select(MenuCategory)
            .where(and_(
                MenuCategory.restaurant_id == restaurant_id,
                MenuCategory.ativo.is_(True)
            ))
            .options(joinedload(MenuCategory.items))
            .order_by(MenuCategory.ordem)
        )
        return result.unique().scalars().all()
    
    # ============================================
    # Orders
    # ============================================
    
    async def create_order(
        self,
        db: AsyncSession,
        customer_id: UUID,
        data: dict
    ) -> FoodOrder:
        """Cria pedido"""
        restaurant_id = data["restaurant_id"]
        
        # Valida restaurante
        restaurant = await self.get_restaurant(db, restaurant_id)
        if not restaurant or restaurant.status != RestaurantStatus.APROVADO.value:
            raise ValueError("Restaurante não disponível")
        
        if not restaurant.aberto:
            raise ValueError("Restaurante fechado")
        
        # Processa itens
        items_data = data["items"]
        order_items = []
        subtotal = Decimal("0")
        max_tempo_preparo = restaurant.tempo_preparo_min
        
        for item_data in items_data:
            result = await db.execute(
                select(MenuItem).where(MenuItem.id == item_data["menu_item_id"])
            )
            menu_item = result.scalar_one_or_none()
            
            if not menu_item or menu_item.restaurant_id != restaurant_id:
                raise ValueError(f"Item {item_data['menu_item_id']} não encontrado")
            
            if menu_item.status != MenuItemStatus.ATIVO.value:
                raise ValueError(f"Item {menu_item.nome} não disponível")
            
            preco = menu_item.preco_atual
            item_subtotal = preco * item_data["quantidade"]
            subtotal += item_subtotal
            
            # Atualiza tempo máximo de preparo
            if menu_item.tempo_preparo_min and menu_item.tempo_preparo_min > max_tempo_preparo:
                max_tempo_preparo = menu_item.tempo_preparo_min
            
            order_items.append({
                "menu_item_id": menu_item.id,
                "quantidade": item_data["quantidade"],
                "preco_unitario": preco,
                "subtotal": item_subtotal,
                "opcoes_selecionadas": {"opcoes": item_data.get("opcoes_selecionadas", [])},
                "notas": item_data.get("notas"),
                "item_nome": menu_item.nome
            })
        
        # Verifica pedido mínimo
        if subtotal < restaurant.pedido_minimo:
            raise ValueError(f"Pedido mínimo: {restaurant.pedido_minimo} Kz")
        
        # Calcula taxa de entrega
        distancia = self.calculate_distance(
            float(restaurant.latitude), float(restaurant.longitude),
            data["latitude_entrega"], data["longitude_entrega"]
        )
        
        if distancia > restaurant.raio_entrega_km:
            raise ValueError(f"Fora do raio de entrega ({restaurant.raio_entrega_km}km)")
        
        taxa_entrega = restaurant.taxa_entrega
        total = subtotal + taxa_entrega
        
        # Cria pedido
        order = FoodOrder(
            customer_id=customer_id,
            restaurant_id=restaurant_id,
            endereco_entrega=data["endereco_entrega"],
            latitude_entrega=Decimal(str(data["latitude_entrega"])),
            longitude_entrega=Decimal(str(data["longitude_entrega"])),
            referencia_entrega=data.get("referencia_entrega"),
            subtotal=subtotal,
            taxa_entrega=taxa_entrega,
            desconto=Decimal("0"),
            total=total,
            telefone_contato=data["telefone_contato"],
            notas=data.get("notas"),
            tempo_preparo_estimado=max_tempo_preparo,
            codigo_entrega=self.generate_code(),
            status=FoodOrderStatus.PENDENTE.value
        )
        
        db.add(order)
        await db.flush()
        
        # Cria itens
        for item_data in order_items:
            item = FoodOrderItem(
                order_id=order.id,
                **item_data
            )
            db.add(item)
        
        # Atualiza stats
        restaurant.total_pedidos += 1
        
        await db.commit()
        await db.refresh(order)
        return order
    
    async def get_order(self, db: AsyncSession, order_id: UUID) -> Optional[FoodOrder]:
        """Obtém pedido"""
        result = await db.execute(
            select(FoodOrder)
            .where(FoodOrder.id == order_id)
            .options(
                joinedload(FoodOrder.items),
                joinedload(FoodOrder.restaurant),
                joinedload(FoodOrder.driver)
            )
        )
        return result.unique().scalar_one_or_none()
    
    async def update_order_status(
        self,
        db: AsyncSession,
        order_id: UUID,
        status: FoodOrderStatus,
        motivo: Optional[str] = None
    ) -> FoodOrder:
        """Atualiza status do pedido"""
        order = await self.get_order(db, order_id)
        if not order:
            raise ValueError("Pedido não encontrado")
        
        order.status = status.value
        now = datetime.now(timezone.utc)
        
        if status == FoodOrderStatus.ACEITE:
            order.aceite_at = now
        elif status == FoodOrderStatus.PRONTO:
            order.pronto_at = now
        elif status == FoodOrderStatus.RECOLHIDO:
            order.recolhido_at = now
        elif status == FoodOrderStatus.ENTREGUE:
            order.entregue_at = now
        elif status == FoodOrderStatus.CANCELADO:
            order.cancelado_at = now
            order.motivo_cancelamento = motivo
        
        await db.commit()
        await db.refresh(order)
        return order
    
    async def list_customer_orders(
        self,
        db: AsyncSession,
        customer_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> List[FoodOrder]:
        """Lista pedidos do cliente"""
        result = await db.execute(
            select(FoodOrder)
            .where(FoodOrder.customer_id == customer_id)
            .options(joinedload(FoodOrder.restaurant), joinedload(FoodOrder.items))
            .order_by(FoodOrder.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.unique().scalars().all()
    
    async def list_restaurant_orders(
        self,
        db: AsyncSession,
        restaurant_id: UUID,
        status: Optional[FoodOrderStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[FoodOrder]:
        """Lista pedidos do restaurante"""
        query = select(FoodOrder).where(FoodOrder.restaurant_id == restaurant_id)
        
        if status:
            query = query.where(FoodOrder.status == status.value)
        
        query = query.options(joinedload(FoodOrder.items), joinedload(FoodOrder.customer))
        query = query.order_by(FoodOrder.created_at.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.unique().scalars().all()
    
    # ============================================
    # Reviews
    # ============================================
    
    async def create_review(
        self,
        db: AsyncSession,
        order_id: UUID,
        user_id: UUID,
        data: dict
    ) -> RestaurantReview:
        """Cria avaliação"""
        order = await self.get_order(db, order_id)
        if not order:
            raise ValueError("Pedido não encontrado")
        
        if order.customer_id != user_id:
            raise ValueError("Apenas o cliente pode avaliar")
        
        if order.status != FoodOrderStatus.ENTREGUE.value:
            raise ValueError("Pedido não entregue")
        
        # Verifica se já avaliou
        existing = await db.execute(
            select(RestaurantReview).where(RestaurantReview.order_id == order_id)
        )
        if existing.scalar_one_or_none():
            raise ValueError("Já avaliou este pedido")
        
        review = RestaurantReview(
            restaurant_id=order.restaurant_id,
            order_id=order_id,
            user_id=user_id,
            nota_comida=data["nota_comida"],
            nota_entrega=data.get("nota_entrega"),
            nota_geral=data["nota_geral"],
            comentario=data.get("comentario")
        )
        
        db.add(review)
        
        # Atualiza rating
        restaurant = order.restaurant
        restaurant.total_avaliacoes += 1
        
        avg_result = await db.execute(
            select(func.avg(RestaurantReview.nota_geral))
            .where(RestaurantReview.restaurant_id == restaurant.id)
        )
        new_avg = avg_result.scalar() or 5.0
        restaurant.rating_medio = Decimal(str(round(new_avg, 2)))
        
        await db.commit()
        await db.refresh(review)
        return review
    
    # ============================================
    # Stats
    # ============================================
    
    async def get_restaurant_stats(self, db: AsyncSession, restaurant_id: UUID) -> dict:
        """Estatísticas do restaurante"""
        # Total pedidos
        total_result = await db.execute(
            select(func.count(FoodOrder.id))
            .where(FoodOrder.restaurant_id == restaurant_id)
        )
        total_pedidos = total_result.scalar() or 0
        
        # Pedidos pendentes
        pendentes_result = await db.execute(
            select(func.count(FoodOrder.id))
            .where(and_(
                FoodOrder.restaurant_id == restaurant_id,
                FoodOrder.status.in_([
                    FoodOrderStatus.PENDENTE.value,
                    FoodOrderStatus.ACEITE.value,
                    FoodOrderStatus.PREPARANDO.value
                ])
            ))
        )
        pedidos_pendentes = pendentes_result.scalar() or 0
        
        # Receita total
        receita_result = await db.execute(
            select(func.sum(FoodOrder.total))
            .where(and_(
                FoodOrder.restaurant_id == restaurant_id,
                FoodOrder.status == FoodOrderStatus.ENTREGUE.value
            ))
        )
        receita_total = float(receita_result.scalar() or 0)
        
        # Rating
        restaurant = await self.get_restaurant(db, restaurant_id)
        rating_medio = float(restaurant.rating_medio) if restaurant else 5.0
        
        return {
            "total_pedidos": total_pedidos,
            "pedidos_hoje": 0,  # TODO
            "pedidos_pendentes": pedidos_pendentes,
            "receita_total": receita_total,
            "receita_hoje": 0,  # TODO
            "rating_medio": rating_medio
        }


# Instância global
restaurante_service = RestauranteService()
