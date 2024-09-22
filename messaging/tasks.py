from celery import shared_task
from django.core.mail import send_mail

import logging

logger = logging.getLogger("Django Starter Project")


@shared_task(name="Send General Email")
def send_general_email(to, subject, message):
    logger.info(to)
    logger.info(subject)
    logger.info(message)
    print(message)
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email="Django Starter Project <hello@support.djangostarterproject.com>",
            recipient_list=[to],
            fail_silently=True,
        )
        return True
    except Exception:
        return False
