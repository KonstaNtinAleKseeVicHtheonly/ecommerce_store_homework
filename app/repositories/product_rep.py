from app.repositories.base import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import ProductModel, ReviewModel
from app.core.project_logging import project_logger
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


class ProductRepository(BaseRepository):
    
    def __init__(self):
                super().__init__(ProductModel)
     
    async def assert_product_rating(self, session : AsyncSession, product_id):
        '''метод для подсчета среднего рейтинга на товар основываясь на поле rating'''
        project_logger.info("Начало расчета среднего рейтинга товара")
        try:
            current_product = await self.get_by_id(session, product_id)
            product_rating_request = await session.execute(
                select(func.avg(ReviewModel.grade)).where(
                    ReviewModel.product_id == product_id,
                    ReviewModel.is_active == True)
            )
            avg_rating = product_rating_request.scalar() or 0.0
            current_product.rating = avg_rating
            project_logger.info(f"средний рейтинг товара с id {product_id} успешно выполнен и равен {avg_rating}, сделайте коммит")
            return avg_rating
        
        except Exception as err:
            raise BaseException(f"что то пошло не так при вычислении рейтинга товарас с id {product_id} : {err}")
            

          