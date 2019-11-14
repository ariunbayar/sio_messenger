from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

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
    threadListByUser = Thread.objects.filter(users=request.user)
    context = {
        'threadListByUser': threadListByUser,
    }
    return render(request, 'chat/threadlist.html',context)
