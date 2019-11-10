from django.db import models

from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q, Count


class ThreadManager(models.Manager):

    def get_or_new(self, user, other_user): # get_or_create
        if user == other_user:
            return None
        lookupByUser = Q(users=user) & Q(users=other_user)
        qs = self.get_queryset().filter(lookupByUser)
        qs = qs.filter(users_count=2)

        if qs.count() == 1:
            return qs.first(), False
        elif qs.count() > 1:
            return qs.order_by('updated_at').first(), False
        else:
            if user != other_user:
                obj = self.model(
                        owner=user,
                    )
                obj.save()
                obj.add_user([other_user, user])
                return obj, True
            return None, False


class Thread(models.Model):
    owner           = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_owner')
    users           = models.ManyToManyField(User, related_name='chat_users')
    users_count     = models.IntegerField(default=0) 
    name            = models.CharField(max_length=200, null=True)
    password        = models.CharField(max_length=50, null=True)
    is_private      = models.BooleanField(default=False)

    updated_at      = models.DateTimeField(auto_now=True)
    created_at      = models.DateTimeField(auto_now_add=True)



    objects      = ThreadManager()


    @property
    def room_group_name(self):
        return f'chat_{self.id}'


    def broadcast(self, msg=None):
        if msg is not None:
            broadcast_msg_to_chat(msg, group_name=self.room_group_name, user='admin')
            return True
        return False


    def thread_list_by_user(self, user):
        return self.objects.filter(users=user)


    def add_user(self, users):
        self.users.add(*users)
        self.users_count = self.users.count()
        self.save()


class ChatMessage(models.Model):
    thread      = models.ForeignKey(Thread, null=True, blank=True, on_delete=models.SET_NULL)
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='sender', on_delete=models.CASCADE)
    message     = models.TextField()
    timestamp   = models.DateTimeField(auto_now_add=True)
