from django.urls import path
from . import views

urlpatterns = [
    path('upload/',views.UploadImageView.as_view(),name='upload'),
]
