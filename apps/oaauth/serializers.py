from rest_framework import serializers
from .models import OAUser,UserStatusChoice,OADepartment
from rest_framework import exceptions

class loginSerializer(serializers.Serializer):
    # 定义这两个变量是为了接收post后传入的email和password
    email = serializers.EmailField(required = True)
    password = serializers.CharField(max_length=20,min_length = 6)
    # 在view.py中serializer.is_valide()调用后调用该validate函数，其中传入的data会赋值给attrs
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = OAUser.objects.filter(email=email).first()
            if not user:
                raise serializers.ValidationError('请输入正确的邮箱')
            if not user.check_password(password):
                raise serializers.ValidationError('请输入正确的密码')
            # 判断是否激活
            if user.status != UserStatusChoice.ACTIVED:
                raise serializers.ValidationError("该用户未激活或被锁定,请联系管理员") 
            # 为了节省查询SQL的次数,这里把user放到attrs中,方便再视图中使用
            attrs['user'] = user
        else:
            raise serializers.ValidationError('请输入邮箱和密码')
        return attrs
    
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OADepartment
        fields = "__all__"
    
class UserSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer()
    class Meta:
        model = OAUser
        # fields = "__all__"
        exclude = ('password','groups','user_permissions')

class ResetPwdSerializer(serializers.Serializer):
    oldPwd = serializers.CharField(min_length=6,max_length=20)
    pwd1 = serializers.CharField(min_length=6,max_length=20)
    pwd2 = serializers.CharField(min_length=6,max_length=20)

    def validate(self, attrs):
        oldPwd = attrs['oldPwd']
        pwd1 = attrs['pwd1']
        pwd2 = attrs['pwd2']

        user = self.context['request'].user
        if not user.check_password(oldPwd):
            raise exceptions.ValidationError("旧密码错误")
        
        if pwd1 != pwd2:
            raise exceptions.ValidationError("两个密码不一致")
        
        return attrs