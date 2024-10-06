from celery import Celery
import os
import logging

# Set default Flask app settings
os.environ.setdefault('FLASK_APP', 'app.py')

# Create Celery instance
celery = Celery('tasks', broker='redis://localhost:6379/0')

# Load any config from Flask if needed
celery.conf.update(result_backend='redis://localhost:6379/0')

# Automatically discover tasks in the tasks module
celery.autodiscover_tasks(['tasks'])

# Periodic task setup
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    logging.info("Setting up periodic tasks...")
    # Schedule the send_queued_emails task
    sender.add_periodic_task(60.0, celery.signature('tasks.send_queued_emails'), name='Send queued emails every minute')