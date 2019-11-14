from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.edit import FormMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.views.generic import DetailView, ListView

from .forms import ComposeForm
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


@login_required
def threadView(request, username):
    other_user = User.objects.get(username=username)
    threadListByUser = Thread.objects.filter(users=request.user)
    form = ComposeForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            thread, created  =  Thread.objects.get_or_new(request.user, other_user)
            message = form.cleaned_data.get("message")
            ChatMessage.objects.create(user=request.user, thread=thread, message=message)

    allChatmessage = ChatMessage.objects.filter(user)

    context = {

        'threadListByUser': threadListByUser,
        'form': form,

    }
    return render(request, 'chat/thread.html', context)
