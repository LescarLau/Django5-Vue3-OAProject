from django.db import models
from apps.oaauth.models import OAUser,OADepartment

class Inform(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    # 如果前端上传的department_id中包含了0，那么认为这个通知是所有部门可见的
    public = models.BooleanField(default=False)
    author = models.ForeignKey(OAUser,on_delete=models.CASCADE,related_name='informs',related_query_name='informs')
    # departments序列化的时候使用，前端上传部门id，外面通过department_ids来获取
    departments = models.ManyToManyField(OADepartment,related_name='informs',related_query_name='informs')

    class Meta:
        ordering = ('-create_time',)

class InformRead(models.Model):
    inform = models.ForeignKey(Inform,on_delete=models.CASCADE,related_name='reads',related_query_name='reads')
    user = models.ForeignKey(OAUser,on_delete=models.CASCADE,related_name='reads',related_query_name='reads')
    read_time = models.DateField(auto_now_add=True)

    class Meta:
        # inform和user的组合必须是唯一的
        unique_together = ('inform','user')