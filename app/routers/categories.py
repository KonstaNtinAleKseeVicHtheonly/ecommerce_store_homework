from app.core.project_logging import project_logger
from fastapi import APIRouter, Body, Path, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
#схемы
from app.schemas.categories_schemas import CategorySchena, CategoryCreateSchema
# depends
from fastapi import Depends
from app.depends.db_depends import get_db_session
from app.depends.repository_depends import get_category_repository
#репозитории
from app.repositories import CategoryRepository

category_api_router = APIRouter(prefix="/api/categories", tags=['Product_categories'])


@category_api_router.get('/', response_model=List[CategorySchena])
async def get_all_categories(session : AsyncSession = Depends(get_db_session),
                             repo:CategoryRepository = Depends(get_category_repository)):
    '''из базы берет все доступные категории'''
    try:
        
        all_categories = await repo.get_objects_by_params(session, is_active = True)
        return all_categories
    except Exception as err:
         raise HTTPException(
            status_code=500,
            detail=str(err))  # общая ошибка 

@category_api_router.get('/{category_id}', response_model=CategorySchena)
async def get_current_category(category_id : int = Path(ge=1), 
                               session : AsyncSession = Depends(get_db_session),
                               repo : CategoryRepository = Depends(get_category_repository)):
    '''вывод категории по id'''
    try:
        current_category = await repo.get_by_id(session, category_id)
        return current_category
    except ValueError as err:
                 raise HTTPException(
            status_code=400,
            detail=str(err)  
        )
    except Exception as err:
         raise HTTPException(
            status_code=500,
            detail=str(err)  # общая ошибка 
        )




@category_api_router.post('/', response_model=CategorySchena)
async def create_category(new_category_info : CategoryCreateSchema, 
                          session : AsyncSession= Depends(get_db_session), 
                          repo:CategoryRepository= Depends(get_category_repository)):
    try:
        # Проверка существования parent_id, если указан
        if new_category_info.parent_id is not None:
            parent = await repo.get_by_params(session, id = new_category_info.parent_id, is_active = True)
            if parent is None: # значит нет в базе родителя по id указанного в запросе
                raise HTTPException(status_code=400, detail="Parent category not found")
        # процесс создания новой категории
        new_category = await repo.create(session, new_category_info.model_dump())
        await session.commit()
        await session.refresh(new_category)
        return new_category
    except ValueError as err:
         raise HTTPException(
            status_code=400,
            detail=str(err)  # "Категория 'Test' уже существует"
        )
    except Exception as err:
         raise HTTPException(
            status_code=500,
            detail=str(err)  # общая ошибка 
        )



@category_api_router.put('/{category_id}', response_model=CategorySchena)
async def update_category(update_data : CategoryCreateSchema,
                          category_id : int = Path(ge=0), 
                          session : AsyncSession = Depends(get_db_session),
                          repo:CategoryRepository = Depends(get_category_repository)):
    try:
        #проверямем наличие и валидность родительского id категории
        if update_data.parent_id is not None:
            parent = await repo.get_by_params(session, id = update_data.parent_id, is_active = True)
            if parent is None:
                raise HTTPException(status_code=400, detail="Parent category not found") 
        updated_result = await repo.update_put(session,category_id, update_data.model_dump())
        await session.commit()
        await session.refresh(updated_result)
        return updated_result
        
    except HTTPException as err:
        raise HTTPException(
                status_code=400,
                detail=str(err)  # неверный id родителя 
            )
    except Exception as err:
            raise HTTPException(
                status_code=500,
                detail=str(err)  # общая ошибка 
            )

@category_api_router.delete('/{category_id}', status_code=status.HTTP_200_OK)
async def delete_category(category_id : int = Path(ge=0), 
                          session : AsyncSession = Depends(get_db_session),
                          repo:CategoryRepository = Depends(get_category_repository)):
    try:
        # логика мягкого удаления
        changed_category = await repo.soft_deleting_by_id(session, category_id)
        await session.commit()
        await session.refresh(changed_category)
        return {"message" : f"Категория  с id {category_id} стала неактивна"}
    except Exception as err:
         raise HTTPException(
            status_code=500,
            detail=str(err)  # общая ошибка 
        )
