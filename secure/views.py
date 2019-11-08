from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET
from django.conf import settings


@csrf_protect
def login(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = auth.authenticate(request, username=username, password=password)
            if user:  # Login is success
                auth.login(request, user)

                if request.GET:
                    return redirect(request.GET.get('next'))
                else:
                    return redirect(settings.LOGIN_REDIRECT_URL)
            else:
                # login fails
                context['error'] = 'Нэвтрэх нэр, нууц үг буруу байна'
        else:
            context['error'] = 'Нэвтрэх нэр, нууц үгээ оруулна уу'
        context['username'] = username
    return render(request, 'secure/login.html', context)


@require_GET
@login_required
def logout(request):
    auth.logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)
