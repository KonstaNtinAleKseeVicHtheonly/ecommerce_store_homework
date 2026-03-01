from typing import List
from fastapi import APIRouter, Body, Path, Query, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
# схемы
from app.schemas.products_schemas import ProductSchema, ProductCreateSchema
from app.schemas.reviews_schemas import ReviewSchema
#репозитории БД
from app.repositories import ProductRepository, CategoryRepository, ReviewRepository
#depends
from app.depends.repository_depends import get_product_repository, get_category_repository, get_review_repository
from app.depends.db_depends import get_db_session
# jwt, авторизация и аутентификация
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import get_current_seller
# модели 
from app.models import UserModel

product_api_router = APIRouter(prefix="/api/products", tags=['Products'])


@product_api_router.get('/', response_model = List[ProductSchema])
async def get_all_products(session : AsyncSession = Depends(get_db_session),
                           repo : ProductRepository = Depends(get_product_repository)
                           )->List[ProductSchema]:
    '''из базы берет все доступные категории'''
    try:
        all_products = await repo.get_objects_by_params(session, is_active = True)
        return all_products
        
    except Exception as err:
                 raise HTTPException(
            status_code=500,
            detail=str(err))  # общая ошибка 
        

@product_api_router.get('/{product_id}', response_model=ProductSchema)
async def get_current_product(product_id : int = Path(ge=0),
                             session : AsyncSession = Depends(get_db_session),
                             repo : ProductRepository = Depends(get_product_repository),
                              ) -> ProductSchema:
    '''Выводит инфу о продукте через id'''
    try:
        current_product = await repo.get_by_params(session, id=product_id, is_active=True)
        if not current_product:
            raise HTTPException(status_code=400, detail="Product doesn't exist or inactive")
        return current_product
    except ValueError as err:
        raise HTTPException(
            status_code=400,
            detail=str(err) )
    except Exception as err:
                 raise HTTPException(
            status_code=500,
            detail=str(err))  
                 
                 
@product_api_router.get('/{product_id}/reviews', response_model=List[ReviewSchema])
async def get_product_reviews(product_id : int = Path(ge=0),
                             session : AsyncSession = Depends(get_db_session),
                             product_repo : ProductRepository = Depends(get_product_repository),
                             review_repo : ReviewRepository = Depends(get_review_repository),
                              ) ->List[ReviewSchema]:
    '''По Id товара выводит все отзывы по нему. Доступно не аутентифицированным юзерам'''
    try:
        current_product = await product_repo.get_by_params(session, id=product_id, is_active=True)
        if not current_product:
              raise HTTPException(
            status_code=404)
        product_reviews = await review_repo.get_objects_by_params(session, product_id=product_id, is_active=True)
        return product_reviews
    except ValueError as err: # если юзер шляпу отправил какую то
        raise HTTPException(
            status_code=400,
            detail=str(err))
    except Exception as err:
                 raise HTTPException(
            status_code=500, 
            detail=str(err))  # общая ошибка на стороне сервера


@product_api_router.post('/', response_model=ProductSchema)
async def create_product(new_product_info:ProductCreateSchema,
                         session : AsyncSession = Depends(get_db_session),
                             product_repo : ProductRepository = Depends(get_product_repository),
                             category_repo : CategoryRepository = Depends(get_category_repository),
                             current_user: UserModel = Depends(get_current_seller)):
        try:
            existed_category = await category_repo.get_by_params(session , id=new_product_info.category_id, is_active = True)
            if existed_category is None : # если категории нет или она неактивно
                     raise HTTPException(status_code=400, detail="Category doesn't exist")
            new_product_validated_data = new_product_info.model_dump()
            new_product_validated_data['seller_id'] = current_user.id
            
            new_product = await product_repo.create(session, new_product_validated_data) # проверка на существование самого продукта внутри метода репозитория
            await session.commit()
            await session.refresh(new_product)
            return new_product
        except Exception as err:
                                     raise HTTPException(
            status_code=500,
            detail=str(err))
                                     
                                     

    
    

@product_api_router.get('/category/{category_id}', response_model=List[ProductSchema])
async def get_category_products(category_id : int = Path(ge=0),
                                session : AsyncSession = Depends(get_db_session),
                             category_repo : CategoryRepository = Depends(get_category_repository)):
    '''По id категории вывожит все вхоящие в нее продукты'''
    try:
        category_products = await category_repo.get_category_products_by_id(session, category_id)
        return category_products
    except ValueError as err:
        raise HTTPException(
            status_code=400,
            detail=str(err))
    except Exception as err:
                                    raise HTTPException(
        status_code=500,
        detail=str(err))  


    
    
@product_api_router.put('/{product_id}', response_model=ProductSchema)
async def update_product(update_info : ProductCreateSchema,
                        product_id : int = Path(ge=0),
                         session : AsyncSession = Depends(get_db_session),
                        product_repo : ProductRepository = Depends(get_product_repository),
                        category_repo : CategoryRepository = Depends(get_category_repository),
                        current_user: UserModel = Depends(get_current_seller)):
        try:
            current_product =   await product_repo.get_by_params(session, id=product_id, is_active=True)
            if not current_product:
                raise HTTPException(status_code=400, detail=f"Product with id : {product_id} doesn't exist or inactive")
            if current_product.seller_id != current_user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own products")
            category_is_active  = await category_repo.object_is_active(session , update_info.category_id)
            if not category_is_active:
                     raise HTTPException(status_code=400, detail=f"Category with id {update_info.category_id} doesn't exist or inactive")
            updated_product = await product_repo.update_put(session, product_id, update_info.model_dump())
            await session.commit()
            await session.refresh(updated_product)
            return updated_product
        except Exception as err:
                                     raise HTTPException(
            status_code=500,
            detail=str(err))  




@product_api_router.delete('/{product_id}',  status_code=status.HTTP_200_OK)
async def delete_product(product_id : int = Path(ge=0),
                        session : AsyncSession = Depends(get_db_session),
                        repo : ProductRepository = Depends(get_product_repository),
                        current_user: UserModel = Depends(get_current_seller)):
    try:
        current_product = await repo.get_by_params(session, id=product_id, is_active=True)
        if not current_product:
            raise HTTPException(status_code=400, detail=f"Product with id : {product_id} doesn't exist or inactive")
        if current_product.seller_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own products")
        deleted_product = await repo.soft_deleting_by_id(session, product_id)
        await session.commit()
        await session.refresh(deleted_product)
        
        return {'message' : f"продукт с id {product_id} стал неактивен"}
    except Exception as err:
                         raise HTTPException(
            status_code=500,
            detail=str(err))  







