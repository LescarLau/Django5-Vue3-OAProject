import os
from celery import Celery
from celery.signals import after_setup_logger
import logging

# 设置django的settings模块，celery会读取这个模块中的配置信息
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oaback.settings')

app = Celery('oaback')

## 日志管理
@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add filehandler
    fh = logging.FileHandler('logs.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

# 配置从settins.py中读取celery配置信息，所有Celery配置信息都要以CELERY_开头
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务，任务可以写在apps/tasks.py中
app.autodiscover_tasks()

# 测试任务
# 1.bind=True,在任务函数中第一个参数就是任务对象task，如果没有这个参数或者为false，那么任务函数中就不会又任务对象参数
# 2.ignore_result=True,不会保存任务结果
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')