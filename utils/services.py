from . import messages
from django.core.mail import send_mail as send
import threading
from utils.exceptions import NetworkException
import logging

logger = logging.getLogger(__name__)

def handle_timeout(thread):
    pass

def set_timeout(duration, func, timeout_message, *args, **kwargs):
    slave = threading.Thread(target=func, args=args, kwargs=kwargs)
    slave.start()
    slave.join(duration)
    if slave.is_alive():
        logger.log(level=logging.WARNING, msg=timeout_message)
        handle_timeout(slave)
        raise NetworkException()

def timeout(duration: int, timeout_message=messages.TIME_OUT):
    def outer(func):
        def inner(*args, **kwargs):
            thread_kwargs = {
                **kwargs,
                'duration': duration,
                'func': func,
                'timeout_message': timeout_message
            }
            thread = threading.Thread(
                target=set_timeout,
                args=args,
                kwargs=thread_kwargs
            )
            thread.start()
            return thread
        return inner
    return outer

# @timeout(60, messages.SEND_MAIL_TIME_OUT)
def send_mail(subject,message,recipient_list,*args,**kwargs):
    return send(
        *args,
        subject=subject,
        message=message,
        recipient_list=recipient_list,
        **kwargs
    )
