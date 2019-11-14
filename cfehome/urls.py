from django.urls import path, include
import secure.views


urlpatterns = [
    path('login/', secure.views.login, name='secure-login'),
    path('logout/', secure.views.logout, name='secure-logout'),

    path('', include('chat.urls')),

]
