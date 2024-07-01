from rest_framework import serializers
from .models import Inform,InformRead
from apps.oaauth.serializers import UserSerializer,DepartmentSerializer
from apps.oaauth.models import OADepartment

class InformReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformRead
        fields = "__all__"

class InformSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    departments = DepartmentSerializer(read_only=True,many=True)
    # 这是一个包含部门id的列表
    # 如果后端要接收列表就需要ListField
    department_ids = serializers.ListField(write_only=True)
    reads = InformReadSerializer(many=True,read_only=True)
    class Meta:
        model = Inform
        fields = '__all__'
        # exclude = ['public']
        read_only_fields = ('public',)
    
    # 重写保存inform对象的create方法
    def create(self, validated_data):
        # 获取request对象
        request = self.context['request']
        department_ids = validated_data.pop('department_ids')
        # 对列表中的某个值做相同的操作，可以用map方法
        # def toInt(value):
        #     return int(value)
        # map(toInt, department_id)
        department_ids = list(map(lambda value:int(value),department_ids))
        if 0 in department_ids:
            # validated_data是字典，前面加**会变成关键字参数
            inform = Inform.objects.create(public=True,author=request.user, **validated_data)
        else:
            departments = OADepartment.objects.filter(id__in=department_ids).all()
            inform = Inform.objects.create(public=False,author=request.user,**validated_data)
            inform.departments.set(departments)
            inform.save()
        return inform

class ReadInormSerializer(serializers.Serializer):
    inform_pk = serializers.IntegerField(error_messages={"requires":"请传入Inform的ID"}) 
