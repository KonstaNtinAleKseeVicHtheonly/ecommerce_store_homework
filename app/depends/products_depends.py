from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from app.core.project_logging import project_logger
from typing import AsyncGenerator
from app.core.database import AsyncSessionLocal
from app.repositories import ProductRepository
from fastapi import Depends
from app.depends.db_depends import get_db_session
from app.depends.repository_depends import get_product_repository
from app.schemas.cartitems_schemas import CartItemUpdateSchema
from fastapi import HTTPException



async def get_current_product_depends( # 👈 прямо тут!
    session: AsyncSession = Depends(get_db_session),
    product_repo: ProductRepository = Depends(get_product_repository),
    payload: CartItemUpdateSchema = Depends(),
    product_id : int|None = None
    
):
    '''если текущий продукт есть в БД по его id То верне его иначе 404 ошибка'''
    if product_id is None:
        current_product_id = payload.product_id  # берем из payload
    else:
        current_product_id = product_id
        
    product = await product_repo.get_by_params(session, id=current_product_id, is_active=True)
    
    if not product:
        raise HTTPException(404, f"Product {product_id} not found")
    
    return product
    

# async def get_current_user(token: str = Depends(oauth2_scheme),
#                            session: AsyncSession = Depends(get_db_session),
#                            user_repo : UserRepository = Depends(get_user_repository)):
#     """
#     Проверяет JWT и возвращает пользователя из базы.Если таковой есть иначе ошибка
#     """
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_email: str = payload.get("sub")
#         project_logger.info(f"начало проверки данных от юзера {user_email} с jwt подписью ")
#         if user_email is None:
#             raise credentials_exception
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Token has expired",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     except jwt.PyJWTError:
#         raise credentials_exception
#     current_user = await user_repo.get_by_params(session, email=user_email, is_active=True)
#     if current_user is None:
#         project_logger('юзера с указанными данными не найден')
#         raise credentials_exception
#     project_logger.info("проверка завершена успешно")
#     return current_user