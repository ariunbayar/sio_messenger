from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.edit import FormMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.views.generic import DetailView, ListView

from .forms import ComposeForm
from .models import Thread, ChatMessage


class InboxView(LoginRequiredMixin, ListView):
    template_name = 'chat/inbox.html'
    def get_queryset(self):
        return Thread.objects.filter(users=self.request.user)

@login_required
def ThreadView1(request, username):
    other_user = User.objects.get(username=username)
    threadListByUser = Thread.objects.filter(users=request.user)
    form = ComposeForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            thread, created  =  Thread.objects.get_or_new(request.user, other_user)
            message = form.cleaned_data.get("message")
            ChatMessage.objects.create(user=request.user, thread=thread, message=message)    

    context = {

        'threadListByUser': threadListByUser,
        'form': form,

    }
    return render(request, 'chat/thread.html', context)

