from app.repositories.base import BaseRepository
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import OrderModel, OrderItemModel, CartItemModel
from app.core.project_logging import project_logger
from decimal import Decimal
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


class OrderRepository(BaseRepository):
    
    item_model = OrderItemModel # добавили для точеченого взаимодействия с позициями в заказе юзера
    
    def __init__(self):
                super().__init__(OrderModel)
     
    async def _load_order_with_items(self, session : AsyncSession, order_id:int):
        '''по id заказа выводит все его позиции(товраы) через связь с OrderItemModel'''
        try:
            project_logger.info(f"Выгрузка всех товаров из заказа по id {order_id}")
            order_items = await session.scalars(
            select(self.model)
            .options(
                selectinload(self.model.items).selectinload(self.item_model.product)).where(self.model.id == order_id))
            current_order = order_items.first()
            if not current_order:
                    raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Серверная ошибка при создании заказа, повторите позже",
                )
        except Exception as err:
            project_logger.error(f"Ошибка при выгрузке заказа с id {order_id} : {err}")
            raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Серверная ошибка при создании заказа, повторите позже",
                )
        
    async def _load_item_from_order_paginated(self, session : AsyncSession, page:int, page_size:int,order_id:int):
        '''по id поизиции в заказе юзра выводит инфу о ней с учетом пагинации'''
        project_logger.info(f"выгрузка опред позиции из заказа с item_id {order_id} с инфой о продукте ")
        current_order_items= await session.scalars(
            select(self.item_model)
            .options(selectinload(self.item_model.product))
            .where(self.item_model.id == order_id)
            .order_by(self.item_model.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size))
        return current_order_items.all()
    
    async def create_new_order_from_cart(self, session:AsyncSession, user_cart_items:list[CartItemModel]):
        '''создает по корзине юзера новый заказ вычисляя цену, изменяя количество товара  на складе и прочие изменения'''
        project_logger.info(f"начало формирования заказа юзера из его корзины : {user_cart_items}")
        current_user_id = user_cart_items[0].user_id # из любой позиции в корзине юзера можно его ud взять
        
        new_order = self.model(user_id=current_user_id)# создание оболочки заказа с привязкой к user_id для наполнения его товарами из корзины
        total_amount = Decimal("0")# общая стоимость товаров в корзине
        project_logger.info("Считываем все заказы из корзины расчитываем стоимость")
        for cart_item in user_cart_items:
            project_logger.info(f"Добавление товара {cart_item}")
            product = cart_item.product
            # проверка активен ли продук в базе
            if not product or not product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product {cart_item.product_id} is unavailable",
                )
            # проверка есть ли в магазе столько, сколько юзер в коризну добавил
            if product.stock < cart_item.quantity:
                            raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Not enough stock for product {product.name}",
                )
            unit_price = product.price # цена за штуку товара на момент формирования заказа
            if unit_price is None:# есть ли у продукта цена, на всякий случай
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product {product.name} has no price set",
                )
            if not cart_item.quantity:# доп проверка на количество товара в корзине на всякий случай ибо заебала ошибка выскакивать
                project_logger.warning(f"у продукта {product.name} в корзине заказа количество 0")
                continue
            else:
                total_price = unit_price * cart_item.quantity # Общая стоимость данного продукта в заказе
                total_amount += total_price # пересчитываем общую стоимоссть всего заказа юзера
                order_item = OrderItemModel( # создаем данный зказа юзера по товарам из корзины
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    unit_price=unit_price,
                    total_price=total_price)
            
            new_order.items.append(order_item) # добавили в общий заказ юзера позицию по текущему товару из корзины учитывая стоимость количество и т.д
            project_logger.info(f"товар {cart_item} добавлен")
            product.stock -= cart_item.quantity # со склада убираем количество товара из заказа
            
        new_order.total_amount = total_amount # общая мтоимость всей корзины 
        session.add(new_order) # общи заказ со всеми позициями добавили в сессиию
        project_logger.info(f"общий заказ из товаров в корзине на общую стоимость {total_amount} сформирован успешно, и добалвен в сессию, сделайте коммит")
        return new_order
        
    async def get_user_orders_paginated(self, session : AsyncSession, page:int, page_size:int, user_id:int)->dict:
        '''выводит все заказы юзера с пагинацией и их общее количество - все в словаре'''
    
        total = await session.scalar(
            select(func.count(OrderModel.id)).where(OrderModel.user_id == user_id)
        ) # общее количество
        result = await session.scalars(
            select(OrderModel)
            .options(selectinload(OrderModel.items).selectinload(OrderItemModel.product))
            .where(OrderModel.user_id == user_id)
            .order_by(OrderModel.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        orders = result.all()
        return {'total' : total, 
                'orders' : orders}
