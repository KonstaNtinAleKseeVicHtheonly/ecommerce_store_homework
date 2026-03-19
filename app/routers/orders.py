
from fastapi import APIRouter, Body, Path, Query, Depends, Response, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
# схемы
from app.schemas.order_schemas import OrderItemSchema, OrderListSchema, OrderSchema, OrderCheckoutResponseSchema

#репозитории БД
from app.repositories import  CartRepository, OrderRepository
#depends
from app.depends.repository_depends import  get_cart_repository, get_order_repository
from app.depends.db_depends import get_db_session
# jwt, авторизация и аутентификация
from app.auth import get_current_user
# модели 
from app.models import UserModel
# оплата заказов
from app.tools.payments.payment_process import create_yookassa_payment
orders_api_router = APIRouter(prefix="/api/orders", tags=['Orders'])


@orders_api_router.get('/', response_model=OrderListSchema)
async def show_user_orders(session:AsyncSession=Depends(get_db_session),
                            page:int = Query(1, ge=1),
                            page_size:int = Query(10, ge=1, le=100),
                            current_user : UserModel=Depends(get_current_user),
                            order_repo : OrderRepository = Depends(get_order_repository)):
    '''Выводит все заказы юзера'''
    # все заказы юзера и их общее количество
    all_orders_and_number : dict= await order_repo.get_user_orders_paginated(session, page=page,
                                                                       page_size=page_size,
                                                                       user_id=current_user.id)
    return {'items' : all_orders_and_number['orders'],
            'total' : all_orders_and_number['total'], 
            'page' : page, 
            'page_size': page_size}
    

@orders_api_router.get('/{order_id}', response_model=OrderSchema)
async def show_current_order(session:AsyncSession=Depends(get_db_session),
                            order_id : int = Path(ge=1),
                            current_user : UserModel=Depends(get_current_user),
                            order_repo : OrderRepository = Depends(get_order_repository)):
    '''по id заказа выводит инфу по нему'''
    current_order = await order_repo._load_order_with_items(session, order_id)
    if not current_order:
            raise HTTPException(
                status_code=404,
                detail=f"заказа с id {order_id} не найдено в базе")
    return current_order

@orders_api_router.get('/{order_id}/status')
async def show_current_order_status(session:AsyncSession=Depends(get_db_session),
                                    order_id : int = Path(ge=1),
                                    current_user : UserModel=Depends(get_current_user),
                                    order_repo : OrderRepository = Depends(get_order_repository)):
    ''' по id заказа выводит инфу инфу о его статусе'''
    current_order = await order_repo.get_by_id(session, order_id)
    if current_order.user_id != current_user.id:            
        raise HTTPException(
                status_code=404,
                detail="Вы можете просматривать только ваши заказы")
    order_info  = {'order_id' : order_id}
    order_info['status'] = current_order.status
    if current_order.status == 'paid ':
        order_info['message'] = "Спасибо! Заказ #123 оплачен. Ожидайте доставку."
        order_info['paid_at'] = current_order.paid_at
    elif current_order.status in ('canceled', 'failed'):
        order_info['message'] = "Оплата не прошла. Попробуйте ещё раз."
        order_info['paid_at'] = None
    elif current_order.status == 'pending':
        order_info['message'] = "Оплата в процессе..."
    else:
        order_info['message'] = "Уточняем данные по вашему заказу, уточните информацию позже"
        order_info['paid_at'] = None
    return order_info        
        
        
                            
@orders_api_router.post('/checkout', response_model=OrderCheckoutResponseSchema, status_code=201)
async def create_order_from_user_cart(
                              session:AsyncSession=Depends(get_db_session),
                              current_user : UserModel=Depends(get_current_user),
                              cart_repo : CartRepository = Depends(get_cart_repository),
                              order_repo: OrderRepository = Depends(get_order_repository)):
    """
    Создаёт заказ на основе текущей корзины пользователя.
    Сохраняет позиции заказа, вычитает остатки и очищает корзину.
    """
    user_cart = await cart_repo._get_user_total_cart(session, current_user.id)
    if not user_cart:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")
    new_order = await order_repo.create_new_order_from_cart(session, user_cart)
    # процесс отправки заказа на юкассу
    try:
        await session.flush() # отправляем только что созданный заказ в БД (генерирует первичный ключ и присваивает его объекту, но транзакция остается открытой)
        payment_info = await create_yookassa_payment(
            order_id=new_order.id,# из за flush мы может уже брать id заказа из бд
            amount=new_order.total_amount,
            user_email=current_user.email,
            description=f"Оплата заказа #{new_order.id}",
        )
    #в случае ошибок все подготовки к оплате откатываем назад
    except RuntimeError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        await session.rollback() # если платёж не был создан, заказ не должен остаться в системе 
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Не удалось инициировать оплату {exc}",
        ) from exc

    new_order.payment_id = payment_info.get("id") # присваиваем заказу уникальный id оплаты
    
    await cart_repo.delete_user_cart(session, current_user.id)#  чистим корзину юзера после формирования заказа
    await session.commit()
    
    created_order = await order_repo._load_order_with_items(session, new_order.id) # выводим заказ юзера со всеми позициями| проверка на создание в самом методе репозитория
    return created_order
    
