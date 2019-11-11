from django.urls import path, re_path
from django.conf.urls import url

from . import views

urlpatterns = [
    path("", views.threadlist, name="threadlist"),
    path("thread_messages/<int:thread_id>/", views.thread_messages, name="thread-messages"),
]
