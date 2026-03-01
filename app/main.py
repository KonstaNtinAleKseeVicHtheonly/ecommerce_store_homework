from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.project_logging import project_logger
# роутеры
from app.routers import category_api_router, product_api_router, user_api_router, review_api_router
# кофнигурация БД
from app.core.database import engine




asynccontextmanager
async def startap_event(app:FastAPI):# не забыть передать в параметры наш app
    project_logger.warning("Начало работы приложения")
    yield
    project_logger.warning("🛑 Конец работы приложения") # почему то от уровня warning и выше выводится инфа в треминал, а уровень info не выводится
 
    await engine.dispose()

app = FastAPI(title='Интернет магазин', lifespan=startap_event)

app.include_router(category_api_router)
app.include_router(product_api_router)
app.include_router(user_api_router)
app.include_router(review_api_router)


@app.get('/')
async def root():
    '''Корневой эндпоинт всего проекта'''
    return {'message' : 'Добро пожаловать'}

