from celery_app import celery  # Import your Celery instance
import logging
import json
from utils import send_email  # Your email sending function
import redis  # Import the redis module

# Initialize Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Queue email task
@celery.task
def queue_email(to_email, subject, content):
    # Add email data to Redis or any other queue
    redis_client.lpush('email_queue', json.dumps({
        'to_email': to_email,
        'subject': subject,
        'content': content
    }))
    logging.info(f"Queued email for {to_email}")

# Function to manually send all queued emails
@celery.task
def send_queued_emails():
    logging.info("send_queued_emails task triggered")
    while True:
        email_data_json = redis_client.rpop('email_queue')  # Get email data from the queue
        if not email_data_json:
            break  # Exit loop if there are no emails left

        email_data = json.loads(email_data_json)
        result = send_email(email_data['to_email'], email_data['subject'], email_data['content'])
        logging.info(f"Sent email to {email_data['to_email']}: {result}")