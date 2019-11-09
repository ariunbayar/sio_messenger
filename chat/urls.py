from django.urls import path, re_path
from django.conf.urls import url

from .views import ThreadView, InboxView
from . import views


app_name = 'chat'
urlpatterns = [
    path("", InboxView.as_view()),
    url(r"^(?P<username>[\w.@+-]+)/$", views.ThreadView1, name="ThreadView"),
]
