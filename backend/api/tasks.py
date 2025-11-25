import time
from celery import shared_task


@shared_task
def test():
    time.sleep(5)


@shared_task
def test2():
    print("WOOOOOOOOOOOOOW")