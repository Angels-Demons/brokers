from django.contrib.auth.models import User
from django.db import models, transaction
from django_jalali.db import models as jmodels


class Broker(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name="user", editable=False)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="creator", editable=False)
    name = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField()
    credit = models.BigIntegerField(default=0, editable=False)
    active = models.BooleanField(default=True)
    timestamp = jmodels.jDateTimeField(auto_now_add=True)
    mcci_discount = models.DecimalField(max_digits=4, decimal_places=2, default=0)

    def __str__(self):
        return self.name

    def get_mcci_discount(self):
        return self.mcci_discount/100

    def charge_for_mcci_transaction(self, price):
        if self.active is False:
            return False
        with transaction.atomic():
            if self.credit >= price:
                self.credit -= price
                self.save()
                return True
            return False


class BalanceIncrease(models.Model):

    # class Meta:
    #     permissions = (
    #         ("top_up", "Can top up users"),
    #     )

    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True, blank=False)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, editable=False)
    amount = models.PositiveIntegerField()
    comment = models.CharField(max_length=255, unique=True)
    success = models.BooleanField(default=False, editable=False)
    timestamp = jmodels.jDateTimeField(auto_now_add=True)
