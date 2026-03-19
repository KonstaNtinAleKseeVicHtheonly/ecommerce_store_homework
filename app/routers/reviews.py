from app.core.project_logging import project_logger
from typing import List
from fastapi import APIRouter, Body, Path, Query, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
# схемы
from app.schemas.reviews_schemas import ReviewSchema, ReviewCreateSchema
#
from app.repositories import ProductRepository, ReviewRepository
#depends
from app.depends.repository_depends import get_product_repository, get_review_repository
from app.depends.db_depends import get_db_session
# jwt, авторизация и аутентификация
from app.auth import get_current_user, get_current_buyer
# модели 
from app.models import UserModel

review_api_router = APIRouter(prefix="/api/reviews", tags=['Reviews'])


@review_api_router.get('/', response_model = List[ReviewSchema])
async def get_all_reviews(session : AsyncSession = Depends(get_db_session),
                           repo : ReviewRepository = Depends(get_review_repository)
                           )->List[ReviewSchema]:
    '''Из базы берет все активыне комментарии на все товары.Доступно не авторизированным юзерам'''
    try:
        all_reviews = await repo.get_objects_by_params(session, is_active = True)
        return all_reviews
        
    except Exception as err:
                 raise HTTPException(
            status_code=500,
            detail=str(err))  # общая ошибка 
                 
                 

@review_api_router.post('/', response_model=ReviewSchema)
async def create_review(new_review_info:ReviewCreateSchema,
                        session : AsyncSession = Depends(get_db_session),
                        product_repo : ProductRepository = Depends(get_product_repository),
                        review_repo : ReviewRepository = Depends(get_review_repository),
                        current_user: UserModel = Depends(get_current_buyer)):
        '''эндпоинт по созданию нового отзыва на товар. Доступен только авторизированным покупателям.
        + проверка на существование продукта по id указанного юзером.Включена переоценка общего рейтинга на товар с учетом 
        выставленной юзером оценки в его комменте'''
        try:
            current_product = await product_repo.get_by_params(session, id = new_review_info.product_id, is_active=True)
            if not current_product:
                raise HTTPException(status_code=404, detail=f"Product with id : {new_review_info.product_id} doesn't exist or inactive")
            new_review_data = new_review_info.model_dump()
            new_review_data['user_id'] = current_user.id
            new_review = await review_repo.create(session, new_review_data) # проверка на существование комента по данному продукту вшита внутрь метода
            await session.flush() # что бы метод расчета рейтинга видел добавленный рейтинг нужно в бд изменения отправить до коммита!
            await product_repo.assert_product_rating(session, current_product.id)# переоценка рейтинга на товар
            await session.commit()
            await session.refresh(new_review)
            return new_review
        except Exception as err:
                                     raise HTTPException(
            status_code=500,
            detail=str(err))
                                     
                                     
                                          
@review_api_router.put('/{review_id}', response_model=ReviewSchema)
async def update_review(update_info : ReviewCreateSchema,
                        review_id : int = Path(gt=0),
                        session : AsyncSession = Depends(get_db_session),
                        product_repo : ProductRepository = Depends(get_product_repository),
                        review_repo : ReviewRepository = Depends(get_review_repository),
                        current_user: UserModel = Depends(get_current_buyer))->ReviewSchema:
    '''Эндпоинт на обновление коммента.Коммент может обновлять только аутентифицированный юзер оставивший данный коммент
    с условием что продукт от данного коммента еще сущесвтует и активен'''
    try:

        current_review = await review_repo.get_by_params(session, id = review_id, user_id=current_user.id, is_active=True) # одновременно проверяем что юзер может изменять только свой отзыв
        if not current_review:
            raise HTTPException(status_code=400, detail=f"Review with id : {review_id} doesn't exist or inactive")
        # проверка на существоание продукта, на который оставлен отзыв
        current_product = await product_repo.get_by_params(session, id=current_review.product_id, is_active=True)
        if not current_product:
            raise HTTPException(status_code=400, detail=f"Product with id : {current_review.product_id} for current_review doesn't exist anymore or inactive")
        
        updated_data = update_info.model_dump()
        updated_data['user_id'] = current_user.id
        updated_review = await review_repo.update_put(session, review_id, updated_data)
        # переоценка рейтинга на товар
        await product_repo.assert_product_rating(session, current_product.id)
        await session.commit()
        await session.refresh(updated_review)
        return updated_review
    
    except Exception as err:
            raise HTTPException(
                    status_code=500,
                    detail=str(err))  
                                    

@review_api_router.delete('/{review_id}',  status_code=status.HTTP_200_OK)
async def delete_review(review_id : int = Path(ge=0),
                        session : AsyncSession = Depends(get_db_session),
                        review_repo : ReviewRepository = Depends(get_review_repository),
                        product_repo : ProductRepository = Depends(get_product_repository),
                        current_user: UserModel = Depends(get_current_user)):
    '''эндпоинт на удаление отзыва - доступно админу и аутентифицированному юзеру оставившему этот товар'''
    try:
        # проверка на роль юзера
        if current_user.role not in  ['admin','buyer']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Отзывы разрешено удалять только аутентифицированным покупателям и одменам')  
        # Для админа - без фильтра по user_id, для buyer - с фильтром
        filters = {'id': review_id, 'is_active': True}
        if current_user.role == 'buyer':
            filters['user_id'] = current_user.id

        current_review = await review_repo.get_by_params(session, **filters)
        # Если админ - отзыва нет, если buyer - нет или чужой
        if not current_review:
            raise HTTPException(
                status_code=404 if current_user.role == 'admin' else 403,
                detail='Отзыв не найден или недостаточно прав')
        current_review.is_active = False # мягкое удаление
        # переоценка с учетом неактивного комментария
        await product_repo.assert_product_rating(session, current_review.product_id)
        await session.commit()
        await session.refresh(current_review)
        return {'message' : f"Отзыв с id {review_id} стал неактивен"}
    except Exception as err:
                         raise HTTPException(
            status_code=500,
            detail=str(err))  







