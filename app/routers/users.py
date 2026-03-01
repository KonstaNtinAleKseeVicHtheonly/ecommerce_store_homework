from fastapi import APIRouter, Body, Path, Query, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
# схемы
from app.schemas.user_schemas import UserSchema, UserCreateSchema
from app.schemas.jwt_schemas import RefreshTokenRequestSchema
#
from app.repositories import ProductRepository, UserRepository
#depends
from app.depends.repository_depends import get_product_repository, get_user_repository
from app.depends.db_depends import get_db_session

# jwt, авторизация аутентификация
import jwt
from app.config import SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import hash_password, verify_password, create_access_token , get_current_seller, create_refresh_token



user_api_router = APIRouter(prefix="/api/users", tags=['Users'])






@user_api_router.post('/', response_model=UserSchema,  status_code=status.HTTP_201_CREATED)
async def create_new_user(new_user_info:UserCreateSchema,
                         session : AsyncSession = Depends(get_db_session),
                         user_repo : ProductRepository = Depends(get_user_repository)):
        try:
            existed_user = await user_repo.get_by_params(session , email = new_user_info.email)
            if existed_user: # если такой юзер уже существует
                     raise HTTPException(status_code=409, detail=" such a User has already been registered")
            new_user_validated_data = {"email" : new_user_info.email,
                "hashed_password":hash_password(new_user_info.password),
                "role": new_user_info.role}
            
            new_user = await user_repo.create(session, new_user_validated_data) 
            await session.commit()
            await session.refresh(new_user)
            return new_user
        except Exception as err:
                                     raise HTTPException(
            status_code=500,
            detail=str(err))  
                            
@user_api_router.post('/token')
async def login_user(form_data:OAuth2PasswordRequestForm = Depends(),
                     session: AsyncSession= Depends(get_db_session),
                     user_repo:UserRepository = Depends(get_user_repository)):
    '''аутентифицирует юзера и вовзвращает jwt токен с почтой ролью и id'''
    current_user = await user_repo.get_by_params(session, email=form_data.username, is_active=True)
    if not current_user or not verify_password(form_data.password, current_user.hashed_password):
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # создает jwt refresh токен
    refresh_token = create_refresh_token(data={'sub':current_user.email,'role':current_user.role,
                                             'id' : current_user.id})
    # создаем jwt access Токен с сроком годности
    access_token = create_access_token(data={'sub':current_user.email,'role':current_user.role,
                                             'id' : current_user.id})
    return {'access_token' : access_token, 'refresh_token' : refresh_token, 'token_type' : 'bearer'}
    
@user_api_router.post('/refresh_token')
async def refresh_token(body:RefreshTokenRequestSchema,
                     session: AsyncSession= Depends(get_db_session),
                     user_repo:UserRepository = Depends(get_user_repository)):
    """
    Обновляет refresh-токен, принимая старый refresh-токен в теле запроса.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"})
    old_refresh_token = body.refresh_token
    
    try:
        
        payload = jwt.decode(old_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str | None = payload.get("sub")
        token_type: str | None = payload.get("token_type")
        # если не подходят условия или не тот тип токена(access)
        if user_email is None or token_type != "refresh":
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        # refresh-токен истёк
        raise credentials_exception
    except jwt.PyJWTError:
        # подпись неверна или токен повреждён
        raise credentials_exception
    current_user = await user_repo.get_by_params(session, email=user_email, is_active=True)
    if current_user is None:
        raise credentials_exception
    # если все ок создае новый рефреш токен
    new_refresh_token = create_refresh_token(
        data={"sub": current_user.email, "role": current_user.role, "id": current_user.id}
    )
    return {
        "refresh_token": new_refresh_token,
        "token_type": "bearer"}
    


@user_api_router.post('/access_token')
async def get_new_access_token(body:RefreshTokenRequestSchema,
                     session: AsyncSession= Depends(get_db_session),
                     user_repo:UserRepository = Depends(get_user_repository)):
    '''по текущему refresh токену если он валиден и юзер есть и активен - выдает новый access токен юзера'''
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"})
    current_refresh_token = body.refresh_token
    try:
        payload = jwt.decode(current_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str | None = payload.get("sub")
        token_type: str | None = payload.get("token_type")
        if user_email is None or token_type != 'refresh':
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        # refresh-токен истёк
        raise credentials_exception
    except jwt.PyJWTError:
        # подпись неверна или токен повреждён
        raise credentials_exception
    except BaseException:
        raise ValueError("общая ошибка при обновлении рефреш токена")
    current_user = await user_repo.get_by_params(session, email=user_email, is_active=True)
    if current_user is None:
        raise credentials_exception
    new_access_token = create_access_token( data={"sub": current_user.email, "role": current_user.role, "id": current_user.id})
    return {'new_access_token' : new_access_token, "token_type": "bearer"}

    
# @user_api_router.put('/{product_id}', response_model=ProductSchema)
# async def update_user(update_info : ProductCreateSchema,
#                         product_id : int = Path(ge=0),
#                          session : AsyncSession = Depends(get_db_session),
#                         product_repo : ProductRepository = Depends(get_product_repository),
#                         category_repo : CategoryRepository = Depends(get_category_repository)):
#         try:
#             product_is_active = await product_repo.object_is_active(session, product_id)
#             if not product_is_active:
#                 raise HTTPException(status_code=400, detail=f"Product with id : {product_id} doesn't exist or inactive")
#             category_is_active  = await category_repo.object_is_active(session , update_info.category_id)
#             if not category_is_active:
#                      raise HTTPException(status_code=400, detail=f"Category with id {update_info.category_id} doesn't exist or inactive")
#             updated_product = await product_repo.update_put(session, product_id, update_info.model_dump())
#             await session.commit()
#             await session.refresh(updated_product)
#             return updated_product
#         except Exception as err:
#                                      raise HTTPException(
#             status_code=500,
#             detail=str(err))  




# @user_api_router.delete('/{product_id}',  status_code=status.HTTP_200_OK)
# async def delete_user(product_id : int = Path(ge=0),
#                             session : AsyncSession = Depends(get_db_session),
#                              repo : ProductRepository = Depends(get_product_repository)):
#     try:
#         deleted_product = await repo.soft_deleting_by_id(session, product_id)
#         await session.commit()
#         await session.refresh(deleted_product)
        
#         return {'message' : f"продукт с id {product_id} стал неактивен"}
#     except Exception as err:
#                          raise HTTPException(
#             status_code=500,
#             detail=str(err))  


