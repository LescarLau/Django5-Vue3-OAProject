from django.db import models
from django.contrib.auth import get_user_model

OAUser = get_user_model()

class AbsentChoices(models.IntegerChoices):
    # 审批中
    AUDITING = 1
    # 通过
    PASS = 2
    # 拒绝
    REJECT = 3

class AbsentType(models.Model):
    name = models.CharField(max_length=100)
    create_time = models.DateField(auto_now_add=True)

class Absent(models.Model):
    # 标题
    title = models.CharField(max_length=200)
    # 请假内容
    content = models.TextField()
    # 请假类型
    absent_type = models.ForeignKey(AbsentType,on_delete=models.CASCADE,related_name='absents',related_query_name="absents")
    # 请假发起人
    requester = models.ForeignKey(OAUser,on_delete=models.CASCADE,related_name='my_absents',related_query_name='my_absents')
    # 审批人(可为空):当在一个模型中，有多个字段对同一个模型引用了外键，必须指定related_name为不同的值
    responser = models.ForeignKey(OAUser,on_delete=models.CASCADE,related_name='sub_absents',related_query_name='sub_absents',null=True)
    # 状态
    status = models.IntegerField(choices=AbsentChoices,default=AbsentChoices.AUDITING)
    # 请假开始时间
    start_date = models.DateField()
    # 请假结束时间
    end_date = models.DateField()
    # 请假发起时间
    create_time = models.DateTimeField(auto_now_add=True)
    # 审批回复内容
    response_content = models.TextField(blank=True)

    class Meta:
        ordering = ('-create_time',)

