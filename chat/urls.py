from django.urls import path, re_path
from django.conf.urls import url

from . import views


app_name = 'chat'
urlpatterns = [
    path("", views.threadlist, name="threadlist"),
]
