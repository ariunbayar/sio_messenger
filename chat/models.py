from django.db import models

from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q


class ThreadManager(models.Manager):
    def by_user(self, user):
        qlookup = Q(first=user) | Q(second=user)
        qlookup2 = Q(first=user) & Q(second=user)
        qs = self.get_queryset().filter(qlookup).exclude(qlookup2).distinct()
        return qs


    def get_or_new(self, user, other_user): # get_or_create
        import pprint
        pprint.pprint(user)
        pprint.pprint(other_user)
        if user == other_user:
            return None
        qlookup1 = Q(owner=user) & Q(users=other_user)
        qs = self.get_queryset().filter(qlookup1).distinct()
        pprint.pprint(qs)
        if qs.count() == 1:
            return qs.first(), False
        elif qs.count() > 1:
            return qs.order_by('timestamp').first(), False
        else:
            Klass = user.__class__
            user2 = Klass.objects.get(id=other_user__id)
            if user != user2:
                obj = self.model(
                        owner=user,
                        second=user2
                    )
                obj.save()
                return obj, True
            return None, False


class Thread(models.Model):
    owner           = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_owner')
    users           = models.ManyToManyField(User, related_name='chat_users')
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


class ChatMessage(models.Model):
    thread      = models.ForeignKey(Thread, null=True, blank=True, on_delete=models.SET_NULL)
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='sender', on_delete=models.CASCADE)
    message     = models.TextField()
    timestamp   = models.DateTimeField(auto_now_add=True)
