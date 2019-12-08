from datetime import datetime
from django.db.models import Sum
from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.exceptions import ValidationError
from django.db import models
from django_jalali.db import models as jmodels
from accounts.models import Broker
from accounts.utils import phone_validator, amount_validator
from transactions.enums import *
from django.db.models import Sum


class ProvidersToken(models.Model):
    provider = models.PositiveSmallIntegerField(choices=Choices.operators, null=False, blank=False)
    token = models.CharField(max_length=150, null=False, blank=False)

    @staticmethod
    def create(provider, token):
        ptoken = ProvidersToken(
            provider=provider,
            token=token,

        )
        ptoken.save()
        return ptoken

    def update_token(self, token):
        self.token = token
        self.save()
        return True


class TopUp(models.Model):
    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True, blank=False)
    operator = models.PositiveSmallIntegerField(choices=Choices.operators, default=Operator.MCI.value)
    timestamp = jmodels.jDateTimeField(auto_now_add=True)
    tell_num = models.BigIntegerField(blank=False, null=False, validators=[phone_validator])
    state = models.PositiveSmallIntegerField(choices=Choices.record_states, default=RecordState.INITIAL.value)
    tell_charger = models.BigIntegerField(blank=False, null=False, validators=[phone_validator])
    amount = models.PositiveIntegerField(blank=False, null=False, verbose_name="Price (Rials)", validators=[amount_validator])
    charge_type = models.PositiveSmallIntegerField(choices=Choices.charge_type_choices, blank=False, null=False)
    call_response_type = models.SmallIntegerField(choices=Choices.response_types_choices, null=True, blank=True)
    call_response_description = models.CharField(max_length=1023, null=True, blank=True)
    execution_time = jmodels.jDateTimeField(null=True, blank=True)
    exe_response_type = models.SmallIntegerField(choices=Choices.response_types_choices, null=True, blank=True)
    exe_response_description = models.CharField(max_length=1023, null=True, blank=True)
    provider_id = models.CharField(max_length=255, null=True, blank=True)
    bank_code = models.PositiveSmallIntegerField(choices=Choices.bank_codes, null=True, blank=True)
    card_number = models.CharField(max_length=255, null=True, blank=True)
    card_type = models.PositiveSmallIntegerField(choices=Choices.card_types, null=True, blank=True)

    @staticmethod
    def report(broker, from_date, to_date):
        dict = []
        # records = TopUp.objects.filter(timestamp__in=None)
        records = TopUp.objects.filter(broker=broker)
        # FILTER BY TIME HERE
        # ----

        # dict.append({"مجموع", intcomma(records.aggregate(Sum('amount'))['amount__sum'])})
        dict.append({
            "title": "جمع کل",
            "value": intcomma(records.aggregate(Sum('amount'))['amount__sum'])
        })
        for charge_type in ChargeType:
            filtered_records = records.filter(charge_type=charge_type.value)
            sum = filtered_records.aggregate(Sum('amount'))['amount__sum']
            # dict.append({ChargeType.farsi(charge_type.value), intcomma(sum)})
            dict.append({
                "title": ChargeType.farsi(charge_type.value),
                "value": intcomma(sum)
            })

    def __str__(self):
        return "Top_up " + str(self.id)

    @staticmethod
    def create(operator, broker, tell_num, tell_charger, amount, charge_type):
        top_up = TopUp(
            operator=operator,
            broker=broker,
            tell_num=tell_num,
            tell_charger=tell_charger,
            amount=int(amount),
            charge_type=charge_type,
        )
        top_up.full_clean()
        top_up.save()
        return top_up

    def after_call(self, call_response_type, call_response_description):
        self.call_response_type = call_response_type
        self.call_response_description = call_response_description

        if int(call_response_type) == ResponseTypes.SUCCESS.value:
            self.provider_id = call_response_description
            self.state = RecordState.CALLED.value
            self.save()
            return True
        else:
            self.state = RecordState.CALL_ERROR.value
            self.save()
            return False

    def before_execute(self, bank_code, card_number, card_type):
        self.execution_time = datetime.now()
        self.state = RecordState.EXE_REQ.value
        self.bank_code = bank_code
        self.card_number = card_number
        self.card_type = card_type
        self.full_clean()
        self.save()

    def after_execute(self, exe_response_type, exe_response_description):
        self.exe_response_type = exe_response_type
        self.exe_response_description = exe_response_description

        if int(exe_response_type) == ResponseTypes.SUCCESS.value:
            self.state = RecordState.EXECUTED.value
            self.save()
            return True
        else:
            self.state = RecordState.EXECUTE_ERROR.value
            self.save()
            return False

    @staticmethod
    def report(broker, from_date, to_date):
        dict = []
        # records = TopUp.objects.filter(timestamp__in=None)
        records = TopUp.objects.filter(broker=broker, timestamp__range=(from_date, to_date))
        # FILTER BY TIME HERE
        # ----

        # dict.append({"مجموع", intcomma(records.aggregate(Sum('amount'))['amount__sum'])})

        for charge_type in ChargeType:
            filtered_records = records.filter(charge_type=charge_type.value)
            sum = filtered_records.aggregate(Sum('amount'))['amount__sum']
            # dict.append({ChargeType.farsi(charge_type.value), intcomma(sum)})
            dict.append({
                "title": ChargeType.farsi(charge_type.value),
                "value": intcomma(sum)
            })
        dict.append({
            "title": "جمع کل شارژ",
            "value": intcomma(records.aggregate(Sum('amount'))['amount__sum'])
        })
        return dict


