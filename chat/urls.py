from django.urls import path, re_path
from django.conf.urls import url

from .views import ThreadView, InboxView

app_name = 'chat'
urlpatterns = [
    path("", InboxView.as_view()),
    url(r"^(?P<username>[\w.@+-]+)/$", ThreadView.as_view()),
]
