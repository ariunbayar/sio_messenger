from django.urls import path

from . import views


urlpatterns = [
    path("searchables/", views.searchables, name="user-searchables"),
]
