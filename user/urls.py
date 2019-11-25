from django.urls import path

from . import views


urlpatterns = [
    path("searchables/", views.searchables, name="user-searchables"),
    path("profile/", views.profile, name="user-profile"),
]
