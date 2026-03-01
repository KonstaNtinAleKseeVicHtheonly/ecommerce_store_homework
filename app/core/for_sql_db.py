# from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
# from sqlalchemy import create_engine
# from app.core.project_logging import project_logger
# from sqlalchemy import text
# from typing import AsyncGenerator
# from sqlalchemy.orm import declarative_base, sessionmaker, DeclarativeBase
# import os
# from dotenv import load_dotenv


# load_dotenv()


# engine = create_engine("sqlite:///ecommerce.db")


# SessionLocal = sessionmaker(bind=engine) # это Фабрика - создаёт новые экземпляры сеансов (Session) при вызове
# # Определяем базовый класс для моделей
# class Base(DeclarativeBase):  # общая таблица для моделей проекта связыающая их мжеду собой и с СУБД
#     pass

# # # 2. Создаем фабрику сессий
# # AsyncSessionLocal = async_sessionmaker(
# #     engine,
# #     class_=AsyncSession,
# #     expire_on_commit=False,
# #     autocommit=False,
# #     autoflush=False
# # )
# # # 3. Базовый класс для моделей
# # Base = declarative_base()



# # # 4.  зависимость для FastAPI
# # async def get_db() -> AsyncGenerator[AsyncSession, None]:
# #     """
# #     FastAPI dependency that provides database session.
# #     Сессия автоматически создается для каждого запроса и закрывается после ответа.
# #     """
# #     async with AsyncSessionLocal() as session:
# #         project_logger.debug("🔌 Database session created")
# #         try:
# #             yield session
# #         finally:
# #             await session.close()
# #             project_logger.debug("🔌 Database session closed")
            
# # async def init_db():
# #     '''инициализация БД'''
# #     async with engine.begin() as conn:
# #         # Проверяем схему
# #         schema = await conn.execute(text("SELECT current_schema()"))
# #         project_logger.info(f"Текущая схема БД: {schema.scalar()}")
        
# #         # Создаем таблицы
# #         await conn.run_sync(Base.metadata.create_all)
# #         project_logger.info("✅ Таблицы созданы")
        
# # async def drop_db():
# #     """Удаляет все таблицы"""
# #     project_logger.warning("⚠️ Удаление таблиц...")
# #     async with engine.begin() as conn:
# #         await conn.run_sync(Base.metadata.drop_all)
# #     project_logger.warning("✅ Таблицы удалены")
    
