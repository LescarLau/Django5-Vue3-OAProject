from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'absent'

router = DefaultRouter()
router.register('absent',viewset=views.AbsentViewSet,basename='absent')

urlpatterns = [
    path('absenttype/',view=views.AbsentTypeView.as_view(),name='absenttypes'),
    path('responser/',view=views.ResponserView.as_view(),name='responser')
]+router.urls
