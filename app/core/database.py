from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from app.core.project_logging import project_logger
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv



load_dotenv()


engine = create_async_engine(os.getenv('DB_URL_Postgre'))

# 2. Создаем фабрику сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)
# 3. Базовый класс для моделей
class Base(DeclarativeBase):  # общая таблица для моделей проекта связыающая их мжеду собой и с СУБД
    pass


            
async def init_db():
    '''инициализация БД'''
    async with engine.begin() as conn:
        # Проверяем схему
        schema = await conn.execute(text("SELECT current_schema()"))
        project_logger.info(f"Текущая схема БД: {schema.scalar()}")
        
        # Создаем таблицы
        await conn.run_sync(Base.metadata.create_all)
        project_logger.info("✅ Таблицы созданы")
        
async def drop_db():
    """Удаляет все таблицы"""
    project_logger.warning("⚠️ Удаление таблиц...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    project_logger.warning("✅ Таблицы удалены")
    
