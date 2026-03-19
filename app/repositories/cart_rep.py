from app.repositories.base import BaseRepository
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import CartItemModel, ProductModel
from sqlalchemy.orm import selectinload
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


class CartRepository(BaseRepository):
    
    def __init__(self):
                super().__init__(CartItemModel)
                
    async def _get_user_cart_item(self, session:AsyncSession, user_id:int, product_id:int)->CartItemModel|None:
        '''по Id юзера  и товара выводит товар из корзины если он там есть иначе None(для проверки при добавлении товара в корзину)'''
        try:
            project_logger.info(f"НАчало вывода товара с id {product_id} в корзине юзера {user_id}")
            cart_item_stmt = select(self.model).options(selectinload(self.model.product)).where(
                self.model.user_id == user_id, self.model.product_id == product_id) # через жадную загрузку делаем т.к через relationship ищем
            cart_item_request = await session.scalars(cart_item_stmt)
            cart_item = cart_item_request.first()
            project_logger.info("поиск товара в корзине юзера произведен успешно")
            return cart_item
        except Exception as err:
            project_logger.error(f"Ошибка при выводе позиции товара корзины {product_id} у юзера {user_id} : {err}")
            
    async def _get_user_total_cart(self, session:AsyncSession, user_id:int):
        '''выводит всю корзину юзера по его id'''
        try:
            project_logger.info(f"НАчало вывода всей корзины товаров  пользователя {user_id}")
            cart_item_stmt = select(self.model).options(selectinload(self.model.product)).where(
                self.model.user_id == user_id).order_by(self.model.id) # через жадную загрузку делаем т.к через relationship ищем
            cart_item_request = await session.scalars(cart_item_stmt)
            user_cart = cart_item_request.all()
            project_logger.info("поиск товара в корзине юзера произведен успешно")
            return user_cart
        except Exception as err:
            project_logger.error(f"Ошибка при выводе всей корзины  у юзера {user_id} : {err}")
            
    def _calculate_total_cart_price(self, cart_items:list[CartItemModel]):
        '''расчитывает стоимость всей корзины по цене товаров в корзине и их количеству'''
        project_logger.info(f"Начало расчета стоимости корзины товаров юзреа с {cart_items}")
        items_price = (
            Decimal(item.quantity) * 
            (item.product.price if item.product.price is not None else Decimal("0"))
            for item in cart_items)
        items_price_decimal = sum(items_price, Decimal("0.00"))
        project_logger.info(f"Общая стоимость всей корзины  {items_price_decimal}")
        return items_price_decimal
        
        
    def _calculate_postions_quantity_in_total_cart(self, cart_items:list[CartItemModel]):
        '''находит общее количество товаров в окрине юзера'''
        project_logger.info(f"Начало обего числа товаров в корзине юзера с {cart_items}")
        total_quantity = sum(item.quantity for item in cart_items)
        project_logger.info(f"Размер корзины {total_quantity}")
        return total_quantity
    
    async def delete_user_cart(self, session:AsyncSession, user_id:int):
        '''удаляет по id Юзера всю его корзину с товарами'''
        project_logger.info(f"удаление всей корзины юзера с id {user_id}")
        await session.execute(delete(self.model).where(self.model.user_id == user_id))
        