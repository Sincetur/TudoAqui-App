"""
TUDOaqui API - Tuendi Restaurante Router
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.users.models import User, UserRole
from src.auth.dependencies import get_current_user, require_roles
from src.tuendi.restaurante.models import FoodOrderStatus
from src.tuendi.restaurante.schemas import (
    RestaurantCreate, RestaurantUpdate, RestaurantResponse, RestaurantListResponse,
    MenuCategoryCreate, MenuCategoryResponse,
    MenuItemCreate, MenuItemUpdate, MenuItemResponse,
    FoodOrderCreate, FoodOrderResponse, FoodOrderDetailResponse, FoodOrderListResponse,
    OrderItemResponse, ReviewCreate, ReviewResponse, RestaurantStats
)
from src.tuendi.restaurante.service import restaurante_service


router = APIRouter(prefix="/restaurantes", tags=["Tuendi Restaurante"])


# ============================================
# Restaurants - Público
# ============================================

@router.get("", response_model=List[RestaurantListResponse])
async def list_restaurants(
    cidade: Optional[str] = None,
    categoria: Optional[str] = None,
    latitude: Optional[float] = Query(None, ge=-90, le=90),
    longitude: Optional[float] = Query(None, ge=-180, le=180),
    raio_km: float = Query(10, ge=1, le=50),
    aberto_agora: bool = False,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Lista restaurantes."""
    results = await restaurante_service.list_restaurants(
        db, cidade=cidade, categoria=categoria,
        user_lat=latitude, user_lon=longitude, raio_km=raio_km,
        aberto_agora=aberto_agora, limit=limit, offset=offset
    )
    return [
        RestaurantListResponse(
            id=r.id,
            nome=r.nome,
            logo_url=r.logo_url,
            categorias=r.categorias.get("items", []) if r.categorias else None,
            rating_medio=float(r.rating_medio),
            tempo_preparo_min=r.tempo_preparo_min,
            taxa_entrega=float(r.taxa_entrega),
            aberto=r.aberto,
            distancia_km=round(d, 2) if d else None
        )
        for r, d in results
    ]


