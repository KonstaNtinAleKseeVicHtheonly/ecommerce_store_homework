from typing import List
from decimal import Decimal
from fastapi import APIRouter, Body, Path, Query, Depends, Response, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
# схемы
from app.schemas.cartitems_schemas import CartItemCreateSchema, TotalCartSchema, CartItemSchema, CartItemUpdateSchema

#репозитории БД
from app.repositories import ProductRepository, CartRepository
#depends
from app.depends.repository_depends import get_product_repository, get_cart_repository
from app.depends.products_depends import get_current_product_depends
from app.depends.db_depends import get_db_session
# jwt, авторизация и аутентификация
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import get_current_user
# модели 
from app.models import UserModel, ProductModel, CartItemModel

carts_api_router = APIRouter(prefix="/api/carts", tags=['Carts'])


@carts_api_router.get('/', response_model=TotalCartSchema)
async def get_user_total_cart(session:AsyncSession=Depends(get_db_session),
                              current_user : UserModel=Depends(get_current_user),
                              cart_repo : CartRepository = Depends(get_cart_repository)):
    '''без доп параметров поиска выводит корзину авторизированного юзера(через jwt токен)'''
    cart_items = await cart_repo._get_user_total_cart(session, current_user.id)
    total_quantity =  cart_repo._calculate_postions_quantity_in_total_cart(cart_items)
    total_price_decimal =  cart_repo._calculate_total_cart_price(cart_items)
    return {'user_id':current_user.id,
        'items' : cart_items,
        'total_quantity' : total_quantity,
        'total_price' :total_price_decimal}
    
@carts_api_router.post('/items', response_model=CartItemCreateSchema, status_code=201)
async def add_item_to_cart(payload : CartItemCreateSchema,
                            session : AsyncSession=Depends(get_db_session),
                              current_user : UserModel=Depends(get_current_user),
                              cart_repo : CartRepository = Depends(get_cart_repository),
                              product : ProductModel = Depends(get_current_product_depends)):
    '''Добавляет товар в корзину'''
    
    cart_item = await cart_repo._get_user_cart_item(session, current_user.id, product.id)
    # юзер не может в корзину добавить больше товара чем есть в магазине
    if product.stock <= payload.quantity:
        raise HTTPException(status_code=401, detail=f"В магазине всего {product.stock} единиц товара {product.name}, а вы хотите добавить {payload.quantity}")
    if cart_item:# Товар уже был к орзине просто увеличиваем его количество
        cart_item.quantity += payload.quantity
    else: # значит не было в корзине данного товара еще
        new_cart_item_info = {'user_id' : current_user.id,
                              'product_id' : product.id,
                              'quantity' : payload.quantity}
        await cart_repo.create(session, new_cart_item_info)
    await session.commit()
    updated_cart_item = await cart_repo._get_user_cart_item(session, current_user.id, product.id)
    return updated_cart_item
        
    
@carts_api_router.put('/items/{product_id}', response_model=CartItemSchema, status_code=201)
async def update_item_in_cart(payload : CartItemUpdateSchema,
                           product_id : int,
                           session:AsyncSession=Depends(get_db_session),
                              current_user : UserModel=Depends(get_current_user),
                              product : ProductModel = Depends(get_current_product_depends),
                              cart_repo : CartRepository = Depends(get_cart_repository)):
    '''изменение товара в корзине'''
    cart_item = await cart_repo._get_user_cart_item(session, current_user.id, product_id) #проверка существования позиции в корзине
    if cart_item is None:
        raise HTTPException(status_code=404, detail="такого продукта нет в вашей корзине что бы его изменить")
    if payload.quantity == 0:
        await session.delete(cart_item)
    else:
        cart_item.quantity = payload.quantity
    await session.commit()
    updated_item = await cart_repo._get_user_cart_item(session, current_user.id, product_id) # гарантируем возврат уже измененных данных
    return updated_item
    

    
@carts_api_router.delete("/items/{product_id}",  status_code=204)
async def delete_item_from_cart(product_id:int,
                                session:AsyncSession=Depends(get_db_session),
                                current_user : UserModel=Depends(get_current_user),
                                product : ProductModel = Depends(get_current_product_depends),
                              cart_repo : CartRepository = Depends(get_cart_repository)):
    '''удаление позиции из корзины'''
    cart_item = await cart_repo._get_user_cart_item(session, current_user.id, product_id) #проверка существования позиции в корзине
    if cart_item is None:
        raise HTTPException(status_code=404, detail="такого продукта нет в вашей корзине что бы его удалить")
    await cart_repo.delete_by_id(session, cart_item.id)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@carts_api_router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_cart(
    session: AsyncSession = Depends(get_db_session),
    current_user: UserModel = Depends(get_current_user),
    cart_repo : CartRepository = Depends(get_cart_repository)
):
    '''удаляет всю корзину юзера с товарами целиком'''
    await cart_repo.delete_user_cart(session, current_user.id)
    await session.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)