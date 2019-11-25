from django.contrib.auth.models import User
from django.db import models


class Broker(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name="user", editable=False)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="creator", editable=False)
    name = models.CharField(max_length=255, unique=True)
    email = models.EmailField()
    credit = models.PositiveIntegerField(default=0, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class BalanceIncrease(models.Model):

    class Meta:
        permissions = (
            ("top_up", "Can top up users"),
        )

    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True, blank=False)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, editable=False)
    amount = models.PositiveIntegerField()
    comment = models.CharField(max_length=255, unique=True)
    success = models.BooleanField(default=False, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
