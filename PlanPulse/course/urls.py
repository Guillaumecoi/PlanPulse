from django.urls import path
from . import views

urlpatterns = [
    path('create', views.CreateCourseView.as_view(), name='create_course'),
]