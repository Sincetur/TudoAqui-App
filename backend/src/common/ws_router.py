"""
TUDOaqui API - WebSocket Router
Endpoints WebSocket para comunicação em tempo real
"""
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import async_session as async_session_factory
from src.auth.service import auth_service
from src.common.websocket import ws_manager, WSMessage
from src.tuendi.rides.service import ride_service
from src.tuendi.drivers.service import driver_service


router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/client/{token}")
async def websocket_client(
    websocket: WebSocket,
    token: str
):
    """WebSocket para clientes - recebe tracking e status da corrida"""
    payload = auth_service.decode_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Token invalido")
        return

    user_id = UUID(payload.get("sub"))
    await ws_manager.connect(websocket, user_id, "client")

    try:
        while True:
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
        print(f"WS client error: {e}")
        ws_manager.disconnect(user_id)


@router.websocket("/driver/{token}")
async def websocket_driver(
    websocket: WebSocket,
    token: str
):
    """WebSocket para motoristas - envia localização, recebe corridas"""
    payload = auth_service.decode_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Token invalido")
        return

    user_id = UUID(payload.get("sub"))
    role = payload.get("role")

    if role not in ("motorista", "motoqueiro", "admin"):
        await websocket.close(code=4003, reason="Role nao autorizado")
        return

    await ws_manager.connect(websocket, user_id, "driver")

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "ping":
                await ws_manager.send_personal(user_id, {"type": "pong"})

            elif msg_type == "location_update":
                lat = data.get("latitude")
                lon = data.get("longitude")
                bearing = data.get("bearing")
                speed = data.get("speed")
                ride_id = data.get("ride_id")

                # Persist driver location to DB
                try:
                    async with async_session_factory() as db:
                        driver = await driver_service.get_driver_by_user(db, user_id)
                        if driver:
                            await driver_service.update_location(db, driver.id, lat, lon)

                            # If active ride, persist tracking point
                            if ride_id:
                                await ride_service.add_tracking_point(
                                    db, UUID(ride_id), lat, lon, speed, bearing
                                )
                except Exception as e:
                    print(f"WS location persist error: {e}")

                # Broadcast to ride group
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
        print(f"WS driver error: {e}")
        ws_manager.disconnect(user_id)


@router.get("/status")
async def websocket_status():
    """Retorna status das conexoes WebSocket"""
    return {
        "total_connections": len(ws_manager.active_connections),
        "online_drivers": ws_manager.get_online_drivers_count(),
        "active_rides": len(ws_manager.ride_groups)
    }
