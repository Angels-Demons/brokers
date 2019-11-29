from django.contrib.auth.models import User

from accounts.models import Broker


def test(request):
    try:
        credit = Broker.objects.get(user=request.user).credit
        return {'user_credit': credit}
    except:
        return {'user_credit': 0}
