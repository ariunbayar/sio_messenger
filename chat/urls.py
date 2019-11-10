from django.urls import path, re_path
from django.conf.urls import url

from .views import InboxView
from . import views


app_name = 'chat'
urlpatterns = [
    path("", InboxView.as_view()),
    url(r"^(?P<username>[\w.@+-]+)/$", views.ThreadView, name="ThreadView"),
]
