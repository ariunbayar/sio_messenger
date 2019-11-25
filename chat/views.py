from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from .models import Thread, ChatMessage


@login_required
def thread_messages(request, thread_id):

    qs = ChatMessage.objects.filter(thread_id=thread_id)
    values = qs.values_list('thread_id', 'message', 'timestamp', 'user__username')

    thread_messages = []
    for thread_id, message, timestamp, username in values:
        thread_messages.append({
                'thread_id': thread_id,
                'message': message,
                'timestamp': int(timestamp.timestamp()),
                'username': username,
            })

    data = {
        'thread_messages': thread_messages,
    }

    return JsonResponse(data)


@login_required
def threadlist(request):

    threadListByUser = Thread.objects.threads_by_user(request.user, prefetch_exclude_user=request.user)

    user_qs = get_user_model().objects.exclude(pk=request.user.pk)
    user_details = user_qs.order_by('username').values_list('pk', 'first_name', 'last_name', 'username', 'profile__image', named=True)

    context = {
        'threadListByUser': threadListByUser,
        'user_details': user_details,
    }
    return render(request, 'chat/threadlist.html', context)
