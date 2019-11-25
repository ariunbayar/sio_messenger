from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

import secure.views


urlpatterns = [
    path('login/', secure.views.login, name='secure-login'),
    path('logout/', secure.views.logout, name='secure-logout'),

    path('', include('chat.urls')),
    path('user/', include('user.urls')),

]

if settings.DEBUG == True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
