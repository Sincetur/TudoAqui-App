"""
TUDOaqui API - Marketplace Service
"""
from typing import List, Optional
from datetime import datetime, timezone
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.config import settings
from src.marketplace.models import (
    Seller, SellerStatus,
    Product, ProductStatus, ProductCategory,
    MarketplaceOrder, OrderStatus, OrderItem,
    ProductReview
)
from src.users.models import User, UserRole


class MarketplaceService:
    """Serviço do Marketplace"""
    
    # ============================================
    # Seller Management
    # ============================================
    
    async def register_seller(
        self,
        db: AsyncSession,
        user_id: UUID,
        data: dict
    ) -> Seller:
        """Registra novo vendedor"""
        # Verifica se já é vendedor
        result = await db.execute(
            select(Seller).where(Seller.user_id == user_id)
        )
        if result.scalar_one_or_none():
            raise ValueError("Utilizador já é vendedor registado")
        
        # Atualiza role do usuário
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if user:
            user.role = UserRole.PROPRIETARIO.value
        
        seller = Seller(
            user_id=user_id,
            nome_loja=data["nome_loja"],
            descricao=data.get("descricao"),
            logo_url=data.get("logo_url"),
            endereco=data.get("endereco"),
            cidade=data.get("cidade"),
            provincia=data.get("provincia"),
            taxa_entrega_base=Decimal(str(data.get("taxa_entrega_base", 0))),
            tempo_preparacao_min=data.get("tempo_preparacao_min", 30),
            status=SellerStatus.PENDENTE.value
        )
        
        db.add(seller)
        await db.commit()
        await db.refresh(seller)
        
        return seller
    
    async def get_seller(self, db: AsyncSession, seller_id: UUID) -> Optional[Seller]:
        """Obtém vendedor por ID"""
        result = await db.execute(
            select(Seller)
            .where(Seller.id == seller_id)
            .options(joinedload(Seller.user))
        )
        return result.scalar_one_or_none()
    
    async def get_seller_by_user(self, db: AsyncSession, user_id: UUID) -> Optional[Seller]:
        """Obtém vendedor pelo user_id"""
        result = await db.execute(
            select(Seller).where(Seller.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def update_seller(
        self,
        db: AsyncSession,
        seller_id: UUID,
        data: dict
    ) -> Seller:
        """Atualiza dados do vendedor"""
        seller = await self.get_seller(db, seller_id)
        if not seller:
            raise ValueError("Vendedor não encontrado")
        
        for field, value in data.items():
            if value is not None:
                if field in ["taxa_entrega_base"]:
                    value = Decimal(str(value))
                setattr(seller, field, value)
        
        await db.commit()
        await db.refresh(seller)
        return seller
    
    async def approve_seller(self, db: AsyncSession, seller_id: UUID) -> Seller:
        """Aprova vendedor (admin)"""
        seller = await self.get_seller(db, seller_id)
        if not seller:
            raise ValueError("Vendedor não encontrado")
        
        seller.status = SellerStatus.APROVADO.value
        await db.commit()
        await db.refresh(seller)
        return seller
    
    async def list_sellers(
        self,
        db: AsyncSession,
        status: Optional[SellerStatus] = None,
        cidade: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Seller]:
        """Lista vendedores"""
        query = select(Seller)
        
        filters = []
        if status:
            filters.append(Seller.status == status.value)
        else:
            filters.append(Seller.status == SellerStatus.APROVADO.value)
        
        if cidade:
            filters.append(Seller.cidade == cidade)
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.order_by(Seller.rating_medio.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    # ============================================
    # Product Management
    # ============================================
    
    async def create_product(
        self,
        db: AsyncSession,
        seller_id: UUID,
        data: dict
    ) -> Product:
        """Cria novo produto"""
        product = Product(
            seller_id=seller_id,
            nome=data["nome"],
            descricao=data.get("descricao"),
            preco=Decimal(str(data["preco"])),
            preco_promocional=Decimal(str(data["preco_promocional"])) if data.get("preco_promocional") else None,
            stock=data.get("stock", 0),
            stock_minimo=data.get("stock_minimo", 5),
            imagens={"urls": data.get("imagens", [])},
            atributos=data.get("atributos"),
            peso_kg=Decimal(str(data["peso_kg"])) if data.get("peso_kg") else None,
            destaque=data.get("destaque", False),
            category_id=data.get("category_id"),
            status=ProductStatus.ATIVO.value
        )
        
        db.add(product)
        await db.commit()
        await db.refresh(product)
        
        return product
    
    async def get_product(self, db: AsyncSession, product_id: UUID) -> Optional[Product]:
        """Obtém produto por ID"""
        result = await db.execute(
            select(Product)
            .where(Product.id == product_id)
            .options(joinedload(Product.seller))
        )
        return result.scalar_one_or_none()
    
    async def update_product(
        self,
        db: AsyncSession,
        product_id: UUID,
        data: dict
    ) -> Product:
        """Atualiza produto"""
        product = await self.get_product(db, product_id)
        if not product:
            raise ValueError("Produto não encontrado")
        
        for field, value in data.items():
            if value is not None:
                if field in ["preco", "preco_promocional", "peso_kg"]:
                    value = Decimal(str(value)) if value else None
                if field == "imagens":
                    value = {"urls": value}
                setattr(product, field, value)
        
        await db.commit()
        await db.refresh(product)
        return product
    
    async def list_products(
        self,
        db: AsyncSession,
        seller_id: Optional[UUID] = None,
        category_id: Optional[UUID] = None,
        search: Optional[str] = None,
        destaque: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Product]:
        """Lista produtos"""
        query = select(Product).options(joinedload(Product.seller))
        
        filters = [Product.status == ProductStatus.ATIVO.value]
        
        if seller_id:
            filters.append(Product.seller_id == seller_id)
        
        if category_id:
            filters.append(Product.category_id == category_id)
        
        if search:
            filters.append(Product.nome.ilike(f"%{search}%"))
        
        if destaque is not None:
            filters.append(Product.destaque == destaque)
        
        query = query.where(and_(*filters))
        query = query.order_by(Product.created_at.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.unique().scalars().all()
    
    async def list_seller_products(
        self,
        db: AsyncSession,
        seller_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[Product]:
        """Lista produtos do vendedor"""
        result = await db.execute(
            select(Product)
            .where(Product.seller_id == seller_id)
            .order_by(Product.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    # ============================================
    # Orders
    # ============================================
    
    async def create_order(
        self,
        db: AsyncSession,
        buyer_id: UUID,
        data: dict
    ) -> MarketplaceOrder:
        """Cria novo pedido"""
        seller_id = data["seller_id"]
        
        # Verifica vendedor
        seller = await self.get_seller(db, seller_id)
        if not seller or seller.status != SellerStatus.APROVADO.value:
            raise ValueError("Vendedor não disponível")
        
        # Processa itens
        items_data = data["items"]
        order_items = []
        subtotal = Decimal("0")
        
        for item_data in items_data:
            product = await self.get_product(db, item_data["product_id"])
            
            if not product or product.seller_id != seller_id:
                raise ValueError(f"Produto {item_data['product_id']} não encontrado nesta loja")
            
            if product.status != ProductStatus.ATIVO.value:
                raise ValueError(f"Produto {product.nome} não disponível")
            
            if product.stock < item_data["quantidade"]:
                raise ValueError(f"Produto {product.nome}: stock insuficiente")
            
            preco = product.preco_atual
            item_subtotal = preco * item_data["quantidade"]
            subtotal += item_subtotal
            
            # Reduz stock
            product.stock -= item_data["quantidade"]
            product.vendas += item_data["quantidade"]
            
            order_items.append({
                "product_id": product.id,
                "quantidade": item_data["quantidade"],
                "preco_unitario": preco,
                "subtotal": item_subtotal,
                "produto_nome": product.nome,
                "produto_imagem": product.imagens.get("urls", [None])[0] if product.imagens else None
            })
        
        # Calcula total
        taxa_entrega = seller.taxa_entrega_base
        total = subtotal + taxa_entrega
        
        # Cria pedido
        order = MarketplaceOrder(
            buyer_id=buyer_id,
            seller_id=seller_id,
            subtotal=subtotal,
            taxa_entrega=taxa_entrega,
            desconto=Decimal("0"),
            total=total,
            endereco_entrega=data["endereco_entrega"],
            latitude_entrega=Decimal(str(data["latitude_entrega"])) if data.get("latitude_entrega") else None,
            longitude_entrega=Decimal(str(data["longitude_entrega"])) if data.get("longitude_entrega") else None,
            telefone_contato=data["telefone_contato"],
            notas=data.get("notas"),
            status=OrderStatus.PENDENTE.value
        )
        
        db.add(order)
        await db.flush()
        
        # Cria itens
        for item_data in order_items:
            item = OrderItem(
                order_id=order.id,
                **item_data
            )
            db.add(item)
        
        # Atualiza stats do vendedor
        seller.total_vendas += 1
        
        await db.commit()
        await db.refresh(order)
        
        return order
    
    async def get_order(self, db: AsyncSession, order_id: UUID) -> Optional[MarketplaceOrder]:
        """Obtém pedido por ID"""
        result = await db.execute(
            select(MarketplaceOrder)
            .where(MarketplaceOrder.id == order_id)
            .options(joinedload(MarketplaceOrder.items))
        )
        return result.scalar_one_or_none()
    
    async def update_order_status(
        self,
        db: AsyncSession,
        order_id: UUID,
        status: OrderStatus
    ) -> MarketplaceOrder:
        """Atualiza status do pedido"""
        order = await self.get_order(db, order_id)
        if not order:
            raise ValueError("Pedido não encontrado")
        
        order.status = status.value
        
        # Atualiza timestamps
        now = datetime.now(timezone.utc)
        if status == OrderStatus.PAGO:
            order.pago_at = now
        elif status == OrderStatus.ENVIADO:
            order.enviado_at = now
        elif status == OrderStatus.ENTREGUE:
            order.entregue_at = now
        elif status == OrderStatus.CANCELADO:
            order.cancelado_at = now
            # Restaura stock
            for item in order.items:
                product_result = await db.execute(
                    select(Product).where(Product.id == item.product_id)
                )
                product = product_result.scalar_one_or_none()
                if product:
                    product.stock += item.quantidade
                    product.vendas -= item.quantidade
        
        await db.commit()
        await db.refresh(order)
        return order
    
    async def list_buyer_orders(
        self,
        db: AsyncSession,
        buyer_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> List[MarketplaceOrder]:
        """Lista pedidos do comprador"""
        result = await db.execute(
            select(MarketplaceOrder)
            .where(MarketplaceOrder.buyer_id == buyer_id)
            .options(joinedload(MarketplaceOrder.items))
            .order_by(MarketplaceOrder.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.unique().scalars().all()
    
    async def list_seller_orders(
        self,
        db: AsyncSession,
        seller_id: UUID,
        status: Optional[OrderStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[MarketplaceOrder]:
        """Lista pedidos do vendedor"""
        query = select(MarketplaceOrder).where(MarketplaceOrder.seller_id == seller_id)
        
        if status:
            query = query.where(MarketplaceOrder.status == status.value)
        
        query = query.options(joinedload(MarketplaceOrder.items))
        query = query.order_by(MarketplaceOrder.created_at.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.unique().scalars().all()
    
    # ============================================
    # Categories
    # ============================================
    
    async def list_categories(self, db: AsyncSession) -> List[ProductCategory]:
        """Lista categorias"""
        result = await db.execute(
            select(ProductCategory)
            .where(ProductCategory.ativo.is_(True))
            .order_by(ProductCategory.ordem)
        )
        return result.scalars().all()
    
    # ============================================
    # Stats
    # ============================================
    
    async def get_seller_stats(self, db: AsyncSession, seller_id: UUID) -> dict:
        """Estatísticas do vendedor"""
        # Total produtos
        produtos_result = await db.execute(
            select(func.count(Product.id))
            .where(Product.seller_id == seller_id)
        )
        total_produtos = produtos_result.scalar() or 0
        
        # Total pedidos
        pedidos_result = await db.execute(
            select(func.count(MarketplaceOrder.id))
            .where(MarketplaceOrder.seller_id == seller_id)
        )
        total_pedidos = pedidos_result.scalar() or 0
        
        # Pedidos pendentes
        pendentes_result = await db.execute(
            select(func.count(MarketplaceOrder.id))
            .where(and_(
                MarketplaceOrder.seller_id == seller_id,
                MarketplaceOrder.status.in_([
                    OrderStatus.PENDENTE.value,
                    OrderStatus.PAGO.value,
                    OrderStatus.PROCESSANDO.value
                ])
            ))
        )
        pedidos_pendentes = pendentes_result.scalar() or 0
        
        # Receita total
        receita_result = await db.execute(
            select(func.sum(MarketplaceOrder.total))
            .where(and_(
                MarketplaceOrder.seller_id == seller_id,
                MarketplaceOrder.status == OrderStatus.ENTREGUE.value
            ))
        )
        receita_total = float(receita_result.scalar() or 0)
        
        return {
            "total_produtos": total_produtos,
            "total_pedidos": total_pedidos,
            "pedidos_pendentes": pedidos_pendentes,
            "receita_total": receita_total,
            "receita_mes": 0  # TODO: calcular receita do mês
        }


# Instância global
marketplace_service = MarketplaceService()
