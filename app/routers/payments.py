
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Body, Path, Query, Depends, Request, Response, status, HTTPException
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
from app.config import YANDEX_IP_LIST
from app.tools.payments.payment_process import _extract_client_ip, is_ip_allowed
from yookassa.domain.notification import WebhookNotification
from loguru import logger

logger.add('payment.log')

payments_api_router = APIRouter(prefix="/api/payments", tags=['Payments'])



@payments_api_router.post('/yookassa/webhook', status_code=200)
async def yookassa_webhook(request : Request,
                            session:AsyncSession=Depends(get_db_session),
                            order_repo : OrderRepository = Depends(get_order_repository)):
    '''вебхук для отлова обнволений с юкассы'''

    client_ip = _extract_client_ip(request) # юерем id клиента
    ip_checker = is_ip_allowed(client_ip)
    if not ip_checker:# поверяем есть ли он в списке разрешенных
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"IP {client_ip} is not allowed")
    try:
        payload = request.json()
    except json.JSONDecodeError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"отправлен невалидный json : {err}")
        
    try:
        notification = WebhookNotification(payload)# валидизируем инфу от клиента для yookassa
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid notification: {exc}")

    current_payment = notification.object
    order_id = current_payment.metadata.get('order_id') if current_payment.metadata else None
    if not order_id:# order_id всегда должен быть передан в метадат при отправке запроса на оплату в юкасса(в методе create_yookassa_payment)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing order id")
    try:
        current_order = await order_repo.get_by_id(session, int(order_id))
    except ValueError:
        return {"status" : 'ignored'} # не найден текущий заказ
    if current_payment.status == 'succeeded':# при успешно заказе данному заказу меняем статус и присваиваем id транзакции
        if not current_order.paid_at: # если время платежа не проставлено
            current_order.status = "paid"
            current_order.paid_at = datetime.now(timezone.utc)
            current_order.payment_id = current_payment.id
    elif current_payment.status == 'canceled':# в случае отмены платежа прост оменяем статус заказа
        current_order.status = 'cancelled' 
    await session.commit()
    return {'status' : 'ok'}



@payments_api_router.get("/create_session")
async def session_set(request: Request):
    '''тестовый метод для создания сессии'''
    logger.info("создагте свой сессии")
    request.session["my_session"] = "1234"
    return 'ok'
        
@payments_api_router.get('/read_session', status_code=200)
async def read_session(request : Request):
    '''тестовый эндпоинт для чтения инфы о запросе'''
    current_session = request.session.get('my_session')
    logger.info(f"вывод инфы из своей сессии | {current_session}")
    if current_session:
        logger.info("К сожалению сессия пустая")
        return {"session_value": current_session}
    else:
        return {"message": "No session found"}