class Package(models.Model):
    package_type = models.IntegerField()
    operator = models.PositiveSmallIntegerField(choices=Choices.operators, default=Operator.MCI.value)
    name = models.CharField(max_length=255, default='')
    active = models.BooleanField(default=True)
    description = models.CharField(max_length=255, default='')
    amount = models.PositiveIntegerField()
    system = models.PositiveIntegerField(default=2)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = jmodels.jDateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name + " :" + str(self.package_type)


class PackageRecord(models.Model):
    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True, blank=False)
    timestamp = jmodels.jDateTimeField(auto_now_add=True)
    tell_num = models.BigIntegerField(blank=False, null=False, validators=[phone_validator])
    state = models.PositiveSmallIntegerField(choices=Choices.record_states, default=RecordState.INITIAL.value)
    tell_charger = models.BigIntegerField(blank=False, null=False, validators=[phone_validator])
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True)
    # amount = models.PositiveIntegerField(default=0, verbose_name="Price (Rials)")
    call_response_type = models.SmallIntegerField(choices=Choices.response_types_choices, null=True, blank=True)
    call_response_description = models.CharField(max_length=1023, null=True, blank=True)
    execution_time = jmodels.jDateTimeField(null=True, blank=True)
    exe_response_type = models.SmallIntegerField(choices=Choices.response_types_choices, null=True, blank=True)
    exe_response_description = models.CharField(max_length=1023, null=True, blank=True)
    provider_id = models.CharField(max_length=255, null=True, blank=True)
    bank_code = models.PositiveSmallIntegerField(choices=Choices.bank_codes, null=True, blank=True)
    card_number = models.CharField(max_length=255, null=True, blank=True)
    card_type = models.PositiveSmallIntegerField(choices=Choices.card_types, null=True, blank=True)

    @staticmethod
    def report(broker, from_date, to_date):
        dict = []
        # records = TopUp.objects.filter(timestamp__in=None)
        records = PackageRecord.objects.filter(broker=broker)
        # FILTER BY TIME HERE
        # ----

        # dict.append({"مجموع", intcomma(records.aggregate(Sum('amount'))['amount__sum'])})
        dict.append({
            "title": "جمع کل",
            "value": intcomma(records.aggregate(Sum('amount'))['amount__sum'])
        })
        # for charge_type in ChargeType:
        #     filtered_records = records.filter(charge_type=charge_type.value)
        #     sum = filtered_records.aggregate(Sum('amount'))['amount__sum']
        #     # dict.append({ChargeType.farsi(charge_type.value), intcomma(sum)})
        #     dict.append({
        #         "title": ChargeType.farsi(charge_type.value),
        #         "value": intcomma(sum)
        #     })
        print(dict)
    # @property
    # def amount_display(self):
    #     return intcomma(self.amount)

    def __str__(self):
        return "Package record " + str(self.id)

    @staticmethod
    def create(broker, tell_num, tell_charger, package):
        package_record = PackageRecord(
            broker=broker,
            tell_num=tell_num,
            tell_charger=tell_charger,
            package_id=package.pk,
            amount=package.amount
        )
        package_record.full_clean()
        package_record.save()
        return package_record

    def after_call(self, call_response_type, call_response_description):
        self.call_response_type = call_response_type
        self.call_response_description = call_response_description

        if int(call_response_type) == ResponseTypes.SUCCESS.value:
            self.provider_id = call_response_description
            self.state = RecordState.CALLED.value
            self.save()
            return True
        else:
            self.state = RecordState.CALL_ERROR.value
            self.save()
            return False

    def before_execute(self, bank_code, card_number, card_type):
        self.execution_time = datetime.now()
        self.state = RecordState.EXE_REQ.value
        self.bank_code = bank_code
        self.card_number = card_number
        self.card_type = card_type
        self.full_clean()
        self.save()

    def after_execute(self, exe_response_type, exe_response_description):
        self.exe_response_type = exe_response_type
        self.exe_response_description = exe_response_description

        if int(exe_response_type) == ResponseTypes.SUCCESS.value:
            self.state = RecordState.EXECUTED.value
            self.save()
            return True
        else:
            self.state = RecordState.EXECUTE_ERROR.value
            self.save()
            return False

    @staticmethod
    def report(broker, from_date, to_date):
        dict = []
        # records = TopUp.objects.filter(timestamp__in=None)
        records = PackageRecord.objects.filter(broker=broker, timestamp__range=(from_date, to_date))
        # FILTER BY TIME HERE
        # ----

        # dict.append({"مجموع", intcomma(records.aggregate(Sum('amount'))['amount__sum'])})
        dict.append({
            "title": "جمع کل بسته ها",
            "value": intcomma(records.aggregate(Sum('package__amount'))['package__amount__sum'])
        })
        # for charge_type in ChargeType:
        #     filtered_records = records.filter(charge_type=charge_type.value)
        #     sum = filtered_records.aggregate(Sum('amount'))['amount__sum']
        #     # dict.append({ChargeType.farsi(charge_type.value), intcomma(sum)})
        #     dict.append({
        #         "title": ChargeType.farsi(charge_type.value),
        #         "value": intcomma(sum)
        #     })
        return dict
