from django.urls import path
from .views import index

accounturlpatterns = [
    path("register", index),
    path("login", index),
    path("profile", index),
    path("logout", index),
]

courseurlpatterns = [
    path("course", index),
    path("course/create", index),
]

urlpatterns = [
    path("", index),
] + accounturlpatterns + courseurlpatterns