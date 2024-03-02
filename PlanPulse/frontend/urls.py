from django.urls import path
from .views import index

urlpatterns = [
    path("", index),
    path("course", index),
    path("course/create", index),
]
