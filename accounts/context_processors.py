from django.contrib.auth.models import User

from accounts.admin import is_admin
from accounts.models import Broker
from interface.API import MCI


def test(request):
    dictionary = {}
    if request.user.is_superuser or is_admin(request.user):
        exe_response_type_1, exe_response_description_1 = MCI().behsa_charge_credit()
        exe_response_type_2, exe_response_description_2 = MCI().behsa_package_credit()

        if exe_response_type_1 == 0:
            dictionary['Charge_Credit'] = exe_response_description_1
        else:
            dictionary['Charge_Credit'] = "اتصال با سرور برقرار نیست"
        if exe_response_type_2 == 0:
            dictionary['Package_Credit'] = exe_response_description_2
        else:
            dictionary['Package_Credit'] = "اتصال با سرور برقرار نیست"

    try:
        Broker.objects.get(user=request.user)
        dictionary['user_Broker'] = 1

    except:
        pass

    return dictionary
