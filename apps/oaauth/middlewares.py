from django.utils.deprecation import MiddlewareMixin
from rest_framework.authentication import get_authorization_header
from rest_framework import exceptions
import jwt
from django.conf import settings
from jwt.exceptions import ExpiredSignatureError
from django.contrib.auth import get_user_model
from django.http.response import JsonResponse
from rest_framework.status import HTTP_403_FORBIDDEN
from django.contrib.auth.models import AnonymousUser

# Return the User model that is active in this project.
OAUser = get_user_model()

class LoginCheckMiddleware(MiddlewareMixin):
    keyword = "JWT"

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.white_list = ['/auth/login/','/auth/register/','/staff/active/']

    # 因为在SessionAuthentication中强制使用CSRF Token。如果未传递有效的CSRF令牌，则会引发403错误。
    # 自定义中间件来禁止CSRF Token验证
    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)

    def process_view(self,request,view_func,view_args,view_kwargs):
        # 1.如果返回None,那么会正常执行（包括执行视图，执行其他中间件的代码
        # 2.如果返回一个HttpResponse对象，那么将不会执行视图，以及后面的中间件的代码
        if request.path in self.white_list or request.path.startswith(settings.MEDIA_URL):
            request.user = AnonymousUser()
            request.auth = None
            return None

        try:
            auth = get_authorization_header(request).split()

            if not auth or auth[0].lower() != self.keyword.lower().encode():
                raise exceptions.ValidationError('请传入JWT')

            if len(auth) == 1:
                msg = "不可用的JWT请求头！"
                raise exceptions.AuthenticationFailed(msg)
            elif len(auth) > 2:
                msg = '不可用的JWT请求头！JWT Token中间不应该有空格！'
                raise exceptions.AuthenticationFailed(msg)

            try:
                jwt_token = auth[1]
                jwt_info = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms='HS256')
                userid = jwt_info.get('userid')
                try:
                    # 绑定当前user到request对象上
                    user = OAUser.objects.get(pk=userid)
                    # 这是个HttpRequest对象，是django内置的
                    request.user = user
                    request.auth = jwt_token
                except:
                    msg = '用户不存在！'
                    raise exceptions.AuthenticationFailed(msg)
            except ExpiredSignatureError:
                msg = "JWT Token已过期！"
                raise exceptions.AuthenticationFailed(msg)
        except Exception as e:
            print(e)
            return JsonResponse(data={"detail":"请先登录"},status=HTTP_403_FORBIDDEN)
        