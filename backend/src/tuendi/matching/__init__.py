"""
TUDOaqui - Driver Matching Service
Algoritmo de matching com geo-filter e prioridade
"""
from typing import List, Optional
import math
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.tuendi.drivers.models import Driver, DriverStatus


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class MatchingService:
    """Matching de motoristas por proximidade, rating e disponibilidade."""

    MAX_RADIUS_KM = 10.0
    MAX_RESULTS = 5

    async def find_nearest_drivers(
        self,
        db: AsyncSession,
        lat: float,
        lon: float,
        vehicle_type: Optional[str] = None,
        radius_km: Optional[float] = None,
        limit: Optional[int] = None,
    ) -> List[dict]:
        """Retorna motoristas mais proximos, ordenados por score."""
        radius = radius_km or self.MAX_RADIUS_KM
        max_results = limit or self.MAX_RESULTS

        conditions = [
            Driver.online == True,
            Driver.status == DriverStatus.APROVADO.value,
            Driver.latitude.is_not(None),
            Driver.longitude.is_not(None),
        ]
        if vehicle_type:
            conditions.append(Driver.tipo_veiculo == vehicle_type)

        result = await db.execute(
            select(Driver).where(and_(*conditions))
        )
        drivers = result.scalars().all()

        candidates = []
        for d in drivers:
            dist = haversine_km(lat, lon, float(d.latitude), float(d.longitude))
            if dist > radius:
                continue
            rating = float(d.rating_medio) if d.rating_medio else 4.0
            score = self._compute_score(dist, rating, d.total_corridas or 0)
            candidates.append({
                "driver_id": str(d.id),
                "user_id": str(d.user_id),
                "nome": d.nome,
                "tipo_veiculo": d.tipo_veiculo,
                "placa": d.placa,
                "distance_km": round(dist, 2),
                "rating": rating,
                "total_corridas": d.total_corridas or 0,
                "score": round(score, 4),
            })

        candidates.sort(key=lambda c: c["score"], reverse=True)
        return candidates[:max_results]

    @staticmethod
    def _compute_score(distance_km: float, rating: float, total_rides: int) -> float:
        """Score = 40% proximidade + 40% rating + 20% experiencia."""
        prox = max(0, 1 - distance_km / 10)
        rat = rating / 5.0
        exp = min(1.0, total_rides / 200)
        return 0.4 * prox + 0.4 * rat + 0.2 * exp


matching_service = MatchingService()
