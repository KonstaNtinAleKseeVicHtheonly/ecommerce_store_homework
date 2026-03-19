from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.project_logging import project_logger
# роутеры
from app.routers import category_api_router, product_api_router, user_api_router, review_api_router, carts_api_router, orders_api_router, payments_api_router
# кофнигурация БД
from app.core.database import engine
# для подгрузки стетических файлов
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware

import time
from datetime import datetime

@asynccontextmanager
async def startap_event(app:FastAPI):# не забыть передать в параметры наш app
    project_logger.warning("Начало работы приложения")
    yield
    project_logger.warning("🛑 Конец работы приложения") # почему то от уровня warning и выше выводится инфа в треминал, а уровень info не выводится
 
    await engine.dispose()

app = FastAPI(title='Интернет магазин', lifespan=startap_event)

app.add_middleware(SessionMiddleware, secret_key="7UzGQS7woBazLUtVQJG39ywOP7J7lkPkB0UmDhMgBR8:")

# @app.task(queue='high_queue')
# def call_background_task(message):
#     time.sleep(10)
#     print("Background Task called!")
#     print(message)
    

# @app.get("/")
# async def hello_world(message: str):
#     call_background_task.delay(message)
#     return {'message': 'Hello World!'}

# @app.middleware('http')
# async def caluclate_request_time(request:Request, call_next):
#             begining = datetime.tzinfo()
#             response = await call_next(request)
            
#             duration = time.time() - begining
#             print(f"Request duration: {duration:.10f} seconds")
app.mount("/media", StaticFiles(directory="media"), name="media") # /media - url для получения фото | directory = media - путь до папки

app.include_router(category_api_router)
app.include_router(product_api_router)
app.include_router(user_api_router)
app.include_router(review_api_router)
app.include_router(carts_api_router)
app.include_router(orders_api_router)
app.include_router(payments_api_router)



@app.get('/')
async def root():
    '''Корневой эндпоинт всего проекта'''
    return {'message' : 'Добро пожаловать'}


