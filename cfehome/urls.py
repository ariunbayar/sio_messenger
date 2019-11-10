from django.urls import path, include
from django.views.generic import TemplateView
import secure.views


urlpatterns = [
    path('', include('chat.urls')),

    path('login/', secure.views.login, name='secure-login'),
    path('logout/', secure.views.logout, name='secure-logout'),
]
