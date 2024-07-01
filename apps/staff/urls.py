from django.urls import path
from . import views

app_name='staff'

urlpatterns = [
    path('department/',views.DepartmentListView.as_view(),name='department'),
    path('staff/',views.StaffView.as_view(),name='staff'),
    path('active/',views.ActiveStaffViews.as_view(),name='active'),
    path('test/',views.TestCelery.as_view(),name='test'),
]
