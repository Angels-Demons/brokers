from datetime import datetime
from enum import Enum

from django.db import models
from django_jalali.db import models as jmodels
from accounts.models import Broker


class ChargeType(Enum):
    MOSTAGHIM = 1001
    DELKHAH = 1002
    FOGHOLAADE = 1003
    JAVANAN = 1004
    BANOVAN = 1005

    @staticmethod
    def farsi(value):
        if value == 1001:
            return "مستقیم"
        elif value == 1002:
            return "دلخواه"
        elif value == 1003:
            return "فوق العاده"
        elif value == 1004:
            return "جوانان"
        elif value == 1005:
            return "بانوان"


class TopUpState(Enum):
    INITIAL = 1
    CALLED = 2
    CALL_ERROR = 3
    EXE_REQ = 4
    EXECUTED = 5
    EXECUTE_ERROR = 6

    # @staticmethod
    # def farsi(value):
    #     if value == 1:
    #         return "مستقیم"
    #     elif value == 2:
    #         return "دلخواه"


class Choices:
    charge_type_choices = (
        (ChargeType.MOSTAGHIM.value, ChargeType.farsi(ChargeType.MOSTAGHIM.value)),
        (ChargeType.DELKHAH.value, ChargeType.farsi(ChargeType.DELKHAH.value)),
        (ChargeType.FOGHOLAADE.value, ChargeType.farsi(ChargeType.FOGHOLAADE.value)),
        (ChargeType.JAVANAN.value, ChargeType.farsi(ChargeType.JAVANAN.value)),
        (ChargeType.BANOVAN.value, ChargeType.farsi(ChargeType.BANOVAN.value)),
    )

    top_up_states = (
        (TopUpState.INITIAL.value, TopUpState.INITIAL.name),
        (TopUpState.EXECUTED.value, TopUpState.EXECUTED.name),
    )

    bank_codes = (

    )

    card_types = (

    )


class TopUp(models.Model):
    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True, blank=False, editable=False)
    timestamp = jmodels.jDateTimeField(auto_now_add=True)
    tell_num = models.BigIntegerField(blank=False, null=False, editable=False)
    state = models.PositiveSmallIntegerField(choices=Choices.top_up_states, default=TopUpState.INITIAL.value, editable=False)
    tell_charger = models.BigIntegerField(blank=False, null=False, editable=False)
    amount = models.PositiveIntegerField(blank=False, null=False, editable=False)
    charge_type = models.PositiveSmallIntegerField(choices=Choices.charge_type_choices, blank=False, null=False, editable=False)
    call_response_type = models.SmallIntegerField(null=True, editable=False)
    call_response_description = models.CharField(max_length=1023, null=True, editable=False)
    execution_time = jmodels.jDateTimeField(null=True, editable=False)
    exe_response_type = models.SmallIntegerField(null=True, editable=False)
    exe_response_description = models.CharField(max_length=1023, null=True, editable=False)
    provider_id = models.CharField(max_length=255, null=True, editable=False)
    # modify RG: bank_codes enum
    bank_code = models.PositiveSmallIntegerField(choices=Choices.bank_codes, null=True, editable=False)
    card_number = models.CharField(max_length=255, null=True, editable=False)
    # modify RG: card_types enum
    card_type = models.PositiveSmallIntegerField(choices=Choices.card_types, null=True, editable=False)

    @staticmethod
    def create(broker, tell_num, tell_charger, amount, charge_type):
        top_up = TopUp(
            broker=broker,
            tell_num=tell_num,
            # state =
            tell_charger=tell_charger,
            amount=amount,
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

        # modify RG: .SUCCESS.VALUE
        if call_response_type == 0:
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
        self.state = TopUpState.EXE_REQ
        self.bank_code = bank_code
        self.card_number = card_number
        self.card_type = card_type
        self.save()

    def after_execute(self, exe_response_type, exe_response_description):
        self.exe_response_type = exe_response_type
        self.exe_response_description = exe_response_description
        self.save()

        if exe_response_type == 0:
            self.state = TopUpState.EXECUTED.value
            return True
        else:
            self.state = TopUpState.EXECUTE_ERROR.value
            return False
