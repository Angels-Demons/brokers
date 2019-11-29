from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django_jalali.db import models as jmodels
from accounts.models import Broker
from accounts.utils import phone_validator, amount_validator
from transactions.enums import *


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
    timestamp = jmodels.jDateTimeField(auto_now_add=True)
    tell_num = models.BigIntegerField(blank=False, null=False, validators=[phone_validator])
    state = models.PositiveSmallIntegerField(choices=Choices.top_up_states, default=TopUpState.INITIAL.value)
    tell_charger = models.BigIntegerField(blank=False, null=False, validators=[phone_validator])
    amount = models.PositiveIntegerField(blank=False, null=False, validators=[amount_validator])
    charge_type = models.PositiveSmallIntegerField(choices=Choices.charge_type_choices, blank=False, null=False)
    call_response_type = models.SmallIntegerField(choices=Choices.response_types_choices, null=True)
    call_response_description = models.CharField(max_length=1023, null=True)
    execution_time = jmodels.jDateTimeField(null=True)
    exe_response_type = models.SmallIntegerField(choices=Choices.response_types_choices, null=True)
    exe_response_description = models.CharField(max_length=1023, null=True)
    provider_id = models.CharField(max_length=255, null=True)
    bank_code = models.PositiveSmallIntegerField(choices=Choices.bank_codes, null=True)
    card_number = models.CharField(max_length=255, null=True)
    card_type = models.PositiveSmallIntegerField(choices=Choices.card_types, null=True)

    def __str__(self):
        return "Top_up " + str(self.id)

    @staticmethod
    def create(broker, tell_num, tell_charger, amount, charge_type):
        top_up = TopUp(
            broker=broker,
            tell_num=tell_num,
            # state =
            tell_charger=tell_charger,
            amount=int(amount),
            charge_type=charge_type,
            # call_response_type =
            # call_response_description =
            # exe_response_type =
            # exe_response_description =
            # provider_id =
            # bank_code =
            # card_number =
            # card_type =
        )
        top_up.save()
        return top_up

    def after_call(self, call_response_type, call_response_description):
        self.call_response_type = call_response_type
        self.call_response_description = call_response_description

        if int(call_response_type) == ResponseTypes.SUCCESS.value:
            self.provider_id = call_response_description
            self.state = TopUpState.CALLED.value
            self.save()
            return True
        else:
            self.state = TopUpState.CALL_ERROR.value
            self.save()
            return False

    def before_execute(self, bank_code, card_number, card_type):
        self.execution_time = datetime.now()
        self.state = TopUpState.EXE_REQ.value
        self.bank_code = bank_code
        self.card_number = card_number
        self.card_type = card_type
        self.save()

    def after_execute(self, exe_response_type, exe_response_description):
        self.exe_response_type = exe_response_type
        self.exe_response_description = exe_response_description

        if int(exe_response_type) == ResponseTypes.SUCCESS.value:
            self.state = TopUpState.EXECUTED.value
            self.save()
            return True
        else:
            self.state = TopUpState.EXECUTE_ERROR.value
            self.save()
            return False


class Package(models.Model):
    package_type = models.IntegerField()
    operator = models.PositiveSmallIntegerField(choices=Choices.operators, default=Operator.MCI.value)
    name = models.CharField(max_length=255, default='')
    active = models.BooleanField(default=True)
    description = models.CharField(max_length=255, default='')
    amount = models.PositiveIntegerField()
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = jmodels.jDateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class PackageRecord(models.Model):
    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True, blank=False)
    timestamp = jmodels.jDateTimeField(auto_now_add=True)
    tell_num = models.BigIntegerField(blank=False, null=False, validators=[phone_validator])
    state = models.PositiveSmallIntegerField(choices=Choices.top_up_states, default=TopUpState.INITIAL.value)
    tell_charger = models.BigIntegerField(blank=False, null=False, validators=[phone_validator])
    # amount = models.PositiveIntegerField(blank=False, null=False)
    # package_type = models.IntegerField(blank=False, null=False)
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True)
    call_response_type = models.SmallIntegerField(choices=Choices.response_types_choices, null=True)
    call_response_description = models.CharField(max_length=1023, null=True)
    execution_time = jmodels.jDateTimeField(null=True)
    exe_response_type = models.SmallIntegerField(choices=Choices.response_types_choices, null=True)
    exe_response_description = models.CharField(max_length=1023, null=True)
    provider_id = models.CharField(max_length=255, null=True)
    bank_code = models.PositiveSmallIntegerField(choices=Choices.bank_codes, null=True)
    card_number = models.CharField(max_length=255, null=True)
    card_type = models.PositiveSmallIntegerField(choices=Choices.card_types, null=True)

    def __str__(self):
        return "Package record " + str(self.id)

    @staticmethod
    def create(broker, tell_num, tell_charger, package_id):
        package_record = PackageRecord(
            broker=broker,
            tell_num=tell_num,
            # state =
            tell_charger=tell_charger,
            # amount=amount,
            package_id=package_id,
            # package_type=package_type,
            # call_response_type =
            # call_response_description =
            # exe_response_type =
            # exe_response_description =
            # provider_id =
            # bank_code =
            # card_number =
            # card_type =
        )
        package_record.save()
        return package_record

    def after_call(self, call_response_type, call_response_description):
        self.call_response_type = call_response_type
        self.call_response_description = call_response_description

        if int(call_response_type) == ResponseTypes.SUCCESS.value:
            self.provider_id = call_response_description
            self.state = TopUpState.CALLED.value
            self.save()
            return True
        else:
            self.state = TopUpState.CALL_ERROR.value
            self.save()
            return False

    def before_execute(self, bank_code, card_number, card_type):
        self.execution_time = datetime.now()
        self.state = TopUpState.EXE_REQ.value
        self.bank_code = bank_code
        self.card_number = card_number
        self.card_type = card_type
        self.save()

    def after_execute(self, exe_response_type, exe_response_description):
        self.exe_response_type = exe_response_type
        self.exe_response_description = exe_response_description

        if int(exe_response_type) == ResponseTypes.SUCCESS.value:
            self.state = TopUpState.EXECUTED.value
            self.save()
            return True
        else:
            self.state = TopUpState.EXECUTE_ERROR.value
            self.save()
            return False
