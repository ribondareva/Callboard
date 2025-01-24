from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab


# Устанавливаем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Используем строку для конфигурации Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач в приложениях Django
app.autodiscover_tasks(['board'])
# Настройка расписания задач

# Настройка повторных подключений при старте
app.conf.broker_connection_retry_on_startup = True

app.conf.beat_schedule = {
    'send-daily-newsletter': {
        'task': 'board.tasks.send_daily_newsletter',
        'schedule': crontab(minute=30, hour=8),
        'args': (),
    },
}