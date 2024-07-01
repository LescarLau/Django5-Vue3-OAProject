from rest_framework import serializers
from django.contrib.auth import get_user_model

OAUser = get_user_model()

class AddStaffSerializer(serializers.Serializer):
    realname = serializers.CharField(max_length=20,error_messages={"required":"请输入用户名"})
    email = serializers.EmailField(error_messages={"required":"请输入邮箱","invalid":"请输入正确格式的邮箱"})
    password = serializers.CharField(max_length=20,error_messages={"required":"请输入密码"})

    def validate(self, attrs):
        request = self.context['request']
        email = attrs.get('email')
        # 1.验证邮箱是否存在
        if OAUser.objects.filter(email=email).exists():
            raise serializers.ValidationError("该邮箱已存在")
        
        # 2.盐城当前用户是否是部门leader
        if request.user.department.leader.uid != request.user.uid:
            raise serializers.ValidationError("非部门leader不能添加员工")
        return attrs
    
class ActiveStaffSerializer(serializers.Serializer):
    email = serializers.EmailField(error_messages={"required":"请输入邮箱","invalid":"请输入正确格式的邮箱"})
    password = serializers.CharField(max_length=20,error_messages={"required":"请输入密码"})

    def validate(self, attrs):
        email = attrs['email']
        password = attrs['password']
        user = OAUser.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            raise serializers.ValidationError("邮箱或密码错误")
        attrs['user'] = user
        return attrs