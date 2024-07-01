from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from apps.oaauth.models import OADepartment,UserStatusChoice
from apps.oaauth.serializers import DepartmentSerializer
from .serializers import AddStaffSerializer,ActiveStaffSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from utils import aeser
from django.urls import reverse
from oaback.celery import debug_task
from .tasks import send_mail_task
from django.views import View
from django.shortcuts import render
from django.http.response import JsonResponse
from urllib import parse

OAUser = get_user_model()
aes = aeser.AESCipher(settings.SECRET_KEY)

class DepartmentListView(ListAPIView):
    queryset = OADepartment.objects.all()
    serializer_class = DepartmentSerializer

# 激活员工过程
# 1.员工点击激活邮件，我们视图中可以获取到token
# 2.返回一个含有表单的登录模板，在用户在提交表单之前先存储到cookie中
# 3.校验用户上传的邮箱和密码是否正确，并且解密token中的邮箱，与用户提交的邮箱进行对比
class ActiveStaffViews(View):
    def get(self,request):
        # 获取token，并把token存储在cookie中，方面下次用户传过来
        # 针对特殊字符需要进行转码
        token = request.GET.get('token')
        response = render(request,'active.html')
        response.set_cookie('token',token)
        return response
    
    def post(self,request):
        try:
            # 获取token
            token = request.COOKIES.get('token')
            print("lesce"+token)
            email = aes.decrypt(token)
            # 这里继承的是django里的View获取表单数据使用的是.POST
            serilizer = ActiveStaffSerializer(data=request.POST)
            if serilizer.is_valid():
                email_valid = serilizer.validated_data.get('email')
                user = serilizer.validated_data.get('user')
                if email != email_valid:
                    return JsonResponse({'code':400,'message':'邮箱错误'})
                else:
                    user.status = UserStatusChoice.ACTIVED
                    user.save()
                    return JsonResponse({'code':200,"message":'激活成功'})
            else:
                detail = list(serilizer.errors.values())[0][0]
                return JsonResponse({"code":400,"message":detail})
        except Exception as e:
            print(e)
            return JsonResponse({'code':400,'message':'token错误'})

class StaffView(APIView):
    # 获取员工表
    def get(self,request):
        pass

    # 创建新用户
    def post(self,request):
        # 如果用的是试图集，那么视图集会自动把request放到serializer的context里面
        serializer = AddStaffSerializer(data=request.data,context={'request':request})
        if serializer.is_valid():
            email = serializer.validated_data['email']
            realname = serializer.validated_data['realname']
            password = serializer.validated_data['password']

            # user = OAUser.objects.create(email=email,realname=realname)
            # user.set_password(password)
            # user.save()
            # 1.保存用户数据
            user = OAUser.objects.create_user(email=email,realname=realname,password=password)
            department = request.user.department
            user.department = department
            user.save()

            # 发送一个链接，让用户点击这个链接后跳转到激活的界面
            # 为了区分用户，在发送链接中，该链接中应该包含这个用户的 邮件
            # 针对邮件进行加密，AES
            # send_mail(f'【OA系统】账号激活',recipient_list=[email],message='测试',from_email=settings.DEFAULT_FROM_EMAIL)

            # 2.发送邮件激活
            self.send_active_email(email)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(data={'detail':list(serializer.errors.values())[0][0]},status=status.HTTP_400_BAD_REQUEST)

    def send_active_email(self,email):
        token = aes.encrypt(email)
        # 在这对token进行编码
        active_path = reverse("staff:active")+"?"+parse.urlencode({'token':token})
        active_url = self.request.build_absolute_uri(active_path)
        message = f"请点击以下链接激活账号：{active_url}"
        subject = f'【OA系统】账号激活'
        # send_mail(f'【OA系统】账号激活',recipient_list=[email],message=message,from_email=settings.DEFAULT_FROM_EMAIL)
        send_mail_task.delay(email,subject,message)

class TestCelery(APIView):
    def get(self,request):
        # 用celery异步执行debug_task
        debug_task.delay()
        return Response({'detail':'成功'})
