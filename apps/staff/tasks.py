from django.core.mail import send_mail
from django.conf import settings
from oaback import celery_app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@celery_app.task(name='send_mail_task')
def send_mail_task(email, subject, message):
    logger.info("Sending mail to %s" % email)
    print(email)
    send_mail(subject, message, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[email])
