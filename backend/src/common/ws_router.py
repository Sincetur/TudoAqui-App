"""
TUDOaqui API - WebSocket Router
Endpoints WebSocket para comunicação em tempo real
"""
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.auth.service import auth_service
from src.common.websocket import ws_manager, WSMessage


router = APIRouter(prefix="/ws", tags=["WebSocket"])


async def get_user_from_token(token: str, db: AsyncSession) -> dict | None:
    """Valida token e retorna dados do utilizador"""
    payload = auth_service.decode_token(token)
    if not payload:
        return None
    
    return {
        "user_id": UUID(payload.get("sub")),
        "role": payload.get("role")
    }


@router.websocket("/client/{token}")
async def websocket_client(
    websocket: WebSocket,
    token: str
):
    """
    WebSocket para clientes.
    
    Recebe:
    - Atualizações de status da corrida
    - Localização do motorista
    - Notificações
    
    Envia:
    - Ping/pong para manter conexão
    """
    # Valida token
    payload = auth_service.decode_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Token inválido")
        return
    
    user_id = UUID(payload.get("sub"))
    
    # Conecta
    await ws_manager.connect(websocket, user_id, "client")
    
    try:
        while True:
            # Recebe mensagens do cliente
            data = await websocket.receive_json()
            
            msg_type = data.get("type")
            
            if msg_type == "ping":
                await ws_manager.send_personal(user_id, {"type": "pong"})
            
            elif msg_type == "join_ride":
                ride_id = UUID(data.get("ride_id"))
                ws_manager.join_ride(user_id, ride_id)
                await ws_manager.send_personal(user_id, {
                    "type": "joined_ride",
                    "ride_id": str(ride_id)
                })
            
            elif msg_type == "leave_ride":
                ride_id = UUID(data.get("ride_id"))
                ws_manager.leave_ride(user_id, ride_id)
    
    except WebSocketDisconnect:
        ws_manager.disconnect(user_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        ws_manager.disconnect(user_id)


@router.websocket("/driver/{token}")
async def websocket_driver(
    websocket: WebSocket,
    token: str
):
    """
    WebSocket para motoristas.
    
    Recebe:
    - Novas corridas próximas
    - Atualizações de corrida aceite
    - Notificações
    
    Envia:
    - Localização atual
    - Status online/offline
    """
    # Valida token
    payload = auth_service.decode_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Token inválido")
        return
    
    user_id = UUID(payload.get("sub"))
    role = payload.get("role")
    
    if role != "motorista":
        await websocket.close(code=4003, reason="Não é motorista")
        return
    
    # Conecta
    await ws_manager.connect(websocket, user_id, "driver")
    
    try:
        while True:
            # Recebe mensagens do motorista
            data = await websocket.receive_json()
            
            msg_type = data.get("type")
            
            if msg_type == "ping":
                await ws_manager.send_personal(user_id, {"type": "pong"})
            
            elif msg_type == "location_update":
                # Atualiza localização e broadcast para corrida ativa
                lat = data.get("latitude")
                lon = data.get("longitude")
                bearing = data.get("bearing")
                ride_id = data.get("ride_id")
                
                if ride_id:
                    await ws_manager.broadcast_to_ride(
                        UUID(ride_id),
                        WSMessage.driver_location(UUID(ride_id), lat, lon, bearing),
                        exclude=user_id
                    )
            
            elif msg_type == "join_ride":
                ride_id = UUID(data.get("ride_id"))
                ws_manager.join_ride(user_id, ride_id)
            
            elif msg_type == "leave_ride":
                ride_id = UUID(data.get("ride_id"))
                ws_manager.leave_ride(user_id, ride_id)
    
    except WebSocketDisconnect:
        ws_manager.disconnect(user_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        ws_manager.disconnect(user_id)


@router.get("/status")
async def websocket_status():
    """Retorna status das conexões WebSocket"""
    return {
        "total_connections": len(ws_manager.active_connections),
        "online_drivers": ws_manager.get_online_drivers_count(),
        "active_rides": len(ws_manager.ride_groups)
    }
