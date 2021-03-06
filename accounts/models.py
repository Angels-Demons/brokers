from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_comma_separated_integer_list, MinValueValidator, MaxValueValidator
from django.db import models, transaction
from django_jalali.db import models as jmodels

from transactions import enums
from transactions.enums import Operator, CreditType


# from transactions.models import Package


class Broker(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name="broker")
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_brokers")
    name = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField()
    # credit = models.BigIntegerField(default=0, editable=False)
    active = models.BooleanField(default=True)
    timestamp = jmodels.jDateTimeField(auto_now_add=True)

    # mcci_discount = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    @staticmethod
    def get_brokers():
        brokers_tuple = []
        brokers = Broker.objects.all()
        for broker in brokers:
            brokers_tuple.append((str(broker.pk), broker.name))
        return brokers_tuple

    def __str__(self):
        return self.name

    # def get_mcci_discount(self):
    #     return self.mcci_discount/100

    # def charge_for_mcci_transaction(self, price):
    #     # if self.active is False:
    #     #     return False
    #     real_price = price * (1-self.get_mcci_discount())
    #     with transaction.atomic():
    #         if self.credit >= real_price:
    #             self.credit -= real_price
    #             self.save()
    #             return True
    #         return False


class ChargeType(models.Model):
    name_fa = models.CharField(max_length=255, default='', editable=False)
    charge_type = models.PositiveSmallIntegerField(choices=enums.Choices.charge_type_choices, unique=True)

    def clean(self):
        self.name_fa = enums.ChargeType.farsi(self.charge_type)

    def __str__(self):
        return self.name_fa


class OperatorAccess(models.Model):
    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True, blank=False)
    operator = models.PositiveSmallIntegerField(choices=enums.Choices.operators, default=Operator.MCI.value)
    general_credit_access = models.BooleanField(default=False)
    top_up_access = models.BooleanField(default=True)
    package_access = models.BooleanField(default=True)
    credit = models.BigIntegerField(default=0, verbose_name='Credit (Rials)',
                                    validators=[MinValueValidator(limit_value=0, message='error')])
    top_up_credit = models.BigIntegerField(default=0, verbose_name='Top_up credit (Rials)',
                                           validators=[MinValueValidator(limit_value=0, message='error')])
    package_credit = models.BigIntegerField(default=0, verbose_name='Package credit (Rials)',
                                            validators=[MinValueValidator(limit_value=0, message='error')])
    banned_packages = models.ManyToManyField('transactions.Package', blank=True)
    banned_charge_types = models.ManyToManyField(ChargeType, blank=True)
    # banned_charge_types = models.IntegerField(default=0)
    last_editor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, editable=False)
    comment = models.TextField()
    active = models.BooleanField(default=True)
    top_up_discount = models.DecimalField(max_digits=4, decimal_places=2, default=0,
                                          validators=[MinValueValidator(0), MaxValueValidator(100)])
    package_discount = models.DecimalField(max_digits=4, decimal_places=2, default=0,
                                           validators=[MinValueValidator(0), MaxValueValidator(100)])
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

    def charge(self, amount, top_up=True, record=None):
        if top_up:
            real_price = amount * (1 - (self.top_up_discount / 100))
        else:
            real_price = amount * (1 - (self.package_discount / 100))

        if record is not None:
            record.cost = real_price
            record.save()
        with transaction.atomic():
            locked_self = OperatorAccess.objects.select_for_update().get(id=self.id)
            if locked_self.general_credit_access:
                locked_self.credit -= real_price
                locked_self.save()
                return True

            if top_up:
                locked_self.top_up_credit -= real_price
                locked_self.save()
                return True
            else:
                locked_self.package_credit -= real_price
                locked_self.save()
                return True

    def increase_balance(self, balance_increase):
        if not self.active:
            return False, "operator access is not active\nدسترسی شما به این اپراتور فعال نیست"
        with transaction.atomic():
            locked_self = OperatorAccess.objects.select_for_update().get(id=self.id)
            if balance_increase.credit_type == CreditType.GENERAL.value:
                if locked_self.general_credit_access:
                    # balance_increase.success = True
                    locked_self.credit += balance_increase.amount
                    locked_self.clean()
                    locked_self.save()
                    return True, ""
                return False, "general credit access is not granted, thus no balance increase\nدسترسی به اعتبار عمومی ندارید"
            elif balance_increase.credit_type == CreditType.TOP_UP.value:
                if locked_self.top_up_access:
                    # balance_increase.success = True
                    locked_self.top_up_credit += balance_increase.amount
                    print(locked_self.clean())
                    locked_self.save()
                    return True, ""
                return False, "top_up access is not granted, thus no balance increase\nدسترسی به شارژ تاپ آپ ندارید"
            elif balance_increase.credit_type == CreditType.PACKAGE.value:
                if locked_self.package_access:
                    # balance_increase.success = True
                    locked_self.package_credit += balance_increase.amount
                    locked_self.clean()
                    print("here!")
                    locked_self.save()
                    locked_self.clean()
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
            print(self.top_up_credit)
            print(self.top_up_credit < 0)
        if self.credit < 0 or self.package_credit < 0 or self.top_up_credit < 0:
            raise ValidationError('credits can not be negative')


class BalanceIncrease(models.Model):
    # class Meta:
    #     permissions = (
    #         ("top_up", "Can top up users"),
    #     )

    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True, blank=False)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    operator = models.PositiveSmallIntegerField(choices=enums.Choices.operators, default=enums.Operator.MCI.value)
    credit_type = models.PositiveSmallIntegerField(choices=enums.Choices.credit_types,
                                                   default=enums.CreditType.GENERAL.value)
    amount = models.BigIntegerField(verbose_name='Amount (Rials)')
    # amount = models.CharField(validators=[validate_comma_separated_integer_list], default=0, max_length=255)
    comment = models.TextField()
    success = models.BooleanField(default=False)
    timestamp = jmodels.jDateTimeField(auto_now_add=True)

    # @property
    # def amount_display(self):
    #     return "$%s" % self.amount

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
