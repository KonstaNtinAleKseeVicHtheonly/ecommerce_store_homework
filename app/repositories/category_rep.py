from app.repositories.base import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import CategoryModel, ProductModel
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

class CategoryRepository(BaseRepository):
    
    def __init__(self):
                super().__init__(CategoryModel)
                
    async def get_category_products_by_id(self, session : AsyncSession, category_id:int):
        '''по категории id если таковая есть выводим все ее продукты'''
        
        category_is_active = await self.object_is_active(session, category_id)
        if not category_is_active:
            raise ValueError(f"Category {category_id} not found or inactive")
        stmt = select(ProductModel).where(ProductModel.category_id== category_id, ProductModel.is_active)
        result = await session.execute(stmt)
        category_products = result.scalars().all()
        return category_products
            
            
