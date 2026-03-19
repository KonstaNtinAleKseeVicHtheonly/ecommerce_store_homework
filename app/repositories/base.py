from sqlalchemy.ext.asyncio import AsyncSession
from app.core.project_logging import project_logger
from typing import List, Any, Dict
#
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





class BaseRepository:
    '''Базовый класс репозиториев с методами общими для отдельных классов репозиториев моделей
    (CRUD операции) (Валидация делается на входе в endpoint через схемы тут в методы только валидные данные поступают)'''
    def __init__(self, model):
        self.model = model
        
    async def get_by_id(self, session : AsyncSession, object_id:int)->object:
            project_logger.info(f"получение объекта с id {object_id} из модели {self.model.__name__}")
            stmt = select(self.model).where(self.model.id == object_id)
            result = await session.execute(stmt)
            current_object =  result.scalar_one_or_none()
            if not current_object:
                project_logger.warning(f"Объект с id {object_id} не найден")
                raise ValueError(f"объект с id {object_id} не найден в модели {self.model.__name__}") 
            return current_object                

    async def object_is_active(self,session:AsyncSession, object_id:int)->bool:
        '''Если у объекта статус активен вернет True Иначе вернет False'''
        if not hasattr(self.model, 'is_active'):
            raise ValueError(f"Нет атрибута is_active в модели {self.model.__name__}")
        current_object = await self.get_by_id(session, object_id)
        if current_object is None:
            raise ValueError(f"объекта с id : {object_id} в модели {self.model.__name__} не существует")
        return current_object.is_active
            
        
    async def get_by_params(self,session:AsyncSession, **filters)->object|None:
        '''ищет строку в табице по заданным параметрам если не находит - вернет None'''
        project_logger.info(f"поиск значения по параметрам {filters} в модели {self.model.__name__}")
        if not filters:
            project_logger.info("пожалуйста введите значения при поиске по параметрам")
            return False
        stmt = select(self.model).filter_by(**filters)
        result = await session.execute(stmt)
        current_object = result.scalar_one_or_none()
        return current_object
    
    async def get_all(self, session: AsyncSession)->List[object]:
        """Получить все записи"""
        stmt = select(self.model)
        result = await session.execute(stmt)
        return result.scalars().all()
            
    async def create(self,session: AsyncSession, data:dict)->object:
        '''создание новоно объекта при post запросе'''

        project_logger.info(f"Создание новго объекта с данными {data} в модели {self.model.__name__}")
        existed_object = await self.get_by_params(session, **data)
        if existed_object:
            project_logger.error(f"объект с парамтетрами {data} уже существуюет в проекте")
            raise ValueError(f"объект с '{data}' уже существует в модели {self.model.__name__}") 
        project_logger.info(f"ПРиступаю к созданию нового объекта в модели {self.model.__name__}")
        new_obj = self.model(**data)
        project_logger.info("объект спешно создан, сделайте комит сессии")
        session.add(new_obj)
        project_logger.info(f"добавили продукт в сессию {data}")
        return new_obj

            
    async def get_objects_by_params(self, session : AsyncSession, **params) -> List[Any]:
        '''по указанным ключам значениями осущесвтляет поиск  объедков в текущей модели'''
        project_logger.info(f"поиск объектов в модели {self.model.__name__} по параметрам {params}")
        if not params:
            project_logger.warning("пожалуйста передайте значение в метод get_objects_by_params")
            return False
        conditions = []
        for field, value in params.items():
            current_column = getattr(self.model, field)
            conditions.append(current_column == value)
        # 3. Создаем запрос
        stmt = select(self.model)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        # 4. Выполняем
        result = await session.execute(stmt)
        return result.scalars().all()  
    
    async def get_objects_for_offset_pagination(self, session:AsyncSession, page:int, page_size:int, **filters)-> Dict[str, Any]:
        '''возвращает объекты с учетом пагинации(страница , количество товаров на странице и критерии поиска) + вернет общее количестов товаров по данным фильрам'''
        
        # 1. Считаем общее количество (для пагинации)
        count_stmt = select(func.count()).select_from(
            select(self.model).filter_by(**filters).subquery()
        )
        total = await session.scalar(count_stmt) or 0
        
        items_stmt = select(self.model).filter_by(**filters).order_by(self.model.id).offset((page - 1)*page_size).limit(page_size)
        #offset - пропустить столько то позиий | limit - взять столько то позиций после пропущенных(offsetом)
        
        items_request = await session.execute(items_stmt)
        items_result = items_request.scalars().all()
        return {'items' : items_result, 'total' : total}
    
    async def get_objects_for_offset_pagination_by_params(self,session:AsyncSession, filters:list, page: int = 1,page_size: int = 10, rank_col=None)->Dict[str, Any]:
        '''принимает параметры пагинаицц (page,page_size),список фильтров для поиска уже сформированных (в эндпоинте) и по ним поиск делает учитывая пагинацию
        возвращает словарь из списка отобранных значений с условимия поиска и пагинации'''
        project_logger.info(f"Начало поиска товаров в модели {self.model.__name__} по запросу юзера, с учетом пагинации страница{page} ")
        # 1. Считаем общее количество элементов по заданным параметрам
        total_stmt = select(func.count()).select_from(self.model).where(*filters)
        total = await session.scalar(total_stmt) or 0 

        # ищем объекты
        #  с учетом ранга поиска(вначале будут товары с наибольшей частотой слова из запроса юзера)
        if rank_col is not None:
            project_logger.info("Адаптирование поиска с учетом ранжирвания")
            items_stmt = (
                    select(self.model)
                    .where(*filters)
                    .order_by(desc(rank_col), self.model.id)
                    .offset((page - 1) * page_size)
                    .limit(page_size)) # срдеи отобранных товаров определяем откуда начать и сколько вывести
            items_request = await session.execute(items_stmt)
            rows = items_request.all()
            items = [item[0] for item in rows]
        else:
            project_logger.info("поиск без ранжирования")
            items_stmt = (
                    select(self.model)
                    .where(*filters)
                    .order_by(self.model.id)
                    .offset((page - 1) * page_size)
                    .limit(page_size)) # срдеи отобранных товаров определяем откуда начать и сколько вывести
            items_request = await session.execute(items_stmt)
            items = items_request.scalars().all()
            
        return {'items': items, 'total' : total}
    
        
    async def delete_by_id(self, session : AsyncSession, object_id:int):
        '''удаление объекта по id'''
        project_logger.info(f"удаление объекта с id {object_id} из модели {self.model.__name__}")
        current_obj = await self.get_by_id(session, object_id)
        if not current_obj:
            raise ValueError(f"объека с  id {object_id} не существует в модели {self.model.__name__}") 
        await session.delete(current_obj)
            
        project_logger.info(f"объект с id {object_id} удален, сделайие коммит сесии")
        return True
    
    async def soft_deleting_by_id(self, session : AsyncSession, object_id:int)->object:
        '''логическое удаление (меняет isactive на False) с оставлением в БД,в случае успешного удаления вернет измененный тип объекта
        (для рефреша в энддпоинте)'''
        project_logger.info(f"Мягкое удаление  объекта с id {object_id} в модели {self.model.__name__}")
        current_obj = await self.get_by_params(session, id = object_id, is_active=True)
        if not current_obj:
            raise ValueError(f"объека с  id {object_id} не существует в модели {self.model.__name__} либо он уже неактивен") 
        current_obj.is_active = False
        project_logger.info(f"Статус объекта с id {object_id} изменен на неактивынй, сделайие коммит сесии")
        return current_obj
        
    async def update_put(self, session: AsyncSession,  object_id:int ,update_data: Dict[str, Any]):
        '''по методу put полностью обновляем строку'''
        project_logger.info(f"НАчало put обновления строки с id {object_id} у модели {self.model.__name__}")
        updated_obj = await self.get_by_id(session, object_id)
        if not updated_obj:
            raise ValueError(f"объекта с id не существует в модели {self.model.__name__}") 
        for field, value in update_data.items():
            if hasattr(updated_obj, field):
                setattr(updated_obj, field, value)
        # # Объект тот же самый, ID тот же # не нужно т.к объект до этого добалвне в сессию и его изменения
        # session.add(updated_obj)
        return updated_obj

        
    async def update_patch(self,session: AsyncSession,  find_by: Dict[str, Any],update_data: Dict[str, Any]):
        '''по методу patch полностью обновляем строку'''
        project_logger.info(f"НАчало put обновления строки с параметрами {find_by} у модели {self.model.__name__}")
        updated_obj = await self.get_by_params(session, **find_by)
        if not updated_obj:
            raise ValueError(f"объекта с параметрами  '{find_by}' не существует в модели {self.model.__name__}") 
        # Перезаписываем ВСЕ поля новыми данными
        for field, value in update_data.items():
            if hasattr(updated_obj, field):
                setattr(updated_obj, field, value)
        # Объект тот же самый, ID тот же
        session.add(updated_obj)
        return updated_obj

