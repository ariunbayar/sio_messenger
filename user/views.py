from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render


@login_required
def searchables(request):

    user_values = get_user_model().objects.all().order_by('username').values_list('pk', 'username')

    searchables = [(pk, username) for pk, username in user_values]

    rsp = {'searchables': searchables}

    return JsonResponse(rsp)
