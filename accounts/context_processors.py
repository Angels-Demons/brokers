from django.contrib.auth.models import User

from accounts.models import Broker


def test(request):
    try:
        credit = Broker.objects.get(user=request.user)
        return {'user_Broker': 1}
    except:
        return {}
