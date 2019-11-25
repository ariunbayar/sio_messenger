from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect

from .models import Profile
from .forms import ProfileForm


@login_required
def searchables(request):

    user_values = get_user_model().objects.all().order_by('username').values_list('pk', 'username')

    searchables = [(pk, username) for pk, username in user_values]

    rsp = {'searchables': searchables}

    return JsonResponse(rsp)


@login_required
def profile(request):

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile()
        profile.user = request.user

    values = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }

    if request.method == 'POST':
        form = ProfileForm(profile, request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data.get('image'):
                profile.image = request.FILES.get('image')
                profile.save()
            request.user.last_name = form.cleaned_data.get('last_name')
            request.user.first_name = form.cleaned_data.get('first_name')
            request.user.email = form.cleaned_data.get('email')
            request.user.save()
            return redirect('user-profile')
    else:
        form = ProfileForm(profile, initial=values)

    context = {
            'user': request.user,
            'profile': profile,
            'form': form,
        }
    return render(request, 'user/profile.html', context)
