from django.urls import path
from . import views

app_name = 'oaauth'

urlpatterns = [
    path('login/',views.loginView.as_view(),name='login'),
    path('resetpwd/',views.ResetPwdView.as_view(),name='resetpwd')
]
