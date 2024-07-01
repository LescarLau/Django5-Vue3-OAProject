from rest_framework.views import APIView
from .serilaizers import UploadImageSerializer
from rest_framework.response import Response
from shortuuid import uuid
import os
from django.conf import settings

class UploadImageView(APIView):
    def post(self,request):
        # 1.校验是否为图片文件
        # 2. png jpg jpeg 
        serilaizer = UploadImageSerializer(data=request.data)
        if serilaizer.is_valid():
            file = serilaizer.validated_data.get('image')
            filename = uuid() + os.path.splitext(file.name)[-1]
            path = settings.MEDIA_ROOT / filename
            try:
                with open(path,'wb') as fp:
                    for chunk in file.chunks():
                        fp.write(chunk)
            except Exception as e:
                # 这个失败的信息是根据wang富文本插件的文档格式来写的
                return Response({
                    "errno":1,
                    "message":"图片保存失败"+e,
                })
            # abc.png => /media/abc.png
            file_url = settings.MEDIA_URL + filename
            return Response({
                "errno":0,
                "data":{
                    "url":file_url,
                    "alt":"",
                    "href":file_url,
                }
            })
        else:
            print(serilaizer.errors)
            return Response({
                "errno":1,
                "message":list(serilaizer.errors.values())[0][0]
            })
