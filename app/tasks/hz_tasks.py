from app.core.celery_app import celery_app
from loguru import logger
from app.core.project_logging import project_logger

# logger.add('tasks_info.log')


# создаю очереди и присваиваю им имя
@celery_app.task(queue='high_priority', name='high_priority_task')
def high_priority_task():
    project_logger.info("запущена таска высокого приоритета")
    print("Выполнение задачи высокого приоритета")


@celery_app.task(queue='low_priority', name='low_priority_task')
def low_priority_task():
    project_logger.info("запущена таска низкого приоритета")
    print("Выполнение задачи низкого приоритета")