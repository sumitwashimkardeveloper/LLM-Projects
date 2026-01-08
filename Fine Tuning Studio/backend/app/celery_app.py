from celery import Celery
import os

app = Celery(__name__)
app.conf.broker_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
app.conf.result_backend = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
app.conf.task_serializer = 'json'
app.conf.accept_content = ['json']
app.conf.result_serializer = 'json'
app.conf.timezone = 'UTC'
app.conf.enable_utc = True
