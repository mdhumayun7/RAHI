"""
RAHI Database Connection Manager
==================================
Handles all PostgreSQL connections using SQLAlchemy async engine.

Why async?
  RAHI will handle multiple requests simultaneously in production.
  Async DB calls prevent blocking — while waiting for DB response,
  RAHI can process other requests.
"""

import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import text

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://rahi_user:rahi_pass@localhost:5432/rahi_db"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,           # Set True to see SQL queries in terminal
    pool_size=10,
    max_overflow=20,
)

# Session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass


async def get_db():
    """Dependency: yields a DB session, closes it after use."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def test_connection():
    """Test that DB is reachable and pgvector is enabled."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT version()"))
        version = result.scalar()
        print(f"✅ PostgreSQL connected: {version[:50]}")

        result2 = await session.execute(
            text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
        )
        ext = result2.scalar()
        if ext:
            print("✅ pgvector extension: enabled")
        else:
            print("⚠️  pgvector not found — run: CREATE EXTENSION vector;")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_connection())