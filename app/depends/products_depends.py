from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from app.core.project_logging import project_logger
from typing import AsyncGenerator
from app.core.database import AsyncSessionLocal
from app.repositories.product_rep import ProductRepository
from fastapi import Depends
from app.depends.db_depends import get_db_session
from app.depends.repository_depends import get_product_repository





