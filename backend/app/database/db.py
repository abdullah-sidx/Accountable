"""
Accountable Platform — Database Engine & Session Factory
=========================================================
Provides:
  - async_engine          : SQLAlchemy async engine
                            SQLite (aiosqlite) for local dev,
                            PostgreSQL (asyncpg) for production.
  - async_session_factory : sessionmaker for background services
  - get_db()              : FastAPI dependency-injected AsyncSession
  - init_db()             : create all tables on startup (dev/test)
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.config import settings

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
# SQLite requires check_same_thread=False and StaticPool so that
# aiosqlite reuses a single connection safely across async tasks.
# PostgreSQL connections use the default QueuePool — those kwargs are
# passed only when the URL is NOT a SQLite URL.
# ---------------------------------------------------------------------------

_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

_engine_kwargs = (
    {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }
    if _is_sqlite
    else {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,
    }
)

async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    **_engine_kwargs,
)

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------

async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------

async def get_db():
    """Yield a scoped AsyncSession; commit/rollback on exit."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ---------------------------------------------------------------------------
# Table creation (dev / test)
# ---------------------------------------------------------------------------

async def init_db() -> None:
    """Create all SQLAlchemy-mapped tables if they don't exist."""
    from app.database.models import Base  # lazy import to avoid circular

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
