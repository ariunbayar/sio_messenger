from django.urls import path, include
from django.views.generic import TemplateView
import secure.views


urlpatterns = [
    path('login/', secure.views.login, name='secure-login'),
    path('logout/', secure.views.logout, name='secure-logout'),

    path('', include('chat.urls')),

]