@router.get("/{restaurant_id}", response_model=RestaurantResponse)
async def get_restaurant(
    restaurant_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Obtém detalhes de um restaurante."""
    restaurant = await restaurante_service.get_restaurant(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante não encontrado")
    
    return _restaurant_to_response(restaurant)


@router.get("/{restaurant_id}/menu", response_model=List[MenuCategoryResponse])
async def get_menu(
    restaurant_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Obtém menu do restaurante."""
    categories = await restaurante_service.get_menu(db, restaurant_id)
    return [
        MenuCategoryResponse(
            id=c.id,
            restaurant_id=c.restaurant_id,
            nome=c.nome,
            descricao=c.descricao,
            ordem=c.ordem,
            ativo=c.ativo,
            items=[
                MenuItemResponse(
                    id=i.id,
                    category_id=i.category_id,
                    restaurant_id=i.restaurant_id,
                    nome=i.nome,
                    descricao=i.descricao,
                    imagem_url=i.imagem_url,
                    preco=float(i.preco),
                    preco_promocional=float(i.preco_promocional) if i.preco_promocional else None,
                    tempo_preparo_min=i.tempo_preparo_min,
                    opcoes=i.opcoes.get("opcoes", []) if i.opcoes else None,
                    info_nutricional=i.info_nutricional,
                    popular=i.popular,
                    status=i.status,
                    preco_atual=float(i.preco_atual)
                )
                for i in c.items if i.status == "ativo"
            ]
        )
        for c in categories
    ]


# ============================================
# Restaurants - Gestão (Dono)
# ============================================

@router.post("", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED)
async def create_restaurant(
    request: RestaurantCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cria novo restaurante."""
    restaurant = await restaurante_service.create_restaurant(db, current_user.id, request.model_dump())
    return _restaurant_to_response(restaurant)


@router.get("/my/restaurant", response_model=RestaurantResponse)
async def get_my_restaurant(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtém meu restaurante."""
    restaurant = await restaurante_service.get_restaurant_by_owner(db, current_user.id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante não encontrado")
    return _restaurant_to_response(restaurant)


@router.put("/my/restaurant", response_model=RestaurantResponse)
async def update_my_restaurant(
    request: RestaurantUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Atualiza meu restaurante."""
    restaurant = await restaurante_service.get_restaurant_by_owner(db, current_user.id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante não encontrado")
    
    try:
        restaurant = await restaurante_service.update_restaurant(
            db, restaurant.id, request.model_dump(exclude_unset=True)
        )
        return _restaurant_to_response(restaurant)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my/stats", response_model=RestaurantStats)
async def get_my_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Estatísticas do restaurante."""
    restaurant = await restaurante_service.get_restaurant_by_owner(db, current_user.id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante não encontrado")
    
    stats = await restaurante_service.get_restaurant_stats(db, restaurant.id)
    return RestaurantStats(**stats)


# ============================================
# Menu Management
# ============================================

@router.post("/my/menu/categories", response_model=MenuCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    request: MenuCategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cria categoria do menu."""
    restaurant = await restaurante_service.get_restaurant_by_owner(db, current_user.id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante não encontrado")
    
    category = await restaurante_service.create_category(db, restaurant.id, request.model_dump())
    return MenuCategoryResponse(
        id=category.id,
        restaurant_id=category.restaurant_id,
        nome=category.nome,
        descricao=category.descricao,
        ordem=category.ordem,
        ativo=category.ativo,
        items=[]
    )


@router.post("/my/menu/items", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
async def create_menu_item(
    request: MenuItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cria item do menu."""
    restaurant = await restaurante_service.get_restaurant_by_owner(db, current_user.id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante não encontrado")
    
    item = await restaurante_service.create_menu_item(db, restaurant.id, request.model_dump())
    return MenuItemResponse(
        id=item.id,
        category_id=item.category_id,
        restaurant_id=item.restaurant_id,
        nome=item.nome,
        descricao=item.descricao,
        imagem_url=item.imagem_url,
        preco=float(item.preco),
        preco_promocional=float(item.preco_promocional) if item.preco_promocional else None,
        tempo_preparo_min=item.tempo_preparo_min,
        opcoes=item.opcoes.get("opcoes", []) if item.opcoes else None,
        info_nutricional=item.info_nutricional,
        popular=item.popular,
        status=item.status,
        preco_atual=float(item.preco_atual)
    )


@router.put("/my/menu/items/{item_id}", response_model=MenuItemResponse)
async def update_menu_item(
    item_id: UUID,
    request: MenuItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Atualiza item do menu."""
    restaurant = await restaurante_service.get_restaurant_by_owner(db, current_user.id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante não encontrado")
    
    try:
        item = await restaurante_service.update_menu_item(db, item_id, request.model_dump(exclude_unset=True))
        return MenuItemResponse(
            id=item.id,
            category_id=item.category_id,
            restaurant_id=item.restaurant_id,
            nome=item.nome,
            descricao=item.descricao,
            imagem_url=item.imagem_url,
            preco=float(item.preco),
            preco_promocional=float(item.preco_promocional) if item.preco_promocional else None,
            tempo_preparo_min=item.tempo_preparo_min,
            opcoes=item.opcoes.get("opcoes", []) if item.opcoes else None,
            info_nutricional=item.info_nutricional,
            popular=item.popular,
            status=item.status,
            preco_atual=float(item.preco_atual)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# Orders - Cliente
# ============================================

@router.post("/orders", response_model=FoodOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    request: FoodOrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cria pedido."""
    try:
        order = await restaurante_service.create_order(db, current_user.id, request.model_dump())
        order = await restaurante_service.get_order(db, order.id)
        return _order_to_response(order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/orders/my", response_model=List[FoodOrderListResponse])
async def list_my_orders(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lista meus pedidos."""
    orders = await restaurante_service.list_customer_orders(db, current_user.id, limit, offset)
    return [
        FoodOrderListResponse(
            id=o.id,
            restaurant_id=o.restaurant_id,
            restaurant_nome=o.restaurant.nome,
            total=float(o.total),
            status=o.status,
            created_at=o.created_at
        )
        for o in orders
    ]


@router.get("/orders/{order_id}", response_model=FoodOrderDetailResponse)
async def get_order(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtém detalhes do pedido."""
    order = await restaurante_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    # Verifica permissão
    restaurant = await restaurante_service.get_restaurant_by_owner(db, current_user.id)
    if order.customer_id != current_user.id and (not restaurant or order.restaurant_id != restaurant.id):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    return _order_to_detail_response(order)


@router.post("/orders/{order_id}/review", response_model=ReviewResponse)
async def create_review(
    order_id: UUID,
    request: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Avalia pedido."""
    try:
        review = await restaurante_service.create_review(db, order_id, current_user.id, request.model_dump())
        return ReviewResponse(
            id=review.id,
            restaurant_id=review.restaurant_id,
            user_id=review.user_id,
            nota_comida=review.nota_comida,
            nota_entrega=review.nota_entrega,
            nota_geral=review.nota_geral,
            comentario=review.comentario,
            created_at=review.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# Orders - Restaurante
# ============================================

@router.get("/my/orders", response_model=List[FoodOrderResponse])
async def list_restaurant_orders(
    status: Optional[FoodOrderStatus] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lista pedidos do restaurante."""
    restaurant = await restaurante_service.get_restaurant_by_owner(db, current_user.id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurante não encontrado")
    
    orders = await restaurante_service.list_restaurant_orders(db, restaurant.id, status, limit, offset)
    return [_order_to_response(o) for o in orders]


@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: UUID,
    status: FoodOrderStatus,
    motivo: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Atualiza status do pedido."""
    order = await restaurante_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    restaurant = await restaurante_service.get_restaurant_by_owner(db, current_user.id)
    if not restaurant or order.restaurant_id != restaurant.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    try:
        order = await restaurante_service.update_order_status(db, order_id, status, motivo)
        return _order_to_response(order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# Helpers
# ============================================

def _restaurant_to_response(r) -> RestaurantResponse:
    return RestaurantResponse(
        id=r.id,
        owner_id=r.owner_id,
        nome=r.nome,
        descricao=r.descricao,
        logo_url=r.logo_url,
        banner_url=r.banner_url,
        endereco=r.endereco,
        cidade=r.cidade,
        latitude=float(r.latitude),
        longitude=float(r.longitude),
        hora_abertura=r.hora_abertura,
        hora_fecho=r.hora_fecho,
        dias_funcionamento=r.dias_funcionamento.get("dias", []) if r.dias_funcionamento else None,
        raio_entrega_km=r.raio_entrega_km,
        tempo_preparo_min=r.tempo_preparo_min,
        pedido_minimo=float(r.pedido_minimo),
        taxa_entrega=float(r.taxa_entrega),
        categorias=r.categorias.get("items", []) if r.categorias else None,
        telefone=r.telefone,
        rating_medio=float(r.rating_medio),
        total_pedidos=r.total_pedidos,
        total_avaliacoes=r.total_avaliacoes,
        aberto=r.aberto,
        status=r.status,
        created_at=r.created_at
    )


def _order_to_response(o) -> FoodOrderResponse:
    return FoodOrderResponse(
        id=o.id,
        customer_id=o.customer_id,
        restaurant_id=o.restaurant_id,
        driver_id=o.driver_id,
        endereco_entrega=o.endereco_entrega,
        latitude_entrega=float(o.latitude_entrega),
        longitude_entrega=float(o.longitude_entrega),
        referencia_entrega=o.referencia_entrega,
        subtotal=float(o.subtotal),
        taxa_entrega=float(o.taxa_entrega),
        desconto=float(o.desconto),
        total=float(o.total),
        telefone_contato=o.telefone_contato,
        notas=o.notas,
        tempo_preparo_estimado=o.tempo_preparo_estimado,
        tempo_entrega_estimado=o.tempo_entrega_estimado,
        codigo_entrega=o.codigo_entrega,
        status=o.status,
        created_at=o.created_at,
        aceite_at=o.aceite_at,
        pronto_at=o.pronto_at,
        recolhido_at=o.recolhido_at,
        entregue_at=o.entregue_at,
        items=[
            OrderItemResponse(
                id=i.id,
                menu_item_id=i.menu_item_id,
                quantidade=i.quantidade,
                preco_unitario=float(i.preco_unitario),
                subtotal=float(i.subtotal),
                opcoes_selecionadas=i.opcoes_selecionadas.get("opcoes", []) if i.opcoes_selecionadas else None,
                notas=i.notas,
                item_nome=i.item_nome
            )
            for i in o.items
        ]
    )


def _order_to_detail_response(o) -> FoodOrderDetailResponse:
    base = _order_to_response(o)
    return FoodOrderDetailResponse(
        **base.model_dump(),
        restaurant_nome=o.restaurant.nome,
        restaurant_telefone=o.restaurant.telefone,
        driver_nome=o.driver.user.nome if o.driver and o.driver.user else None,
        driver_telefone=o.driver.user.telefone if o.driver and o.driver.user else None
    )
