"""
Alembic env.py - TUDOaqui database migrations
"""
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import Base e todos os modelos para que metadata tenha todas as tabelas
from src.database import Base
from src.config import settings

# Import all models so they register with Base.metadata
from src.users.models import User, UserRole, OTPCode, RefreshToken  # noqa
from src.events.models import Event, TicketType, Ticket, CheckIn  # noqa
from src.marketplace.models import (Seller, ProductCategory, Product, MarketplaceOrder, OrderItem, ProductReview)  # noqa
from src.alojamento.models import (Property, PropertyAvailability, Booking, PropertyReview)  # noqa
from src.turismo.models import (Experience, ExperienceSchedule, ExperienceBooking, ExperienceReview)  # noqa
from src.realestate.models import (RealEstateAgent, RealEstateProperty, Lead, PropertyFavorite)  # noqa
from src.tuendi.restaurante.models import (Restaurant, MenuCategory, MenuItem, FoodOrder, FoodOrderItem, RestaurantReview)  # noqa
from src.tuendi.entrega.models import (Delivery, DeliveryTracking)  # noqa
from src.tuendi.rides.models import (Ride, RideTracking, Rating)  # noqa
from src.tuendi.drivers.models import Driver  # noqa
from src.payments.models import (Payment, LedgerEntry, Wallet)  # noqa
from src.partners import Partner  # noqa
from src.notifications.models import Notification  # noqa

target_metadata = Base.metadata


def get_url():
    # Use sync driver for migrations
    url = settings.DATABASE_URL
    url = url.replace("+asyncpg", "")
    return url


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.DATABASE_URL
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
