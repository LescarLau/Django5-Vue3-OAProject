from django.shortcuts import render
from rest_framework import viewsets,mixins
from .models import AbsentType,Absent,AbsentChoices
from .serializers import AbsentSerializer,AbsentTypeSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from .utils import get_responser
from apps.oaauth.serializers import UserSerializer
from rest_framework.settings import api_settings


# Create your views here.
# 1.发起考勤（create
# 2.处理考勤（update
# 3.查看自己考勤列表（list?who=my
# 4.查看下属考勤列表（list?who=sub

class AbsentViewSet(mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Absent.objects.all()
    serializer_class = AbsentSerializer

    def update(self, request, *args, **kwargs):
        # 默认情况下，如果要修改某一条数据，那么要把这个数据的序列化中指定的所有字段都要传
        # 如果只需要修改一部分数据，可以这样设置
        kwargs['partial'] = True
        return super().update(request,*args,**kwargs)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        who = request.query_params.get('who')
        if who and who == 'sub':
            result = queryset.filter(responser=request.user)
        else:
            result = queryset.filter(requester=request.user)
        # result代表符合要求的数据
        # paginate_queryset会做分页逻辑
        page = self.paginate_queryset(result)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # get_paginated_response除了返回序列化后的数据外，还会返回总数据是多少
            return self.get_paginated_response(serializer.data)
        
        serializer = self.serializer_class(result,many=True)
        return Response(data=serializer.data)

# 请假类型
class AbsentTypeView(APIView):
    def get(self,request):
        types = AbsentType.objects.all()
        serializer = AbsentTypeSerializer(types,many=True)
        return Response(data=serializer.data)

# 显示审批者
class ResponserView(APIView):
    def get(self,request):
        responser = get_responser(request)
        # 如果序列化为none，会返回一个包含除了主键外的空字典
        serializer = UserSerializer(responser)
        return Response(data=serializer.data)