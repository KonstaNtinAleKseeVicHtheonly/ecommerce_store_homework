from celery import Celery


celery_app = app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://127.0.0.1:6379/0',
    include=['app.tasks.hz_tasks'],
    broker_connection_retry_on_startup=True
)
celery_app.conf.beat_schedule = {
    'run-me-background-task': {
        'task': 'app.tasks.hz_tasks.high_priority_task',
        'schedule': 60.0,
        'args': ('Test text message',)
    }
}

