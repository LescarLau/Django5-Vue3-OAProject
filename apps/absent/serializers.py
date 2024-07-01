from rest_framework import serializers
from .models import Absent,AbsentType,AbsentChoices
from apps.oaauth.serializers import UserSerializer
from rest_framework import exceptions
from .utils import get_responser


class AbsentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbsentType
        fields = "__all__"

class AbsentSerializer(serializers.ModelSerializer):
    # read_only:这个参数，只会将ORM模型序列化成字典时将这个字段序列化
    # write_only:这个参数，只会将data进行校验时才会用到
    absent_type = AbsentTypeSerializer(read_only=True)
    absent_type_id = serializers.IntegerField(write_only=True)
    requester = UserSerializer(read_only=True)
    responser = UserSerializer(read_only=True)
    class Meta:
        model = Absent
        fields = "__all__"

    # 验证absent_tyoe_id是否在当前数据库
    def validate_absent_type_id(self, value):
        if not AbsentType.objects.filter(pk=value).exists():
            raise exceptions.ValidationError("考勤类型不存在")
        return value

    # create
    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        # 获取审批者
        # 判断如果时部门leader
        # if user.department.leader.uid == user.uid:
        #     if user.department.name == '董事会':
        #         responser = None
        #     else:
        #         responser = user.department.manager
        # else:
        #     responser = user.department.leader
        responser = get_responser(request)
        # 如果时董事会，直接通过
        if responser is None:
            validated_data['status'] = AbsentChoices.PASS
        else:
            validated_data['status'] = AbsentChoices.AUDITING
        absent = Absent.objects.create(**validated_data,requester=user,responser=responser)
        return absent

    # update
    def update(self, instance, validated_data):
        if instance.status != AbsentChoices.AUDITING:
            raise exceptions.APIException(detail='不能修改已经确定的请假数据')
        request = self.context['request']
        user = request.user
        if instance.responser.uid != user.uid:
            raise exceptions.APIException(detail='您无权处理该考勤')
        instance.status = validated_data['status']
        instance.response_content = validated_data['response_content']
        instance.save()
        return instance