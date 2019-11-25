from django.db import models

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django.db.models import Q


class ThreadManager(models.Manager):

    def get_or_new(self, user, other_user): # get_or_create
        if user == other_user:
            return None, False
        lookupByUser = Q(users=user) & Q(users=other_user)
        qs = self.get_queryset().filter(lookupByUser)
        qs = qs.filter(users_count=2)

        if qs.count() == 1:
            return qs.first(), False
        elif qs.count() > 1:
            return qs.order_by('updated_at').first(), False
        else:
            obj = self.model(
                    owner=user,
                )
            obj.save()
            obj.name = str(obj.pk)  # XXX for debugging purposes only
            obj.add_user([other_user, user])
            return obj, True

    def threads_by_user(self, user, prefetch_exclude_user=None):
        qs = self.get_queryset().filter(users=user)
        if prefetch_exclude_user:
            qs_user_excluded = get_user_model().objects.exclude(pk=prefetch_exclude_user.pk)
            qs = qs.prefetch_related(Prefetch('users', queryset=qs_user_excluded))
        return qs


class Thread(models.Model):
    owner           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_owner')
    users           = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_users')
    users_count     = models.IntegerField(default=0)
    name            = models.CharField(max_length=200, null=True)
    password        = models.CharField(max_length=50, null=True)
    is_private      = models.BooleanField(default=False)

    updated_at      = models.DateTimeField(auto_now=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    objects      = ThreadManager()

    def add_user(self, users):
        self.users.add(*users)
        self.users_count = self.users.count()
        self.save()

    def get_chat_room_name(self):
        return "thread_{}".format(self.id)


class ChatMessage(models.Model):
    thread      = models.ForeignKey(Thread, null=True, blank=True, on_delete=models.SET_NULL)
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='sender', on_delete=models.CASCADE)
    message     = models.TextField()
    filename    = models.FileField(upload_to='%Y/%m/%d/', null=True)
    timestamp   = models.DateTimeField(auto_now_add=True)


class UserChannel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Length is 30, according to channel_redis.core.RedisChannelLayer.new_channel
    # 64 = 30 + 34. We reserved 34 char for later use.
    channel_name = models.CharField(max_length=64, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
