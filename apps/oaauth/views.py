from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import loginSerializer, UserSerializer
from datetime import datetime
from .authentications import generate_jwt
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ResetPwdSerializer
from rest_framework import status

# Create your views here.
class loginView(APIView):
    # 这个request是drf封装的，针对django的HttpRequest对象进行了封装
    def post(self,request):
        # 验证是否可用
        # loginSerializer的祖先类为BaseSerializer,In particular, if a `data=` argument is passed then:.is_valid() - Available.
        serializer = loginSerializer(data=request.data)
        if serializer.is_valid():
            print("lescar" , serializer.validated_data.get('user'))
            # 保存数据,validated_data 是个字典，做拆包处理，当前返回的attrs为attrs['user'] = user，validate函数返回值会传给validated_data
            # 因此当前user为OAUser中其中一个
            user = serializer.validated_data.get('user')
            user.last_login = datetime.now()
            user.save()
            # 生成token
            token = generate_jwt(user)
            # 最后调用UserSerializer对user进行序列化，并返回其data
            return Response({'token':token,'user':UserSerializer(user).data})
        else:
            # print(serializer.errors)
            detail = list(serializer.errors.values())[0][0]
            # drf在相应是非200时，他的相应参数名为detail，所以我们这里也叫detail
            return Response({'detail':detail},status=status.HTTP_400_BAD_REQUEST)


class ResetPwdView(APIView):
    def post(self,request):
        serializer = ResetPwdSerializer(data=request.data,context={'request':request})
        # return Response({'message':'success'})
        if serializer.is_valid():
            pwd1 = serializer.validated_data.get('pwd1')
            request.user.set_password(pwd1)
            request.user.save()
            return Response({"status":"sucess"})
        else:
            print(serializer.errors)
            detail = list(serializer.errors.values())[0][0]
            return Response({"detail":detail},status=status.HTTP_400_BAD_REQUEST)