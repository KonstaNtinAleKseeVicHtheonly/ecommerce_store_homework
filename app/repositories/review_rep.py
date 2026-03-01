from app.repositories.base import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import UserModel, ProductModel, ReviewModel
from sqlalchemy import (
    select,        # для создания SELECT запросов
    insert,        # для INSERT
    update,        # для UPDATE
    delete,        # для DELETE
    and_,          # логическое И
    or_,           # логическое ИЛИ
    not_,          # логическое НЕ
    desc,          # сортировка по убыванию
    asc,           # сортировка по возрастанию
    func,          # SQL функции (count, sum, avg, etc.)
    between,       # BETWEEN оператор
    distinct,      # DISTINCT
    text,          # для сырых SQL запросов
)
from sqlalchemy.orm import selectinload

class ReviewRepository(BaseRepository):
    
    def __init__(self):
                super().__init__(ReviewModel)

            
