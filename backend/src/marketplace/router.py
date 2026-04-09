"""
TUDOaqui API - Marketplace Router
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.users.models import User, UserRole
from src.auth.dependencies import get_current_user, require_roles
from src.marketplace.models import SellerStatus, OrderStatus
from src.marketplace.schemas import (
    SellerCreate, SellerUpdate, SellerResponse,
    ProductCreate, ProductUpdate, ProductResponse, ProductDetailResponse,
    OrderCreate, OrderResponse, OrderStatusUpdate, OrderItemResponse,
    CategoryResponse, SellerStats
)
from src.marketplace.service import marketplace_service


router = APIRouter(prefix="/marketplace", tags=["Marketplace"])


# ============================================
# Sellers - Público
# ============================================

@router.get("/sellers", response_model=list[SellerResponse])
async def list_sellers(
    cidade: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Lista vendedores aprovados."""
    sellers = await marketplace_service.list_sellers(
        db, cidade=cidade, limit=limit, offset=offset
    )
    return [SellerResponse.model_validate(s) for s in sellers]


@router.get("/sellers/{seller_id}", response_model=SellerResponse)
async def get_seller(
    seller_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Obtém detalhes de um vendedor."""
    seller = await marketplace_service.get_seller(db, seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Vendedor não encontrado")
    return SellerResponse.model_validate(seller)


# ============================================
# Sellers - Gestão
# ============================================

@router.post("/sellers/register", response_model=SellerResponse, status_code=status.HTTP_201_CREATED)
async def register_seller(
    request: SellerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Registra-se como vendedor."""
    try:
        seller = await marketplace_service.register_seller(
            db, current_user.id, request.model_dump()
        )
        return SellerResponse.model_validate(seller)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sellers/me/profile", response_model=SellerResponse)
async def get_my_seller_profile(
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Obtém perfil de vendedor do usuário."""
    seller = await marketplace_service.get_seller_by_user(db, current_user.id)
    if not seller:
        raise HTTPException(status_code=404, detail="Perfil de vendedor não encontrado")
    return SellerResponse.model_validate(seller)


@router.put("/sellers/me", response_model=SellerResponse)
async def update_my_seller(
    request: SellerUpdate,
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Atualiza perfil de vendedor."""
    seller = await marketplace_service.get_seller_by_user(db, current_user.id)
    if not seller:
        raise HTTPException(status_code=404, detail="Perfil de vendedor não encontrado")
    
    try:
        seller = await marketplace_service.update_seller(
            db, seller.id, request.model_dump(exclude_unset=True)
        )
        return SellerResponse.model_validate(seller)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sellers/me/stats", response_model=SellerStats)
async def get_my_seller_stats(
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Obtém estatísticas do vendedor."""
    seller = await marketplace_service.get_seller_by_user(db, current_user.id)
    if not seller:
        raise HTTPException(status_code=404, detail="Perfil de vendedor não encontrado")
    
    stats = await marketplace_service.get_seller_stats(db, seller.id)
    return SellerStats(**stats)


# ============================================
# Products - Público
# ============================================

@router.get("/products", response_model=list[ProductResponse])
async def list_products(
    seller_id: UUID | None = None,
    category_id: UUID | None = None,
    search: str | None = None,
    destaque: bool | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Lista produtos."""
    products = await marketplace_service.list_products(
        db,
        seller_id=seller_id,
        category_id=category_id,
        search=search,
        destaque=destaque,
        limit=limit,
        offset=offset
    )
    return [
        ProductResponse(
            id=p.id,
            seller_id=p.seller_id,
            nome=p.nome,
            descricao=p.descricao,
            preco=float(p.preco),
            preco_promocional=float(p.preco_promocional) if p.preco_promocional else None,
            stock=p.stock,
            stock_minimo=p.stock_minimo,
            imagens=p.imagens.get("urls", []) if p.imagens else None,
            atributos=p.atributos,
            peso_kg=float(p.peso_kg) if p.peso_kg else None,
            destaque=p.destaque,
            category_id=p.category_id,
            status=p.status,
            visualizacoes=p.visualizacoes,
            vendas=p.vendas,
            preco_atual=float(p.preco_atual),
            em_promocao=p.em_promocao,
            created_at=p.created_at
        )
        for p in products
    ]


@router.get("/products/{product_id}", response_model=ProductDetailResponse)
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Obtém detalhes de um produto."""
    product = await marketplace_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    # Incrementa visualizações
    product.visualizacoes += 1
    await db.commit()
    
    return ProductDetailResponse(
        id=product.id,
        seller_id=product.seller_id,
        nome=product.nome,
        descricao=product.descricao,
        preco=float(product.preco),
        preco_promocional=float(product.preco_promocional) if product.preco_promocional else None,
        stock=product.stock,
        stock_minimo=product.stock_minimo,
        imagens=product.imagens.get("urls", []) if product.imagens else None,
        atributos=product.atributos,
        peso_kg=float(product.peso_kg) if product.peso_kg else None,
        destaque=product.destaque,
        category_id=product.category_id,
        status=product.status,
        visualizacoes=product.visualizacoes,
        vendas=product.vendas,
        preco_atual=float(product.preco_atual),
        em_promocao=product.em_promocao,
        created_at=product.created_at,
        seller_nome=product.seller.nome_loja,
        seller_rating=float(product.seller.rating_medio)
    )


# ============================================
# Products - Gestão Vendedor
# ============================================

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    request: ProductCreate,
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Cria novo produto."""
    seller = await marketplace_service.get_seller_by_user(db, current_user.id)
    if not seller:
        raise HTTPException(status_code=400, detail="Perfil de vendedor não encontrado")
    
    if seller.status != SellerStatus.APROVADO.value:
        raise HTTPException(status_code=400, detail="Vendedor não aprovado")
    
    try:
        product = await marketplace_service.create_product(
            db, seller.id, request.model_dump()
        )
        return ProductResponse(
            id=product.id,
            seller_id=product.seller_id,
            nome=product.nome,
            descricao=product.descricao,
            preco=float(product.preco),
            preco_promocional=float(product.preco_promocional) if product.preco_promocional else None,
            stock=product.stock,
            stock_minimo=product.stock_minimo,
            imagens=product.imagens.get("urls", []) if product.imagens else None,
            atributos=product.atributos,
            peso_kg=float(product.peso_kg) if product.peso_kg else None,
            destaque=product.destaque,
            category_id=product.category_id,
            status=product.status,
            visualizacoes=product.visualizacoes,
            vendas=product.vendas,
            preco_atual=float(product.preco_atual),
            em_promocao=product.em_promocao,
            created_at=product.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/products/my/list", response_model=list[ProductResponse])
async def list_my_products(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Lista produtos do vendedor."""
    seller = await marketplace_service.get_seller_by_user(db, current_user.id)
    if not seller:
        raise HTTPException(status_code=400, detail="Perfil de vendedor não encontrado")
    
    products = await marketplace_service.list_seller_products(db, seller.id, limit, offset)
    return [
        ProductResponse(
            id=p.id,
            seller_id=p.seller_id,
            nome=p.nome,
            descricao=p.descricao,
            preco=float(p.preco),
            preco_promocional=float(p.preco_promocional) if p.preco_promocional else None,
            stock=p.stock,
            stock_minimo=p.stock_minimo,
            imagens=p.imagens.get("urls", []) if p.imagens else None,
            atributos=p.atributos,
            peso_kg=float(p.peso_kg) if p.peso_kg else None,
            destaque=p.destaque,
            category_id=p.category_id,
            status=p.status,
            visualizacoes=p.visualizacoes,
            vendas=p.vendas,
            preco_atual=float(p.preco_atual),
            em_promocao=p.em_promocao,
            created_at=p.created_at
        )
        for p in products
    ]


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    request: ProductUpdate,
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Atualiza produto."""
    product = await marketplace_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    # Verifica permissão
    seller = await marketplace_service.get_seller_by_user(db, current_user.id)
    if not seller or (product.seller_id != seller.id and current_user.role != UserRole.ADMIN.value):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        product = await marketplace_service.update_product(
            db, product_id, request.model_dump(exclude_unset=True)
        )
        return ProductResponse(
            id=product.id,
            seller_id=product.seller_id,
            nome=product.nome,
            descricao=product.descricao,
            preco=float(product.preco),
            preco_promocional=float(product.preco_promocional) if product.preco_promocional else None,
            stock=product.stock,
            stock_minimo=product.stock_minimo,
            imagens=product.imagens.get("urls", []) if product.imagens else None,
            atributos=product.atributos,
            peso_kg=float(product.peso_kg) if product.peso_kg else None,
            destaque=product.destaque,
            category_id=product.category_id,
            status=product.status,
            visualizacoes=product.visualizacoes,
            vendas=product.vendas,
            preco_atual=float(product.preco_atual),
            em_promocao=product.em_promocao,
            created_at=product.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# Orders - Comprador
# ============================================

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    request: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cria novo pedido."""
    try:
        order = await marketplace_service.create_order(
            db, current_user.id, request.model_dump()
        )
        
        # Carrega items
        order = await marketplace_service.get_order(db, order.id)
        
        return OrderResponse(
            id=order.id,
            buyer_id=order.buyer_id,
            seller_id=order.seller_id,
            subtotal=float(order.subtotal),
            taxa_entrega=float(order.taxa_entrega),
            desconto=float(order.desconto),
            total=float(order.total),
            endereco_entrega=order.endereco_entrega,
            telefone_contato=order.telefone_contato,
            notas=order.notas,
            status=order.status,
            created_at=order.created_at,
            pago_at=order.pago_at,
            enviado_at=order.enviado_at,
            entregue_at=order.entregue_at,
            items=[OrderItemResponse.model_validate(i) for i in order.items]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/orders/my", response_model=list[OrderResponse])
async def list_my_orders(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lista pedidos do comprador."""
    orders = await marketplace_service.list_buyer_orders(
        db, current_user.id, limit, offset
    )
    return [
        OrderResponse(
            id=o.id,
            buyer_id=o.buyer_id,
            seller_id=o.seller_id,
            subtotal=float(o.subtotal),
            taxa_entrega=float(o.taxa_entrega),
            desconto=float(o.desconto),
            total=float(o.total),
            endereco_entrega=o.endereco_entrega,
            telefone_contato=o.telefone_contato,
            notas=o.notas,
            status=o.status,
            created_at=o.created_at,
            pago_at=o.pago_at,
            enviado_at=o.enviado_at,
            entregue_at=o.entregue_at,
            items=[OrderItemResponse.model_validate(i) for i in o.items]
        )
        for o in orders
    ]


# ============================================
# Orders - Vendedor
# ============================================

@router.get("/orders/seller", response_model=list[OrderResponse])
async def list_seller_orders(
    status: OrderStatus | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Lista pedidos do vendedor."""
    seller = await marketplace_service.get_seller_by_user(db, current_user.id)
    if not seller:
        raise HTTPException(status_code=400, detail="Perfil de vendedor não encontrado")
    
    orders = await marketplace_service.list_seller_orders(
        db, seller.id, status, limit, offset
    )
    return [
        OrderResponse(
            id=o.id,
            buyer_id=o.buyer_id,
            seller_id=o.seller_id,
            subtotal=float(o.subtotal),
            taxa_entrega=float(o.taxa_entrega),
            desconto=float(o.desconto),
            total=float(o.total),
            endereco_entrega=o.endereco_entrega,
            telefone_contato=o.telefone_contato,
            notas=o.notas,
            status=o.status,
            created_at=o.created_at,
            pago_at=o.pago_at,
            enviado_at=o.enviado_at,
            entregue_at=o.entregue_at,
            items=[OrderItemResponse.model_validate(i) for i in o.items]
        )
        for o in orders
    ]


@router.put("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: UUID,
    request: OrderStatusUpdate,
    current_user: User = Depends(require_roles(UserRole.PROPRIETARIO, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Atualiza status do pedido."""
    order = await marketplace_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    # Verifica permissão
    seller = await marketplace_service.get_seller_by_user(db, current_user.id)
    if not seller or (order.seller_id != seller.id and current_user.role != UserRole.ADMIN.value):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        order = await marketplace_service.update_order_status(db, order_id, request.status)
        return OrderResponse(
            id=order.id,
            buyer_id=order.buyer_id,
            seller_id=order.seller_id,
            subtotal=float(order.subtotal),
            taxa_entrega=float(order.taxa_entrega),
            desconto=float(order.desconto),
            total=float(order.total),
            endereco_entrega=order.endereco_entrega,
            telefone_contato=order.telefone_contato,
            notas=order.notas,
            status=order.status,
            created_at=order.created_at,
            pago_at=order.pago_at,
            enviado_at=order.enviado_at,
            entregue_at=order.entregue_at,
            items=[OrderItemResponse.model_validate(i) for i in order.items]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# Categories
# ============================================

@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db)
):
    """Lista categorias de produtos."""
    categories = await marketplace_service.list_categories(db)
    return [CategoryResponse.model_validate(c) for c in categories]
