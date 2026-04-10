"""
TUDOaqui API - Rate Limiter
Sistema de rate limiting em memória com suporte a Redis (opcional)
"""
import asyncio
from datetime import datetime, timezone
from collections import defaultdict
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class InMemoryRateLimiter:
    """
    Rate limiter em memória usando sliding window.
    Para produção com múltiplas instâncias, usar Redis.
    """
    
    def __init__(self):
        # Estrutura: {key: [(timestamp, count), ...]}
        self._requests: Dict[str, list] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def check_rate_limit(
        self, 
        key: str, 
        limit: int, 
        window: int
    ) -> bool:
        """
        Verifica se a requisição está dentro do limite.
        
        Args:
            key: Identificador único (ex: "login:192.168.1.1")
            limit: Número máximo de requisições permitidas
            window: Janela de tempo em segundos
        
        Returns:
            True se permitido, False se bloqueado
        """
        async with self._lock:
            now = datetime.now(timezone.utc).timestamp()
            window_start = now - window
            
            # Remove entradas antigas
            self._requests[key] = [
                ts for ts in self._requests[key] 
                if ts > window_start
            ]
            
            # Verifica limite
            if len(self._requests[key]) >= limit:
                logger.warning(f"Rate limit exceeded for key: {key}")
                return False
            
            # Adiciona nova requisição
            self._requests[key].append(now)
            return True
    
    async def get_remaining(self, key: str, limit: int, window: int) -> Tuple[int, int]:
        """
        Retorna requisições restantes e tempo até reset.
        
        Returns:
            (remaining_requests, seconds_until_reset)
        """
        async with self._lock:
            now = datetime.now(timezone.utc).timestamp()
            window_start = now - window
            
            # Limpa entradas antigas
            self._requests[key] = [
                ts for ts in self._requests[key] 
                if ts > window_start
            ]
            
            current_count = len(self._requests[key])
            remaining = max(0, limit - current_count)
            
            # Calcula tempo até reset
            if self._requests[key]:
                oldest = min(self._requests[key])
                reset_in = int(oldest + window - now)
            else:
                reset_in = 0
            
            return remaining, max(0, reset_in)
    
    async def reset(self, key: str) -> None:
        """Limpa o rate limit para uma chave específica"""
        async with self._lock:
            if key in self._requests:
                del self._requests[key]
    
    async def cleanup(self) -> int:
        """
        Remove todas as entradas expiradas.
        Chamar periodicamente para evitar memory leak.
        
        Returns:
            Número de chaves removidas
        """
        async with self._lock:
            now = datetime.now(timezone.utc).timestamp()
            max_window = 3600  # 1 hora máximo
            window_start = now - max_window
            
            keys_to_remove = []
            for key, timestamps in self._requests.items():
                # Remove timestamps antigos
                self._requests[key] = [ts for ts in timestamps if ts > window_start]
                # Marca chave para remoção se vazia
                if not self._requests[key]:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self._requests[key]
            
            return len(keys_to_remove)


class RedisRateLimiter:
    """
    Rate limiter usando Redis para ambientes distribuídos.
    Usar quando houver múltiplas instâncias da API.
    """
    
    def __init__(self, redis_client=None):
        self._redis = redis_client
        self._fallback = InMemoryRateLimiter()
    
    async def check_rate_limit(
        self, 
        key: str, 
        limit: int, 
        window: int
    ) -> bool:
        """Verifica rate limit usando Redis"""
        if not self._redis:
            return await self._fallback.check_rate_limit(key, limit, window)
        
        try:
            import redis.asyncio as aioredis
            
            redis_key = f"ratelimit:{key}"
            
            # Pipeline para atomicidade
            pipe = self._redis.pipeline()
            now = datetime.now(timezone.utc).timestamp()
            window_start = now - window
            
            # Remove entradas antigas e adiciona nova
            pipe.zremrangebyscore(redis_key, 0, window_start)
            pipe.zadd(redis_key, {str(now): now})
            pipe.zcard(redis_key)
            pipe.expire(redis_key, window + 1)
            
            results = await pipe.execute()
            current_count = results[2]
            
            return current_count <= limit
            
        except Exception as e:
            logger.error(f"Redis rate limit error: {e}, falling back to memory")
            return await self._fallback.check_rate_limit(key, limit, window)


# Instância global — usa Redis se disponível, cai para memória como fallback
def _create_rate_limiter():
    """
    Tenta criar RedisRateLimiter.
    Se Redis não estiver disponível (ex: desenvolvimento sem Docker),
    usa InMemoryRateLimiter como fallback automático.
    """
    try:
        from src.config import settings
        import redis.asyncio as aioredis
        redis_client = aioredis.Redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=False,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        logger.info(f"Rate limiter: Redis ({settings.REDIS_URL})")
        return RedisRateLimiter(redis_client)
    except Exception as e:
        logger.warning(f"Rate limiter: Redis indisponível ({e}), usando InMemory (não distribuído)")
        return InMemoryRateLimiter()


rate_limiter = _create_rate_limiter()
