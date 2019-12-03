from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django_jalali.db import models as jmodels

from transactions import enums
from transactions.enums import Operator, CreditType


# from transactions.models import Package


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
        # if self.active is False:
        #     return False
        real_price = price * (1-self.get_mcci_discount())
        with transaction.atomic():
            if self.credit >= real_price:
                self.credit -= real_price
                self.save()
                return True
            return False


class OperatorAccess(models.Model):
    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True, blank=False)
    operator = models.PositiveSmallIntegerField(choices=enums.Choices.operators, default=Operator.MCI.value)
    general_credit_access = models.BooleanField(default=False)
    top_up_access = models.BooleanField(default=True)
    package_access = models.BooleanField(default=True)
    credit = models.BigIntegerField(default=0)
    top_up_credit = models.BigIntegerField(default=0)
    package_credit = models.BigIntegerField(default=0)
    banned_packages = models.ManyToManyField('transactions.Package', null=True, blank=True)
    last_editor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, editable=False)
    comment = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    timestamp = jmodels.jDateTimeField(auto_now_add=True)

    def can_sell(self, top_up=True):
        if self.general_credit_access:
            return True
        if top_up and self.top_up_access:
            return True
        if not top_up and self.package_access:
            return True
        return False

    def get_credit(self, top_up=True):
        if self.general_credit_access:
            return self.credit
        if top_up:
            return self.top_up_credit
        else:
            return self.package_credit

    def charge(self, amount, top_up=True):
        if self.general_credit_access:
            self.credit -= amount
            self.save()
            return True

        if top_up:
            self.top_up_credit -= amount
            self.save()
            return True
        else:
            self.package_credit -= amount
            self.save()
            return True

    def increase_balance(self, balance_increase):
        if not self.active:
            return False, "operator access is not active\nدسترسی شما به این اپراتور فعال نیست"
        if balance_increase.credit_type == CreditType.GENERAL.value:
            if self.general_credit_access:
                # balance_increase.success = True
                self.credit += balance_increase.amount
                self.save()
                return True, ""
            return False, "general credit access is not granted, thus no balance increase\nدسترسی به اعتبار عمومی ندارید"
        elif balance_increase.credit_type == CreditType.TOP_UP.value:
            if self.top_up_access:
                # balance_increase.success = True
                self.top_up_credit += balance_increase.amount
                self.save()
                return True, ""
            return False, "top_up access is not granted, thus no balance increase\nدسترسی به شارژ تاپ آپ ندارید"
        elif balance_increase.credit_type == CreditType.PACKAGE.value:
            if self.package_access:
                # balance_increase.success = True
                self.package_credit += balance_increase.amount
                self.save()
                return True, ""
            return False, "package access is not granted, thus no balance increase\nدسترسی به بسته ندارید"
        return False, "invalid credit type"

    class Meta:
        verbose_name_plural = "Access to operators"
        unique_together = ('broker', 'operator')

    def __str__(self):
        return str(self.broker) + " " + str(Operator.farsi(self.operator))

    def clean(self):
        if self.general_credit_access:
            if self.top_up_access or self.package_access:
                raise ValidationError('Brokers can either have general credit access or top_up/package access')


class BalanceIncrease(models.Model):

    # class Meta:
    #     permissions = (
    #         ("top_up", "Can top up users"),
    #     )

    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True, blank=False)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, editable=False)
    operator = models.PositiveSmallIntegerField(choices=enums.Choices.operators, default=enums.Operator.MCI.value)
    credit_type = models.PositiveSmallIntegerField(choices=enums.Choices.credit_types, default=enums.CreditType.GENERAL.value)
    amount = models.PositiveIntegerField()
    comment = models.CharField(max_length=255)
    success = models.BooleanField(default=False)
    timestamp = jmodels.jDateTimeField(auto_now_add=True)

    def clean(self):
        try:
            operator_access = OperatorAccess.objects.get(operator=self.operator, broker=self.broker)
        except OperatorAccess.DoesNotExist as e:
            raise ValidationError("broker does not have an operator_access with selected operator")

        success, error = operator_access.increase_balance(self)
        if not success:
            raise ValidationError(error)
        self.success = True

    def __str__(self):
        try:
            return self.broker.username
        except AttributeError:
            return "Null broker"
