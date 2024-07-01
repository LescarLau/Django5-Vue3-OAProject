from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path

app_name = 'inform'

router = DefaultRouter()
router.register('inform',views.InformViewSet,basename='inform')

urlpatterns = [
    path('inform/read/',view=views.ReadInformView.as_view(),name='informread'),
]+router.urls
