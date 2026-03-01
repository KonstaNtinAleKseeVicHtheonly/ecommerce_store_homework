from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from app.core.project_logging import project_logger
from typing import AsyncGenerator
from app.core.database import AsyncSessionLocal





async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides database session.
    Сессия автоматически создается для каждого запроса и закрывается после ответа.
    """
    async with AsyncSessionLocal() as session:
        project_logger.debug("🔌 Database session created")
        yield session
    # ЗАКРЫТИЕ СЕССИИ
    project_logger.debug("🔌 Database session closed")
            
