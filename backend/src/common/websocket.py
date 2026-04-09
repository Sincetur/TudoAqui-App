"""
TUDOaqui API - WebSocket Manager
Gestão de conexões WebSocket para tempo real
"""
import json
from uuid import UUID
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ConnectionInfo:
    """Informações de uma conexão WebSocket"""
    websocket: WebSocket
    user_id: UUID
    user_type: str  # 'client' | 'driver'
    connected_at: datetime = field(default_factory=datetime.now)
    ride_id: UUID | None = None


class WebSocketManager:
    """
    Gestor de conexões WebSocket para comunicação em tempo real.
    
    Funcionalidades:
    - Tracking de localização do motorista
    - Atualizações de status da corrida
    - Notificações push em tempo real
    """
    
    def __init__(self):
        # Conexões ativas por user_id
        self.active_connections: Dict[str, ConnectionInfo] = {}
        
        # Grupos de corridas (ride_id -> set of user_ids)
        self.ride_groups: Dict[str, Set[str]] = {}
        
        # Motoristas online (driver_id -> user_id)
        self.online_drivers: Dict[str, str] = {}
    
    async def connect(
        self, 
        websocket: WebSocket, 
        user_id: UUID, 
        user_type: str
    ):
        """Aceita nova conexão WebSocket"""
        await websocket.accept()
        
        user_key = str(user_id)
        
        # Remove conexão antiga se existir
        if user_key in self.active_connections:
            try:
                old_ws = self.active_connections[user_key].websocket
                await old_ws.close()
            except Exception:
                pass
        
        # Registra nova conexão
        self.active_connections[user_key] = ConnectionInfo(
            websocket=websocket,
            user_id=user_id,
            user_type=user_type
        )
        
        # Se for motorista, adiciona aos online
        if user_type == 'driver':
            self.online_drivers[user_key] = user_key
        
        await self.send_personal(user_id, {
            "type": "connected",
            "message": "Conexão estabelecida"
        })
    
    def disconnect(self, user_id: UUID):
        """Remove conexão WebSocket"""
        user_key = str(user_id)
        
        if user_key in self.active_connections:
            conn = self.active_connections[user_key]
            
            # Remove de grupos de corrida
            if conn.ride_id:
                ride_key = str(conn.ride_id)
                if ride_key in self.ride_groups:
                    self.ride_groups[ride_key].discard(user_key)
            
            # Remove dos motoristas online
            if conn.user_type == 'driver':
                self.online_drivers.pop(user_key, None)
            
            del self.active_connections[user_key]
    
    async def send_personal(self, user_id: UUID, data: dict):
        """Envia mensagem para um utilizador específico"""
        user_key = str(user_id)
        
        if user_key in self.active_connections:
            try:
                ws = self.active_connections[user_key].websocket
                await ws.send_json(data)
            except Exception:
                self.disconnect(user_id)
    
    async def broadcast_to_ride(self, ride_id: UUID, data: dict, exclude: UUID = None):
        """Envia mensagem para todos os participantes de uma corrida"""
        ride_key = str(ride_id)
        
        if ride_key not in self.ride_groups:
            return
        
        exclude_key = str(exclude) if exclude else None
        
        for user_key in self.ride_groups[ride_key]:
            if user_key != exclude_key and user_key in self.active_connections:
                try:
                    ws = self.active_connections[user_key].websocket
                    await ws.send_json(data)
                except Exception:
                    pass
    
    async def broadcast_to_drivers(self, data: dict, lat: float = None, lon: float = None, radius_km: float = 5):
        """Envia mensagem para motoristas (opcionalmente filtrados por localização)"""
        # TODO: Implementar filtro por localização quando necessário
        for driver_key in self.online_drivers:
            if driver_key in self.active_connections:
                conn = self.active_connections[driver_key]
                if conn.user_type == 'driver':
                    try:
                        await conn.websocket.send_json(data)
                    except Exception:
                        pass
    
    def join_ride(self, user_id: UUID, ride_id: UUID):
        """Adiciona utilizador ao grupo de uma corrida"""
        user_key = str(user_id)
        ride_key = str(ride_id)
        
        if ride_key not in self.ride_groups:
            self.ride_groups[ride_key] = set()
        
        self.ride_groups[ride_key].add(user_key)
        
        if user_key in self.active_connections:
            self.active_connections[user_key].ride_id = ride_id
    
    def leave_ride(self, user_id: UUID, ride_id: UUID):
        """Remove utilizador do grupo de uma corrida"""
        user_key = str(user_id)
        ride_key = str(ride_id)
        
        if ride_key in self.ride_groups:
            self.ride_groups[ride_key].discard(user_key)
            
            # Remove grupo se vazio
            if not self.ride_groups[ride_key]:
                del self.ride_groups[ride_key]
        
        if user_key in self.active_connections:
            self.active_connections[user_key].ride_id = None
    
    def get_online_drivers_count(self) -> int:
        """Retorna número de motoristas online"""
        return len(self.online_drivers)
    
    def is_user_online(self, user_id: UUID) -> bool:
        """Verifica se utilizador está online"""
        return str(user_id) in self.active_connections


# Instância global
ws_manager = WebSocketManager()


# ============================================
# Mensagens WebSocket padrão
# ============================================

class WSMessage:
    """Factory para mensagens WebSocket"""
    
    @staticmethod
    def ride_requested(ride_id: UUID, origem: dict, destino: dict, valor: float) -> dict:
        return {
            "type": "ride_requested",
            "ride_id": str(ride_id),
            "origem": origem,
            "destino": destino,
            "valor_estimado": valor,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def ride_accepted(ride_id: UUID, driver: dict) -> dict:
        return {
            "type": "ride_accepted",
            "ride_id": str(ride_id),
            "driver": driver,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def driver_location(ride_id: UUID, lat: float, lon: float, bearing: float = None) -> dict:
        return {
            "type": "driver_location",
            "ride_id": str(ride_id),
            "location": {
                "latitude": lat,
                "longitude": lon,
                "bearing": bearing
            },
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def ride_started(ride_id: UUID) -> dict:
        return {
            "type": "ride_started",
            "ride_id": str(ride_id),
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def ride_finished(ride_id: UUID, valor_final: float) -> dict:
        return {
            "type": "ride_finished",
            "ride_id": str(ride_id),
            "valor_final": valor_final,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def ride_cancelled(ride_id: UUID, cancelled_by: str, reason: str = None) -> dict:
        return {
            "type": "ride_cancelled",
            "ride_id": str(ride_id),
            "cancelled_by": cancelled_by,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def new_ride_nearby(ride_id: UUID, origem: dict, valor: float, distancia: float) -> dict:
        return {
            "type": "new_ride_nearby",
            "ride_id": str(ride_id),
            "origem": origem,
            "valor_estimado": valor,
            "distancia_metros": distancia,
            "timestamp": datetime.now().isoformat()
        }
