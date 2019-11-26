from enum import Enum

from django.db import models


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


class Choices:
    charge_type_choices = (
        (ChargeType.MOSTAGHIM.value, ChargeType.farsi(ChargeType.MOSTAGHIM.value)),
        (ChargeType.DELKHAH.value, ChargeType.farsi(ChargeType.DELKHAH.value)),
        (ChargeType.FOGHOLAADE.value, ChargeType.farsi(ChargeType.FOGHOLAADE.value)),
        (ChargeType.JAVANAN.value, ChargeType.farsi(ChargeType.JAVANAN.value)),
        (ChargeType.BANOVAN.value, ChargeType.farsi(ChargeType.BANOVAN.value)),
    )


class TopUp(models.Model):
    tell_num = models.BigIntegerField()
    tell_charger = models.BigIntegerField()
    amount = models.PositiveIntegerField()
    charge_type = models.PositiveSmallIntegerField(choices=Choices.charge_type_choices)

