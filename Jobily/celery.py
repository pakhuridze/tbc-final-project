import os
from celery import Celery

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Jobily.settings')

# Create celery app
app = Celery('Jobily')

# Config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')